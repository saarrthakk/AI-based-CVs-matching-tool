import spacy
from sentence_transformers import SentenceTransformer, util
import numpy as np # Often useful with embeddings, though not directly used in the functions below

# --- SPACY MODEL LOADING ---
# Load spaCy model at the module level.
# This code runs only ONCE when 'text_processing' is first imported.
try:
    nlp = spacy.load("en_core_web_sm")
    print("spaCy model 'en_core_web_sm' loaded successfully.") # Optional: for debugging
except OSError:
    print("spaCy model 'en_core_web_sm' not found. Attempting download...")
    from spacy.cli import download
    try:
        download("en_core_web_sm")
        nlp = spacy.load("en_core_web_sm")
        print("spaCy model 'en_core_web_sm' downloaded and loaded.")
    except Exception as e:
        print(f"Failed to download and load spaCy model: {e}")
        print("Please run 'python -m spacy download en_core_web_md' manually.")
        nlp = None # Set to None if loading fails to prevent further errors


# --- SENTENCE-TRANSFORMERS MODEL LOADING ---
# Load Sentence-Transformer model at the module level.
# This code also runs only ONCE when 'text_processing' is first imported.
try:
    sbert_model = SentenceTransformer('all-MiniLM-L6-v2')
    print("Sentence-Transformer model 'all-MiniLM-L6-v2' loaded successfully.") # Optional: for debugging
except Exception as e:
    print(f"Error loading Sentence-Transformer model: {e}")
    print("Please ensure 'sentence-transformers' is installed and you have an internet connection for first-time download.")
    sbert_model = None # Set to None and handle this in the semantic_match_score function


# --- YOUR TEXT PROCESSING FUNCTIONS ---
def extract_entities(text):
    """
    Extract named entities using spaCy.
    Returns list of tuples: (entity_text, entity_label)
    """
    if nlp is None:
        print("spaCy model not available. Cannot extract entities.")
        return []
    doc = nlp(text)
    entities = [(ent.text.strip(), ent.label_) for ent in doc.ents]
    return entities

def extract_nouns_verbs(text):
    """
    Extract key nouns, proper nouns, and verbs — useful for skills/tools/tasks.
    """
    if nlp is None:
        print("spaCy model not available. Cannot extract nouns/verbs.")
        return []
    doc = nlp(text)
    keywords = [
        token.lemma_.lower()
        for token in doc
        if token.pos_ in ["NOUN", "PROPN", "VERB"]
        and not token.is_stop
        and token.is_alpha
    ]
    return sorted(set(keywords))

def extract_keywords(text):
    """
    Extract a clean set of keyword lemmas — suitable for matching with JD.
    Focuses on nouns and proper nouns only.
    """
    if nlp is None:
        print("spaCy model not available. Cannot extract keywords.")
        return []
    doc = nlp(text)
    keywords = [
        token.lemma_.lower()
        for token in doc
        if token.pos_ in ["NOUN", "PROPN"]
        and not token.is_stop
        and token.is_alpha
    ]
    return sorted(set(keywords))

def semantic_match_score(text1, text2):
    """
    Calculates the semantic similarity score between two texts using Sentence-Transformers.
    Returns a score between 0 and 1.
    """
    if sbert_model is None:
        print("Semantic embedding model not loaded, returning 0 score.")
        return 0.0

    if not text1 or not text2: # Handle empty texts
        return 0.0

    # Encode the texts into embeddings
    embeddings1 = sbert_model.encode(text1, convert_to_tensor=True)
    embeddings2 = sbert_model.encode(text2, convert_to_tensor=True)

    # Calculate cosine similarity
    score = util.cos_sim(embeddings1, embeddings2).item()

    # Scores from cosine similarity can range from -1 to 1.
    # Convert to 0-1 scale for easier interpretation in this context.
    # (score + 1) / 2 maps -1 to 0, 0 to 0.5, 1 to 1.
    return (score + 1) / 2