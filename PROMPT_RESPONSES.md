# Prompt Engineering Techniques - Response Comparison

This document contains responses from different prompt engineering techniques applied to the question: **"What is the maximum takeoff weight of the AC4?"**

---

## 1. BASIC

**Response:**
> The maximum take-off mass of the Lightwing AC4 is 600 kg.

---

## 2. FEW-SHOT

**Response:**
> According to the manual (Section 2.7), the maximum take-off mass is 600 kg.

---

## 3. CHAIN OF THOUGHTS

**Response:**

1) The question asks for the maximum takeoff weight (maximum take-off mass) of the Lightwing AC4.

2) Searching the provided context: under "2.7 Weight limits" it states "Maximum take-off mass: 600 kg". The performance section also references takeoff with maximum takeoff mass 600 kg.

3) Reasoning: both the weight limits and performance chapters explicitly list the maximum take-off mass as 600 kg.

**Answer:** 600 kg.

---

## 4. ANTI-HALLUCINATION

**Response:**

The maximum take-off mass is 600 kg.

**Quote from the provided document:**
> "Maximum take-off mass: 600 kg"

---

## 5. TREE OF THOUGHTS

**Response:**

### Reasoning paths (Tree of Thoughts)

**Branch 1 — Direct reading**
- **Analyze:** The question asks for the maximum takeoff weight (MTOW).
- **Extract from context:** The limitations section states: "Maximum take-off mass: 600 kg".
- **Reasoning:** This is an explicit, authoritative statement of MTOW in the limitations.
- **Conclusion:** MTOW = 600 kg.

**Branch 2 — Corroboration from performance chapter**
- **Analyze:** Confirm with other parts of the document to avoid misreading.
- **Extract from context:** The performance chapter (range/endurance) says the data are valid for "Take off with maximum take of mass 600kg".
- **Reasoning:** This independently corroborates the MTOW value.
- **Conclusion:** MTOW = 600 kg.

**Branch 3 — Infer from other weight figures (rejected)**
- **Analyze:** Could try to compute MTOW from empty mass + fuel + baggage + occupants.
- **Extract from context:** "Maximum permissible operational empty mass 405 kg", "Maximum loading aft baggage compartment: 25 kg", fuel tank 90 liters usable (but no occupant/payload specifics).
- **Reasoning:** Insufficient data (no occupant/payload or usable fuel mass conversion given) to reliably compute MTOW; doing so would require assumptions and risk error.
- **Conclusion:** Discard — not supported by explicit data.

### Evaluation and selection
Branch 1 is direct and supported by Branch 2. Branch 3 lacks required data and is discarded.

### Final answer (quoted):
> "Maximum take-off mass: 600 kg" (Lightwing AC4 Limitations, Page 16).

Therefore, the maximum takeoff weight of the AC4 is **600 kg**.

---

## 6. SELF-CONSISTENCY

**Response:**

### Chain 1
1. The "Lightwing AC4 Limitations" section (2.7 Weight limits) lists "Maximum take-off mass: 600 kg."
2. Therefore the maximum takeoff weight is 600 kg.

### Chain 2
1. The "Performance" section (5.3.2 Range and endurance) states the range/endurance data are valid for "Take off with maximum take of mass 600kg."
2. Therefore the maximum takeoff weight is 600 kg.

### Chain 3
1. The weight limits section also gives related mass limits (e.g., "Maximum permissible operational empty mass 405 kg") and defines the datum and CG limits around a stated maximum take-off mass.
2. The only stated maximum take-off mass in the document is 600 kg.
3. Therefore the maximum takeoff weight is 600 kg.

### Comparison and answer
All three chains independently conclude the same value. The maximum takeoff weight (mass) of the AC4 is **600 kg**.

---

## 7. REACT

**Response:**

**Thought:** Find the maximum takeoff weight in the provided AC4 documentation.

**Action:** Search context for "Maximum take-off mass" / weight limits.

**Observation:** The document states "Maximum take-off mass: 600 kg" (also referenced elsewhere as "Take off with maximum take of mass 600kg").

**Final Answer:** 600 kg

---

## 8. LEAST TO MOST

**Response:**

### Step 1 — Break into sub-questions
1. Where are the aircraft weight limits stated in the provided context?
2. What value is given for the maximum take-off mass/weight?
3. Is that value referenced elsewhere in the document?

### Step 2 — Answers using only the context
1. The weight limits are given under "2.7 Weight limits" in the Lightwing AC4 Limitations section.
2. The context states: "Maximum take-off mass: 600 kg."
3. Yes — the Performance section (5.3.2 Range and endurance) also refers to "Take off with maximum take of mass 600kg."

### Final answer
The maximum takeoff weight (maximum take-off mass) of the AC4 is **600 kg**.
