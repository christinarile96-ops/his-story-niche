# Asset library: one paid month ($14), used for every Short after it

Goal: in **one month of Tripo Pro** ($20, 3000 credits, about 200 models), generate the core reusable 3D library (~100 textured models) the channel will need for months of daily Shorts, store it in this repo, then cancel.
Quality bar: the HisStory look (`research/competitor-analysis.md` §4) with our own brand (`brand/brand-guide.md`).

> Status: **plan, nothing bought yet.** The user pays and cancels the subscription herself. Claude does the generation in Chrome.

## 0. License (checked 2026-10-23 on tripo3d.ai)
- **Free plan:** "Public Models · Non-Commercial Use". The Terms (§5.2.1) say Tripo "retains all rights" to free users' outputs. **Free models must never appear in a published video.**
- **Pro plan:** "Private Models · Commercial Use". The Terms (§5.2.2) say paid users "generally have all rights … derive revenue" in their outputs. The rights cover models generated *while paid*, so everything must be generated and downloaded inside the paid month. Keep the invoice.
- Mixamo: free with an Adobe account. Animations can be used in monetized videos, but the raw animation files can't be redistributed. **Keep this repo private.**
- Meshy Free (fallback): CC BY 4.0, which allows commercial use with the credit "3D models: Meshy". Front image only, "Meshy 6 Lite" quality.

## 1. Price and credit budget (checked 2026-10-23 on tripo3d.ai/pricing)
- Pro, monthly: **$14 the first month (30% off), then renews at $20/month**. Cancel before the renewal date. Refunds are only for accidental purchases, requested within 24h with no credits used.
- Extra credits if needed: **$10 = 1000 credits**.
- Credit costs (Tripo FAQ): HD Generate **15**, Texture Gen **+10**, HD Texture **+10**, Ultra **+15**, Auto Rig **20**.
  - A character (HD + texture + HD texture) = **35 credits**.
  - A prop (HD + texture) = **25 credits**.
  - "≈200 models" on the pricing page means untextured models, so **the real number is about 90–100 textured models**, not 180.

| Block | Models | Credits |
|---|---|---|
| A + B. Hero, recurring and variant characters | ~25 | ~875 |
| Retries for faces (Milo above all) | ~10 | ~350 |
| Pets (dog, cat) incl. Tripo Auto Rig | 2 | ~110 |
| C + D. Props and set pieces most needed by scripts 01–10 | ~65 | ~1625 |
| **Total** | **~100** | **~2960 / 3000** |

Order: A → the props and set pieces scripts 01–10 need → the rest. The remaining props in §5/§6 are added later, as scripts need them, with a $10 credit pack (~40 props) instead of a second month.
Simple props (a mug, a book, a box) can be untextured (15 credits) and given flat materials in Blender, which matches the stylised look and saves 10 credits each.

## 2. Input image rules (quality depends on this more than anything)
Pro includes image generation (Nano Banana etc.) that costs no 3D credits, so every input image is made inside Tripo with the same **style lock**:

> stylized semi-realistic 3D CGI character, Pixar-meets-Unreal look, big expressive eyes, soft skin shading, clean readable silhouette, plain mid-grey studio background, soft even lighting, no text, no labels, no shadow on the floor

Rules for characters:
- **A-pose** (arms ~45° away from the body, legs slightly apart, fingers spread). Arms touching the body break Mixamo's auto-rig.
- Front, side and back views of the same character at the same scale, **with no text labels**. The current `assets/3d-input/*.png` include "FRONT VIEW" labels and cropped edges, so they get regenerated clean.
- Mouth closed and neutral expression, because the expressions are added later.
- Avoid long open coats, scarves and capes, which rig badly. Hair should be fairly compact.

Rules for props: one object, centred, 3/4 view, plain grey background, the same style lock without the character part.

## 3. Block A: characters (multi-view, HD textures, then Mixamo)
File names: `assets/3d/<id>/<id>.fbx` plus textures, and animations `assets/3d/<id>/<id>__<animation>.fbx`.

| id | Who | Notes (from the brand guide) |
|---|---|---|
| milo6 | Milo at 6 | silver-white hair with a cowlick crest, ice-blue eyes with an amber wedge in the left iris, crescent birthmark, mustard hoodie with a navy M, navy cargo joggers, white high-tops with yellow laces |
| milo10 | Milo at 10 | **default mascot age** for childhood stories |
| milo15 | Milo at 15 | |
| milo17 | Milo at 17 | |
| milo30 | adult Milo | same hair and eyes; plain mustard jumper instead of the hoodie |
| grandpa | Grandpa Joe | white beard, white cowlick, red plaid flannel |
| grandma | Grandma | soft grey bun, cardigan (new, brand guide to add) |
| mom | Mom | brown bob, green cardigan |
| dad | Dad | stubble, navy work jacket |
| theo8 / theo15 | best friend Theo | buzz cut, orange tee |
| sister | little sister (new, to name) | |
| friend_a, friend_b, friend_c | teen friend group | distinct hair and colours, never the competitor's palette |
| bully | school bully | |
| teacher_f, teacher_m | teachers | |
| coach | sports coach | tracksuit, whistle |
| doctor, nurse | hospital | |
| neighbor_old | old neighbour | |
| boss | adult-story boss or customer | suit |
| stranger_poor | homeless or poor stranger | a common HisStory beat |
| baby | a baby in a blanket, posed and not rigged | |
| dog, cat | pets | rigged with **Tripo's own rigging** (Mixamo is humanoid only) |

Extras (crowds, classmates, a waiter) are **not** made in Tripo. They come free and unlimited from **MPFB** in Blender, posed with the same Mixamo animations.

## 4. Block B: outfit and age variants
Each variant is generated from the base character's front image ("same character, now wearing…") so the face stays the same:
`milo10_pajamas`, `milo10_winter`, `milo10_school_uniform`, `milo17_snow_gear`, `milo30_suit`, `milo30_hospital_gown`, `grandpa_winter`, `grandpa_hospital_gown`, `grandpa_suit`, `mom_work_uniform`, `dad_construction`, `dad_suit`, `theo15_football_kit`, `milo15_football_kit`, `grandma_apron`.

## 5. Block C: props (≈90, grouped by story theme)
**Motif and memory objects (these carry the twists, so they're worth the most):** a whistle, a pocket watch, a handwritten letter, a framed photo, a wedding ring, an old music box, a worn teddy bear, a diary, a homemade birthday card, a toy car, a knitted scarf, a key on a string, a jar of coins, a paper crane, a seashell, a medal, a trophy, a harmonica, an old cassette player, a love-lock padlock
**Home:** an alarm clock (digital), a smartphone, an old flip phone, a laptop, a TV remote, a mug, a dinner plate with food, a birthday cake with candles, a gift box, a lunchbox, a broom, a laundry basket, a table lamp, a backpack, a piggy bank, an envelope pile (bills), a wallet, a bundle of cash, a coin, a credit card (blank)
**School:** a desk with chair, an exam paper with a red mark, textbooks, a pencil case, a school bus seat, a locker door, a chalkboard eraser, a basketball, a football, a skateboard
**Work and money:** a cement bag, a toolbox, a hammer, a paint bucket, a shovel, a hard hat, a briefcase, a cash register, a delivery box, a "SOLD" sign
**Outdoors and travel:** a bicycle, a kid's bike with training wheels, a park bench, a mailbox, a trash can, a street lamp, an umbrella, a suitcase, a bus-stop sign, a snowboard, a flashlight, a rope, a camping lantern
**Hospital:** a hospital bed, an IV stand, a heart monitor, a wheelchair, a crutch, a pill bottle, a get-well flower bouquet, a cast (arm)
**Food and celebrations:** a pizza box, a Christmas tree, a wrapped present stack, balloons, a graduation cap, a wedding cake, a candle
**Animals and nature:** a bird nest, a goldfish bowl, a dog bowl and leash, a small potted plant, a dead tree stump

## 6. Block D: set pieces (large objects that make a location believable)
A porch with steps and a railing (Grandpa's house, the brand's home base), a front door and frame, a kid's bed, a kitchen counter with stove, a dining table with chairs, a sofa, a classroom whiteboard wall, a hospital curtain, a car (old family sedan), a pickup truck, a snowmobile, a school bus (exterior), a garden fence with gate, a treehouse, a gravestone, a mailbox post, a garage door, a football goal, a ski-lodge door with chair, a stadium seat row.
Everything else for a location (rooms, terrain, skies, lighting) comes free from **Poly Haven** (CC0: HDRIs, textures, models) and from MPFB/Blender primitives.

## 7. After download, per asset (automatic, done by the scene engine)
1. Import, scale to real-world size (a person is ~1.7 m), set the origin at the feet or the base.
2. Downscale textures to **2K** (so the scenes fit the 8 GB M1).
3. Characters: check the Mixamo rig (fingers, hair, clothes), and add **face shape keys** (blink, mouth open, smile, frown) so lip-sync and acting are possible. See decision 3 in `docs/handoff-message.md`.
4. Write one line per asset into `assets/3d/library.json` (id, type, tags, height, animations, license = "Tripo Pro, generated <date>").

## 8. Storage
150–200 models with textures come to several GB. Before the first push, decide **Git LFS** (`*.fbx`, `*.glb`, `*.png` under `assets/3d/`) and check the GitHub LFS quota, and keep a second copy on Google Drive.

## 9. Review by the scene-engine chat (2026-10-23)
**Decisions**
1. **Milo 10 as the default:** agreed. Script 01 still needs milo6, milo15, milo17, grandpa, grandpa_winter and three friends, so those go first.
2. **Locations, not only objects.** HisStory reuses the same few sets over and over (the blue hospital room appears in many Shorts). I'll build **6 reusable location .blend files** once: Grandpa's porch and yard, the family kitchen/living room, Milo's bedroom, a school classroom and hallway, a hospital room, and a street. They're assembled from Tripo set pieces, Poly Haven and primitives. Block D should feed these six first.
3. **Faces: the pilot decides,** with this checklist on the free Tripo milo15:
   - (i) Are the eyes separate geometry or painted onto the texture?
   - (ii) Is there a mouth opening?
   - (iii) Is the mesh clean enough for shape keys?
   If the answers are no, no, no, then **(b)**: hero cast faces/bodies come from MPFB (real eyeballs, so the gold-wedge iris is just a texture; a face rig; stylized with head/eye proportion targets), with hair and clothes from Tripo as separate meshes. Faceit (c) needs clean quad topology around the eyes and mouth, which Tripo meshes usually lack, so try it only if the pilot shows a clean mesh. Lip-sync is needed for quoted dialogue (Grandpa's "Kiddo…"). Rhubarb plus 6–8 mouth shapes is enough.
4. **Storage:** `.gitattributes` for LFS is added. Before the first push, check the LFS quota in GitHub Billing (the free quota is small). Keep the repo **private** (Mixamo terms) and keep a Drive backup.
5. **Pilot first:** agreed. Also measure Eevee speed on the M1: run `engine/blender/walk_test.py` at 720×1280 and write down seconds per frame.

**Draft slate 02–10 and assets missing from the lists above**
| # | Working title | Core idea | Missing assets |
|---|---|---|---|
| 02 | The Lunch Lady Knew | She quietly paid Milo's lunch debt for years | lunch_lady (character), cafeteria counter, tray, school cafeteria set |
| 03 | Dad's Watch Stopped At 4:17 | Milo mocks Dad's broken watch; it stopped the minute Milo was born and nearly didn't make it | wristwatch, hospital delivery room, baby, incubator |
| 04 | The New Kid Who Never Talked | Milo (10) sits with silent Theo; years later Theo returns the favour | lunch table, school bus interior |
| 05 | Grandma's Coin Jar | Milo steals coins for a game; the jar was his college fund | video-game controller/console, graduation stage |
| 06 | Mom Always "Already Ate" | Poverty; Mom skipped dinner for years | refrigerator (open, empty), mom_work_uniform |
| 07 | The Dog That Barked Every Night | The neighbour's "annoying" dog wakes the house during a fire | fire truck, smoke alarm, smoke/fire (Blender FX) |
| 08 | I Was Ashamed Of Dad's Job | Dad is the school janitor; twist at the award assembly | dad_janitor variant, mop and bucket, auditorium seats, stage |
| 09 | Theo's Last Pass | A football final and a hospital promise | stadium stand (set), scoreboard |
| 10 | The Card That Came Every Birthday | Anonymous cards every year, from Grandpa, even after he died | gravestone (already listed), mailbox (already listed), a stack of old cards |

**Growth ideas (additions)**
- **Captions are applied after rendering in our engine**, so every language version only re-runs captions + audio, with no 3D re-render. Language order: Spanish, Portuguese, Hindi, then Indonesian.
- **Series numbering** in the description ("Milo's Memory #12") plus a pinned "all memories" playlist. Recurring Easter eggs (the whistle, the crescent, the M) get people commenting without asking them to.
- Don't add a CTA or end card: the competitor never uses one, and the seamless loop gives more rewatches.
- Start "Her" only after Milo reaches about 50 posted Shorts, so the library is already paid off.

**Before paying**
- [ ] Pilot render approved on the Mac (body + walk + camera + face test)
- [ ] Eevee seconds/frame measured on the M1
- [ ] Repo private, LFS quota checked, Drive backup folder ready
- [ ] Mixamo/Adobe login works
- [ ] Calendar reminder to cancel Tripo Pro 2 days before renewal
