# 01: Grandpa's Whistle, image prompts for Nano Banana (Google Flow)

## How it all fits
- **You (Nano Banana):** characters and their poses on chroma green, empty environment plates, plus 4 full "hero" scenes where the characters have to touch the environment (the hug, the snowmobile).
- **Me (code):**
  - keying out the green and compositing each character into the plates in 3D layers with real parallax
  - camera moves (push-ins, orbits, handheld drift, whip pans)
  - contact shadows, colour-matching each character to the scene light
  - procedural snow, fog, breath vapour, the flashlight beam and lens flare, the white-out
  - the dying phone screen, the "6 HRS" clock, the rope-duck moment
  - captions, every sound effect, the music, voice cutting and the 1080×1920 60fps export

## Settings in Flow
- Model: **Nano Banana 2** (or Nano Banana Pro if you have it)
- Resolution: **the highest available** (4K if offered, otherwise 2K). Never 1K.
- Aspect ratio: as written in each file name (`9x16` = portrait, `16x9` = landscape)
- Outputs per prompt: **2**. Send me both; I'll pick.

## Order (important for consistency)
1. **A_reference_sheets_16x9.txt** (no reference). Pick the best sheet of each and name them:
   - A1 = Milo age 6
   - A2 = Milo age 15
   - A3 = Milo age 17 (snow)
   - A4 = Grandpa (flannel)
   - A5 = Grandpa (winter coat)
   - A6 = the 3 friends

   **Send me these first, before batch B,** so I can check that Milo looks right.
2. Each **B** file and the **D** file: attach the reference images named in its file name, e.g. `B5_..._attach_A3` means attach sheet A3, then paste the prompts.
3. **C** (environments): no reference needed. You can run it in parallel with A.
4. **E** (brand: profile picture and banner): attach A2.

## Sending back
Zip each batch and keep the file names, or just keep the download order. I can identify every image by looking at it.

## Format of the .txt files
One prompt per paragraph, with a blank line between prompts. If the Flow Automator wants one prompt per line, every prompt is already on a single line, so just delete the blank lines.
