"""
Communication analyzer using Anthropic Claude API.

Analyzes customer communications across all channels (calls, emails, slack, tickets)
to extract sentiment, risk signals, competitive mentions, and value indicators.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

import anthropic


def analyze_communication_channel(
    text: str,
    channel_type: str,
    customer_name: str,
    date: str
) -> Dict:
    """
    Analyze a single communication using the Anthropic API.

    Args:
        text: Communication content
        channel_type: One of 'call', 'email', 'slack', 'ticket'
        customer_name: Name of the customer
        date: Date of the communication

    Returns:
        Dict with structured analysis including sentiment, risk signals, etc.
    """
    client = anthropic.Anthropic()

    prompt = f"""Analyze this {channel_type} communication from customer {customer_name} on {date}.

Communication content:
{text}

Return ONLY a valid JSON object with these exact fields:
{{
    "sentiment_score": <number 1-10, where 10 is most positive>,
    "engagement_level": "<high|medium|low>",
    "tone": "<partnership|transactional|frustrated|satisfied>",
    "risk_signals": [<array of specific risk indicators found>],
    "value_indicators": [<array of value/ROI mentions with quotes>],
    "competitive_mentions": [<array of competitor names or evaluation language with quotes>],
    "key_concerns": [<array of main issues or blockers raised>],
    "action_items_mentioned": [<array of follow-ups discussed>],
    "product_feedback": "<positive|negative|mixed|none>",
    "response_quality": "<engaged|brief|delayed|none>"
}}

Risk signals to look for:
- Competitor names (Snyk, GitGuardian, etc.)
- Budget concerns ("CFO", "cost", "budget review")
- Evaluation language ("looking at alternatives", "getting quotes", "due diligence")
- Implementation blockers ("not working", "failing", "frustrated")
- Disengagement ("we'll see", "need to discuss", vague answers)

Value indicators to look for:
- ROI mentions ("saved us X", "prevented Y")
- Success stories ("helped us achieve", "team loves")
- Feature appreciation ("this is great", "exactly what we needed")
- Adoption mentions ("rolled out to entire team")

Be specific - quote actual phrases from the text when listing signals."""

    try:
        message = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'\{[\s\S]*\}', response_text)
        if json_match:
            response_text = json_match.group()

        analysis = json.loads(response_text)

        # Validate required fields
        required_fields = [
            'sentiment_score', 'engagement_level', 'tone', 'risk_signals',
            'value_indicators', 'competitive_mentions', 'key_concerns',
            'action_items_mentioned', 'product_feedback', 'response_quality'
        ]
        for field in required_fields:
            if field not in analysis:
                analysis[field] = [] if field in [
                    'risk_signals', 'value_indicators', 'competitive_mentions',
                    'key_concerns', 'action_items_mentioned'
                ] else 'unknown'

        # Ensure sentiment_score is numeric
        analysis['sentiment_score'] = float(analysis.get('sentiment_score', 5))
        analysis['channel_type'] = channel_type
        analysis['date'] = date
        analysis['customer_name'] = customer_name

        return analysis

    except json.JSONDecodeError as e:
        print(f"   ⚠️  JSON parse error for {customer_name} {channel_type} on {date}: {e}")
        return _default_analysis(channel_type, customer_name, date)
    except anthropic.APIError as e:
        print(f"   ⚠️  API error for {customer_name} {channel_type} on {date}: {e}")
        return _default_analysis(channel_type, customer_name, date)


def _default_analysis(channel_type: str, customer_name: str, date: str) -> Dict:
    """Return a default analysis when API call fails."""
    return {
        'sentiment_score': 5.0,
        'engagement_level': 'medium',
        'tone': 'transactional',
        'risk_signals': [],
        'value_indicators': [],
        'competitive_mentions': [],
        'key_concerns': [],
        'action_items_mentioned': [],
        'product_feedback': 'none',
        'response_quality': 'none',
        'channel_type': channel_type,
        'date': date,
        'customer_name': customer_name
    }


def analyze_all_channels(customer_folder: str) -> Dict:
    """
    Analyze all communication files for a customer across all channels.

    Args:
        customer_folder: Path to the customer's data folder

    Returns:
        Dict with aggregated insights across all channels
    """
    folder = Path(customer_folder)
    channel_map = {
        'transcripts': 'call',
        'emails': 'email',
        'slack': 'slack',
        'tickets': 'ticket'
    }

    all_analyses: List[Dict] = []

    for subfolder, channel_type in channel_map.items():
        channel_path = folder / subfolder
        if not channel_path.exists():
            continue

        for file_path in sorted(channel_path.glob('*.txt')):
            # Extract date from filename (format: YYYY-MM-DD_description.txt)
            date_match = re.match(r'(\d{4}-\d{2}-\d{2})', file_path.name)
            date = date_match.group(1) if date_match else 'unknown'

            try:
                text = file_path.read_text(encoding='utf-8')
            except Exception as e:
                print(f"   ⚠️  Error reading {file_path}: {e}")
                continue

            customer_name = folder.name.replace('_', ' ').title()
            print(f"   📄 Analyzing {channel_type}: {file_path.name}")

            analysis = analyze_communication_channel(text, channel_type, customer_name, date)
            all_analyses.append(analysis)

    if not all_analyses:
        return {
            'overall_sentiment': 5.0,
            'sentiment_trajectory': 'stable',
            'early_sentiment_avg': 5.0,
            'recent_sentiment_avg': 5.0,
            'risk_signals': [],
            'competitive_mentions': [],
            'competitive_pressure_score': 0,
            'value_indicators': [],
            'value_articulation_count': 0,
            'channel_sentiments': {},
            'cross_channel_divergence': False,
            'total_communications_analyzed': 0,
            'analyses': []
        }

    # Sort by date
    all_analyses.sort(key=lambda x: x.get('date', ''))

    # Calculate aggregations
    sentiments = [a['sentiment_score'] for a in all_analyses]
    overall_sentiment = sum(sentiments) / len(sentiments)

    # Sentiment trajectory: compare first half to second half
    mid = len(sentiments) // 2
    if mid > 0:
        early_avg = sum(sentiments[:mid]) / mid
        recent_avg = sum(sentiments[mid:]) / len(sentiments[mid:])
    else:
        early_avg = recent_avg = overall_sentiment

    if recent_avg - early_avg >= 0.5:
        trajectory = 'improving'
    elif early_avg - recent_avg >= 0.5:
        trajectory = 'declining'
    else:
        trajectory = 'stable'

    # Deduplicate risk signals and competitive mentions
    all_risk_signals = []
    all_competitive = []
    all_value = []

    for a in all_analyses:
        for signal in a.get('risk_signals', []):
            if signal not in all_risk_signals:
                all_risk_signals.append(signal)
        for mention in a.get('competitive_mentions', []):
            if mention not in all_competitive:
                all_competitive.append(mention)
        all_value.extend(a.get('value_indicators', []))

    competitive_pressure_score = min(len(all_competitive) * 5, 20)

    # Channel sentiments
    channel_sentiments: Dict[str, List[float]] = {}
    for a in all_analyses:
        ch = a['channel_type']
        if ch not in channel_sentiments:
            channel_sentiments[ch] = []
        channel_sentiments[ch].append(a['sentiment_score'])

    channel_avg = {ch: sum(scores) / len(scores) for ch, scores in channel_sentiments.items()}

    # Cross-channel divergence
    if len(channel_avg) > 1:
        cross_channel_divergence = (max(channel_avg.values()) - min(channel_avg.values())) > 3
    else:
        cross_channel_divergence = False

    return {
        'overall_sentiment': round(overall_sentiment, 2),
        'sentiment_trajectory': trajectory,
        'early_sentiment_avg': round(early_avg, 2),
        'recent_sentiment_avg': round(recent_avg, 2),
        'risk_signals': all_risk_signals,
        'competitive_mentions': all_competitive,
        'competitive_pressure_score': competitive_pressure_score,
        'value_indicators': all_value,
        'value_articulation_count': len(all_value),
        'channel_sentiments': channel_avg,
        'cross_channel_divergence': cross_channel_divergence,
        'total_communications_analyzed': len(all_analyses),
        'analyses': all_analyses
    }
