"""
Intervention effectiveness tracker.

Analyzes historical intervention outcomes to calculate success rates
and recommend data-driven actions for at-risk customers.
"""

from typing import Dict, List

import pandas as pd


SUCCESS_OUTCOMES = {
    'score_improved', 'issue_resolved', 'renewed',
    'tickets_decreased', 'usage_increased'
}


def analyze_intervention_effectiveness(interventions_df: pd.DataFrame) -> Dict:
    """
    Analyze effectiveness of each intervention type.

    Args:
        interventions_df: DataFrame with intervention records

    Returns:
        Dict mapping intervention types to effectiveness metrics
    """
    if interventions_df.empty:
        return {}

    effectiveness = {}

    for intervention_type in interventions_df['intervention_type'].unique():
        type_df = interventions_df[
            interventions_df['intervention_type'] == intervention_type
        ]

        total = len(type_df)
        successes = len(type_df[type_df['outcome'].isin(SUCCESS_OUTCOMES)])
        success_rate = (successes / total * 100) if total > 0 else 0.0

        avg_days = type_df['days_to_outcome'].mean()

        # Breakdown by trigger reason
        by_trigger = {}
        for trigger in type_df['trigger_reason'].unique():
            trigger_df = type_df[type_df['trigger_reason'] == trigger]
            trigger_total = len(trigger_df)
            trigger_successes = len(
                trigger_df[trigger_df['outcome'].isin(SUCCESS_OUTCOMES)]
            )
            trigger_rate = (
                (trigger_successes / trigger_total * 100) if trigger_total > 0 else 0.0
            )
            by_trigger[trigger] = {
                'success_rate': round(trigger_rate, 1),
                'sample_size': trigger_total
            }

        effectiveness[intervention_type] = {
            'overall_success_rate': round(success_rate, 1),
            'avg_days_to_outcome': round(avg_days, 1),
            'sample_size': total,
            'by_trigger': by_trigger
        }

    return effectiveness


def calculate_historical_churn_rate_by_score(interventions_df: pd.DataFrame) -> Dict:
    """
    Calculate overall churn/retention statistics from intervention outcomes.

    Args:
        interventions_df: DataFrame of interventions

    Returns:
        Dict with churn rate statistics
    """
    if interventions_df.empty:
        return {
            'total_renewals': 0,
            'total_churns': 0,
            'overall_churn_rate': 0.0,
            'sample_size': 0
        }

    renewals = len(interventions_df[interventions_df['outcome'] == 'renewed'])
    churns = len(interventions_df[interventions_df['outcome'] == 'churned'])

    total = renewals + churns
    churn_rate = (churns / total) if total > 0 else 0.0

    return {
        'total_renewals': renewals,
        'total_churns': churns,
        'overall_churn_rate': round(churn_rate, 3),
        'sample_size': total
    }


def recommend_intervention(
    customer_data: Dict,
    comm_insights: Dict,
    risk_forecast: Dict,
    effectiveness_data: Dict
) -> List[Dict]:
    """
    Recommend data-driven interventions based on customer risk factors.

    Args:
        customer_data: Dict with customer metrics
        comm_insights: Dict with communication insights
        risk_forecast: Dict with risk forecast
        effectiveness_data: Dict with intervention effectiveness analysis

    Returns:
        List of recommendation dicts sorted by priority
    """
    recommendations = []
    risk_factors = []

    # Identify current risk factors
    logins = customer_data.get('logins_30d', 0)
    tickets = customer_data.get('tickets_30d', 0)
    competitive_pressure = comm_insights.get('competitive_pressure_score', 0)
    trajectory = comm_insights.get('sentiment_trajectory', 'stable')
    days_to_renewal = risk_forecast.get('days_to_renewal', 365)
    churn_prob = risk_forecast.get('churn_probability', 0)
    urgency_level = risk_forecast.get('urgency_level', 'low')
    arr = risk_forecast.get('arr', 0)
    revenue_at_risk = risk_forecast.get('revenue_at_risk', 0)

    if logins < 10:
        risk_factors.append('declining_usage')
    if tickets > 8:
        risk_factors.append('support_ticket_spike')
    if competitive_pressure > 10:
        risk_factors.append('competitive_mention')
    if trajectory in ['declining']:
        risk_factors.append('negative_sentiment')
    if days_to_renewal < 60:
        risk_factors.append('renewal_approaching')

    # If no specific risk factors but churn probability is elevated
    if not risk_factors and churn_prob > 0.25:
        risk_factors.append('routine_touchpoint')

    # For each risk factor, find the best intervention
    for risk_factor in risk_factors:
        best = _find_best_intervention(risk_factor, effectiveness_data)
        if best:
            urgency = 'critical' if urgency_level == 'critical' else (
                'high' if urgency_level == 'high' or churn_prob > 0.35 else 'medium'
            )

            reasoning = f"Customer has {churn_prob*100:.0f}% churn probability"
            if revenue_at_risk > 50000:
                reasoning += f" with ${revenue_at_risk:,.0f} ARR at risk (high-value account)"
            elif revenue_at_risk > 0:
                reasoning += f" with ${revenue_at_risk:,.0f} at risk"

            prefix = "URGENT: " if urgency_level == 'critical' else ""

            recommendations.append({
                'risk_factor': risk_factor,
                'recommended_action': f"{prefix}{best['action']}",
                'expected_success_rate': best['success_rate'],
                'evidence': best['evidence'],
                'urgency': urgency,
                'reasoning': reasoning
            })

    # Sort by urgency (critical first) then by success rate
    urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    recommendations.sort(
        key=lambda x: (urgency_order.get(x['urgency'], 3), -x['expected_success_rate'])
    )

    return recommendations


def _find_best_intervention(
    trigger_reason: str,
    effectiveness_data: Dict
) -> Dict:
    """Find the intervention type with the highest success rate for a given trigger."""
    best_action = None
    best_rate = 0.0
    best_evidence = ""

    for intervention_type, data in effectiveness_data.items():
        triggers = data.get('by_trigger', {})
        if trigger_reason in triggers:
            trigger_data = triggers[trigger_reason]
            if trigger_data['sample_size'] >= 3 and trigger_data['success_rate'] > best_rate:
                best_rate = trigger_data['success_rate']
                best_action = intervention_type
                best_evidence = (
                    f"Based on {trigger_data['sample_size']} historical interventions "
                    f"for {trigger_reason}"
                )

    # If no trigger-specific data with enough samples, use overall rates
    if best_action is None:
        for intervention_type, data in effectiveness_data.items():
            if data['sample_size'] >= 3 and data['overall_success_rate'] > best_rate:
                best_rate = data['overall_success_rate']
                best_action = intervention_type
                best_evidence = (
                    f"Based on {data['sample_size']} historical interventions "
                    f"(overall rate, no trigger-specific data)"
                )

    if best_action:
        return {
            'action': best_action,
            'success_rate': best_rate,
            'evidence': best_evidence
        }
    return None
