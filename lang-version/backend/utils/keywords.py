import spacy

nlp = spacy.load("en_core_web_sm")

def extract_keywords(text: str):
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