"""Tag every word with spaCy and count verbs, adjectives and nouns in each text."""

import time

import pandas as pd
import spacy


def load_model():
    """Load spaCy's small English model, downloading it the first time."""
    try:
        return spacy.load("en_core_web_sm", disable=["ner", "parser"])
    except OSError:
        from spacy.cli import download

        download("en_core_web_sm")
        return spacy.load("en_core_web_sm", disable=["ner", "parser"])


def extract_clt_features(df, text_col, key_col="url", n_process=2, batch_size=2000):
    """Count parts of speech in each text.

    Returns one row per text: url_key, verb_count, adj_count, noun_count, word_count.
    Each word counts once. Helping verbs (spaCy's AUX tag, e.g. "is") are not counted as verbs.
    """
    if spacy.prefer_gpu():
        print("GPU detected.")
    nlp = load_model()

    rows = df[[key_col, text_col]].dropna()
    texts = rows[text_col].astype(str).tolist()
    keys = rows[key_col].tolist()

    print(f"Processing {len(texts)} texts...")
    start = time.time()

    features = []
    docs = nlp.pipe(texts, batch_size=batch_size, n_process=n_process)
    for key, doc in zip(keys, docs):
        tags = [token.pos_ for token in doc]
        features.append({
            "url_key": key,
            "verb_count": tags.count("VERB"),
            "adj_count": tags.count("ADJ"),
            "noun_count": tags.count("NOUN"),
            "word_count": len(doc),
        })

    print(f"Done in {time.time() - start:.1f} seconds.")
    return pd.DataFrame(features)
