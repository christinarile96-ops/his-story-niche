# Milo Remembers: animated story Shorts factory

These are faceless 3D-animated first-person story Shorts in the lane of @HisYTStory, made better: 1080p60, full sound design, a named mascot and seamless loops. Shorts only for now. Read `research/competitor-analysis.md` and `brand/brand-guide.md` before any work.

## Workflow (follow it in order)
1. **Script first, then stop.**
   - Write `scripts/NN-slug.md` with the title, a VO block, pronunciation notes and a beat map. Send it to the user.
   - **Wait for the voiceover.** Don't build anything before the audio arrives.
2. **Visuals:** one 3D shot per beat (about 2–4s each), with Milo and the recurring cast kept on-model.
   - Generate clips from the beat-map prompts with an image-to-video model, using character reference images to keep them consistent. Options: Kling / Seedance / Veo, via vidIQ `generate_video` or done by the user.
   - Always quote the credit cost before generating.
3. **Voice edit:** cut every pause to **≤0.08s** and remove breaths. Normalise to −14 LUFS. Keep the voice continuous, a "wall of voice".
4. **Captions:**
   - force-align each word
   - 1–3 words per card, Montserrat ExtraBold, white with a black stroke, centred at 70% height, about 6% of frame height
   - 1–2 keywords per sentence in Milo Yellow `#F6B800`
   - 80ms pop-in on each card
5. **Sound:**
   - a quiet music bed about 20 dB under the voice, which swells at the twist and drops out on the final line
   - the story's motif SFX every time the motif is mentioned
   - whooshes on camera moves and room tone per location
6. **Edit rules:**
   - a new shot or camera move every 1.5–3s
   - the first frame already shows emotion, and the first caption is on screen at 0.0s
   - the last frame matches the first so the loop is seamless
   - no CTA, no end card, no intro
7. **Export:** 1080×1920, 60fps, H.264 at a high bitrate, 75–95s. Save it to `final/NN-slug.mp4`.
8. **Deliver:**
   - a phone-viewable copy as a private Artifact page
   - the full file via SendUserFile
   - a title (3–7 words + 1 emoji), a 1-line description and 3 hashtags

## Script rules
- 200–240 words (about 75–90s at 160–170 wpm), first person, plain words, short sentences, 30–40% dialogue.
- The first sentence puts the viewer in a specific emotional situation. No "Hey guys", no context-setting.
- Plant a motif in the first 5s and pay it off in the last line.
- Use 2–4 time jumps ("Two winters later…"), at least one doubter, and one crisis.
- The last line is a quiet callback. Never end with a question or a "follow".
- Original stories only. Never retell a competitor's plot.
- Write numbers the way they should be said ("seventy-four").

## Never
- Copy the competitor's mascot (orange curly hair, white "his" tee, green pants), logo, name or plots.
- Present invented stories as verified true events about real, named people.
