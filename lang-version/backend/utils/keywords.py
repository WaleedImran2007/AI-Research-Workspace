import spacy

# Loaded lazily (only when extract_keywords is first called) so the model
# isn't pulled into memory on every app startup/import, and only when BM25
# search is actually used. We also disable the "parser" and "ner" pipeline
# components since only tokenization/lemmatization/stopword info is used
# below - these two components are the largest part of the model's memory
# footprint and dropping them does not change extract_keywords' output.
_nlp = None


def _get_nlp():
    global _nlp

    if _nlp is None:
        print("Loading spaCy Keyword Model...")
        _nlp = spacy.load("en_core_web_sm", disable=["parser", "ner"])
        print("spaCy Keyword Model Loaded!")

    return _nlp


def extract_keywords(text: str):
    nlp = _get_nlp()
    doc = nlp(text)

    keywords = []

    for token in doc:
        if(
            not token.is_stop and
            not token.is_punct and 
            not token.is_space and
            token.is_alpha
        ):
            keywords.append(token.lemma_.lower())

    return sorted(set(keywords))