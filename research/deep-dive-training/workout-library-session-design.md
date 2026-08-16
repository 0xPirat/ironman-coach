# Workout Library & Session Design — Concrete Session Catalog per Sport

**Purpose:** The methodology file sets zones, intensity distribution (80/20), and progression *rules* (see `ironman-training-methodology.md` §2–§3, §6). This file is the **session cookbook**: actual set structures (10×100, 3×12 min, 4×8 min, etc.) per sport, target intensities as %FTP / %LTHR / CSS-offset, how those sessions **change across base → build → peak**, how to **scale a session up or down for fatigue on the day**, and **beginner vs. intermediate variants**. Use it to generate a concrete workout, not just a zone.

> Evidence note: Interval structures and %-targets below are coaching-practice convention (TrainingPeaks, 220Triathlon, MyProCoach, Roadman, D3, FasCat) plus the sport-science on VO2max/threshold work. Zone models reference the same Coggan/Friel framework as the methodology file. Flagged where a claim is a rule-of-thumb rather than evidence.

---

## 1. Session Design Principles (apply to every sport)

1. **Every session has one job.** Aerobic/technique, threshold, or VO2max — do not blend a "hard-ish everything" soup. Blurry sessions are the #1 amateur error (see methodology §2.2).
2. **Warm-up and cool-down are not optional.** 10–20 min progressive warm-up before any quality; 5–10 min easy after. Quality-set quality collapses without it.
3. **Time-at-intensity is the currency of hard sessions.** A VO2max session is judged by minutes ≥95% VO2max (~9–15 min); a threshold session by minutes at 95–105% threshold (~20–40 min). Design backward from a target dose.
4. **Recoveries are prescriptive, not "until you feel like it."** Short recoveries (≤ interval length) keep an aerobic session aerobic; long recoveries (≥ interval length) allow higher-quality VO2max reps.
5. **Progress one variable at a time** across weeks: reps → duration → intensity → density (shorter recovery). Never two at once (methodology §3).
6. **Key sessions are protected; filler sessions are sacrificial** when time/fatigue is short (see `what-a-coach-actually-does.md` §3, `plan-adaptation-coaching-logic.md`).

---

## 2. Swim Sessions

Zones anchored on **CSS** (Critical Swim Speed = ~lactate-threshold pace; test protocol in `testing-zones-benchmarking.md` §4). Notation: "CSS" = your CSS pace per 100; "CSS+3" = 3 s/100 *slower*; "CSS−2" = 2 s/100 *faster*. For adult-onset swimmers, **technique volume dominates base** (methodology §3.3).

### 2.1 Technique / drill session (all phases, 2–3×/wk early)
- WU: 300 easy mixed (100 free / 100 back / 100 free).
- Drill main: 8–12 × 50 as [25 drill / 25 swim], 15–20 s rest. Rotate drills: catch-up, single-arm, fingertip-drag, sculling, 6-kick-switch, zipper.
- Skill: 4 × 100 pull with buoy focusing on high elbow, 20 s rest.
- CD: 100 easy. **Total ~1,500–2,000 m.**
- *Beginner variant:* more 25s, add fins for the drill portion, cut total to 1,200–1,500 m.

### 2.2 CSS / threshold session (build the race engine)
- WU: 300 easy + 4 × 50 build (25 fast/25 easy), 15 s rest + 4 × 100 as [50 drill/50 swim].
- **Main options (pick one):**
  - **10 × 100 @ CSS, 15 s rest** — the canonical CSS set ([U.S. Masters Swimming](https://www.usms.org/fitness-and-training/articles-and-videos/articles/how-to-train-with-critical-swim-speed-intervals), [MyProCoach](https://www.myprocoach.net/blog/swim-workouts-for-triathlons/)).
  - **6 × 200 @ CSS+2, 20 s rest** — longer reps, endurance bias.
  - **CSS descending ladder: 400 / 300 / 200 (@ CSS+3→CSS), 20–30 s rest**, then 5 × 100 @ CSS ([The Triathlete UK ladder](https://thetriathlete.co.uk/sessions/css-descending-ladder-swim-session/)).
  - **20 × 50 @ CSS−2, 10 s rest** — speed-at-threshold, race-pace turnover.
- CD: 200 easy. **Total ~2,400–3,000 m.**
- *Progression:* base = 8 × 100 @ CSS+2; build = 10 × 100 @ CSS; peak = 12 × 100 @ CSS with 10 s rest (density up).
- *Fatigue scale-down:* cut reps by 2–4, add 5 s rest, hold pace at CSS+3.

### 2.3 Endurance / continuous session (race-specific durability)
- WU 300, then **1 × (800–1,500) continuous @ CSS+4–6 (aerobic)**, or **3 × 500 @ CSS+3, 30 s rest**, then 300 pull. CD 200. **Total 2,500–3,500 m.**
- Build toward one swim ≥ 3,000 m continuous by peak so 3.8 km is not novel.

### 2.4 Open-water skill set (pool-simulated or in open water)
- 6–8 × 100 with **sighting every 6th stroke**; 4 × 50 "head-up Tarzan" drill; 3 × 100 **draft practice** on a partner's feet/hips; 2 × 100 **race-start surge** (fast 25, settle 75). See `race-preparation-logistics.md` §1 for open-water progression.

### 2.5 Weekly swim mix by phase
| Phase | Sessions/wk | Emphasis |
|---|---|---|
| Base | 2–3 | 60% technique/drill, 30% aerobic, 10% CSS |
| Build | 3 | 40% CSS/threshold, 30% aerobic endurance, 30% technique + OW skills |
| Peak | 2–3 | Race-pace continuous + OW skills; maintain CSS with 1 set/wk |
| Taper | 2 | Short, feel-good; 4–6 × 100 @ CSS to stay sharp, low volume |

---

## 3. Bike Sessions

Anchored on **FTP** (test in `testing-zones-benchmarking.md` §2). Coggan zones: Z1 <55%, Z2 56–75% (endurance), Z3 76–90% (tempo), **Sweet Spot 88–94%**, Z4 91–105% (threshold), Z5 106–120% (VO2max). Ironman race power ≈ 0.65–0.78 IF (methodology §3.2; execution in `race-day-execution-pacing.md` §2).

### 3.1 Z2 aerobic endurance (the bread and butter)
- **60–300 min steady @ 60–72% FTP**, cadence 85–95, low variability. This is where CTL is built.
- *Add-in for durability:* last 20–30 min at 75% FTP; or insert 3 × 8 min @ 80% mid-ride to break monotony without leaving aerobic.
- *Scale:* duration is the lever; hold %FTP, shorten by 30–60 min when fatigued.

### 3.2 Sweet Spot (best time-efficient FTP builder for time-crunched athletes)
- WU 15 min → **3 × 12 min @ 88–92% FTP, 5 min easy** → CD 10 min (~75 min total) ([TrainingPeaks Sweet Spot](https://www.trainingpeaks.com/blog/sweet-spot-interval-training-cycling/), [Triathlete one-hour SS](https://www.triathlete.com/training/workouts/one-hour-workout-sweet-spot-bike-intervals/)).
- Progressions: `2×15 @ 90%` → `3×15 @ 90%` → `2×20 @ 90%` → `3×20 @ 90%`. Total SS time 30→60 min.
- *Beginner variant:* `3 × 8 min @ 85–88%, 4 min easy`.
- *Fatigue scale-down:* drop one interval, or hold 85% instead of 90%.

### 3.3 Threshold / FTP intervals (raise the ceiling)
- WU 15 → **2–4 × 8–12 min @ 95–105% FTP, recovery = ½ interval @ Z1** → CD. Classic: **3 × 10 min @ 98–100%, 5 min easy**; or **4 × 8 min @ 100–105%, 4 min easy** ([TrainingPeaks — raise FTP](https://www.trainingpeaks.com/blog/3-workouts-to-raise-your-functional-threshold-power/)).
- Over-unders (great for IM specificity): **3 × 9 min as [2 min @ 95% / 1 min @ 105%]**, teaches clearing lactate at effort.
- *Progression:* 2×8 → 3×8 → 3×10 → 4×10 → 3×12. Target 24–40 min total at/near threshold.

### 3.4 VO2max intervals (used sparingly for age-groupers)
- WU 15 → **5 × 3 min @ 108–115% FTP, 3 min easy** (≈9–10 min near VO2max) or **4 × 4 min @ 106–120%, 4 min easy** (Norwegian 4×4) → CD ([INSCYD](https://inscyd.com/article/vo2max-intervals/), [Roadman VO2](https://roadmancycling.com/blog/cycling-vo2max-intervals)).
- 1×/wk max; ≥48 h from other hard work. More relevant to short-course; for IM, 1 short VO2 block in build is enough to lift FTP, then convert to threshold/SS.

### 3.5 Race-simulation / long bike with race efforts
- **3–6 h @ 60–70% FTP** with **race-power blocks**: e.g. after 60 min easy, **3 × 30 min @ 70–75% FTP (target IM IF)**, 10 min easy between; fuel at race rate (80–120 g carb/h — see `nutrition-deep-dive.md`). Peak version is the "Big Day" (§7 below, and `race-preparation-logistics.md` §5).

### 3.6 Weekly bike mix by phase
| Phase | Key sessions | Aerobic |
|---|---|---|
| Base | 1 Sweet Spot | 1–2 long Z2, 1 short Z2 |
| Build | 1 threshold + 1 SS or race-power long | 1 long Z2 with race blocks |
| Peak | 1 race-power long ride + brick | 1 Z2, taper volume as race nears |
| Taper | Keep 1 short opener: 3–4 × 3 min @ 90% | short easy spins |

---

## 4. Run Sessions

Highest injury risk (methodology §3.1) — progress cautiously, ≤10%/wk volume, run easy truly easy. Anchored on **LTHR** and **threshold pace** (test in `testing-zones-benchmarking.md` §3). Zones (Friel): Z1 <85% LTHR, Z2 85–89%, Z3 90–94%, Z4 (threshold) 95–99%, Z5 100%+.

### 4.1 Easy / aerobic run (majority of run volume)
- 30–75 min @ Z1–low-Z2, conversational, cadence ~170–180. If HR drifts above Z2 on flat, slow down or walk hills.

### 4.2 Long run (the key run session)
- Build 60 → 150 min progressively (~10%/wk, deload every 3–4 wk). Mostly Z2.
- *Race-specific variant (build/peak):* **last 20–40 min @ IM goal pace / low-Z3**, or "**fast finish**." For full IM, the standalone long run tops out ~2:15–2:45; extra durability comes from the brick, not endless solo long runs.

### 4.3 Tempo / threshold run
- WU 15 → **20–40 min tempo @ Z3 (marathon–half-marathon effort, ~88–92% LTHR)**; or **cruise intervals 3–4 × 8–10 min @ Z4 (95–99% LTHR), 2 min jog** → CD.
- *Progression:* 2×10 → 3×10 → 4×8 → 1×30 continuous tempo.

### 4.4 VO2max / speed (small dose, mostly base for economy)
- **5 × 3 min @ ~3k–5k effort, 2–3 min jog**; or **6–8 × 2 min hard, 2 min jog**. Keeps top-end and running economy; 1×/wk max and not the priority for IM.

### 4.5 Hill work (strength + economy, lower impact than flat speed)
- **6–10 × 45–90 s uphill @ hard-but-controlled, jog-down recovery**, 4–6% grade. Great early-season alternative to track work; lower injury risk. Or long hilly Z2 run for strength endurance.

### 4.6 Brick run (off the bike — see methodology §4)
- **Transition run** off a bike ride: base 10–20 min easy (learn legs/cadence); build 30–45 min with tempo segment; peak **60–90 min at IM goal pace** off a 4–5 h ride ([Roadman bricks](https://roadmancycling.com/blog/brick-workouts-for-ironman), [MyProCoach bricks](https://www.myprocoach.net/blog/8-best-brick-triathlon-workouts/)).
- Ratio stays low: for a 5 h ride, 60–90 min run is plenty. Don't let the brick cannibalize the standalone long run — separate them by ≥2 days.

### 4.7 Weekly run mix by phase
| Phase | Key sessions | Notes |
|---|---|---|
| Base | 1 long, 1 hill/strides, easy runs | build durability + economy |
| Build | 1 long (race-pace finish), 1 tempo/threshold, 1 brick | intensity rises |
| Peak | 1 long-ish, 1 brick @ IM pace, race-pace tempo | specificity |
| Taper | short easy + a few strides / short race-pace pickups | freshness |

---

## 5. Strength Sessions (concurrent — see methodology §5–§6)

Periodized across the season: **Anatomical Adaptation → Max Strength → Power/Conversion → Maintenance** (Friel; [TrainingPeaks AA phase](https://help.trainingpeaks.com/hc/en-us/articles/204072094-ATP-Strength-Phase-Workouts), [Enervit review](https://www.enervit.com/en/magazine/strength-training-for-endurance-sports-what-science-says)).

### 5.1 Phase templates
| Phase | Weeks | Load | Sets×reps | Goal |
|---|---|---|---|---|
| Anatomical Adaptation (AA) | 3–4 | 40–60% 1RM | 2–3 × 12–15 | tissue prep, motor control, no soreness |
| Max Strength (MS) | 6–8 | 80–90% 1RM | 3–5 × 3–6, 2–3 RIR | neural strength, economy, tendon stiffness |
| Power/Conversion | 3–4 | 40–60% explosive + plyo | 3–4 × 4–6 fast | RFD, running economy |
| Maintenance (in-season) | ongoing | ~80% 1RM | 1–2 × 4–6 | hold gains, minimal fatigue |

### 5.2 Key lifts (triathlon-relevant)
- **Bilateral:** back/front squat, deadlift/trap-bar, hip thrust.
- **Unilateral:** split squat, step-up, single-leg RDL, walking lunge (addresses run-specific asymmetry).
- **Posterior/anti-rotation core:** plank/side-plank, Pallof press, bird-dog, dead-bug.
- **Swim/shoulder prehab:** band external rotation, YTWs, scap retraction, face-pulls (see `injury-prevention-return-protocols.md` §7).
- **Calf/Achilles:** heavy slow calf raises (bent + straight knee) — prehab + economy.

### 5.3 Sample in-season maintenance session (~35–40 min)
Warm-up 5 min → Trap-bar deadlift 2×5 @ 80% → Bulgarian split squat 2×6/leg → Hip thrust 2×6 → Pallof press 2×10/side → Calf raise 2×8 → done. **Place ≥6 h (ideally next day) from key run; never the day before a key run.**

### 5.4 Scaling for fatigue
- Green day: full loads. Amber: cut to 1 set per lift, drop load 10%. Red: skip lifting, do mobility only. Never chase 1RMs on a fatigued nervous system.

---

## 6. How Coaches Vary Sessions Week to Week

- **Progressive overload within a block (3-week loading):** Wk1 introduce (e.g. 2×10 min threshold), Wk2 extend (3×10), Wk3 peak (4×10 or 3×12), Wk4 deload (2×8 easy). Then repeat at a higher baseline. See `weekly-structure-microcycles.md` §4.
- **Rotate the stimulus** to avoid plateau (`plan-adaptation-coaching-logic.md` §7): alternate SS ↔ threshold ↔ over-unders on the bike; tempo ↔ cruise-intervals ↔ hills on the run.
- **Specificity funnel:** general (SS, hills, drills) in base → race-specific (race-power long rides, IM-pace bricks, CSS continuous) in build/peak.
- **Same session, different day-state:** the plan says "threshold bike," the athlete's readiness sets the *version* (see §8).

---

## 7. The "Big Day" Race-Simulation Session (peak-phase capstone)

Structured to rehearse fuel, pacing, and gear (Friel's Big Day; [Joe Friel](https://joefrieltraining.com/ironman-big-day/)):
- Wake at race time, eat race breakfast. **Swim 60 min @ race effort** → short T1 → **Bike ~5 h @ IM power/HR** with race fuel → short T2 → **Run 30–45 min @ IM pace.**
- Schedule **~9 and ~4 weekends out**, always immediately before a rest day/recovery block. Not full distance — ~70–80% of race duration is enough and far less costly to recover from. Full detail in `race-preparation-logistics.md` §5.

---

## 8. Scaling a Session Up or Down for Fatigue (the daily decision)

Cross-reference the readiness logic in methodology §8. Given a prescribed key session:

| Readiness | Action on a QUALITY session | Action on an EASY session |
|---|---|---|
| **Green** (HRV/RHR normal, feel good) | Do as written; may add 1 rep if flying | As written |
| **Amber** (slightly off, poor sleep, mild niggle) | Reduce volume ~20–30% (drop a rep/set), hold intensity OR hold volume and drop one zone | Keep, maybe shorten |
| **Red** (HRV/RHR flagged, sick-ish, deep fatigue) | Convert to easy aerobic or rest; do NOT do quality | Easy short or rest |

Rules:
- **When cutting a hard session, prefer keeping intensity and cutting reps** (get the neuromuscular signal) rather than grinding full volume at reduced quality — unless the goal was pure durability, then do the reverse.
- **A shorter completed session beats a skipped one** (`what-a-coach-actually-does.md` §3). 20 min easy on a red-ish day maintains rhythm.
- Two amber/red days in a row on a hard-session week → insert an unplanned easy/rest day; don't force the block.

---

## 9. Beginner vs. Intermediate — Quick Differentiators

| Dimension | Beginner (yr 1 of build) | Intermediate |
|---|---|---|
| Swim | Technique-dominant, fins allowed, shorter CSS sets (8×100) | CSS/threshold volume, OW skills, 12×100 dense |
| Bike | Sweet Spot + Z2, avoid frequent VO2max | Threshold + over-unders + race-power longs |
| Run | Run-walk if needed, hills over track, lower long-run cap | Tempo/threshold, race-pace finishes, longer bricks |
| Intensity days/wk | 2 (one bike, one run) | 3 (bike, run, swim quality) |
| Long session cap | build slowly; long run ≤ 2:00 | long run ≤ 2:45, brick to IM pace |
| Strength | AA + light MS, form first | full MS → power → maintenance |

---

## If-Then Rules Summary

- IF designing any session → THEN give it ONE job (aerobic / threshold / VO2max), a warm-up/cool-down, prescribed recoveries, and a target time-at-intensity.
- IF building the bike engine time-efficiently → THEN use Sweet Spot (88–92% FTP), e.g. 3×12 min, progressing reps→duration→density.
- IF raising FTP/threshold → THEN 24–40 min total at 95–105% FTP (bike) or 95–99% LTHR (run) via 8–12 min reps; over-unders for IM specificity.
- IF prescribing VO2max → THEN 9–15 min near-max via 3–5 min reps (bike 108–120% FTP), max 1×/wk, ≥48 h from other hard work; keep it a small dose for IM.
- IF swim threshold work → THEN CSS sets like 10×100 @ CSS/15 s rest; progress base→build→peak by reps then density.
- IF long run → THEN mostly Z2, cap ~2:15–2:45, add race-pace finish in build/peak; get durability from the brick, not endless solo long runs.
- IF brick run → THEN keep run:bike ratio low (60–90 min off a 5 h ride) and separate it from the standalone long run by ≥2 days.
- IF strength → THEN periodize AA→Max→Power→Maintenance; place ≥6 h (ideally a day) from key runs; never before a key run; scale down on amber/red days.
- IF the athlete is fatigued on a quality day → THEN cut reps and keep intensity (or drop a zone), and remember a short completed session beats a skipped one.
- IF a session stops producing adaptation → THEN rotate the stimulus (SS↔threshold↔over-unders, tempo↔cruise↔hills) and check the loading/deload cadence.
- IF ~9 and ~4 weekends out → THEN run a Big Day race-simulation before a rest block (not full distance).

---

## Sources
- [U.S. Masters Swimming — CSS intervals](https://www.usms.org/fitness-and-training/articles-and-videos/articles/how-to-train-with-critical-swim-speed-intervals)
- [MyProCoach — swim workouts for triathletes](https://www.myprocoach.net/blog/swim-workouts-for-triathlons/) · [MyProCoach — 8 best brick workouts](https://www.myprocoach.net/blog/8-best-brick-triathlon-workouts/)
- [The Triathlete UK — CSS descending ladder](https://thetriathlete.co.uk/sessions/css-descending-ladder-swim-session/)
- [TrainingPeaks — Sweet Spot intervals](https://www.trainingpeaks.com/blog/sweet-spot-interval-training-cycling/) · [TrainingPeaks — 3 workouts to raise FTP](https://www.trainingpeaks.com/blog/3-workouts-to-raise-your-functional-threshold-power/) · [TrainingPeaks — ATP strength phases](https://help.trainingpeaks.com/hc/en-us/articles/204072094-ATP-Strength-Phase-Workouts)
- [Triathlete — one-hour Sweet Spot bike](https://www.triathlete.com/training/workouts/one-hour-workout-sweet-spot-bike-intervals/)
- [INSCYD — science of VO2max intervals](https://inscyd.com/article/vo2max-intervals/) · [Roadman — cycling VO2max intervals](https://roadmancycling.com/blog/cycling-vo2max-intervals) · [Roadman — brick workouts for Ironman](https://roadmancycling.com/blog/brick-workouts-for-ironman)
- [Joe Friel — Ironman Big Day](https://joefrieltraining.com/ironman-big-day/)
- [Enervit — strength training for endurance, what science says](https://www.enervit.com/en/magazine/strength-training-for-endurance-sports-what-science-says)
- [FasCat — VO2max intervals with a power meter](https://fascatcoaching.com/blogs/training-tips/vo2-max-intervals/)

*Compiled July 2026. Session structures are coaching-practice convention grounded in threshold/VO2max physiology; individualize by testing (see testing-zones-benchmarking.md) and daily readiness (methodology §8).*
