# Competitor teardown: His Story (@HisYTStory)

Data pulled from vidIQ on 2026-10-23. The video analysis comes from 3 downloaded Shorts: "I'm Happy My Dad Lied 🏠" (66s), "He Tapped Back 💔" (112s) and "I Couldn't Afford A Football 😢" (101s). I sampled frames at 10fps, OCR'd every caption, measured audio levels and pauses, and pitch-tracked the narrator.

## 1. The channel in numbers
| Metric | Value |
|---|---|
| Subscribers | **7.36M** (+3.03M in the last 90 days) |
| Total views | **11.49B** (+5.6B in 90 days ≈ 62M views/day) |
| Uploads | 1,946 total, **~8 Shorts per day, one every ~3 hours** |
| Created | Jan 2022, US, faceless, Entertainment |
| Typical Short | 1:15–2:30 long, recent uploads 0.5–10M views in 24h |
| Top Shorts | He Tapped Back 85M · Her Teacher Gave Her An F For Being Right 48M · Don't Go In There 46M · Grandma's Recipe 43M · I Couldn't Afford A Football 39M |

**Sister / copycat channels** (vidIQ "similar"): **Her Story** (3.49M subs, +18.7% subs in 30 days, the same formula with a female narrator), Bliss Bits (3.84M), Here's My Story, Funovesity. The format is proven and still growing fast.

## 2. Story formula (from all three transcripts)
1. **Second 0, no intro.** The first sentence drops you into a specific, emotional situation:
   - "I handed my son a ball of garbage on his ninth birthday."
   - "My twin brother Chris and I were 9 when we learned Morse code."
   - "Every weekend morning since I was five, Dad would wake me up at 6AM…"
2. **A motif is planted in the first 5 seconds** (the garbage ball, the tapping, the house). It has to come back at the end.
3. **Conflict / doubters:** a nurse ("they're reflexes"), Mom ("you're talking to a corpse"), the narrator's own resentment ("I hated every second").
4. **Time jumps keep it moving:** "A week later…", "For the next two years…", "Four months in…", "Then I turned 18…".
5. **Escalation to a crisis:** organ donation, the World Cup, finishing the house.
6. **The twist / payoff uses the motif:** SOS tapped back; he juggles the garbage ball at the World Cup; "there was never any client".
7. **The last line is a quiet emotional callback, with no CTA**, no "follow for more" and no question. The end lands, then the video loops.
8. **Dialogue makes up about 30–40% of the script**, always in short quoted lines.
9. **Plain words at about a 3rd-grade level.** Short sentences, concrete numbers ("fifty times", "eighty thousand strangers", "two bus tickets").

**Titles:** 3–7 words, first person or "He/She…", plus **one emoji** at the end. They hint at the story without spoiling it: "He Tapped Back 💔", "I'm Happy My Dad Lied 🏠", "I Labeled It FISH 🐟".

## 3. Voice and audio (measured)
| | Dad Lied | Tapped Back | Football |
|---|---|---|---|
| Narrator pitch (median F0) | 112 Hz | 110 Hz | 109 Hz |
| Pitch range p10–p90 | 91–136 Hz | 88–137 Hz | 90–131 Hz |
| Speaking rate | ~160 wpm | ~170 wpm | ~165 wpm |
| Longest pause in the whole video | 0.11s | 0.12s | 0.09s |

- **It's the same narrator in every video**: an adult male, low-mid baritone (~110 Hz), calm, warm and restrained. He uses the same voice even when the "I" is a kid or a dad, and the narrow pitch range shows he never shouts.
- **Pauses are cut to almost nothing.** Between words the gaps are 20–60ms, the longest is about 0.1s, and breaths are removed. This "wall of voice" is the main retention trick.
- **Mix:** the voice sits at about -16 dB mean and peaks around 0 dB. Under it is a very quiet tonal music bed (sustained notes are visible in the spectrogram at ~200/577 Hz), plus only occasional SFX. Voice is about 90% of the mix.

## 4. Visual style (frame by frame)
- **3D CG animation** that looks like Unreal Engine / iClone: semi-realistic characters with stylised faces, big expressive eyes and photoreal environments (slums, hospitals, construction sites, stadiums).
- **Recurring mascot:** a boy with curly orange hair, heterochromia (one blue eye, one green), a white tee with a small "his" logo in orange/white/green, and green track pants with a yellow stripe. He plays the narrator in many stories, and the logo also shows up on other characters' shirts as product placement.
- **Camera:**
  - wide-angle and fisheye lenses
  - lots of low "hero" angles and extreme close-ups of faces and hands
  - POV shots (the narrator's own hands handing over the ball)
  - constant slow push-ins and handheld drift; it is never static
  - motion blur on fast moves
- **Shot length:** a new shot about every 1.5–3s. They are mostly camera moves rather than hard cuts (a scene-detect at 0.25 only finds 9–11 hard cuts per video), so it feels continuous but never still.
- **Lip-sync / acting:** characters gesture and react to the line being spoken (hand to chest on "you're", a pointed finger on "donating").
- **Captions:**
  - white bold rounded sans (similar to Inter / SF Pro Bold) with a thin dark outline and shadow, sentence case
  - **1–3 words at a time**, swapped every ~0.3–0.5s, centred at **~74% of screen height** (in the lower body area, away from faces)
  - no colour highlight and no pop animation; quotes are kept in the captions
  - the font is small, about 4% of frame height
- **Hook frame (0.0s):** a close-up of a character with an emotion already on their face, and the first caption on screen from frame 1.
- **Format:** 720×1280, 30fps, h264 at ~1.1–1.9 Mbps. It is low resolution and noticeably soft.

## 5. Where we can beat them
| Them | Us |
|---|---|
| 720p/30fps, soft and compressed | **1080×1920, 60fps**, crisp, uploaded at a high bitrate |
| Captions are small, flat white and often sit right on top of the "his" shirt logo, which the OCR read inside the caption area dozens of times | Bigger captions placed safely, with a **subtle pop-in on each word** and keywords in our brand yellow. Still clean and readable, never gimmicky |
| Very little sound design | **Full sound design** that lands on the words: the motif sound (whistle/tap), whooshes on camera moves, room tone per scene, and a music swell timed to the twist |
| Story ends, then a hard loop | The **last frame matches the first frame**, so the loop is seamless and rewatches count |
| Generic mascot, unnamed | A **named mascot (Milo)** that viewers can attach to, comment about and ask for |
| Up to 3 minutes, sometimes with saggy middles | A **75–95s** sweet spot: every line either pushes the plot or sets up the payoff |

## 6. Risks / rules for us
- **Never copy their stories, mascot, logo or name.** Our stories are original, and we never reuse their character designs. Close imitation risks YouTube "reused content" demonetisation and impersonation strikes.
- Stories are presented as fiction or storytelling. We don't claim specific real people or events as true.
- Animation is the expensive part, so the production plan in `CLAUDE.md` covers how we generate it.
