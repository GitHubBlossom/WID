"""
Traditional metrics scorer for customer health analysis.

Calculates health scores based on product usage, feature adoption,
support health, and responsiveness metrics.
"""

from typing import Dict, Tuple


def calculate_traditional_score(customer_data: Dict) -> Tuple[float, Dict]:
    """
    Calculate traditional health score from customer metrics.

    Args:
        customer_data: Dict with keys: logins_30d, scans_30d, features_used,
                       tickets_30d, last_response_days

    Returns:
        Tuple of (total_score: float 0-60, breakdown: dict)
    """
    # Product Usage (25 points total)
    logins_30d = customer_data.get('logins_30d', 0)
    scans_30d = customer_data.get('scans_30d', 0)

    login_score = min(15, (logins_30d / 20) * 15)
    scan_score = min(10, (scans_30d / 60) * 10)
    usage_score = login_score + scan_score

    # Feature Adoption (15 points)
    features_used = customer_data.get('features_used', 0)
    feature_score = min(15, (features_used / 10) * 15)

    # Support Health (10 points)
    tickets_30d = customer_data.get('tickets_30d', 0)
    if 2 <= tickets_30d <= 5:
        support_score = 10.0
    elif tickets_30d < 2:
        support_score = 5.0
    else:
        support_score = max(0, 10 - (tickets_30d - 5))

    # Responsiveness (10 points)
    last_response_days = customer_data.get('last_response_days', 999)
    if last_response_days <= 2:
        responsiveness_score = 10.0
    elif last_response_days <= 5:
        responsiveness_score = 7.0
    elif last_response_days <= 10:
        responsiveness_score = 4.0
    else:
        responsiveness_score = 0.0

    total_score = usage_score + feature_score + support_score + responsiveness_score
    total_score = min(60, max(0, total_score))

    breakdown = {
        'product_usage': round(usage_score, 2),
        'login_score': round(login_score, 2),
        'scan_score': round(scan_score, 2),
        'feature_adoption': round(feature_score, 2),
        'support_health': round(support_score, 2),
        'responsiveness': round(responsiveness_score, 2),
        'total': round(total_score, 2)
    }

    return total_score, breakdown
