import re

def clean_caption(text: str) -> str | None:
    if not text or not text.strip():
        return None
    # حذف لینک‌ها (http, https, t.co)
    cleaned = re.sub(r'http[s]?://\S+', '', text)
    cleaned = re.sub(r't\.co/\S+', '', cleaned)
    cleaned = cleaned.replace("  ", " ").strip()
    return cleaned if cleaned else None
