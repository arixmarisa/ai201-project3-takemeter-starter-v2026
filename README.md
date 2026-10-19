# TakeMeter

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, the notebook, the baseline, and troubleshooting.
>
> Once `python test.py` passes:
>
> ```bash
> head -5 data/practice_labels.csv  # the shape your labels.csv needs
> ```
>
> Then open `takemeter.ipynb` in this folder and select the project's `.venv` kernel. Run section 1 to check hardware.
>
> The notebook runs locally and writes results beside your code. No hosted-model API key is needed.
>
> **The rest of this file is your submission.**

---

<!-- ─────────────────────────────────────────────────────────────────────────

    HOW TO USE THIS FILE

    Unit 5 asks for the first five sections. Unit 6 adds the five below them.

    Everything is pasted as TEXT. No screenshots, no images.

    ⚠️ The confusion matrix especially. The notebook prints one as a markdown

    table, ready to copy. A screenshot of a matrix earns nothing. Paste the

    table.

    ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 5 — THE BUILD ═══════════════════════ -->

## **What This Does**


<!-- Your community, and what your classifier sorts posts into. Three or four

    sentences. -->

TakeMeter is a text classifier that categorizes publicly available posts from Reddit's [r/college](https://www.reddit.com/r/college/) community. It uses a fine-tuned DistilBERT model to assign one of four discussion topics: `academic_advice`, `college_experience`, `campus_life`, or `financial_concerns`. The goal is to identify the primary purpose or subject of a post, not to judge whether the post is valuable or correct. Some posts touch on multiple topics, making clear definitions and consistent annotations especially important.

---

## **Label Taxonomy**


<!-- Each label: a one-sentence definition and two real examples from your

    reading. Then your decision rule for the hardest boundary.

    The decision rule is worth a point on its own and it's the thing most

    people leave out. Every taxonomy has a hardest boundary. Name yours. -->

<!-- e.g. "If the post names a specific checkable fact, it's `analysis`, even

    if the tone is heated." -->

### `academic_advice`

**Definition:** A post primarily seeking guidance on academics, courses, grades, studying, academic policies, programs, or educational decisions.

**Example 1:** [Should I take Calc 2 in the summer?](https://www.reddit.com/r/college/comments/1x83aob/) — requests advice about scheduling a course.

**Example 2:** [Pipeline to engineering from community college as someone who needs math help](https://www.reddit.com/r/college/comments/1whqsud/) — asks which courses and preparation steps to take.

### `college_experience`

**Definition:** A post primarily sharing a college-related experience, reflection, accomplishment, or frustration without a more specific financial or campus-life focus and without principally requesting academic guidance.

**Example 1:** [Learn from my mistakes!](https://www.reddit.com/r/college/comments/1x82bdm/) — reflects on the writer's choices and college experience.

**Example 2:** [I noticed that this part of college is still the same back at HS.](https://www.reddit.com/r/college/comments/1x95d1i/) — describes an observation about university quizzes.

### `campus_life`

**Definition:** A post primarily concerning dorms, roommates, campus facilities, student organizations, friendships, social events, or day-to-day campus living.

**Example 1:** [My college roommate has been using my bed while I’m gone, what do I do?](https://www.reddit.com/r/college/comments/1x4jp2f/) — focuses on roommate boundaries.

**Example 2:** [Starting a Recreational Volleyball Club at my college](https://www.reddit.com/r/college/comments/1wh53oj/) — concerns organizing a student club.

### `financial_concerns`

**Definition:** A post primarily about paying for college or student living costs, tuition, scholarships, loans, financial aid, affordability, or personal financial pressure related to college.

**Example 1:** [How do yall afford college](https://www.reddit.com/r/college/comments/1wkdb27/) — asks how to pay for housing, meal plans, and attendance.

**Example 2:** [Accepted, but on my own for the costs.](https://www.reddit.com/r/college/comments/1wlxy59/) — requests guidance about tuition, grants, and scholarships.

### The hardest boundary

**Which two labels:** `academic_advice` and `college_experience`.

**Decision rule:** If the main purpose is to obtain guidance about academic work, course planning, grades, professors, or degree decisions, assign `academic_advice`. If the main purpose is to tell a story, share a feeling, or reflect on what happened, assign `college_experience`, even when classes or grades are mentioned. **Specific-topic priority:** If the central issue is college financing, assign `financial_concerns`; if it is roommates, social life, clubs, or campus facilities, assign `campus_life`, even when the writer also asks for advice.

---

## **The Dataset**


<!-- Where you collected from, how you labelled, your counts, and three hard

    cases. -->

<!-- Cold first? Pre-labelled with AI and corrected?

Say so plainly — the disclosure is required, not penalised. -->

<!-- Any post that made you pause: what it was, which two labels it could have

    been, and what you chose. These are worth more than the easy 190. -->

**Source:** Public submissions from r/college, with links to original threads recorded in the `note` column. Posts were collected using an archive-based Python script (`collect_college_250.py`) and assembled into one `labels.csv` with `text`, `label`, and `note` columns.

**Labeling process:** I first independently labeled 20 posts without AI suggestions and kept those original annotations separately in `college_first_20_human_labels.csv`. For the larger collection, an AI-assisted labeling workflow proposed categories; I used additional review and a label audit to refine the taxonomy assignments. The final 250-row training CSV was rebuilt from the candidate pool rather than directly combining the original 20 cold-labeled posts with 230 additional posts. Consequently, the original 20 annotations remain separately documented and should not be represented as 20 cold-labeled rows *inside the current training CSV*.

**Final training CSV:** 250 rows, with the following audited class distribution. These are the labels used for the reported eight-epoch experiments; the labels were AI-assisted and are not a substitute for an independent second-human annotation study.

| Label | Count | Share |
|---|---:|---:|
| `academic_advice` | 87 | 34.8% |
| `college_experience` | 64 | 25.6% |
| `campus_life` | 64 | 25.6% |
| `financial_concerns` | 35 | 14.0% |
| **Total** | **250** | **100%** |

No category exceeds the 40% threshold in [criteria.md](criteria.md).

### Three hard cases

**1. [Should I take Calc 2 in the summer?](https://www.reddit.com/r/college/comments/1x83aob/)**  
**Could have been:** `college_experience` or `academic_advice`.  
**I chose:** `academic_advice`, because the post asks for a recommendation about a class decision rather than primarily recounting an experience.

**2. [Learn from my mistakes!](https://www.reddit.com/r/college/comments/1x82bdm/)**  
**Could have been:** `academic_advice` or `college_experience`.  
**I chose:** `college_experience`, because the post's central structure is the author's retrospective account of personal decisions and lessons learned, not a request for guidance.

**3. [Tiny ass moldy flat - what do I do?](https://www.reddit.com/r/college/comments/1wnpoai/)**  
**Could have been:** `financial_concerns` or `campus_life`.  
**I chose:** `campus_life`, because the primary problem is the condition of a shared student residence. Rent is mentioned, but tuition or financing is not the central issue.

---

## **The Training Run**


<!-- Your starting model, your settings, and anything you changed and why. -->

<!-- epochs, learning rate, batch size, seed -->

<!-- train / val / test, and per-label counts in the test

split. If a label had fewer than about 8 in test, say so — it explains a lot

of next unit's variance. -->

**Base model:** `distilbert-base-uncased` fine-tuned for four-class text classification with the Hugging Face training pipeline in `takemeter.ipynb`.

| Setting | Initial training | Second experiment |
|---|---|---|
| Epochs | 3 | 8 |
| Learning rate | `2e-5` | `2e-5` |
| Batch size | 16 | 16 |
| Maximum token length | 128 | 128 |
| Seeds evaluated | 42, 7, 2024 | 42, 7, 2024 |
| Device | Apple Silicon GPU (MPS) | Apple Silicon GPU (MPS) |

**Reason for the change:** The initial three-epoch run often predicted one dominant category for most or all posts. I increased *only* the number of epochs, from 3 to 8, to test whether additional fine-tuning helped the classifier learn the distinctions. For this controlled comparison I kept the audited dataset and other hyperparameters unchanged. Earlier exploratory training also used an older version of the dataset and is not part of this controlled comparison.

**Split sizes:** Approximately 174 training posts, 38 validation posts, and 38 held-out test posts. Each test split contained only five examples of `financial_concerns`, so its per-seed F1 is especially unstable.

### Three-seed accuracy comparison

| Seed | 3 epochs | 8 epochs |
|---|---:|---:|
| 42 | 34.2% | 55.3% |
| 7 | 34.2% | 68.4% |
| 2024 | 36.8% | 57.9% |
| **Mean** | **35.1%** | **60.5%** |

Eight epochs improved average accuracy by approximately **25.4 percentage points**. However, only seed 7 reached the 65% accuracy target, and the model continued to struggle with `college_experience` and `financial_concerns`. Full metrics are in the saved results files. This comparison demonstrates the hyperparameter experiment, **not** fulfillment of all five acceptance criteria.

---

## **How I Used AI**


<!-- Two specific moments — what you asked, what came back, what you changed.

    ⚠️ Plus disclosure of any pre-labelling. If you had a model pre-label a

    batch and then read and corrected every one, say that. It's an allowed

    workflow and disclosing it costs you nothing. Not disclosing it is the

    problem. -->

**Moment 1 — Collecting and organizing posts**

- **What I asked for:** Help building a Python collection workflow to recover source text from public r/college posts and assemble a large candidate dataset.
- **What came back:** The `collect_college_250.py` collection workflow and CSV review files containing post text, URLs, and candidate labels.
- **What I changed or verified:** I kept my initial 20 labels separate, checked the collection outputs, and selected a final training CSV from the candidate pool.

**Moment 2 — Reviewing category definitions and label consistency**

- **What I asked for:** Suggestions to correct obvious mismatches between post content and my category definitions.
- **What came back:** A 250-row audited dataset with 67 proposed label corrections, along with a change log and uncertain cases.
- **What I changed or verified:** I used the revised dataset for retraining and evaluated the model across three seeds, comparing three and eight epochs. The resulting labels remain AI-assisted and may contain errors.

**Pre-labeling disclosure:** I assigned the first 20 labels myself before requesting AI suggestions. Subsequent labeling and audit steps used AI-generated suggestions. Some batch `APPROVED` statuses were set programmatically and should not be interpreted as independent human review of every row. The final training file does not establish human verification of all 250 examples.

---

## Planned Stretch Features — Status

These three stretch features were planned for this project. Their implementation status is recorded separately rather than assumed from dataset size alone.

| Stretch | Evidence | Status |
|---|---|---|
| **Four categories (+1)** | Four definitions and four-category training run | **Completed** |
| **Second run, one hyperparameter changed (+1)** | Three versus eight epochs on audited data; other settings held constant | **Completed** |
| **50 new examples for the thinnest original label (+1)** | Initial 200 showed `financial_concerns` smallest (28 posts), but the final 250-row file was assembled from a separate candidate selection rather than documenting 50 newly added posts in that category | **Not verified** |

The 250-row dataset meets the minimum sample-count requirement, but it would be misleading to claim the minority-label stretch bonus merely because it contains 250 rows.

---

<!-- ═══════════════════════ UNIT 6 — THE TEST ═══════════════════════

    Don't fill these in during unit 5.

    ═══════════════════════════════════════════════════════════════════ -->

---

## **Baseline vs. Trained**

<!-- Both models on the same posts. `python baseline.py --trained results.json`

    prints this table for you. -->

| Measure | Baseline | Trained | Difference |

|---|---|---|---|

| Overall accuracy |  |  |  |

| Macro F1 |  |  |  |

| F1 — `label_one` |  |  |  |

| F1 — `label_two` |  |  |  |

****What I predicted before I looked:****

<!-- Milestone 1 asks you to write this BEFORE seeing the trained numbers. A

    prediction made afterwards isn't one. -->

****What the gap actually means:****

<!-- If the baseline matched your trained model, your fine-tuning added

    nothing — and that is a real finding, not a failure. Say it plainly. -->

---

## **Run Log — Before**

<!-- Five criteria across three seeds. The notebook's section 6 prints the

    spread table; the Target and Verdict columns are yours. -->

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |

|---|---|---|---|---|---|

| 1.  |  |  |  |  |  |

| 2.  |  |  |  |  |  |

| 3.  |  |  |  |  |  |

| 4.  |  |  |  |  |  |

| 5.  |  |  |  |  |  |

### **Confusion matrix**

<!-- ⚠️ TYPED AS A MARKDOWN TABLE. The notebook prints one ready to paste.

    An image of a matrix earns nothing. -->

| true \ predicted |  |  |  |

|---|---|---|---|

| ****** |  |  |  |

| ****** |  |  |  |

| ****** |  |  |  |

****My biggest off-diagonal number, and what it means:****

<!-- Not "the model made mistakes" — WHICH boundary it didn't learn, and which

    direction. "7 real analysis posts were called hot_take and only 3 went the

    other way" is a direction, not just an error rate. -->

---

## **Verdicts and Diagnoses**

<!-- MET or MISSED against LAST UNIT's target. The target has to hold across

    all three seeds, not turn up sometimes. -->

| # | Criterion | Target | Verdict | How I decided |

|---|---|---|---|---|

| 1 |  |  |  |  |

| 2 |  |  |  |  |

| 3 |  |  |  |  |

| 4 |  |  |  |  |

| 5 |  |  |  |  |

****Diagnoses****

<!-- For each miss: the cause, and how you know. The four common causes are:

    too few examples for a label, a boundary you applied inconsistently, a

    genuinely hard label pair, and a task the model can't reach from this

    much data.

    ⚠️ Use your agreement report as evidence. It is the only instrument you

    have that can tell a LABELLING problem from a MODEL problem, and this

    section is graded on whether you used it that way. -->

---

## **Agreement Report**

<!-- Your rate against the staff set, and every disagreement adjudicated.

    Remember you labelled these 30 under the STAFF taxonomy in

    data/staff_taxonomy.md, not your own — so every argument below is made

    from those definitions and those decision rules. -->

****Agreement rate:**** **___ / 30 = ___**%

<!-- Nobody grades this number. A 60% who argues every disagreement from the

    stated rules beats a 95% who wrote "staff was right" nine times. Several

    of the 30 were chosen because they're genuinely ambiguous — you should be

    winning some of these. -->

****Disagreements****

<!-- Three lines each: the post, both labels, and who you think is right and

    why — grounded in the staff definitions you were both applying.

    Then sort each into one of three piles:

      (a) the rule covered it and I applied it loosely → a consistency problem

      (b) the rule genuinely doesn't say               → a gap in the definitions

      (c) the rule is ambiguous here and my reading is defensible → argue it.

          This is a legitimate win.

    Pile (a) is the one that matters most for your diagnosis: if you applied a

    written rule two different ways on 30 posts, that is direct evidence about

    what you did across your own 200. -->

****1.****

> **The post:**

>

> **Staff said / I said:**

>

> **My call, and why:**

>

> **Which pile:**

****2.****

> **The post:**

>

> **Staff said / I said:**

>

> **My call, and why:**

>

> **Which pile:**

****What the pattern in my disagreements tells me:****

---

## **The Improvement**

****What I changed:****

****Which diagnosis pointed at it:****

### **Run Log — After**

| Criterion | Target | Seed 42 | Seed 7 | Seed 2024 | Verdict |

|---|---|---|---|---|---|

| 1.  |  |  |  |  |  |

| 2.  |  |  |  |  |  |

| 3.  |  |  |  |  |  |

| 4.  |  |  |  |  |  |

| 5.  |  |  |  |  |  |

****Did it help, and how do I know:****

<!-- If it didn't, say so. Relabelling that didn't help is a genuinely

    interesting result and earns full credit. -->

---

## **What's Still Broken**

<!-- For each criterion still missed: what you'd do, and why you stopped. -->

**The gap between what I meant my labels to capture and what the model

learned:**

<!-- Two sentences. Your confusion matrix is the evidence. -->

<!-- ═════════════════════════════════════════════════════════════════════

    SUBMISSION CHECKLIST — unit 5

      [ ] criteria.md has five numbered criteria, each naming a NUMBER

      [ ] Each has a reason underneath tied to your data or taxonomy

      [ ] labels.csv: at least 150 rows, text/label/note, ONE file not split

      [ ] No label above 70%

      [ ] All five unit 5 sections have real content

      [ ] Label Taxonomy includes the decision rule for your hardest boundary

      [ ] The Dataset includes three hard cases

      [ ] results.json and test_split.csv committed (the notebook does this)

      [ ] At least four new commits

      [ ] Repository URL submitted — WRITE IT DOWN

    SUBMISSION CHECKLIST — unit 6

      [ ] Baseline vs. Trained table, with your prediction written beforehand

      [ ] Run Log — Before, five criteria across three seeds

      [ ] Confusion matrix TYPED AS A MARKDOWN TABLE

      [ ] A verdict on every criterion

      [ ] A diagnosis for every miss, using the agreement report as evidence

      [ ] Agreement Report with every disagreement adjudicated

      [ ] One improvement, with Run Log — After

      [ ] What's Still Broken

      [ ] results_three_seeds_before.json, results_three_seeds_after.json,

          baseline_results.json and

          agreement_results.json committed

      [ ] At least four new commits

      [ ] The SAME repository URL as last unit

    Do not delete and recreate this repository.

    ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
