import PyPDF2
import docx2txt
import re
from collections import Counter


# ---------------- TEXT EXTRACTION ----------------
def extract_text(file):
    text = ""

    if file.type == "application/pdf":
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""

    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = docx2txt.process(file)

    elif file.type == "text/plain":
        text = str(file.read(), "utf-8")

    return text


# ---------------- CLASSIFICATION ----------------
def classify_document(text):
    text = text.lower()

    categories = {
        "Business": ["stock", "market", "finance", "money"],
        "Education": ["study", "exam", "notes", "class"],
        "News": ["news", "report", "breaking"],
        "Story": ["once", "king", "forest", "story"]
    }

    scores = {c: 0 for c in categories}

    for cat, words in categories.items():
        for w in words:
            if w in text:
                scores[cat] += 1

    best = max(scores, key=scores.get)
    return best, scores


# ---------------- SUMMARY ----------------
def summarize_text(text):
    text = re.sub(r'\s+', ' ', text)
    sentences = re.split(r'(?<=[.!?]) +', text)

    if len(sentences) <= 2:
        return text

    words = re.findall(r'\w+', text.lower())

    stopwords = set(["the","is","in","and","to","of","a","for","on","with"])

    filtered = [w for w in words if w not in stopwords]
    freq = Counter(filtered)

    scores = {}

    for s in sentences:
        score = 0
        for w in s.lower().split():
            if w in freq:
                score += freq[w]
        scores[s] = score

    top = sorted(scores, key=scores.get, reverse=True)[:2]

    return " ".join(top)