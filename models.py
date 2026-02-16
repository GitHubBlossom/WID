"""
Data models and JSON structure definitions for What I Did productivity tracker.

This module defines the data structures for:
- Daily activities (manual and auto-collected)
- Weekly goals
- AI-generated insights and to-dos
"""

from dataclasses import dataclass, asdict
from datetime import datetime, date
from typing import List, Dict, Optional, Any
from enum import Enum
import json
from pathlib import Path


class ActivitySource(Enum):
    """Source of an activity entry."""
    MANUAL = "manual"
    GMAIL = "gmail"
    CALENDAR = "calendar"
    DRIVE = "drive"


class ActivityCategory(Enum):
    """Category of activity."""
    WORK = "work"
    MEETING = "meeting"
    EMAIL = "email"
    DOCUMENT = "document"
    LEARNING = "learning"
    PERSONAL = "personal"
    OTHER = "other"


class GoalStatus(Enum):
    """Status of a weekly goal."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class Activity:
    """Represents a single activity entry."""
    id: str
    date: str  # ISO format: YYYY-MM-DD
    timestamp: str  # ISO format: YYYY-MM-DDTHH:MM:SS
    title: str
    description: str
    category: str  # ActivityCategory value
    source: str  # ActivitySource value
    duration_minutes: Optional[int] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None  # Additional source-specific data

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'Activity':
        """Create Activity from dictionary."""
        return Activity(**data)


@dataclass
class WeeklyGoal:
    """Represents a weekly goal."""
    id: str
    week_start: str  # ISO format: YYYY-MM-DD (Monday)
    title: str
    description: str
    status: str  # GoalStatus value
    created_at: str  # ISO format timestamp
    updated_at: str  # ISO format timestamp
    completed_at: Optional[str] = None
    target_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    related_activities: List[str] = None  # Activity IDs

    def __post_init__(self):
        if self.related_activities is None:
            self.related_activities = []

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'WeeklyGoal':
        """Create WeeklyGoal from dictionary."""
        return WeeklyGoal(**data)


@dataclass
class Insight:
    """Represents an AI-generated insight."""
    id: str
    generated_at: str  # ISO format timestamp
    week_start: str  # ISO format: YYYY-MM-DD
    insight_type: str  # "summary", "pattern", "recommendation"
    title: str
    content: str
    confidence: float  # 0.0 to 1.0
    related_activities: List[str] = None  # Activity IDs
    related_goals: List[str] = None  # Goal IDs

    def __post_init__(self):
        if self.related_activities is None:
            self.related_activities = []
        if self.related_goals is None:
            self.related_goals = []

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'Insight':
        """Create Insight from dictionary."""
        return Insight(**data)


@dataclass
class ToDo:
    """Represents an AI-generated to-do item."""
    id: str
    generated_at: str  # ISO format timestamp
    title: str
    description: str
    priority: str  # "high", "medium", "low"
    status: str  # "pending", "in_progress", "completed", "dismissed"
    due_date: Optional[str] = None  # ISO format: YYYY-MM-DD
    completed_at: Optional[str] = None
    related_goals: List[str] = None  # Goal IDs
    related_insights: List[str] = None  # Insight IDs

    def __post_init__(self):
        if self.related_goals is None:
            self.related_goals = []
        if self.related_insights is None:
            self.related_insights = []

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @staticmethod
    def from_dict(data: dict) -> 'ToDo':
        """Create ToDo from dictionary."""
        return ToDo(**data)


class DataStore:
    """Handles reading and writing data to JSON files."""

    def __init__(self, data_dir: str = "data"):
        """Initialize the data store.

        Args:
            data_dir: Directory to store JSON files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        self.activities_file = self.data_dir / "activities.json"
        self.goals_file = self.data_dir / "goals.json"
        self.insights_file = self.data_dir / "insights.json"
        self.todos_file = self.data_dir / "todos.json"

        # Initialize files if they don't exist
        self._init_file(self.activities_file, [])
        self._init_file(self.goals_file, [])
        self._init_file(self.insights_file, [])
        self._init_file(self.todos_file, [])

    def _init_file(self, filepath: Path, default_data: Any):
        """Initialize a JSON file with default data if it doesn't exist."""
        if not filepath.exists():
            with open(filepath, 'w') as f:
                json.dump(default_data, f, indent=2)

    def _read_json(self, filepath: Path) -> Any:
        """Read and parse a JSON file."""
        with open(filepath, 'r') as f:
            return json.load(f)

    def _write_json(self, filepath: Path, data: Any):
        """Write data to a JSON file."""
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    # Activities
    def get_activities(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Activity]:
        """Get activities, optionally filtered by date range."""
        data = self._read_json(self.activities_file)
        activities = [Activity.from_dict(a) for a in data]

        if start_date or end_date:
            activities = [
                a for a in activities
                if (not start_date or a.date >= start_date) and
                   (not end_date or a.date <= end_date)
            ]

        return sorted(activities, key=lambda x: x.timestamp, reverse=True)

    def get_activity(self, activity_id: str) -> Optional[Activity]:
        """Get a specific activity by ID."""
        data = self._read_json(self.activities_file)
        for item in data:
            if item['id'] == activity_id:
                return Activity.from_dict(item)
        return None

    def save_activity(self, activity: Activity):
        """Save or update an activity."""
        data = self._read_json(self.activities_file)

        # Update existing or append new
        updated = False
        for i, item in enumerate(data):
            if item['id'] == activity.id:
                data[i] = activity.to_dict()
                updated = True
                break

        if not updated:
            data.append(activity.to_dict())

        self._write_json(self.activities_file, data)

    def delete_activity(self, activity_id: str):
        """Delete an activity."""
        data = self._read_json(self.activities_file)
        data = [item for item in data if item['id'] != activity_id]
        self._write_json(self.activities_file, data)

    # Goals
    def get_goals(self, week_start: Optional[str] = None) -> List[WeeklyGoal]:
        """Get goals, optionally filtered by week."""
        data = self._read_json(self.goals_file)
        goals = [WeeklyGoal.from_dict(g) for g in data]

        if week_start:
            goals = [g for g in goals if g.week_start == week_start]

        return sorted(goals, key=lambda x: x.created_at, reverse=True)

    def get_goal(self, goal_id: str) -> Optional[WeeklyGoal]:
        """Get a specific goal by ID."""
        data = self._read_json(self.goals_file)
        for item in data:
            if item['id'] == goal_id:
                return WeeklyGoal.from_dict(item)
        return None

    def save_goal(self, goal: WeeklyGoal):
        """Save or update a goal."""
        data = self._read_json(self.goals_file)

        # Update existing or append new
        updated = False
        for i, item in enumerate(data):
            if item['id'] == goal.id:
                data[i] = goal.to_dict()
                updated = True
                break

        if not updated:
            data.append(goal.to_dict())

        self._write_json(self.goals_file, data)

    def delete_goal(self, goal_id: str):
        """Delete a goal."""
        data = self._read_json(self.goals_file)
        data = [item for item in data if item['id'] != goal_id]
        self._write_json(self.goals_file, data)

    # Insights
    def get_insights(self, week_start: Optional[str] = None) -> List[Insight]:
        """Get insights, optionally filtered by week."""
        data = self._read_json(self.insights_file)
        insights = [Insight.from_dict(i) for i in data]

        if week_start:
            insights = [i for i in insights if i.week_start == week_start]

        return sorted(insights, key=lambda x: x.generated_at, reverse=True)

    def save_insight(self, insight: Insight):
        """Save an insight."""
        data = self._read_json(self.insights_file)
        data.append(insight.to_dict())
        self._write_json(self.insights_file, data)

    # To-Dos
    def get_todos(self, status: Optional[str] = None) -> List[ToDo]:
        """Get to-dos, optionally filtered by status."""
        data = self._read_json(self.todos_file)
        todos = [ToDo.from_dict(t) for t in data]

        if status:
            todos = [t for t in todos if t.status == status]

        return sorted(todos, key=lambda x: (x.priority, x.generated_at), reverse=True)

    def get_todo(self, todo_id: str) -> Optional[ToDo]:
        """Get a specific to-do by ID."""
        data = self._read_json(self.todos_file)
        for item in data:
            if item['id'] == todo_id:
                return ToDo.from_dict(item)
        return None

    def save_todo(self, todo: ToDo):
        """Save or update a to-do."""
        data = self._read_json(self.todos_file)

        # Update existing or append new
        updated = False
        for i, item in enumerate(data):
            if item['id'] == todo.id:
                data[i] = todo.to_dict()
                updated = True
                break

        if not updated:
            data.append(todo.to_dict())

        self._write_json(self.todos_file, data)

    def delete_todo(self, todo_id: str):
        """Delete a to-do."""
        data = self._read_json(self.todos_file)
        data = [item for item in data if item['id'] != todo_id]
        self._write_json(self.todos_file, data)
