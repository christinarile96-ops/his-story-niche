# Pilot results (2026-10-23): faces decide the pipeline

Test done for $0, before paying for Tripo Pro. Code: `engine/blender/pilot/`.

## 1. Tripo (free plan, 40 of 200 credits used)
Input: `milo15_front.png` with the labels cropped off, HD model, 4K PBR texture, Remove Lighting on, 80k triangles.
- ✅ **Body, clothes and hair are very close to the sheet:** the M hoodie, the silver cowlick and the yellow laces.
- ❌ **The face can't be animated.** In the untextured (clay) view the eyes and mouth are only **painted on the texture**. There are no eyeballs, no eyelids and no mouth opening, so no blink, no lip-sync and no expressions. Tripo Pro uses the same generator, so paying won't change this.
- ❌ The free plan blocks **every export** (FBX and GLB both open the "Upgrade" paywall).

## 2. MPFB 2 (free, CC0 assets): the face works
Milo 15 is built entirely from script (`milo.py`):
- macro age 0.33, male, `spamrakuen_toon_eyes` 0.75 plus `sonntag78_toonify_head` 0.45 for the stylised big-eye look;
- hair `culturalibre_hair_05` tinted white;
- eyes recoloured to ice blue (`milo_eye_blue.png`);
- fisherman sweater tinted Milo Yellow, cargo pants tinted navy, `shoes05` white sneakers.

**ARKit face units plus visemes are loaded as shape keys:** eyeBlink, mouthSmile, jawOpen, browDown, browInnerUp, mouthFrown, mouthFunnel and the rest. Blink, smile, talk, annoyed and sad were all tested and render correctly.

What still needs work:
- a real hoodie with an M patch (an MPFB clothes asset, or a Tripo hoodie fitted with MPFB's MakeClothes);
- the amber wedge and crescent birthmark as a texture overlay;
- clothing clipping at the elbows.

## 3. Animation
- **Mixamo:** logged in fine, but every download from Christina's Chrome fails with **HTTP 503 from Mixamo's S3 storage** (three attempts, three animations). Unresolved. Try again later, or from another network.
- **Pilot fallback: CMU motion capture** (free) on MPFB's `cmu_mb` rig. The bone names match the BVH 1:1. `retarget.py` aligns the rest pose, bakes world-space rotations and scales the root motion. The walk plants its feet properly.
- The standing/acting pose is procedural: aimed arm bones plus keyed head, neck and spine beats.

## 4. Location and camera
- Poly Haven (CC0): sofa, rocking chair, plant, tables, lantern, laminate floor and plaster walls. The API needs a `User-Agent` header.
- **Shot A:** 26 mm low angle, dolly plus Track-To on Milo's chest.
- **Shot B:** 50 mm f/2 close-up with DOF on the eyes and a slow push-in. The cut is done with timeline markers.

## 5. Render cost
- Cloud container (2 CPU, no GPU): Cycles at 432×768, 6 samples plus denoise, takes **~13 s per frame**. Eevee in software GL is unusable (more than 10 minutes per frame).
- The M1 Mac should run Eevee or Cycles on Metal many times faster. This still needs measuring there (`docs/asset-library.md` checklist).

## 6. Decision this supports
- **Hero and recurring characters: MPFB** (free, real face rig, unlimited variants, CC0).
- **Tripo is only needed for props and set pieces.** Start with a **$10 credit pack** (~40 props) instead of a $14–20 Pro month. Note: the commercial-use terms for credit packs bought on the free plan still need checking.
- Next: hoodie and brand details on Milo, a Grandpa Joe build, retry Mixamo, and a Mac speed test.
