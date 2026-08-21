import spacy

_nlp = None
_docs_processed = 0
_RELOAD_EVERY = int(__import__("os").environ.get("SPACY_RELOAD_EVERY", "200"))


def _get_nlp():
    global _nlp, _docs_processed

    if _nlp is None:
        print("Loading spaCy Keyword Model...")
        _nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        _docs_processed = 0
        print("spaCy Keyword Model Loaded!")

    return _nlp


def extract_keywords(text: str):
    global _docs_processed

    nlp = _get_nlp()
    doc = nlp(text)

    keywords = []
    for token in doc:
        if (
            not token.is_stop and
            not token.is_punct and
            not token.is_space and
            token.is_alpha
        ):
            keywords.append(token.lemma_.lower())

    _docs_processed += 1

    # spaCy's vocab.strings table grows permanently and is never freed -
    # periodically drop and reload the model so it doesn't accumulate
    # across the server's entire uptime.
    if _docs_processed >= _RELOAD_EVERY:
        _nlp = None

    return sorted(set(keywords))

# import re

# # Common English stopwords.
# STOPWORDS = {
#     "a", "an", "the", "and", "or", "but", "if", "then",
#     "of", "in", "on", "at", "to", "for", "from", "by",
#     "with", "about", "as", "is", "are", "was", "were",
#     "be", "been", "being", "this", "that", "these", "those",
#     "it", "its", "they", "them", "their", "there",
#     "he", "she", "his", "her", "we", "you", "your",
#     "i", "me", "my", "our", "us",
#     "do", "does", "did", "have", "has", "had",
#     "can", "could", "will", "would", "should",
#     "what", "which", "who", "whom", "where", "when",
#     "why", "how"
# }


# def extract_keywords(text: str):
#     words = re.findall(r"[a-zA-Z]+", text.lower())

#     return [
#         word
#         for word in words
#         if word not in STOPWORDS
#     ]