# 3D pipeline (Blender): Milo Remembers

Goal: real 3D characters that act, with a camera that never stops, like the competitor.

## Who does what
| Step | Who | Where |
|---|---|---|
| 1. Our character sheets → 3D models | you | Tripo or Meshy (image → 3D) |
| 2. Skeleton + animations | you | Mixamo (free, Adobe login) |
| 3. Upload the files to the repo | you, or the local Claude chat | GitHub `assets/3d/` |
| 4. Automatic scene building: characters, animations, a camera synced to the words, lights, mouth movement | me | `engine/blender/` |
| 5. Render (Eevee, 720×1280 @30fps, upscaled to 1080p) | the local Claude chat on the M1 Mac | Blender |
| 6. Captions, voice cutting, SFX, music, export | me | `engine/render.py` + `engine/sound.py` |

The M1 with 8GB has a GPU, so Eevee is many times faster than the CPU-only cloud server (11 s/frame there). We keep scenes light (2K textures, at most 3 characters per shot) so they fit in 8GB.

## Step 1: Tripo or Meshy (image → 3D)
Input images are in `assets/3d-input/`. Each character has front / threequarter / side / back views on a plain background.
1. Choose **Image to 3D**. If the site offers **Multi-view**, upload `*_front`, `*_side` and `*_back`; otherwise use `*_front` only.
2. Generate with textures. Pick the version whose face looks most like the sheet; the eyes matter most for Milo.
3. Export as **FBX** (or GLB) **with textures**, in **A-pose / T-pose**, with no rig (Mixamo does the rig).
4. Order of priority: `milo15` (the main mascot), `grandpa`, `milo6`, `milo17`, `grandpa_winter`.
5. ⚠️ **License:** check that your plan allows commercial use (monetized YouTube/TikTok). Some free plans make models public or CC BY.

## Step 2: Mixamo (skeleton + animations)
1. mixamo.com → **Upload Character** → the FBX from Tripo or Meshy → place the markers (chin, wrists, elbows, knees, groin) → Next.
2. For each animation below: search for it, set **In Place** when the option exists, then **Download** → FBX Binary, **With Skin**, **30 fps**.
3. Name the files `<character>__<animation>.fbx`, e.g. `milo15__walking.fbx`.

### Animations for script 01 (search these names in Mixamo, or the closest match)
**Grandpa:** Idle · Waving · Talking · Head Nod Yes · Sad Idle · Walking · Kneeling · Looking Around · Pointing
**Milo 6:** Idle · Waving · Running · Walking
**Milo 15:** Walking · Angry Gesture (or Yelling) · Shrugging · Sad Walk · Looking Around
**Milo 17:** Idle · Looking Around · Yelling · Terrified · Sitting Idle (curled under the tree) · Crying · Standing Up
**Friends:** Laughing · Pointing · Idle

## Step 3: Upload
To keep the file names, put them in `assets/3d/<character>/` on the branch `claude/serene-brahmagupta-9222yv`. Files over 25MB can't go through the GitHub website, so let the local Claude chat push them with git.
