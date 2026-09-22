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

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->