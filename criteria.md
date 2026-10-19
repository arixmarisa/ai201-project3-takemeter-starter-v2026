
# **Acceptance criteria — TakeMeter**

Five criteria that say what "working" means for this classifier, written in
unit 5 **before** anything was trained.

**All five are yours this time.** None are given. You've had two projects of
practice.

An acceptance criterion names a number. *"The model is accurate"* is an
opinion. *"Every label has an F1 of at least 0.60 on the held-out set"* is a
criterion.

Under each, write a sentence or two on **why that number**. A reason that says
something about your data or your taxonomy earns credit — *"I picked 0.60 F1
for `reaction` because it's my smallest label and I only have about 50
examples of it"*. A reason that could be attached to any project does not.

> *Missing your own targets next unit costs you nothing. Setting a target so*
> *easy you can't miss it does.*

---

## **Pick numbers you can defend**

Not numbers that sound impressive. Three labels means a coin-flip guesser gets
about 33%, so a target of 0.40 is barely a target. Your number should sit
somewhere you'd honestly call useful.

**Cover at least three of these five areas.** They're here as prompts, not as a
form to fill in — a criterion that fits none of them is fine if it names a
number.

| Area | A question it could answer |
|---|---|
| Overall accuracy | How often does it need to be right to be worth using? |
| Per-label performance | Is one label allowed to be much worse than the others? |
| Balance | How lopsided can your label counts get before it's a problem? |
| Consistency | If someone else labelled the same posts, how often should you agree? |
| Confidence | Should a confident prediction be right more often than an unsure one? |

Two things worth knowing before you pick numbers, because both will affect
whether you hit them:

- **Your smallest label will have the jumpiest score.** If a label has 50
  examples, about 8 land in the test split. An F1 computed on 8 examples moves
  a lot between seeds. A target for that label should be looser than one for
  your biggest label, and saying so is a good reason.
- **Unit 6 tests across three seeds, and the target has to hold across all
  three.** A target of 0.65 against results of 0.71, 0.62, 0.68 is a **miss**.
  Pick with that in mind — it is stricter than it first sounds.

---

## **1. Overall classification accuracy**

The model must achieve an overall accuracy of at least **0.65 (65%)** on the
held-out test set across each of the three random seeds (42, 7, and 2024).

**Why this target:**

My classifier will categorize real posts from r/college into four categories:
`academic_advice`, `college_experience`, `campus_life`, and
`financial_concerns`. Since college discussions can overlap between topics,
I believe 65% accuracy is a reasonable but meaningful target for a model
trained on approximately 250 examples.

---

## **2. Per-label F1 performance**

Each of the four labels must achieve an F1 score of at least **0.50** on the
held-out test set for each of the three random seeds.

**Why this target:**

Some college posts may mention more than one topic, such as a student discussing
financial aid while asking for academic advice. I chose an F1 target of 0.50
because these overlapping subjects can make classification difficult, especially
when each category will have approximately 50–70 examples in the dataset.

---

## **3. Dataset label balance**

No individual label may represent more than **40%** of the final dataset,
which will contain at least **200 unique posts** from r/college.

**Why this target:**

Posts asking for academic advice may be more common than posts about financial
concerns or campus activities. I want to prevent one category from dominating
the training data while still allowing the distribution to reflect the types
of discussions found in the community.

---

## **4. Human annotation agreement**

A second human annotator must independently classify at least **40 randomly
selected posts**, achieving at least **80% agreement** with my original labels.

**Why this target:**

Some posts may fit multiple categories. For example, a student discussing
problems with a roommate could be describing a personal college experience
or discussing campus life. An agreement target of 80% will help determine
whether my category definitions and labeling rules are clear enough for
another person to apply consistently.

---

## **5. High-confidence prediction accuracy**

For each random seed, predictions with a confidence score of at least **0.80**
must achieve at least **75% accuracy**, provided at least **5 test predictions**
meet that confidence threshold.

**Why this target:**

Some college posts clearly belong to one category, while others combine
multiple topics. I expect the model to be more accurate when it is highly
confident about a prediction. I chose 75% because high-confidence predictions
should be more reliable than the overall accuracy target of 65%. If fewer
than five predictions reach the threshold, I will report insufficient data
rather than claim that this criterion was met.

---

## Planned Stretch Features (+3 Points)

### 1. Four-Label Classification (+1 Point)

Train TakeMeter to classify r/college posts into four categories:

- `academic_advice`
- `college_experience`
- `campus_life`
- `financial_concerns`

Each label will have a clear definition, examples, and boundary rules.

### 2. Second Training Experiment (+1 Point)

Complete a second training run that changes exactly one
hyperparameter while keeping the dataset and evaluation
conditions the same.

Compare accuracy, macro F1, and per-label F1 between
the original and modified training runs.

### 3. Fifty Additional Minority-Label Posts (+1 Point)

First, collect and review 200 genuine posts from r/college.

Identify the label with the fewest examples in that
initial dataset.

Then collect 50 additional genuine posts specifically
belonging to that smallest category.

Document the label distribution before and after
adding the 50 examples.

**Final dataset target:** 250 unique, reviewed posts.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 6 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath, like this:

         ## 2. Every label performs acceptably

         The model performs well on all labels.

         **Why this target:** ...

         > **Revised in unit 6:** Every label has an F1 of at least 0.60 on
         > the held-out set.
         >
         > **Why revised:** "performs well" gave me nothing to check. I
         > couldn't produce a verdict from it at all.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "Overall accuracy of at least 0.65" → "at least 0.55", because
            0.65 turned out to be optimistic for 200 examples.

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.
     ───────────────────────────────────────────────────────────────────────── -->
