# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**
My questions cover distinct topics across the corpus, but one asks about a specific dining hall policy that only appears in a single short forum post. Because vector embeddings can sometimes favor broader campus threads over that single document, setting the target to 4 of 5 tests retrieval strength while leaving room for document scarcity.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
This is set strictly to 5 of 5 because source attribution is enforced directly in the system prompt (`GROUNDING_INSTRUCTION`), which mandates citing the source file name for every claim. Because the template injects the filename metadata alongside each retrieved context block, any missing citation indicates an instruction-following failure in the generation model rather than a data issue.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

**Why this target:**
In Milestone 4 testing, my in-scope questions clustered at distances between 0.38 and 0.52, while unrelated queries averaged around 0.76 to 0.85. Setting a 4 of 5 target at my 0.60 threshold allows a margin for occasional cross-domain vocabulary overlap (e.g., an out-of-scope query using common words like "hours" or "access") while ensuring the gate reliably stops genuinely foreign topics before hitting the LLM.

---

## 4. Something about your chunks

At least 4 of 5 randomly sampled chunks consist of complete, self-contained thoughts with no mid-sentence cuts or orphan section titles, and no chunk in the entire index is shorter than 150 characters.

**Why this target:**
The starter chunker left a 2-character trailing fragment and repeatedly cut sentences in half. In this corpus, advice threads and reviews rely on causal sentences ("Don't take the 8 AM because..."). Bounding chunks above 150 characters eliminates meaningless headers, while the 4 of 5 complete-thought threshold ensures semantic integrity when embedding.

---

## 5. Your choice

For all 5 test questions, the generated response contains zero factual claims that cannot be traced directly back to the text in the retrieved chunks.

**Why this target:**
The core failure mode of campus RAG systems is hallucinating standard college assumptions (e.g., assuming typical 24/7 library policies or generic pass/fail rules). Setting this target to 5 of 5 tests whether the system strictly grounds its answers in what the student corpus actually says rather than falling back on the model's pre-trained parametric knowledge.

---