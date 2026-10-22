Making the Vocal Sit: A Loudness Engineer's Guide to Vocal Placement

Little sQrt Edition — v2.0.1

Lewis Seals & Beyonce Knowles Carter 

---

Front Matter

Preface — Why "sitting in the mix" is a measurable problem, not a taste problem

Every mix engineer has heard the note. The vocal is "floating." It is "on top of the track." It "disappears in the car." The client cannot say what is wrong in numbers, and for decades the profession has treated this as a matter of taste — a conversation about feel, references, and "vibe."

It is not.

"Sitting in the mix" is a perceptual outcome with measurable causes. The vocal's relationship to the instrumental bed has a loudness ratio. The vocal's micro-dynamics have a statistical distribution. The mix's peak structure has a ceiling. These are numbers. They are not the whole of the problem — presence, timbre, and arrangement density are not loudness quantities, and no LUFS meter will tell you whether a 3 kHz lift is needed — but they are the floor. If the numbers are wrong, no amount of EQ will make the vocal sit. If the numbers are right and the vocal still feels buried, you have saved yourself a week of fader moves that were never going to work.

This book is about that floor. It is written for engineers who already know what LUFS means at the headline level, who have exported a stem before, and who are tired of guessing.

How to read this book

There are two paths.

Path one: straight through. Read Part I for the conceptual foundation, Part II for the measurement protocol, Part III for the diagnosis layer (the heart of the book), Part IV for delivery, and Part V for the assistant prompt. This is the engineer's path.

Path two: as a system prompt source. Every chapter maps to a block in the Little sQrt mix-coach gem prompt. Part V explains the mapping. If you are compiling an AI assistant rather than reading a PDF, the chapters are the rationale and the prompt is the executable distillation. Ship both, or ship the prompt alone and keep the book as the internal reference it was distilled from.

What this book is not

This is not a mastering book. It is not an EQ book. It is not a beginner's first mix. It assumes you can already make a record that sounds like music; it is about making the vocal in that record behave.

Assumed reader

You have a DAW. You have exported a stem. You know what LUFS means at the headline level — that it is a loudness unit relative to full scale, that streaming platforms normalize to targets around -14, that true peak is not the same as sample peak. You do not need to be taught what a compressor is. You need a protocol.

---

Part I — Foundations

Chapter 1 — What "sits in the mix" actually means

The phrase is perceptual. The measurement is a proxy. Confusing the two is the most common diagnostic error in vocal mixing.

"Sitting" describes a set of relationships: the vocal is intelligible without effort, it feels connected to the rhythm section rather than pasted over it, it does not spike forward on every consonant, and it does not vanish when the arrangement thickens. These are listening outcomes.

Underneath them are three measurable components and one that is not measurable by loudness analysis at all.

Component one: the vocal-to-bed loudness ratio (V/B). This is the difference between the integrated LUFS of the vocal stem and the integrated LUFS of the instrumental bed stem, both measured at the session's fader positions. It is the primary lever for placement. A V/B that is too high produces the "floating" complaint. A V/B that is too low produces the "buried" complaint. The ratio is blind to genre, arrangement, and taste until you supply those contexts.

Component two: short-term dynamics. The vocal's 3-second short-term LUFS profile — summarized by LRA and by the gap between short-term maximum and integrated loudness — tells you whether the vocal is spiky or crushed. A vocal with high LRA pokes out on syllables even when its integrated loudness is correct, because the ear tracks the peaks, not the average. A vocal with LRA far below the genre norm has no micro-dynamics to cut through the bed; it will feel detached and small regardless of fader position.

Component three: peak headroom. True-peak compliance affects what the streaming service will do to your mix after normalization. A mix that is ceiling-limited at the normalization stage will miss its loudness target, and the vocal's relationship to the bed will shift unpredictably on the platform side.

The component LUFS cannot measure: presence. Presence is the perceptual result of energy in the 2–5 kHz zone, harmonic content, transient shape, and arrangement density in the vocal's spectral range. A vocal can measure at the correct V/B and still read as buried because the bed has too much energy in the same band, or because the vocal's transients have been crushed, or because the arrangement never leaves space. Loudness analysis will not tell you which of these is true. It will tell you that the loudness is correct, which means you can stop moving the fader and start looking at the spectral and arrangement causes.

The rule: loudness proves placement, it does not prove presence. An engineer with good ears can hear that something is wrong and still misdiagnose it, because the ear reports an outcome and the meter reports a cause. Use the meter to eliminate the causes it can see, then use the ear — and the DAW — for the ones it cannot.

Chapter 2 — The four numbers that matter

Little sQrt reports many fields. Four of them carry the diagnostic weight for vocal placement.

Integrated LUFS. This is the gated average loudness over the duration of the file, measured according to ITU-R BS.1770-4. It is not "loudness" in the perceptual sense. It is a standardized, gated mean that correlates with perceived loudness well enough to serve as a placement proxy. The gating algorithm — 400 ms blocks at 75% overlap, an absolute gate at -70 LUFS, and a relative gate at -10 LU below the absolute-gated mean — is what prevents silence and low-level noise from dragging the average down. When you read measurement.integrated_lufs on a stem, you are reading the number that the rest of this protocol depends on.

Short-term LUFS. This is the loudness measured over a 3-second sliding window. Its maximum value over the file (measurement.short_term_max_lufs) tells you how loud the loudest 3-second passage is relative to the integrated average. A vocal with a short-term maximum 6 LU above its integrated is behaving well: it has peaks, but they are contained. A vocal with a short-term maximum 12 LU above its integrated is spiky; it will poke out on phrases even if the integrated ratio is correct.

LRA (Loudness Range). LRA quantifies the statistical spread of the short-term loudness distribution, from the 10th to the 95th percentile, after gating. In a vocal stem, LRA is a direct proxy for how much micro-dynamic variation the vocal retains. A heavily compressed pop vocal might read 3–7 LU. A jazz or acoustic vocal might read 10–20 LU. LRA that is too low means over-compression; too high means under-compression. The genre context is supplied in Chapter 10.

True-peak dBTP. True peak is the estimated peak of the reconstructed analog waveform, including inter-sample peaks that a sample-peak meter misses. It is measured by oversampling — typically 4× in BS.1770-4 Annex 2, and Little sQrt's --no-8x flag controls whether an 8× upsample path is used for delivery rather than measurement. The delivery ceiling is not optional: -1.0 dBTP for streaming, -2.0 dBTP for ATSC A/85, -1.0 dBTP for EBU R128. If the mix exceeds the ceiling, the normalizer will either limit it (changing the vocal's relationship to the bed) or miss the target.

The number most engineers ignore: short-term max minus integrated. This is the peak-to-average spread of the vocal stem. It is not a standard metric with a formal name, but it is the single most useful diagnostic for the "V/B is in range but the vocal still pokes" complaint. A spread above 8–10 LU suggests the vocal bus compressor is not catching phrase-level peaks. A spread below 3–4 LU suggests the vocal has been flattened and will lack cut-through.

Chapter 3 — Delivery targets and what they imply for the vocal

A delivery target is not a mastering instruction. It is a constraint on the mix. The vocal treatment that works for a -14 LUFS streaming master is not the same as the treatment that works for a -23 LUFS broadcast master, because the amount of gain reduction applied at the normalization stage changes the peak-to-loudness relationship.

Delivery Target (integrated) True-peak ceiling Implication for the vocal
Spotify / Apple / YouTube -14 LUFS -1.0 dBTP The mix can retain more peak-to-loudness ratio; the vocal can be less compressed and still hit target after normalization.
EBU R128 broadcast -23 LUFS -1.0 dBTP The mix must be much quieter on average; the vocal needs more consistent short-term dynamics to survive the larger gain reduction without pumping.
ATSC A/85 (US TV) -24 LKFS -2.0 dBTP Similar to R128 but with a stricter peak ceiling; the vocal's peak structure must be controlled before normalization.
Podcast (Apple) -16 LUFS -1.0 dBTP Mono or stereo; the voice-to-bed ratio is a special case (Chapter 9).
CD master -9 to -10 LUFS -0.3 dBTP Legacy pre-normalization target; peak-to-loudness is already low, so the vocal is likely heavily compressed.
Club / DJ -7 to -8 LUFS -0.1 dBTP Heavily limited; vocal placement is dominated by the limiter's behavior, not the fader.

The same mix can produce two different vocal outcomes at two different targets. At -14, a vocal with a short-term spread of 8 LU will normalize cleanly. At -23, the same vocal may be pushed into the limiter's ceiling, and the normalizer will trim gain, leaving the vocal quieter relative to the bed than the fader position suggested. The delivery target changes the vocal's effective placement even if the fader never moves.

The true-peak ceiling is a mix constraint, not a mastering constraint. If your mix cannot meet the ceiling without limiting that changes the vocal's dynamics, the mix is not ready for that delivery. Chapter 15 covers the fix.

Chapter 4 — Why Little sQrt, and why not something else

Little sQrt is a command-line loudness analyzer and static-gain normalizer. It measures BS.1770-4 integrated loudness, short-term loudness, LRA, and true peak. It writes a forensic JSON report with three blocks: measurement (the input signal's loudness, before normalization), render (what the tool decided to do), and verification (the output file's measured values). It does not compress, EQ, isolate stems, or automate faders. It is a measurement instrument and a gain stage, nothing more.

What it does well: BS.1770-4 accuracy, stem measurement without altering the stem, forensic JSON that separates input measurement from output verification, and no arbitrary pre-gain that would invalidate a comparison between two stems. The --no-8x flag makes the measurement path deterministic; 8× upsampling is reserved for delivery scenarios that require it, such as archival or interchange formats.

What it does not do: It does not make a vocal brighter, denser, or more present. It does not tell you whether a 3 kHz lift is needed. It does not separate a vocal from a finished mix. If the problem is spectral or arrangement-based, Little sQrt will tell you the loudness is correct and hand the problem back to your DAW. That handoff is the tool's most important feature, because an instrument that pretends to solve non-loudness problems is worse than no instrument at all.

Honest comparison: A DAW's built-in loudness meter can give you integrated LUFS and true peak, but it rarely gives you the three-block separation that lets you compare a stem's measurement against a master's verification in the same report. A dedicated analyzer plugin (VisLM, Insight, Youlean) offers real-time visualization and history, which Little sQrt does not; Little sQrt is batch-oriented and forensic. If you need to watch a meter while you mix, use a plugin. If you need to measure two stems, compare them, and produce a verifiable report, use Little sQrt.

The v2.0.1 fix. Earlier versions could produce a safety_scaled: true flag on inputs that were not actually over 0 dBFS, due to a K-weighting sign error in the measurement path. The fix corrects the sign and makes the flag trustworthy: on a normal mix, safety_scaled should never be true. If it is, treat it as a red flag and re-export the input. This is a cautionary tale about measurement trust: an analyzer is only as good as its calibration, and a sign error in a weighting filter is invisible until someone checks the numbers against a reference.

---

Part II — The Measurement Protocol

Chapter 5 — Stem export discipline

The measurement is only as valid as the export. Three stems are required.

Stem one: the vocal bus. The lead vocal after its processing chain — compression, EQ, saturation, any parallel processing — but before the master bus. Export at the session's fader position, not at unity. You want the vocal as it sits in the mix, not the raw signal.

Stem two: the bed bus. Everything that is not the lead vocal — instruments, drums, backing vocals, effects — after their bus processing but before the master bus. Export at the session's fader position.

Stem three: the pre-master mix. The full mix before the master limiter, at the session's master fader position. This is the file that will be normalized in Phase 6. It is not used in the two-stem V/B pipeline, but it is required for delivery.

The three rules. Same sample rate across all three exports. Same time range — start and end at the same bar. Same session version — do not export the vocal at 14:00 and the bed at 14:05 if any plug-in or fader changed in between. A mismatch in any of these invalidates every downstream comparison.

Common export mistakes. Exporting at unity instead of session faders (you lose the mix balance). Exporting with the master limiter engaged on the mix stem but not on the stems (the mix stem is limited, the stems are not, and the V/B is measured on an unlimited signal). Exporting the vocal with a sidechain compressor keyed by the bed (the vocal's level depends on the bed, so the stem is not a static representation). Exporting in a different bit depth without noting it (measurement is unaffected, but delivery is).

A checklist for your session notes: all three stems from the same session save; same sample rate; same start and end; faders at session positions; master limiter bypassed on stems, engaged only on the mix stem if the mix stem is the delivery render; no sidechain dependencies that change between exports.

Chapter 6 — Running the two-stem pipeline

The canonical command pair measures each stem without caring about its normalized output:

```
littlesqrt.py vox.wav /tmp/_v.wav --target -14 --no-8x --report vox.json
littlesqrt.py bed.wav /tmp/_b.wav --target -14 --no-8x --report bed.json
```

The --target value is irrelevant for stem measurement because you will read measurement.integrated_lufs, not verification.integrated_lufs. The --no-8x flag is mandatory for measurement: it keeps the path deterministic and avoids the 8× upsample that is reserved for delivery.

The one-shot Python snippet that prints vocal, bed, and V/B in one line:

```python
import json
a = json.load(open('vox.json'))['reports'][0]['measurement']
b = json.load(open('bed.json'))['reports'][0]['measurement']
print(f"vocal  {a['integrated_lufs']:7.2f} LUFS  LRA {a['lra_lu']:5.2f} LU  STmax {a['short_term_max_lufs']:6.2f}")
print(f"bed    {b['integrated_lufs']:7.2f} LUFS  LRA {b['lra_lu']:5.2f} LU  STmax {b['short_term_max_lufs']:6.2f}")
print(f"V/B    {a['integrated_lufs'] - b['integrated_lufs']:+7.2f} LU")
```

Reading the JSON. The report has three blocks per file. For stems, read measurement.*. For the final master, read verification.*. render.requested_gain_db tells you what the normalizer did; render.ceiling_limited tells you whether the true-peak ceiling blocked the full gain; render.safety_scaled should never be true on a normal file.

When --no-8x is mandatory: every measurement run, every stem comparison, every streaming or CD delivery. When it is a mistake: archival or interchange deliveries that explicitly require 8× upsampling, and some broadcast pipelines where the spec calls for it. For the vocal-placement workflow in this book, --no-8x is always the right choice.

Chapter 7 — Reading the report honestly

Three flags determine whether a report is trustworthy.

ceiling_limited: true. The true-peak ceiling blocked the normalizer from applying the full gain. You will not hit the target. The most common cause is a mix whose peak-to-loudness ratio is too high for the delivery target: the normalizer wants to add 3 dB, the ceiling only allows 1 dB, and the result is 2 LU short. The fix is in the DAW (Chapter 15), not in the normalizer.

safety_scaled: true. On v2.0.1, this should never appear on a normal mix. It indicates that the input exceeded 0 dBFS somewhere, or that a measurement-path error occurred. Treat it as a red flag: re-export and re-measure. Do not proceed with a report that contains it.

loudness_error_lu. This is the difference between verification.integrated_lufs and the target. ±0.1 LU is normal measurement noise. ±1 LU is usually inaudible on the perceptual "sitting" axis, though it matters for broadcast compliance. A value above ±0.3 LU on a streaming master almost always means ceiling_limited: true or a deliberate gain adjustment. Read it as an integrity check, not as a quality score.

What a ±0.1 LU error is: the difference between two runs of the same file on the same machine, or between two compliant meters. It is below the threshold of perceptual relevance. Why ±1 LU is usually inaudible: the just-noticeable difference for broadband loudness is around 1 LU under ideal listening conditions and larger under normal conditions. Do not chase tenths of a LU until the V/B and dynamics are in range.

The three reports that should make you stop and re-export: safety_scaled: true; a measurement.integrated_lufs that differs by more than 0.5 LU from a previous run of the same stem without a session change; a verification.loudness_error_lu above ±0.3 LU on a master that was not ceiling-limited.

Chapter 8 — Reference-track calibration

A reference track is a calibration source for integrated loudness, LRA, true peak, and short-term maximum. It is not a source for V/B, because a finished mix does not expose its vocal and bed as separate signals, and Little sQrt does not isolate stems.

The reference worksheet. Measure the reference with --no-8x and no meaningful --target (the target is a no-op for measurement). Record measurement.integrated_lufs, measurement.lra_lu, verification.true_peak_dbtp, and measurement.short_term_max_lufs. These are your numeric context targets for loudness, macro-dynamics, ceiling, and peak stress.

What a reference cannot calibrate. You cannot read a V/B ratio from a finished mix. V/B requires the vocal and the bed as separate signals. If the reference has clean exposed sections — a verse with the vocal alone, an instrumental break — you can cut two 3–5 second clips, measure each, and subtract to get a reference passage ratio (R-PR). This is not a target. It is a sanity check. If the reference reads +4 R-PR and your mix reads +7 V/B, look at why. R-PR is often unavailable; accept that the reference gives you four numbers and an ear calibration, and nothing more.

The rule: calibrate integrated, LRA, and true peak numerically against the reference. Calibrate V/B by ear. Do not pretend the reference can give you a V/B number it cannot.

Using the reference to set the initial fader. Before you measure your own mix, measure the reference's integrated LUFS and LRA. If your genre target is +3 to +6 V/B and the reference sits at a similar integrated level with a similar LRA, you can set the vocal fader to a plausible starting position based on the relationship between the reference's overall loudness and your mix's overall loudness. This is a rough calibration, not a measurement. The two-stem pipeline is the measurement.

When to abandon the reference. The client changes direction mid-project. The genre hybridizes (a pop song with a jazz vocal, a hip-hop track with a cinematic bed). The reference is mastered for a different delivery target than yours. In these cases, the reference's numbers are context, not targets, and the V/B table in Chapter 9 is your primary guide.

---

Part III — Diagnosis

Chapter 9 — The V/B ratio: targets by genre

The V/B ratio is the vocal stem's integrated LUFS minus the bed stem's integrated LUFS. Positive means the vocal is louder than the bed; negative means the bed is louder. The ranges below are practice-derived, not standards. They are starting points, and arrangement context overrides them.

Genre V/B target (LU) Typical vocal LRA (LU)
Modern pop / EDM +3 to +6 6–10
Pop-rock +2 to +4 8–14
Hip-hop / rap +2 to +5 3–7 (heavily compressed)
Singer-songwriter +2 to +4 10–20
Jazz / acoustic +1 to +3 10–20
Metal / hard rock +1 to +3 6–12
Podcast (voice + bed) +15 to +20 n/a
Cinematic / orchestral -2 to +2 Very high

Why the ranges are wide. Arrangement, arrangement, arrangement. A sparse singer-songwriter track can sit at +2 V/B and feel vocal-forward because the bed never occupies the vocal's spectral space. A dense EDM track can sit at +5 V/B and still feel like the vocal is competing, because the synth stack is doing everything it can to fill the same band. The ratio is a loudness relationship, not a spectral one.

The podcast row. The voice-to-bed ratio in spoken-word production is not the same as a musical V/B. Broadcast and podcast practice commonly places the bed 15–20 dB under the voice on the delivered file, with additional separation in the 1–4 kHz consonant zone. This is a different regime from music mixing, and the V/B table reflects it. If you are mixing voice and music for spoken-word delivery, use the podcast row; if you are mixing a song, use the genre row.

The negative V/B case. Cinematic and orchestral mixes can legitimately have a bed that is louder than the vocal, because the vocal is treated as an instrument within the arrangement rather than a foreground element. Do not apply the pop target to a cue where the voice is meant to blend.

Above-range symptoms. The vocal pokes out. It covers the instrumental. It "floats on top." The cause is usually a fader that is too high, a bed that is too quiet, or a vocal that is under-compressed (short-term peaks poking through). Below-range symptoms. The vocal is buried. It lacks presence. It sits "inside" the instruments. The cause is usually a fader that is too low, a bed that is too loud, or a vocal that is over-compressed (no transients to cut through).

Chapter 10 — Short-term dynamics: the LRA axis

LRA measures the statistical spread of short-term loudness. In a vocal stem, it is the best single proxy for how much micro-dynamic life the vocal retains.

What LRA actually measures in a vocal stem. The vocal's loudest syllables, its quieter phrases, and the distribution between them, after gating. A vocal that is compressed to a flat line will have low LRA. A vocal that is untouched will have high LRA. The genre table in Chapter 9 gives the range.

Over-compressed vocal: LRA too low. Symptoms: the vocal feels detached from the bed, it has no cut-through, it sounds "small" even when the fader is up. The cause is usually a vocal bus compressor with too much gain reduction, too fast an attack, or a low ratio applied serially. The fix is to back off the compressor, re-export, re-measure. If the delivery is streaming, over-compression is the single biggest reason a mix loses energy after platform normalization, because the platform's gain reduction has nothing to work with.

Under-compressed vocal: LRA too high. Symptoms: the vocal jumps out on loud phrases and disappears on quiet ones. It feels inconsistent. The cause is a vocal that has not been controlled at the bus level. The fix is more compression: a bus compressor with a moderate ratio (3–4:1), a medium attack (10–30 ms), and 2–4 dB of gain reduction on the loudest phrases. Re-export, re-measure.

The dynamics check that separates "correct V/B but still poking" from "wrong V/B." If V/B is in range but the vocal still pokes, compute short-term max minus integrated. If the spread is above 8–10 LU, the problem is dynamics, not placement. Compress the vocal, re-measure, and leave the fader alone.

Chapter 11 — The diagnostic decision tree

Five diagnoses cover most vocal-placement problems.

1. Vocal buried but V/B in range. The problem is spectral or arrangement-based, not loudness. Check, in order: bed arrangement density in the 2–5 kHz zone; vocal presence EQ (a 1–2 dB lift at 3 kHz often reads louder perceptually with no LUFS change); vocal LRA (below 6 LU means the transients are crushed and the vocal has nothing to cut through with); mono compatibility. Do not raise the fader. It is already right.

2. Vocal poking but V/B in range. The problem is transient shape. Check short-term max minus integrated. If the spread is above 8–10 LU, compress the vocal bus. If the spread is already tight, check presence EQ and bed density. The fader is already right.

3. Sounds fine solo, disappears in the car. Mono compatibility and mid-range masking, not loudness. Check the mono fold-down in the DAW. Little sQrt cannot help here; say so.

4. loudness_error_lu off by more than 1 LU. Almost always ceiling_limited: true. The true-peak ceiling blocked the gain. Fix the peak-to-loudness ratio in the DAW with a final limiter, re-render, re-normalize.

5. Mixed readings across stems. Phase cancellation, or an export error. Check phase in the DAW. Check that both stems were exported from the same session version at the same time range. Re-export both.

Each diagnosis has a trigger number, a DAW action, and a re-measurement requirement. The trigger is what you read in the report. The DAW action is what you do. The re-measurement is what confirms the fix.

Chapter 12 — The handoff: when the problem is not loudness

If the V/B is in range, the LRA is in range, and the vocal still feels buried, the problem is one of four things, and none of them are loudness.

Presence EQ and the 2–5 kHz masking zone. The ear's sensitivity peaks in this band. A bed with excessive energy here will mask a vocal that measures correctly. A 1–2 dB lift on the vocal at 3 kHz, or a 1–2 dB cut on the bed in the same band, often solves the problem with no LUFS change. This is a DAW decision, not a Little sQrt decision.

Transient shape. A vocal with sharp, fast transients cuts through a dense bed more easily than a vocal with rounded transients, even at the same integrated loudness. Compression changes transient shape. If the vocal is over-compressed, it will not cut through; if it is under-compressed, it will poke. The LRA check in Chapter 10 tells you which direction to move.

Arrangement density in the vocal's spectral range. If the guitar, the synth, and the snare are all occupying 2–5 kHz, the vocal has nowhere to sit. The fix is arrangement: a high-pass on the guitar, a scoop on the synth, a different snare. Loudness analysis cannot see this.

Mono compatibility. A vocal that is wide in stereo can collapse in mono if it is out of phase with the bed. Check the fold-down. If the vocal disappears in mono, the problem is phase, not level.

In all four cases, the fader is already correct and should not move. The handoff back to the DAW is the correct action.

Chapter 13 — The iterate loop

The protocol is 2–3 cycles: export, measure, adjust, export. Do not trust a mental model of "how much the fader moved." Fader moves on an isolated vocal stem are approximately 1:1 with V/B, but downstream compression, sidechain interaction with the bed, and the stem's own integrated loudness can make the relationship non-linear. Measure after every change.

When to stop. When V/B is within ±1 LU of the target range and the short-term dynamics are in the genre range. ±1 LU of V/B is inaudible on the perceptual "sitting" axis. Do not chase 0.1 LU.

The over-fix trap. Chasing a 0.3 LU error by moving the fader and re-exporting five times will destroy a working mix. The ear adapts to small changes; the meter does not. If the numbers are in range, stop measuring and start listening.

The 2–3 cycle rule. Most vocal-placement problems are solved in two cycles: one to measure and diagnose, one to adjust and confirm. A third cycle is for fine-tuning. If you are on cycle five, the problem is not loudness.

---

Part IV — Delivery

Chapter 14 — The final normalize

The canonical command:

```
littlesqrt.py mix_raw.wav mix_master.wav --target -14 --tp -1.0 --bits 24 --no-8x --report final.json
```

Stems are measured, never normalized. Only the final mix is normalized. The --target is the delivery target; the --tp is the true-peak ceiling.

The sign of requested_gain_db. A positive value means the normalizer added gain. A negative value means the mix was already louder than the target and the normalizer attenuated it. A negative gain is not a failure, but a large negative gain (more than -3 dB) suggests the mix was crushed before normalization. Consider mixing slightly quieter so the normalizer is not pulling gain off a limited signal.

When --no-8x is the wrong choice. Archival and interchange deliveries that explicitly require 8× upsampling, and some broadcast pipelines where the spec calls for it. For streaming and CD, --no-8x is correct.

Chapter 15 — Peak headroom and the ceiling-limited case

ceiling_limited: true is the most common reason a mix misses its target. The normalizer wants to add gain, the true-peak ceiling blocks it, and the output is short of the target LUFS.

The DAW fix. Add a final limiter before the normalization stage. Set the ceiling to the delivery's true-peak limit. Aim for 1–2 dB of gain reduction on the loudest peaks, with an attack of 0.1–0.3 ms and a release that suits the material. This reduces the peak-to-loudness ratio so the normalizer can apply the full gain without hitting the ceiling. Re-render, re-normalize.

Re-render discipline. Never fix a limited render by re-normalizing the limited file. The limiter has already changed the peak structure; a second normalization will either miss the target or change the vocal's relationship to the bed. Go back to the pre-limiter mix, adjust, and normalize once.

Peak-to-loudness ratio is a mix decision. The amount of peak headroom you leave is not a mastering afterthought. It determines whether the delivery target is reachable without limiting that changes the vocal. A mix with a high peak-to-loudness ratio is a mix that has not been controlled at the bus level.

Chapter 16 — Verification and A/B

Read verification.integrated_lufs, verification.true_peak_dbtp, and verification.loudness_error_lu. The acceptance thresholds: ±0.2 LU on integrated loudness, ±0.1 dBTP on true peak, ±0.3 LU on error. If any of these is outside tolerance, the master is not ready.

A/B against the reference in the same delivery format. Normalize the reference to the same target and ceiling, then compare. Do not compare a -14 master against a -9 CD master and expect the vocal to behave the same way.

The ship checklist. Integrated loudness within ±0.2 LU of target. True peak at or below the ceiling with no overs. loudness_error_lu within ±0.3 LU. ceiling_limited is false. safety_scaled is false. The vocal sits against the reference by ear. If all six are true, ship.

Chapter 17 — Delivery targets in practice

Streaming (-14 LUFS). Platforms normalize on playback, but true peak still matters because the platform's codec can introduce inter-sample peaks. A master that is compliant at -1.0 dBTP may still clip after encoding if the true peak is at the ceiling. Leave 0.2–0.3 dB of margin.

Podcast (-16 LUFS). Mono or stereo. The voice-to-bed ratio is the special case: 15–20 dB under the voice, with additional separation in the 1–4 kHz band. The podcast row in the V/B table is the guide.

Broadcast (EBU R128 -23 LUFS, ATSC A/85 -24 LKFS). Tolerance bands are tight. EBU R128 permits ±0.2 LU around -23 LUFS, with ±1.0 LU acceptable for live or short-turnaround programs. ATSC A/85 uses LKFS, which is numerically identical to LUFS. The true-peak ceiling is -1.0 dBTP for R128 and -2.0 dBTP for A/85.

CD and club. Legacy targets. CD at -9 to -10 LUFS with a -0.3 dBTP ceiling. Club at -7 to -8 LUFS with a -0.1 dBTP ceiling. These are pre-normalization targets; the vocal is likely heavily compressed, and the V/B ratio is dominated by the limiter's behavior.

---

Part V — The Gem

Chapter 18 — Building the mix-coach assistant

The book is the rationale; the gem prompt is the executable. The prompt is built from the chapters according to a compile-time contract.

The role block. Ch 1 supplies the epistemics: the assistant is a loudness coach, not a mastering engineer, and it does not make sonic decisions. The "LUFS proves placement, not presence" rule is the guardrail that keeps the assistant from over-claiming.

The tool reference block. Ch 6 and Ch 7 supply the flags, the report schema, and the three-block split. The compile check: every flag in the prompt appears in Appendix A with the same default, and every field the prompt cites appears in Appendix B.

The delivery targets and V/B tables. Ch 3 and Ch 9 supply the numbers. The podcast row must be in Ch 9, or the prompt is citing a number the book never derives.

The workflow block. Ch 5–8 and Ch 14–17 supply the seven phases. Phase 0's stem definitions match Ch 5. Phase 1's reference command reflects Ch 8's rule that a finished mix cannot give a V/B number. Phase 6's normalize command matches Ch 14.

The diagnostic block. Ch 11 supplies the five-question tree. Ch 9 and Ch 10 supply the V/B and LRA triggers. Ch 12 supplies the handoff rules. Every leaf must have a trigger number, a DAW action, and a re-measurement.

The guardrails block. Six rules, each traceable to a book paragraph: never normalize stems; never omit --no-8x for streaming; never chase sub-0.5 LU; never assume the delivery target; never defend a mix the numbers say is out of spec; never treat "make it brighter" as a loudness question.

The interaction style block. Numbers, not adjectives. Name the file, the number, and the target. Redirect sonic decisions to the DAW.

The worked example. The arithmetic must be internally consistent. If V/B is +6.7 against a +3 to +6 target, the diagnosis is "0.7 LU above the top of range," and the recommended move is 1.5 dB down to land mid-upper range. A reader will check the math; it must survive the check.

---

Appendices

Appendix A — Command reference

Flag Default Use for vocal work
--target -23.0 Delivery LUFS target; irrelevant for stem measurement.
--tp -1.0 True-peak ceiling; -1.0 streaming, -2.0 broadcast.
--hp 20.0 Input high-pass; leave at 20 for measurement consistency.
--no-8x off Always pass for measurement and streaming delivery; omit only for archival/interchange that requires 8×.
--bits 24 16 for CD, 24 broadcast, 32 float archive.
--report – JSON path; where the numbers live.

The three commands you will type most often: the two-stem measurement pair (Chapter 6), the final normalize (Chapter 14), and the reference measurement (littlesqrt.py ref.wav /tmp/_r.wav --no-8x --report ref.json). The one-liner Python snippet is in Chapter 6.

Appendix B — Report field reference

Block Field Read it when
measurement.* integrated_lufs, lra_lu, short_term_max_lufs Measuring a stem or a reference.
render.* requested_gain_db, ceiling_limited, safety_scaled Diagnosing a normalize run.
verification.* integrated_lufs, true_peak_dbtp, loudness_error_lu Verifying a master.

The four fields that indicate a broken run: safety_scaled: true; verification.loudness_error_lu above ±0.3 LU on a non-ceiling-limited master; a measurement.integrated_lufs that differs by more than 0.5 LU from a previous run without a session change; verification.true_peak_dbtp above the ceiling.

Appendix C — Tables

Delivery targets (LUFS + dBTP): the table in Chapter 3.

V/B ratio ranges by genre: the table in Chapter 9, including the podcast row.

Vocal LRA ranges by genre: the right column of the Chapter 9 table.

Acceptance thresholds: ±0.2 LU integrated, ±0.1 dBTP true peak, ±0.3 LU error.

Appendix D — Checklists

Stem export checklist: same session save; same sample rate; same start and end; faders at session positions; master limiter bypassed on stems; no sidechain dependencies that change between exports.

Measurement run checklist: both stems exported; two-stem pipeline run with --no-8x; V/B computed; LRA and short-term max recorded; report saved.

Final delivery checklist: pre-master mix exported; normalized with the correct target and ceiling; ceiling_limited false; safety_scaled false; verification within tolerance.

The four-item "should I ship?" gate: V/B in genre range; LRA in genre range; verification within tolerance; A/B against reference confirms the vocal sits.

---

Back Matter

Glossary

LUFS — Loudness Units relative to Full Scale; the unit of BS.1770 integrated loudness. LKFS — Loudness K-weighted relative to Full Scale; numerically identical to LUFS, used in ATSC A/85. LU — Loudness Unit; a relative change in loudness, equivalent to 1 dB on the LUFS scale. LRA — Loudness Range; the statistical spread of short-term loudness, from the 10th to the 95th percentile. dBTP — decibels true peak; the estimated peak of the reconstructed analog waveform. dBFS — decibels relative to full scale; sample peak. K-weighting — the frequency weighting specified in BS.1770 that approximates the ear's sensitivity. Gating — the process of excluding silence and low-level material from the integrated loudness calculation, using a 400 ms block, a -70 LUFS absolute gate, and a -10 LU relative gate. V/B — the vocal-to-bed loudness ratio.

Version note

v2.0.1 corrects a K-weighting sign error that could produce a false safety_scaled: true flag. The fix makes the flag trustworthy. The episode is a case study in measurement trust: an analyzer's output is only as good as its calibration, and a sign error in a weighting filter is invisible until the numbers are checked against a reference.

Validation status

The loudness standards referenced in this book — BS.1770-4, EBU R128, EBU Tech 3342, ATSC A/85 — are published specifications. The V/B ranges and LRA ranges are practice-derived, not standards; they are starting points that require your own reference vectors to validate. The diagnostic decision tree is engineering judgment, tested against the protocol in Part II. What is proven: the measurement math, the gating algorithm, the true-peak definition. What requires your ears: whether a vocal sits.

Further reading

ITU-R BS.1770-4 (the loudness algorithm). EBU R128 (the -23 LUFS broadcast recommendation). EBU Tech 3342 (Loudness Range). EBU Tech 3343 (practical guidelines). ATSC A/85 (US broadcast loudness).
