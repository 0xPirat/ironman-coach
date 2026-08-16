# Testing, Zones & Benchmarking — Setting and Updating the Numbers

**Purpose:** The methodology file *uses* zones (FTP, LTHR, CSS, Coggan/Friel models) throughout but does not detail **how to measure and update them**. This file is the **testing manual**: field-test protocols per sport, how to derive HR/power/pace zones from results, **how often to retest per phase**, field alternatives to lab testing, VO2max estimation, how a coach **interprets a test and adjusts the plan**, and how to use **benchmark races (Olympic / 70.3)** inside an 18-month build.

> Evidence note: Field-test protocols (20-min FTP, ramp, 30-min run TT, CSS 400/200) are validated coaching-standard methods (Coggan/Allen, Friel, Ginn/Sweetenham). The %-corrections (95% of 20-min, 75% of ramp, etc.) are the published conventions. Lab lactate/VO2max testing is the gold standard but rarely available to age-groupers.

---

## 1. Why Test (and the golden rules)

- **Zones drift.** Fitness rises in build, so 8-week-old zones under-prescribe. Stale zones = junk-intensity training.
- **Test fresh, test consistently.** Same conditions each time (indoor trainer for FTP, same course/treadmill for run, same pool). Test after a recovery day, not after a hard block.
- **A test is also a session** — it's a hard workout; schedule it like one and recover after.
- **Round conservatively.** If unsure, set FTP/threshold slightly *low* — better to nail intensity targets than blow up every quality session.
- **Retest, don't guess.** Re-benchmark on a fixed cadence (see §5), not by feel.

---

## 2. Bike — FTP Testing

**FTP (Functional Threshold Power)** = highest power sustainable ~60 min; anchors all bike zones (methodology §3.2; [FasCat FTP testing](https://fascatcoaching.com/blogs/training-tips/ftp-testing/), [TrainRight — FTP tests](https://trainright.com/ftp-tests-how-to-perform-20-minute-8-minute-and-ramp-tests/)).

### 2.1 20-minute test (default for experienced riders — most valid)
- WU 15–20 min incl. 3×1 min fast/1 min easy + a 5-min hard opener, then 5 min easy.
- **20 min all-out, evenly paced** (start controlled — most riders go out too hard).
- **FTP = 0.95 × 20-min average power.** Best correlation to lab lactate threshold ([Cycling Archives](https://cyclingarchives.com/ftp-test-cycling-2026-complete-how-to-guide-coggan-friel-ramp-8-minute-protocols/)). Total session ~75 min.

### 2.2 Ramp test (best for beginners / pacing-averse)
- Step power up (e.g. +20 W/min or platform default) to exhaustion.
- **FTP ≈ 0.75 × best 1-min power.** Short (45–55 min), no pacing skill needed. **Caveat:** over-estimates FTP for riders with big anaerobic capacity; under-estimates for diesel/aerobic types. Use for first 1–2 cycles, then move to 20-min.

### 2.3 8-minute test (alternative)
- 2 × 8 min all-out, 10 min easy between; **FTP = 0.90 × average of the better (or mean) 8-min power.**

### 2.4 Deriving bike zones (Coggan, % of FTP)
| Zone | % FTP | Use |
|---|---|---|
| Z1 Active recovery | <55% | recovery spins |
| Z2 Endurance | 56–75% | long aerobic base |
| Z3 Tempo | 76–90% | durability |
| Sweet Spot | 88–94% | efficient FTP builder |
| Z4 Threshold | 91–105% | FTP intervals |
| Z5 VO2max | 106–120% | ceiling work |
| Z6 Anaerobic | >120% | rarely for IM |
- **IM race power ≈ 0.65–0.78 × FTP** (methodology §3.2; `race-day-execution-pacing.md` §2).

---

## 3. Run — Threshold / LTHR & Threshold-Pace Testing

**Friel 30-minute solo time trial** ([Joe Friel — determining your LTHR](https://joefrieltraining.com/determining-your-lthr/), [TrainingPeaks — Friel zones](https://www.trainingpeaks.com/learn/articles/joe-friel-s-quick-guide-to-setting-zones/)):

### 3.1 Protocol
- WU 10–15 min easy → **run hard, evenly, solo, 30 min** (flat course or treadmill).
- **Press lap at the 10-min mark.** Your **LTHR = average HR of the final 20 min.** (First 10 min discarded because HR lags effort.)
- **Threshold pace = average pace of the final 20 min** (or whole 30 for pace). Must be solo — a race or partner skews it.

### 3.2 Deriving run HR zones (Friel, % of LTHR)
| Zone | % LTHR | Use |
|---|---|---|
| Z1 | <85% | recovery |
| Z2 | 85–89% | aerobic endurance / long run |
| Z3 | 90–94% | tempo |
| Z4 | 95–99% | threshold (sub-LT / just under) |
| Z5a–c | 100%+ | VO2max/anaerobic |
- Prescribe tempo/threshold as **LTHR ±5 bpm** ([RunnersConnect](https://runnersconnect.net/how-to-calculate-your-lactate-threshold/)). Also set **pace zones** off threshold pace (better than HR for intervals; HR lags and drifts).
- **IM race run pace** is well below threshold — roughly Z2 / marathon effort minus fatigue (see `race-day-execution-pacing.md` §3).

---

## 4. Swim — CSS Testing

**Critical Swim Speed** ≈ swim lactate-threshold pace ([TrainingPeaks CSS](https://www.trainingpeaks.com/blog/how-to-use-critical-swim-speed-training/), [MyProCoach CSS calculator](https://www.myprocoach.net/calculators/critical-swim-speed/)):

### 4.1 Protocol (400 + 200 TT, same session)
- Thorough WU (~600–800 m incl. build 50s and a few 100s at target 400 pace).
- **400 m TT** all-out, even pace → record time.
- Full recovery (easy swim / rest several minutes).
- **200 m TT** all-out → record time.
- **CSS pace per 100 m = (400 − 200 distance) / (T400 − T200) = 200 / (T400 − T200)** → gives m/s; convert to sec/100 m. In practice: **CSS (s/100) = (T400 − T200) / 2.**
  - Example: 400 in 6:40 (400 s), 200 in 3:12 (192 s) → CSS = (400−192)/2 = **104 s/100 = 1:44/100 m.**
- 400 pace typically ~3–4 s/100 slower than 200 pace for trained swimmers ([Tri Training Harder](https://tritrainingharder.com/blog/2013/10/swim-testing-critical-swim-speed.html)).

### 4.2 Deriving swim zones (offsets from CSS)
| Zone | Offset from CSS (s/100) | Use |
|---|---|---|
| Easy/aerobic | CSS + 6–10 | technique, warm-up, long swims |
| Endurance | CSS + 3–5 | aerobic sets |
| **CSS/threshold** | CSS ± 0–2 | key threshold sets (10×100) |
| Speed | CSS − 3–5 | short fast reps |

---

## 5. Retest Cadence by Phase

| Test | Base | Build | Peak | Notes |
|---|---|---|---|---|
| FTP (bike) | every 6–8 wk | every 4–6 wk | 1× early-peak | fitness moves fastest in build |
| Run LTHR/pace | every 6–8 wk | every 6–8 wk | 1× | HR-based, stable-ish |
| CSS (swim) | every 6–8 wk | every 4–6 wk | 1× | improves fast for adult-onset swimmers |
- **Always test fresh** (after a recovery day / in a recovery week). See `weekly-structure-microcycles.md` §5.
- Don't over-test — testing every 3 weeks costs a quality session for marginal info. 6–8 weeks is the sweet spot; tighten to 4–6 in build when adaptation is rapid.
- **Auto-detected FTP** (TrainerRoad/Garmin/intervals.icu from ride data) can supplement or replace formal tests once the athlete trusts it; treat it as a check, not gospel.

---

## 6. Field Alternatives & VO2max Estimation (no lab)

- **No power meter (bike):** use the **30-min HR TT** on the bike (same as run protocol) to set bike LTHR; ride to HR + RPE. Less precise than power but workable (`race-day-execution-pacing.md` §2.2).
- **No pool pace clock:** use a **tempo trainer beeper** set to CSS.
- **VO2max estimation:** Garmin FR965 gives a **VO2max estimate** from run/ride HR-pace/power data (methodology §12) — good for *tracking trend*, not an absolute lab number. Other proxies: Cooper 12-min run test, or predicted from a recent 5k/10k race (Daniels VDOT). Treat all as directional.
- **Talk test / RPE anchoring:** Z2 = full sentences comfortably; threshold = a few words only. Useful cross-check that zones aren't mis-set.
- **Lactate meter (optional):** a finger-prick lactate meter lets an athlete map LT1/LT2 at home; advanced, but the most accurate DIY option.

---

## 7. Interpreting Tests & Adjusting the Plan

What a coach does with a result:
- **FTP up ≥3–5%:** raise zones, progress key sessions; validates the block. Watch that easy stays easy at the new higher watts.
- **FTP/threshold flat after a solid block:** check first for confounds (fatigue on test day, poor sleep, heat, under-fueling) before concluding a plateau. If genuinely flat → diagnose (see `plan-adaptation-coaching-logic.md` §7): rotate stimulus, check recovery/nutrition, possibly the athlete needs *more* easy volume or *more* specific intensity.
- **FTP/threshold DOWN:** red flag — likely accumulated fatigue, illness, under-recovery, or under-fueling (methodology §7; `recovery-sleep-rest.md` §4). Do NOT raise load; insert recovery, investigate sleep/stress/RED-S, re-test when fresh.
- **Big swim CSS jump for a beginner:** expected (technique gains) — reset zones and keep technique emphasis.
- **Zone spread sanity check:** if threshold HR and easy HR are very close, or pace zones look off, re-test — a bad test is worse than no test.

**Interpretation rule:** one test is a data point, not a verdict. Combine with PMC trend, subjective feel, and session performance before re-writing the plan.

---

## 8. Benchmark Races in an 18-Month Build

Tune-up races are **rehearsal + fitness test + motivation**, not the goal (methodology §1; `race-preparation-logistics.md` §3–§4). Recommended cadence for an ~18-month full-IM build (goal race = A race at month 18):

| When | Race | Priority | Purpose |
|---|---|---|---|
| Months 4–6 | Sprint or Olympic | C | Learn racing, transitions, open-water start; low pressure |
| Months 8–10 | Olympic | B/C | Test threshold fitness, pacing, nutrition basics |
| Months 12–14 | **70.3 (half)** | B | Key rehearsal: pacing, fueling ≥60 g carb/h, gear, mental — the most important prep race |
| ~8–12 wk before A race | Optional 70.3 or long training day | B/C | Final dress rehearsal; or replace with a Big Day (`race-preparation-logistics.md` §5) |
| Month 18 | **Full Ironman** | A | Goal race |

Rules:
- **Schedule prep races before a planned recovery week** (they're a big stimulus). Taper lightly (3–5 days) for a B race; don't full-taper and lose training rhythm.
- **The 70.3 ~4–5 months out is the linchpin** — it's the only way to rehearse >4 h of continuous racing, fueling under race stress, and pacing discipline before the full.
- **Don't over-race.** Each A/B race costs a mini-taper + recovery; 2–4 tune-ups across 18 months is plenty. Racing every month erodes the build.
- **Debrief every prep race** and feed lessons forward (`what-a-coach-actually-does.md` §5).

---

## If-Then Rules Summary

- IF setting bike zones → THEN FTP via 20-min test (FTP = 0.95×avg) for experienced riders, ramp test (FTP = 0.75×best 1-min) for beginners; derive Coggan %FTP zones.
- IF setting run zones → THEN Friel 30-min solo TT; LTHR = avg HR of final 20 min; prescribe threshold as LTHR ±5 bpm and set pace zones too.
- IF setting swim zones → THEN CSS via 400+200 TT; CSS s/100 = (T400−T200)/2; prescribe sets as CSS ± offset.
- IF choosing retest frequency → THEN every 6–8 wk in base, tighten to 4–6 wk in build (esp. FTP/CSS); once early in peak; always test fresh after a recovery day.
- IF no lab/power/pace clock → THEN use HR-TT + RPE + Garmin VO2max trend + talk test as directional proxies; consider a home lactate meter for precision.
- IF a test shows FTP/threshold UP ≥3–5% → THEN raise zones and progress key sessions; re-check that easy stays easy.
- IF a test is flat → THEN rule out fatigue/sleep/fuel/heat confounds first; if genuine, rotate stimulus and audit recovery/nutrition before adding load.
- IF a test is DOWN → THEN treat as a fatigue/illness/under-fuel red flag: insert recovery, investigate, do NOT increase load, re-test fresh.
- IF planning the 18-month build → THEN schedule ~2–4 tune-ups (Sprint/Oly early, a 70.3 ~4–5 months out as the key rehearsal), each before a recovery week, lightly tapered, and debriefed.
- IF tempted to race monthly → THEN don't; over-racing erodes the training build.

---

## Sources
- [FasCat — FTP testing (20-min field test)](https://fascatcoaching.com/blogs/training-tips/ftp-testing/) · [TrainRight (Carmichael) — FTP tests: 20-min, 8-min, ramp](https://trainright.com/ftp-tests-how-to-perform-20-minute-8-minute-and-ramp-tests/) · [Cycling Archives — FTP protocols (Coggan/Friel/ramp)](https://cyclingarchives.com/ftp-test-cycling-2026-complete-how-to-guide-coggan-friel-ramp-8-minute-protocols/)
- [Joe Friel — determining your LTHR](https://joefrieltraining.com/determining-your-lthr/) · [Joe Friel — the 30-minute test](https://joefrieltraining.com/the-30-minute-test-is-easy-really/) · [TrainingPeaks — Friel's quick guide to setting zones](https://www.trainingpeaks.com/learn/articles/joe-friel-s-quick-guide-to-setting-zones/)
- [TrainingPeaks — how to use Critical Swim Speed](https://www.trainingpeaks.com/blog/how-to-use-critical-swim-speed-training/) · [MyProCoach — CSS calculator](https://www.myprocoach.net/calculators/critical-swim-speed/) · [Tri Training Harder — CSS testing](https://tritrainingharder.com/blog/2013/10/swim-testing-critical-swim-speed.html)
- [RunnersConnect — how to calculate lactate threshold](https://runnersconnect.net/how-to-calculate-your-lactate-threshold/)
- [80/20 Endurance — planning your race season](https://www.8020endurance.com/planning-your-race-season/)

*Compiled July 2026. Field-test %-corrections are published conventions; individual physiology varies, so treat any single test as one input alongside PMC trend and subjective feel (methodology §7–§8).*
