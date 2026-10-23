"""Build Milo (15) with MPFB: real eyes, eyelids, mouth, ARKit face units + visemes."""
import bpy, os, glob, addon_utils
addon_utils.enable("bl_ext.user_default.mpfb", default_set=True)
addon_utils.enable("io_anim_bvh", default_set=True)
from bl_ext.user_default.mpfb.services.humanservice import HumanService
from bl_ext.user_default.mpfb.services.targetservice import TargetService
from bl_ext.user_default.mpfb.services.faceservice import FaceService
from bl_ext.user_default.mpfb.services.locationservice import LocationService

USER = "/root/.config/blender/5.2/extensions/.user/user_default/mpfb/data"

MILO_YELLOW = (0.80, 0.36, 0.015, 1)   # mustard hoodie, linear-ish
NAVY = (0.012, 0.018, 0.06, 1)
HAIR_WHITE = (0.85, 0.86, 0.9, 1)
ICE_BLUE = (0.35, 0.65, 0.95, 1)


def find(kind, name, ext=".mhclo"):
    for root in (USER, os.path.join(os.path.dirname(USER), "..")):
        hits = glob.glob(f"{USER}/{kind}/**/{name}{ext}", recursive=True)
        if hits:
            return hits[0]
    hits = glob.glob(f"/root/.config/blender/5.2/extensions/**/{kind}/**/{name}{ext}", recursive=True)
    if not hits:
        raise FileNotFoundError(f"{kind}/{name}{ext}")
    return hits[0]


def _tint(obj, rgba, rough=None, keep_tex_mult=False):
    """Recolour every material on obj by multiplying the base colour input."""
    for slot in obj.material_slots:
        m = slot.material
        if not m or not m.use_nodes:
            continue
        nt = m.node_tree
        for n in nt.nodes:
            if n.type == 'BSDF_PRINCIPLED':
                inp = n.inputs["Base Color"]
                if inp.is_linked and keep_tex_mult:
                    # keep only the texture's light/dark detail, then colour it
                    src = inp.links[0].from_socket
                    bw = nt.nodes.new("ShaderNodeRGBToBW")
                    nt.links.new(src, bw.inputs[0])
                    mr = nt.nodes.new("ShaderNodeMapRange")
                    mr.inputs["From Min"].default_value = 0.0
                    mr.inputs["From Max"].default_value = TINT_FROM_MAX
                    mr.inputs["To Min"].default_value = 0.55
                    mr.inputs["To Max"].default_value = 1.0
                    nt.links.new(bw.outputs[0], mr.inputs["Value"])
                    mix = nt.nodes.new("ShaderNodeMix")
                    mix.data_type = 'RGBA'
                    mix.blend_type = 'MULTIPLY'
                    mix.inputs[0].default_value = 1.0
                    nt.links.new(mr.outputs[0], mix.inputs[6])
                    mix.inputs[7].default_value = rgba
                    nt.links.new(mix.outputs[2], inp)
                else:
                    for l in list(inp.links):
                        nt.links.remove(l)
                    inp.default_value = rgba
                if rough is not None:
                    n.inputs["Roughness"].default_value = rough


def build(age=0.33, cartoon=0.75, rig="cmu_mb"):
    macro = TargetService.get_default_macro_info_dict()
    macro.update({"gender": 1.0, "age": age, "muscle": 0.45, "weight": 0.42,
                  "height": 0.55, "proportions": 0.55,
                  "race": {"asian": 0.05, "caucasian": 0.9, "african": 0.05}})
    body = HumanService.create_human(macro_detail_dict=macro, scale=0.1)
    body.name = "Milo.body"

    # Stylised head (bigger eyes, softer features) – the HisStory / Pixar-ish look
    TargetService.bulk_load_targets(body, [
        {"target": "spamrakuen_toon_eyes_and_slim_body_head_only", "value": cartoon},
        {"target": "sonntag78_toonify_head", "value": 0.45},
    ])

    # Face: ARKit face units + visemes as shape keys (blink, smile, jawOpen, ...)
    FaceService.load_targets(body, load_microsoft_visemes=True, load_meta_visemes=False,
                             load_arkit_faceunits=True)

    HumanService.add_builtin_rig(body, rig)

    def add(kind, name, asset_type, mat="MAKESKIN"):
        return HumanService.add_mhclo_asset(find(kind, name), body, asset_type=asset_type,
                                            subdiv_levels=0, material_type=mat)

    parts = {}
    parts["eyes"] = add("eyes", "high-poly", "Eyes")
    parts["eyebrows"] = add("eyebrows", "mindfront_eyebrows_11", "Eyebrows")
    parts["eyelashes"] = add("eyelashes", "mindfront_eyelashes_01", "Eyelashes")
    for nm, at in (("teeth_base", "Teeth"), ("tongue01", "Tongue")):
        try:
            parts[at.lower()] = add(at.lower(), nm, at)
        except Exception as e:
            print("skip", nm, e)
    parts["hair"] = add("hair", HAIR, "Hair")
    parts["top"] = add("clothes", "toigo_fisherman_sweater", "Clothes")
    parts["pants"] = add("clothes", "cortu_cargo_pants", "Clothes")
    try:
        parts["shoes"] = add("clothes", SHOES, "Clothes")
    except Exception as e:
        print("no shoes", e)

    # Skin
    skins = glob.glob(f"/root/.config/blender/5.2/extensions/.user/user_default/mpfb/data/skins/**/*.mhmat", recursive=True)
    skin = next((s for s in skins if "young" in s and "caucasian" in s and "male" in s and "female" not in s), skins[0] if skins else None)
    if skin:
        HumanService.set_character_skin(skin, body, skin_type="ENHANCED_SSS")

    # Brand colours
    if parts.get("hair"):
        _tint(parts["hair"], HAIR_WHITE, rough=0.45, keep_tex_mult=True)
    _tint(parts["top"], MILO_YELLOW, rough=0.85, keep_tex_mult=True)
    _tint(parts["pants"], NAVY, rough=0.8, keep_tex_mult=True)
    if parts.get("eyebrows"):
        _tint(parts["eyebrows"], (0.75, 0.75, 0.78, 1), keep_tex_mult=True)
    if parts.get("shoes"):
        _tint(parts["shoes"], (0.9, 0.9, 0.88, 1), keep_tex_mult=True)
    try:
        recolor_eyes(parts["eyes"], os.path.join(os.path.dirname(__file__), "milo_eye_blue.png"))
    except Exception as e:
        print("eye recolor failed", e)
    return body, parts


TINT_FROM_MAX = 0.5


def recolor_eyes(eye_obj, out_png):
    """Brown iris -> ice blue (brand), keep sclera; adds amber wedge on the left iris later."""
    import numpy as np
    for slot in eye_obj.material_slots:
        nt = slot.material.node_tree
        for n in nt.nodes:
            if n.type == 'TEX_IMAGE' and n.image:
                img = n.image
                w, h = img.size
                px = np.array(img.pixels[:], dtype=np.float32).reshape(h, w, 4)
                rgb = px[..., :3]
                mx, mn = rgb.max(-1), rgb.min(-1)
                sat = (mx - mn) / np.maximum(mx, 1e-5)
                mask = (sat > 0.18)[..., None]
                lum = rgb.mean(-1, keepdims=True)
                blue = np.concatenate([lum * 0.55, lum * 1.15, lum * 1.9], -1)
                blue = np.clip(blue * 1.4 + np.array([0.05, 0.12, 0.2]), 0, 1)
                rgb[:] = np.where(mask, blue, rgb)
                px[..., :3] = rgb
                new = bpy.data.images.new("milo_eye_blue", w, h, alpha=True)
                new.pixels = px.ravel().tolist()
                new.filepath_raw = out_png
                new.file_format = 'PNG'
                new.save()
                n.image = new


HAIR = os.environ.get("MILO_HAIR", "cortu_short_messy_hair")
SHOES = os.environ.get("MILO_SHOES", "")
