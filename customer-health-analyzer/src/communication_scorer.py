"""
Communication health scorer.

Converts communication analysis insights into a numerical score (0-40)
that complements the traditional metrics score.
"""

from typing import Dict, Tuple


def calculate_communication_score(
    comm_insights: Dict,
    customer_data: Dict
) -> Tuple[float, Dict]:
    """
    Calculate communication health score from analyzed insights.

    Args:
        comm_insights: Dict from communication_analyzer (possibly blended with CSM input)
        customer_data: Dict with customer metrics

    Returns:
        Tuple of (score: float 0-40, breakdown: dict)
    """
    # Sentiment (15 points)
    overall_sentiment = comm_insights.get('overall_sentiment', 5.0)
    sentiment_points = (overall_sentiment / 10) * 15

    # Engagement (10 points)
    total_comms = comm_insights.get('total_communications_analyzed', 0)
    if total_comms >= 5:
        freq_points = 5.0
    elif total_comms >= 3:
        freq_points = 3.0
    else:
        freq_points = 0.0

    # Channel diversity
    channel_sentiments = comm_insights.get('channel_sentiments', {})
    num_channels = len(channel_sentiments)
    if num_channels >= 3:
        diversity_points = 3.0
    elif num_channels == 2:
        diversity_points = 2.0
    else:
        diversity_points = 0.0

    # Sentiment trajectory
    trajectory = comm_insights.get('sentiment_trajectory', 'stable')
    if trajectory == 'improving':
        trajectory_points = 2.0
    elif trajectory == 'declining':
        trajectory_points = -2.0
    else:
        trajectory_points = 0.0

    engagement_points = max(0, min(10, freq_points + diversity_points + trajectory_points))

    # Risk Penalty (up to -10 points)
    competitive_pressure = comm_insights.get('competitive_pressure_score', 0)
    risk_signals = comm_insights.get('risk_signals', [])
    cross_channel_div = comm_insights.get('cross_channel_divergence', False)

    penalty = 0.0
    penalty += competitive_pressure * 0.5
    penalty += len(risk_signals) * 2
    if cross_channel_div:
        penalty += 3
    risk_penalty = min(penalty, 10)

    # Value Bonus (up to +5 points)
    value_count = comm_insights.get('value_articulation_count', 0)
    value_bonus = min(value_count * 1.5, 5)

    # Final score
    total = sentiment_points + engagement_points - risk_penalty + value_bonus
    total = max(0, min(40, total))

    breakdown = {
        'sentiment_points': round(sentiment_points, 2),
        'engagement_points': round(engagement_points, 2),
        'frequency_points': round(freq_points, 2),
        'diversity_points': round(diversity_points, 2),
        'trajectory_points': round(trajectory_points, 2),
        'risk_penalty': round(-risk_penalty, 2),
        'competitive_pressure_component': round(competitive_pressure * 0.5, 2),
        'risk_signal_component': round(len(risk_signals) * 2, 2),
        'value_bonus': round(value_bonus, 2),
        'total': round(total, 2)
    }

    # Add human input details if present
    if comm_insights.get('human_input_present', False):
        breakdown['csm_sentiment_used'] = comm_insights.get('csm_sentiment')
        breakdown['automated_sentiment_used'] = comm_insights.get('automated_sentiment')
        breakdown['blend_weight'] = comm_insights.get('csm_weight_applied')
        breakdown['human_ai_divergence'] = comm_insights.get('human_ai_divergence', False)

    return total, breakdown
