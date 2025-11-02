from __future__ import annotations

from openai import OpenAI
from typing import List
from app.config import settings
from app.services.prompt_manager import get_prompt_manager


client = OpenAI(api_key=settings.OPENAI_API_KEY)


async def two_word_label(
    texts: list[str], 
    existing_labels: list[str] | None = None,
    is_retry: bool = False,
    is_hard_retry: bool = False
) -> str:
    pm = get_prompt_manager()
    text = "\n".join(texts[:5])
    if len(texts) > 5:
        text += f"\n... and {len(texts)-5} more"
    
    # Get prompts from JSON with fallbacks
    if is_hard_retry:
        system_prompt = pm.get("two_word_label", "hard_retry", "system")
        existing_labels_str = ", ".join(existing_labels) if existing_labels else ""
        user_prompt = pm.format_template(
            "two_word_label", "hard_retry", "user_template",
            existing_labels_str=existing_labels_str,
            text=text
        )
    elif is_retry:
        system_prompt = pm.get("two_word_label", "retry", "system")
        existing_labels_str = ", ".join(existing_labels) if existing_labels else ""
        user_prompt = pm.format_template(
            "two_word_label", "retry", "user_template",
            existing_labels_str=existing_labels_str,
            text=text
        )
    elif existing_labels:
        system_prompt = pm.get("two_word_label", "with_existing", "system")
        existing_labels_str = ", ".join(existing_labels)
        user_prompt = pm.format_template(
            "two_word_label", "with_existing", "user_template",
            existing_labels_str=existing_labels_str,
            text=text
        )
    else:
        system_prompt = pm.get("two_word_label", "default", "system")
        user_prompt = pm.format_template("two_word_label", "default", "user_template", text=text)
    
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_completion_tokens=10,
        temperature=0.5,
    )
    words = (res.choices[0].message.content or "").strip().split()[:2]
    return " ".join(words) if words else "summary message"


async def classify_message(text: str) -> str:
    pm = get_prompt_manager()
    system_prompt = pm.get("classify_message", "system")
    
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        max_tokens=2,
        temperature=0.0,
    )
    label = (res.choices[0].message.content or "").strip().lower()
    return label if label in {"positive", "neutral", "negative"} else "neutral"


async def best_message(messages: list[str]) -> str | None:
    pm = get_prompt_manager()
    if not messages:
        return None
    if len(messages) == 1:
        return messages[0]
    
    messages_list = "\n".join(f"{i+1}. {m}" for i, m in enumerate(messages))
    system_prompt = pm.get("best_message", "system")
    user_prompt = pm.format_template(
        "best_message", "user_template",
        messages_list=messages_list
    )
    
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=400,
        temperature=0.0,
    )
    return (res.choices[0].message.content or "").strip()


async def noble_message_per_cluster(
    cluster_messages: List[str], 
    cluster_label: str = ""
) -> str | None:
    """
    Select the most noble message from a cluster.
    
    A noble message is well-articulated, constructive, thoughtful, and best 
    represents the core perspective of the cluster.
    
    Args:
        cluster_messages: List of message contents in the cluster
        cluster_label: Optional 2-word label of the cluster for context
        
    Returns:
        The most noble message text, or None if no messages
    """
    pm = get_prompt_manager()
    if not cluster_messages:
        return None
    if len(cluster_messages) == 1:
        return cluster_messages[0]
    
    messages_list = "\n".join(f"{i+1}. {msg}" for i, msg in enumerate(cluster_messages))
    system_prompt = pm.get("noble_message", "system")
    user_prompt = pm.format_template(
        "noble_message", "user_template",
        cluster_label=cluster_label or "this cluster",
        messages_list=messages_list
    )
    
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=500,  # Allow for longer messages
        temperature=0.0,  # Deterministic selection
    )
    selected = (res.choices[0].message.content or "").strip()
    
    # Find the exact message that matches (handles cases where LLM adds commentary)
    # Try exact match first
    for msg in cluster_messages:
        if msg.strip() == selected.strip():
            return msg
    
    # Try partial match (in case of formatting differences)
    for msg in cluster_messages:
        if msg in selected or selected in msg:
            return msg
    
    # Fallback: return first message if exact match not found
    return cluster_messages[0] if cluster_messages else None


async def generate_expert_expertise_bullets(
    user_messages: List[str], 
    cluster_label: str = ""
) -> List[str]:
    """
    Generate 3 bullet points describing a user's area of expertise based on their messages.
    
    Args:
        user_messages: List of message contents written by the user
        cluster_label: Optional cluster label for context
        
    Returns:
        List of 3 bullet point strings describing their expertise
    """
    pm = get_prompt_manager()
    if not user_messages:
        return ["No messages available", "Cannot determine expertise", "Insufficient data"]
    
    messages_list = "\n".join(f"- {msg}" for msg in user_messages)
    system_prompt = pm.get("expert_expertise", "system")
    user_prompt = pm.format_template(
        "expert_expertise", "user_template",
        cluster_label=cluster_label or "this cluster",
        messages_list=messages_list
    )
    
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=200,
        temperature=0.3,
    )
    
    content = (res.choices[0].message.content or "").strip()
    
    # Parse bullet points (handle various formats)
    bullets = []
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        # Remove leading '- ', '* ', or numbers
        if line.startswith('- '):
            line = line[2:]
        elif line.startswith('* '):
            line = line[2:]
        elif line and line[0].isdigit() and ('. ' in line or ') ' in line):
            # Remove numbered bullets (e.g., "1. " or "1) ")
            parts = line.split('. ', 1) if '. ' in line else line.split(') ', 1)
            if len(parts) > 1:
                line = parts[1]
        bullets.append(line)
        if len(bullets) >= 3:
            break
    
    # Ensure we have exactly 3 bullet points
    while len(bullets) < 3:
        bullets.append(f"Additional expertise area {len(bullets) + 1}")
    
    return bullets[:3]


async def generate_bullet_point_summary_with_pros_cons(messages: List[str], question: str = "") -> str:
    """
    Generate 3 bullet points summary of a list of messages.
    Generate in total 2 pros and 2 cons for each bullet point
    
    Args:
        messages: List of messages to summarize
        question: Optional question text (defaults to placeholder if not provided)
    """
    pm = get_prompt_manager()
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    messages_list = "\n".join(f"- {msg}" for msg in messages)
    system_prompt = pm.get("bullet_summary", "system")
    user_prompt = pm.format_template(
        "bullet_summary", "user_template",
        question=question or "What is the risk of using ai in business?",
        messages_list=messages_list
    )
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=2000,
        temperature=0.4,
    )
    content = response.choices[0].message.content
    summary = content.strip() if content else ""
    return summary
