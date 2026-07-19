#!/usr/bin/env python3
"""Download trip photos from Wikimedia at 960px (fallback 1280), throttled."""
import os, sys, time, urllib.request

B = "https://upload.wikimedia.org/wikipedia/commons/thumb/"
IMGS = {
 "sargan":      "9/9a/Sargan_Eight_-_Mokra_Gora_station_3.jpg",
 "drvengrad":   "c/c7/Drvengrad.jpg",
 "visegrad":    "c/c9/Mehmed_Pa%C5%A1a_Sokolovi%C4%87_Bridge%2C_Vi%C5%A1egrad.JPG",
 "andricgrad":  "5/5e/Andri%C4%87grad_ulica_Mlade_Bosne.JPG",
 "sebilj":      "1/1d/Sarajevo_Bascarsija_Sebilj_2007-08-16_%287%29.jpg",
 "kafa":        "f/fe/Set_za_kafu_03.jpg",
 "panorama":    "3/37/Sarajevo_Panorama_2011-09-27.JPG",
 "zuta":        "a/af/%C5%BDuta_Tabija%2C_Sarajevo.jpg",
 "bob":         "7/76/Sarajevo_%E2%80%93_Bob_staza_%282017%29_1.jpg",
 "kazandziluk": "8/8b/Kazandziluk_02.jpg",
 "tunnel":      "d/d4/Buried_Within_These_Walls_%28207106961%29.jpeg",
 "bijela":      "8/87/Bijela_Tabija%2C_Sarajevo_03.jpg",
 "plateau":     "9/9c/Bjela%C5%A1nica_plateau.jpg",
 "studeni":     "8/8a/Studeni_Polje_-_Umoljani.jpg",
 "dzamija":     "d/d6/Umoljani_%E2%80%93_d%C5%BEamija_2.jpg",
 "lukomir_v":   "c/c8/Lukomir_Village_%283886707753%29.jpg",
 "approach":    "2/20/Approach_to_Lukomir_%283886704127%29.jpg",
 "haystacks":   "2/2c/Haystacks_in_Lukomir_%283887503164%29.jpg",
 "blick":       "1/14/Blick_Richtung_Rakitinica-Canyon_von_Studeni_Polje_-_Umoljani.jpg",
 "konjic":      "1/15/Konjic_and_its_Stara_%C4%86uprija%2C_Old_Bridge.jpg",
 "boracko":     "8/82/Boracko_jezero.JPG",
 "prenj":       "1/1e/Prenj_s_Bjela%C5%A1nice.jpg",
 "bunker":      "4/4d/Room_inside_ARK_bunker_in_Konjic.jpg",
 "boracko2":    "0/07/DSCN2574_Bora%C4%8Dko_jezero.jpg",
 "mostar_pan":  "d/d7/Mostar_Old_Town_Panorama_2007.jpg",
 "diver":       "8/83/Mostar_Stari_Most_diver_2010.jpg",
 "blagaj":      "2/2b/Blagaj_%E2%80%93_Vrelo_Bune_3.jpg",
 "kujundziluk": "5/50/Kujundziluk_Mostar_09.jpg",
}

os.makedirs("raw", exist_ok=True)
fails = []
for key, path in IMGS.items():
    out = f"raw/{key}.jpg"
    if os.path.exists(out) and os.path.getsize(out) > 10000:
        print("skip", key); continue
    fname = path.rsplit("/", 1)[1]
    got = False
    for width in (960, 1280):
        url = f"{B}{path}/{width}px-{fname}"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (BosniaTripPlanner personal)"})
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                data = r.read()
            open(out, "wb").write(data)
            print(f"ok {key} {width}px {len(data)//1024}KB")
            got = True
            break
        except Exception as e:
            print(f"  try{width} {key}: {e}")
            time.sleep(6)
    if not got:
        fails.append(key)
    time.sleep(4)
print("FAILS:", fails or "none")
