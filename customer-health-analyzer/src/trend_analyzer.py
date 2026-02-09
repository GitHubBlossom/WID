"""
Score trend analyzer.

Tracks health score changes over time, calculates velocity,
and labels trends for risk assessment.
"""

import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import pandas as pd


def get_score_trend(
    customer_name: str,
    history_df: pd.DataFrame,
    days: int = 90
) -> Optional[Dict]:
    """
    Analyze score trend for a customer over a given time period.

    Args:
        customer_name: Name of the customer
        history_df: DataFrame with columns: customer_name, date, traditional_score,
                    communication_score, final_score, tier
        days: Lookback period in days (default 90)

    Returns:
        Dict with trend analysis or None if insufficient history
    """
    customer_history = history_df[
        history_df['customer_name'] == customer_name
    ].copy()

    if customer_history.empty:
        return None

    customer_history['date'] = pd.to_datetime(customer_history['date'])
    customer_history = customer_history.sort_values('date', ascending=False)

    if len(customer_history) < 2:
        return None

    # Current score (most recent)
    current = customer_history.iloc[0]
    current_score = float(current['final_score'])
    current_date = current['date']

    # Find score closest to 30 days ago
    target_30d = current_date - timedelta(days=30)
    score_30d = _find_closest_score(customer_history, target_30d)

    # Find score closest to 90 days ago
    target_90d = current_date - timedelta(days=days)
    score_90d = _find_closest_score(customer_history, target_90d)

    # Calculate changes
    change_30d = (current_score - score_30d['score']) if score_30d else None
    change_90d = (current_score - score_90d['score']) if score_90d else None

    # Calculate velocity (points per month over 90 days)
    if change_90d is not None:
        velocity_monthly = change_90d / 3.0
    elif change_30d is not None:
        velocity_monthly = change_30d
    else:
        velocity_monthly = 0.0

    # Determine trend label
    trend_label = _get_trend_label(velocity_monthly)

    # Build historical scores list
    historical_scores = [
        {
            'date': str(row['date'].date()),
            'score': float(row['final_score']),
            'traditional': float(row['traditional_score']),
            'communication': float(row['communication_score']),
            'tier': row['tier']
        }
        for _, row in customer_history.iterrows()
    ]

    return {
        'customer': customer_name,
        'current_score': current_score,
        'current_date': str(current_date.date()),
        'score_30d_ago': score_30d['score'] if score_30d else None,
        'date_30d_ago': score_30d['date'] if score_30d else None,
        'score_90d_ago': score_90d['score'] if score_90d else None,
        'date_90d_ago': score_90d['date'] if score_90d else None,
        'change_30d': round(change_30d, 1) if change_30d is not None else None,
        'change_90d': round(change_90d, 1) if change_90d is not None else None,
        'velocity_monthly': round(velocity_monthly, 1),
        'trend_label': trend_label,
        'has_sufficient_history': len(customer_history) >= 2,
        'historical_scores': historical_scores
    }


def _find_closest_score(
    history: pd.DataFrame,
    target_date: pd.Timestamp
) -> Optional[Dict]:
    """Find the score entry closest to a target date."""
    if history.empty:
        return None

    diffs = abs(history['date'] - target_date)
    closest_idx = diffs.idxmin()
    closest = history.loc[closest_idx]

    # Only return if within 45 days of target (reasonable proximity)
    if abs((closest['date'] - target_date).days) > 45:
        return None

    return {
        'score': float(closest['final_score']),
        'date': str(closest['date'].date())
    }


def _get_trend_label(velocity: float) -> str:
    """Determine trend label from monthly velocity."""
    if velocity < -5:
        return "DECLINING RAPIDLY"
    elif velocity < -2:
        return "DECLINING"
    elif velocity < -0.5:
        return "SLIGHTLY DECLINING"
    elif velocity <= 0.5:
        return "STABLE"
    elif velocity <= 2:
        return "SLIGHTLY IMPROVING"
    elif velocity <= 5:
        return "IMPROVING"
    else:
        return "IMPROVING RAPIDLY"


def save_score_to_history(
    customer_score: Dict,
    history_file: str = 'data/score_history.csv'
) -> None:
    """
    Append current score to the score history CSV.

    Args:
        customer_score: Dict from master_scorer with score data
        history_file: Path to score_history.csv
    """
    date = datetime.now().strftime('%Y-%m-%d')
    file_exists = os.path.exists(history_file)

    with open(history_file, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                'customer_name', 'date', 'traditional_score',
                'communication_score', 'final_score', 'tier'
            ])
        writer.writerow([
            customer_score['customer'],
            date,
            round(customer_score['traditional_score'], 1),
            round(customer_score['communication_score'], 1),
            round(customer_score['final_score'], 1),
            customer_score['tier']
        ])
