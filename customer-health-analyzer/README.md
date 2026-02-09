# Customer Health Analyzer

An AI-powered customer health scoring platform that goes beyond traditional metrics by analyzing multi-channel communications, blending CSM human judgment with AI insights, tracking score trends over time, forecasting renewal risk, and recommending data-driven interventions.

## Why This Exists

Enterprise customer success platforms (Gainsight, Totango, ChurnZero) rely primarily on product usage metrics and CRM data to calculate health scores. They miss a critical dimension: **what customers are actually saying** across calls, emails, Slack, and support tickets.

A customer can have perfect usage metrics while simultaneously evaluating competitors, expressing budget concerns, and showing declining engagement in communications. Traditional health scores miss this entirely. This platform catches it.

## What It Does

### 1. Traditional Metrics Scoring (0-60 points)
Analyzes product usage, feature adoption, support health, and responsiveness using configurable scoring rules.

### 2. AI-Powered Communication Analysis (0-40 points)
Uses Claude to analyze call transcripts, emails, Slack messages, and support tickets for sentiment, risk signals, competitive mentions, and value indicators.

### 3. CSM Human Judgment Blending
Incorporates manual CSM assessments with configurable confidence-based weighting. Detects human-AI divergence and supports CSM override for situations only humans can detect (off-record conversations, body language, industry intel).

### 4. Usage-Communication Divergence Detection
Identifies dangerous patterns where metrics look healthy but communications reveal risk (the "silent churn" problem), or where relationships are strong but product adoption lags.

### 5. Score Trend Tracking
Monitors health scores over time, calculates velocity (points/month), and labels trends from "DECLINING RAPIDLY" to "IMPROVING RAPIDLY."

### 6. Renewal Risk Forecasting
Calculates churn probability using score bands, trend velocity, risk factors (competitive mentions, CSM overrides), and days-to-renewal urgency. Shows revenue at risk and decision timeline.

### 7. Intervention Effectiveness Tracking
Analyzes historical intervention outcomes to calculate success rates by intervention type and trigger reason. Identifies what works and what doesn't.

### 8. Data-Driven Intervention Recommendations
Recommends specific actions based on identified risk factors and historical success rates, with urgency-aware prioritization.

## Quick Start

### Prerequisites
- Python 3.9+
- Anthropic API key

### Setup

```bash
cd customer-health-analyzer
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### Run Analysis

```bash
cd src
python main.py
```

### Add CSM Assessment

```bash
cd src
python csm_input_cli.py
```

## Example Output

### Individual Customer Report
```
================================================================================
CUSTOMER HEALTH REPORT: Acme Corp
================================================================================
  OVERALL HEALTH SCORE: 62.5/100 (ATTENTION NEEDED)
  ARR: $75,000
  Days to Renewal: 75

RENEWAL RISK ASSESSMENT:
  ├─ Churn Probability: 55% (high confidence)
  ├─ Revenue at Risk: $41,250
  ├─ Decision Timeline: Entering decision window
  └─ Urgency Level: HIGH

⚠️  CRITICAL INSIGHT:
  HIGH RISK: Strong product usage but deteriorating relationship.
  Customer may churn despite good metrics.

🚨 RISK SIGNALS DETECTED:
  • Customer mentioned evaluating Snyk and GitGuardian
  • CFO initiated vendor consolidation review
  • Budget concerns raised in recent calls

💡 RECOMMENDED ACTIONS (Data-Driven):
  1. Executive Call [HIGH]
     Risk Factor: Competitive Mention
     Success Rate: 68%
     Based on 8 historical interventions
```

### Summary Dashboard
The platform generates a CSV summary sorted by urgency, showing all customers with their scores, churn probability, revenue at risk, and trend data.

## Project Structure

```
customer-health-analyzer/
├── data/
│   ├── customers/          # Per-customer communication files
│   │   ├── acme_corp/
│   │   │   ├── transcripts/
│   │   │   ├── emails/
│   │   │   ├── slack/
│   │   │   └── tickets/
│   │   └── ...
│   ├── customers.csv       # Customer metrics
│   ├── interventions.csv   # Historical interventions
│   ├── manual_sentiment.csv # CSM assessments
│   └── score_history.csv   # Historical scores
├── src/
│   ├── main.py                  # Orchestrator
│   ├── traditional_scorer.py    # Usage metrics scoring
│   ├── communication_analyzer.py # AI communication analysis
│   ├── communication_scorer.py  # Communication scoring
│   ├── csm_input.py            # CSM judgment blending
│   ├── csm_input_cli.py        # CSM input CLI
│   ├── master_scorer.py        # Final score calculation
│   ├── trend_analyzer.py       # Score trend tracking
│   ├── risk_forecaster.py      # Churn probability forecast
│   ├── intervention_tracker.py # Intervention analysis
│   └── report_generator.py     # Report formatting
├── output/                 # Generated reports
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Technology Stack

- **AI Analysis**: Anthropic Claude API (claude-sonnet-4-5-20250929)
- **Data Processing**: pandas
- **Configuration**: python-dotenv
- **Language**: Python 3.9+

## Key Differentiators vs Enterprise Platforms

| Feature | Gainsight/Totango | This Platform |
|---------|------------------|---------------|
| Usage Metrics | ✅ | ✅ |
| Communication Sentiment | ❌ (manual only) | ✅ AI-powered |
| Competitive Mention Detection | ❌ | ✅ Automatic |
| Human-AI Judgment Blending | ❌ | ✅ Configurable |
| Usage-Comm Divergence | ❌ | ✅ Automatic alerts |
| Intervention ROI Tracking | Basic | ✅ By type & trigger |
| Risk Forecasting | Rule-based | ✅ Multi-factor model |

## Roadmap

- [ ] Web dashboard with interactive visualizations
- [ ] Real-time Slack/email integration (no manual file drops)
- [ ] CRM integration (Salesforce, HubSpot)
- [ ] Multi-language communication support
- [ ] Automated alert system for score drops
- [ ] A/B testing framework for intervention strategies
- [ ] ML-based churn prediction model training on historical data

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.
