# Work Tracker

A powerful desktop app for logging daily work, auto-generating rich weekly PPT reports with AI enrichment, and creating professional presentations on any topic.

## Quick Start

**Double-click** `Work Tracker.command` on your Desktop.

Your browser will open automatically to `http://localhost:5000`.

---

## ✨ What's New — Rich Presentations!

Both the **Weekly Report** and **Presentation Generator** now create visually rich, professional slides:

### Enhanced Features:
- ✅ **Colored backgrounds** — Gradient and solid color themes
- ✅ **Multiple content lines** — 4-6 detailed bullet points per slide
- ✅ **Visual elements** — Accent bars, cards, decorative corners
- ✅ **Better typography** — Larger fonts, proper hierarchy
- ✅ **Stats and badges** — Task counts, time tracked, category metrics
- ✅ **Professional layouts** — Cards, rounded rectangles, structured content

---

## Features

### 1. Daily Task Logging (Dashboard)
- Quick-add tasks with category, description, and optional duration
- Log short notes or URLs — AI will expand them in reports
- View today's tasks at a glance

### 2. Weekly View
- See all tasks grouped by category
- Stats bar showing total tasks, time, and categories
- Color-coded category badges

### 3. History
- Browse all tasks grouped by date
- Complete work history timeline

### 4. 🎨 Presentation Generator
Create a full styled presentation on **any topic** — not just work tasks.

**How it works:**
1. Go to the **Presenter** tab
2. Enter a title (e.g., "AI in Healthcare", "Q4 Marketing Strategy")
3. Describe your topic in detail
4. Choose slide count (4-10 slides)
5. Pick a theme or let it auto-detect
6. Click **Generate Presentation**
7. Rich PPT saved to your Desktop with:
   - Gradient backgrounds
   - 4-6 bullet points per slide
   - Content cards with colored backgrounds
   - Accent bars and decorative elements
   - Professional typography

**Auto-detect themes:**
| Theme | Colors | Best For |
|-------|--------|----------|
| Tech & Innovation | Dark navy + cyan | Software, AI, digital |
| Business & Strategy | Navy + gold | Marketing, startups, pitch decks |
| Creative & Design | Purple + pink | Art, UI/UX, branding |
| Nature & Environment | Forest green + gold | Sustainability, ecology |
| Education & Learning | Warm brown + orange | Training, courses, research |
| Health & Wellness | Rose + mint | Medical, fitness, nutrition |
| Finance & Data | Navy + green | Banking, investment, analytics |
| General | Slate + amber | Everything else |

### 5. AI Report Enrichment
Automatically expand short task notes into rich, presentation-ready content for weekly reports.

**Setup:** Settings tab → Enable AI enrichment → (Optional) Add OpenAI API key

**Without API key:** Smart rule-based enrichment
**With API key:** GPT-4o-mini writes professional descriptions

---

## Tabs Overview

| Tab | Purpose |
|-----|---------|
| **Dashboard** | Log today's tasks quickly |
| **This Week** | View weekly summary with stats |
| **History** | Browse all past tasks |
| **🎨 Presenter** | Generate rich presentations on any topic |
| **Settings** | AI enrichment, categories, API key |

---

## Example Presentations

### Weekly Report
- **Cover slide** — Gradient background, title, date, stats summary
- **Agenda slide** — Dark background, numbered categories with task counts
- **Category slides** — One per work category, dark background, content cards with all tasks listed
- **Summary slide** — Gradient background, complete week summary, thank you message

### Topic Presentation
- **Cover slide** — Gradient background, title, subtitle bullets, decorative corners
- **Content slides** — Colored background, title with accent bar, content card with 4-6 detailed bullets
- **Closing slide** — Gradient background, thank you message, decorative elements

---

## Categories (pre-loaded)

- Local Support
- LLM Training
- eSIM Onboarding Review
- Freelancers Review
- Meetings
- Banners Translations

Add or remove categories in **Settings** tab.

---

## File Structure

```
work-tracker-app/
├── web_app.py              ← Web server (run this)
├── db.py                   ← Database layer
├── report.py               ← Enhanced weekly PPT report generator
├── ppt_generator.py        ← Enhanced presentation generator
├── enrich.py               ← AI enrichment engine
├── templates/
│   └── index.html          ← Web interface
── work_tracker.db         ← Your task data
── settings.json           ← App settings
└── README.md               ← This file
```

---

## Example Workflows

### Weekly Report Workflow
1. **Daily:** Log tasks quickly ("Korea campaign", "Fixed bug", URLs)
2. **Friday:** Click "Generate Report" → AI enriches descriptions → Rich PPT on Desktop with colored slides and detailed content

### Presentation Generator Workflow
1. **Presenter tab:** Enter "The Future of Remote Work"
2. **Describe:** "How remote work is evolving with AI collaboration tools, asynchronous communication, and access to global talent pools..."
3. **Choose:** 6 slides, auto-detect theme
4. **Generate:** Rich PPT with gradient backgrounds, content cards, multiple bullets per slide, saved to Desktop

---

## Requirements

- Python 3.10+
- `flask` (pip install flask)
- `openai` (pip install openai) — optional, for AI features
- `officecli` (for PPT generation — already installed)

---

## Stopping the App

Close the browser tab, then press `Ctrl+C` in the Terminal window, or just close the Terminal.

---

## What Changed in This Update

### Before:
- ❌ Single line of text per slide
-  Plain white backgrounds
- ❌ No visual elements
- ❌ Minimal content

### After:
- ✅ 4-6 detailed bullet points per slide
- ✅ Gradient and colored backgrounds
- ✅ Content cards with rounded corners
- ✅ Accent bars and decorative elements
- ✅ Stats badges and task counts
- ✅ Professional typography and spacing
- ✅ Slide numbers
- ✅ Cover and closing slides with style
