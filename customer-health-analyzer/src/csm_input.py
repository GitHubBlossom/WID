"""
CSM (Customer Success Manager) manual input handler.

Loads, blends, and saves CSM manual sentiment assessments
alongside automated AI analysis.
"""

import csv
import os
from datetime import datetime
from typing import Dict, Optional

import pandas as pd


def load_csm_input(customer_name: str, manual_sentiment_df: pd.DataFrame) -> Optional[Dict]:
    """
    Load the most recent CSM manual assessment for a customer.

    Args:
        customer_name: Name of the customer
        manual_sentiment_df: DataFrame of manual assessments

    Returns:
        Dict with CSM input or None if no assessment exists
    """
    if manual_sentiment_df.empty:
        return None

    customer_rows = manual_sentiment_df[
        manual_sentiment_df['customer_name'] == customer_name
    ]

    if customer_rows.empty:
        return None

    # Get most recent assessment
    customer_rows = customer_rows.copy()
    customer_rows['date'] = pd.to_datetime(customer_rows['date'])
    latest = customer_rows.sort_values('date', ascending=False).iloc[0]

    return {
        'csm_name': latest['csm_name'],
        'date': str(latest['date'].date()),
        'manual_sentiment_score': float(latest['manual_sentiment_score']),
        'confidence_level': latest['confidence_level'].lower(),
        'reasoning': latest['reasoning'],
        'override_flag': bool(latest['override_flag'])
    }


def incorporate_csm_judgment(automated_insights: Dict, csm_input: Optional[Dict]) -> Dict:
    """
    Blend CSM manual assessment with automated communication insights.

    Args:
        automated_insights: Dict from communication analyzer
        csm_input: Dict from load_csm_input or None

    Returns:
        Dict with blended analysis
    """
    if csm_input is None:
        automated_insights['human_input_present'] = False
        return automated_insights

    # Calculate blend weights based on confidence
    confidence = csm_input['confidence_level']
    if confidence == 'high':
        csm_weight = 0.6
    elif confidence == 'medium':
        csm_weight = 0.5
    else:  # low
        csm_weight = 0.3
    auto_weight = 1.0 - csm_weight

    auto_score = automated_insights['overall_sentiment']
    csm_score = csm_input['manual_sentiment_score']

    blended_sentiment = (csm_score * csm_weight) + (auto_score * auto_weight)

    # Detect divergence
    divergence_magnitude = abs(csm_score - auto_score)
    human_ai_divergence = divergence_magnitude > 2.5

    # Override alert
    override_alert = csm_input['override_flag']

    # Update insights with blended data
    result = automated_insights.copy()
    result.update({
        'overall_sentiment': round(blended_sentiment, 2),
        'automated_sentiment': auto_score,
        'csm_sentiment': csm_score,
        'csm_name': csm_input['csm_name'],
        'csm_confidence': confidence,
        'csm_reasoning': csm_input['reasoning'],
        'csm_weight_applied': csm_weight,
        'human_ai_divergence': human_ai_divergence,
        'divergence_magnitude': round(divergence_magnitude, 2),
        'override_alert': override_alert,
        'human_input_present': True
    })

    return result


def save_csm_input(
    customer_name: str,
    csm_name: str,
    sentiment_score: float,
    confidence: str,
    reasoning: str,
    override: bool,
    filepath: str
) -> None:
    """
    Append a new CSM manual assessment to the CSV file.

    Args:
        customer_name: Name of the customer
        csm_name: Name of the CSM
        sentiment_score: Manual sentiment score (1-10)
        confidence: Confidence level (low/medium/high)
        reasoning: CSM's reasoning text
        override: Whether to override automated score
        filepath: Path to manual_sentiment.csv
    """
    date = datetime.now().strftime('%Y-%m-%d')
    file_exists = os.path.exists(filepath)

    with open(filepath, 'a', newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                'customer_name', 'date', 'csm_name', 'manual_sentiment_score',
                'confidence_level', 'reasoning', 'override_flag'
            ])
        writer.writerow([
            customer_name, date, csm_name, sentiment_score,
            confidence, reasoning, override
        ])
