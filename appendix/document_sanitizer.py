# document_sanitizer.py — strip hidden-text tricks and known injection phrases
import re
from typing import Iterable

# Patterns that have no business in a legitimate user document
SUSPICIOUS_PHRASES = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"you\s+are\s+now\s+(a|an)",
    r"(system|assistant)\s*:\s*new\s+instructions?",
    r"\bsend_email\b|\bwebhook\b|\bcurl\b|\bexec\b",
    r"sk-[a-zA-Z0-9]{20,}",  # API keys in the document
]
SUSPICIOUS_REGEX = re.compile("|".join(SUSPICIOUS_PHRASES), re.IGNORECASE)

def sanitize_document(raw_text: str) -> tuple[str, list[str]]:
    """Clean a document and report what was stripped.

    Returns (cleaned_text, list_of_findings).
    Non-empty findings => treat with suspicion (refusal, human review, etc.).
    """
    findings = []

    # 1. Remove invisible control characters (zero-width, RTL override)
    cleaned = re.sub(r"[\u200B-\u200F\u202A-\u202E\uFEFF]", "", raw_text)

    # 2. Remove markup blocks that have no reason to be there
    cleaned = re.sub(r"</?(system|assistant|instruction)[^>]*>", "", cleaned,
                     flags=re.IGNORECASE)

    # 3. Spot injection phrases — we do NOT remove them (we want to know),
    #    we log them and let the caller decide
    for match in SUSPICIOUS_REGEX.finditer(cleaned):
        findings.append(match.group()[:80])

    return cleaned, findings

# Usage
raw = extract_text_from_pdf("cv_candidate.pdf")
clean, findings = sanitize_document(raw)
if findings:
    logger.warning("Injection-like patterns in document", extra={"findings": findings})
    # Product policy: refuse, escalate, or continue with a classifier model?
    raise DocumentRejected(f"Suspicious content: {findings[:3]}")

safe_input = f"Summarize this resume:\n<document>{clean}</document>"
result = await Runner.run(cv_agent, input=safe_input)
