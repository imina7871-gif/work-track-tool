"""Enhanced Report generator — builds rich weekly PPT with colors and detailed content."""

import subprocess
import os
from datetime import datetime, timedelta
from typing import Optional

from db import get_tasks_for_week, get_categories, get_week_stats
from enrich import enrich_all_tasks


def _run(cmd: str) -> str:
    """Run a shell command and return stdout."""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, timeout=60
    )
    if result.returncode != 0:
        print(f"  WARN: {result.stderr.strip()}")
    return result.stdout.strip()


def generate_weekly_report(
    user_id: str = 'default',
    output_dir: Optional[str] = None,
    week_start: Optional[str] = None,
    api_key: Optional[str] = None,
    enrich: bool = True,
) -> str:
    """Generate a rich weekly achievements PPT and return the file path."""

    if output_dir is None:
        output_dir = os.path.expanduser("~/Desktop")

    today = datetime.now()
    if week_start is None:
        monday = today - timedelta(days=today.weekday())
        week_start = monday.strftime("%Y-%m-%d")

    sunday = (datetime.strptime(week_start, "%Y-%m-%d") + timedelta(days=6)).strftime("%Y-%m-%d")

    filename = f"Weekly_Report_{week_start}_to_{sunday}.pptx"
    filepath = os.path.join(output_dir, filename)

    tasks = get_tasks_for_week(user_id, week_start)

    # Enrich tasks if enabled
    if enrich and tasks:
        print("Enriching task descriptions with AI...")
        tasks = enrich_all_tasks(tasks, api_key)

    # Rebuild stats with enriched tasks
    stats = {}
    for t in tasks:
        cat = t["category"]
        if cat not in stats:
            stats[cat] = {"count": 0, "total_minutes": 0, "tasks": []}
        stats[cat]["count"] += 1
        stats[cat]["total_minutes"] += t["duration_minutes"]
        stats[cat]["tasks"].append(t)

    categories = get_categories()

    if not tasks:
        print("No tasks found for this week. Report will be empty.")

    # ── Build PPT via officecli ──────────────────────────────
    _run(f'officecli create "{filepath}"')
    _run(f'officecli open "{filepath}"')

    # Slide 1: Cover - Rich gradient background
    _run(f'officecli add "{filepath}" / --type slide --prop layout=blank --prop background=1E2761-CADCFC-180')
    
    # Title
    _run(f'officecli add "{filepath}" "/slide[1]" --type shape --prop text="Weekly Achievements Report" '
         f'--prop x=2cm --prop y=5cm --prop width=29.87cm --prop height=3cm '
         f'--prop font=Georgia --prop size=48 --prop bold=true --prop color=FFFFFF --prop align=center')
    
    # Date range
    _run(f'officecli add "{filepath}" "/slide[1]" --type shape --prop text="{week_start} — {sunday}" '
         f'--prop x=2cm --prop y=9cm --prop width=29.87cm --prop height=1.5cm '
         f'--prop font=Calibri --prop size=22 --prop color=CADCFC --prop align=center')
    
    # Stats summary
    total_tasks = len(tasks)
    total_hours = sum(t["duration_minutes"] for t in tasks) / 60
    active_cats = len(stats)
    
    stats_text = f"{total_tasks} Tasks Completed  •  {total_hours:.1f} Hours Tracked  •  {active_cats} Work Categories"
    _run(f'officecli add "{filepath}" "/slide[1]" --type shape --prop text="{stats_text}" '
         f'--prop x=3cm --prop y=11.5cm --prop width=27.87cm --prop height=1.2cm '
         f'--prop font=Calibri --prop size=18 --prop color=FFFFFF --prop align=center')
    
    # Accent line
    _run(f'officecli add "{filepath}" "/slide[1]" --type shape --prop preset=rect --prop fill=CADCFC --prop line=none '
         f'--prop x=12cm --prop y=13.5cm --prop width=9.87cm --prop height=0.15cm')
    
    # Decorative corners
    _run(f'officecli add "{filepath}" "/slide[1]" --type shape --prop preset=rect --prop fill=CADCFC --prop line=none '
         f'--prop x=1cm --prop y=1cm --prop width=0.5cm --prop height=0.5cm')
    _run(f'officecli add "{filepath}" "/slide[1]" --type shape --prop preset=rect --prop fill=CADCFC --prop line=none '
         f'--prop x=32.37cm --prop y=1cm --prop width=0.5cm --prop height=0.5cm')
    _run(f'officecli add "{filepath}" "/slide[1]" --type shape --prop preset=rect --prop fill=CADCFC --prop line=none '
         f'--prop x=1cm --prop y=17.55cm --prop width=0.5cm --prop height=0.5cm')
    _run(f'officecli add "{filepath}" "/slide[1]" --type shape --prop preset=rect --prop fill=CADCFC --prop line=none '
         f'--prop x=32.37cm --prop y=17.55cm --prop width=0.5cm --prop height=0.5cm')

    # Slide 2: Agenda - Dark background
    _run(f'officecli add "{filepath}" / --type slide --prop layout=blank --prop background=1E2761')
    _run(f'officecli add "{filepath}" "/slide[2]" --type shape --prop text="This Week at a Glance" '
         f'--prop x=1.5cm --prop y=1.2cm --prop width=30cm --prop height=2cm '
         f'--prop font=Georgia --prop size=36 --prop bold=true --prop color=FFFFFF')
    _run(f'officecli add "{filepath}" "/slide[2]" --type shape --prop preset=rect --prop fill=CADCFC --prop line=none '
         f'--prop x=1.5cm --prop y=3.2cm --prop width=6cm --prop height=0.15cm')

    active_cats = [c for c in categories if c["name"] in stats]
    for i, cat in enumerate(active_cats, 1):
        y = 4.5 + (i - 1) * 1.7
        cat_stats = stats[cat["name"]]
        
        # Numbered circle
        _run(f'officecli add "{filepath}" "/slide[2]" --type shape '
             f'--prop name="C{i}" --prop preset=ellipse --prop fill=CADCFC --prop line=none '
             f'--prop x=2cm --prop y={y}cm --prop width=1.2cm --prop height=1.4cm '
             f'--prop text="{i}" --prop font=Georgia --prop size=18 --prop bold=true '
             f'--prop color=1E2761 --prop align=center --prop valign=middle')
        
        # Category name
        _run(f'officecli add "{filepath}" "/slide[2]" --type shape '
             f'--prop name="L{i}" --prop text="{cat["name"]}" '
             f'--prop x=3.8cm --prop y={y}cm --prop width=12cm --prop height=1.2cm '
             f'--prop font=Calibri --prop size=20 --prop color=FFFFFF --prop valign=middle')
        
        # Task count
        _run(f'officecli add "{filepath}" "/slide[2]" --type shape '
             f'--prop name="T{i}" --prop text="{cat_stats["count"]} tasks • {cat_stats["total_minutes"]}min" '
             f'--prop x=16cm --prop y={y}cm --prop width=10cm --prop height=1.2cm '
             f'--prop font=Calibri --prop size=16 --prop color=CADCFC --prop valign=middle --prop align=right')

    # Slides for each category with tasks - Rich design
    slide_idx = 3
    for cat in active_cats:
        cat_tasks = stats[cat["name"]]["tasks"]
        
        # Dark background for category slides
        _run(f'officecli add "{filepath}" / --type slide --prop layout=blank --prop background=1E2761')
        
        # Category title
        _run(f'officecli add "{filepath}" "/slide[{slide_idx}]" --type shape '
             f'--prop text="{cat["name"]}" '
             f'--prop x=1.5cm --prop y=1cm --prop width=30cm --prop height=2cm '
             f'--prop font=Georgia --prop size=36 --prop bold=true --prop color=FFFFFF')
        
        # Accent bar
        _run(f'officecli add "{filepath}" "/slide[{slide_idx}]" --type shape '
             f'--prop preset=rect --prop fill=CADCFC --prop line=none '
             f'--prop x=1.5cm --prop y=3cm --prop width=8cm --prop height=0.15cm')
        
        # Stats badge
        cat_stat = stats[cat["name"]]
        _run(f'officecli add "{filepath}" "/slide[{slide_idx}]" --type shape '
             f'--prop text="{cat_stat["count"]} Tasks • {cat_stat["total_minutes"]} Minutes" '
             f'--prop x=20cm --prop y=1.2cm --prop width=12cm --prop height=1cm '
             f'--prop font=Calibri --prop size=16 --prop color=CADCFC --prop align=right')
        
        # Build rich bullet text with dates and details
        bullet_lines = []
        for t in cat_tasks:
            day_label = datetime.strptime(t["date"], "%Y-%m-%d").strftime("%a %d")
            line = f"• [{day_label}] {t['description']}"
            if t["duration_minutes"] > 0:
                line += f"  ({t['duration_minutes']}min)"
            bullet_lines.append(line)
        
        body_text = "\n".join(bullet_lines) if bullet_lines else "No tasks logged."
        
        # Content card with background
        _run(f'officecli add "{filepath}" "/slide[{slide_idx}]" --type shape '
             f'--prop preset=roundRect --prop fill=334155 --prop line=none '
             f'--prop x=1.5cm --prop y=3.8cm --prop width=30cm --prop height=12cm')
        
        # Bullet text
        _run(f'officecli add "{filepath}" "/slide[{slide_idx}]" --type shape '
             f'--prop text="{body_text}" '
             f'--prop x=2.5cm --prop y=4.3cm --prop width=28cm --prop height=11cm '
             f'--prop font=Calibri --prop size=18 --prop color=FFFFFF')
        
        # Slide number
        _run(f'officecli add "{filepath}" "/slide[{slide_idx}]" --type shape '
             f'--prop text="{slide_idx - 1}" '
             f'--prop x=30cm --prop y=17cm --prop width=2cm --prop height=1cm '
             f'--prop font=Calibri --prop size=14 --prop color=CADCFC --prop align=right')
        
        slide_idx += 1

    # Summary slide - Rich design
    _run(f'officecli add "{filepath}" / --type slide --prop layout=blank --prop background=1E2761-CADCFC-180')
    
    _run(f'officecli add "{filepath}" "/slide[{slide_idx}]" --type shape '
         f'--prop text="Summary & Highlights" '
         f'--prop x=2cm --prop y=2cm --prop width=29.87cm --prop height=2.5cm '
         f'--prop font=Georgia --prop size=40 --prop bold=true --prop color=FFFFFF --prop align=center')
    
    _run(f'officecli add "{filepath}" "/slide[{slide_idx}]" --type shape '
         f'--prop preset=rect --prop fill=CADCFC --prop line=none '
         f'--prop x=10cm --prop y=4.8cm --prop width=13.87cm --prop height=0.15cm')
    
    # Summary content
    total_tasks = len(tasks)
    total_mins = sum(t["duration_minutes"] for t in tasks)
    total_hours = total_mins / 60
    
    summary_lines = [
        f"✓ {total_tasks} tasks completed this week",
        f"✓ {len(active_cats)} work categories active",
        f"✓ {total_hours:.1f} hours tracked",
        "",
    ]
    
    for cat_name, cat_stats in stats.items():
        summary_lines.append(f"✓ {cat_name}: {cat_stats['count']} task(s), {cat_stats['total_minutes']}min")
    
    summary_text = "\n".join(summary_lines)
    
    # Content card
    _run(f'officecli add "{filepath}" "/slide[{slide_idx}]" --type shape '
         f'--prop preset=roundRect --prop fill=1E2761 --prop line=none '
         f'--prop x=3cm --prop y=5.5cm --prop width=27.87cm --prop height=9cm')
    
    _run(f'officecli add "{filepath}" "/slide[{slide_idx}]" --type shape '
         f'--prop text="{summary_text}" '
         f'--prop x=4cm --prop y=6cm --prop width=25.87cm --prop height=8cm '
         f'--prop font=Calibri --prop size=20 --prop color=FFFFFF')
    
    _run(f'officecli add "{filepath}" "/slide[{slide_idx}]" --type shape '
         f'--prop text="Thank You" '
         f'--prop x=2cm --prop y=15.5cm --prop width=29.87cm --prop height=1.5cm '
         f'--prop font=Georgia --prop size=24 --prop italic=true --prop color=FFFFFF --prop align=center')

    _run(f'officecli close "{filepath}"')
    _run(f'officecli validate "{filepath}"')

    return filepath


if __name__ == "__main__":
    path = generate_weekly_report()
    print(f"Report saved to: {path}")
