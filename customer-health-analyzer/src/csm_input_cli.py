"""
CLI interface for CSM manual sentiment input.

Provides a simple command-line tool for Customer Success Managers
to record their manual sentiment assessments for customers.
"""

import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from csm_input import save_csm_input


def collect_csm_assessment() -> None:
    """Collect and save a CSM manual sentiment assessment via CLI."""
    print("\n=== CSM Manual Sentiment Input ===\n")

    customer_name = input("Customer name: ").strip()
    if not customer_name:
        print("Error: Customer name is required.")
        return

    csm_name = input("Your name: ").strip()
    if not csm_name:
        print("Error: CSM name is required.")
        return

    while True:
        try:
            sentiment = float(input("Your sentiment score (1-10): "))
            if 1 <= sentiment <= 10:
                break
            print("Please enter a number between 1 and 10")
        except ValueError:
            print("Please enter a valid number")

    confidence = input("Confidence level (low/medium/high): ").lower().strip()
    while confidence not in ['low', 'medium', 'high']:
        confidence = input("Please enter 'low', 'medium', or 'high': ").lower().strip()

    reasoning = input("Your reasoning: ").strip()

    override = input("Override automated score? (y/n): ").lower().strip() == 'y'

    # Determine filepath relative to project root
    filepath = Path(__file__).parent.parent / 'data' / 'manual_sentiment.csv'

    save_csm_input(
        customer_name, csm_name, sentiment, confidence,
        reasoning, override, str(filepath)
    )

    print(f"\n✅ Assessment saved for {customer_name}")
    print(f"   Score: {sentiment}/10 | Confidence: {confidence} | Override: {override}")


if __name__ == "__main__":
    collect_csm_assessment()
