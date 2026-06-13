from pathlib import Path
import asyncio
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def build_prompt(user_query, context, intent="general"):

    intent_rules = {
        "research": """
- Be comprehensive and analytical.
- Compare evidence from multiple sources.
- Cite sources as [1], [2].
- Mention uncertainties.
""",

        "educational": """
- Explain clearly.
- Use examples.
- Teach step by step.
""",

        "summary": """
- Be concise.
- Focus on key findings.
""",

        "general": """
- Be accurate.
- Use the provided sources.
"""
    }

    rules = intent_rules.get(
        intent,
        intent_rules["general"]
    )

    return f"""
Question:
{user_query}

Retrieved Sources:
{context}

Instructions:
{rules}

Answer:
"""



