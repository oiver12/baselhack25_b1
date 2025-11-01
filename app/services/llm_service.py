from openai import OpenAI
from app.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


async def two_word_label(texts: list[str], existing_labels: list[str] | None = None) -> str:
    text = "\n".join(texts[:5])
    if len(texts) > 5:
        text += f"\n... and {len(texts)-5} more"
    
    system_prompt = "Summarize in exactly 2 words, no punctuation."
    user_prompt = text
    
    # Add existing labels context if provided
    if existing_labels:
        system_prompt = "Summarize in exactly 2 words, no punctuation. Make sure your label is distinct from existing labels."
        existing_labels_str = ", ".join(existing_labels)
        user_prompt = f"Generate a 2-word label. Existing labels: {existing_labels_str}. Make sure your label is distinct.\n\nMessages to summarize:\n{text}"
    
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        max_tokens=10,
        temperature=0.3,
    )
    words = (res.choices[0].message.content or "").strip().split()[:2]
    return " ".join(words) if words else "summary message"


async def classify_message(text: str) -> str:
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Classify as 'good', 'neutral', or 'bad' only."},
            {"role": "user", "content": text},
        ],
        max_tokens=2,
        temperature=0.0,
    )
    label = (res.choices[0].message.content or "").strip().lower()
    return label if label in {"good", "neutral", "bad"} else "neutral"


async def best_message(messages: list[str]) -> str | None:
    if not messages:
        return None
    if len(messages) == 1:
        return messages[0]
    prompt = "Select the best, clearest, most helpful message. Return only that text:\n" + "\n".join(
        f"{i+1}. {m}" for i, m in enumerate(messages)
    )
    res = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You evaluate helpfulness."},
                  {"role": "user", "content": prompt}],
        max_tokens=400,
        temperature=0.0,
    )
    return (res.choices[0].message.content or "").strip()