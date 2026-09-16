"""AI enrichment module — expands short task descriptions into rich content."""

import os
import re
import json
from typing import Optional

# Try to import OpenAI, but make it optional
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


def is_url(text: str) -> bool:
    """Check if text is a URL."""
    url_pattern = r'https?://[^\s]+'
    return bool(re.match(url_pattern, text.strip()))


def fetch_url_content(url: str) -> str:
    """Fetch and extract text content from a URL."""
    try:
        import urllib.request
        from html.parser import HTMLParser
        
        class TextExtractor(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = []
                self.skip = False
                
            def handle_starttag(self, tag, attrs):
                if tag in ['script', 'style', 'nav', 'footer']:
                    self.skip = True
                    
            def handle_endtag(self, tag):
                if tag in ['script', 'style', 'nav', 'footer']:
                    self.skip = False
                    
            def handle_data(self, data):
                if not self.skip:
                    text = data.strip()
                    if text and len(text) > 20:
                        self.text.append(text)
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
        
        parser = TextExtractor()
        parser.feed(html)
        
        # Return first 500 chars of extracted text
        content = ' '.join(parser.text[:10])
        return content[:500] if content else "Could not extract content"
    except Exception as e:
        return f"URL: {url} (could not fetch content)"


def enrich_description(
    description: str,
    category: str,
    api_key: Optional[str] = None,
) -> str:
    """
    Enrich a short task description into a detailed, presentation-ready version.
    
    If api_key is provided, uses OpenAI GPT-4o-mini.
    Otherwise, uses rule-based expansion.
    """
    
    # If already long enough, return as-is
    if len(description) > 100 and not is_url(description):
        return description
    
    # Handle URLs
    if is_url(description):
        url = description.strip()
        content = fetch_url_content(url)
        description = f"Reviewed/processed: {url}\nContent: {content[:200]}"
    
    # If no API key, use rule-based enrichment
    if not api_key or not HAS_OPENAI:
        return rule_based_enrich(description, category)
    
    # Use OpenAI for enrichment
    try:
        client = openai.OpenAI(api_key=api_key)
        
        prompt = f"""You are a professional work report writer. Expand this brief task note into a rich, detailed description suitable for a weekly achievements presentation.

Category: {category}
Brief note: {description}

Requirements:
- Write 2-3 sentences
- Include what was done, why it matters, and the outcome/impact
- Use professional, action-oriented language
- Keep it concise but informative
- Do NOT use buzzwords like "seamless", "robust", or "game-changing"

Output ONLY the enriched description, no labels or prefixes."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150,
            temperature=0.7,
        )
        
        enriched = response.choices[0].message.content.strip()
        return enriched if enriched else rule_based_enrich(description, category)
        
    except Exception as e:
        print(f"AI enrichment failed: {e}")
        return rule_based_enrich(description, category)


def rule_based_enrich(description: str, category: str) -> str:
    """
    Rule-based enrichment when no API key is available.
    Adds context and structure to short descriptions.
    """
    
    # Category-specific context
    context_map = {
        "Local Support": "Supported regional campaigns and marketing initiatives",
        "LLM Training": "Advanced AI model training and fine-tuning efforts",
        "eSIM Onboarding Review": "Reviewed and optimized the eSIM activation flow",
        "Freelancers Review": "Evaluated freelance contributor performance and deliverables",
        "Meetings": "Participated in cross-functional alignment and planning sessions",
        "Banners Translations": "Completed localization and translation of marketing materials",
    }
    
    context = context_map.get(category, "Completed assigned work tasks")
    
    # If description is very short, add more detail
    if len(description) < 30:
        return f"{context}. Task: {description}. Delivered on schedule with quality standards met."
    
    # If description is medium length, enhance it
    if len(description) < 100:
        return f"{context}. Specifically: {description}. Outcome: Task completed successfully."
    
    # Already detailed enough
    return description


def enrich_all_tasks(tasks: list, api_key: Optional[str] = None) -> list:
    """
    Enrich all tasks in a list. Returns new list with enriched descriptions.
    """
    enriched_tasks = []
    for task in tasks:
        enriched_desc = enrich_description(
            task["description"],
            task["category"],
            api_key,
        )
        enriched_task = {**task, "description": enriched_desc}
        enriched_tasks.append(enriched_task)
    return enriched_tasks


if __name__ == "__main__":
    # Test enrichment
    test_tasks = [
        {"description": "Korea campaign", "category": "Local Support"},
        {"description": "https://example.com/article", "category": "LLM Training"},
        {"description": "Reviewed onboarding flow and fixed 3 bugs", "category": "eSIM Onboarding Review"},
    ]
    
    print("Testing enrichment (no API key):")
    for task in test_tasks:
        enriched = enrich_description(task["description"], task["category"])
        print(f"\nOriginal: {task['description']}")
        print(f"Enriched: {enriched}")
