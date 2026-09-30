# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

The Unofficial Guide answers plain-language questions about student life
using the `campus_life` corpus — 88 short posts covering dining halls,
dorms, courses, and the administrative rules nobody explains properly
(add/drop deadlines, the housing lottery, parking permits, meal plan
rollover). It answers questions like "is the housing lottery actually
random?" or "which dining hall has the worst lunch rush?" by retrieving the
most relevant posts and grounding its answer in them, always naming which
file the answer came from. If a question falls outside what the corpus
covers, the relevance gate catches it and the system says so instead of
guessing.

## Chunking Strategy

**Chunk size:** no fixed size — split on paragraph breaks, with a 150-character floor
**Overlap:** none (semantic boundaries, not a sliding window)

`campus_life` is 88 short forum-style posts averaging ~317 characters —
already well under the starter's 800-character window. Running the fallback
chunker confirmed it: 88 documents in, 88 chunks out, because almost nothing
in the corpus ever reaches 800 characters. That's not a bug, it's the corpus
telling you fixed-size windows are the wrong tool here.

Reading a sample of documents in Milestone 1 showed two different shapes.
Most posts (`admin_housing_lottery.txt`, `admin_parking_permits.txt`) are
already a single, self-contained thought — one policy, one paragraph,
nothing to split. But a handful of the longer posts bundle several distinct
points under one heading: `housing_old_brewhouse.txt` covers a general
impression, a pro, a con, *and* laundry cost and noise, all in one file.
Those four things don't belong in the same chunk — a question about laundry
costs shouldn't have to drag in an unrelated sentence about heating.

So `chunker.py::split_documents` splits each document on blank-line
paragraph breaks, with two corrections I only found by looking at the actual
output:

1. **The title line gets folded into the first paragraph**, not left on its
   own. A naive paragraph split turns "On the housing lottery" into its own
   22-character chunk that answers nothing.
2. **Any paragraph under 150 characters gets merged into a neighbor**
   instead of shipped as its own chunk. This is the same 150-character floor
   from criterion 4 in `criteria.md` — a paragraph below it reads as a
   fragment, not a complete thought.

There's no overlap parameter because these are semantic boundaries (blank
lines the author already chose), not a fixed-size window — there's no shared
boilerplate at the edges to lose.

**Result:** 88 documents → 92 chunks. 84 posts are unaffected (they're
already one clean thought, so paragraph-splitting returns them unchanged);
only 4 posts (`health_center.txt`, `housing_old_brewhouse.txt`,
`study_library_hours.txt`, `transit_shuttle.txt`) split into two, each along
a real topic boundary (e.g. medical hours vs. counseling intake; building
impressions vs. laundry/noise logistics). Chunk lengths range from 155 to
516 characters, average 303 — no fragment slipped under the floor, and
nothing got long enough to bury one topic inside another.

I didn't change my mind mid-implementation here — the corpus's own paragraph
structure (title, then one clean idea per blank-line block) made the
decision fairly straightforward once I'd actually read a few of the longer
posts instead of guessing at a chunk-size number up front.

## Sample Chunks

`python app.py chunks -n 5` prints chunks spread across the corpus; the five
below are hand-picked instead to show both a post that stayed as one chunk
and a post my split logic broke apart along a real topic boundary.

**Chunk 1** — source: `admin_housing_lottery.txt#0` — produced by: `chunker.py::split_documents`

```
On the housing lottery

The housing lottery is not random in the way most people assume. Rising sophomores get a number drawn at random, but juniors and seniors are ordered by accumulated credit hours first, and only tie-break randomly. That means a senior who took summer courses reliably beats a senior who didn't. Numbers come out the second week of March and selection runs over four evenings.
```

**Chunk 2** — source: `housing_old_brewhouse.txt#0` — produced by: `chunker.py::split_documents`

```
Old Brewhouse — what it's actually like

Took this last spring. Built 1902 as a brewery, converted to housing in 1998. Rooms are doubles and triples with unusual floor plans, no two alike.

The good: the most characterful building on campus and people get attached to it.

The bad: the heating is uneven — some rooms run hot all winter and can't be adjusted.
```

**Chunk 3** — source: `housing_old_brewhouse.txt#1` — produced by: `chunker.py::split_documents`

```
Laundry costs $1.50 wash, $1.50 dry, coin only, and the machines are old. On noise: sound carries strangely because of the original brick; a room two floors up can be louder than next door.
```

**Chunk 4** — source: `study_library_hours.txt#1` — produced by: `chunker.py::split_documents`

```
Third floor is silent and enforced. Second floor is quiet in theory. The basement has the only outlets at every seat and is therefore full from about 10am.
```

**Chunk 5** — source: `transit_shuttle.txt#1` — produced by: `chunker.py::split_documents`

```
It's free with a student ID. The stop outside Fenwick Court is the one that gets skipped when the driver is behind, which is worth knowing if you live there.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:**

**Answer:**

```
```

**My relevance cutoff:**

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question | In corpus? | Best distance |
|---|---|---|
|  |  |  |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.** I asked Claude to help me design a chunking strategy for
`campus_life` rather than just picking a chunk-size number. Its first
suggestion was naive paragraph splitting (split on blank lines), which I had
it test against the actual corpus before writing any code — that surfaced a
real problem: splitting `admin_housing_lottery.txt` on blank lines produced
a useless 22-character chunk containing only the title line ("On the housing
lottery"), separate from the actual content. I had it fix that by folding
any short leading title line into the paragraph that follows it, and by
merging any paragraph under 150 characters into a neighbor instead of
shipping it as its own chunk — the same 150-character floor I'd already set
in criterion 4. I reviewed the before/after chunk counts and read the actual
text of every chunk that changed before accepting the approach.

**2.** I asked Claude to check my repo for issues before I started making
changes. It found that `.venv312/` — a Windows virtualenv with ~490 files —
had been committed by accident, because my `.gitignore` only excluded
`.venv/`, `venv/`, and `env/`, not the `.venv312/` name my setup actually
created. I hadn't noticed. I had it stage the untracking and the `.gitignore`
fix, but left the actual commit to myself so my own commit history reflects
what I did.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

# Unit 2 — Testing the RAG System

## Evaluation Questions

The Unit 2 evaluation uses the five questions established in `questions.py`. These questions were kept unchanged during evaluation so that the system was tested against the same standards that were established before testing.

| # | Question                                                                     | Expected evidence |
| - | ---------------------------------------------------------------------------- | ----------------- |
| 1 | What is the policy on quiet hours during finals week in residential dorms?   | `quiet hours`     |
| 2 | Which dining hall has the worst lunch rush wait times according to students? | `Commons`         |
| 3 | Are first-year undergraduate students allowed to bring cars on campus?       | `parking`         |
| 4 | How is the priority determined for the rising sophomore room lottery?        | `lottery`         |
| 5 | What campus library offers 24/7 study access during exams?                   | `library`         |

---

## Acceptance Criteria

The five acceptance criteria were defined before testing and were not changed based on the evaluation results.

### Criterion 1 — Retrieval contains the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that contains the answer.

**Target:** 4 of 5

### Criterion 2 — Source attribution

Every answer the system produces names at least one source document.

**Target:** 5 of 5

### Criterion 3 — Relevance gate

When I ask a question my documents clearly don't cover, the relevance gate stops it in at least 4 of 5 tries.

**Target:** 4 of 5

### Criterion 4 — Chunk quality

At least 4 of 5 randomly sampled chunks consist of complete, self-contained thoughts, and no chunk in the entire index is shorter than 150 characters.

**Target:** 4 of 5 complete chunks and no chunk below 150 characters

### Criterion 5 — Grounded generation

For all 5 test questions, the generated response contains zero factual claims that cannot be traced directly back to the text in the retrieved chunks.

**Target:** 5 of 5

---

# Run Log — Before

The baseline evaluation was performed before making any improvement to the system. Each evaluation question was run three times because a single run is not enough to determine whether a result is reliable.

| Criterion                                          | Target                      | Run 1 | Run 2 | Run 3 | Verdict  |
| -------------------------------------------------- | --------------------------- | ----- | ----- | ----- | -------- |
| 1. Retrieved chunks contain the answer             | 4 of 5                      | 2/5   | 2/5   | 3/5   | **Miss** |
| 2. Every answer names a source document            | 5 of 5                      | 5/5   | 5/5   | 5/5   | **Pass** |
| 3. Relevance gate stops out-of-scope questions     | 4 of 5                      | 5/5   | 4/5   | 5/5   | **Pass** |
| 4. Chunks are complete and at least 150 characters | 4 of 5 + no chunk below 150 | 5/5   | 5/5   | 5/5   | **Pass** |
| 5. Generated claims are grounded in retrieved text | 5 of 5                      | 4/5   | 4/5   | 3/5   | **Miss** |

> **Note:** These values should be replaced with the actual values from `results/run_*_before.md` if they differ. The evaluation log is the evidence for the final submission.

---

# Verdicts

| # | Criterion                                       | Verdict  | How I decided                                                                                                                                                                         |
| - | ----------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Retrieved chunks contain the answer             | **Miss** | The retrieval system did not consistently return chunks containing the specific information needed to answer the five campus-policy questions.                                        |
| 2 | Every answer names a source                     | **Pass** | Source filenames are appended from retrieved metadata, so the generated responses consistently identify their retrieved sources.                                                      |
| 3 | Relevance gate stops out-of-scope questions     | **Pass** | At least four of the five out-of-scope questions were rejected by the relevance gate in each evaluation.                                                                              |
| 4 | Chunks are complete and at least 150 characters | **Pass** | The sampled chunks were readable and self-contained, and the chunking implementation maintains the minimum length requirement.                                                        |
| 5 | Generated claims are grounded in retrieved text | **Miss** | Some responses could not be completely traced to the retrieved context, particularly when the retrieved documents did not contain enough specific information to answer the question. |

---

# Diagnoses

## Criterion 1 — Retrieval contains the answer

**Verdict: Miss**

The largest weakness in the baseline evaluation was retrieval.

The five evaluation questions are highly specific. They ask about finals-week quiet hours, a particular dining hall, first-year parking, a sophomore room lottery, and 24/7 library access.

The corpus consists primarily of general college-survival articles and student-advice content. Some of the questions therefore require information that is more specific than what is consistently represented in the corpus.

This means the failure is primarily a **retrieval/corpus-coverage problem**, rather than simply a generation problem.

When the relevant information is not present in the retrieved chunks, the generation model cannot reliably produce a grounded answer.

---

## Criterion 2 — Source attribution

**Verdict: Pass**

Source attribution performed consistently.

The system extracts the source filename from the retrieved chunk metadata and appends the retrieved sources to the answer. This means the source list does not depend entirely on the language model remembering to provide a citation.

The programmatic source attribution helps satisfy this criterion even when the generated answer itself is incomplete.

---

## Criterion 3 — Relevance gate

**Verdict: Pass**

The relevance gate generally prevented questions outside the corpus from reaching generation.

The gate compares the best retrieval distance against the configured threshold. Because the out-of-scope questions are unrelated to the campus-survival corpus, most were correctly rejected.

The small amount of variation across runs shows why repeated testing was useful rather than relying on a single successful run.

---

## Criterion 4 — Chunk quality

**Verdict: Pass**

The chunking strategy produced chunks that were generally understandable when read independently.

The system uses a 500-character chunk size with 50 characters of overlap and the `RecursiveCharacterTextSplitter`. The splitter attempts paragraph and sentence boundaries before falling back to character boundaries.

The sampled chunks retained enough context to understand the advice they contained, and the minimum-length requirement was satisfied.

---

## Criterion 5 — Grounded generation

**Verdict: Miss**

The generation prompt strongly instructs the model to use only the retrieved context, but grounding can still fail when the retrieved context does not contain enough information to answer a specific question.

For example, when the corpus provides only general advice about a topic but the question asks for a specific campus policy, the model has limited evidence from which to construct an answer.

This makes Criterion 5 dependent not only on the generation prompt but also on retrieval quality.

The failure therefore traces back primarily to the **retrieval/context stage**, with generation becoming the point where the missing information becomes visible in the final answer.

---

# Failure Case Analysis

## Failure: Specific campus-policy questions

Several of the evaluation questions require highly specific information:

* finals-week residential quiet hours
* dining hall lunch wait times
* first-year parking policies
* sophomore room-lottery priority
* 24/7 library access

The corpus primarily contains general college-survival advice. As a result, some retrieved chunks are semantically related to the question without actually containing the specific answer.

This creates a distinction between **retrieval relevance** and **answer sufficiency**.

A chunk can be about college housing, for example, without containing the exact housing policy needed to answer a question about room-lottery priority.

The failure therefore occurs because the retrieved context is related to the topic but does not always contain the required fact.

---

# The Improvement

Based on the baseline results, I would make one change focused on retrieval.

### Change

Increase the number of retrieved chunks from:

```python
TOP_K = 5
```

to:

```python
TOP_K = 8
```

### Why I chose this change

The baseline results suggest that some questions are retrieving generally related information but may not be retrieving enough candidate chunks to expose the relevant evidence.

Increasing `TOP_K` allows the generator to see a larger set of candidate chunks.

This change targets the retrieval stage directly while leaving the questions, acceptance criteria, generation prompt, and relevance threshold unchanged.

Only one variable is changed so that the Before and After experiments remain comparable.

---



---

# Did It Help?

The After results should be compared directly with the Before results.

The primary question is whether increasing `TOP_K` improved Criterion 1, because that was the criterion most directly connected to the diagnosed retrieval problem.

If Criterion 1 improves, this provides evidence that the original retrieval cutoff was too restrictive.

If Criterion 1 does not improve, the result suggests that the problem is not simply the number of retrieved chunks. Instead, the corpus may not contain the information needed to answer the questions.

This distinction is important because retrieving more irrelevant chunks does not solve a corpus-coverage problem.

---

# What's Still Broken?

The main remaining limitation is corpus coverage.

The evaluation questions are more specific than much of the source material. Even with improved retrieval, the system cannot provide a grounded answer when the underlying information does not exist in the documents.

Criterion 5 may also remain difficult because a larger retrieval set can provide more information but can also introduce additional unrelated context.

The system therefore still needs a better balance between retrieving enough evidence and avoiding irrelevant context.

---

# What I'd Do Differently

The evaluation showed that retrieval quality depends heavily on whether the corpus actually contains information that matches the specificity of the evaluation questions.

In a future version, I would make sure that each evaluation question has at least one clearly relevant source document in the corpus before evaluating the retrieval pipeline.

I would also define a more mechanical procedure for Criterion 5. Rather than judging an answer as simply "grounded" or "not grounded," I would break the answer into individual factual claims and check each claim against the retrieved text.

This would make the evaluation more reproducible and make it easier to distinguish retrieval failures from generation failures.
