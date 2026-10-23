# 01: Grandpa's Whistle, prompts for TryAIToday Flow Automator (Image tab)

These follow the Flow Automator format: one prompt per block with a blank line between blocks, `#name` names the image a prompt creates, and `@name` reuses a named image as a reference for that prompt. Leave the **Reference Images (Subject/Scene/Style) slots empty**. Every reference is handled by `@tags` inside the prompts.

**Settings for every run:** Nano Banana 2 (or Pro) · highest quality/resolution available (4K, else 2K) · images-per-prompt **1** for RUN1, **2** for the other runs.

| Run | File | Aspect ratio | What |
|---|---|---|---|
| 1 | `RUN1_16x9_character_sheets.txt` | **16:9** | 6 character sheets, named `#milo6 #milo15 #milo17 #grandpa #grandpa_winter #friends` |
| ⏸ | **Stop and send me the 6 sheets.** If one is off, re-run just that block. If you prefer a different image, rename it in Flow to the same name (the newest image with a name wins). |
| 2 | `RUN2_9x16_scenes_poses_backgrounds.txt` | **9:16** | 9 backgrounds (`#bg_*`), 21 poses on green (`#gj_*`, `#gjw_*`, `#m6_*`, `#m15_*`, `#m17_*`, `#friends_laugh`), 4 hero scenes (`#scene_*`) |
| 3 | `RUN3_1x1_profile_picture.txt` | **1:1** | `#brand_avatar` |
| 4 | `RUN4_16x9_banner.txt` | **16:9** | `#brand_banner` |

Runs 2–4 reuse the sheets from run 1 through `@milo17`, `@grandpa_winter` and the other names, so run 1 has to finish first.

**Send back:** the downloaded run folders (zip them). The `#names` tell me exactly what each image is.

What I build in code is listed in `scripts/01-grandpas-whistle.md` and the main `CLAUDE.md`: the compositing, camera moves, snow, fog, the flashlight beam, the phone screen, captions, sound and the export.
