"""
Customer Health Analysis Platform - Main Orchestrator.

Analyzes customer health by combining traditional metrics with AI-powered
communication analysis, CSM manual judgment, trend tracking, risk forecasting,
and data-driven intervention recommendations.
"""

import pandas as pd
from pathlib import Path
import os
import sys
from dotenv import load_dotenv
from datetime import datetime

from traditional_scorer import calculate_traditional_score
from communication_analyzer import analyze_all_channels
from csm_input import load_csm_input, incorporate_csm_judgment
from communication_scorer import calculate_communication_score
from trend_analyzer import get_score_trend, save_score_to_history
from risk_forecaster import calculate_churn_probability
from intervention_tracker import (
    analyze_intervention_effectiveness,
    calculate_historical_churn_rate_by_score,
    recommend_intervention
)
from master_scorer import calculate_final_health_score
from report_generator import generate_customer_report, generate_effectiveness_dashboard


def main():
    """Main execution orchestrator."""
    # Load environment variables
    load_dotenv()

    # Verify API key
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("⚠️  ERROR: ANTHROPIC_API_KEY not found in .env file")
        print("Please add your API key to .env file")
        return

    print("=" * 80)
    print("CUSTOMER HEALTH ANALYSIS PLATFORM")
    print("=" * 80)
    print(f"Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Determine base directory (support running from src/ or project root)
    base_dir = Path(__file__).parent.parent
    data_dir = base_dir / 'data'
    output_dir = base_dir / 'output'

    # Load data
    print("\n📊 Loading data files...")
    try:
        customers_df = pd.read_csv(data_dir / 'customers.csv')
        print(f"  ✓ Loaded {len(customers_df)} customers")
    except FileNotFoundError:
        print("  ❌ ERROR: data/customers.csv not found")
        return

    try:
        interventions_df = pd.read_csv(data_dir / 'interventions.csv')
        print(f"  ✓ Loaded {len(interventions_df)} intervention records")
    except FileNotFoundError:
        print("  ❌ ERROR: data/interventions.csv not found")
        return

    try:
        manual_sentiment_df = pd.read_csv(data_dir / 'manual_sentiment.csv')
        print(f"  ✓ Loaded {len(manual_sentiment_df)} manual CSM assessments")
    except FileNotFoundError:
        manual_sentiment_df = pd.DataFrame()
        print("  ⚠️  No manual sentiment data found (optional)")

    try:
        score_history_df = pd.read_csv(data_dir / 'score_history.csv')
        print(f"  ✓ Loaded {len(score_history_df)} historical score records")
    except FileNotFoundError:
        score_history_df = None
        print("  ⚠️  No score history found (optional)")

    # Analyze intervention effectiveness
    print("\n🔍 Analyzing intervention effectiveness...")
    effectiveness_data = analyze_intervention_effectiveness(interventions_df)
    churn_stats = calculate_historical_churn_rate_by_score(interventions_df)
    print(f"  ✓ Analyzed {len(effectiveness_data)} intervention types")

    # Create output directory if needed
    output_dir.mkdir(exist_ok=True)

    # Analyze each customer
    all_scores = []
    total_customers = len(customers_df)

    for idx, customer in customers_df.iterrows():
        customer_name = customer['customer_name']
        print(f"\n{'=' * 80}")
        print(f"[{idx + 1}/{total_customers}] Analyzing: {customer_name}")
        print(f"{'=' * 80}")

        # Find customer data folder
        folder_name = customer_name.lower().replace(' ', '_').replace('.', '')
        customer_folder = data_dir / 'customers' / folder_name

        if not customer_folder.exists():
            print(f"  ⚠️  Warning: No communication data found for {customer_name}")
            print(f"     Expected folder: {customer_folder}")
            continue

        # Check if folder has any communication files
        comm_files = list(customer_folder.rglob('*.txt'))
        if not comm_files:
            print(f"  ⚠️  Warning: No communication files found in {customer_folder}")
            continue

        # Analyze all communication channels
        print("  📞 Analyzing communications across all channels...")
        try:
            comm_insights = analyze_all_channels(str(customer_folder))
            print(f"   ✓ Analyzed {comm_insights['total_communications_analyzed']} communications")
            print(f"   ✓ Sentiment: {comm_insights['overall_sentiment']:.1f}/10 ({comm_insights['sentiment_trajectory']})")
        except Exception as e:
            print(f"   ❌ Error analyzing communications: {str(e)}")
            continue

        # Check for CSM manual input
        if not manual_sentiment_df.empty:
            csm_input = load_csm_input(customer_name, manual_sentiment_df)
            if csm_input:
                print(f"  👤 Found manual CSM assessment:")
                print(f"     CSM: {csm_input['csm_name']}")
                print(f"     Score: {csm_input['manual_sentiment_score']}/10")
                print(f"     Confidence: {csm_input['confidence_level']}")
                comm_insights = incorporate_csm_judgment(comm_insights, csm_input)

        # Calculate final health score
        print("  📊 Calculating final health score...")
        customer_score = calculate_final_health_score(customer.to_dict(), comm_insights)
        print(f"   ✓ Score: {customer_score['final_score']:.1f}/100 ({customer_score['tier']})")

        # Get trend analysis
        trend_analysis = None
        if score_history_df is not None:
            trend_analysis = get_score_trend(customer_name, score_history_df)
            if trend_analysis and trend_analysis['has_sufficient_history']:
                print(f"  📈 Trend: {trend_analysis['trend_label']}")
                print(f"     Change (90d): {trend_analysis['change_90d']:+.1f} points")

        # Calculate churn risk forecast
        print("  🎯 Forecasting renewal risk...")
        risk_forecast = calculate_churn_probability(
            customer_score,
            trend_analysis,
            interventions_df
        )
        print(f"   ✓ Churn Probability: {risk_forecast['churn_probability_pct']:.0f}%")
        print(f"   ✓ Revenue at Risk: ${risk_forecast['revenue_at_risk']:,.0f}")
        print(f"   ✓ Urgency: {risk_forecast['urgency_level'].upper()}")

        # Get intervention recommendations
        print("  💡 Generating intervention recommendations...")
        recommendations = recommend_intervention(
            customer.to_dict(),
            comm_insights,
            risk_forecast,
            effectiveness_data
        )
        print(f"   ✓ Generated {len(recommendations)} recommendations")

        # Generate report
        report = generate_customer_report(
            customer_score,
            trend_analysis,
            risk_forecast,
            recommendations
        )

        # Save individual report
        report_filename = output_dir / f"{folder_name}_report.txt"
        with open(report_filename, 'w') as f:
            f.write(report)
        print(f"  ✅ Report saved: {report_filename.name}")

        all_scores.append({
            'score': customer_score,
            'trend': trend_analysis,
            'risk': risk_forecast,
            'recommendations': recommendations
        })

    if not all_scores:
        print("\n❌ No customers were successfully analyzed.")
        return

    # Generate effectiveness dashboard
    print("\n" + "=" * 80)
    print("📊 Generating intervention effectiveness dashboard...")
    dashboard = generate_effectiveness_dashboard(effectiveness_data, churn_stats)

    with open(output_dir / "intervention_effectiveness.txt", 'w') as f:
        f.write(dashboard)
    print("  ✓ Dashboard saved: intervention_effectiveness.txt")

    # Generate summary CSV
    summary_rows = []
    for s in all_scores:
        trend = s['trend']
        has_trend = trend and trend.get('has_sufficient_history')
        summary_rows.append({
            'customer': s['score']['customer'],
            'score': round(s['score']['final_score'], 1),
            'tier': s['score']['tier'],
            'traditional': round(s['score']['traditional_score'], 1),
            'communication': round(s['score']['communication_score'], 1),
            'churn_probability': round(s['risk']['churn_probability_pct'], 1),
            'revenue_at_risk': round(s['risk']['revenue_at_risk'], 0),
            'urgency': s['risk']['urgency_level'],
            'days_to_renewal': s['score']['days_to_renewal'],
            'trend': trend['trend_label'] if has_trend else 'N/A',
            'velocity_monthly': round(trend['velocity_monthly'], 1) if has_trend else 'N/A',
            'risk_count': len(s['score']['risk_signals']),
            'competitive_mentions': len(s['score']['competitive_mentions']),
            'value_indicators': len(s['score']['value_indicators']),
            'csm_input': s['score']['human_input_present'],
            'human_ai_divergence': s['score'].get('human_ai_divergence', False)
        })

    summary_df = pd.DataFrame(summary_rows)

    # Sort by urgency and churn probability
    urgency_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
    summary_df['urgency_rank'] = summary_df['urgency'].map(urgency_order)
    summary_df = summary_df.sort_values(
        ['urgency_rank', 'churn_probability'],
        ascending=[True, False]
    )
    summary_df = summary_df.drop('urgency_rank', axis=1)

    summary_df.to_csv(output_dir / 'customer_summary.csv', index=False)

    # Print final summary
    print("\n" + "=" * 80)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 80)
    print(f"\n📈 Processed {len(all_scores)} customers")
    print(f"💾 Reports saved to: {output_dir}/")
    print(f"\n📁 Files created:")
    print(f"  • Individual customer reports: output/*_report.txt")
    print(f"  • Summary CSV: output/customer_summary.csv")
    print(f"  • Effectiveness dashboard: output/intervention_effectiveness.txt")

    # Health Score Distribution
    print(f"\n📊 Health Score Distribution:")
    for tier in ['HEALTHY', 'ATTENTION NEEDED', 'AT RISK', 'CRITICAL']:
        count = len([s for s in all_scores if s['score']['tier'] == tier])
        if count > 0:
            print(f"  {tier}: {count} customers")

    # Urgency Distribution
    print(f"\n⚠️  Urgency Distribution:")
    for urgency in ['critical', 'high', 'medium', 'low']:
        count = len([s for s in all_scores if s['risk']['urgency_level'] == urgency])
        if count > 0:
            total_risk = sum([
                s['risk']['revenue_at_risk']
                for s in all_scores
                if s['risk']['urgency_level'] == urgency
            ])
            print(f"  {urgency.upper()}: {count} customers (${total_risk:,.0f} at risk)")

    total_revenue_at_risk = sum(s['risk']['revenue_at_risk'] for s in all_scores)
    print(f"\n💰 Total Revenue at Risk: ${total_revenue_at_risk:,.0f}")

    # Highlight critical accounts
    critical_accounts = [
        s for s in all_scores if s['risk']['urgency_level'] == 'critical'
    ]
    if critical_accounts:
        print(f"\n🚨 CRITICAL ACCOUNTS REQUIRING IMMEDIATE ATTENTION:")
        for acc in critical_accounts:
            print(
                f"  • {acc['score']['customer']}: "
                f"{acc['risk']['churn_probability_pct']:.0f}% churn risk, "
                f"${acc['risk']['revenue_at_risk']:,.0f} at risk"
            )


if __name__ == "__main__":
    main()
