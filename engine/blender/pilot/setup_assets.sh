#!/usr/bin/env bash
# Downloads every free asset the pilot uses into ./_cache and installs the MakeHuman packs for MPFB.
# All packs below are CC0 (MakeHuman), CC0 (Poly Haven) or free-to-use (CMU mocap).
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p _cache/mpfb _cache/cmu
B=https://files2.makehumancommunity.org
for f in asset_packs/makehuman_system_assets/makehuman_system_assets_cc0.zip functional/faceunits01.zip functional/visemes01.zip \
         asset_packs/hair01/hair01_cc0.zip asset_packs/eyebrows01/eyebrows01_cc0.zip asset_packs/eyelashes01/eyelashes01_cc0.zip \
         asset_packs/cartoon01/cartoon01_cc0.zip asset_packs/shirts01/shirts01_cc0.zip asset_packs/pants01/pants01_cc0.zip \
         asset_packs/shoes01/shoes01_cc0.zip; do
  [ -f "_cache/mpfb/$(basename $f)" ] || curl -sL -o "_cache/mpfb/$(basename $f)" "$B/$f"
done
for p in 002/02_01 016/16_15; do curl -sL -o "_cache/cmu/$(basename $p).bvh" "https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/master/data/$p.bvh"; done
echo "Now install MPFB 2 from Blender > Preferences > Get Extensions, then unzip _cache/mpfb/*.zip into the MPFB user data dir"
echo "(Blender > MPFB > System > Data directories shows the path)."
