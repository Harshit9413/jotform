import re
from typing import List


def chunk_text(text: str, max_size: int = 600) -> List[str]:
    paragraphs = re.split(r'\n{2,}', text.strip())
    chunks: List[str] = []
    current = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        if len(current) + len(para) + 2 <= max_size:
            current = (current + "\n\n" + para).strip() if current else para
        else:
            if current:
                chunks.append(current)
            if len(para) <= max_size:
                current = para
            else:
                words = para.split()
                sub: List[str] = []
                for w in words:
                    sub.append(w)
                    if len(" ".join(sub)) >= max_size:
                        chunks.append(" ".join(sub))
                        sub = sub[-15:]
                current = " ".join(sub) if sub else ""
    if current:
        chunks.append(current)
    return chunks or [text[:max_size]]


def score_chunk(query: str, chunk: str) -> float:
    q_words = set(re.findall(r'\w{3,}', query.lower()))
    c_words = set(re.findall(r'\w{3,}', chunk.lower()))
    if not q_words:
        return 0.0
    return len(q_words & c_words) / len(q_words)


def retrieve(query: str, documents: List[dict], top_k: int = 3) -> List[str]:
    scored = []
    for doc in documents:
        for chunk in chunk_text(doc["content"]):
            scored.append((score_chunk(query, chunk), chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored[:top_k] if score > 0]
