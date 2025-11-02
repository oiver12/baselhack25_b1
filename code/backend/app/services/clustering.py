import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_similarity


def centroid(embeddings: np.ndarray) -> np.ndarray:
    if len(embeddings) == 0:
        raise ValueError("Empty embeddings")
    return np.mean(embeddings, axis=0)


def intra_similarity(embeddings: np.ndarray) -> float:
    if len(embeddings) <= 1:
        return 1.0 if len(embeddings) == 1 else 0.0
    sim = cosine_similarity(embeddings)
    triu = np.triu_indices_from(sim, k=1)
    return float(np.mean(sim[triu])) if len(triu[0]) else 0.0


def sentiment_metrics(messages) -> dict[str, float]:
    sentiment_map = {"positive": 1, "neutral": 0, "negative": -1}
    vals = [sentiment_map.get(m.classification or "neutral", 0) for m in messages]
    if not vals:
        return {"avg": 0.0, "std": 0.0}
    return {"avg": float(np.mean(vals)), "std": float(np.std(vals))}


def assign_nearest(msg_emb, clusters, threshold: float):
    if not clusters:
        return None
    sims = [
        cosine_similarity(msg_emb.reshape(1, -1), np.array(c.centroid).reshape(1, -1))[0][0]
        for c in clusters
    ]
    best = np.argmax(sims)
    return best if sims[best] >= threshold else None


def cluster_embeddings(embs: np.ndarray, min_sim: float, max_clusters: int):
    sim = cosine_similarity(embs)
    dist = 1 - sim
    n, best_labels = len(embs), None
    lo, hi = 1, n
    while lo < hi:
        k = (lo + hi) // 2
        labels = AgglomerativeClustering(
            n_clusters=k, metric="precomputed", linkage="average"
        ).fit_predict(dist)
        valid = True
        for cid in np.unique(labels):
            idx = np.where(labels == cid)[0]
            if len(idx) <= 1:
                continue
            avg_sim = np.mean(sim[np.ix_(idx, idx)][np.triu_indices(len(idx), 1)])
            if avg_sim < min_sim:
                valid = False
                break
        if valid:
            best_labels, hi = labels, k
        else:
            lo = k + 1
    if best_labels is None:
        best_labels = AgglomerativeClustering(
            n_clusters=min(max_clusters, n), metric="precomputed", linkage="average"
        ).fit_predict(dist)
    return best_labels