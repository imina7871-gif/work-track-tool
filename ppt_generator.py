"""Enhanced Presentation Generator — creates rich, visually appealing PPTs."""

import subprocess
import os
import json
import re
from datetime import datetime
from typing import Optional
import urllib.request

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


# ─ Color themes for different topics ───────────────────────

THEMES = {
    "tech": {
        "primary": "0F172A", "secondary": "38BDF8", "accent": "818CF8",
        "bg_dark": "0F172A", "bg_light": "1E293B", "text": "F8FAFC",
        "card_bg": "334155", "name": "Tech & Innovation"
    },
    "business": {
        "primary": "1E3A5F", "secondary": "4A90D9", "accent": "F5A623",
        "bg_dark": "1E3A5F", "bg_light": "2C5282", "text": "FFFFFF",
        "card_bg": "2D3748", "name": "Business & Strategy"
    },
    "creative": {
        "primary": "6D28D9", "secondary": "A78BFA", "accent": "F472B6",
        "bg_dark": "4C1D95", "bg_light": "5B21B6", "text": "FAF5FF",
        "card_bg": "6B46C1", "name": "Creative & Design"
    },
    "nature": {
        "primary": "065F46", "secondary": "34D399", "accent": "FBBF24",
        "bg_dark": "064E3B", "bg_light": "065F46", "text": "ECFDF5",
        "card_bg": "047857", "name": "Nature & Environment"
    },
    "education": {
        "primary": "7C2D12", "secondary": "FB923C", "accent": "FDE047",
        "bg_dark": "7C2D12", "bg_light": "9A3412", "text": "FFFBEB",
        "card_bg": "92400E", "name": "Education & Learning"
    },
    "health": {
        "primary": "BE185D", "secondary": "F472B6", "accent": "A7F3D0",
        "bg_dark": "831843", "bg_light": "9D174D", "text": "FDF2F8",
        "card_bg": "BE185D", "name": "Health & Wellness"
    },
    "finance": {
        "primary": "1E2761", "secondary": "CADCFC", "accent": "22C55E",
        "bg_dark": "1E2761", "bg_light": "1E3A8A", "text": "FFFFFF",
        "card_bg": "312E81", "name": "Finance & Data"
    },
    "general": {
        "primary": "334155", "secondary": "94A3B8", "accent": "F59E0B",
        "bg_dark": "1E293B", "bg_light": "334155", "text": "F8FAFC",
        "card_bg": "475569", "name": "General"
    },
}


def detect_theme(description: str) -> str:
    """Detect the best theme based on description keywords."""
    desc_lower = description.lower()
    
    theme_keywords = {
        "tech": ["tech", "software", "ai", "artificial intelligence", "machine learning",
                 "coding", "developer", "app", "digital", "innovation", "llm", "data"],
        "business": ["business", "strategy", "marketing", "sales", "revenue", "growth",
                     "startup", "investor", "pitch", "campaign", "brand"],
        "creative": ["design", "creative", "art", "ui", "ux", "branding", "visual",
                     "aesthetic", "fashion", "media"],
        "nature": ["nature", "environment", "sustainability", "green", "climate",
                   "ecology", "outdoor", "garden"],
        "education": ["education", "learning", "training", "course", "teaching",
                      "student", "academic", "research"],
        "health": ["health", "medical", "wellness", "fitness", "nutrition",
                   "healthcare", "hospital", "pharma"],
        "finance": ["finance", "financial", "banking", "investment", "accounting",
                    "budget", "economic", "money", "fintech"],
    }
    
    scores = {}
    for theme, keywords in theme_keywords.items():
        scores[theme] = sum(1 for kw in keywords if kw in desc_lower)
    
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "general"


def generate_slide_outline(
    title: str,
    description: str,
    num_slides: int,
    api_key: Optional[str] = None,
) -> list[dict]:
    """Generate a rich slide outline with detailed content."""
    
    if api_key and HAS_OPENAI:
        return _llm_outline(title, description, num_slides, api_key)
    
    return _rule_based_outline(title, description, num_slides)


def _llm_outline(title: str, description: str, num_slides: int, api_key: str) -> list[dict]:
    """Use OpenAI to generate rich slide content."""
    try:
        client = openai.OpenAI(api_key=api_key)
        
        prompt = f"""You are a professional presentation designer. Create a {num_slides}-slide presentation outline.

Title: {title}
Description: {description}

For each slide, provide:
1. A clear slide title (max 8 words)
2. 4-6 detailed bullet points (each 10-20 words, informative and specific)
3. An image search query for finding a relevant visual (5-10 words)

Output ONLY valid JSON in this format:
[
  {{
    "title": "Slide Title",
    "content": [
      "First detailed bullet point with specific information",
      "Second bullet point with data or examples",
      "Third bullet point with actionable insight",
      "Fourth bullet point with supporting detail"
    ],
    "image_query": "relevant search terms for image"
  }}
]

Rules:
- First slide should be a cover/title slide with 1-2 subtitle bullets
- Last slide should be a closing/thank you slide
- Middle slides should have 4-6 substantial bullet points each
- Make content informative, specific, and valuable
- Avoid generic statements - use concrete examples and data
- Image queries should be specific and visual"""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2000,
            temperature=0.7,
        )
        
        content = response.choices[0].message.content.strip()
        
        # Extract JSON from response
        json_match = re.search(r'\[.*\]', content, re.DOTALL)
        if json_match:
            slides = json.loads(json_match.group())
            return slides
        
        return _rule_based_outline(title, description, num_slides)
        
    except Exception as e:
        print(f"LLM outline failed: {e}")
        return _rule_based_outline(title, description, num_slides)


def _rule_based_outline(title: str, description: str, num_slides: int) -> list[dict]:
    """Generate rich outline using templates."""
    slides = []
    
    # Cover slide
    slides.append({
        "title": title,
        "content": [
            description[:150] if len(description) > 150 else description,
            "Comprehensive overview and analysis",
            "Key insights and actionable recommendations",
        ],
        "image_query": f"{title} professional",
        "is_cover": True,
    })
    
    # Content slides
    content_slides = num_slides - 2
    
    slide_templates = [
        {
            "title": "Overview & Context",
            "bullets": [
                f"Current landscape of {title.lower()}",
                "Key drivers and market forces at play",
                "Historical development and evolution",
                "Stakeholders and ecosystem participants",
                "Current challenges and opportunities",
            ]
        },
        {
            "title": "Key Components",
            "bullets": [
                "Core elements and fundamental building blocks",
                "Primary technologies and methodologies",
                "Essential frameworks and best practices",
                "Critical success factors",
                "Integration points and dependencies",
            ]
        },
        {
            "title": "Benefits & Impact",
            "bullets": [
                "Measurable improvements and ROI",
                "Efficiency gains and cost reductions",
                "Enhanced user experience and satisfaction",
                "Competitive advantages and market position",
                "Long-term strategic value",
            ]
        },
        {
            "title": "Implementation Strategy",
            "bullets": [
                "Phase 1: Assessment and planning",
                "Phase 2: Pilot and validation",
                "Phase 3: Full-scale deployment",
                "Resource requirements and timeline",
                "Risk mitigation and contingency plans",
            ]
        },
        {
            "title": "Best Practices",
            "bullets": [
                "Industry standards and proven approaches",
                "Common pitfalls to avoid",
                "Quality assurance and testing",
                "Continuous improvement methods",
                "Documentation and knowledge sharing",
            ]
        },
        {
            "title": "Case Studies & Examples",
            "bullets": [
                "Successful implementation examples",
                "Lessons learned from failures",
                "Industry-specific applications",
                "Measurable results and outcomes",
                "Key takeaways and insights",
            ]
        },
        {
            "title": "Future Trends",
            "bullets": [
                "Emerging technologies and innovations",
                "Market evolution and predictions",
                "Regulatory changes and compliance",
                "Shifting consumer expectations",
                "Opportunities for early adopters",
            ]
        },
        {
            "title": "Action Plan",
            "bullets": [
                "Immediate next steps and priorities",
                "Short-term goals (30-90 days)",
                "Medium-term objectives (6-12 months)",
                "Long-term vision and roadmap",
                "Success metrics and KPIs",
            ]
        },
    ]
    
    for i in range(content_slides):
        template = slide_templates[i % len(slide_templates)]
        slides.append({
            "title": template["title"],
            "content": template["bullets"],
            "image_query": f"{title} {template['title'].lower()}",
        })
    
    # Closing slide
    slides.append({
        "title": "Thank You",
        "content": [
            "Questions & Discussion",
            "Contact information and resources",
            "Follow-up actions and next steps",
        ],
        "image_query": "thank you professional",
        "is_closing": True,
    })
    
    return slides[:num_slides]


def _run(cmd: str) -> str:
    """Run a shell command."""
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=60)
    if result.returncode != 0:
        print(f"  WARN: {result.stderr.strip()}")
    return result.stdout.strip()


def _download_image(query: str, filepath: str) -> bool:
    """Download a placeholder image based on query."""
    try:
        # Use a simple colored rectangle as placeholder
        # In production, you'd integrate with Unsplash or similar
        return False
    except:
        return False


def generate_presentation(
    title: str,
    description: str,
    num_slides: int = 6,
    output_dir: Optional[str] = None,
    api_key: Optional[str] = None,
    image_paths: Optional[dict] = None,
) -> str:
    """Generate a rich, visually appealing presentation PPT."""
    
    if output_dir is None:
        output_dir = os.path.expanduser("~/Desktop")
    
    # Detect theme
    theme_key = detect_theme(description)
    theme = THEMES[theme_key]
    
    # Generate slide outline
    print(f"Generating outline for: {title}")
    slides_data = generate_slide_outline(title, description, num_slides, api_key)
    
    # Create filename
    safe_title = re.sub(r'[^\w\s-]', '', title)[:50]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    filename = f"{safe_title}_{timestamp}.pptx"
    filepath = os.path.join(output_dir, filename)
    
    # Build PPT
    print(f"Building presentation with '{theme['name']}' theme...")
    _run(f'officecli create "{filepath}"')
    _run(f'officecli open "{filepath}"')
    
    slide_idx = 1
    
    for i, slide_data in enumerate(slides_data):
        is_cover = slide_data.get("is_cover", False)
        is_closing = slide_data.get("is_closing", False)
        
        if is_cover:
            _build_cover_slide(filepath, slide_idx, slide_data, theme)
        elif is_closing:
            _build_closing_slide(filepath, slide_idx, slide_data, theme)
        else:
            _build_content_slide(filepath, slide_idx, slide_data, theme, i)
        
        slide_idx += 1
    
    _run(f'officecli close "{filepath}"')
    _run(f'officecli validate "{filepath}"')
    
    print(f"Presentation saved: {filepath}")
    return filepath


def _build_cover_slide(filepath: str, idx: int, data: dict, theme: dict):
    """Build a rich cover/title slide."""
    # Dark gradient background
    _run(f'officecli add "{filepath}" / --type slide --prop layout=blank --prop background={theme["bg_dark"]}-{theme["bg_light"]}-180')
    
    # Title
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop text="{data["title"]}" '
         f'--prop x=2cm --prop y=5cm --prop width=29.87cm --prop height=3cm '
         f'--prop font=Georgia --prop size=48 --prop bold=true --prop color=FFFFFF --prop align=center')
    
    # Subtitle bullets
    subtitle_text = "\n".join(f"• {b}" for b in data.get("content", [])[:2])
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop text="{subtitle_text}" '
         f'--prop x=4cm --prop y=9cm --prop width=25.87cm --prop height=3cm '
         f'--prop font=Calibri --prop size=20 --prop color={theme["secondary"]} --prop align=center')
    
    # Accent line
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop preset=rect --prop fill={theme["accent"]} --prop line=none '
         f'--prop x=12cm --prop y=13cm --prop width=9.87cm --prop height=0.15cm')
    
    # Decorative corner elements
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop preset=rect --prop fill={theme["accent"]} --prop line=none '
         f'--prop x=1cm --prop y=1cm --prop width=0.5cm --prop height=0.5cm')
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop preset=rect --prop fill={theme["accent"]} --prop line=none '
         f'--prop x=32.37cm --prop y=1cm --prop width=0.5cm --prop height=0.5cm')
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop preset=rect --prop fill={theme["accent"]} --prop line=none '
         f'--prop x=1cm --prop y=17.55cm --prop width=0.5cm --prop height=0.5cm')
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop preset=rect --prop fill={theme["accent"]} --prop line=none '
         f'--prop x=32.37cm --prop y=17.55cm --prop width=0.5cm --prop height=0.5cm')


def _build_content_slide(filepath: str, idx: int, data: dict, theme: dict, slide_num: int):
    """Build a rich content slide with multiple elements."""
    # Background
    _run(f'officecli add "{filepath}" / --type slide --prop layout=blank --prop background={theme["bg_light"]}')
    
    # Title with accent bar
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop text="{data["title"]}" '
         f'--prop x=1.5cm --prop y=1cm --prop width=30cm --prop height=1.8cm '
         f'--prop font=Georgia --prop size=36 --prop bold=true --prop color=FFFFFF')
    
    # Accent bar under title
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop preset=rect --prop fill={theme["accent"]} --prop line=none '
         f'--prop x=1.5cm --prop y=2.8cm --prop width=8cm --prop height=0.15cm')
    
    # Content bullets in a card
    bullets = "\n".join(f"• {b}" for b in data.get("content", []))
    
    # Card background
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop preset=roundRect --prop fill={theme["card_bg"]} --prop line=none '
         f'--prop x=1.5cm --prop y=3.5cm --prop width=30cm --prop height=12cm')
    
    # Bullet text
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop text="{bullets}" '
         f'--prop x=2.5cm --prop y=4cm --prop width=28cm --prop height=11cm '
         f'--prop font=Calibri --prop size=18 --prop color={theme["text"]}')
    
    # Slide number
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop text="{slide_num + 1}" '
         f'--prop x=30cm --prop y=17cm --prop width=2cm --prop height=1cm '
         f'--prop font=Calibri --prop size=14 --prop color={theme["secondary"]} --prop align=right')


def _build_closing_slide(filepath: str, idx: int, data: dict, theme: dict):
    """Build a rich closing/thank you slide."""
    # Dark gradient background
    _run(f'officecli add "{filepath}" / --type slide --prop layout=blank --prop background={theme["bg_dark"]}-{theme["bg_light"]}-180')
    
    # Thank you text
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop text="{data["title"]}" '
         f'--prop x=2cm --prop y=6cm --prop width=29.87cm --prop height=2.5cm '
         f'--prop font=Georgia --prop size=48 --prop bold=true --prop color=FFFFFF --prop align=center')
    
    # Subtitle bullets
    subtitle_text = "\n".join(f"• {b}" for b in data.get("content", []))
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop text="{subtitle_text}" '
         f'--prop x=4cm --prop y=10cm --prop width=25.87cm --prop height=3cm '
         f'--prop font=Calibri --prop size=20 --prop color={theme["secondary"]} --prop align=center')
    
    # Accent line
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop preset=rect --prop fill={theme["accent"]} --prop line=none '
         f'--prop x=12cm --prop y=14cm --prop width=9.87cm --prop height=0.15cm')
    
    # Decorative elements
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop preset=ellipse --prop fill={theme["accent"]} --prop line=none '
         f'--prop x=1cm --prop y=1cm --prop width=1cm --prop height=1cm')
    _run(f'officecli add "{filepath}" "/slide[{idx}]" --type shape '
         f'--prop preset=ellipse --prop fill={theme["accent"]} --prop line=none '
         f'--prop x=31.87cm --prop y=16.55cm --prop width=1cm --prop height=1cm')


def get_available_themes() -> list[dict]:
    """Return list of available themes."""
    return [
        {"key": k, "name": v["name"], "primary": v["primary"]}
        for k, v in THEMES.items()
    ]


if __name__ == "__main__":
    # Test
    themes = get_available_themes()
    print("Available themes:")
    for t in themes:
        print(f"  {t['name']} ({t['key']})")
    
    path = generate_presentation(
        title="AI in Healthcare",
        description="Exploring how artificial intelligence is transforming medical diagnosis, treatment planning, and patient care.",
        num_slides=6,
        output_dir="/tmp",
    )
    print(f"\nGenerated: {path}")
