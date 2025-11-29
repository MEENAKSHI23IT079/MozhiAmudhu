# app/summarizer.py
"""
Summarizer module (lightweight, offline-friendly).

Generates two DIFFERENT summaries:
- generate_official_summary(text, sentences=3): extractive, formal, picks policy/command sentences
- generate_simplified_summary(text, bullets=5): short citizen-friendly bullets, short sentences

Algorithm:
- Sentence split via regex.
- Word frequency scoring (simple tokenization, basic stopwords).
- Official summary: choose sentences with high score and presence of directive keywords.
- Simplified summary: choose top-scoring short sentences and compress them into bullet points.
"""

import re
import math
from typing import List, Tuple

# Basic English stopwords (small set; extend if needed)
_STOPWORDS = {
    "the","and","a","an","of","in","on","for","to","is","are","was","were",
    "that","this","with","by","as","be","will","shall","has","have","it",
    "at","from","or","which","may","can","should","their","its","all","such"
}

# Directive / policy keywords to prioritize in official summary
_DIRECTIVE_KEYWORDS = {
    "must", "shall", "should", "required", "instruct", "instructed",
    "ensure", "require", "implement", "compliance", "comply", "notify",
    "mandatory", "direct", "order", "issue", "issued", "deadline", "effective"
}

_SENT_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')

def _split_sentences(text: str) -> List[str]:
    text = text.strip().replace("\r\n", "\n").replace("\t", " ")
    # naive split keeps punctuation
    sents = [s.strip() for s in _SENT_SPLIT_RE.split(text) if s.strip()]
    return sents

def _tokenize_words(text: str) -> List[str]:
    # lowercase and split on non-word, keep alphanumeric tokens
    tokens = re.findall(r"[A-Za-z0-9]+(?:'[A-Za-z0-9]+)?", text.lower())
    return tokens

def _score_sentences(sentences: List[str]) -> List[float]:
    # Build word frequency excluding stopwords
    freq = {}
    for s in sentences:
        for w in _tokenize_words(s):
            if w in _STOPWORDS:
                continue
            freq[w] = freq.get(w, 0) + 1

    # Normalize
    if not freq:
        return [0.0]*len(sentences)
    maxf = max(freq.values())
    for k in list(freq.keys()):
        freq[k] = freq[k] / maxf

    # Sentence score = sum(normed frequencies / sqrt(length) to slightly prefer concise sentences
    scores = []
    for s in sentences:
        tokens = [w for w in _tokenize_words(s) if w not in _STOPWORDS]
        if not tokens:
            scores.append(0.0)
            continue
        raw = sum(freq.get(t, 0) for t in tokens)
        length_penalty = math.sqrt(len(tokens))
        scores.append(raw / (length_penalty if length_penalty > 0 else 1.0))
    return scores

def _contains_directive(sentence: str) -> bool:
    s = sentence.lower()
    for kw in _DIRECTIVE_KEYWORDS:
        if kw in s:
            return True
    return False

def generate_official_summary(text: str, sentences: int = 3) -> str:
    """
    Produce an official, formal summary of the text.
    Strategy:
      - split sentences
      - score sentences by frequency
      - boost sentences that include directive keywords
      - select top sentences preserving original order
    """
    if not text or not text.strip():
        return ""

    sents = _split_sentences(text)
    if not sents:
        return ""

    scores = _score_sentences(sents)

    # Boost directive sentences
    boosted = []
    for i, sent in enumerate(sents):
        score = scores[i]
        if _contains_directive(sent):
            score *= 1.6  # boost factor for directives/policies
        # Slightly favor sentences near beginning (lead bias)
        lead_factor = 1.0 + max(0, (1.0 - (i / max(1, len(sents)))) * 0.15)
        score *= lead_factor
        boosted.append((i, score))

    # pick top N sentences
    boosted_sorted = sorted(boosted, key=lambda x: x[1], reverse=True)
    top_idx = sorted([idx for idx, _ in boosted_sorted[:sentences]])

    # Build summary, preserving original order, join as paragraph
    chosen = [sents[i].rstrip() for i in top_idx]
    # Make sure sentences end with punctuation
    for i in range(len(chosen)):
        if chosen[i] and chosen[i][-1] not in ".!?":
            chosen[i] += "."
    summary = " ".join(chosen)
    return summary.strip()

def _shorten_sentence(s: str, max_words: int = 20) -> str:
    words = s.split()
    if len(words) <= max_words:
        return s.strip()
    # prefer chopping after comma if available in first max_words+5
    first = " ".join(words[: max_words + 5])
    comma_pos = first.find(",")
    if comma_pos != -1:
        # cut at nearest comma before or at max_words boundary
        short = first[:comma_pos]
        return short.strip().rstrip(" ,;") + "."
    # fallback: simple truncation
    return " ".join(words[:max_words]).strip().rstrip(" ,;") + "..."

def generate_simplified_summary(text: str, bullets: int = 5, max_words_per_bullet: int = 18) -> str:
    """
    Produce a simplified, citizen-friendly bullet list.
    Strategy:
      - split sentences
      - score by frequency
      - prefer short sentences and those with directives
      - produce bullets (shortened)
    """
    if not text or not text.strip():
        return ""

    sents = _split_sentences(text)
    if not sents:
        return ""

    scores = _score_sentences(sents)

    # rank sentences but prefer short ones and directive ones
    ranked = []
    for i, sent in enumerate(sents):
        score = scores[i]
        length = len(_tokenize_words(sent))
        length_factor = 1.0 / (1.0 + (length / 25.0))  # prefer shorter sentences moderately
        directive_boost = 1.4 if _contains_directive(sent) else 1.0
        final = score * length_factor * directive_boost
        ranked.append((i, final))

    ranked_sorted = sorted(ranked, key=lambda x: x[1], reverse=True)
    chosen_indices = []
    for idx, _ in ranked_sorted:
        if len(chosen_indices) >= bullets:
            break
        # avoid near-duplicates: skip sentences that are very similar to already chosen (simple substring check)
        candidate = sents[idx].lower()
        skip = False
        for j in chosen_indices:
            if candidate in sents[j].lower() or sents[j].lower() in candidate:
                skip = True
                break
        if not skip:
            chosen_indices.append(idx)

    # If not enough bullets chosen, fill with top remaining short sentences
    if len(chosen_indices) < bullets:
        for idx, _ in ranked_sorted:
            if idx not in chosen_indices:
                chosen_indices.append(idx)
            if len(chosen_indices) >= bullets:
                break

    # Preserve original order for readability
    chosen_indices = sorted(chosen_indices)
    bullets_out = []
    for idx in chosen_indices:
        s = sents[idx].strip()
        s_short = _shorten_sentence(s, max_words=max_words_per_bullet)
        # Clean trailing punctuation
        s_short = s_short.strip()
        if s_short and s_short[-1] not in ".!?":
            s_short += "."
        bullets_out.append("- " + s_short)

    return "\n".join(bullets_out)

# convenience wrapper returning both
def generate_both_summaries(text: str, official_sentences: int = 3, simplified_bullets: int = 5) -> dict:
    return {
        "official": generate_official_summary(text, sentences=official_sentences),
        "simplified": generate_simplified_summary(text, bullets=simplified_bullets)
    }

# Module test
if __name__ == "__main__":
    sample = (
        "CIRCULAR NO. 2024/112. Date: 12.08.2024. "
        "Subject: Implementation of Digital Attendance System in All Government Schools. "
        "The Government of Tamil Nadu has decided to introduce a Digital Attendance System for all teaching "
        "and non-teaching staff across government and government-aided schools. This initiative aims to improve "
        "transparency, track attendance accurately, and provide real-time data to the Department. "
        "All Headmasters are instructed to ensure the installation of the attendance devices before 30th August 2024. "
        "Training for staff will be conducted between 20th–25th August 2024."
    )
    print("OFFICIAL:\n", generate_official_summary(sample, sentences=3))
    print("\nSIMPLIFIED:\n", generate_simplified_summary(sample, bullets=4))
