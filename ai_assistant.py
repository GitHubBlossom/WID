"""
AI Assistant for generating insights and to-dos using Anthropic's Claude.
"""

import os
from typing import List, Dict, Tuple
from datetime import datetime
import anthropic

from models import Activity, WeeklyGoal


class AIAssistant:
    """AI assistant for productivity insights and to-do generation."""

    def __init__(self):
        """Initialize the AI assistant."""
        api_key = os.environ.get('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"

    def generate_insights_and_todos(
        self,
        activities: List[Activity],
        goals: List[WeeklyGoal],
        week_start: str
    ) -> Tuple[List[Dict], List[Dict]]:
        """Generate AI insights and to-dos based on activities and goals.

        Args:
            activities: List of activities for the week
            goals: List of weekly goals
            week_start: ISO format date string for week start

        Returns:
            Tuple of (insights_list, todos_list)
        """
        # Prepare context for AI
        context = self._prepare_context(activities, goals, week_start)

        # Generate insights and todos using Claude
        prompt = self._build_prompt(context)

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse the response
            insights, todos = self._parse_response(response.content[0].text)

            return insights, todos

        except Exception as e:
            print(f"Error generating insights: {e}")
            return [], []

    def _prepare_context(
        self,
        activities: List[Activity],
        goals: List[WeeklyGoal],
        week_start: str
    ) -> Dict:
        """Prepare context data for AI analysis.

        Args:
            activities: List of activities
            goals: List of goals
            week_start: Week start date

        Returns:
            Dictionary with context information
        """
        # Calculate activity statistics
        total_hours = sum(a.duration_minutes or 0 for a in activities) / 60

        category_breakdown = {}
        for activity in activities:
            cat = activity.category
            if cat not in category_breakdown:
                category_breakdown[cat] = {'count': 0, 'hours': 0}
            category_breakdown[cat]['count'] += 1
            category_breakdown[cat]['hours'] += (activity.duration_minutes or 0) / 60

        source_breakdown = {}
        for activity in activities:
            src = activity.source
            source_breakdown[src] = source_breakdown.get(src, 0) + 1

        # Goal analysis
        goals_by_status = {}
        for goal in goals:
            status = goal.status
            goals_by_status[status] = goals_by_status.get(status, 0) + 1

        return {
            'week_start': week_start,
            'total_activities': len(activities),
            'total_hours': round(total_hours, 1),
            'category_breakdown': category_breakdown,
            'source_breakdown': source_breakdown,
            'activities': [
                {
                    'title': a.title,
                    'description': a.description,
                    'category': a.category,
                    'date': a.date,
                    'duration_minutes': a.duration_minutes
                }
                for a in activities[:50]  # Limit to 50 most recent
            ],
            'goals': [
                {
                    'title': g.title,
                    'description': g.description,
                    'status': g.status,
                    'target_hours': g.target_hours,
                    'actual_hours': g.actual_hours
                }
                for g in goals
            ],
            'goals_by_status': goals_by_status
        }

    def _build_prompt(self, context: Dict) -> str:
        """Build the prompt for Claude.

        Args:
            context: Context dictionary

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are an AI productivity assistant analyzing a user's weekly activities and goals.

Week Starting: {context['week_start']}

ACTIVITY SUMMARY:
- Total Activities: {context['total_activities']}
- Total Time Tracked: {context['total_hours']} hours

Category Breakdown:
"""

        for category, stats in context['category_breakdown'].items():
            prompt += f"- {category}: {stats['count']} activities, {stats['hours']:.1f} hours\n"

        prompt += f"\nActivity Sources:\n"
        for source, count in context['source_breakdown'].items():
            prompt += f"- {source}: {count} activities\n"

        prompt += f"\nWEEKLY GOALS ({len(context['goals'])} total):\n"
        for goal in context['goals']:
            prompt += f"- [{goal['status']}] {goal['title']}: {goal['description']}\n"
            if goal.get('target_hours'):
                prompt += f"  Target: {goal['target_hours']} hours"
                if goal.get('actual_hours'):
                    prompt += f" | Actual: {goal['actual_hours']} hours"
                prompt += "\n"

        prompt += f"\nRECENT ACTIVITIES:\n"
        for activity in context['activities'][:20]:  # Show top 20
            desc = f": {activity['description'][:100]}" if activity['description'] else ""
            duration = f" ({activity['duration_minutes']}min)" if activity['duration_minutes'] else ""
            prompt += f"- [{activity['date']}] {activity['title']}{desc}{duration}\n"

        prompt += """
Based on this data, please provide:

1. INSIGHTS (3-5 key insights about productivity patterns, time usage, and progress):
   - Identify patterns in work habits
   - Note achievements and areas of focus
   - Compare progress against goals
   - Highlight any concerning trends or positive developments

2. ACTION ITEMS (5-8 specific, actionable to-dos for next week):
   - Prioritize based on goals and current progress
   - Make them specific and measurable
   - Include items to address any gaps or issues identified

Format your response as JSON with this structure:
{
  "insights": [
    {
      "insight_type": "summary|pattern|recommendation",
      "title": "Brief title",
      "content": "Detailed insight",
      "confidence": 0.0-1.0
    }
  ],
  "todos": [
    {
      "title": "Action item title",
      "description": "Detailed description",
      "priority": "high|medium|low"
    }
  ]
}
"""

        return prompt

    def _parse_response(self, response_text: str) -> Tuple[List[Dict], List[Dict]]:
        """Parse Claude's response to extract insights and todos.

        Args:
            response_text: Raw response text from Claude

        Returns:
            Tuple of (insights, todos)
        """
        import json
        import re

        # Extract JSON from the response (handle code blocks)
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON without code blocks
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                print("Could not find JSON in response")
                return [], []

        try:
            data = json.loads(json_str)
            insights = data.get('insights', [])
            todos = data.get('todos', [])

            return insights, todos

        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response: {response_text[:500]}")
            return [], []

    def generate_weekly_summary(self, activities: List[Activity], goals: List[WeeklyGoal]) -> str:
        """Generate a natural language summary of the week.

        Args:
            activities: List of activities
            goals: List of goals

        Returns:
            Summary text
        """
        context = self._prepare_context(activities, goals, "")

        prompt = f"""Provide a brief, encouraging weekly summary (2-3 paragraphs) for a user based on:

- Total Activities: {context['total_activities']}
- Hours Tracked: {context['total_hours']}
- Goals: {len(goals)} ({context['goals_by_status'].get('completed', 0)} completed)

Category breakdown:
{context['category_breakdown']}

Make it personal, positive, and actionable. Focus on achievements and constructive suggestions.
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            print(f"Error generating summary: {e}")
            return "Unable to generate summary at this time."
