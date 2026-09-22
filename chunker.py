"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document

# The floor a chunk has to clear before it stands on its own (see criteria.md
# #4). A paragraph shorter than this reads as a fragment, not a complete
# thought, and gets merged into a neighboring paragraph instead of becoming
# its own chunk.
MIN_CHUNK_CHARS = 150

# A leading line shorter than this is treated as a title/heading rather than
# real content (e.g. "On the housing lottery" sitting alone on its own line)
# and gets folded into the paragraph that follows it, instead of being left
# to stand alone as a near-empty chunk.
TITLE_LINE_MAX_CHARS = 60


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def _paragraphs(text: str) -> list[str]:
    """
    Split one document's text into paragraphs on blank lines, then clean up
    the two ways a plain paragraph split goes wrong on these documents:

      - The first "paragraph" is often just a short title line
        ("On the housing lottery"). Left alone, that becomes a near-empty
        chunk that answers nothing. It gets folded into the paragraph after
        it instead.
      - Any paragraph under MIN_CHUNK_CHARS (a one-line aside, a stray
        heading) is a fragment on its own. It gets merged into a
        neighboring paragraph rather than shipped as its own chunk.
    """
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    if not paras:
        return []

    if len(paras) > 1 and len(paras[0]) < TITLE_LINE_MAX_CHARS:
        paras = [paras[0] + "\n\n" + paras[1]] + paras[2:]

    merged: list[str] = []
    for p in paras:
        if merged and len(p) < MIN_CHUNK_CHARS:
            merged[-1] = merged[-1] + "\n\n" + p
        else:
            merged.append(p)

    # If the merge above still leaves a short first paragraph (nothing came
    # before it to absorb into), fold it forward into the second instead.
    if len(merged) > 1 and len(merged[0]) < MIN_CHUNK_CHARS:
        merged[1] = merged[0] + "\n\n" + merged[1]
        merged = merged[1:]

    return merged


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Split documents into chunks by paragraph, not by a fixed character count.

    campus_life is 88 short forum-style posts averaging ~317 characters —
    well under the fallback's 800-character window, which is why that
    chunker never actually split anything (88 docs in, 88 chunks out).
    Reading the corpus in Milestone 1 showed most posts are already a single
    self-contained thought (`admin_housing_lottery.txt`,
    `admin_parking_permits.txt`), but a handful bundle several distinct
    points under one heading — pros, cons, and a logistics aside in
    `housing_old_brewhouse.txt`; hours vs. seating in
    `study_library_hours.txt`. Those deserve to come apart so a question
    about one point doesn't retrieve the other three along with it.

    So: split on paragraph breaks, but treat a lone title line as part of
    the paragraph that follows it, and refuse to let any paragraph stand
    alone as a chunk once it's short enough to be a fragment
    (MIN_CHUNK_CHARS, matching criterion 4's 150-character floor) — merging
    it into a neighbor instead. Net effect on this corpus: 88 documents
    become 92 chunks. 84 posts stay exactly as they were (one genuine
    thought, one chunk); only 4 posts split into two.

    There's no overlap parameter here — these are semantic (paragraph)
    boundaries, not a sliding window, so there's no shared boilerplate at
    the edges to worry about losing.
    """
    chunks: list[Chunk] = []
    for doc in documents:
        for index, paragraph in enumerate(_paragraphs(doc.text)):
            chunks.append(
                Chunk(
                    text=paragraph,
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )
    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))