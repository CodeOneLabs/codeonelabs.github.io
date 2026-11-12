#!/usr/bin/env python3
"""Builds the BeatBound song wiki at beatbound/wiki/ (Korean).

Reads the game's own data from the BeatBound Unity project, so the numbers match the build:
  - Songs/*.asset            title, artist, city, BPM
  - Analysis/*.json          genre (grooveType)
  - SongIdentities.json      sound basis, motif, 8x8 LED picture
  - SectionNames.json        named song parts
  - FeverRanges.json         FEVER highlight
  - Charts/*.json            notes (blasts) per tier
  - ChartLevelTable.asset    internal levels (rating values)
  - RankCalibration.json     1,000,000-point reference per chart
  - CertificationCatalog.cs  STEP UP courses
  - StarterCourses.cs        first-run starter courses

Run: python3 tools/build_beatbound_wiki.py [path/to/BeatBound]
"""
import html
import json
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "beatbound" / "wiki"
BB = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "Downloads" / "BeatBound"
GD = BB / "Assets" / "Resources" / "GameData"
SCRIPTS = BB / "Assets" / "Scripts"
SITE = "https://memegames.dev/beatbound/wiki"

# ---------------------------------------------------------------- game constants (mirrors C#)
# ERuleSet stored numbers: Normal=0 Perfect=1 Extreme=2 Hard=3 Easy=4
TIERS = [  # (key, label, rule number, chart suffix)
    ("easy", "EASY", 4, ".beginner"),
    ("normal", "NORMAL", 0, ".easy"),
    ("hard", "HARD", 3, ".normal"),
    ("extreme", "EXTREME", 2, ""),
]
TIER_LABEL = {4: "EASY", 0: "NORMAL", 3: "HARD", 2: "EXTREME", 1: "PERFECT"}
TIER_COLOR = {"easy": "#5fd38a", "normal": "#5cb8ff", "hard": "#ffb547", "extreme": "#ff5c8a"}
LEAD_SECONDS = {4: 1.3, 0: 1.3, 3: 1.0}
CITY_ORDER = ["BERLIN", "DETROIT", "SÃO PAULO", "TOKYO", "DELHI", "SEOUL", "JAKARTA", "SAPPORO",
              "NEO AKIBA", "SKY SEONGSU", "LOS ANGELES"]
CITY_FILE = {0: "Berlin", 1: "Detroit", 2: "SaoPaulo", 3: "Tokyo", 4: "Delhi", 5: "Seoul", 6: "Jakarta",
             7: "Sapporo", 8: "NeoAkiba", 9: "NeoSeongsu", 10: "LosAngeles"}
DLC_CITIES = {6, 7, 8}
RAW_UNIT = 50
MAX_SCORE = 1_000_000
CUTS = [("SSS++", 980000), ("SSS+", 950000), ("SSS", 900000), ("SS++", 875000), ("SS+", 850000), ("SS", 800000),
        ("S++", 775000), ("S+", 750000), ("S", 700000), ("A++", 675000), ("A+", 650000), ("A", 600000),
        ("B++", 575000), ("B+", 550000), ("B", 500000), ("C++", 475000), ("C+", 450000), ("C", 400000),
        ("D++", 300000), ("D+", 200000), ("D", 0)]
RATING_TIERS = [("BRONZE I", 0), ("BRONZE II", 1), ("BRONZE III", 2), ("SILVER I", 3), ("SILVER II", 4),
                ("SILVER III", 5), ("GOLD I", 6), ("GOLD II", 6.33), ("GOLD III", 6.66), ("PLATINUM I", 7),
                ("PLATINUM II", 7.33), ("PLATINUM III", 7.66), ("EMERALD I", 8), ("EMERALD II", 8.33),
                ("EMERALD III", 8.66), ("DIAMOND I", 9), ("DIAMOND II", 9.33), ("DIAMOND III", 9.66), ("MASTER", 10)]
TIER_COLORS = {"BRONZE": "#cc8040", "SILVER": "#c2ccde", "GOLD": "#ffc738", "PLATINUM": "#73ebe0",
               "EMERALD": "#3de680", "DIAMOND": "#7aadff", "MASTER": "#ff4dc7"}
AIM_CELLS = {1: 1, 2: 8, 3: 8, 4: 15, 5: 9, 6: 15}
GRADE_NAME = {"SSS": "SSS", "SS": "SS", "S": "S", "A": "A", "B": "B", "C": "C", "D": "D", "F": "F"}

# Korean text for the public wiki. SongIdentities.json mixes audio notes with production notes; only these are shown.
SOUND_KO = {
    "berlin1": "어두운 포온더플로어. 밝기가 낮고, 천천히 쌓아 올려 늦게 터진다.",
    "berlin2": "어두운 포온더플로어. 낮은 음역이 꾸준히 밀어붙인다.",
    "berlin3": "어두운 포온더플로어. 일찍 본론에 들어가 에너지를 오래 유지한다.",
    "detroit1": "빠르고 어두운 포온더플로어. 드롭이 여러 번 오고 브레이크와의 대비가 크다.",
    "detroit2": "밝은 주크/풋워크. 고음이 밝고 짧은 리듬 악센트가 많다.",
    "detroit3": "밝고 곧게 달리는 곡. 깊은 브레이크 뒤에 빽빽한 클라이맥스가 온다.",
    "detroit4": "아주 어두운 음색. 빌드와 드롭이 반복된다.",
    "detroit5": "어두운 주크/풋워크. 끊어지는 빠른 그루브, 드롭과 브레이크가 번갈아 온다.",
    "saopaolo1": "따뜻한 브로큰 비트. 둥근 그루브에 후반으로 갈수록 에너지가 오른다.",
    "saopaolo2": "따뜻한 바일리/탐보르장. 엇박 타악기와 반복해서 솟는 구간.",
    "saopaolo3": "따뜻한 포온더플로어. 바로 드롭에 들어가 끝까지 에너지를 유지한다.",
    "saopaolo4": "어둡고 곧은 그루브. 아주 낮은 밝기에 에너지가 여러 번 몰아친다.",
    "saopaolo5": "어두운 바일리/탐보르장. 전곡 중 가장 어두운 음색, 엇박 저음 그루브.",
    "tokyo1": "따뜻한 브로큰 비트. 드롭이 반복되고 사이 브레이크가 넓다.",
    "tokyo2": "따뜻한 주크/풋워크. 비슷한 빠르기의 곡들보다 어두운 음색.",
    "tokyo3": "따뜻한 주크/풋워크. 비교적 밝은 디테일, 중간에 깊은 브레이크.",
    "tokyo5": "밝은 브로큰 비트. 고음이 밝고 브레이크 대비가 크다.",
}
MOTIF_KO = {
    "null sign Ø": "공집합 기호 Ø", "signal waves": "신호 파동", "capsule pill": "캡슐 알약", "fireball streak": "불덩이 꼬리",
    "fast-forward >>": "빨리감기 >>", "water drop": "물방울", "speaker cabinet": "스피커", "trash can": "쓰레기통",
    "party balloons": "파티 풍선", "flame": "불꽃", "sun": "태양", "storm cloud": "폭풍 구름", "microphone": "마이크",
    "umbrella": "우산", "flowing ribbon": "흐르는 리본", "sparkles": "반짝이", "nova burst": "신성 폭발",
    "saffron crocus": "사프란 꽃", "damaru drum": "다마루 북", "peacock fan": "공작 깃", "yantra": "얀트라",
    "ghost": "유령", "cake pop": "케이크 팝", "cotton candy": "솜사탕", "dice five": "주사위 5",
    "surprised face :O": "놀란 얼굴 :O", "heartbeat line": "심전도", "arcade boss": "아케이드 보스",
    "bonang kettle gongs": "보낭 공", "segmented bamboo": "대나무 마디", "hanging gong": "걸린 징",
    "chanters around a fire": "불가에 둘러앉은 합창", "speaker stack": "스피커 더미", "guruguru spiral": "빙글빙글 소용돌이",
    "clock at four": "4시 시계", "TV with play button": "재생 버튼 TV", "gacha capsule": "가챠 캡슐", "moe heart": "하트",
    "snowflake": "눈송이", "wind chevrons": "바람 화살표", "neon skyline": "네온 스카이라인",
    "crescent moon with an unread dot": "초승달과 안 읽은 알림 점", "speed gauge": "속도계", "festival shrine": "축제 신사",
    "three bursts of colored powder": "색 가루 세 번", "split waveform eye": "갈라진 파형 눈", "paired heartbeat peaks": "두 심박 봉우리",
    "volcano and staggered lava stream": "화산과 흘러내리는 용암", "banana peel": "바나나 껍질", "soap bubbles": "비눗방울",
    "hourglass": "모래시계", "snowman": "눈사람", "sun under the horizon": "지평선 아래 해",
    "bouncing cube over its shadow": "그림자 위로 튀는 큐브", "palm tree": "야자수", "pier ferris wheel": "부두 관람차",
}


def fmt_bpm(bpm):
    return f"{bpm:.0f}" if abs(bpm - round(bpm)) < 0.05 else f"{bpm:.1f}"


def e(s):
    return html.escape(str(s), quote=True)


def unit_for(raw_ref):
    if raw_ref <= 0:
        return RAW_UNIT
    exact = (RAW_UNIT * MAX_SCORE + raw_ref - 1) // raw_ref
    return max(5, (exact + 4) // 5 * 5)


def hit_budget(blasts, rule):
    if rule == 1:
        return 1
    per_mille = 42 if rule == 4 else 30
    return max(1, blasts * per_mille // 1000)


def display_level(internal):
    return max(1, min(12, math.floor(internal + 0.5)))


def fmt_time(sec):
    s = int(round(max(0, sec)))
    return f"{s // 60}:{s % 60:02d}"


# ---------------------------------------------------------------- loading
def yaml_field(text, name):
    m = re.search(rf"^\s*{name}: (.*)$", text, re.M)
    if not m:
        return None
    v = m.group(1).strip()
    if v.startswith('"') and v.endswith('"'):
        v = v[1:-1].encode("ascii", "backslashreplace").decode("unicode_escape")
    return v


def load_cities():
    cities = {}
    for num, name in CITY_FILE.items():
        t = (GD / "Themes" / f"{name}.asset").read_text(encoding="utf-8")
        acc = re.search(r"accent: \{r: ([\d.]+), g: ([\d.]+), b: ([\d.]+)", t)
        color = "#%02x%02x%02x" % tuple(int(float(x) * 255 + .5) for x in acc.groups())
        cities[num] = dict(num=num, name=yaml_field(t, "displayName"), tagline=yaml_field(t, "tagline") or "",
                           color=color, slug=name.lower(), dlc=num in DLC_CITIES)
    return cities


def load_levels():
    txt = (GD / "ChartLevelTable.asset").read_text(encoding="utf-8")
    levels = {}
    for s, t, lv in re.findall(r"songId: (\S+)\n\s+tier: (\d)\n\s+fingerprint: \S+\n\s+internalLevel: (\S+)", txt):
        levels[(s, int(t))] = float(lv)
    return levels


def load_courses():
    src = (SCRIPTS / "Certification" / "CertificationCatalog.cs").read_text(encoding="utf-8")
    src = src.split("#else", 1)[1].split("#endif", 1)[0]
    courses = []
    for m in re.finditer(r'Course\("(\w+)", "(\w+)", ([\d.]+)f,(.*?\))\),', src, re.S):
        stages = []
        for sm in re.finditer(r'Stage\("(\w+)", ERuleSet\.(\w+)(?:, EGrade\.(\w+))?(?:, (\d))?\)', m.group(4)):
            stages.append(dict(song=sm.group(1), rule=sm.group(2).upper(), grade=sm.group(3),
                               plus=int(sm.group(4) or 0)))
        courses.append(dict(id=m.group(1), title=m.group(2), bonus=float(m.group(3)), stages=stages))
    return courses


def load_starters():
    src = (SCRIPTS / "Gameplay" / "Play" / "StarterCourses.cs").read_text(encoding="utf-8")
    src = src.split("#else", 1)[1].split("#endif", 1)[0]
    out = []
    for m in re.finditer(r'ETutorialPickBand\.(\w+), "([^"]+)",(.*?\))\),', src, re.S):
        steps = [dict(rule=sm.group(1).upper(), songs=re.findall(r'"(\w+)"', sm.group(2)))
                 for sm in re.finditer(r'StarterStep\(ERuleSet\.(\w+), ([^)]*)\)', m.group(3))]
        out.append(dict(band=m.group(1), title=m.group(2), steps=steps))
    return out


def chart_stats(chart):
    """Per-chart note statistics from the chart JSON (fixed cells exactly; aim/hole blasts estimated)."""
    bpm = chart["bpm"]
    step = 30.0 / max(1.0, bpm)
    first = chart["firstBeat"]
    bars = chart["totalBars"]
    bt = chart.get("barTimes") or []
    mapped = len(bt) == bars + 1

    def tick_time(tick):
        if mapped:
            b = tick / 16.0
            i = min(int(b), bars - 1)
            return bt[i] + (bt[i + 1] - bt[i]) * (b - i)
        return first + tick * step * 0.5

    ticks = defaultdict(list)
    for h in chart["hits"]:
        ticks[h["step"] * 2 + (1 if h.get("sub", 0) > 0 else 0)].append(h)
    heat = [0] * 64
    per_bar = [0] * bars
    cells_total = 0
    hole_ticks = aim_ticks = off_ticks = 0
    for tick, hs in ticks.items():
        mask = 0
        hole = 0
        aim = 0
        for h in hs:
            mask |= int(h.get("cells", "0") or "0", 16)
            if h.get("holeSize", 0) > 0:
                hole = max(hole, h["holeSize"])
            if h.get("aim", 0):
                aim += AIM_CELLS.get(h["aim"], 1)
        if hole:
            n = 64 - hole * hole
            hole_ticks += 1
        else:
            n = min(64, bin(mask).count("1") + aim)
            if aim:
                aim_ticks += 1
        cells_total += n
        for c in range(64):
            if mask >> c & 1:
                heat[c] += 1
        if tick % 2:
            off_ticks += 1
        b = tick // 16
        if 0 <= b < bars:
            per_bar[b] += 1
    count = len(ticks)
    end = bt[-1] if mapped else first + bars * 8 * step
    start = tick_time(min(ticks)) if ticks else first
    play = max(1.0, end - first)
    bar_sec = [(bt[i + 1] - bt[i]) if mapped else 8 * step for i in range(bars)]
    # densest 4-bar window
    best = (0, 0.0)
    for i in range(max(1, bars - 3)):
        n = sum(per_bar[i:i + 4])
        sec = sum(bar_sec[i:i + 4]) or 1
        if n / sec > best[1]:
            best = (i, n / sec)
    return dict(blasts=count, nps=count / play, cells=cells_total / max(1, count), sixteenth=off_ticks / max(1, count),
                hole=hole_ticks / max(1, count), aim=aim_ticks / max(1, count), heat=heat, per_bar=per_bar,
                bar_sec=bar_sec, peak_bar=best[0], peak_nps=best[1], end=end, first=first, start=start,
                lead=chart.get("leadSteps", 4), step=step, groups=chart.get("groups", []), bars=bars)


def lead_steps(base_lead, step, rule):
    target = LEAD_SECONDS.get(rule)
    if not target:
        return base_lead
    best, err = base_lead, 1e9
    for s in range(2, 17, 2):
        d = abs(s * step - target)
        if d < err:
            err, best = d, s
    return max(base_lead, best)


def load_songs(cities, levels):
    analysis = {p.stem: json.loads(p.read_text(encoding="utf-8")) for p in (GD / "Analysis").glob("*.json")}
    ident = {s["id"]: s for s in json.loads((GD / "SongIdentities.json").read_text(encoding="utf-8"))["songs"]}
    parts = {s["id"]: s["parts"] for s in json.loads((GD / "SectionNames.json").read_text(encoding="utf-8"))["songs"]}
    fever = {s["songId"]: s["ranges"] for s in json.loads((GD / "FeverRanges.json").read_text(encoding="utf-8"))["songs"]}
    calib = {(c["songId"], c["rule"]): c for c in json.loads((GD / "RankCalibration.json").read_text(encoding="utf-8"))["entries"]}
    songs = []
    for p in sorted((GD / "Songs").glob("*.asset")):
        t = p.read_text(encoding="utf-8")
        sid = yaml_field(t, "id")
        rows = re.findall(r"^\s+- '?(\d{8})'?$", t.split("identityRows:", 1)[1].split("artist:", 1)[0], re.M)
        song = dict(id=sid, title=yaml_field(t, "title"), tagline=yaml_field(t, "tagline") or "",
                    artist=yaml_field(t, "artist") or "", city=int(yaml_field(t, "city")),
                    number=int(yaml_field(t, "number")), bpm=float(yaml_field(t, "bpm")),
                    duration=float(yaml_field(t, "duration")), rows=rows)
        a = analysis.get(sid, {})
        song["genre"] = a.get("grooveType") or ""
        i = ident.get(sid, {})
        song["basis"] = SOUND_KO.get(sid, "")
        song["motif"] = MOTIF_KO.get(i.get("motif", ""), i.get("motif", ""))
        song["parts"] = parts.get(sid, [])
        song["fever"] = fever.get(sid, [])
        base = json.loads((GD / "Charts" / f"{sid}.json").read_text(encoding="utf-8"))
        song["tiers"] = {}
        for key, label, rule, suffix in TIERS:
            path = GD / "Charts" / f"{sid}{suffix}.json"
            chart = json.loads(path.read_text(encoding="utf-8")) if path.exists() else base
            st = chart_stats(chart)
            internal = levels.get((sid, rule))
            c = calib.get((sid, rule), {})
            blasts = c.get("totalBlasts", st["blasts"])
            ref = c.get("sssPlusPlus", 0)
            u = unit_for(ref)
            ls = lead_steps(base.get("leadSteps", 4), 30.0 / max(1.0, base["bpm"]), rule)
            st.update(internal=internal, level=display_level(internal) if internal else None, blasts=blasts,
                      ref=ref, unit=u, max_near=c.get("maxNear"), near_fever=c.get("maxNearInFever"),
                      baseline=c.get("baseline"), budget=hit_budget(blasts, rule), lead_sec=ls * st["step"],
                      perfect_budget=1)
            song["tiers"][key] = st
        x = song["tiers"]["extreme"]
        song["play"] = x["end"] - x["first"]
        songs.append(song)
    songs.sort(key=lambda s: (s["city"], s["number"]))
    return songs


# ---------------------------------------------------------------- rendering helpers
CSS = """
:root{color-scheme:dark;--bg:#0c0b12;--face:#16141f;--face2:#1d1a29;--line:#2c2840;--ink:#f3ecdc;--muted:#a49cb8;--dim:#6f6886;
--accent:#ff5cc0;--sans:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR","Segoe UI",sans-serif;
--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.65 var(--sans)}
a{color:inherit;text-decoration-color:#ffffff40;text-underline-offset:3px}a:hover{text-decoration-color:currentColor}
.top{position:sticky;top:0;z-index:5;background:#0c0b12ee;backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.top .in{max-width:1080px;margin:0 auto;padding:0 16px;height:54px;display:flex;align-items:center;gap:18px;overflow-x:auto;white-space:nowrap}
.brand{font-weight:800;letter-spacing:.08em;text-decoration:none;font-size:14px}.brand b{color:var(--accent)}
.top nav{display:flex;gap:4px;margin-left:auto}.top nav a{text-decoration:none;color:var(--muted);font-size:14px;padding:6px 10px;border-radius:8px}
.top nav a:hover,.top nav a.on{color:var(--ink);background:var(--face2)}
main{max-width:1080px;margin:0 auto;padding:28px 16px 64px}
h1{font-size:30px;line-height:1.2;margin:4px 0 6px;letter-spacing:-.01em}h2{font-size:20px;margin:40px 0 12px;padding-top:4px}
h3{font-size:16px;margin:24px 0 8px}p{margin:8px 0}.lead{color:var(--muted);max-width:720px}
.eyebrow{font:700 12px var(--mono);letter-spacing:.14em;color:var(--muted);text-transform:uppercase}
.card{background:var(--face);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:12px 0}
.grid{display:grid;gap:12px}.g2{grid-template-columns:repeat(auto-fit,minmax(260px,1fr))}.g4{grid-template-columns:repeat(auto-fit,minmax(220px,1fr))}
.tw{overflow-x:auto;margin:10px 0;border:1px solid var(--line);border-radius:12px}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:8px 10px;text-align:left;border-bottom:1px solid var(--line);white-space:nowrap}
th{font-weight:600;color:var(--muted);background:var(--face);font-size:12.5px;position:sticky;top:0}
tbody tr:last-child td{border-bottom:0}td.n,th.n{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums}
tbody tr:hover{background:#ffffff06}
.chip{display:inline-block;font:700 11px/1 var(--mono);letter-spacing:.06em;padding:5px 7px 4px;border-radius:6px;border:1px solid currentColor;vertical-align:middle;white-space:nowrap}
.lv{display:inline-block;min-width:28px;text-align:center;font:700 13px/1 var(--mono);padding:5px 6px 4px;border-radius:6px;background:var(--face2);border:1px solid currentColor}
.mut{color:var(--muted)}.dim{color:var(--dim)}.small{font-size:13px}.mono{font-family:var(--mono)}
.kv{display:grid;grid-template-columns:max-content 1fr;gap:4px 16px;margin:0}.kv dt{color:var(--muted)}.kv dd{margin:0}
.hero{display:flex;gap:22px;align-items:center;flex-wrap:wrap}.led{flex:none;display:grid;grid-template-columns:repeat(8,1fr);gap:3px;width:136px;height:136px;padding:8px;background:#07060b;border-radius:12px;border:1px solid var(--line)}
.led i{border-radius:3px;background:#1a1726}
.filters{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0}.filters button{font:600 12.5px var(--sans);color:var(--muted);background:var(--face);border:1px solid var(--line);border-radius:999px;padding:6px 12px;cursor:pointer}
.filters button.on{color:var(--ink);border-color:var(--ink)}
input.search{width:100%;max-width:320px;font:15px var(--sans);color:var(--ink);background:var(--face);border:1px solid var(--line);border-radius:10px;padding:9px 12px}
th.sort{cursor:pointer;user-select:none}th.sort:after{content:" ↕";color:var(--dim)}
.formula{font:14px/1.7 var(--mono);background:#07060b;border:1px solid var(--line);border-radius:12px;padding:14px 16px;overflow-x:auto;white-space:pre}
.bars{display:flex;align-items:flex-end;gap:1px;height:56px;margin:6px 0 2px}.bars i{flex:1;min-width:1px;border-radius:1px 1px 0 0}
.heat{display:grid;grid-template-columns:repeat(8,1fr);gap:2px;width:112px;height:112px}.heat i{border-radius:2px}
.tier-cards{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(240px,1fr))}
.tc h3{margin:0 0 8px;display:flex;align-items:center;gap:8px}.tc .big{font:800 26px/1 var(--mono)}
.note{border-left:3px solid var(--line);padding:2px 0 2px 12px;color:var(--muted)}
ul.plain{padding-left:18px;margin:6px 0}ul.plain li{margin:3px 0}
footer{border-top:1px solid var(--line);color:var(--dim);font-size:13px}footer .in{max-width:1080px;margin:0 auto;padding:20px 16px 40px}
@media(max-width:640px){h1{font-size:24px}.led{width:104px;height:104px;padding:6px;gap:2px}main{padding-top:20px}}
"""

NAV = [("index.html", "곡 목록"), ("rating.html", "레이팅"), ("stepup.html", "STEP UP"), ("rules.html", "점수·랭크")]


def page(rel, active, title, desc, body, script=""):
    pre = "../" if rel else ""
    nav = "".join(f'<a href="{pre}{h}"{" class=on" if h == active else ""}>{t}</a>' for h, t in NAV)
    return (f'<!doctype html><html lang="ko"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(title)} · BeatBound 위키</title><meta name="description" content="{e(desc)}">'
            f'<link rel="icon" type="image/png" href="{pre}../../assets/beatbound-icon-128.png">'
            f'<link rel="stylesheet" href="{pre}wiki.css?v={VERSION}"></head><body>'
            f'<header class="top"><div class="in"><a class="brand" href="{pre}index.html">BEAT<b>BOUND</b> WIKI</a>'
            f'<nav>{nav}</nav></div></header><main>{body}</main>'
            f'<footer><div class="in">BeatBound © 2026 MeMe Games · 게임 데이터에서 자동 생성 ({e(BUILD_DATE)}) · '
            f'레벨 평가기 {e(EVALUATOR)}</div></footer>{script}</body></html>\n')


def lv_chip(tier_key, level, internal=None):
    if level is None:
        return '<span class="dim">–</span>'
    title = f' title="내부 수치 {internal:.2f}"' if internal is not None else ""
    return f'<span class="lv" style="color:{TIER_COLOR[tier_key]}"{title}>{level}</span>'


def city_chip(city):
    return f'<span class="chip" style="color:{city["color"]}">{e(city["name"])}</span>'


def led(rows, color):
    cells = []
    alpha = {"0": None, "1": .35, "2": .65, "3": 1}
    for r in rows:
        for ch in r[:8]:
            a = alpha.get(ch)
            cells.append(f'<i style="background:{color};opacity:{a}"></i>' if a else "<i></i>")
    return f'<div class="led" aria-hidden="true">{"".join(cells)}</div>'


def heat(cells, color):
    mx = max(cells) or 1
    out = []
    for v in cells:
        a = v / mx
        out.append(f'<i style="background:{color};opacity:{.08 + .92 * a:.2f}"></i>' if v else '<i style="background:#ffffff0a"></i>')
    return f'<div class="heat" title="고정 칸이 터진 횟수 (밝을수록 많이)">{"".join(out)}</div>'


def density(per_bar, bar_sec, color, peak):
    rates = [n / s if s else 0 for n, s in zip(per_bar, bar_sec)]
    mx = max(rates) or 1
    bars = "".join(f'<i style="height:{max(2, 100 * r / mx):.0f}%;background:{color};opacity:{.95 if peak <= i < peak + 4 else .55}"></i>'
                   for i, r in enumerate(rates))
    return f'<div class="bars" title="마디별 폭발 수 (초당)">{bars}</div>'


def pct(x):
    return f"{100 * x:.0f}%"


def rating_tier(value):
    name = RATING_TIERS[0][0]
    for n, lo in RATING_TIERS:
        if value >= lo:
            name = n
    return name


def tier_color(name):
    return TIER_COLORS[name.split()[0]]


# ---------------------------------------------------------------- song notes (derived from the charts)
def chart_notes(song, key):
    t = song["tiers"][key]
    notes = []
    if t["sixteenth"] >= .2:
        notes.append(f"16분 엇박 폭발이 {pct(t['sixteenth'])}로 많다. 손이 박자 사이에도 움직여야 한다.")
    elif t["sixteenth"] < .03:
        notes.append("거의 모든 폭발이 8분 정박 위에 있다.")
    if t["hole"] >= .05:
        notes.append(f"판 전체가 터지고 빈칸만 남는 '구멍' 폭발이 {pct(t['hole'])}. 빈칸을 찾아 들어가야 한다.")
    if t["aim"] >= .05:
        notes.append(f"플레이어 위치를 겨냥하는 조준 폭발이 {pct(t['aim'])} 섞여 있다.")
    if t["cells"] >= 24:
        notes.append(f"한 번에 평균 {t['cells']:.0f}칸이 터지는 넓은 패턴 위주.")
    elif t["cells"] <= 10:
        notes.append(f"한 번에 평균 {t['cells']:.0f}칸, 가는 선과 작은 블록 위주.")
    pk = t["peak_bar"]
    sec_name = section_at(song, pk)
    notes.append(f"가장 빽빽한 곳은 {pk + 1}–{pk + 4}마디{(' (' + sec_name + ')') if sec_name else ''}, 초당 {t['peak_nps']:.1f}회.")
    return notes


def section_at(song, bar):
    name = ""
    for p in song["parts"]:
        if p["bar"] <= bar:
            name = p["name"]
    if not name:
        for g in song["tiers"]["extreme"]["groups"]:
            if g["startBar"] <= bar:
                name = g["name"]
    return name


# ---------------------------------------------------------------- pages
def song_page(song, cities, ranks, courses_by_song, starters_by_song):
    city = cities[song["city"]]
    col = city["color"]
    T = song["tiers"]
    body = [f'<p class="eyebrow"><a href="../index.html#{city["slug"]}">{e(city["name"])}</a> · {e(song["genre"])}</p>',
            '<div class="hero">', led(song["rows"], col),
            f'<div><h1>{e(song["title"])}</h1><p class="lead">{e(song["tagline"])}</p>',
            f'<p class="small mut">{e(song["artist"])} · {fmt_bpm(song["bpm"])} BPM · {fmt_time(song["play"])}',
            f'{" · DLC 팩" if city["dlc"] else ""}</p><p>',
            " ".join(f'{lv_chip(k, T[k]["level"], T[k]["internal"])}' for k, *_ in TIERS),
            '</p></div></div>']

    # features
    body.append('<h2>곡 특징</h2><div class="grid g2"><div class="card"><dl class="kv">')
    kv = [("도시", f'{city_chip(city)} <span class="mut small">{e(city["tagline"])}</span>'),
          ("장르", e(song["genre"])), ("템포", f'{fmt_bpm(song["bpm"])} BPM'),
          ("플레이 길이", f'{fmt_time(song["play"])} · {T["extreme"]["bars"]}마디'),
          ("곡 그림", f'{e(song["motif"])} (왼쪽 8×8 LED)' if song["motif"] else "–")]
    if song["basis"]:
        kv.insert(4, ("사운드", e(song["basis"])))
    body += [f"<dt>{k}</dt><dd>{v}</dd>" for k, v in kv]
    body.append('</dl></div><div class="card"><h3 style="margin-top:0">구간</h3>')
    if song["parts"]:
        body.append('<ul class="plain small">')
        bar_t = T["extreme"]
        for p in song["parts"]:
            sec = bar_t["first"] + sum(bar_t["bar_sec"][:p["bar"]])
            body.append(f'<li><span class="mono mut">{p["bar"] + 1:>3}마디 · {fmt_time(sec)}</span> {e(p["name"])}</li>')
        body.append("</ul>")
    for fv in song["fever"]:
        s, n = fv["startBar"], fv["bars"]
        body.append(f'<p class="small"><b style="color:#ffd34d">FEVER</b> {s + 1}–{s + n}마디. '
                    f'이 구간에선 근접(COOL)·JUST 점수가 두 배.</p>')
    body.append("</div></div>")

    # tier cards
    body.append('<h2>난이도별 노트</h2><p class="mut small">막대는 마디마다 초당 폭발 수(진한 부분이 가장 빽빽한 4마디), '
                '사각형은 8×8 판에서 고정 칸이 터진 횟수입니다. 조준·구멍 폭발은 플레이어 위치에 따라 바뀌어 사각형에서 뺐습니다.</p>'
                '<div class="tier-cards">')
    for key, label, rule, _ in TIERS:
        t = T[key]
        c = TIER_COLOR[key]
        rk = ranks[key].get(song["id"])
        body.append(f'<div class="card tc"><h3><span class="chip" style="color:{c}">{label}</span>'
                    f'<span class="big" style="color:{c}">Lv {t["level"]}</span>'
                    f'<span class="mono mut small" style="margin-left:auto">{t["internal"]:.2f}</span></h3>'
                    f'{density(t["per_bar"], t["bar_sec"], c, t["peak_bar"])}'
                    f'<div style="display:flex;gap:14px;align-items:flex-start;margin-top:10px">{heat(t["heat"], c)}'
                    f'<dl class="kv small"><dt>폭발</dt><dd class="mono">{t["blasts"]}</dd>'
                    f'<dt>초당</dt><dd class="mono">{t["nps"]:.2f}</dd>'
                    f'<dt>평균 칸</dt><dd class="mono">{t["cells"]:.1f}</dd>'
                    f'<dt>16분</dt><dd class="mono">{pct(t["sixteenth"])}</dd>'
                    f'<dt>예고</dt><dd class="mono">{t["lead_sec"]:.2f}s</dd></dl></div>'
                    f'<ul class="plain small mut" style="margin-top:10px">'
                    + "".join(f"<li>{e(n)}</li>" for n in chart_notes(song, key)) +
                    f'</ul><p class="small dim">{label} {len(ranks[key])}곡 중 {rk}번째로 어려움</p></div>')
    body.append("</div>")

    # rating
    body.append('<h2>레이팅 계산</h2><p class="mut">채보 한 칸의 레이팅 값 = 내부 수치 × min(1, 점수 ÷ 1,000,000). '
                '완주한 기록만 셉니다. 이 값이 내 상위 1–5위 안이면 ×1/10, 6–20위면 ×1/30으로 레이팅에 더해집니다. '
                '<a href="../rating.html">레이팅 전체 설명</a></p>')
    scores = [1000000, 980000, 950000, 900000, 800000, 700000]
    body.append('<div class="tw"><table><thead><tr><th>난이도</th><th class="n">내부 수치</th>'
                + "".join(f'<th class="n">{s // 1000}k</th>' for s in scores)
                + '<th class="n">1–5위 기여</th><th class="n">6–20위 기여</th></tr></thead><tbody>')
    for key, label, rule, _ in TIERS:
        t = T[key]
        lv = t["internal"]
        body.append(f'<tr><td><span class="chip" style="color:{TIER_COLOR[key]}">{label}</span></td>'
                    f'<td class="n">{lv:.3f}</td>'
                    + "".join(f'<td class="n">{lv * min(1, s / MAX_SCORE):.3f}</td>' for s in scores)
                    + f'<td class="n">+{lv / 10:.3f}</td><td class="n">+{lv / 30:.3f}</td></tr>')
    body.append("</tbody></table></div>")
    body.append(f'<p class="small mut">PERFECT는 EXTREME과 같은 채보에 피격 1회면 실패하는 규칙이라, EXTREME 칸에서 둘 중 높은 값을 씁니다. '
                f'100만점을 넘는 점수(JUST 보너스)도 계수는 1에서 멈춥니다.</p>')

    # score detail
    body.append('<h2>점수 배점</h2><p class="mut">곡마다 100만점이 “피격 0, 근접(COOL)을 최대로 챙기고 JUST는 하나도 없는” 최적 플레이가 되도록 '
                '단위 u를 정합니다. JUST는 100만점 위로 넘치는 보너스입니다. <a href="../rules.html">점수·랭크 규칙</a></p>')
    body.append('<div class="tw"><table><thead><tr><th>난이도</th><th class="n">폭발</th><th class="n">단위 u</th>'
                '<th class="n">피함 3u</th><th class="n">COOL·JUST u</th><th class="n">BONUS 20u</th><th class="n">피격 −10u</th>'
                '<th class="n">최대 COOL</th><th class="n">FEVER 안</th><th class="n">피격 허용</th></tr></thead><tbody>')
    for key, label, rule, _ in TIERS:
        t = T[key]
        u = t["unit"]
        body.append(f'<tr><td><span class="chip" style="color:{TIER_COLOR[key]}">{label}</span></td>'
                    f'<td class="n">{t["blasts"]}</td><td class="n">{u}</td><td class="n">{3 * u}</td><td class="n">{u}</td>'
                    f'<td class="n">{20 * u}</td><td class="n">−{10 * u}</td><td class="n">{t["max_near"] or "–"}</td>'
                    f'<td class="n">{t["near_fever"] if t["near_fever"] is not None else "–"}</td>'
                    f'<td class="n">{t["budget"]}</td></tr>')
    body.append("</tbody></table></div>")
    x = T["extreme"]
    body.append(f'<p class="small mut">피격 허용은 연속으로 맞아도 버티는 횟수입니다(EASY 4.2%, 나머지 3%, PERFECT 1회). '
                f'EXTREME 기준: 원점수 100만 기준 {x["ref"]:,} = 폭발·BONUS {x["baseline"]:,} + 50 × (COOL {x["max_near"]} + FEVER 안 COOL {x["near_fever"]}).</p>')

    # courses
    extra = []
    for c, i, st in courses_by_song.get(song["id"], []):
        need = f' · {st["grade"]}{"+" * st["plus"]} 이상' if st["grade"] else " · 클리어"
        extra.append(f'<li><a href="../stepup.html#{c["id"]}">STEP UP {e(c["title"])}</a> {i + 1}번째 곡 · {st["rule"]}{need}</li>')
    for s, i, st in starters_by_song.get(song["id"], []):
        extra.append(f'<li><a href="../stepup.html#starter-{s["band"].lower()}">스타터 {e(s["title"])}</a> {i + 1}단계 · {st["rule"]}</li>')
    if extra:
        body.append('<h2>코스</h2><ul class="plain">' + "".join(extra) + "</ul>")

    prev_next = NEIGHBOURS[song["id"]]
    body.append('<p style="margin-top:40px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap" class="small">'
                + (f'<a href="{prev_next[0]["id"]}.html">← {e(prev_next[0]["title"])}</a>' if prev_next[0] else "<span></span>")
                + (f'<a href="{prev_next[1]["id"]}.html">{e(prev_next[1]["title"])} →</a>' if prev_next[1] else "")
                + "</p>")
    desc = f'{song["title"]} ({city["name"]}, {fmt_bpm(song["bpm"])} BPM) — 난이도별 노트, 레이팅 값, 점수 배점.'
    return page(True, "index.html", song["title"], desc, "".join(body))


def index_page(songs, cities):
    body = ['<p class="eyebrow">BeatBound Wiki</p><h1>곡 목록</h1>',
            f'<p class="lead">BeatBound에 들어 있는 {len(songs)}곡, {len(cities)}개 도시. 곡마다 난이도별 노트 특징, '
            '레이팅에 들어가는 내부 수치, 점수 배점을 정리했습니다. 숫자는 모두 게임 데이터에서 그대로 뽑았습니다.</p>',
            '<div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:18px">'
            '<input class="search" id="q" type="search" placeholder="곡, 장르 검색" aria-label="곡 검색"></div>',
            '<div class="filters" id="cities"><button class="on" data-c="">전체</button>']
    for c in cities.values():
        body.append(f'<button data-c="{c["slug"]}" id="{c["slug"]}">{e(c["name"])}</button>')
    body.append('</div><div class="tw"><table id="songs"><thead><tr>'
                '<th class="sort" data-k="t">곡</th><th class="sort" data-k="c">도시</th><th>장르</th>'
                '<th class="sort n" data-k="b">BPM</th><th class="sort n" data-k="l">길이</th>'
                + "".join(f'<th class="sort n" data-k="{k}">{lbl}</th>' for k, lbl, *_ in TIERS)
                + '</tr></thead><tbody>')
    for s in songs:
        c = cities[s["city"]]
        T = s["tiers"]
        body.append(f'<tr data-c="{c["slug"]}" data-q="{e((s["title"] + " " + s["genre"] + " " + c["name"]).lower())}">'
                    f'<td data-v="{e(s["title"].lower())}"><a href="songs/{s["id"]}.html">{e(s["title"])}</a></td>'
                    f'<td data-v="{s["city"]:02d}{s["number"]:04d}">{city_chip(c)}</td><td class="small mut">{e(s["genre"])}</td>'
                    f'<td class="n" data-v="{s["bpm"]}">{fmt_bpm(s["bpm"])}</td><td class="n" data-v="{s["play"]:.0f}">{fmt_time(s["play"])}</td>'
                    + "".join(f'<td class="n" data-v="{T[k]["internal"]:.3f}">{lv_chip(k, T[k]["level"], T[k]["internal"])}'
                              f' <span class="dim small">{T[k]["internal"]:.2f}</span></td>' for k, *_ in TIERS)
                    + "</tr>")
    body.append("</tbody></table></div>")
    body.append('<p class="small mut">레벨 칩은 게임에 보이는 표시 레벨(내부 수치 반올림, 1–12), 옆의 작은 숫자는 레이팅에 쓰는 내부 수치입니다. '
                'JAKARTA·SAPPORO·NEO AKIBA는 DLC 팩 도시입니다.</p>')
    script = """<script>
(()=>{const rows=[...document.querySelectorAll('#songs tbody tr')],q=document.getElementById('q');let city='';
function apply(){const s=q.value.trim().toLowerCase();rows.forEach(r=>{r.hidden=(city&&r.dataset.c!==city)||(s&&!r.dataset.q.includes(s));});}
document.querySelectorAll('#cities button').forEach(b=>b.onclick=()=>{city=b.dataset.c;document.querySelectorAll('#cities button').forEach(x=>x.classList.toggle('on',x===b));apply();history.replaceState(null,'',city?'#'+city:location.pathname);});
q.oninput=apply;
const ths=[...document.querySelectorAll('#songs th')];let last=null,dir=1;
ths.forEach((th,i)=>{if(!th.classList.contains('sort'))return;th.onclick=()=>{dir=last===i?-dir:(th.classList.contains('n')?-1:1);last=i;
const tb=document.querySelector('#songs tbody');rows.sort((a,b)=>{const x=a.children[i].dataset.v,y=b.children[i].dataset.v;const nx=parseFloat(x),ny=parseFloat(y);
return (isNaN(nx)||isNaN(ny)?x.localeCompare(y):nx-ny)*dir;}).forEach(r=>tb.appendChild(r));};});
const h=location.hash.slice(1);if(h){const b=document.querySelector('#cities button[data-c="'+h+'"]');if(b)b.click();}
})();</script>"""
    return page(False, "index.html", "곡 목록", "BeatBound 전곡의 난이도, 노트 특징, 레이팅 내부 수치.", "".join(body), script)


def rating_page(songs, cities):
    vals = sorted((s["tiers"][k]["internal"], s, k) for s in songs for k, *_ in TIERS)[::-1]
    top = [v for v, *_ in vals[:20]]
    chart_max = sum(v / 10 for v in top[:5]) + sum(v / 30 for v in top[5:20])
    body = ['<p class="eyebrow">Rating</p><h1>레이팅</h1>',
            '<p class="lead">레이팅은 내가 잘 친 채보 20개로 정해지는 실력 숫자입니다. 어려운 채보를 높은 점수로 완주할수록 오릅니다. '
            '승패나 플레이 횟수는 들어가지 않습니다.</p>',
            '<h2>계산식</h2><div class="formula">채보 값   = 내부 수치 × min(1, 점수 ÷ 1,000,000)      (완주한 기록만, 실패·중간 시작은 0)\n'
            '레이팅    = (1~5위 채보 값 합) × 1/10\n'
            '          + (6~20위 채보 값 합) × 1/30\n'
            '          + STEP UP 보너스 (최대 0.50)\n'
            '          + 래더 시즌 보너스 (최대 0.50)</div>',
            '<ul class="plain"><li><b>채보 칸</b>은 곡 × EASY/NORMAL/HARD/EXTREME입니다. 한 칸에는 그 칸의 최고 기록 하나만 들어갑니다.</li>'
            '<li><b>PERFECT</b>는 EXTREME 채보를 피격 1회 실패 규칙으로 치는 것이라 EXTREME 칸에 합쳐지고, 둘 중 높은 값을 씁니다.</li>'
            '<li>가중치 합은 5×1/10 + 15×1/30 = 1. 20칸을 모두 같은 값 x로 채우면 레이팅도 x가 됩니다.</li>'
            '<li>빈 칸은 0으로 셉니다. 기록이 20개 미만이면 그만큼 낮아집니다.</li>'
            '<li>점수가 100만을 넘어도(JUST 보너스) 계수는 1에서 멈춥니다.</li>'
            '<li>화면 숫자는 소수 둘째 자리에서 <b>버립니다</b>. 9.999는 9.99로 보입니다.</li>'
            '<li>래더·친구 대전 기록도 일반 기록처럼 레이팅에 들어갑니다. 대전 승패는 레이팅을 움직이지 않습니다.</li></ul>',
            '<h2>예시</h2>']
    ex = vals[:1][0]
    v, s, k = ex
    body.append(f'<div class="card"><p><a href="songs/{s["id"]}.html">{e(s["title"])}</a> {k.upper()} (내부 수치 {v:.3f})를 '
                f'950,000점으로 완주하면 채보 값은 {v:.3f} × 0.95 = <b class="mono">{v * .95:.3f}</b>. '
                f'이 값이 내 1위면 레이팅에 {v * .95 / 10:.3f}, 6위 이하라면 {v * .95 / 30:.3f}을 더합니다.</p>'
                f'<p class="mut small">상위 5칸이 레이팅의 절반을 차지합니다. 같은 점수라도 1–5위 안의 채보를 올리는 쪽이 세 배 효과가 큽니다.</p></div>')
    body.append('<h2>등급</h2><div class="tw"><table><thead><tr><th>등급</th><th class="n">레이팅</th></tr></thead><tbody>')
    for i, (n, lo) in enumerate(RATING_TIERS):
        hi = f'{RATING_TIERS[i + 1][1] - .01:.2f}' if i + 1 < len(RATING_TIERS) else "+"
        rng = f"{lo:.2f} ~ {hi}" if hi != "+" else f"{lo:.2f} +"
        body.append(f'<tr><td><span class="chip" style="color:{tier_color(n)}">{n}</span></td><td class="n">{rng}</td></tr>')
    body.append('</tbody></table></div><p class="small mut">MASTER(10.00 이상)는 더 나누지 않고 온라인 순위로 “MASTER #n”을 표시합니다. '
                'EMERALD(8.00)에 닿으면 모든 곡의 EXTREME이 열립니다.</p>')
    body.append('<h2>보너스</h2><div class="grid g2"><div class="card"><h3 style="margin-top:0">STEP UP 보너스 · 최대 0.50</h3>'
                '<p class="small">코스를 통과할 때마다 코스 보너스가 한 번 더해집니다. 8코스를 모두 통과하면 0.50. '
                '<a href="stepup.html">코스 목록</a></p></div>'
                '<div class="card"><h3 style="margin-top:0">래더 시즌 보너스 · 최대 0.50</h3>'
                '<p class="small">래더를 시즌에 20판 이상(고스트 판은 10판까지만 셈) 하면 순위가 매겨지고, 순위에 따라 보너스를 받습니다.</p>'
                '<div class="tw"><table><thead><tr><th>순위</th><th class="n">보너스</th></tr></thead><tbody>'
                '<tr><td>TOP 3 또는 상위 1%</td><td class="n">0.5</td></tr><tr><td>TOP 10 또는 상위 5%</td><td class="n">0.4</td></tr>'
                '<tr><td>상위 10%</td><td class="n">0.3</td></tr><tr><td>상위 25%</td><td class="n">0.2</td></tr>'
                '<tr><td>상위 50%</td><td class="n">0.1</td></tr></tbody></table></div>'
                '<p class="small mut">어느 구간이든 순위권 인원의 상위 절반 안이어야 합니다. 시즌이 바뀌면 딴 보너스를 한 시즌 그대로 지키고, '
                '그 뒤로는 못 따면 시즌마다 0.1씩 줄어듭니다.</p></div></div>')
    body.append(f'<h2>이론상 최대</h2><p>전 채보를 100만점 이상으로 완주했을 때 채보 몫은 <b class="mono">{chart_max:.3f}</b>, '
                f'보너스를 모두 받으면 <b class="mono">{chart_max + 1:.3f}</b>입니다. 이보다 높은 값은 온라인 순위에 올라가지 않습니다.</p>')
    body.append('<h2>내부 수치가 높은 채보 TOP 20</h2><div class="tw"><table><thead><tr><th class="n">#</th><th>곡</th><th>난이도</th>'
                '<th class="n">내부 수치</th><th class="n">표시 Lv</th></tr></thead><tbody>')
    for i, (v, s, k) in enumerate(vals[:20]):
        body.append(f'<tr><td class="n">{i + 1}</td><td><a href="songs/{s["id"]}.html">{e(s["title"])}</a> '
                    f'<span class="dim small">{e(cities[s["city"]]["name"])}</span></td>'
                    f'<td><span class="chip" style="color:{TIER_COLOR[k]}">{k.upper()}</span></td><td class="n">{v:.3f}</td>'
                    f'<td class="n">{s["tiers"][k]["level"]}</td></tr>')
    body.append('</tbody></table></div>')
    body.append(f'<h2>내부 수치는 어떻게 정하나</h2><p>채보마다 게임에 들어 있는 난이도 평가기({e(EVALUATOR)})가 채보를 읽어 소수점 수치를 냅니다. '
                '보는 것은 대략 세 가지입니다.</p><ul class="plain">'
                '<li><b>읽기</b>: 예고가 뜨고 터질 때까지 판을 읽고 갈 칸을 정하는 부담. 예고가 짧고 폭발이 겹칠수록 큽니다.</li>'
                '<li><b>이동</b>: 안전한 칸으로 가는 거리와 시간. 직전 폭발이 남긴 안전 칸에서 다음 안전 칸까지 멀수록 큽니다(판을 꽉 채운 노트가 여기서 무거워집니다).</li>'
                '<li><b>시간 밀도</b>: 1초 단위 부담을 평균 40%, 상위 20% 구간 50%, 가장 힘든 1초 10%로 섞습니다. 1초 하나가 8을 넘게 세지는 않고, '
                '빠른 연속 쓸기는 한 번의 물결로 봐 부담을 줄입니다.</li></ul>'
                '<p>표시 레벨은 이 수치를 반올림한 값(1–12)입니다. 레이팅은 반올림 전 수치를 그대로 씁니다.</p>')
    return page(False, "rating.html", "레이팅", "BeatBound 레이팅 계산식, 등급표, 보너스, 내부 수치 TOP 20.", "".join(body))


def stepup_page(songs, cities, courses, starters):
    by_id = {s["id"]: s for s in songs}
    rule_key = {"EASY": "easy", "NORMAL": "normal", "HARD": "hard", "EXTREME": "extreme"}
    body = ['<p class="eyebrow">STEP UP</p><h1>STEP UP 코스</h1>',
            '<p class="lead">세 곡을 연달아 치는 인증 코스입니다. 한 곡이라도 실패하거나 요구 등급에 못 미치면 코스가 끝납니다. '
            '통과하면 코스 보너스가 레이팅에 더해집니다(합계 최대 0.50).</p>',
            '<ul class="plain small mut"><li>곡마다 완주가 기본 조건이고, 등급 조건이 있으면 그 등급(+, ++ 포함) 이상이어야 합니다.</li>'
            '<li>코스 보너스는 앞의 다섯 코스(SPARK–RESONANCE)가 0.05–0.10, 팩 곡이 든 세 코스가 0.03–0.04입니다.</li>'
            '<li>VELOCITY·OVERLOAD·ZENITH에는 JAKARTA·SAPPORO·NEO AKIBA 팩 곡이 하나씩 들어 있어 그 팩이 있어야 열립니다.</li></ul>']
    total = 0
    for c in courses:
        total += c["bonus"]
        ints = []
        rows = []
        for i, st in enumerate(c["stages"]):
            s = by_id[st["song"]]
            k = rule_key[st["rule"]]
            t = s["tiers"][k]
            ints.append(t["internal"])
            need = f'{st["grade"]}{"+" * st["plus"]} 이상' if st["grade"] else "클리어"
            rows.append(f'<tr><td class="n">{i + 1}</td><td><a href="songs/{s["id"]}.html">{e(s["title"])}</a></td>'
                        f'<td>{city_chip(cities[s["city"]])}</td><td><span class="chip" style="color:{TIER_COLOR[k]}">{st["rule"]}</span></td>'
                        f'<td class="n">{lv_chip(k, t["level"])}</td><td class="n">{t["internal"]:.2f}</td><td>{need}</td></tr>')
        pack = any(cities[by_id[st["song"]]["city"]]["dlc"] for st in c["stages"])
        body.append(f'<h2 id="{c["id"]}">{e(c["title"])} <span class="mono mut small">+{c["bonus"]:.2f}</span></h2>'
                    f'<p class="small mut">평균 내부 수치 {sum(ints) / len(ints):.2f}{" · 팩 곡 포함" if pack else ""}</p>'
                    '<div class="tw"><table><thead><tr><th class="n">#</th><th>곡</th><th>도시</th><th>난이도</th><th class="n">Lv</th>'
                    '<th class="n">내부 수치</th><th>조건</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")
    body.append(f'<p class="mut">보너스 합계 {total:.2f} (상한 0.50).</p>')
    body.append('<h2>스타터 코스</h2><p class="lead">튜토리얼을 마치면 플레이 결과에 맞춰 세 코스 중 하나를 추천합니다. '
                '단계마다 비슷한 레벨의 곡 세 개가 있고, A 이상으로 클리어하면 다음 단계로 넘어갑니다. 레이팅 보너스는 없습니다.</p>')
    band_desc = {"Struggled": "레슨을 여러 번 다시 했거나 마지막 구간에서 많이 맞았을 때", "Steady": "무난히 마쳤을 때",
                 "Strong": "여유 있게 마쳤을 때"}
    for s in starters:
        body.append(f'<h3 id="starter-{s["band"].lower()}">{e(s["title"])} <span class="mut small">· {band_desc.get(s["band"], "")}</span></h3>'
                    '<div class="tw"><table><thead><tr><th class="n">단계</th><th>난이도</th><th>곡</th></tr></thead><tbody>')
        for i, st in enumerate(s["steps"]):
            k = rule_key[st["rule"]]
            links = " · ".join(f'<a href="songs/{sid}.html">{e(by_id[sid]["title"])}</a> '
                               f'<span class="dim small mono">{by_id[sid]["tiers"][k]["internal"]:.2f}</span>' for sid in st["songs"])
            body.append(f'<tr><td class="n">{i + 1}</td><td><span class="chip" style="color:{TIER_COLOR[k]}">{st["rule"]}</span></td><td>{links}</td></tr>')
        body.append("</tbody></table></div>")
    return page(False, "stepup.html", "STEP UP", "BeatBound STEP UP 인증 코스 8개와 스타터 코스 구성.", "".join(body))


def rules_page():
    body = ['<p class="eyebrow">Score &amp; Rank</p><h1>점수·랭크 규칙</h1>',
            '<p class="lead">8×8 패드 판 위에서 큐브를 움직여 음악에 맞춰 터지는 폭발을 피하는 게임입니다. '
            '점수는 피한 폭발, 아슬아슬하게 피한 COOL, 마지막 순간에 빠져나간 JUST로 쌓입니다.</p>',
            '<h2>100만점 배점</h2><p>곡마다 단위 u를 정해 배점합니다. 100만점은 “피격 0, COOL 최대, JUST 0”인 최적 플레이입니다.</p>',
            '<div class="tw"><table><thead><tr><th>항목</th><th class="n">점수</th><th>설명</th></tr></thead><tbody>'
            '<tr><td>폭발 피함</td><td class="n">3u</td><td>16분 틱마다 한 번</td></tr>'
            '<tr><td>COOL (근접)</td><td class="n">u</td><td>폭발 바로 옆에서 피함. FEVER 안에서는 2u</td></tr>'
            '<tr><td>JUST</td><td class="n">u</td><td>터지기 0–150ms 전에 폭발 범위 밖으로 빠져나감. FEVER 안 2u, 100만점 위로 넘침</td></tr>'
            '<tr><td>BONUS</td><td class="n">20u</td><td>30콤보마다</td></tr>'
            '<tr><td>피격</td><td class="n">−10u</td><td>맞으면 감점, 연속 피격은 HP를 깎음</td></tr></tbody></table></div>',
            '<div class="formula">u = 50 × 1,000,000 ÷ 기준 원점수   (5의 배수로 올림)\n'
            '기준 원점수 = 150 × 폭발 수 + 1000 × ⌊폭발 수 ÷ 30⌋ + 50 × (최대 COOL + FEVER 안 최대 COOL)</div>',
            '<p class="small mut">최대 COOL은 채보 전체를 미리 아는 봇이 계산한 정확한 최적값입니다(50ms 격자, 입력 간격 150ms 이상, 한 칸씩 이동). '
            '곡별 값은 각 곡 페이지의 “점수 배점” 표에 있습니다.</p>',
            '<h2>랭크 컷</h2><p>모든 곡이 같은 컷을 씁니다. 랭크는 점수만 봅니다.</p>'
            '<div class="tw"><table><thead><tr><th>랭크</th><th class="n">기본</th><th class="n">+</th><th class="n">++</th></tr></thead><tbody>']
    for g in ["SSS", "SS", "S", "A", "B", "C", "D"]:
        d = dict(CUTS)
        body.append(f'<tr><td><b>{g}</b></td><td class="n">{d[g]:,}</td><td class="n">{d[g + "+"]:,}</td><td class="n">{d[g + "++"]:,}</td></tr>')
    body.append('</tbody></table></div><p class="small mut">실패한 판은 F. 100만을 넘는 점수도 그대로 기록됩니다.</p>')
    body.append('<h2>난이도와 규칙</h2><div class="tw"><table><thead><tr><th>난이도</th><th>예고 시간</th><th>피격 허용</th><th>열리는 조건</th></tr></thead><tbody>'
                f'<tr><td><span class="chip" style="color:{TIER_COLOR["easy"]}">EASY</span></td><td>약 1.3초</td><td>폭발 수의 4.2%</td><td>항상</td></tr>'
                f'<tr><td><span class="chip" style="color:{TIER_COLOR["normal"]}">NORMAL</span></td><td>약 1.3초</td><td>3%</td><td>항상</td></tr>'
                f'<tr><td><span class="chip" style="color:{TIER_COLOR["hard"]}">HARD</span></td><td>약 1.0초</td><td>3%</td><td>그 곡 NORMAL 이상 클리어, 또는 아무 곡 10곡 클리어</td></tr>'
                f'<tr><td><span class="chip" style="color:{TIER_COLOR["extreme"]}">EXTREME</span></td><td>곡 기본 (8분 4칸 또는 2칸)</td><td>3%</td><td>그 곡 HARD를 S 이상, 또는 레이팅 EMERALD</td></tr>'
                f'<tr><td><span class="chip" style="color:#ff4dc7">PERFECT</span></td><td>EXTREME과 같음</td><td>1회</td><td>그 곡 EXTREME 클리어</td></tr>'
                '</tbody></table></div>'
                '<p class="small mut">예고 시간은 목표 초에 가장 가까운 박 단위 길이로 맞추고, 곡 기본 예고보다 짧아지지는 않습니다. '
                '피격 허용은 연속으로 맞을 수 있는 횟수이고, 피하는 동안 조금씩 회복됩니다.</p>')
    body.append('<h2>FEVER</h2><p>곡마다 가장 뜨거운 구간 하나가 FEVER입니다. 그 안에서는 COOL·JUST가 두 배입니다. '
                '곡별 FEVER 구간은 각 곡 페이지에 있습니다.</p>')
    return page(False, "rules.html", "점수·랭크 규칙", "BeatBound 100만점 배점, 랭크 컷, 난이도별 규칙.", "".join(body))


# ---------------------------------------------------------------- main
def main():
    global VERSION, BUILD_DATE, EVALUATOR, NEIGHBOURS
    import datetime
    BUILD_DATE = datetime.date.today().isoformat()
    VERSION = BUILD_DATE.replace("-", "")
    EVALUATOR = re.search(r"evaluatorVersion: (\S+)", (GD / "ChartLevelTable.asset").read_text(encoding="utf-8")).group(1)
    cities = load_cities()
    levels = load_levels()
    songs = load_songs(cities, levels)
    courses = load_courses()
    starters = load_starters()
    NEIGHBOURS = {s["id"]: (songs[i - 1] if i else None, songs[i + 1] if i + 1 < len(songs) else None) for i, s in enumerate(songs)}
    ranks = {}
    for k, *_ in TIERS:
        order = sorted(songs, key=lambda s: -s["tiers"][k]["internal"])
        ranks[k] = {s["id"]: i + 1 for i, s in enumerate(order)}
    courses_by_song = defaultdict(list)
    for c in courses:
        for i, st in enumerate(c["stages"]):
            courses_by_song[st["song"]].append((c, i, st))
    starters_by_song = defaultdict(list)
    for s in starters:
        for i, st in enumerate(s["steps"]):
            for sid in st["songs"]:
                starters_by_song[sid].append((s, i, st))

    (OUT / "songs").mkdir(parents=True, exist_ok=True)
    (OUT / "wiki.css").write_text(CSS.strip() + "\n", encoding="utf-8")
    (OUT / "index.html").write_text(index_page(songs, cities), encoding="utf-8")
    (OUT / "rating.html").write_text(rating_page(songs, cities), encoding="utf-8")
    (OUT / "stepup.html").write_text(stepup_page(songs, cities, courses, starters), encoding="utf-8")
    (OUT / "rules.html").write_text(rules_page(), encoding="utf-8")
    keep = set()
    for s in songs:
        (OUT / "songs" / f"{s['id']}.html").write_text(song_page(s, cities, ranks, courses_by_song, starters_by_song), encoding="utf-8")
        keep.add(f"{s['id']}.html")
    for old in (OUT / "songs").glob("*.html"):
        if old.name not in keep:
            old.unlink()
    print(f"wrote {len(songs)} songs, {len(courses)} courses, {len(starters)} starter courses → {OUT}")


if __name__ == "__main__":
    main()
