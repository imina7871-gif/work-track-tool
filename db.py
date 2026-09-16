"""Database layer for Work Tracker App — multi-user with Lark auth."""

import sqlite3
import os
from datetime import datetime, timedelta
from typing import Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "work_tracker.db")

def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_conn()
    
    # Create tables with minimal schema (no indexes on columns that may not exist yet)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            color TEXT DEFAULT '#1E2761',
            sort_order INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lark_user_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            email TEXT DEFAULT '',
            avatar TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            duration_minutes INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TEXT DEFAULT (datetime('now','localtime'))
        );
    """)

    # Migrate existing database: add user_id column if missing
    try:
        conn.execute("SELECT user_id FROM tasks LIMIT 1")
    except sqlite3.OperationalError:
        conn.execute("ALTER TABLE tasks ADD COLUMN user_id TEXT DEFAULT 'legacy'")

    # Migrate: add new task columns if missing
    for col in ['name', 'url', 'requester']:
        try:
            conn.execute(f"SELECT {col} FROM tasks LIMIT 1")
        except sqlite3.OperationalError:
            conn.execute(f"ALTER TABLE tasks ADD COLUMN {col} TEXT DEFAULT ''")

    # Create indexes AFTER migrations (columns are guaranteed to exist now)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_user ON tasks(user_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_date ON tasks(date)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_category ON tasks(category)")
    
    # Create teams table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_by TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    
    # Create team_members table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS team_members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            user_email TEXT NOT NULL,
            role TEXT DEFAULT 'member',
            joined_at TEXT DEFAULT (datetime('now','localtime')),
            FOREIGN KEY (team_id) REFERENCES teams(id),
            UNIQUE(team_id, user_email)
        )
    """)
    
    conn.execute("CREATE INDEX IF NOT EXISTS idx_team_members_team ON team_members(team_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_team_members_user ON team_members(user_email)")
    
    conn.commit()

    # Seed default categories if empty
    count = conn.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    if count == 0:
        defaults = [
            ("Local Support", "#1E2761", 1),
            ("LLM Training", "#028090", 2),
            ("eSIM Onboarding Review", "#2C5F2D", 3),
            ("Freelancers Review", "#B85042", 4),
            ("Meetings", "#6D2E46", 5),
            ("Banners Translations", "#36454F", 6),
        ]
        conn.executemany(
            "INSERT INTO categories (name, color, sort_order) VALUES (?, ?, ?)",
            defaults
        )
    conn.commit()
    conn.close()

# ── Users ──────────────────────────────────────────────────

def get_or_create_user(email: str, name: str, avatar: str = "") -> str:
    """Get existing user or create new one. Returns email as user_id."""
    conn = get_conn()
    existing = conn.execute(
        "SELECT lark_user_id FROM users WHERE lark_user_id = ?", (email,)
    ).fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO users (lark_user_id, name, email, avatar) VALUES (?, ?, ?, ?)",
            (email, name, email, avatar)
        )
        conn.commit()
    conn.close()
    return email

def get_user_name(email: str) -> str:
    conn = get_conn()
    row = conn.execute(
        "SELECT name FROM users WHERE lark_user_id = ?", (email,)
    ).fetchone()
    conn.close()
    return row["name"] if row else "Unknown"

# ── Categories ──────────────────────────────────────────────

def get_categories() -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM categories ORDER BY sort_order"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_category(name: str, color: str = "#1E2761") -> int:
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO categories (name, color) VALUES (?, ?)", (name, color)
    )
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid

def delete_category(name: str):
    conn = get_conn()
    conn.execute("DELETE FROM categories WHERE name = ?", (name,))
    conn.commit()
    conn.close()

# ── Tasks (all scoped to user_id) ──────────────────────────

def add_task(user_id: str, date: str, category: str, description: str,
             duration: int = 0, notes: str = "", name: str = "", url: str = "", requester: str = "") -> int:
    conn = get_conn()
    cur = conn.execute(
        """INSERT INTO tasks (user_id, date, category, name, description, url, requester, duration_minutes, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, date, category, name, description, url, requester, duration, notes)
    )
    conn.commit()
    tid = cur.lastrowid
    conn.close()
    return tid

def get_tasks_for_date(user_id: str, date: str) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE user_id = ? AND date = ? ORDER BY created_at DESC",
        (user_id, date)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_tasks_for_week(user_id: str, week_start: Optional[str] = None) -> list[dict]:
    conn = get_conn()
    if week_start is None:
        today = datetime.now()
        monday = today - timedelta(days=today.weekday())
        week_start = monday.strftime("%Y-%m-%d")
    sunday = (datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")
    rows = conn.execute(
        """SELECT * FROM tasks
           WHERE user_id = ? AND date BETWEEN ? AND ?
           ORDER BY date DESC, created_at DESC""",
        (user_id, week_start, sunday)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_tasks(user_id: str) -> list[dict]:
    conn = get_conn()
    rows = conn.execute(
        "SELECT * FROM tasks WHERE user_id = ? ORDER BY date DESC, created_at DESC",
        (user_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_task(user_id: str, task_id: int):
    conn = get_conn()
    conn.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, user_id))
    conn.commit()
    conn.close()

# ── Stats ───────────────────────────────────────────────────

def get_week_stats(user_id: str, week_start: Optional[str] = None) -> dict:
    tasks = get_tasks_for_week(user_id, week_start)
    stats: dict[str, dict] = {}
    for t in tasks:
        cat = t["category"]
        if cat not in stats:
            stats[cat] = {"count": 0, "total_minutes": 0, "tasks": []}
        stats[cat]["count"] += 1
        stats[cat]["total_minutes"] += t["duration_minutes"]
        stats[cat]["tasks"].append(t)
    return stats

def get_today_summary(user_id: str) -> dict:
    today = datetime.now().strftime("%Y-%m-%d")
    tasks = get_tasks_for_date(user_id, today)
    total = sum(t["duration_minutes"] for t in tasks)
    return {
        "count": len(tasks),
        "total_minutes": total,
        "tasks": tasks,
    }

# ── Teams ───────────────────────────────────────────────────

def create_team(name: str, creator_email: str) -> int:
    """Create a new team and add creator as manager."""
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO teams (name, created_by) VALUES (?, ?)",
            (name, creator_email)
        )
        team_id = cur.lastrowid
        # Add creator as manager
        conn.execute(
            "INSERT INTO team_members (team_id, user_email, role) VALUES (?, ?, 'manager')",
            (team_id, creator_email)
        )
        conn.commit()
        conn.close()
        return team_id
    except sqlite3.IntegrityError:
        conn.close()
        return None  # Team name already exists

def get_user_teams(user_email: str) -> list[dict]:
    """Get all teams a user belongs to."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT t.id, t.name, tm.role, t.created_at
        FROM teams t
        JOIN team_members tm ON t.id = tm.team_id
        WHERE tm.user_email = ?
        ORDER BY t.name
    """, (user_email,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_team_members(team_id: int) -> list[dict]:
    """Get all members of a team with their info."""
    conn = get_conn()
    rows = conn.execute("""
        SELECT tm.user_email, tm.role, tm.joined_at, u.name, u.email
        FROM team_members tm
        LEFT JOIN users u ON tm.user_email = u.lark_user_id
        WHERE tm.team_id = ?
        ORDER BY tm.role DESC, u.name
    """, (team_id,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_team_member(team_id: int, user_email: str, role: str = 'member') -> bool:
    """Add a member to a team."""
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO team_members (team_id, user_email, role) VALUES (?, ?, ?)",
            (team_id, user_email, role)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False  # Already a member

def remove_team_member(team_id: int, user_email: str):
    """Remove a member from a team."""
    conn = get_conn()
    conn.execute(
        "DELETE FROM team_members WHERE team_id = ? AND user_email = ?",
        (team_id, user_email)
    )
    conn.commit()
    conn.close()

def is_team_manager(team_id: int, user_email: str) -> bool:
    """Check if user is a manager of the team."""
    conn = get_conn()
    row = conn.execute(
        "SELECT role FROM team_members WHERE team_id = ? AND user_email = ?",
        (team_id, user_email)
    ).fetchone()
    conn.close()
    return row and row['role'] == 'manager'

def get_team_analytics(team_id: int, days: int = 7) -> dict:
    """Get analytics data for a team over the specified period."""
    conn = get_conn()
    
    # Get date range
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    # Get all team members
    members = conn.execute("""
        SELECT user_email FROM team_members WHERE team_id = ?
    """, (team_id,)).fetchall()
    
    member_emails = [m['user_email'] for m in members]
    
    if not member_emails:
        conn.close()
        return {"members": [], "total_tasks": 0, "total_hours": 0, "category_breakdown": {}}
    
    # Get tasks for all team members
    placeholders = ','.join('?' * len(member_emails))
    tasks = conn.execute(f"""
        SELECT t.user_id, t.category, t.duration_minutes, t.date, u.name
        FROM tasks t
        LEFT JOIN users u ON t.user_id = u.lark_user_id
        WHERE t.user_id IN ({placeholders})
        AND t.date BETWEEN ? AND ?
        ORDER BY t.date DESC
    """, member_emails + [start_date, end_date]).fetchall()
    
    conn.close()
    
    # Process analytics
    member_stats = {}
    category_breakdown = {}
    daily_stats = {}
    
    for task in tasks:
        user_id = task['user_id']
        name = task['name'] or user_id
        category = task['category']
        duration = task['duration_minutes'] or 0
        date = task['date']
        
        # Member stats
        if user_id not in member_stats:
            member_stats[user_id] = {
                'name': name,
                'email': user_id,
                'task_count': 0,
                'total_minutes': 0,
                'categories': {}
            }
        member_stats[user_id]['task_count'] += 1
        member_stats[user_id]['total_minutes'] += duration
        
        # Category breakdown per member
        if category not in member_stats[user_id]['categories']:
            member_stats[user_id]['categories'][category] = 0
        member_stats[user_id]['categories'][category] += 1
        
        # Overall category breakdown
        if category not in category_breakdown:
            category_breakdown[category] = 0
        category_breakdown[category] += duration
        
        # Daily stats
        if date not in daily_stats:
            daily_stats[date] = 0
        daily_stats[date] += duration
    
    total_tasks = sum(m['task_count'] for m in member_stats.values())
    total_minutes = sum(m['total_minutes'] for m in member_stats.values())
    
    return {
        'members': list(member_stats.values()),
        'total_tasks': total_tasks,
        'total_hours': round(total_minutes / 60, 1),
        'category_breakdown': category_breakdown,
        'daily_stats': daily_stats,
        'start_date': start_date,
        'end_date': end_date
    }

def get_user_analytics(user_id: str, days: int = 7) -> dict:
    """Get personal analytics for a user."""
    conn = get_conn()
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    tasks = conn.execute("""
        SELECT category, duration_minutes, date
        FROM tasks
        WHERE user_id = ? AND date BETWEEN ? AND ?
        ORDER BY date DESC
    """, (user_id, start_date, end_date)).fetchall()
    
    conn.close()
    
    category_breakdown = {}
    daily_stats = {}
    hourly_stats = {}
    
    for task in tasks:
        category = task['category']
        duration = task['duration_minutes'] or 0
        date = task['date']
        
        # Category breakdown
        if category not in category_breakdown:
            category_breakdown[category] = 0
        category_breakdown[category] += duration
        
        # Daily stats
        if date not in daily_stats:
            daily_stats[date] = 0
        daily_stats[date] += duration
    
    total_tasks = len(tasks)
    total_minutes = sum(t['duration_minutes'] or 0 for t in tasks)
    
    return {
        'total_tasks': total_tasks,
        'total_hours': round(total_minutes / 60, 1),
        'category_breakdown': category_breakdown,
        'daily_stats': daily_stats,
        'start_date': start_date,
        'end_date': end_date
    }
