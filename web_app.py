"""Work Tracker — Web app with simple email/username authentication."""

from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from datetime import datetime, timedelta
from functools import wraps
import os
import sys
import json
import webbrowser
import threading
import secrets
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import (
    init_db, get_categories, add_task, get_tasks_for_date,
    get_tasks_for_week, get_all_tasks, delete_task, get_today_summary,
    get_week_stats, add_category, delete_category, get_or_create_user,
    create_team, get_user_teams, get_team_members, add_team_member,
    remove_team_member, is_team_manager, get_team_analytics, get_user_analytics,
)
from report import generate_weekly_report
from ppt_generator import generate_presentation, get_available_themes

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))
init_db()

# Settings file path
SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

# Allowed email domain
ALLOWED_DOMAIN = "trip.com"

def load_settings() -> dict:
    """Load settings from JSON file."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {"openai_api_key": "", "enrich_enabled": True}

def save_settings(settings: dict):
    """Save settings to JSON file."""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

def login_required(f):
    """Decorator to require login."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def get_current_user() -> dict:
    """Get current user from session."""
    return {
        'user_id': session.get('user_id'),
        'name': session.get('user_name'),
        'email': session.get('user_email'),
        'avatar': session.get('user_avatar', ''),
    }

# ── Routes ──────────────────────────────────────────────────

@app.route('/')
@login_required
def index():
    user = get_current_user()
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        name = request.form.get('name', '').strip()
        
        # Validate email domain
        if not email.endswith(f'@{ALLOWED_DOMAIN}'):
            return render_template('login.html', error=f'Only @{ALLOWED_DOMAIN} email addresses are allowed.')
        
        if not name:
            return render_template('login.html', error='Username is required.')
        
        # Create or get user (use email as user_id)
        get_or_create_user(email, name, email)
        
        # Set session
        session['user_id'] = email
        session['user_name'] = name
        session['user_email'] = email
        
        return redirect(url_for('index'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/api/me')
@login_required
def api_me():
    return jsonify(get_current_user())

@app.route('/api/categories', methods=['GET'])
def api_get_categories():
    return jsonify(get_categories())

@app.route('/api/categories', methods=['POST'])
def api_add_category():
    data = request.json
    name = data.get('name', '').strip()
    if not name:
        return jsonify({'error': 'Name required'}), 400
    try:
        add_category(name)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/categories/<name>', methods=['DELETE'])
def api_delete_category(name):
    delete_category(name)
    return jsonify({'success': True})

@app.route('/api/tasks', methods=['GET'])
@login_required
def api_get_tasks():
    user_id = session.get('user_id')
    scope = request.args.get('scope', 'today')

    if scope == 'today':
        tasks = get_tasks_for_date(user_id, datetime.now().strftime('%Y-%m-%d'))
    elif scope == 'week':
        tasks = get_tasks_for_week(user_id)
    elif scope == 'all':
        tasks = get_all_tasks(user_id)
    else:
        tasks = get_tasks_for_date(user_id, scope)

    return jsonify(tasks)

@app.route('/api/tasks', methods=['POST'])
@login_required
def api_add_task():
    import re
    user_id = session.get('user_id')
    data = request.json
    date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
    category = data.get('category', '')
    description = data.get('description', '').strip()
    duration = int(data.get('duration', 0))
    notes = data.get('notes', '')
    name = data.get('name', '').strip()
    url = data.get('url', '').strip()
    requester = data.get('requester', '').strip()

    # Auto-detect URL in description if not provided separately
    if not url and description:
        url_pattern = r'https?://[^\s]+'
        url_match = re.search(url_pattern, description)
        if url_match:
            url = url_match.group(0)
            # Remove URL from description
            description = re.sub(url_pattern, '', description).strip()

    # Auto-generate name from description if not provided
    if not name and description:
        # Use first 50 chars or first sentence as name
        name = description[:50] if len(description) <= 50 else description[:47] + "..."

    if not description:
        return jsonify({'error': 'Description required'}), 400
    if not category:
        return jsonify({'error': 'Category required'}), 400

    tid = add_task(user_id, date, category, description, duration, notes, name, url, requester)
    return jsonify({'id': tid, 'success': True})

@app.route('/api/tasks/<int:task_id>', methods=['DELETE'])
@login_required
def api_delete_task(task_id):
    user_id = session.get('user_id')
    delete_task(user_id, task_id)
    return jsonify({'success': True})

@app.route('/api/stats/today', methods=['GET'])
@login_required
def api_today_stats():
    user_id = session.get('user_id')
    return jsonify(get_today_summary(user_id))

@app.route('/api/stats/week', methods=['GET'])
@login_required
def api_week_stats():
    user_id = session.get('user_id')
    return jsonify(get_week_stats(user_id))

@app.route('/api/report', methods=['POST'])
@login_required
def api_generate_report():
    try:
        user_id = session.get('user_id')
        settings = load_settings()
        
        # Create temp directory for reports
        temp_dir = os.path.join(tempfile.gettempdir(), 'work_tracker_reports')
        os.makedirs(temp_dir, exist_ok=True)
        
        path = generate_weekly_report(
            user_id=user_id,
            output_dir=temp_dir,
            api_key=settings.get("openai_api_key", ""),
            enrich=settings.get("enrich_enabled", True),
        )
        
        # Extract filename from path for download URL
        filename = os.path.basename(path)
        download_url = f'/api/download-report/{filename}'
        
        return jsonify({'success': True, 'path': path, 'download_url': download_url, 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download-report/<filename>')
@login_required
def download_report(filename):
    """Download a generated weekly report file."""
    temp_dir = os.path.join(tempfile.gettempdir(), 'work_tracker_reports')
    filepath = os.path.join(temp_dir, filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
    )

@app.route('/api/settings', methods=['GET'])
def api_get_settings():
    settings = load_settings()
    # Don't expose full API key, just whether it's set
    return jsonify({
        "openai_api_key_set": bool(settings.get("openai_api_key")),
        "enrich_enabled": settings.get("enrich_enabled", True),
    })

@app.route('/api/settings', methods=['POST'])
def api_save_settings():
    data = request.json
    settings = load_settings()

    if "openai_api_key" in data:
        settings["openai_api_key"] = data["openai_api_key"]
    if "enrich_enabled" in data:
        settings["enrich_enabled"] = data["enrich_enabled"]

    save_settings(settings)
    return jsonify({'success': True})


# ── Presentation Generator API ──────────────────────────────

@app.route('/api/themes', methods=['GET'])
def api_get_themes():
    return jsonify(get_available_themes())


@app.route('/api/generate-presentation', methods=['POST'])
@login_required
def api_generate_presentation():
    data = request.json
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    num_slides = int(data.get('num_slides', 6))
    theme = data.get('theme', 'general')

    if not title:
        return jsonify({'error': 'Title is required'}), 400
    if not description:
        return jsonify({'error': 'Description is required'}), 400

    settings = load_settings()
    api_key = settings.get("openai_api_key", "")

    try:
        # Create temp directory for presentations
        temp_dir = os.path.join(tempfile.gettempdir(), 'work_tracker_presentations')
        os.makedirs(temp_dir, exist_ok=True)
        
        path = generate_presentation(
            title=title,
            description=description,
            num_slides=num_slides,
            output_dir=temp_dir,
            api_key=api_key,
        )
        
        # Extract filename from path for download URL
        filename = os.path.basename(path)
        download_url = f'/api/download-presentation/{filename}'
        
        return jsonify({'success': True, 'path': path, 'download_url': download_url, 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download-presentation/<filename>')
@login_required
def download_presentation(filename):
    """Download a generated presentation file."""
    temp_dir = os.path.join(tempfile.gettempdir(), 'work_tracker_presentations')
    filepath = os.path.join(temp_dir, filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.presentationml.presentation'
    )


# ── Team Management API ─────────────────────────────────────

@app.route('/api/teams', methods=['GET'])
@login_required
def api_get_user_teams():
    """Get all teams the current user belongs to."""
    user_email = session.get('user_id')
    teams = get_user_teams(user_email)
    return jsonify(teams)


@app.route('/api/teams', methods=['POST'])
@login_required
def api_create_team():
    """Create a new team."""
    user_email = session.get('user_id')
    data = request.json
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': 'Team name is required'}), 400
    
    team_id = create_team(name, user_email)
    if team_id is None:
        return jsonify({'error': 'Team name already exists'}), 400
    
    return jsonify({'success': True, 'team_id': team_id})


@app.route('/api/teams/<int:team_id>/members', methods=['GET'])
@login_required
def api_get_team_members(team_id):
    """Get all members of a team."""
    members = get_team_members(team_id)
    return jsonify(members)


@app.route('/api/teams/<int:team_id>/members', methods=['POST'])
@login_required
def api_add_team_member(team_id):
    """Add a member to a team."""
    user_email = session.get('user_id')
    
    # Check if user is manager
    if not is_team_manager(team_id, user_email):
        return jsonify({'error': 'Only managers can add members'}), 403
    
    data = request.json
    member_email = data.get('email', '').strip().lower()
    role = data.get('role', 'member')
    
    if not member_email:
        return jsonify({'error': 'Email is required'}), 400
    
    if not member_email.endswith(f'@{ALLOWED_DOMAIN}'):
        return jsonify({'error': f'Only @{ALLOWED_DOMAIN} emails allowed'}), 400
    
    success = add_team_member(team_id, member_email, role)
    if not success:
        return jsonify({'error': 'User is already a member'}), 400
    
    return jsonify({'success': True})


@app.route('/api/teams/<int:team_id>/members/<email>', methods=['DELETE'])
@login_required
def api_remove_team_member(team_id, email):
    """Remove a member from a team."""
    user_email = session.get('user_id')
    
    # Check if user is manager
    if not is_team_manager(team_id, user_email):
        return jsonify({'error': 'Only managers can remove members'}), 403
    
    remove_team_member(team_id, email)
    return jsonify({'success': True})


# ── Analytics API ───────────────────────────────────────────

@app.route('/api/analytics/personal', methods=['GET'])
@login_required
def api_personal_analytics():
    """Get personal analytics for the current user."""
    user_email = session.get('user_id')
    days = int(request.args.get('days', 7))
    analytics = get_user_analytics(user_email, days)
    return jsonify(analytics)


@app.route('/api/analytics/team/<int:team_id>', methods=['GET'])
@login_required
def api_team_analytics(team_id):
    """Get analytics for a team."""
    user_email = session.get('user_id')
    
    # Check if user is member of team
    teams = get_user_teams(user_email)
    team_ids = [t['id'] for t in teams]
    if team_id not in team_ids:
        return jsonify({'error': 'Access denied'}), 403
    
    days = int(request.args.get('days', 7))
    analytics = get_team_analytics(team_id, days)
    is_manager = is_team_manager(team_id, user_email)
    
    analytics['is_manager'] = is_manager
    return jsonify(analytics)


def open_browser():
    """Open browser after server starts."""
    import time
    time.sleep(1)
    webbrowser.open('http://localhost:5000')


if __name__ == '__main__':
    print("Starting Work Tracker web app...", flush=True)
    
    # Use PORT from environment (Railway) or default to 5000
    port = int(os.environ.get('PORT', 5000))
    
    # Only open browser when running locally
    if port == 5000:
        print("Opening browser automatically...", flush=True)
        threading.Thread(target=open_browser, daemon=True).start()

    # Start Flask server
    app.run(host='0.0.0.0', port=port, debug=False)
