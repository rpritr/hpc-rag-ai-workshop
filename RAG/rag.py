"""Small RAG pipeline for the HPC workshop.

Each non-empty line in cat-facts.txt is one fact.
Ollama embeds the facts, we keep the closest ones, and a second
Ollama model writes the answer from those facts only.

The Ollama server must already be running (see run_rag.sh).
"""

from pathlib import Path

import numpy as np
import ollama

KB_PATH = Path(__file__).resolve().parent / "cat-facts.txt"
EMBED_MODEL = "mxbai-embed-large"
LLM_MODEL = "llama3"
TOP_K = 4

_kb = None


def load_facts(path=KB_PATH):
    lines = path.read_text(encoding="utf-8").splitlines()
    facts = [line.strip() for line in lines if line.strip()]
    if not facts:
        raise SystemExit(f"No facts found in {path}")
    return facts


def _field(obj, name):
    if isinstance(obj, dict):
        return obj[name]
    return getattr(obj, name)


def embed(text):
    """Return one embedding vector for a string."""
    if hasattr(ollama, "embed"):
        response = ollama.embed(model=EMBED_MODEL, input=text)
        vector = _field(response, "embeddings")[0]
    else:
        response = ollama.embeddings(model=EMBED_MODEL, prompt=text)
        vector = _field(response, "embedding")
    return np.asarray(vector, dtype=np.float32)


class KnowledgeBase:
    def __init__(self, facts):
        self.facts = facts
        vectors = []
        total = len(facts)
        for i, fact in enumerate(facts, start=1):
            vectors.append(embed(fact))
            if i % 25 == 0 or i == total:
                print(f"  embedded {i}/{total}", flush=True)
        self.vectors = np.vstack(vectors)

    def search(self, query, k=TOP_K):
        query_vector = embed(query)
        fact_norms = np.linalg.norm(self.vectors, axis=1)
        query_norm = np.linalg.norm(query_vector)
        scores = self.vectors @ query_vector / (fact_norms * query_norm + 1e-10)
        best = np.argsort(scores)[::-1][:k]
        return [(self.facts[i], float(scores[i])) for i in best]


def get_kb():
    """Build the index once per process and reuse it."""
    global _kb
    if _kb is None:
        facts = load_facts()
        print(f"Building the search index ({len(facts)} facts)...", flush=True)
        _kb = KnowledgeBase(facts)
    return _kb


def answer(query, k=TOP_K):
    hits = get_kb().search(query, k=k)
    print("Retrieved facts:", flush=True)
    for fact, score in hits:
        print(f"  [{score:.3f}] {fact}", flush=True)

    context = "\n".join(f"- {fact}" for fact, _score in hits)
    prompt = (
        "Answer the question in two or three sentences using only the facts below. "
        "If the facts do not contain the answer, say you do not know.\n\n"
        f"Facts:\n{context}\n\n"
        f"Question: {query}\n"
        "Answer:"
    )
    response = ollama.generate(
        model=LLM_MODEL,
        prompt=prompt,
        options={"temperature": 0},
    )
    return _field(response, "response").strip()
