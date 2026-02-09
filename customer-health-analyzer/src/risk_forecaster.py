"""
Renewal risk forecaster.

Calculates churn probability using score bands, trend analysis,
and specific risk factors to produce actionable risk assessments.
"""

from datetime import datetime
from typing import Dict, List, Optional

import pandas as pd


# Default churn rates by score band
DEFAULT_CHURN_RATES = {
    'healthy': 0.08,       # 80-100: ~5-10%
    'attention': 0.25,     # 60-79: ~20-30%
    'at_risk': 0.45,       # 40-59: ~40-50%
    'critical': 0.70       # 0-39: ~60-80%
}

# Trend adjustments (percentage points)
TREND_ADJUSTMENTS = {
    'DECLINING RAPIDLY': 0.15,
    'DECLINING': 0.10,
    'SLIGHTLY DECLINING': 0.05,
    'STABLE': 0.0,
    'SLIGHTLY IMPROVING': -0.05,
    'IMPROVING': -0.10,
    'IMPROVING RAPIDLY': -0.15
}


def calculate_churn_probability(
    customer_score: Dict,
    trend_analysis: Optional[Dict],
    interventions_df: pd.DataFrame
) -> Dict:
    """
    Calculate churn probability for a customer.

    Args:
        customer_score: Dict from master_scorer
        trend_analysis: Dict from trend_analyzer or None
        interventions_df: DataFrame of historical interventions

    Returns:
        Dict with comprehensive risk forecast
    """
    final_score = customer_score['final_score']
    arr = customer_score['arr']
    days_to_renewal = customer_score['days_to_renewal']
    customer_name = customer_score['customer']

    # Step 1: Baseline churn rate by score band
    if final_score >= 80:
        baseline = DEFAULT_CHURN_RATES['healthy']
        score_band = '80-100'
    elif final_score >= 60:
        baseline = DEFAULT_CHURN_RATES['attention']
        score_band = '60-79'
    elif final_score >= 40:
        baseline = DEFAULT_CHURN_RATES['at_risk']
        score_band = '40-59'
    else:
        baseline = DEFAULT_CHURN_RATES['critical']
        score_band = '0-39'

    # Try to refine with historical data
    historical_baseline = _get_historical_churn_rate(interventions_df, score_band)
    if historical_baseline is not None:
        baseline = historical_baseline

    # Step 2: Trend adjustment
    trend_adjustment = 0.0
    trend_label = 'N/A'
    if trend_analysis and trend_analysis.get('has_sufficient_history'):
        trend_label = trend_analysis['trend_label']
        trend_adjustment = TREND_ADJUSTMENTS.get(trend_label, 0.0)

    # Step 3: Risk factor adjustments
    risk_factor_adjustment = 0.0
    primary_risk_factors: List[str] = []

    # Competitive mentions
    competitive_mentions = customer_score.get('competitive_mentions', [])
    if competitive_mentions:
        risk_factor_adjustment += 0.10
        primary_risk_factors.append(
            f"Competitive pressure: {len(competitive_mentions)} mention(s)"
        )

    # Risk signals
    risk_signals = customer_score.get('risk_signals', [])
    if risk_signals:
        signal_adj = min(len(risk_signals) * 0.05, 0.15)
        risk_factor_adjustment += signal_adj
        primary_risk_factors.append(
            f"Risk signals detected: {len(risk_signals)}"
        )

    # Human/AI divergence with CSM scoring lower
    if customer_score.get('human_ai_divergence', False):
        csm_sent = customer_score.get('csm_sentiment', 0)
        auto_sent = customer_score.get('automated_sentiment', 0)
        if csm_sent and auto_sent and csm_sent < auto_sent:
            risk_factor_adjustment += 0.10
            primary_risk_factors.append(
                "CSM rates sentiment lower than AI analysis"
            )

    # Override alert
    if customer_score.get('override_alert', False):
        risk_factor_adjustment += 0.05
        primary_risk_factors.append("CSM override alert active")

    # Days to renewal urgency
    if days_to_renewal < 30:
        risk_factor_adjustment += 0.05
        primary_risk_factors.append(
            f"Renewal in {days_to_renewal} days (critical period)"
        )

    # Divergence alert
    if customer_score.get('divergence_alert'):
        risk_factor_adjustment += 0.05
        primary_risk_factors.append("Usage/communication divergence detected")

    # Step 4: Calculate final probability
    churn_probability = baseline + trend_adjustment + risk_factor_adjustment
    churn_probability = max(0.05, min(0.95, churn_probability))

    # Step 5: Revenue at risk
    revenue_at_risk = arr * churn_probability

    # Step 6: Decision timeline
    if days_to_renewal > 60:
        decision_timeline = "Decision window not yet open"
    elif days_to_renewal > 30:
        decision_timeline = "Entering decision window"
    else:
        decision_timeline = "In critical decision period"

    # Urgency level
    urgency_level = _calculate_urgency(churn_probability, days_to_renewal)

    # Confidence level
    has_trend = trend_analysis and trend_analysis.get('has_sufficient_history')
    has_comms = len(risk_signals) > 0 or len(competitive_mentions) > 0
    if has_trend and has_comms:
        confidence = 'high'
    elif has_trend or has_comms:
        confidence = 'medium'
    else:
        confidence = 'low'

    # Forecast basis description
    basis_parts = [f"Baseline {baseline*100:.0f}% churn rate for score band {score_band}"]
    if trend_adjustment != 0:
        basis_parts.append(f"trend adjustment {trend_adjustment*100:+.0f}pp ({trend_label})")
    if risk_factor_adjustment > 0:
        basis_parts.append(
            f"risk factor adjustment +{risk_factor_adjustment*100:.0f}pp "
            f"({len(primary_risk_factors)} factors)"
        )
    forecast_basis = "; ".join(basis_parts)

    if not primary_risk_factors:
        primary_risk_factors.append("No specific risk factors identified")

    return {
        'customer': customer_name,
        'churn_probability': round(churn_probability, 3),
        'churn_probability_pct': round(churn_probability * 100, 1),
        'confidence_level': confidence,
        'baseline_churn_rate': round(baseline, 3),
        'trend_adjustment': round(trend_adjustment, 3),
        'risk_factor_adjustment': round(risk_factor_adjustment, 3),
        'arr': arr,
        'revenue_at_risk': round(revenue_at_risk, 2),
        'days_to_renewal': days_to_renewal,
        'decision_timeline': decision_timeline,
        'urgency_level': urgency_level,
        'primary_risk_factors': primary_risk_factors,
        'forecast_basis': forecast_basis
    }


def _get_historical_churn_rate(
    interventions_df: pd.DataFrame,
    score_band: str
) -> Optional[float]:
    """
    Try to calculate historical churn rate from intervention outcomes.
    Returns None if insufficient data.
    """
    if interventions_df.empty:
        return None

    churned = len(interventions_df[interventions_df['outcome'] == 'churned'])
    renewed = len(interventions_df[interventions_df['outcome'] == 'renewed'])

    total = churned + renewed
    if total < 3:
        return None

    return churned / total


def _calculate_urgency(churn_probability: float, days_to_renewal: int) -> str:
    """Determine urgency level from churn probability and renewal timeline."""
    if churn_probability >= 0.60 and days_to_renewal <= 60:
        return "critical"
    elif churn_probability >= 0.40 and days_to_renewal <= 90:
        return "high"
    elif churn_probability >= 0.25 or days_to_renewal <= 30:
        return "medium"
    else:
        return "low"
