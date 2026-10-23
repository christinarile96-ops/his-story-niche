"""Grandpa's Whistle: shot list. Every cut is anchored to a spoken word with w(line, 'word').

Layers sit in screen space (x, y = where the image centre lands, s = width relative
to the frame; a 1536px-wide image at s=1 fills 1080px). depth < 1 moves less with the
camera (parallax). Values can be [from, to] (eased over the shot) or [[u, v], ...] keys.
"""
import re

TIMING = None  # set by build()
DURATION = 0.0

NIGHT = {'tint': (1.12, 0.92, 0.78), 'exp': 0.62}          # cool moonlight on cutouts (BGR)
DUSK = {'tint': (0.95, 0.95, 1.05), 'exp': 0.9}
WARM = {'tint': (0.9, 0.98, 1.08)}
SNOWDAY = {'tint': (1.06, 1.0, 0.96)}


def w(line, word, n=0):
    """Start time of the n-th occurrence of `word` in script line `line`."""
    ws = TIMING['lines'][line]['words']
    hits = [x for x in ws if re.sub(r'[^a-z\-]', '', x['w'].lower()).startswith(word.lower())]
    return hits[n]['s']


def line(i):
    return TIMING['lines'][i]['start']


def bg(name, **kw):
    d = {'img': name, 'depth': 0.35, 's': 1.12}
    d.update(kw)
    return d


def cut(name, **kw):
    d = {'img': f'cut/{name}', 'depth': 1.0, 'shadow': True, 'bob': 2}
    d.update(kw)
    return d


def build(timing):
    global DURATION, TIMING
    TIMING = timing
    DURATION = round(timing['lines'][-1]['end'] + 1.6, 2)
    L = timing['lines']
    S = []

    # 0 · porch, Grandpa whistling (also the loop frame)
    S.append(dict(id='porch', t0=0.0, layers=[
        bg('bg_porch'),
        cut('gj_whistle', x=650, y=1010, s=0.98, grade=WARM, shadow=False)],
        cam=dict(z=[1.12, 1.0], y=[30, 0], ease='out'),
        fx=dict(bloom=0.25)))
    # 1 · "High, then low" – close on Grandpa, two notes float up
    S.append(dict(id='highlow', t0=line(1), layers=[
        bg('bg_porch', blur=10, x=500),
        cut('gj_smile', x=540, y=1080, s=1.0, grade=WARM, shadow=False)],
        cam=dict(z=[1.0, 1.08]),
        fx=dict(notes=[(w(1, 'high'), 200, 900, 70), (w(1, 'low'), 880, 1000, 56)], bloom=0.2)))
    # 2 · six-year-old Milo whistling back from the gate
    S.append(dict(id='kid', t0=line(2), in_='whip', layers=[
        bg('bg_yard'),
        cut('m6_whistle', x=560, y=1150, s=0.62, grade=WARM)],
        cam=dict(z=[1.0, 1.12], fy=150),
        fx=dict(notes=[(w(2, 'whistle') + 0.05, 720, 760, 50)], bloom=0.2)))
    # 3 · "Come home safe" – Grandpa's warm smile
    S.append(dict(id='safe', t0=line(3), layers=[
        bg('bg_porch', blur=14, x=600),
        cut('gj_smile', x=560, y=1030, s=1.12, grade=WARM, shadow=False)],
        cam=dict(z=[1.0, 1.1], fy=-200)))
    # 4 · fifteen: friends laughing
    S.append(dict(id='friends', t0=line(4), in_='whip', layers=[
        bg('bg_street'),
        cut('friends_laugh', x=540, y=1050, s=1.15)],
        cam=dict(z=[1.0, 1.2], x=[40, -40], fy=-200)))
    # 5 · Milo embarrassed, friends behind
    S.append(dict(id='embarrassed', t0=w(4, 'whistled'), layers=[
        bg('bg_street', blur=4),
        cut('friends_laugh', x=380, y=880, s=0.62, blur=5, depth=0.6, shadow=False),
        cut('m15_embarrassed', x=640, y=1080, s=0.95)],
        cam=dict(z=[1.0, 1.1], x=[-20, 20])))
    # 6 · "I didn't whistle back" – Grandpa watches him walk off
    S.append(dict(id='walkaway', t0=line(5), layers=[
        bg('bg_yard', grade=DUSK),
        cut('m15_walk', x=640, y=1180, s=[0.42, 0.36], depth=0.6, flip=True),
        cut('gj_quiet_whistle', x=270, y=1150, s=1.25, grade=DUSK, shadow=False)],
        cam=dict(z=[1.0, 1.06])))
    # 7 · "I'm not a dog" – Milo turns and shouts at the porch
    S.append(dict(id='dog', t0=line(6), in_='whip', layers=[
        bg('bg_porch', grade=DUSK),
        cut('gj_whistle', x=650, y=900, s=0.55, depth=0.5, blur=3, grade=DUSK, shadow=False),
        cut('m15_shout', x=520, y=1180, s=1.1)],
        cam=dict(z=[1.0, 1.08], shake=[0, 0])))
    S.append(dict(id='dog2', t0=w(6, 'stop'), layers=[
        bg('bg_porch', grade=DUSK, blur=6),
        cut('m15_shout', x=540, y=1350, s=1.7)],
        cam=dict(z=[1.0, 1.05], shake=4)))
    # 8 · "He just nodded"
    S.append(dict(id='nodded', t0=line(7), layers=[
        bg('bg_porch', blur=16, grade={'exp': 0.75, 'sat': 0.7}),
        cut('gj_hurt', x=540, y=1050, s=1.25, grade={'sat': 0.85}, shadow=False)],
        cam=dict(z=[1.0, 1.12], fy=-250, ease='linear'), vignette=0.8))
    # 9 · empty porch at dusk
    S.append(dict(id='empty', t0=line(8), layers=[
        bg('bg_porch', grade={'exp': 0.55, 'tint': (1.15, 0.95, 0.85), 'sat': 0.6})],
        cam=dict(z=[1.08, 1.0], ease='out'), vignette=0.9))
    # 10 · two winters later: snowboarding
    S.append(dict(id='carve', t0=line(9), in_='flash', layers=[
        bg('bg_slope', s=[1.15, 1.2]),
        cut('m17_carve', x=[420, 640], y=[1150, 1250], s=0.85, grade=SNOWDAY, shadow=False)],
        cam=dict(z=[1.0, 1.1], shake=2), fx=dict(snow=0.3, wind=-200)))
    S.append(dict(id='rope', t0=w(9, 'cut'), in_='whip', layers=[
        bg('bg_slope', x=420),
        cut('m17_rope', x=560, y=1150, s=1.0, grade=SNOWDAY)],
        cam=dict(z=[1.0, 1.08]), fx=dict(snow=0.25)))
    # 11 · fog rolls in
    S.append(dict(id='fog', t0=line(10), layers=[
        bg('bg_fog'),
        cut('m17_lost', x=540, y=1200, s=0.6, grade={'exp': 0.9, 'sat': 0.8}, shadow=False)],
        cam=dict(z=[1.0, 1.15]),
        fx=dict(fog=[0.15, 0.85], snow=0.4, fog_col=(0.88, 0.89, 0.9))))
    # 12 · phone died, dark
    S.append(dict(id='phone', t0=line(11), layers=[
        bg('bg_fog', grade={'exp': 0.6, 'tint': (1.15, 0.95, 0.8)}),
        cut('m17_lost', x=520, y=1250, s=1.25, grade={'exp': 0.8, 'tint': (1.1, 0.95, 0.85)}, shadow=False)],
        cam=dict(z=[1.0, 1.1], fx=150, fy=-300),
        fx=dict(snow=0.4, night=True, fog=0.25, fog_col=(0.45, 0.42, 0.4),
                dark=[[0, 0], [0.55, 0], [0.75, 0.45], [1, 0.45]])))
    # 13 · screaming into the dark
    S.append(dict(id='scream', t0=line(12), in_='whip', layers=[
        bg('bg_pine_night'),
        cut('m17_scream', x=540, y=1180, s=0.95, grade=NIGHT)],
        cam=dict(z=[1.15, 0.98], shake=5, ease='out'),
        fx=dict(snow=0.6, night=True, wind=120, fog=0.15, fog_col=(0.35, 0.3, 0.25))))
    # 14 · search teams, six hours
    S.append(dict(id='search', t0=line(13), in_='fade', layers=[
        bg('bg_search', s=1.15)],
        cam=dict(z=[1.0, 1.18], y=[0, 60]),
        fx=dict(snow=0.5, night=True, counter=(0, 6, w(13, 'six') - 0.3, w(13, 'nothing'), 540, 520))))
    # 15 · curled under the pine
    S.append(dict(id='tree', t0=line(14), in_='dip', layers=[
        bg('scene_tree', depth=1.0, s=1.1)],
        cam=dict(z=[[0, 1.0], [0.8, 1.08], [1, 1.25]], fy=250),
        fx=dict(snow=0.35, night=True)))
    # 16 · the distant whistle
    S.append(dict(id='distant', t0=line(15), layers=[
        bg('bg_fog', grade={'exp': 0.35, 'tint': (1.2, 0.95, 0.75)}, s=1.2)],
        cam=dict(z=[1.0, 1.1]),
        fx=dict(fog=0.35, fog_col=(0.32, 0.3, 0.28), snow=0.4, night=True,
                glow=(540, 760, 260, [0.05, 0.18]),
                notes=[(w(15, 'high'), 470, 760, 54), (w(15, 'low'), 640, 860, 44)])))
    # 17 · cracked lips whistle back
    S.append(dict(id='lips', t0=line(16), layers=[
        bg('bg_pine_night', blur=12),
        cut('m17_lips', x=540, y=1000, s=1.3, grade=NIGHT, shadow=False)],
        cam=dict(z=[1.0, 1.12], fy=200), fx=dict(snow=0.3, night=True,
                                                    notes=[(w(16, 'back') - 0.1, 380, 1000, 48)])))
    S.append(dict(id='curled', t0=w(16, 'before'), layers=[
        bg('bg_pine_night'),
        cut('m17_curled', x=540, y=1260, s=0.85, grade=NIGHT)],
        cam=dict(z=[1.0, 1.06]), fx=dict(snow=0.4, night=True)))
    # 18 · "High, then low. Again. Closer." – Grandpa through the fog
    S.append(dict(id='closer', t0=line(17), layers=[
        bg('bg_fog', grade={'exp': 0.4, 'tint': (1.2, 0.95, 0.75)}),
        cut('gjw_whistle', x=540, y=[1150, 1080], s=[0.55, 1.05], grade=NIGHT, shadow=False, ease='in')],
        cam=dict(z=[1.0, 1.05]),
        fx=dict(fog=[0.55, 0.2], fog_col=(0.3, 0.28, 0.26), snow=0.5, night=True,
                glow=(540, 1150, [200, 420], [0.08, 0.3]),
                notes=[(w(17, 'high'), 330, 700, 52), (w(17, 'low'), 760, 820, 46)])))
    # 19 · flashlight hits his face
    S.append(dict(id='light', t0=line(18), layers=[
        bg('bg_pine_night', blur=10, grade={'exp': 0.8}),
        cut('m17_light', x=540, y=1050, s=1.25, shadow=False, grade={'exp': [0.65, 1.0]})],
        cam=dict(z=[1.0, 1.1], shake=[0, 3]),
        fx=dict(snow=0.3, night=True, glow=(540, 820, [300, 800], [0.05, 0.45]), bloom=0.35,
                flash=[(w(18, 'hit'), 0.35)])))
    # 20 · Grandpa. Seventy-four, waist-deep.
    S.append(dict(id='hero', t0=line(19), in_='flash', layers=[
        bg('scene_hero', depth=1.0, s=1.12)],
        cam=dict(z=[1.0, 1.18], y=[40, 0], fy=-200),
        fx=dict(snow=0.5, night=True, bloom=0.35)))
    # 21 · the lodge: he was told to wait
    S.append(dict(id='lodge', t0=line(20), in_='fade', layers=[
        bg('bg_lodge', s=1.12)],
        cam=dict(z=[1.0, 1.12], x=[30, -10]), fx=dict(bloom=0.3)))
    S.append(dict(id='hug', t0=w(20, 'didn') - 0.15, in_='flash', layers=[
        bg('scene_hug', depth=1.0, s=1.12)],
        cam=dict(z=[1.08, 1.0], ease='out'), fx=dict(snow=0.4, night=True, bloom=0.3)))
    # 22 · ride down at sunrise
    S.append(dict(id='ride', t0=line(21), in_='dip', layers=[
        bg('scene_snowmobile', depth=1.0, s=1.12)],
        cam=dict(z=[1.0, 1.1], x=[-25, 25], shake=1.5), fx=dict(snow=0.15, wind=-160, bloom=0.3)))
    # 23 · "Kiddo, I've whistled every single time…"
    S.append(dict(id='kiddo', t0=line(22), layers=[
        bg('bg_sunrise', blur=14),
        cut('gjw_smile', x=540, y=1020, s=1.3, shadow=False, grade={'tint': (0.95, 1.0, 1.06)})],
        cam=dict(z=[1.0, 1.08], fy=-200), fx=dict(snow=0.12, bloom=0.3)))
    S.append(dict(id='memory6', t0=w(22, 'every'), in_='fade', layers=[
        bg('bg_yard', grade={'sat': 0.75, 'exp': 1.05}),
        cut('m6_walk', x=620, y=1180, s=0.4, depth=0.6),
        cut('gj_quiet_whistle', x=260, y=1130, s=1.25, shadow=False, grade=WARM)],
        cam=dict(z=[1.0, 1.06]), fx=dict(bloom=0.35, notes=[(w(22, 'every') + 0.1, 520, 560, 40)])))
    S.append(dict(id='memory15', t0=w(22, 'you'), in_='fade', layers=[
        bg('bg_yard', grade=DUSK),
        cut('m15_walk', x=650, y=1190, s=0.4, depth=0.6, flip=True),
        cut('gj_quiet_whistle', x=260, y=1130, s=1.25, shadow=False, grade=DUSK)],
        cam=dict(z=[1.04, 1.1]), fx=dict(bloom=0.3, notes=[(w(22, 'you') + 0.1, 520, 560, 36)])))
    # 24 · "Just quiet enough that you wouldn't hear."
    S.append(dict(id='final', t0=line(23), in_='fade', layers=[
        bg('bg_porch', blur=16),
        cut('gj_final', x=540, y=1000, s=1.3, shadow=False, grade=WARM)],
        cam=dict(z=[1.0, 1.1], fy=-250, ease='linear'), fx=dict(bloom=0.3)))
    # 25 · tail: back to the porch frame so the Short loops
    S.append(dict(id='loop', t0=L[-1]['end'] + 0.35, in_='fade', layers=[
        bg('bg_porch'),
        cut('gj_whistle', x=650, y=1010, s=0.98, grade=WARM, shadow=False)],
        cam=dict(z=[1.0, 1.12], y=[0, 30], ease='in'),
        fx=dict(bloom=0.25, notes=[(L[-1]['end'] + 0.5, 470, 600, 44), (L[-1]['end'] + 0.9, 640, 700, 38)])))

    for s in S:
        if 'in_' in s:
            s['in'] = s.pop('in_')
    return S


def SFX(timing):
    L = timing['lines']
    end = L[-1]['end']
    return [
        # porch: birds + Grandpa's whistle sitting right under "two notes" / "High, then low"
        ('birds', 0.0, 1.1, dict(d=10.8)),
        ('whistle', w(1, 'high') - 0.05, 1.3, dict()),
        ('whoosh', line(2) - 0.15, 0.6, dict(d=0.35)),
        ('whistle', L[2]['end'] - 0.05, 0.9, dict(kid=True)),
        ('whoosh', line(4) - 0.15, 0.6, dict(d=0.35)),
        ('laugh', w(4, 'laughed') - 0.1, 0.55, dict(d=1.8)),
        ('whistle', w(4, 'whistled') - 0.05, 0.5, dict(kid=True, notes=[(1500, 0.22), (1000, 0.3)])),
        ('whoosh', line(6) - 0.15, 0.6, dict(d=0.35)),
        ('impact', w(6, 'dog'), 0.35, dict()),
        ('wind', line(7), 0.25, dict(d=2.8, strength=0.2, a=0.3)),
        # snow
        ('riser', line(9) - 0.9, 0.5, dict(d=0.9)),
        ('impact', line(9), 0.5, dict()),
        ('wind', line(9), 0.45, dict(d=5.2, strength=0.4)),
        ('carve', w(9, 'snowboarding') - 0.1, 0.8, dict(d=1.1)),
        ('whoosh', w(9, 'cut') - 0.15, 0.7, dict(d=0.4)),
        ('carve', w(9, 'trail'), 0.6, dict(d=0.8)),
        ('wind', line(10), 0.8, dict(d=5.2, strength=0.9, a=1.5)),
        ('beeps', w(11, 'died'), 0.6, dict()),
        ('wind', line(12), 0.7, dict(d=2.5, strength=1.0, a=0.2)),
        ('whoosh', line(12) - 0.15, 0.6, dict(d=0.4, lo=150, hi=2000)),
        ('radio', line(13) + 0.1, 0.45, dict(d=2.6)),
        ('tick', w(13, 'six') - 0.3, 0.6, dict()),
        ('tick', w(13, 'six'), 0.6, dict()),
        ('tick', w(13, 'hours'), 0.6, dict()),
        ('tick', w(13, 'found'), 0.6, dict()),
        ('wind', line(14), 0.35, dict(d=10, strength=0.5, a=1.0)),
        ('heartbeat', line(14), 1.6, dict(d=w(14, 'heard') - line(14) + 0.3)),
        # the whistle in the fog: far, then he answers, then closer
        ('whistle', w(15, 'high') - 0.05, 2.2, dict(dist=0.8)),
        ('whistle', w(16, 'back') - 0.1, 1.2, dict(weak=True)),
        ('whistle', w(17, 'high') - 0.05, 1.8, dict(dist=0.4)),
        ('crunch', w(17, 'again'), 0.9, dict(n=4, gap=0.38, g0=0.3)),
        ('riser', line(18) - 0.6, 0.5, dict(d=0.8)),
        ('click', w(18, 'flashlight'), 0.9, dict()),
        ('impact', w(18, 'hit'), 0.8, dict()),
        ('whoosh', line(19) - 0.1, 0.5, dict(d=0.4)),
        ('wind', line(19), 0.3, dict(d=3.2, strength=0.5)),
        ('fire', line(20), 0.5, dict(d=2.5)),
        ('impact', w(20, 'didn') - 0.15, 0.45, dict()),
        ('engine', line(21) - 0.2, 0.45, dict(d=3.3)),
        ('birds', line(22) + 1.5, 0.7, dict(d=6)),
        # tail: one last quiet whistle as it loops back to the porch
        ('whistle', end + 0.45, 1.4, dict(dist=0.3)),
    ]


def MUSIC(timing):
    return [
        (0.0, 'warm'),
        (line(5), 'sad'),
        (line(7), 'hold'),
        (line(9), 'tension'),
        (line(14), 'suspense'),
        (line(19), 'swell'),
        (line(23) - 0.1, 'out'),
    ]
