import json,urllib.request,os,sys
op=urllib.request.build_opener(); op.addheaders=[('User-Agent','MiloPipeline/1.0')]; urllib.request.install_opener(op)
def get(u): return json.load(urllib.request.urlopen(u))
def dl(u,p):
    os.makedirs(os.path.dirname(p) or '.',exist_ok=True)
    if not os.path.exists(p): urllib.request.urlretrieve(u,p)
for m in ['Sofa_01','CoffeeTable_01','Rockingchair_01','potted_plant_01','Lantern_01','book_encyclopedia_set_01','WoodenTable_01']:
    try:
        f=get(f'https://api.polyhaven.com/files/{m}')['gltf']['2k']['gltf']
        dl(f['url'],f'{m}/{m}.gltf')
        for rel,inc in f.get('include',{}).items(): dl(inc['url'],f'{m}/{rel}')
        print('ok',m)
    except Exception as e: print('fail',m,e)
for t in ['wood_floor_deck','painted_plaster_wall','laminate_floor_02','beige_wall_001']:
    try:
        f=get(f'https://api.polyhaven.com/files/{t}')
        for mp in ['Diffuse','nor_gl','Rough']:
            if mp in f: dl(f[mp]['2k']['jpg']['url'],f'tex/{t}_{mp}.jpg')
        print('ok',t)
    except Exception as e: print('fail',t,e)
for h in ['lebombo','brown_photostudio_02','st_fagans_interior','entrance_hall']:
    try:
        dl(get(f'https://api.polyhaven.com/files/{h}')['hdri']['2k']['hdr']['url'],f'hdri/{h}_2k.hdr'); print('ok',h)
    except Exception as e: print('fail',h,e)
