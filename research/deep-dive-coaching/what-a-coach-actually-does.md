# What a Coach Actually Does — The Practice (Not the Science) of Coaching

**Purpose:** The companion file `ironman-training-methodology.md` covers the *exercise science*. This file covers the *craft*: the human, process, and relationship work a paid endurance coach actually performs. For an AI coach to be a credible replacement, it must replicate not just plan-writing but onboarding, communication rhythm, judgment under real-life disruption, and the "reading the athlete" that coaches consider the core of their job.

> Evidence note: This is a **practice-consensus** domain, not an RCT domain. Almost none of the below is backed by controlled trials — it reflects what established coaches and coaching platforms publicly describe doing. Treat it as "how the industry works," and flag it that way to the athlete rather than dressing it up as proven science.

---

## 1. Onboarding & Initial Assessment

Real coaches do **not** start by writing workouts. They start by understanding the athlete and the life the training must fit into. The onboarding sequence is remarkably consistent across services.

### 1.1 The typical sequence

| Step | What happens | Typical timing |
|---|---|---|
| **Application / inquiry** | Short form: goals, race(s), history, budget | Day 0 |
| **Free intro call** (~20–30 min) | "Discovery" conversation — is this a fit? Coaching style vs athlete need | Within days |
| **Onboarding questionnaire** | Detailed intake (see §1.2) | On signup |
| **Platform setup** | Athlete added to TrainingPeaks / app; device (Garmin) connected; zones entered | Week 1 |
| **Baseline testing** | Field tests (FTP / CSS / threshold run), sometimes lab lactate or gait analysis | Week 1–2 |
| **First plan + kickoff call** | Season skeleton delivered and explained | End of week 1–2 |

The full process typically takes **1–2 weeks** depending on athlete responsiveness ([Scientific Triathlon Coaching](https://scientifictriathlon.com/coaching/), [Sound Training and Racing](https://soundtrainingandracing.com/coaching/triathlon/)).

### 1.2 What the intake questionnaire actually asks

Good intake goes far beyond training history. It captures the **whole athlete** because "life stress is training stress" (see the existing methodology file, §7). A comprehensive intake covers:

- **Athletic background:** years in sport, previous races + times, biggest strengths, biggest limiters, injury history (this is critical and often under-asked).
- **Current fitness:** recent training volume, current weekly hours, benchmark efforts.
- **Goals:** the A-race, secondary goals, *why* — the emotional driver ("finish before my father's birthday", "prove I can").
- **Life constraints:** job hours and flexibility, commute, family/childcare, travel schedule, typical sleep, realistic weekly training-hours ceiling, which days are hard/easy to train.
- **Health:** medical conditions, medications, current niggles, nutrition patterns, menstrual history (for female athletes — relevant to RED-S, see nutrition file).
- **Equipment & environment:** bike, power meter, pool access, gym access, indoor trainer, wearable (here: Garmin FR965).
- **Preferences:** communication style wanted (hand-holding vs independent), how they respond to pressure.

Coaches emphasize understanding "the person behind the training" — work schedule, family commitments, and the realities that influence consistency ([Scientific Triathlon](https://scientifictriathlon.com/coaching/), [t3 Triathlon FAQ](https://www.t3-triathlon.com/faq-2/)).

### 1.3 Baseline testing coaches use

- **Field tests** (most common, no lab needed): 20-min FTP or ramp test (bike), 400 m + 200 m CSS test (swim), threshold run test (e.g., 30-min TT) — these set the zones that drive everything (see methodology §3).
- **Lab testing** (higher-end / performance-focused coaches): blood lactate step tests to set precise zones and track fat-oxidation; some do VO₂max ([Alan Couzens](https://www.alancouzens.com/), [lactate.com protocols](https://lactate.com/triathlon/lactate_triathlon_protocols.html)).
- **Movement / gait screening:** running gait analysis, functional movement screens to find mechanical limiters and injury risk ([Scientific Triathlon](https://scientifictriathlon.com/coaching/), [The Empowered Athlete — off-season testing](https://triathlontraining-coach.com/testing-and-assessment-in-the-off-season/)).

**AI-coach implication:** the app should run a structured multi-domain intake wizard, store it as a living athlete profile, and re-surface it (especially injury history and life constraints) whenever it makes decisions — not just at signup.

---

## 2. Communication Cadence — The Rhythm of Coaching

The single biggest thing athletes pay for beyond the plan is **responsive, individualized communication**. A generic plan is cheap; a coach who answers "I feel terrible today, what do I do?" is not.

### 2.1 Standard cadence

| Channel | Frequency | Content |
|---|---|---|
| **Daily** | Per-session | Written feedback/comments on key workouts (e.g., via TrainingPeaks comments), data review |
| **Weekly** | Once | Check-in: review the week, adjust the next week, athlete self-report (see workflow file for question templates) |
| **Monthly / block** | Per mesocycle | Bigger-picture call: is the block working? re-test results, re-plan |
| **Ad hoc** | As needed | Text/email/app messages when life happens; how fast the coach replies is a headline selling point |
| **Race week** | Elevated | Detailed pacing/nutrition/logistics plan; reassurance; final adjustments |

Coaching packages are explicitly differentiated by **communication frequency and channel** — this is often what separates a $200/mo tier from a $400/mo tier ([TriDot pricing](https://www.tridot.com/pricing), [BuildPeakCompete packages](https://member.buildpeakcompete.com/coaching-packages/)). Athletes and coaches both stress that **matching communication style** (quick texts vs weekly calls vs detailed written feedback) is central to a good relationship — some athletes want frequent reassurance, others want to be left alone ([BetterTriathlete](https://bettertriathlete.com/coaching/questions-to-ask/), [SportCoaching](https://sportcoaching.com.au/what-questions-to-ask-a-triathlon-coach/)).

### 2.2 How plans are delivered

- Plans live in a **platform** (TrainingPeaks is the industry default) — athlete sees the week ahead, each workout has a structured description, target zones, and a "why."
- Good coaches **explain the purpose** of each session, not just the numbers — TriDot, for instance, ships written + video rationale for why a workout exists and how it fits the block ([TriDot for coaches](https://www.tridot.com/coaches/tridot-for-coaches)).
- Plans are usually delivered **1–3 weeks at a time**, not the whole season at once, so they can flex to real-life feedback.

**AI-coach implication:** deliver the plan a rolling 1–2 weeks ahead, always attach a plain-language "why this session," and provide a fast conversational channel for "life happened" messages. Offer a configurable communication personality (more/less hand-holding).

---

## 3. How Coaches Actually Adjust Plans (Concrete Decision Patterns)

"Reduce load" is the science answer. Coaches operate on **specific, repeatable heuristics**. The governing principle: **something is always better than nothing, a shorter workout beats a missed one, and you never "make up" missed sessions by stacking them** ([Triathlete — adapt when things go wrong](https://www.triathlete.com/training/how-to-adapt-your-training-when-things-go-wrong/), [TriForce Team](https://www.triforceteam.com/2020/08/how-and-when-to-adjust-your-plan/)).

### 3.1 Missed session(s) / a bad day

- **Missed one session:** let it go. Do NOT double up tomorrow. Prioritize keeping the *next* key session intact.
- **When forced to cut, protect the key sessions** (long ride, long run, key interval set); sacrifice the easy/filler aerobic sessions first.
- **Rearrange, don't cram:** shuffle the week so the key stressors still land with adequate spacing.

### 3.2 A disrupted week (travel, work crunch, family)

- **Rearrange weeks, not days.** If a whole week is compromised, **re-designate it as the recovery week** and pull a load week forward/back. This turns a problem into planned periodization ([Triathlete](https://www.triathlete.com/training/how-to-adapt-your-training-when-things-go-wrong/)).
- **Travel:** substitute what's available (hotel-gym bike, run off the door, bodyweight strength); prioritize frequency over duration to hold motor patterns; accept lower volume.
- **Build "contingency" slack in from the start** — good plans assume ~1 in 4 weeks will be partly disrupted.

### 3.3 Illness — the "neck check" + day-count decision

- **Neck check:** symptoms **above the neck** (runny nose, sore throat, no fever) → easy training usually OK; symptoms **below the neck** (chest, body aches) or **fever** → NO training ([Triathlete — dealing with illness](https://www.triathlete.com/training/the-triathletes-guide-to-dealing-with-illness/)).
- **Return-to-training by days missed** ([Race Smart — bouncing back](https://www.racesmart.com/article/bouncing-back-illness/), [AsiaTRI](https://www.asiatri.com/2021/02/how-to-restart-training-after-illness-or-missed-workouts/)):
  - **2–5 days out:** fitness essentially unchanged; ease back, maybe reschedule a key session; no panic.
  - **6–14 days out:** step the progression **back 1–2 weeks** before the illness; rebuild.
  - **When resuming:** take interval sessions **down a zone** and make the recovery portions **more active** — you get the theme of the session without the full stress.

### 3.4 Life stress (the invisible load)

- Coaches treat psychological stress as **physiological load** — "your body can't tell the difference between a work deadline and a hard interval session" ([Triathlete](https://www.triathlete.com/training/how-to-adapt-your-training-when-things-go-wrong/)).
- Practical response: when life stress spikes, **cut intensity first** (the polarized "easy" volume is more restorative and less risky than pushing quality on a frazzled nervous system), and lower expectations for the block rather than forcing it.

**AI-coach implication:** encode these as explicit branch logic (missed-session → protect key; whole week gone → convert to recovery week; illness → neck-check + day-count rewind; life-stress spike → cut intensity, not necessarily volume). This is arguably the highest-value coaching behavior to automate well.

---

## 4. What's Actually in Paid Coaching Packages (Market Survey)

What athletes get for their money, by service archetype:

| Service / model | Rough price | What's included | Notable positioning |
|---|---|---|---|
| **Boutique 1:1 on TrainingPeaks** (individual coach) | ~$150–$400/mo | Premium TP account, fully custom plan, daily workout feedback, weekly check-ins, power/HR/pace analysis, ad-hoc messaging | Most personal; quality varies by coach |
| **Purplepatch Fitness** (Matt Dixon) | Squad + 1:1 tiers | Time-starved-athlete philosophy: ~10 h/wk focus, strength + recovery + nutrition emphasis, holistic "life-first" framing, squad community | "Performance is performance"; not high-volume ([Purplepatch methodology](https://www.purplepatchfitness.com/our-methodology), [Precision — Dixon on integrating life](https://www.precisionhydration.com/performance-advice/interview/matt-dixon-integrate-sports-training-with-family-and-work/)) |
| **TriDot** (AI + optional coach) | Software from ~$15/mo; coach tiers **$199–$399/mo** | AI-optimized plan accounting for weather/environment/"DNA"; optional human coach for messaging/calls | Data-driven; some athletes report it feels less personalized ([TriDot pricing](https://www.tridot.com/pricing), [Triathlete AI apps review](https://www.triathlete.com/gear/tech-wearables/ai-triathlon-training-apps/)) |
| **80/20 Endurance** (Fitzgerald/House) | Plans cheap; coaching higher | Polarized-intensity plans, strong educational content, structured workouts | Strict intensity-distribution discipline |
| **Ironguides "The Method"** | Squad/plan/1:1 | System-based training "recipes," adaptable globally | Method-driven ([Ironguides on TP](https://www.trainingpeaks.com/coach/ironguides)) |
| **TrainingPeaks platform itself** | Coach edition from ~$22/mo + ~$9/athlete/mo | The delivery rails coaches use — *not* coaching itself | Platform, not coach ([TP coach pricing](https://www.trainingpeaks.com/pricing/for-coaches/)) |

**Common thread:** across all tiers, the paid deliverables are (1) an individualized plan, (2) ongoing analysis/feedback of your data, (3) responsive communication, (4) accountability, and (5) race-specific strategy. The differentiators between price tiers are almost always **communication frequency + degree of personalization**, not the workouts themselves ([BuildPeakCompete](https://member.buildpeakcompete.com/coaching-packages/), [TriDot pricing](https://www.tridot.com/pricing)).

**AI-coach implication:** the app can natively deliver (1), (2), and (5) at the top-tier level, and (4) via nudges. Its unique advantage is *unlimited responsive communication* at zero marginal cost — the thing human coaches ration by price.

---

## 5. Post-Race Debrief

A structured debrief is standard coaching practice and a genuine performance lever — how an athlete interprets an outcome shapes the next block.

### 5.1 Timing & method

- **Write it down within a few days**, while details are fresh but after the emotional high/low has settled enough for objectivity ([NYX Endurance](https://nyxendurance.com/the-power-of-reflection-why-writing-a-post-race-recap-is-essential-for-every-triathlete/), [TrainingPeaks — debrief](https://www.trainingpeaks.com/coach-blog/how-to-properly-debrief-after-a-race/)).
- Structure it **discipline by discipline** (swim / T1 / bike / T2 / run / nutrition / mental), plus overall.

### 5.2 The core questions

- **What went well?** (Coaches stress leading with this — reinforce and *reward* what worked; acknowledge good execution, not just fitness) ([TrainingPeaks](https://www.trainingpeaks.com/coach-blog/how-to-properly-debrief-after-a-race/), [MyProCoach post-race analysis](https://support.myprocoach.net/hc/en-us/articles/360022748952-Triathlon-Post-Race-Analysis)).
- **What 1–2 things would I do differently next time?**
- **What gear or nutrition needs testing in training?**
- **Which pacing / mental strategies worked, and which failed?**
- **How well did I express my fitness?** (Separate "was I fit enough" from "did I race well" — different fixes.)

### 5.3 Turning it into action

The debrief's output is a **short list of specific training/testing changes** for the next block — that's the point. It also feeds the mental side: framing a hard race as *feedback, not failure* (see mental file, §4).

**AI-coach implication:** trigger a guided debrief 2–4 days post-race, store answers, and explicitly carry the "differently next time" items into the next block's plan.

---

## 6. Red Flags Coaches Watch For (Beyond HRV/Pace)

The methodology file covers the *numbers* (HRV, RHR, TSB). Experienced coaches also read **language, mood, and life cues** — often the earliest warning of overtraining, illness, burnout, or under-fueling. These come from check-in text and conversation, not the watch.

Watch for:

- **Language shifts:** workouts described as "flat," "heavy," "just going through the motions," "can't be bothered"; loss of the usual enthusiasm in messages; shorter/curter replies than normal.
- **Motivation loss / dread** — reluctance to train, especially for previously-loved sessions, is a classic overreaching/burnout sign (see recovery file §4; [overtraining psychology / POMS research](https://econtent.hogrefe.com/doi/10.1024/2674-0052/a000072)).
- **Irritability, low mood, emotional flatness** — mood disturbance rises with excessive load and reverts with recovery (POMS literature).
- **Sleep complaints** despite fatigue; "tired but wired."
- **Life-stress cues:** mentions of work crunch, relationship strain, poor eating, skipped meals, travel — coaches proactively ask about these.
- **Body-image / food language** — restriction talk, "trying to lean out," skipping fuel on long sessions → RED-S risk (see nutrition file).
- **Recurrent minor illness / niggles** — a body under too much total load.
- **Obsessive/compulsive training** — inability to take a rest day, guilt about missed sessions.

The coach's move is usually to **ask an open question** ("How's life outside training? How are you sleeping? How did that session *feel*, not just the numbers?") and then adjust — often pulling back before the data confirms a problem.

**AI-coach implication:** the app should (a) run lightweight daily/weekly subjective check-ins with free-text, (b) do sentiment/keyword flagging on athlete messages, (c) proactively ask about sleep, life stress, mood, and fueling, and (d) weight these subjective signals alongside Garmin data — mirroring how coaches trust "how are you?" as much as the HRV chart. This is the "soft" coaching that pure-data apps miss.

---

## 7. Practitioner Craft Insights (from expert podcasts/videos)

The transcripts in [`youtube-transcripts/`](youtube-transcripts/) put working coaches' own words behind this file's practice-consensus claims.

**Communication and RPE are the core of coaching (backs §2, §6).** Mikael Eriksson treats RPE as a central training metric *because it is the athlete's own communication* — effective coaching depends on constant athlete communication and good workout comments that capture both how hard a session felt and how the athlete performed relative to expectation. He warns against over-specificity (race pace is a % of threshold, which is a % of VO₂max — develop the underlying qualities rather than always training race-specific) and against racing too frequently, which can trap athletes in a single stimulus ([Eriksson — getting faster](youtube-transcripts/human-endurance-mikael-eriksson-getting-faster.md)). Skiba puts the accountability sharply: coaching is "99% good coaching and communication," and if the athlete executes the plan but doesn't improve, that's the *coach's* fault, not the athlete's ([Skiba](youtube-transcripts/scientific-triathlon-skiba-endurance-training-science.md)).

**Matt Dixon's operating system for time-crunched athletes (extends §3, §4).** Deep detail behind the §4 Purplepatch row:
- **Total weekly hours is not the barometer** — his age-group World Champs qualifiers average ~10–12 h/week, but that's the optimal dose *within their life context*, not proof less is better (his pros trained 18–30 h). Dumping a fixed hour target on top of a stressful life wrecks sleep, fueling, and recovery ([Dixon — training loads & non-negotiables](youtube-transcripts/trainingpeaks-matt-dixon-training-loads-non-negotiables.md)).
- **Key sessions vs filler** (a concrete version of §3.1's "protect the key sessions"): each week has only 1–3 sessions that move the performance needle — protect those; everything else is flexible "packing filler" you can scale or move. Don't treat weeks as pass/fail; when life disrupts a key session, *move* it and swap in a "soul-filling" easy session rather than cramming a make-up — exactly §3.1–§3.2's logic.
- **The "Sunday Special" habit** (a planning tool the app could implement): before each week, spend ≤20–30 min laying out life commitments first, then work, then fitting training into what's left — planning all three as one system, and communicating it to your partner.
- **Non-negotiables before gadgets:** master ~7 simple habits (year-round strength, prioritized sleep, fuel after every workout, genuinely easy easy days, daily hydration) — "95% of the way to success"; ice baths/supplements/boots only on top of that foundation.
- **Metrics are a "heads-up display," the athlete flies the plane** — start each day by checking in with the "inner animal" (how do I feel?) before consulting sleep/readiness data. He's cautious about AI *prescribing* training and about isolating "specificity" work that strips away the team, community, and fun that drive adherence — a useful caution for an AI-coach product ([Dixon](youtube-transcripts/trainingpeaks-matt-dixon-training-loads-non-negotiables.md)).

---

## Coaching-Practice Rules Summary (If-Then)

- IF onboarding an athlete → THEN run a full multi-domain intake (history, goals-and-*why*, life constraints, injury history, health, equipment, comms preference) before writing any workout; set baselines via field tests (FTP/CSS/threshold) ± gait screen.
- IF delivering plans → THEN roll out 1–2 weeks at a time, always with a plain-language "why," via a platform the athlete checks daily.
- IF a single session is missed → THEN drop it, protect the next key session, never double up.
- IF a whole week is disrupted → THEN convert it to the recovery week and reshuffle the block.
- IF the athlete is ill → THEN neck-check (above = easy OK, below/fever = rest); on return, rewind the progression 1–2 weeks if >5 days lost, and take intervals down a zone.
- IF life stress spikes → THEN cut intensity first and lower block expectations.
- IF after a race → THEN run a guided debrief (lead with what went well; extract 1–2 concrete changes) and feed it into the next block.
- IF reading the athlete → THEN watch language/mood/motivation/sleep/food cues as leading indicators; ask open questions and pull back before the data confirms trouble.
- IF setting price/positioning expectations → THEN remember the paid differentiators are communication frequency + personalization, which an AI coach can offer without rationing.

*Compiled July 2026. This file is practice-consensus, not RCT evidence; sources are coaching services, platforms, and coach interviews. Present these behaviors to the athlete as "how good coaches work," and individualize.*
