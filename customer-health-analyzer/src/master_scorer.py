"""
Master health scorer.

Combines traditional metrics and communication health into a final
composite score, detects divergence patterns, and assigns health tiers.
"""

from datetime import datetime
from typing import Dict

from traditional_scorer import calculate_traditional_score
from communication_scorer import calculate_communication_score


def calculate_final_health_score(
    customer_data: Dict,
    comm_insights: Dict
) -> Dict:
    """
    Calculate the final composite health score for a customer.

    Args:
        customer_data: Dict with customer metrics (from CSV row)
        comm_insights: Dict from communication analyzer (possibly blended with CSM)

    Returns:
        Comprehensive score dict with all components and metadata
    """
    customer_name = customer_data['customer_name']

    # Calculate component scores
    traditional_score, traditional_breakdown = calculate_traditional_score(customer_data)
    communication_score, communication_breakdown = calculate_communication_score(
        comm_insights, customer_data
    )

    # Final composite score
    final_score = traditional_score + communication_score
    final_score = max(0, min(100, final_score))

    # Assign tier
    if final_score >= 80:
        tier = "HEALTHY"
        color = "green"
    elif final_score >= 60:
        tier = "ATTENTION NEEDED"
        color = "yellow"
    elif final_score >= 40:
        tier = "AT RISK"
        color = "orange"
    else:
        tier = "CRITICAL"
        color = "red"

    # Detect usage/communication divergence
    divergence_alert = None
    if traditional_score >= 45 and communication_score < 20:
        divergence_alert = (
            "HIGH RISK: Strong product usage but deteriorating relationship. "
            "Customer may churn despite good metrics."
        )
    elif traditional_score < 30 and communication_score >= 25:
        divergence_alert = (
            "ADOPTION ISSUE: Good relationship but low product engagement. "
            "Focus on driving usage."
        )

    # Calculate days to renewal
    try:
        renewal_date = datetime.strptime(customer_data['renewal_date'], '%Y-%m-%d')
        days_to_renewal = (renewal_date - datetime.now()).days
    except (ValueError, KeyError):
        days_to_renewal = -1

    # Extract CSM-related fields
    human_input_present = comm_insights.get('human_input_present', False)
    csm_sentiment = comm_insights.get('csm_sentiment') if human_input_present else None
    automated_sentiment = comm_insights.get('automated_sentiment') if human_input_present else None
    csm_reasoning = comm_insights.get('csm_reasoning') if human_input_present else None
    csm_name = comm_insights.get('csm_name') if human_input_present else None
    csm_confidence = comm_insights.get('csm_confidence') if human_input_present else None
    human_ai_divergence = comm_insights.get('human_ai_divergence', False)
    override_alert = comm_insights.get('override_alert', False)

    return {
        'customer': customer_name,
        'final_score': round(final_score, 1),
        'tier': tier,
        'color': color,
        'traditional_score': round(traditional_score, 1),
        'traditional_breakdown': traditional_breakdown,
        'communication_score': round(communication_score, 1),
        'communication_breakdown': communication_breakdown,
        'divergence_alert': divergence_alert,
        'risk_signals': comm_insights.get('risk_signals', []),
        'competitive_mentions': comm_insights.get('competitive_mentions', []),
        'value_indicators': comm_insights.get('value_indicators', []),
        'sentiment_trajectory': comm_insights.get('sentiment_trajectory', 'unknown'),
        'overall_sentiment': comm_insights.get('overall_sentiment', 0),
        'days_to_renewal': days_to_renewal,
        'arr': customer_data.get('arr', 0),
        'human_input_present': human_input_present,
        'csm_sentiment': csm_sentiment,
        'csm_name': csm_name,
        'csm_confidence': csm_confidence,
        'automated_sentiment': automated_sentiment,
        'csm_reasoning': csm_reasoning,
        'human_ai_divergence': human_ai_divergence,
        'override_alert': override_alert
    }
