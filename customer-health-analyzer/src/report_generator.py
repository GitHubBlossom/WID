"""
Report generator for customer health analysis.

Creates formatted text reports for individual customers and
intervention effectiveness dashboards.
"""

from typing import Dict, List, Optional


def generate_customer_report(
    customer_score: Dict,
    trend_analysis: Optional[Dict],
    risk_forecast: Dict,
    intervention_recommendations: List[Dict]
) -> str:
    """
    Generate a comprehensive customer health report.

    Args:
        customer_score: Dict from master_scorer
        trend_analysis: Dict from trend_analyzer or None
        risk_forecast: Dict from risk_forecaster
        intervention_recommendations: List of recommendation dicts

    Returns:
        Formatted string report
    """
    lines = []
    sep = "=" * 80

    # Header
    lines.append(sep)
    lines.append(f"CUSTOMER HEALTH REPORT: {customer_score['customer']}")
    lines.append(sep)
    lines.append("")
    lines.append(f"  OVERALL HEALTH SCORE: {customer_score['final_score']:.1f}/100 ({customer_score['tier']})")
    lines.append(f"  ARR: ${customer_score['arr']:,.0f}")
    lines.append(f"  Days to Renewal: {customer_score['days_to_renewal']}")
    lines.append("")

    # Renewal Risk Assessment
    lines.append(sep)
    lines.append("RENEWAL RISK ASSESSMENT:")
    lines.append(sep)
    lines.append(f"  ├─ Churn Probability: {risk_forecast['churn_probability_pct']:.0f}% ({risk_forecast['confidence_level']} confidence)")
    lines.append(f"  ├─ Revenue at Risk: ${risk_forecast['revenue_at_risk']:,.0f}")
    lines.append(f"  ├─ Decision Timeline: {risk_forecast['decision_timeline']}")
    lines.append(f"  └─ Urgency Level: {risk_forecast['urgency_level'].upper()}")
    lines.append("")

    if risk_forecast['primary_risk_factors']:
        lines.append(f"  Primary Risk Factors: {', '.join(risk_forecast['primary_risk_factors'])}")
        lines.append("")

    # Trend Analysis
    if trend_analysis and trend_analysis.get('has_sufficient_history'):
        lines.append(sep)
        lines.append("📈 SCORE TREND (Last 90 Days):")
        lines.append(sep)
        lines.append(f"  Current: {trend_analysis['current_score']:.0f}/100 ({customer_score['tier']})")

        if trend_analysis['score_30d_ago'] is not None:
            lines.append(f"  30 days ago: {trend_analysis['score_30d_ago']:.0f}/100")
        if trend_analysis['score_90d_ago'] is not None:
            lines.append(f"  90 days ago: {trend_analysis['score_90d_ago']:.0f}/100")

        if trend_analysis['change_90d'] is not None:
            lines.append(f"  Change: {trend_analysis['change_90d']:+.1f} points over 90 days ({trend_analysis['velocity_monthly']:+.1f} points/month)")

        lines.append(f"  Trend: {trend_analysis['trend_label']}")

        # Warning for rapid decline
        velocity = trend_analysis['velocity_monthly']
        if velocity < -3 and trend_analysis['change_90d'] is not None:
            lines.append("")
            lines.append(f"  ⚠️  WARNING: Customer has lost {abs(trend_analysis['change_90d']):.0f} points in 3 months.")
            current = trend_analysis['current_score']
            if velocity != 0:
                days_to_critical = max(0, int((current - 40) / abs(velocity) * 30))
                lines.append(f"  At current velocity, will reach CRITICAL tier in ~{days_to_critical} days.")
        lines.append("")

    # Score Breakdown
    tb = customer_score['traditional_breakdown']
    cb = customer_score['communication_breakdown']

    lines.append(sep)
    lines.append("SCORE BREAKDOWN:")
    lines.append(sep)
    lines.append(f"  ├─ Traditional Metrics: {customer_score['traditional_score']:.1f}/60")
    lines.append(f"  │  ├─ Product Usage: {tb['product_usage']:.1f}/25")
    lines.append(f"  │  ├─ Feature Adoption: {tb['feature_adoption']:.1f}/15")
    lines.append(f"  │  ├─ Support Health: {tb['support_health']:.1f}/10")
    lines.append(f"  │  └─ Responsiveness: {tb['responsiveness']:.1f}/10")
    lines.append("  │")
    lines.append(f"  └─ Communication Health: {customer_score['communication_score']:.1f}/40")
    lines.append(f"     ├─ Sentiment: {cb['sentiment_points']:.1f}/15")
    lines.append(f"     ├─ Engagement: {cb['engagement_points']:.1f}/10")
    lines.append(f"     ├─ Risk Penalty: {cb['risk_penalty']:.1f}")
    lines.append(f"     └─ Value Bonus: {cb['value_bonus']:.1f}/5")
    lines.append("")

    # Human/AI Sentiment Analysis
    if customer_score.get('human_input_present'):
        lines.append(sep)
        lines.append("📊 SENTIMENT ANALYSIS (Human + AI Blend):")
        lines.append(sep)
        lines.append(f"  Automated (AI): {customer_score['automated_sentiment']:.1f}/10 (from communication analysis)")
        lines.append(f"  CSM Assessment: {customer_score['csm_sentiment']:.1f}/10 ({customer_score['csm_name']} - {customer_score['csm_confidence']} confidence)")
        lines.append(f"  Blended Score: {customer_score['overall_sentiment']:.1f}/10")
        lines.append(f"  CSM Notes: \"{customer_score['csm_reasoning']}\"")

        if customer_score.get('human_ai_divergence'):
            magnitude = abs(customer_score['csm_sentiment'] - customer_score['automated_sentiment'])
            lines.append(f"  ⚠️  Human-AI Divergence: CSM rating differs by {magnitude:.1f} points from AI.")

        if customer_score.get('override_alert'):
            lines.append("  🚨 CSM OVERRIDE: CSM has flagged this as requiring manual attention.")

        lines.append("")

    # Divergence Alert
    if customer_score.get('divergence_alert'):
        lines.append(sep)
        lines.append("⚠️  CRITICAL INSIGHT:")
        lines.append(sep)
        lines.append(f"  {customer_score['divergence_alert']}")
        lines.append("")

    # Risk Signals
    risk_signals = customer_score.get('risk_signals', [])
    if risk_signals:
        lines.append(sep)
        lines.append("🚨 RISK SIGNALS DETECTED:")
        lines.append(sep)
        for signal in risk_signals:
            lines.append(f"  • {signal}")
        lines.append("")

    # Competitive Mentions
    competitive = customer_score.get('competitive_mentions', [])
    if competitive:
        lines.append(sep)
        lines.append("⚔️  COMPETITIVE PRESSURE:")
        lines.append(sep)
        for mention in competitive:
            lines.append(f"  • {mention}")
        lines.append("")

    # Value Indicators
    value = customer_score.get('value_indicators', [])
    if value:
        lines.append(sep)
        lines.append("✅ VALUE REALIZATION MOMENTS:")
        lines.append(sep)
        for indicator in value[:5]:
            lines.append(f"  • {indicator}")
        if len(value) > 5:
            lines.append(f"  ... and {len(value) - 5} more")
        lines.append("")

    # Sentiment Trend
    lines.append(f"  📊 SENTIMENT TREND: {customer_score.get('sentiment_trajectory', 'unknown')}")
    lines.append("")

    # Recommendations
    if intervention_recommendations:
        lines.append(sep)
        lines.append("💡 RECOMMENDED ACTIONS (Data-Driven):")
        lines.append(sep)
        for i, rec in enumerate(intervention_recommendations, 1):
            action = rec['recommended_action'].replace('_', ' ').title()
            lines.append(f"  {i}. {action} [{rec['urgency'].upper()}]")
            lines.append(f"     Risk Factor: {rec['risk_factor'].replace('_', ' ').title()}")
            lines.append(f"     Success Rate: {rec['expected_success_rate']:.0f}%")
            lines.append(f"     {rec['evidence']}")
            if rec['urgency'] in ('high', 'critical'):
                lines.append(f"     ⚠️  {rec['reasoning']}")
            lines.append("")

    # Forecast Methodology
    lines.append(sep)
    lines.append("📋 Risk Forecast Methodology:")
    lines.append(sep)
    lines.append(f"  {risk_forecast['forecast_basis']}")
    lines.append("")
    lines.append(sep)

    return "\n".join(lines)


def generate_effectiveness_dashboard(
    effectiveness_data: Dict,
    churn_stats: Dict
) -> str:
    """
    Generate an intervention effectiveness dashboard.

    Args:
        effectiveness_data: Dict from analyze_intervention_effectiveness
        churn_stats: Dict from calculate_historical_churn_rate_by_score

    Returns:
        Formatted string dashboard
    """
    lines = []
    sep = "=" * 80

    lines.append(sep)
    lines.append("INTERVENTION EFFECTIVENESS DASHBOARD")
    lines.append(sep)
    lines.append("")

    # Overall Summary
    total_interventions = sum(d['sample_size'] for d in effectiveness_data.values())
    total_successes = sum(
        int(d['sample_size'] * d['overall_success_rate'] / 100)
        for d in effectiveness_data.values()
    )
    overall_rate = (total_successes / total_interventions * 100) if total_interventions > 0 else 0

    lines.append("Overall Performance Summary:")
    lines.append(f"  ├─ Total Interventions Tracked: {total_interventions}")
    lines.append(f"  ├─ Overall Success Rate: {overall_rate:.0f}%")
    lines.append(f"  ├─ Total Renewals: {churn_stats['total_renewals']}")
    lines.append(f"  ├─ Total Churns: {churn_stats['total_churns']}")
    lines.append(f"  └─ Historical Churn Rate: {churn_stats['overall_churn_rate']*100:.1f}%")
    lines.append("")

    # Sort by success rate descending
    sorted_types = sorted(
        effectiveness_data.items(),
        key=lambda x: x[1]['overall_success_rate'],
        reverse=True
    )

    lines.append(sep)
    lines.append("Performance by Intervention Type:")
    lines.append(sep)

    for intervention_type, data in sorted_types:
        display_name = intervention_type.replace('_', ' ').title()
        lines.append("")
        lines.append(f"  {display_name}:")
        lines.append(f"    Success Rate: {data['overall_success_rate']:.1f}%")
        lines.append(f"    Avg Time to Outcome: {data['avg_days_to_outcome']:.0f} days")
        lines.append(f"    Sample Size: {data['sample_size']} interventions")

        if data['by_trigger']:
            lines.append("    Performance by Trigger:")
            for trigger, trigger_data in sorted(
                data['by_trigger'].items(),
                key=lambda x: x[1]['success_rate'],
                reverse=True
            ):
                trigger_display = trigger.replace('_', ' ').title()
                lines.append(
                    f"      • {trigger_display}: "
                    f"{trigger_data['success_rate']:.0f}% "
                    f"({trigger_data['sample_size']} cases)"
                )

    # Key Insights
    lines.append("")
    lines.append(sep)
    lines.append("KEY INSIGHTS:")
    lines.append(sep)

    if sorted_types:
        best = sorted_types[0]
        lines.append(f"  Most effective intervention: {best[0].replace('_', ' ').title()} ({best[1]['overall_success_rate']:.0f}%)")

        fastest = min(effectiveness_data.items(), key=lambda x: x[1]['avg_days_to_outcome'])
        lines.append(f"  Fastest resolution: {fastest[0].replace('_', ' ').title()} ({fastest[1]['avg_days_to_outcome']:.0f} days average)")

        most_common = max(effectiveness_data.items(), key=lambda x: x[1]['sample_size'])
        lines.append(f"  Highest volume: {most_common[0].replace('_', ' ').title()} ({most_common[1]['sample_size']} uses)")

    lines.append("")
    lines.append(sep)

    return "\n".join(lines)
