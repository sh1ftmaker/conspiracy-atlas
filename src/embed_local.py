"""Embed every theory in docs/data.json with a LOCAL sentence-transformers
model — no Google API key needed. Drop-in alternative to embed_theories.py:
same input text construction, same .npz output shape, so project_embed.py
consumes the result unchanged.

Default model is Qwen/Qwen3-Embedding-0.6B (Apache-2.0, ~600M params,
top-tier MTEB retrieval/STS quality, runs on any recent GPU or CPU).
Vectors are unit-normalized (cosine == dot, ideal for UMAP).

Usage:
  python embed_local.py --out ../out/embeddings.npz
  # or with a different model / on CPU:
  python embed_local.py --out ../out/embeddings.npz --model BAAI/bge-m3 --device cpu

Note: switching embedding models re-lays-out the whole semantic map (UMAP
runs fresh on the new space). Old and new embeddings must never be mixed in
one npz.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def log(*a):
    print(*a, file=sys.stderr, flush=True)


def load_rows(data_json: Path):
    """Identical text construction to embed_theories.py."""
    d = json.loads(data_json.read_text(encoding="utf-8"))
    ids, texts = [], []
    for t in d["theories"]:
        parts = [t["name"], t.get("summary", "")]
        ev = [x if isinstance(x, str) else (x.get("text") or "")
              for x in t.get("evidence_for", []) if x]
        parts += ev[:3]
        text = " ".join(p.strip() for p in parts if p and p.strip())
        if len(text) > 6000:
            text = text[:6000]
        ids.append(t["id"])
        texts.append(text)
    return ids, texts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(Path(__file__).resolve().parent.parent / "docs" / "data.json"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="Qwen/Qwen3-Embedding-0.6B")
    ap.add_argument("--device", default=None, help="cuda / cpu (default: auto)")
    ap.add_argument("--batch", type=int, default=32)
    args = ap.parse_args()

    from sentence_transformers import SentenceTransformer

    ids, texts = load_rows(Path(args.data))
    log(f"loaded {len(ids)} theories")

    model = SentenceTransformer(args.model, device=args.device)
    log(f"model {args.model} on {model.device}")

    mat = model.encode(texts, batch_size=args.batch, normalize_embeddings=True,
                       show_progress_bar=True).astype(np.float32)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, ids=np.array(ids), vectors=mat,
                        model=args.model, dim=mat.shape[1])
    log(f"wrote {out} -> {mat.shape}")


if __name__ == "__main__":
    main()
