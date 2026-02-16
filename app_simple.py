"""
What I Did - Flask Web Application (Simplified for Testing)
A personal productivity tracker - without Google sync dependencies
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from datetime import datetime, timedelta, date
from pathlib import Path
import uuid
import os

from models import (
    DataStore, Activity, WeeklyGoal, Insight, ToDo,
    ActivitySource, ActivityCategory, GoalStatus
)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')

# Initialize data store
data_store = DataStore()

# Utility functions
def get_current_week_start() -> str:
    """Get the Monday of the current week in ISO format."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return monday.isoformat()


def get_week_range(week_start_str: str) -> tuple:
    """Get start and end dates for a week."""
    week_start = date.fromisoformat(week_start_str)
    week_end = week_start + timedelta(days=6)
    return week_start.isoformat(), week_end.isoformat()


# Routes

@app.route('/')
def index():
    """Dashboard/home page."""
    week_start = get_current_week_start()
    start_date, end_date = get_week_range(week_start)

    # Get current week's data
    activities = data_store.get_activities(start_date, end_date)
    goals = data_store.get_goals(week_start)
    insights = data_store.get_insights(week_start)
    todos = data_store.get_todos(status="pending")

    # Calculate statistics
    total_activities = len(activities)
    total_hours = sum(a.duration_minutes or 0 for a in activities) / 60
    completed_goals = len([g for g in goals if g.status == GoalStatus.COMPLETED.value])
    total_goals = len(goals)

    # Activity breakdown by category
    category_stats = {}
    for activity in activities:
        cat = activity.category
        if cat not in category_stats:
            category_stats[cat] = {'count': 0, 'hours': 0}
        category_stats[cat]['count'] += 1
        category_stats[cat]['hours'] += (activity.duration_minutes or 0) / 60

    return render_template('dashboard.html',
                          week_start=week_start,
                          activities=activities[:10],
                          goals=goals,
                          insights=insights[:5],
                          todos=todos[:10],
                          total_activities=total_activities,
                          total_hours=round(total_hours, 1),
                          completed_goals=completed_goals,
                          total_goals=total_goals,
                          category_stats=category_stats)


@app.route('/activities')
def activities():
    """Activity log page."""
    week_start = request.args.get('week', get_current_week_start())
    start_date, end_date = get_week_range(week_start)

    activities = data_store.get_activities(start_date, end_date)

    return render_template('activities.html',
                          activities=activities,
                          week_start=week_start,
                          categories=ActivityCategory,
                          sources=ActivitySource)


@app.route('/activities/add', methods=['GET', 'POST'])
def add_activity():
    """Add a new activity."""
    if request.method == 'POST':
        activity = Activity(
            id=str(uuid.uuid4()),
            date=request.form['date'],
            timestamp=f"{request.form['date']}T{request.form.get('time', '12:00:00')}",
            title=request.form['title'],
            description=request.form.get('description', ''),
            category=request.form['category'],
            source=ActivitySource.MANUAL.value,
            duration_minutes=int(request.form['duration']) if request.form.get('duration') else None,
            tags=request.form.get('tags', '').split(',') if request.form.get('tags') else []
        )

        data_store.save_activity(activity)
        flash('Activity added successfully!', 'success')
        return redirect(url_for('activities'))

    return render_template('add_activity.html', categories=ActivityCategory)


@app.route('/activities/<activity_id>/edit', methods=['GET', 'POST'])
def edit_activity(activity_id):
    """Edit an existing activity."""
    activity = data_store.get_activity(activity_id)
    if not activity:
        flash('Activity not found', 'error')
        return redirect(url_for('activities'))

    if request.method == 'POST':
        activity.date = request.form['date']
        activity.timestamp = f"{request.form['date']}T{request.form.get('time', '12:00:00')}"
        activity.title = request.form['title']
        activity.description = request.form.get('description', '')
        activity.category = request.form['category']
        activity.duration_minutes = int(request.form['duration']) if request.form.get('duration') else None
        activity.tags = request.form.get('tags', '').split(',') if request.form.get('tags') else []

        data_store.save_activity(activity)
        flash('Activity updated successfully!', 'success')
        return redirect(url_for('activities'))

    return render_template('edit_activity.html', activity=activity, categories=ActivityCategory)


@app.route('/activities/<activity_id>/delete', methods=['POST'])
def delete_activity(activity_id):
    """Delete an activity."""
    data_store.delete_activity(activity_id)
    flash('Activity deleted successfully!', 'success')
    return redirect(url_for('activities'))


@app.route('/goals')
def goals():
    """Weekly goals page."""
    week_start = request.args.get('week', get_current_week_start())
    goals = data_store.get_goals(week_start)

    return render_template('goals.html', goals=goals, week_start=week_start)


@app.route('/goals/add', methods=['GET', 'POST'])
def add_goal():
    """Add a new weekly goal."""
    if request.method == 'POST':
        now = datetime.now().isoformat()
        goal = WeeklyGoal(
            id=str(uuid.uuid4()),
            week_start=request.form['week_start'],
            title=request.form['title'],
            description=request.form.get('description', ''),
            status=GoalStatus.NOT_STARTED.value,
            created_at=now,
            updated_at=now,
            target_hours=float(request.form['target_hours']) if request.form.get('target_hours') else None
        )

        data_store.save_goal(goal)
        flash('Goal added successfully!', 'success')
        return redirect(url_for('goals'))

    return render_template('add_goal.html', week_start=get_current_week_start())


@app.route('/goals/<goal_id>/update_status', methods=['POST'])
def update_goal_status(goal_id):
    """Update a goal's status."""
    goal = data_store.get_goal(goal_id)
    if not goal:
        return jsonify({'error': 'Goal not found'}), 404

    new_status = request.json.get('status')
    goal.status = new_status
    goal.updated_at = datetime.now().isoformat()

    if new_status == GoalStatus.COMPLETED.value:
        goal.completed_at = datetime.now().isoformat()

    data_store.save_goal(goal)
    return jsonify({'success': True})


@app.route('/goals/<goal_id>/delete', methods=['POST'])
def delete_goal(goal_id):
    """Delete a goal."""
    data_store.delete_goal(goal_id)
    flash('Goal deleted successfully!', 'success')
    return redirect(url_for('goals'))


@app.route('/insights')
def insights():
    """AI insights page."""
    week_start = request.args.get('week', get_current_week_start())
    insights = data_store.get_insights(week_start)

    return render_template('insights.html', insights=insights, week_start=week_start)


@app.route('/insights/generate', methods=['POST'])
def generate_insights():
    """Generate AI insights - disabled in this version."""
    return jsonify({'error': 'AI features not available in this test version'}), 503


@app.route('/todos')
def todos():
    """To-dos page."""
    status_filter = request.args.get('status', 'pending')
    todos = data_store.get_todos(status=status_filter if status_filter != 'all' else None)

    return render_template('todos.html', todos=todos, status_filter=status_filter)


@app.route('/todos/<todo_id>/update_status', methods=['POST'])
def update_todo_status(todo_id):
    """Update a to-do's status."""
    todo = data_store.get_todo(todo_id)
    if not todo:
        return jsonify({'error': 'To-do not found'}), 404

    new_status = request.json.get('status')
    todo.status = new_status

    if new_status == 'completed':
        todo.completed_at = datetime.now().isoformat()

    data_store.save_todo(todo)
    return jsonify({'success': True})


@app.route('/todos/<todo_id>/delete', methods=['POST'])
def delete_todo(todo_id):
    """Delete a to-do."""
    data_store.delete_todo(todo_id)
    flash('To-do deleted successfully!', 'success')
    return redirect(url_for('todos'))


@app.route('/sync/google', methods=['POST'])
def sync_google():
    """Sync Google data - disabled in this version."""
    return jsonify({'error': 'Google sync not available in this test version'}), 503


@app.route('/settings')
def settings():
    """Settings page."""
    return render_template('settings.html')


@app.route('/api/stats/week/<week_start>')
def api_week_stats(week_start):
    """Get statistics for a specific week."""
    start_date, end_date = get_week_range(week_start)

    activities = data_store.get_activities(start_date, end_date)
    goals = data_store.get_goals(week_start)

    stats = {
        'total_activities': len(activities),
        'total_hours': sum(a.duration_minutes or 0 for a in activities) / 60,
        'goals_completed': len([g for g in goals if g.status == GoalStatus.COMPLETED.value]),
        'goals_total': len(goals),
        'category_breakdown': {}
    }

    for activity in activities:
        cat = activity.category
        if cat not in stats['category_breakdown']:
            stats['category_breakdown'][cat] = 0
        stats['category_breakdown'][cat] += 1

    return jsonify(stats)


if __name__ == '__main__':
    # Create data directory if it doesn't exist
    Path('data').mkdir(exist_ok=True)

    print("=" * 60)
    print("What I Did - Flask Productivity Tracker")
    print("=" * 60)
    print("Starting server at http://localhost:5555")
    print("")
    print("Note: This is a simplified version for testing")
    print("      AI insights and Google sync are disabled")
    print("")
    print("Features available:")
    print("  ✓ Dashboard with stats")
    print("  ✓ Manual activity logging")
    print("  ✓ Weekly goals management")
    print("  ✓ View insights and to-dos")
    print("")
    print("Press Ctrl+C to stop the server")
    print("=" * 60)

    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5555)
