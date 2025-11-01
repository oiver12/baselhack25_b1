from openai import OpenAI
from typing import List
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

async def generate_bullet_point_summary_with_pros_cons(messages: List[str]) -> str:
    """
    Generate 3 bullet points summary of a list of messages.
    Generate in total 2 pros and 2 cons for each bullet point
    """
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    prompt = (
        "Summarize the following messages as 3 concise bullet points. "
        "Also add a approval rating for each bullet point from 0 to 1"
        "Each bullet point should be clear and distinct."
        "Respond with the 3 bullet points, no introduction or extra text. Also respond with 2 pros and 2 cons for each bullet point. "
        "Respond in this exact JSON format (no extra commentary): {\n"
        "  \"summary\": \"Summary of all the messages (approx 40 words)\",\n"
        "  \"description\": \"Description of the problem (approx 100 words)\",\n"
        "  \"points\": [\n"
        "    {\n"
        "      \"title\": \"First bullet point\",\n"
        "      \"pros\": [\"Pro 1\", \"Pro 2\"],\n"
        "      \"cons\": [\"Con 1\", \"Con 2\"]\n"
        "      \"approval_rating\": 0.5\n"
        "    },\n"
        "    {\n"
        "      \"title\": \"Second bullet point\",\n"
        "      \"pros\": [\"Pro 1\", \"Pro 2\"],\n"
        "      \"cons\": [\"Con 1\", \"Con 2\"]\n"
        "      \"approval_rating\": 0.5\n"
        "    },\n"
        "    {\n"
        "      \"title\": \"Third bullet point\",\n"
        "      \"pros\": [\"Pro 1\", \"Pro 2\"],\n"
        "      \"cons\": [\"Con 1\", \"Con 2\"]\n"
        "      \"approval_rating\": 0.5\n"
        "    }\n"
        "  ]\n"
        "}\n"
        f"The question to this conversation is: What is the risk of using ai in business?"
    )
    for msg in messages:
        prompt += f"- {msg}\n"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a skilled summarizer. Summarize in exactly 3 bullet points, one per line, with no introduction or extra commentary. The bullet points should be how we can solve the problem",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        max_tokens=2000,
        temperature=0.4,
    )
    summary = response.choices[0].message.content.strip()
    return summary
