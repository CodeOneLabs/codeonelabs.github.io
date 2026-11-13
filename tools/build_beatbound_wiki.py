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
        def col(field):
            m = re.search(rf"{field}: \{{r: ([\d.]+), g: ([\d.]+), b: ([\d.]+)", t)
            return "#%02x%02x%02x" % tuple(int(float(x) * 255 + .5) for x in m.groups())
        cities[num] = dict(num=num, name=yaml_field(t, "displayName"), tagline=yaml_field(t, "tagline") or "",
                           color=color, accent2=col("accent2"), blast=col("blast"), player=col("player"),
                           slug=name.lower(), dlc=num in DLC_CITIES)
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
    enc = []
    for tick, hs in sorted(ticks.items()):
        mask = 0
        hole = 0
        aim = 0
        aim_kind = hole_dx = hole_dy = 0
        for h in hs:
            if h.get("aim", 0) and not aim_kind:
                aim_kind = h["aim"]
            if h.get("holeSize", 0) > 0 and not hole:
                hole_dx, hole_dy = h.get("holeDx", 0), h.get("holeDy", 0)
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
        row = [round(tick_time(tick) * 1000), format(mask, "x")]
        if aim_kind or hole:
            row += [aim_kind, hole, hole_dx, hole_dy]
        enc.append(row)
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
    return dict(enc=enc, bar_starts=[round((bt[i] if mapped else first + i * 8 * step) * 1000) for i in range(bars + 1)],
                blasts=count, nps=count / play, cells=cells_total / max(1, count), sixteenth=off_ticks / max(1, count),
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
        song["basis_en"] = i.get("soundBasis", "") if sid in SOUND_KO else ""
        song["motif_en"] = i.get("motif", "")
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


# ---------------------------------------------------------------- language
sys.path.insert(0, str(Path(__file__).resolve().parent))
from beatbound_wiki_text import TEXT  # noqa: E402

LANG = "ko"
LANGS = ("ko", "en")


def t(key, **kw):
    s = TEXT[key][LANG]
    return s.format(**kw) if kw else s


def L(ko, en):
    return ko if LANG == "ko" else en


# ---------------------------------------------------------------- rendering helpers
CSS = r"""
:root{color-scheme:dark;--bg:#0b0a11;--face:#15131e;--face2:#1c1928;--line:#2b2740;--ink:#f3ecdc;--muted:#a49cb8;--dim:#6f6886;
--accent:#ff5cc0;--blast:#ffe047;--player:#00f0ff;--sans:-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Noto Sans KR","Segoe UI",sans-serif;
--mono:ui-monospace,"SF Mono",Menlo,Consolas,monospace}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.65 var(--sans);overflow-x:hidden}
body:before{content:"";position:fixed;inset:0;pointer-events:none;z-index:-1;background:
radial-gradient(900px 500px at 85% -10%,color-mix(in srgb,var(--accent) 16%,transparent),transparent 70%),
radial-gradient(700px 400px at -10% 30%,#3b2a8a22,transparent 70%)}
a{color:inherit;text-decoration-color:#ffffff40;text-underline-offset:3px}a:hover{text-decoration-color:currentColor}
.top{position:sticky;top:0;z-index:5;background:#0b0a11e6;backdrop-filter:blur(8px);border-bottom:1px solid var(--line)}
.top .in{max-width:1100px;margin:0 auto;padding:0 16px;height:56px;display:flex;align-items:center;gap:14px;overflow-x:auto;white-space:nowrap;scrollbar-width:none}
.brand{display:flex;align-items:center;gap:9px;font-weight:800;letter-spacing:.08em;text-decoration:none;font-size:14px}.brand b{color:var(--accent)}
.logo{display:grid;grid-template-columns:repeat(3,6px);gap:2px}.logo i{width:6px;height:6px;border-radius:1.5px;background:#2e2944}
.logo i.on{background:var(--accent);box-shadow:0 0 6px var(--accent)}.brand:hover .logo i{animation:pop .5s calc(var(--d)*60ms) both}
.top nav{display:flex;gap:2px;margin-left:auto}.top nav a{text-decoration:none;color:var(--muted);font-size:14px;padding:6px 10px;border-radius:8px}
.top nav a:hover,.top nav a.on{color:var(--ink);background:var(--face2)}.top nav a.lang{border:1px solid var(--line);margin-left:6px;font:700 12px var(--mono)}
main{max-width:1100px;margin:0 auto;padding:28px 16px 64px}
h1{font-size:32px;line-height:1.15;margin:4px 0 8px;letter-spacing:-.01em}h2{font-size:20px;margin:44px 0 12px}
h3{font-size:16px;margin:24px 0 8px}p{margin:8px 0}.lead{color:var(--muted);max-width:720px}
.eyebrow{font:700 12px var(--mono);letter-spacing:.14em;color:var(--muted);text-transform:uppercase;margin:0}
.card{background:var(--face);border:1px solid var(--line);border-radius:14px;padding:16px 18px;margin:12px 0}
.grid{display:grid;gap:12px}.g2{grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr))}
.tw{overflow-x:auto;margin:10px 0;border:1px solid var(--line);border-radius:12px;background:var(--face)}
table{border-collapse:collapse;width:100%;font-size:14px}th,td{padding:8px 10px;text-align:left;border-bottom:1px solid var(--line);white-space:nowrap}
th{font-weight:600;color:var(--muted);background:var(--face2);font-size:12.5px}
tbody tr:last-child td{border-bottom:0}td.n,th.n{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums}
tbody tr{transition:background .2s}tbody tr:hover{background:#ffffff08}
.chip{display:inline-block;font:700 11px/1 var(--mono);letter-spacing:.06em;padding:5px 7px 4px;border-radius:6px;border:1px solid currentColor;vertical-align:middle;white-space:nowrap}
.lv{display:inline-block;min-width:28px;text-align:center;font:700 13px/1 var(--mono);padding:5px 6px 4px;border-radius:6px;background:var(--face2);border:1px solid currentColor;transition:transform .2s,box-shadow .2s}
.lv:hover,tr:hover .lv{box-shadow:0 0 10px currentColor}.lv:hover{transform:translateY(-2px)}
.mut{color:var(--muted)}.dim{color:var(--dim)}.small{font-size:13px}.mono{font-family:var(--mono)}
.kv{display:grid;grid-template-columns:max-content 1fr;gap:4px 16px;margin:0}.kv dt{color:var(--muted)}.kv dd{margin:0}
.filters{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0}.filters button{font:600 12.5px var(--sans);color:var(--muted);background:var(--face);border:1px solid var(--line);border-radius:999px;padding:6px 12px;cursor:pointer;transition:all .2s}
.filters button:hover{color:var(--ink)}.filters button.on{color:var(--c,var(--ink));border-color:var(--c,var(--ink));box-shadow:0 0 12px color-mix(in srgb,var(--c,#fff) 35%,transparent)}
input.search{width:100%;max-width:320px;font:15px var(--sans);color:var(--ink);background:var(--face);border:1px solid var(--line);border-radius:10px;padding:9px 12px}
th.sort{cursor:pointer;user-select:none}th.sort:after{content:" ↕";color:var(--dim)}
.formula{font:14px/1.7 var(--mono);background:#07060b;border:1px solid var(--line);border-radius:12px;padding:14px 16px;overflow-x:auto;white-space:pre}
.bars{display:flex;align-items:flex-end;gap:1px;height:56px;margin:6px 0 2px}.bars i{flex:1;min-width:1px;border-radius:1px 1px 0 0;transform-origin:bottom;animation:grow .7s cubic-bezier(.2,.9,.3,1.2) both;animation-delay:calc(var(--i)*6ms)}
.heat{display:grid;grid-template-columns:repeat(8,1fr);gap:2px;width:112px;height:112px;flex:none}.heat i{border-radius:2px;transition:transform .15s}.heat i:hover{transform:scale(1.35);position:relative;z-index:1}
.tier-cards{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(min(100%,240px),1fr))}
.tc{transition:border-color .2s,transform .2s}.tc:hover{border-color:var(--tc);transform:translateY(-2px)}
.tc h3{margin:0 0 8px;display:flex;align-items:center;gap:8px}.tc .big{font:800 26px/1 var(--mono)}
.tc .go{margin-left:auto;font:700 11px var(--mono);color:var(--tc);background:none;border:1px solid var(--tc);border-radius:6px;padding:4px 7px;cursor:pointer}
.tc .go:hover{background:var(--tc);color:#000}
ul.plain{padding-left:18px;margin:6px 0}ul.plain li{margin:3px 0}
.parts{list-style:none;padding:0;margin:0}.parts button{all:unset;cursor:pointer;display:flex;gap:10px;width:100%;padding:3px 6px;border-radius:6px;font-size:13px}
.parts button:hover{background:var(--face2)}.parts button.on{background:color-mix(in srgb,var(--accent) 20%,transparent)}
.parts .pt{font-family:var(--mono);color:var(--muted);min-width:118px}
footer{border-top:1px solid var(--line);color:var(--dim);font-size:13px}footer .in{max-width:1100px;margin:0 auto;padding:20px 16px 40px}

/* launchpad board */
.hero{display:grid;grid-template-columns:minmax(0,380px) 1fr;gap:32px;align-items:center}
.bb{width:100%;max-width:380px}
.board{position:relative;display:grid;grid-template-columns:repeat(8,1fr);gap:clamp(3px,1.2vw,6px);padding:clamp(8px,2.6vw,14px);aspect-ratio:1;
border-radius:18px;background:linear-gradient(160deg,#1a1726,#09080e);border:1px solid #2f2a45;
box-shadow:0 0 0 5px #0c0b12,0 0 0 6px #2a2540,0 24px 60px #000a,inset 0 1px 0 #ffffff10;touch-action:manipulation;user-select:none;-webkit-user-select:none}
.board.shake{animation:shake .28s}
.pad{position:relative;border-radius:22%;background:#1d1a2b;box-shadow:inset 0 -2px 0 #0007,inset 0 1px 0 #ffffff12;cursor:pointer;overflow:hidden;
transition:background .38s ease-out,box-shadow .38s ease-out}
.pad .l{position:absolute;inset:0;border-radius:inherit;background:var(--accent);opacity:var(--a,0);transition:opacity .5s}
.pad .w{position:absolute;inset:12%;border-radius:18%;border:2px solid var(--accent);opacity:0;transform:scale(calc(.25 + .75*var(--w,0)))}
.pad.warn .w{opacity:calc(.35 + .65*var(--w,0))}
.pad.warn.hot .w{border-color:#fff;background:color-mix(in srgb,var(--accent) 35%,transparent)}
.pad.boom{background:var(--blast);box-shadow:0 0 18px var(--blast),inset 0 0 0 2px #fff6;transition:none}
.pad.ring{background:color-mix(in srgb,var(--accent) 70%,#fff);box-shadow:0 0 14px var(--accent);transition:none}
.pad:hover{background:#262238}
.bb-ui{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin-top:14px}
.bb-ui button,.bb-ui select{font:700 12px var(--mono);letter-spacing:.04em;color:var(--muted);background:var(--face);border:1px solid var(--line);border-radius:8px;padding:7px 10px;cursor:pointer}
.bb-ui button:hover{color:var(--ink)}.bb-ui button.on{color:var(--c,var(--ink));border-color:var(--c,var(--ink))}
.bb-ui .play{color:#000;background:var(--accent);border-color:var(--accent)}.bb-ui .play:hover{color:#000;filter:brightness(1.15)}
.bb-ui select{max-width:160px}
.bb-hint{font-size:12.5px;color:var(--dim);margin:8px 0 0}
.mini{display:inline-grid;grid-template-columns:repeat(8,1fr);gap:1px;width:26px;height:26px;vertical-align:middle;margin-right:10px;padding:2px;border-radius:5px;background:#07060b}
.mini i{border-radius:1px;background:#1d1a2b}.mini i.on{background:var(--c);opacity:var(--a)}
tr:hover .mini i.on{animation:twinkle .7s calc(var(--d)*25ms) both}
.songcell{display:flex;align-items:center}
@keyframes pop{0%{transform:scale(1)}40%{transform:scale(1.5);background:var(--blast)}100%{transform:scale(1)}}
@keyframes twinkle{0%{opacity:var(--a)}35%{opacity:1;filter:brightness(1.8)}100%{opacity:var(--a)}}
@keyframes hop{from{transform:scale(.6)}to{transform:scale(1)}}
@keyframes shake{0%,100%{transform:none}25%{transform:translate(-5px,2px)}50%{transform:translate(4px,-3px)}75%{transform:translate(-3px,1px)}}
@keyframes grow{from{transform:scaleY(0)}to{transform:scaleY(1)}}
@media(max-width:760px){.hero{grid-template-columns:1fr;gap:20px}.bb{max-width:340px;margin:0 auto}h1{font-size:26px}main{padding-top:20px}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""

JS = r"""
(()=>{
const L=window.BBL||{};const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
let ac=null,soundOn=true;
function audio(){if(!ac){try{ac=new (window.AudioContext||window.webkitAudioContext)()}catch(e){}}if(ac&&ac.state==='suspended')ac.resume();return ac}
// live: a tap (user gesture) may wake a suspended context; board playback only sounds while the context runs,
// otherwise blips queue on a frozen clock and all fire at once when the tab comes back.
function blip(f,d,type,vol,live){if(!soundOn||document.hidden)return;const a=audio();if(!a||(!live&&a.state!=='running'))return;const o=a.createOscillator(),g=a.createGain();o.type=type||'square';o.frequency.setValueAtTime(f,a.currentTime);
o.frequency.exponentialRampToValueAtTime(Math.max(40,f*.45),a.currentTime+d);g.gain.setValueAtTime(vol||.05,a.currentTime);g.gain.exponentialRampToValueAtTime(.0001,a.currentTime+d);o.connect(g).connect(a.destination);o.start();o.stop(a.currentTime+d)}
function cellsOf(hex){const out=[];let v=BigInt('0x'+hex);for(let i=0;v>0n;i++,v>>=1n)if(v&1n)out.push(i);return out}
const AIM={1:(x,y)=>[[x,y]],2:(x,y)=>[...Array(8)].map((_,i)=>[i,y]),3:(x,y)=>[...Array(8)].map((_,i)=>[x,i]),
4:(x,y)=>[...Array(8)].flatMap((_,i)=>[[i,y],[x,i]]),5:(x,y)=>[-1,0,1].flatMap(a=>[-1,0,1].map(b=>[x+a,y+b])),
6:(x,y)=>[...Array(15)].flatMap((_,k)=>{const i=k-7;return[[x+i,y+i],[x+i,y-i]]})};

class Board{
 constructor(root){this.root=root;this.el=root.querySelector('.board');this.pads=[];this.px=3;this.py=4;this.playing=false;this.data=null;
  const led=(root.dataset.led||'').split(',');
  for(let i=0;i<64;i++){const p=document.createElement('div');p.className='pad';p.innerHTML='<i class="l"></i><i class="w"></i>';
   const ch=(led[i>>3]||'')[i&7];const a={'1':.3,'2':.6,'3':1}[ch];if(a)p.style.setProperty('--a',a);p.dataset.i=i;this.el.appendChild(p);this.pads.push(p)}
  this.el.addEventListener('pointerdown',e=>{const p=e.target.closest('.pad');if(!p)return;e.preventDefault();this.tap(+p.dataset.i)});
  this.ui=root.querySelector('.bb-ui');this.stat=root.querySelector('.bb-stat');
  if(this.ui)this.setupUI();
  if(root.dataset.demo&&!reduce)this.load().then(()=>{this.mode='demo';this.start(0)});
 }
 led(on){this.pads.forEach(p=>p.querySelector('.l').style.opacity=on?'':'0')}
 flash(cells,cls,ms){cells.forEach(i=>{const p=this.pads[i];if(!p)return;p.classList.add(cls);clearTimeout(p._t);p._t=setTimeout(()=>p.classList.remove(cls),ms||70)})}
 ripple(i){const x=i&7,y=i>>3;const cross=[];for(let k=0;k<8;k++){cross.push(y*8+k,k*8+x)}this.flash(cross,'boom',90);blip(520+x*40,.12,'square',.04,true);
  for(let r=1;r<9;r++)setTimeout(()=>{const ring=[];for(let j=0;j<64;j++){const d=Math.max(Math.abs((j&7)-x),Math.abs((j>>3)-y));if(d===r)ring.push(j)}this.flash(ring,'ring',80)},r*45)}
 tap(i){audio();this.ripple(i)}
 async load(){if(this.data)return this.data;const r=await fetch(this.root.dataset.src);this.data=await r.json();
  for(const k in this.data.tiers){this.data.tiers[k].hits.forEach(h=>h.cells=cellsOf(h[1]))}return this.data}
 setupUI(){const ui=this.ui;this.tier=this.root.dataset.tier||'extreme';
  ui.querySelectorAll('[data-tier]').forEach(b=>b.onclick=()=>{this.tier=b.dataset.tier;ui.querySelectorAll('[data-tier]').forEach(x=>x.classList.toggle('on',x===b));if(this.playing)this.start(this.fromMs)});
  this.sel=ui.querySelector('select');
  ui.querySelector('.play').onclick=()=>{audio();this.playing?this.stop():this.start(this.sel?+this.sel.value:0)};
  const snd=ui.querySelector('.snd');if(snd)snd.onclick=()=>{soundOn=!soundOn;snd.classList.toggle('on',soundOn)};
  document.querySelectorAll('[data-seek]').forEach(b=>b.onclick=()=>{if(this.sel)this.sel.value=b.dataset.seek;audio();this.start(+b.dataset.seek);this.root.scrollIntoView({behavior:'smooth',block:'center'})});
  document.querySelectorAll('[data-playtier]').forEach(b=>b.onclick=()=>{const t=ui.querySelector('[data-tier="'+b.dataset.playtier+'"]');if(t)t.click();audio();this.start(0);this.root.scrollIntoView({behavior:'smooth',block:'center'})});
 }
 async start(fromMs){await this.load();this.stop(true);this.fromMs=fromMs||0;const tier=this.data.tiers[this.mode==='demo'?'extreme':this.tier];
  this.hits=tier.hits;this.lead=tier.lead;this.i=0;while(this.i<this.hits.length&&this.hits[this.i][0]<this.fromMs)this.i++;
  this.resolved=new Map();this.nHit=0;this.nDodge=0;this.playing=true;if(this.mode!=='demo'){this.mode='play';this.px=3;this.py=4}
  this.endMs=this.mode==='demo'?this.data.demoEnd:(this.hits.length?this.hits[this.hits.length-1][0]+900:0);
  this.led(false);this.t0=performance.now()-(this.fromMs-this.lead-300);const pb=this.ui&&this.ui.querySelector('.play');if(pb)pb.textContent=L.stop||'STOP';this.root.classList.add('on');
  this.last=performance.now();
  // a long frame gap (hidden tab, occluded window) pauses the chart instead of replaying everything it missed
  const loop=()=>{if(!this.playing)return;const now=performance.now();if(now-this.last>250)this.t0+=now-this.last-16;this.last=now;this.frame(now-this.t0);this.raf=requestAnimationFrame(loop)};loop()}
 stop(quiet){this.playing=false;cancelAnimationFrame(this.raf);this.pads.forEach(p=>{p.classList.remove('warn','hot');p.style.removeProperty('--w')});
  if(!quiet)this.led(true);
  const pb=this.ui&&this.ui.querySelector('.play');if(pb)pb.textContent=L.play||'PLAY';this.root.classList.remove('on')}
 resolve(h){let c=this.resolved.get(h);if(c)return c;c=h.cells.slice();const aim=h[2]||0,hole=h[3]||0;
  if(aim&&AIM[aim])AIM[aim](this.px,this.py).forEach(([x,y])=>{if(x>=0&&x<8&&y>=0&&y<8)c.push(y*8+x)});
  if(hole){const hx=Math.min(8-hole,Math.max(0,this.px-((h[4]||0)<0?hole-1:0))),hy=Math.min(8-hole,Math.max(0,this.py-((h[5]||0)<0?hole-1:0)));
   c=[];for(let j=0;j<64;j++){const x=j&7,y=j>>3;if(!(x>=hx&&x<hx+hole&&y>=hy&&y<hy+hole))c.push(j)}}
  this.resolved.set(h,c);return c}
 frame(t){const w=new Float32Array(64);let due=0;
  for(let k=this.i;k<this.hits.length;k++){const h=this.hits[k];if(h[0]>t+this.lead)break;
   if(h[0]<=t){if(k===this.i){const cells=this.resolve(h);this.flash(cells,'boom',70);due=Math.max(due,cells.length);this.i++}continue}
   const p=1-(h[0]-t)/this.lead;this.resolve(h).forEach(c=>{if(p>w[c])w[c]=p})}
  for(let c=0;c<64;c++){const p=this.pads[c];if(w[c]>0){p.classList.add('warn');p.classList.toggle('hot',w[c]>.8);p.style.setProperty('--w',w[c].toFixed(3))}else if(p.classList.contains('warn')){p.classList.remove('warn','hot')}}
  if(due)blip(300+due*6,.06,'square',this.mode==='demo'?.02:.03);
  if(t>this.endMs){if(this.mode==='demo'){this.start(0)}else{this.stop()}}}
}
document.querySelectorAll('.bb').forEach(r=>new Board(r));
document.querySelectorAll('.secret,.secret-line').forEach(el=>{const open=()=>el.classList.add('shown');el.addEventListener('click',open);el.addEventListener('keydown',e=>{if(e.key==='Enter')open()})});
const ra=document.querySelector('.reveal-all');if(ra)ra.onclick=()=>document.querySelectorAll('.secret,.secret-line').forEach(el=>el.classList.add('shown'));
// small LED marks: twinkle the header logo, city filter glow is CSS
})();
"""

NAV = [("index.html", "nav.songs"), ("rating.html", "nav.rating"), ("stepup.html", "nav.stepup"), ("rules.html", "nav.rules"), ("gear.html", "nav.gear"), ("ranking.html", "nav.ranking")]
LOGO = "".join(f'<i class="{"on" if c == "1" else ""}" style="--d:{i}"></i>' for i, c in enumerate("101010101"))


def page(path, active, title, desc, body, script=""):
    """path is relative to the language root, e.g. "index.html" or "songs/la1.html"."""
    depth = path.count("/")
    base = "../" * depth
    shared = base + ("../" if LANG == "en" else "")
    other = (base + "en/" + path) if LANG == "ko" else (base + "../" + path)
    nav = "".join(f'<a href="{base}{h}"{" class=on" if h == active else ""}>{t(k)}</a>' for h, k in NAV)
    nav += f'<a class="lang" href="{other}" hreflang="{"en" if LANG == "ko" else "ko"}">{t("nav.lang")}</a>'
    labels = json.dumps({"play": "▶ " + t("board.play").upper(), "stop": "■ " + t("board.stop").upper(),
                         "hits": t("board.hits").upper(), "dodged": t("board.dodged").upper()}, ensure_ascii=False)
    url_ko = f"{SITE}/{path}"
    url_en = f"{SITE}/en/{path}"
    return (f'<!doctype html><html lang="{LANG}"><head><meta charset="utf-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{e(title)} · {t("site")}</title><meta name="description" content="{e(desc)}">'
            f'<link rel="alternate" hreflang="ko" href="{url_ko}"><link rel="alternate" hreflang="en" href="{url_en}">'
            f'<meta property="og:title" content="{e(title)} · {t("site")}"><meta property="og:description" content="{e(desc)}">'
            f'<link rel="icon" type="image/png" href="{shared}../../assets/beatbound-icon-128.png">'
            f'<link rel="stylesheet" href="{shared}wiki.css?v={VERSION}"></head><body>'
            f'<header class="top"><div class="in"><a class="brand" href="{base}index.html"><span class="logo">{LOGO}</span><span>BEAT<b>BOUND</b> WIKI</span></a>'
            f'<nav>{nav}</nav></div></header><main>{body}</main>'
            f'<footer><div class="in">{e(t("footer", date=BUILD_DATE))}</div></footer>'
            f'<script>window.BBL={labels}</script><script src="{shared}wiki.js?v={VERSION}" defer></script>{script}</body></html>\n')


def lv_chip(tier_key, level, internal=None):
    if level is None:
        return '<span class="dim">–</span>'
    title = f' title="{t("col.internal")} {internal:.2f}"' if internal is not None else ""
    return f'<span class="lv" style="color:{TIER_COLOR[tier_key]}"{title}>{level}</span>'


def tier_chip(key, label=None):
    return f'<span class="chip" style="color:{TIER_COLOR[key]}">{label or key.upper()}</span>'


def city_chip(city):
    return f'<span class="chip" style="color:{city["color"]}">{e(city["name"])}</span>'


def mini_led(rows, color):
    out = []
    for y, r in enumerate(rows[:8]):
        for x, ch in enumerate(r[:8]):
            a = {"1": .35, "2": .65, "3": 1}.get(ch)
            out.append(f'<i class="on" style="--a:{a};--d:{x + y}"></i>' if a else "<i></i>")
    return f'<span class="mini" style="--c:{color}" aria-hidden="true">{"".join(out)}</span>'


def board(song_id, rows, city, shared, demo=False, parts=None, tier="extreme"):
    style = f'--accent:{city["color"]};--blast:{city["blast"]};--player:{city["player"]}'
    led_attr = ",".join(rows)
    head = (f'<div class="bb" data-src="{shared}data/{song_id}.json" data-led="{led_attr}" data-tier="{tier}"'
            f'{" data-demo=1" if demo else ""} style="{style}"><div class="board" aria-label="8×8 launchpad"></div>')
    if demo:
        return head + "</div>"
    tiers = "".join(f'<button data-tier="{k}" style="--c:{TIER_COLOR[k]}"{" class=on" if k == tier else ""}>{lbl}</button>'
                    for k, lbl, *_ in TIERS)
    opts = f'<option value="0">{t("board.from")} · 0:00</option>' + "".join(
        f'<option value="{p["ms"]}">{e(p["name"])} · {fmt_time(p["ms"] / 1000)}</option>' for p in (parts or []))
    return (head + f'<div class="bb-ui"><button class="play">▶ {t("board.play").upper()}</button>{tiers}'
            f'<select aria-label="{t("board.from")}">{opts}</select>'
            f'<button class="snd on" title="{t("board.sound")}">♪</button></div>'
            f'<p class="bb-hint">{t("board.hint")}</p></div>')


def heat(cells, color):
    mx = max(cells) or 1
    out = []
    for v in cells:
        a = v / mx
        out.append(f'<i style="background:{color};opacity:{.08 + .92 * a:.2f}" title="{v}"></i>' if v else '<i style="background:#ffffff0a"></i>')
    return f'<div class="heat">{"".join(out)}</div>'


def density(per_bar, bar_sec, color, peak):
    rates = [n / s if s else 0 for n, s in zip(per_bar, bar_sec)]
    mx = max(rates) or 1
    bars = "".join(f'<i style="--i:{i};height:{max(2, 100 * r / mx):.0f}%;background:{color};opacity:{.95 if peak <= i < peak + 4 else .5}"></i>'
                   for i, r in enumerate(rates))
    return f'<div class="bars">{bars}</div>'


def pct(x):
    return f"{100 * x:.0f}%"


def tier_color(name):
    return TIER_COLORS[name.split()[0]]


def need_text(st):
    return t("need.grade", g=f'{st["grade"]}{"+" * st["plus"]}') if st["grade"] else t("need.clear")


# ---------------------------------------------------------------- song notes (derived from the charts)
def chart_notes(song, key):
    tt = song["tiers"][key]
    notes = []
    if tt["sixteenth"] >= .2:
        notes.append(t("note.16th_many", p=pct(tt["sixteenth"])))
    elif tt["sixteenth"] < .03:
        notes.append(t("note.16th_none"))
    if tt["hole"] >= .05:
        notes.append(t("note.hole", p=pct(tt["hole"])))
    if tt["aim"] >= .05:
        notes.append(t("note.aim", p=pct(tt["aim"])))
    if tt["cells"] >= 24:
        notes.append(t("note.wide", n=f'{tt["cells"]:.0f}'))
    elif tt["cells"] <= 10:
        notes.append(t("note.thin", n=f'{tt["cells"]:.0f}'))
    pk = tt["peak_bar"]
    sec_name = section_at(song, pk)
    notes.append(t("note.peak", a=pk + 1, b=pk + 4, sec=f" ({sec_name})" if sec_name else "", n=f'{tt["peak_nps"]:.1f}'))
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


def part_list(song):
    x = song["tiers"]["extreme"]
    out = []
    for p in song["parts"]:
        ms = x["bar_starts"][min(p["bar"], len(x["bar_starts"]) - 1)]
        out.append(dict(bar=p["bar"], name=p["name"], ms=ms))
    return out


# ---------------------------------------------------------------- pages
def song_page(song, cities, ranks, courses_by_song, starters_by_song):
    city = cities[song["city"]]
    T = song["tiers"]
    parts = part_list(song)
    shared = "../" + ("../" if LANG == "en" else "")
    body = [f'<div class="hero" style="--accent:{city["color"]}">',
            board(song["id"], song["rows"], city, shared, parts=parts),
            f'<div><p class="eyebrow"><a href="../index.html#{city["slug"]}">{e(city["name"])}</a> · {e(song["genre"])}</p>'
            f'<h1>{e(song["title"])}</h1><p class="lead">{e(song["tagline"])}</p>'
            f'<p class="small mut">{e(song["artist"])} · {fmt_bpm(song["bpm"])} BPM · {fmt_time(song["play"])}'
            f'{" · " + t("song.dlc") if city["dlc"] else ""}</p><p>'
            + " ".join(lv_chip(k, T[k]["level"], T[k]["internal"]) for k, *_ in TIERS) + "</p>"]

    basis = song["basis"] if LANG == "ko" else song["basis_en"]
    motif = song["motif"] if LANG == "ko" else song["motif_en"]
    kv = [(t("song.city"), f'{city_chip(city)} <span class="mut small">{e(city["tagline"])}</span>'),
          (t("song.genre"), e(song["genre"])), (t("song.tempo"), f'{fmt_bpm(song["bpm"])} BPM'),
          (t("song.length"), f'{fmt_time(song["play"])} · {t("song.bars", n=T["extreme"]["bars"])}')]
    if basis:
        kv.append((t("song.sound"), e(basis)))
    if motif:
        kv.append((t("song.picture"), e(t("song.picture_note", motif=motif))))
    body.append('<dl class="kv" style="margin-top:14px">' + "".join(f"<dt>{k}</dt><dd>{v}</dd>" for k, v in kv) + "</dl></div></div>")

    # sections + fever
    body.append(f'<h2>{t("song.sections")}</h2><div class="card">')
    if parts:
        body.append('<ul class="parts">' + "".join(
            f'<li><button data-seek="{p["ms"]}"><span class="pt">▶ {e(t("song.bar", n=p["bar"] + 1))} · {fmt_time(p["ms"] / 1000)}</span>{e(p["name"])}</button></li>'
            for p in parts) + "</ul>")
    for fv in song["fever"]:
        s, n = fv["startBar"], fv["bars"]
        body.append(f'<p class="small" style="margin-top:10px"><b style="color:#ffd34d">FEVER</b> {e(t("song.fever", a=s + 1, b=s + n))}</p>')
    body.append("</div>")

    # tier cards
    body.append(f'<h2>{t("song.notes")}</h2><p class="mut small">{t("song.notes_lead")}</p><div class="tier-cards">')
    for key, label, rule, _ in TIERS:
        tt = T[key]
        c = TIER_COLOR[key]
        rk = ranks[key].get(song["id"])
        body.append(f'<div class="card tc" style="--tc:{c}"><h3>{tier_chip(key, label)}'
                    f'<span class="big" style="color:{c}">Lv {tt["level"]}</span>'
                    f'<button class="go" data-playtier="{key}">▶ {t("board.play").upper()}</button></h3>'
                    f'{density(tt["per_bar"], tt["bar_sec"], c, tt["peak_bar"])}'
                    f'<div style="display:flex;gap:14px;align-items:flex-start;margin-top:10px">{heat(tt["heat"], c)}'
                    f'<dl class="kv small"><dt>{t("song.k.blasts")}</dt><dd class="mono">{tt["blasts"]}</dd>'
                    f'<dt>{t("song.k.nps")}</dt><dd class="mono">{tt["nps"]:.2f}</dd>'
                    f'<dt>{t("song.k.cells")}</dt><dd class="mono">{tt["cells"]:.1f}</dd>'
                    f'<dt>{t("song.k.16th")}</dt><dd class="mono">{pct(tt["sixteenth"])}</dd>'
                    f'<dt>{t("song.k.lead")}</dt><dd class="mono">{tt["lead_sec"]:.2f}s</dd></dl></div>'
                    f'<ul class="plain small mut" style="margin-top:10px">'
                    + "".join(f"<li>{e(n)}</li>" for n in chart_notes(song, key)) +
                    f'</ul><p class="small dim">{e(t("song.rank", tier=label, n=len(ranks[key]), r=rk))}</p></div>')
    body.append("</div>")

    # score detail
    body.append(f'<h2>{t("song.score")}</h2><p class="mut">{t("song.score_lead")} <a href="../rules.html">{t("song.score_more")}</a></p>')
    body.append(f'<div class="tw"><table><thead><tr><th>{t("col.tier")}</th><th class="n">{t("col.blasts")}</th><th class="n">{t("col.unit")}</th>'
                f'<th class="n">{t("col.dodge")}</th><th class="n">COOL·JUST u</th><th class="n">BONUS 20u</th><th class="n">{t("col.hit")}</th>'
                f'<th class="n">{t("col.maxcool")}</th><th class="n">{t("col.infever")}</th><th class="n">{t("col.hitbudget")}</th></tr></thead><tbody>')
    for key, label, rule, _ in TIERS:
        tt = T[key]
        u = tt["unit"]
        body.append(f'<tr><td>{tier_chip(key, label)}</td>'
                    f'<td class="n">{tt["blasts"]}</td><td class="n">{u}</td><td class="n">{3 * u}</td><td class="n">{u}</td>'
                    f'<td class="n">{20 * u}</td><td class="n">−{10 * u}</td><td class="n">{tt["max_near"] or "–"}</td>'
                    f'<td class="n">{tt["near_fever"] if tt["near_fever"] is not None else "–"}</td>'
                    f'<td class="n">{tt["budget"]}</td></tr>')
    body.append("</tbody></table></div>")
    x = T["extreme"]
    note = t("song.score_note", ref=f'{x["ref"]:,}', base=f'{x["baseline"]:,}', cool=x["max_near"], fever=x["near_fever"])
    body.append(f'<p class="small mut">{e(note)}</p>')

    body.append(song_rewards(song, GEAR, None, SONG_WORDS))

    # courses
    extra = []
    for c, i, st in courses_by_song.get(song["id"], []):
        extra.append(f'<li><a href="../stepup.html#{c["id"]}">{e(t("song.course_stepup", title=c["title"]))}</a> · '
                     f'{e(t("song.course_pos", n=i + 1))} · {st["rule"]} · {e(need_text(st))}</li>')
    for s, i, st in starters_by_song.get(song["id"], []):
        extra.append(f'<li><a href="../stepup.html#starter-{s["band"].lower()}">{e(t("song.course_starter", title=s["title"]))}</a> · '
                     f'{e(t("song.course_step", n=i + 1))} · {st["rule"]}</li>')
    if extra:
        body.append(f'<h2>{t("song.courses")}</h2><ul class="plain">' + "".join(extra) + "</ul>")

    prev_next = NEIGHBOURS[song["id"]]
    body.append('<p style="margin-top:40px;display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap" class="small">'
                + (f'<a href="{prev_next[0]["id"]}.html">← {e(prev_next[0]["title"])}</a>' if prev_next[0] else "<span></span>")
                + (f'<a href="{prev_next[1]["id"]}.html">{e(prev_next[1]["title"])} →</a>' if prev_next[1] else "")
                + "</p>")
    desc = t("song.desc", title=song["title"], city=city["name"], bpm=fmt_bpm(song["bpm"]))
    return page(f"songs/{song['id']}.html", "index.html", song["title"], desc, "".join(body))


def index_page(songs, cities):
    shared = "../" if LANG == "en" else ""
    la = next(s for s in songs if s["id"] == "la1")
    body = [f'<div class="hero" style="--accent:{cities[la["city"]]["color"]}">',
            board("la1", la["rows"], cities[la["city"]], shared, demo=True),
            f'<div><p class="eyebrow">BeatBound Wiki</p><h1>{t("index.title")}</h1>'
            f'<p style="font-size:17px">{t("index.hero")}</p>'
            f'<p class="lead">{t("index.lead", songs=len(songs), cities=len(cities))}</p>'
            f'<p class="small dim">↖ {t("index.demo")} · <a href="songs/la1.html">{t("board.play")} →</a></p></div></div>',
            '<div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-top:34px">'
            f'<input class="search" id="q" type="search" placeholder="{t("index.search")}" aria-label="{t("index.search")}"></div>',
            f'<div class="filters" id="cities"><button class="on" data-c="">{t("index.all")}</button>']
    for c in cities.values():
        body.append(f'<button data-c="{c["slug"]}" id="{c["slug"]}" style="--c:{c["color"]}">{e(c["name"])}</button>')
    body.append(f'</div><div class="tw"><table id="songs"><thead><tr>'
                f'<th class="sort">{t("col.song")}</th><th class="sort">{t("col.city")}</th><th>{t("col.genre")}</th>'
                f'<th class="sort n">BPM</th><th class="sort n">{t("col.length")}</th>'
                + "".join(f'<th class="sort n">{lbl}</th>' for k, lbl, *_ in TIERS)
                + '</tr></thead><tbody>')
    for s in songs:
        c = cities[s["city"]]
        T = s["tiers"]
        body.append(f'<tr data-c="{c["slug"]}" data-q="{e((s["title"] + " " + s["genre"] + " " + c["name"]).lower())}">'
                    f'<td data-v="{e(s["title"].lower())}"><span class="songcell">{mini_led(s["rows"], c["color"])}'
                    f'<a href="songs/{s["id"]}.html">{e(s["title"])}</a></span></td>'
                    f'<td data-v="{s["city"]:02d}{s["number"]:04d}">{city_chip(c)}</td><td class="small mut">{e(s["genre"])}</td>'
                    f'<td class="n" data-v="{s["bpm"]}">{fmt_bpm(s["bpm"])}</td><td class="n" data-v="{s["play"]:.0f}">{fmt_time(s["play"])}</td>'
                    + "".join(f'<td class="n" data-v="{T[k]["internal"]:.3f}">{lv_chip(k, T[k]["level"], T[k]["internal"])}'
                              f' <span class="dim small">{T[k]["internal"]:.2f}</span></td>' for k, *_ in TIERS)
                    + "</tr>")
    body.append("</tbody></table></div>")
    body.append(f'<p class="small mut">{t("index.legend")}</p>')
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
    return page("index.html", "index.html", t("index.title"), t("index.desc"), "".join(body), script)


def stepup_page(songs, cities, courses, starters):
    by_id = {s["id"]: s for s in songs}
    rule_key = {"EASY": "easy", "NORMAL": "normal", "HARD": "hard", "EXTREME": "extreme"}
    body = [f'<p class="eyebrow">STEP UP</p><h1>{t("stepup.title")}</h1><p class="lead">{t("stepup.lead")}</p>',
            '<ul class="plain small mut">' + "".join(f"<li>{t('stepup.b' + str(i))}</li>" for i in range(1, 4)) + "</ul>"]
    total = 0
    for c in courses:
        total += c["bonus"]
        ints, rows = [], []
        for i, st in enumerate(c["stages"]):
            s = by_id[st["song"]]
            k = rule_key[st["rule"]]
            tt = s["tiers"][k]
            ints.append(tt["internal"])
            rows.append(f'<tr><td class="n">{i + 1}</td><td><span class="songcell">{mini_led(s["rows"], cities[s["city"]]["color"])}<a href="songs/{s["id"]}.html">{e(s["title"])}</a></span></td>'
                        f'<td>{city_chip(cities[s["city"]])}</td><td>{tier_chip(k, st["rule"])}</td>'
                        f'<td class="n">{lv_chip(k, tt["level"])}</td><td class="n">{tt["internal"]:.2f}</td><td>{e(need_text(st))}</td></tr>')
        pack = any(cities[by_id[st["song"]]["city"]]["dlc"] for st in c["stages"])
        body.append(f'<h2 id="{c["id"]}">{e(c["title"])} <span class="mono mut small">+{c["bonus"]:.2f}</span></h2>'
                    f'<p class="small mut">{t("stepup.avg", v=f"{sum(ints) / len(ints):.2f}")}{" · " + t("stepup.pack") if pack else ""}</p>'
                    f'<div class="tw"><table><thead><tr><th class="n">#</th><th>{t("col.song")}</th><th>{t("col.city")}</th><th>{t("col.tier")}</th><th class="n">Lv</th>'
                    f'<th class="n">{t("col.internal")}</th><th>{t("col.need")}</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table></div>")
    body.append(f'<p class="mut">{t("stepup.total", v=f"{total:.2f}")}</p>')
    body.append(f'<h2>{t("stepup.starters")}</h2><p class="lead">{t("stepup.starters_lead")}</p>')
    for s in starters:
        body.append(f'<h3 id="starter-{s["band"].lower()}">{e(s["title"])} <span class="mut small">· {t("starter." + s["band"])}</span></h3>'
                    f'<div class="tw"><table><thead><tr><th class="n">{t("col.step")}</th><th>{t("col.tier")}</th><th>{t("col.songs")}</th></tr></thead><tbody>')
        for i, st in enumerate(s["steps"]):
            k = rule_key[st["rule"]]
            links = " · ".join(f'<a href="songs/{sid}.html">{e(by_id[sid]["title"])}</a> '
                               f'<span class="dim small mono">{by_id[sid]["tiers"][k]["internal"]:.2f}</span>' for sid in st["songs"])
            body.append(f'<tr><td class="n">{i + 1}</td><td>{tier_chip(k, st["rule"])}</td><td>{links}</td></tr>')
        body.append("</tbody></table></div>")
    return page("stepup.html", "stepup.html", t("stepup.title"), t("stepup.desc"), "".join(body))


# ---------------------------------------------------------------- art: tier badges, gear icons, rule diagrams
BADGE_COLORS = ["#ff8034", "#c4e4ff", "#ffd630", "#5cffec", "#30ff88", "#5ca8ff", "#ff40c8"]
BADGE_FACE, BADGE_IVORY = "#0e121e", "#ecf2ff"


def _star(n, r0, r1, rot):
    pts = []
    for i in range(n * 2):
        a = rot + i * math.pi / n
        r = r1 if i % 2 else r0
        pts.append(f"{50 + r * math.cos(a):.1f},{50 + r * math.sin(a):.1f}")
    return f'<polygon points="{" ".join(pts)}"/>'


def _badge_shape(fam):
    return {0: '<circle cx="50" cy="50" r="40"/>',
            1: '<path d="M50 8 L87 19 V50 Q87 79 50 93 Q13 79 13 50 V19 Z"/>',
            2: _star(12, 43, 37, 0),
            3: _star(3, 43, 43, -math.pi / 2),
            4: '<polygon points="33,9 67,9 90,32 90,68 67,91 33,91 10,68 10,32"/>',
            5: '<polygon points="50,5 94,50 50,95 6,50"/>'}.get(fam, _star(8, 47, 31, -math.pi / 2))


def tier_badge(name, size=56, rim=False):
    """Game rank badge (Design/RankBadge/v2/tier_badge_v3.html): C2 outline for big, C3 rim for small."""
    idx = [n for n, _ in RATING_TIERS].index(name)
    fam = 6 if name == "MASTER" else idx // 3
    div = 0 if name == "MASTER" else idx % 3 + 1
    c = BADGE_COLORS[fam]
    sh = _badge_shape(fam)
    label = "M" if fam == 6 else ["I", "II", "III"][div - 1]
    shadow = f'<g transform="translate(0 5)" fill="#000" opacity=".6">{sh}</g>'
    if rim:
        fs = 30 if fam == 6 else 25 if div == 3 else 29
        inner = f'<g fill="{c}">{sh}</g><g transform="translate(50 50) scale(.74) translate(-50 -50)" fill="{BADGE_FACE}">{sh}</g>'
        text_fill = c
    else:
        fs = 34 if fam == 6 else 28 if div == 3 else 32
        inner = (f'<g fill="{BADGE_FACE}" stroke="{c}" stroke-width="4" stroke-linejoin="round">{sh}</g>'
                 f'<g transform="translate(50 50) scale(.8) translate(-50 -50)" fill="none" stroke="{c}" stroke-width="1.6" opacity=".45" stroke-linejoin="round">{sh}</g>')
        text_fill = BADGE_IVORY
    return (f'<svg class="badge" width="{size}" height="{size}" viewBox="0 0 100 105" aria-label="{name}" role="img">{shadow}{inner}'
            f'<text x="50" y="{50 + fs * .36:.1f}" text-anchor="middle" font-family="ui-sans-serif,-apple-system,Arial Black,sans-serif" '
            f'font-weight="900" font-size="{fs}" fill="{text_fill}">{label}</text></svg>')


LAUNCHPAD_SKINS = {
    "CLASSIC": ("linear-gradient(160deg,#1d1a2b,#0b0a12)", "#2f2a45"),
    "IVORY": ("linear-gradient(160deg,#f4ecd8,#cfc3a6)", "#fffaf0"),
    "CARBON": ("repeating-linear-gradient(45deg,#1b1b1f 0 4px,#26262c 4px 8px)", "#3a3a44"),
    "WALNUT": ("linear-gradient(160deg,#7a4a2a,#3e2414),repeating-linear-gradient(100deg,#0000 0 6px,#00000022 6px 7px)", "#a06a40"),
    "CHROME": ("linear-gradient(160deg,#f2f5fa,#8d97a8 45%,#e3e8f0 55%,#6f7889)", "#ffffff"),
    "GOLD": ("linear-gradient(160deg,#ffe58a,#c8901e 45%,#ffd45c 55%,#9a6a10)", "#fff1b8"),
}


def gear_icon(g, color):
    kind, name = g["kind"], g["name"]
    if kind == "character":
        return f'<canvas class="chr" data-char="{name}" width="128" height="128" style="--g:{color}" aria-label="{name}"></canvas>'
    if kind == "launchpad":
        body, rim = LAUNCHPAD_SKINS.get(name, LAUNCHPAD_SKINS["CLASSIC"])
        pads = "".join("<i></i>" for _ in range(9))
        return f'<span class="lp" style="--body:{body};--rim:{rim}"><span class="lp-dots"><i></i><i></i><i></i></span><span class="lp-pads">{pads}</span></span>'
    return f'<span class="strip" style="background-image:url(img/gear/{kind}-{name.lower()}.png)" aria-label="{name}"></span>'


def mini_board(cells, me=None, arrow=None, near=(), size=150, n=5, color="#ffe047"):
    """Rule diagram: n×n board, blast cells lit, the player cube, optional move arrow."""
    gap, pad = 4, 8
    cell = (size - pad * 2 - gap * (n - 1)) / n
    out = [f'<svg class="dia" viewBox="0 0 {size} {size}" width="{size}" height="{size}" role="img">',
           f'<rect width="{size}" height="{size}" rx="14" fill="#100e18" stroke="#2f2a45"/>']

    def xy(i):
        return pad + (i % n) * (cell + gap), pad + (i // n) * (cell + gap)
    for i in range(n * n):
        x, y = xy(i)
        lit = i in cells
        fill = color if lit else ("#2a2440" if i in near else "#1d1a2b")
        cls = ' class="boomcell"' if lit else ""
        out.append(f'<rect{cls} x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="5" fill="{fill}"/>')
        if i in near and not lit:
            out.append(f'<rect x="{x + 2:.1f}" y="{y + 2:.1f}" width="{cell - 4:.1f}" height="{cell - 4:.1f}" rx="4" fill="none" stroke="#5cffec" stroke-width="1.5" stroke-dasharray="3 3"/>')
    if arrow:
        (ax, ay), (bx, by) = xy(arrow[0]), xy(arrow[1])
        h = cell / 2
        out.append(f'<line x1="{ax + h:.1f}" y1="{ay + h:.1f}" x2="{bx + h:.1f}" y2="{by + h:.1f}" stroke="#fff" stroke-width="3" stroke-dasharray="4 4" marker-end="url(#ar)"/>')
        out.append('<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="5" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#fff"/></marker></defs>')
    if me is not None:
        x, y = xy(me)
        k = cell * .18
        out.append(f'<rect class="me" x="{x + k:.1f}" y="{y + k:.1f}" width="{cell - 2 * k:.1f}" height="{cell - 2 * k:.1f}" rx="5" fill="#00f0ff"/>')
    out.append("</svg>")
    return "".join(out)


def score_bar():
    """Rank cut ruler 0 … 1,000,000+ with the base cut of each rank."""
    marks = [("D", 0, "#8a83a3"), ("C", 400000, "#9aa4b8"), ("B", 500000, "#7aadff"), ("A", 600000, "#3de680"),
             ("S", 700000, "#ffc738"), ("SS", 800000, "#ff8a3d"), ("SSS", 900000, "#ff4dc7")]
    lo = 350000
    span = 1050000 - lo
    segs = []
    for i, (g, cut, col) in enumerate(marks):
        start = max(cut, lo)
        end = marks[i + 1][1] if i + 1 < len(marks) else 1050000
        left = (start - lo) / span * 100
        width = (end - start) / span * 100
        segs.append(f'<div class="seg" style="left:{left:.2f}%;width:{width:.2f}%;--c:{col}"><b>{g}</b><span>{cut // 1000}k</span></div>')
    plus = [(950000, "SSS+"), (980000, "SSS++"), (1000000, "1M")]
    ticks = "".join(f'<i class="tick{" mil" if v == 1000000 else ""}" style="left:{(v - lo) / span * 100:.2f}%;--h:{8 + k * 13}px"><em>{lbl} <span>{v // 1000}k</span></em></i>'
                    for k, (v, lbl) in enumerate(plus))
    return f'<div class="ruler">{"".join(segs)}{ticks}</div>'


def rules_page():
    rows = [(t("rules.r_dodge"), "3u", t("rules.r_dodge_d")), (t("rules.r_cool"), "u", t("rules.r_cool_d")),
            ("JUST", "u", t("rules.r_just_d")), ("BONUS", "20u", t("rules.r_bonus_d")), (t("rules.r_hit"), "−10u", t("rules.r_hit_d"))]
    blast = {5, 6, 7, 8, 9}          # a horizontal line through row 1
    figs = [
        (mini_board(blast, me=17), L("피함", "Dodge"), "3u", L("폭발 칸 밖에 있으면 피한 것", "Stand outside the lit cells")),
        (mini_board(blast, me=12, near={10, 11, 12, 13, 14}), "COOL", "+u", L("폭발 바로 옆 칸에서 피하면", "Dodge from a cell right next to the blast")),
        (mini_board(blast, me=12, arrow=(7, 12)), "JUST", "+u", L("터지기 0–150ms 전에 빠져나가면", "Leave the blast 0–150 ms before it goes off")),
        (mini_board(blast, me=7), L("피격", "Hit"), "−10u", L("터질 때 폭발 칸 안에 있으면", "Inside a lit cell when it goes off")),
    ]
    fig_html = '<div class="figs">' + "".join(
        f'<figure class="fig{" bad" if i == 3 else ""}">{svg}<figcaption><b>{name}</b> <span class="mono">{pts}</span><br><span class="small mut">{cap}</span></figcaption></figure>'
        for i, (svg, name, pts, cap) in enumerate(figs)) + "</div>"
    body = [f'<p class="eyebrow">Score &amp; Rank</p><h1>{t("rules.title")}</h1><p class="lead">{t("rules.lead")}</p>', fig_html,
            f'<h2>{t("rules.million")}</h2><p>{t("rules.million_text")}</p>',
            f'<div class="tw"><table><thead><tr><th>{t("col.item")}</th><th class="n">{t("col.points")}</th><th>{t("col.what")}</th></tr></thead><tbody>'
            + "".join(f'<tr><td>{a}</td><td class="n">{b}</td><td>{c}</td></tr>' for a, b, c in rows) + "</tbody></table></div>",
            f'<div class="formula">{e(t("rules.formula"))}</div><p class="small mut">{t("rules.formula_note")}</p>',
            f'<h2>{t("rules.cuts")}</h2><p>{t("rules.cuts_text")}</p>', score_bar(),
            f'<div class="tw"><table><thead><tr><th>{t("col.rankname")}</th><th class="n">{t("col.base")}</th><th class="n">+</th><th class="n">++</th></tr></thead><tbody>']
    d = dict(CUTS)
    for g in ["SSS", "SS", "S", "A", "B", "C", "D"]:
        body.append(f'<tr><td><b>{g}</b></td><td class="n">{d[g]:,}</td><td class="n">{d[g + "+"]:,}</td><td class="n">{d[g + "++"]:,}</td></tr>')
    body.append(f'</tbody></table></div><p class="small mut">{t("rules.cuts_note")}</p>')
    # difficulty cards with warning-length bars
    tiers = [("easy", None, 1.3), ("normal", None, 1.3), ("hard", None, 1.0), ("extreme", None, .65), ("perfect", "#ff4dc7", .65)]
    body.append(f'<h2>{t("rules.tiers")}</h2><div class="tiercards">')
    for key, color, lead in tiers:
        cells = t("rules.t_" + key).split("|")
        col = color or TIER_COLOR[key]
        body.append(f'<div class="tcard" style="--tc:{col}"><span class="chip" style="color:{col}">{key.upper()}</span>'
                    f'<div class="leadbar"><i style="width:{lead / 1.3 * 100:.0f}%"></i></div>'
                    f'<dl class="kv small"><dt>{t("col.warning")}</dt><dd>{cells[0]}</dd><dt>{t("col.hitbudget")}</dt><dd>{cells[1]}</dd>'
                    f'<dt>{t("col.unlock")}</dt><dd>{cells[2]}</dd></dl></div>')
    body.append(f'</div><p class="small mut">{t("rules.tiers_note")}</p>')
    body.append(f'<h2>{t("rules.fever")}</h2><div class="fever"><div class="fv-line">'
                + "".join(f'<i style="height:{h}%"></i>' for h in [20, 30, 25, 45, 40, 55, 50, 60, 70, 90, 95, 100, 92, 96, 100, 85, 50, 40, 35, 30, 45, 40, 30, 20])
                + f'</div><div class="fv-band" style="left:37.5%;width:33.3%"><b>FEVER</b> COOL·JUST ×2</div></div><p>{t("rules.fever_text")}</p>')
    return page("rules.html", "rules.html", t("rules.title"), t("rules.desc"), "".join(body))


ART_CSS = r"""
.strip{display:block;width:56px;height:56px;border-radius:10px;background-size:800% 100%;background-repeat:no-repeat;animation:strip 1.6s steps(7,end) infinite}
.gear:hover .strip{animation-duration:.8s}
@keyframes strip{from{background-position:0 0}to{background-position:100% 0}}
canvas.chr{width:56px;height:56px;display:block}
.lp{display:flex;flex-direction:column;gap:3px;width:56px;height:56px;padding:5px;border-radius:9px;background:var(--body);border:1.5px solid var(--rim);box-shadow:inset 0 1px 0 #ffffff30,0 3px 0 #0006}
.lp-dots{display:flex;gap:3px}.lp-dots i{width:5px;height:5px;border-radius:50%;background:var(--g);opacity:.8}
.lp-pads{flex:1;display:grid;grid-template-columns:repeat(3,1fr);gap:3px}.lp-pads i{border-radius:3px;background:#1d1a2bdd;box-shadow:inset 0 0 0 1px #ffffff12}
.gear:hover .lp-pads i:nth-child(odd){background:var(--g);box-shadow:0 0 6px var(--g)}
.badge{display:inline-block;vertical-align:middle;overflow:visible;transition:transform .25s cubic-bezier(.3,1.6,.5,1)}
.tw-t:hover .badge,.badge:hover{transform:scale(1.12) rotate(-4deg)}
.tw-t{flex-direction:row!important;align-items:center;gap:10px!important}.tw-t .tt{display:flex;flex-direction:column}
.rt-row{display:flex;align-items:center;gap:10px}
.figs{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:18px 0}
.fig{margin:0;background:var(--face);border:1px solid var(--line);border-radius:14px;padding:12px;display:flex;flex-direction:column;align-items:center;gap:8px;text-align:center}
.fig svg{max-width:100%;height:auto}.fig.bad .me{fill:#ff3b5c}.fig figcaption b{font-size:15px}
.dia .boomcell{animation:boomc 1.8s ease-out infinite}.dia .me{animation:hopme 1.8s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes boomc{0%,55%{opacity:.25}60%{opacity:1}100%{opacity:.25}}
@keyframes hopme{0%,50%,100%{transform:scale(1)}58%{transform:scale(1.15)}}
.ruler{position:relative;height:58px;margin:18px 0 64px;border-radius:10px;background:var(--face);border:1px solid var(--line)}
.ruler .seg{position:absolute;top:0;bottom:0;border-left:2px solid var(--c);background:linear-gradient(180deg,color-mix(in srgb,var(--c) 28%,transparent),transparent);padding:6px 6px;display:flex;flex-direction:column}
.ruler .seg b{color:var(--c);font:800 14px var(--mono)}.ruler .seg span{font:11px var(--mono);color:var(--muted)}
.ruler .tick{position:absolute;top:100%;width:1px;height:var(--h);background:var(--muted)}.ruler .tick em{position:absolute;top:calc(var(--h) + 1px);left:0;transform:translateX(-90%);font:700 10.5px var(--mono);color:var(--muted);font-style:normal;white-space:nowrap}
.ruler .tick em span{opacity:.7}.ruler .tick.mil{background:#fff}.ruler .tick.mil em{color:#fff}
.tiercards{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px;margin:10px 0}
.tcard{background:var(--face);border:1px solid var(--line);border-radius:14px;padding:12px 14px;display:flex;flex-direction:column;gap:8px;transition:border-color .2s}.tcard:hover{border-color:var(--tc)}
.leadbar{height:6px;border-radius:3px;background:#ffffff10;overflow:hidden}.leadbar i{display:block;height:100%;background:var(--tc);border-radius:3px}
.fever{position:relative;background:var(--face);border:1px solid var(--line);border-radius:14px;padding:14px;margin:10px 0}
.fv-line{display:flex;align-items:flex-end;gap:3px;height:70px}.fv-line i{flex:1;background:#5a5470;border-radius:2px 2px 0 0}
.fv-line i:nth-child(n+10):nth-child(-n+17){background:#ffd34d;box-shadow:0 0 8px #ffd34d88}
.fv-band{position:absolute;top:8px;font:700 11px var(--mono);color:#ffd34d;text-align:center}
.rank-tbl td.badgecell{width:40px}.lookup{display:flex;gap:8px;flex-wrap:wrap;margin:8px 0 12px}
.lookup input{font:15px var(--mono);color:var(--ink);background:var(--face2);border:1px solid var(--line);border-radius:8px;padding:8px 10px;width:180px}
.notice{border:1px dashed var(--line);border-radius:12px;padding:14px;color:var(--muted)}
"""

CHAR_JS = r"""<script src="characters.js?v=VER"></script><script>
(()=>{if(!window.BBChars)return;const cs=[...document.querySelectorAll('canvas.chr')];const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
const vis=new Set();const io=new IntersectionObserver(es=>es.forEach(e=>e.isIntersecting?vis.add(e.target):vis.delete(e.target)));cs.forEach(c=>io.observe(c));
const local=new Map();const t0=performance.now();
function draw(c,t){const x=c.getContext('2d'),w=c.width;const col=getComputedStyle(c).getPropertyValue('--g').trim()||'#00f0ff';
 const beatT=(t%(60/128))/(60/128);const hop=reduce?0:Math.max(0,1-beatT*4);x.setTransform(1,0,0,1,0,0);x.clearRect(0,0,w,w);
 x.translate(w/2,w/2+hop*-6);const s=(w*.78)/128*(1+hop*.06);x.scale(s,s);if(!local.has(c))local.set(c,{});BBChars.draw(x,c.dataset.char,col,t,local.get(c))}
function loop(now){const t=reduce?0.4:(now-t0)/1000;vis.forEach(c=>draw(c,t));if(!reduce)requestAnimationFrame(loop)}
cs.forEach(c=>draw(c,0.4));requestAnimationFrame(loop)})();</script>"""


# ---------------------------------------------------------------- collectibles (GEAR, plates, titles)
RULE_NAME = {"Easy": "EASY", "Normal": "NORMAL", "Hard": "HARD", "Extreme": "EXTREME", "Perfect": "PERFECT"}
RULE_KEY = {"EASY": "easy", "NORMAL": "normal", "HARD": "hard", "EXTREME": "extreme", "PERFECT": "perfect"}
TIER_COLOR.setdefault("perfect", "#ff4dc7")
GEAR_KINDS = [("character", "Character", "ECubeSkin"), ("launchpad", "Launchpad", "ELaunchpadSkin"),
              ("marker", "Fill", "EWarnFill"), ("frame", "Frame", "EWarnFrame")]


def load_gear():
    src = (SCRIPTS / "Gear" / "GearCatalog.cs").read_text(encoding="utf-8")
    src = src.split("Items = Scope(", 1)[1].split("});", 1)[0]
    items = []
    for m in re.finditer(r'(Fill|Frame|Character|Launchpad|LaunchpadCourse)\(E\w+\.(\w+)(?:, "(\w+)"(?:, ERuleSet\.(\w+))?)?\)', src):
        call, name, a, rule = m.groups()
        kind = {"Fill": "marker", "Frame": "frame", "Character": "character"}.get(call, "launchpad")
        item = dict(kind=kind, name=name.upper(), song=None, rule=None, course=None)
        if call == "LaunchpadCourse":
            item["course"] = a
        elif a:
            item["song"], item["rule"] = a, RULE_NAME[rule]
        items.append(item)
    return items


def load_loc(name):
    rows = {}
    for line in (GD / "Localization" / f"{name}.txt").read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        cols = line.split("\t")
        if len(cols) >= 3:
            rows[cols[0]] = dict(en=cols[1], ko=cols[2])
    return rows


def load_titles():
    tdir = SCRIPTS / "Title"
    skill = (tdir / "TitleSkillWords.cs").read_text(encoding="utf-8")
    words = []

    def add(group, wid, word, slot, mission, hidden=False):
        words.append(dict(group=group, id=int(wid), word=word, slot=slot, m=mission, hidden=hidden))

    body = skill.split("Skill()", 1)[1].split("Cities()", 1)[0]
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("yield return"):
            continue
        m = re.search(r'(\w+)\((\d+), "([^"]+)", (?:(F|B), )?(.*)\);', line)
        if not m:
            continue
        helper, wid, word, slot, rest = m.groups()
        if helper == "Grade":
            g = re.match(r"EGrade\.(\w+), (\d), (\d+)", rest)
            add("skill", wid, word, "F", ("grade", g.group(1), int(g.group(2)), int(g.group(3))))
        elif helper == "Charts":
            c = re.match(r'"([\w.]+)", (\d+)', rest)
            add("skill", wid, word, slot, ("perfect" if "perfect" in c.group(1) else "clear", int(c.group(2))))
        elif helper == "Best":
            b = re.match(r'"([^"]+)", TitleStats\.(\w+), (\d+)', rest)
            add("skill", wid, word, slot, ("best", b.group(1), int(b.group(3))))
        elif "ChartCountMission.Grade" in rest:
            g = re.search(r"EGrade\.(\w+), (\d), (\d+)", rest)
            add("skill", wid, word, slot, ("grade", g.group(1), int(g.group(2)), int(g.group(3))))
        elif "LevelClearMission" in rest:
            add("skill", wid, word, slot, ("level", int(re.search(r"\((\d+)\)", rest).group(1))))
        elif "StatMission" in rest:
            s = re.search(r'StatMission\("([^"]+)", (\d+), TitleStats\.(\w+)', rest)
            add("skill", wid, word, slot, ("stat", s.group(1), int(s.group(2)), s.group(3)))
        elif "CityCountMission" in rest:
            add("skill", wid, word, slot, ("cities", int(re.search(r"\((\d+)\)", rest).group(1))))
        elif "CourseCountMission" in rest:
            add("skill", wid, word, slot, ("courses", int(re.search(r"\((\d+)\)", rest).group(1))))
        elif "RatingMission" in rest:
            add("skill", wid, word, slot, ("rating", re.search(r"ERatingTier\.(\w+)", rest).group(1).upper()))
    names = re.search(r"string\[\] names = \{([^}]*)\}", skill).group(1)
    for i, n in enumerate(re.findall(r'"([^"]+)"', names)):
        add("city", 100 + i, n, "F", ("city", i))
    for m in re.finditer(r'new TitleWord\((\d+), "([^"]+)", (F|B), ETitleSource\.Plate, new PlateCountMission\((\d+)\)', skill):
        add("plate", m.group(1), m.group(2), m.group(3), ("plates", int(m.group(4))))
    hidden = skill.split("Hidden()", 1)[1]
    for m in re.finditer(r'Secret\((\d+), "([^"]+)", (F|B), "([\w.]+)", (\d+), TitleStats\.(\w+)', hidden):
        add("hidden", m.group(1), m.group(2), m.group(3), ("stat", m.group(4), int(m.group(5)), m.group(6)), True)
    for m in re.finditer(r'new TitleWord\((\d+), "([^"]+)", (F|B), ETitleSource\.Hidden, new SongTiersMission\(\)', hidden):
        add("hidden", m.group(1), m.group(2), m.group(3), ("stat", "title.mission.all_tiers", 1, "x"), True)
    song_words = {}
    for m in re.finditer(r'Song\("(\w+)", (\d+), "([^"]+)", (F|B), "([^"]+)", "([^"]+)"\)', (tdir / "TitleSongWords.cs").read_text(encoding="utf-8")):
        song_words[m.group(1)] = dict(clear=m.group(3), clear_slot=m.group(4), mood=m.group(5), motif=m.group(6))
    words.sort(key=lambda w: w["id"])
    return words, song_words


def mission_text(m, loc, cities):
    kind = m[0]
    if kind == "clear":
        return L(f"채보 {m[1]}개 클리어", f"Clear {m[1]} chart{'s' if m[1] > 1 else ''}")
    if kind == "perfect":
        return L(f"PERFECT로 {m[1]}개 클리어", f"Clear {m[1]} on PERFECT")
    if kind == "grade":
        g = m[1] + "+" * m[2]
        return L(f"{g} 이상으로 채보 {m[3]}개", f"{m[3]} chart{'s' if m[3] > 1 else ''} at {g} or better")
    if kind == "level":
        return L(f"Lv{m[1]} 이상 채보 클리어", f"Clear a Lv{m[1]}+ chart")
    if kind == "best":
        fmt = loc[m[1]][LANG] if m[1] in loc else (L("한 판에 ", "") + m[1] + L("", " in a play"))
        return fmt.replace("{0}", f"{m[2]:,}")
    if kind == "stat":
        label, n, stat = m[1], m[2], m[3]
        if stat == "BestBonus":
            return L(f"한 판에 BONUS {n}", f"BONUS {n} in a play")
        text = loc[label][LANG] if label in loc else label
        if label == "NEAR MISS":
            text = "COOL (NEAR MISS)"
        return text + (f" ×{n:,}" if n > 1 else "")
    if kind == "cities":
        return L(f"{m[1]}개 도시에서 곡 클리어", f"Clear songs in {m[1]} cities")
    if kind == "courses":
        return L(f"STEP UP {m[1]}코스 통과", f"Pass {m[1]} STEP UP course{'s' if m[1] > 1 else ''}")
    if kind == "rating":
        return L(f"레이팅 {m[1]} 달성", f"Reach {m[1]} rating")
    if kind == "plates":
        return L(f"플레이트 {m[1]}개 모으기", f"Collect {m[1]} plate{'s' if m[1] > 1 else ''}")
    if kind == "city":
        return L(f"{cities[m[1]]['name']}에서 곡 하나 클리어", f"Clear a song in {cities[m[1]]['name']}")
    return ""


def plus_rule(rule):
    return rule if rule == "PERFECT" else rule + "+"


def gear_condition(item, by_id, courses, base):
    if item["course"]:
        title = next((c["title"] for c in courses if c["id"] == item["course"]), item["course"].upper())
        return f'<a href="{base}stepup.html#{item["course"]}">{e(t("gear.course", title=title))}</a>'
    if not item["song"]:
        return f'<span class="dim">{t("gear.default")}</span>'
    s = by_id[item["song"]]
    k = RULE_KEY[item["rule"]]
    return (f'<a href="{base}songs/{s["id"]}.html">{e(s["title"])}</a> '
            f'<span class="chip" style="color:{TIER_COLOR[k]}">{plus_rule(item["rule"])}</span>')


def gear_page(songs, cities, courses, gear, titles, song_words, loc):
    by_id = {s["id"]: s for s in songs}
    body = [f'<p class="eyebrow">GEAR</p><h1>{t("gear.title")}</h1><p class="lead">{t("gear.lead")}</p>',
            '<ul class="plain small mut">' + "".join(f"<li>{t('gear.b' + str(i))}</li>" for i in (1, 2, 3)) + "</ul>",
            f'<p class="small" style="display:flex;gap:10px;align-items:center;flex-wrap:wrap"><span class="mut">{t("gear.spoiler")}</span>'
            f'<button class="reveal-all">{t("gear.reveal_all")}</button></p>',
            '<nav class="jump">' + "".join(f'<a href="#{k}">{t("gear.kind." + k)}</a>' for k, *_ in GEAR_KINDS)
            + f'<a href="#plates">{t("gear.plates")}</a><a href="#titles">{t("gear.titles")}</a></nav>']
    for kind, *_ in GEAR_KINDS:
        items = [g for g in gear if g["kind"] == kind]
        body.append(f'<h2 id="{kind}">{t("gear.kind." + kind)} <span class="mono mut small">{len(items)}</span></h2>'
                    f'<p class="mut small">{t("gear.kind." + kind + "_d")}</p><div class="gear-grid">')
        for g in items:
            secret = g["name"] == "NONE"
            color = cities[by_id[g["song"]]["city"]]["color"] if g["song"] else ("#ffd34d" if g["course"] else "#00f0ff")
            body.append(f'<div class="gear{" secret" if secret else ""}" style="--g:{color}" tabindex="0">'
                        f'{gear_icon(g, color)}<b>{e(g["name"])}</b>'
                        f'<span class="gc">{gear_condition(g, by_id, courses, "")}</span></div>')
        body.append("</div>")
        if kind == "frame":
            body.append(f'<p class="small mut secret-line" tabindex="0"><span>{t("gear.stealth")}</span></p>')

    # plates and pins
    counts = Counter(s["city"] for s in songs)
    body.append(f'<h2 id="plates">{t("gear.plates")}</h2><p class="mut small">{t("gear.plates_d")}</p>'
                f'<div class="tw"><table><thead><tr><th>{t("col.city")}</th><th class="n">{t("col.songs")}</th>'
                f'<th>{t("gear.plate_col")}</th>' + "".join(f'<th>{g} PIN</th>' for g in ("A", "S", "SS", "SSS")) + "</tr></thead><tbody>")
    for num, c in cities.items():
        if not counts.get(num):
            continue
        body.append(f'<tr><td>{city_chip(c)}</td><td class="n">{counts[num]}</td><td>{t("gear.plate_cond")}</td>'
                    + "".join(f'<td class="small">{t("gear.pin_cond", g=g)}</td>' for g in ("A", "S", "SS", "SSS")) + "</tr>")
    body.append("</tbody></table></div>")

    # titles
    body.append(f'<h2 id="titles">{t("gear.titles")}</h2><p class="mut small">{t("gear.titles_d")}</p>')

    def words_table(group, heading, note=None):
        ws = [w for w in titles if w["group"] == group]
        if not ws:
            return
        body.append(f'<h3>{heading} <span class="mono mut small">{len(ws)}</span></h3>' + (f'<p class="mut small">{note}</p>' if note else ""))
        body.append(f'<div class="tw"><table><thead><tr><th>{t("gear.word")}</th><th>{t("gear.front")}/{t("gear.back")}</th>'
                    f'<th>{t("gear.mission")}</th></tr></thead><tbody>')
        for w in ws:
            cls = ' class="secret" tabindex="0"' if w["hidden"] else ""
            body.append(f'<tr{cls}><td><b class="word">{e(w["word"])}</b></td><td class="small mut">{t("gear.front") if w["slot"] == "F" else t("gear.back")}</td>'
                        f'<td><span class="sv">{e(mission_text(w["m"], loc, cities))}</span></td></tr>')
        body.append("</tbody></table></div>")

    words_table("skill", t("gear.t.skill"))
    words_table("city", t("gear.t.city"))
    body.append(f'<h3>{t("gear.t.song")} <span class="mono mut small">{len(song_words) * 3}</span></h3><p class="mut small">{t("gear.t.song_d")}</p>'
                f'<div class="tw"><table><thead><tr><th>{t("col.song")}</th><th>{t("gear.w.normal")}</th><th>{t("gear.w.sss")} · {t("gear.front")}</th>'
                f'<th>{t("gear.w.extreme")} · {t("gear.back")}</th></tr></thead><tbody>')
    for s in songs:
        w = song_words.get(s["id"])
        if not w:
            continue
        slot = t("gear.front") if w["clear_slot"] == "F" else t("gear.back")
        body.append(f'<tr><td><span class="songcell">{mini_led(s["rows"], cities[s["city"]]["color"])}<a href="songs/{s["id"]}.html">{e(s["title"])}</a></span></td>'
                    f'<td><b class="word">{e(w["clear"])}</b> <span class="dim small">{slot}</span></td><td><b class="word">{e(w["mood"])}</b></td>'
                    f'<td><b class="word">{e(w["motif"])}</b></td></tr>')
    body.append("</tbody></table></div>")
    words_table("plate", t("gear.t.plate"))
    words_table("hidden", t("gear.t.hidden"), t("gear.t.hidden_d"))
    script = CHAR_JS.replace("characters.js", ("../" if LANG == "en" else "") + "characters.js").replace("VER", VERSION)
    return page("gear.html", "gear.html", t("gear.title"), t("gear.desc"), "".join(body), script)


def song_rewards(song, gear, courses, song_words):
    rows = []
    for g in gear:
        if g["song"] == song["id"]:
            k = RULE_KEY[g["rule"]]
            label = {"character": L("캐릭터", "Character"), "marker": L("마커", "Marker"), "frame": L("프레임", "Frame")}[g["kind"]]
            secret = g["name"] == "NONE"
            rows.append(f'<li{" class=secret tabindex=0" if secret else ""}><span class="chip" style="color:{TIER_COLOR[k]}">{plus_rule(g["rule"])}</span> {label} <b>{e(g["name"])}'
                        f'{" · " + L("스텔스", "stealth") if secret else ""}</b></li>')
    w = song_words.get(song["id"])
    if w:
        rows.append(f'<li><span class="chip" style="color:{TIER_COLOR["normal"]}">NORMAL+</span> {L("칭호", "Title")} <b>{e(w["clear"])}</b></li>')
        rows.append(f'<li><span class="chip" style="color:#ffd34d">SSS</span> {L("칭호", "Title")} <b>{e(w["mood"])}</b></li>')
        rows.append(f'<li><span class="chip" style="color:{TIER_COLOR["extreme"]}">EXTREME+</span> {L("칭호", "Title")} <b>{e(w["motif"])}</b></li>')
    if not rows:
        return ""
    return f'<h2>{t("song.rewards")}</h2><ul class="rewards">' + "".join(rows) + f'</ul><p class="small"><a href="../gear.html">GEAR →</a></p>'


def rating_page(songs, cities, courses):
    vals = sorted((s["tiers"][k]["internal"], s, k) for s in songs for k, *_ in TIERS)[::-1]
    top = [v for v, *_ in vals[:20]]
    chart_max = sum(v / 10 for v in top[:5]) + sum(v / 30 for v in top[5:20])
    data = dict(songs=[dict(id=s["id"], t=s["title"], c=cities[s["city"]]["color"],
                            lv={k: round(s["tiers"][k]["internal"], 3) for k, *_ in TIERS}) for s in songs],
                courses=[dict(t=c["title"], b=c["bonus"]) for c in courses],
                tiers=[dict(n=n, lo=lo, c=tier_color(n), b=tier_badge(n, 40)) for n, lo in RATING_TIERS],
                tierColors={k: TIER_COLOR[k] for k, *_ in TIERS})
    weights = "".join(f'<i class="{"h" if i < 5 else "t"}" title="#{i + 1} · {"10%" if i < 5 else "3.3%"}"></i>' for i in range(20))
    ladder = "".join(f'<i style="--c:{tier_color(n)};flex:{(RATING_TIERS[i + 1][1] if i + 1 < len(RATING_TIERS) else 11) - lo}" title="{n} · {lo:.2f}+"></i>'
                     for i, (n, lo) in enumerate(RATING_TIERS))
    body = [f'<p class="eyebrow">Rating</p><h1>{t("rating.title")}</h1><p class="lead">{t("rating.lead")}</p>',
            f'<h2>{t("rating.glance")}</h2>',
            '<div class="eq">'
            f'<div class="eqc"><span class="eqn">8.52</span><span>{t("rating.g1")}</span></div><span class="op">×</span>'
            f'<div class="eqc"><span class="eqn">0.95</span><span>{t("rating.g2")}</span></div><span class="op">=</span>'
            f'<div class="eqc hi"><span class="eqn">8.094</span><span>{t("rating.g3")}</span></div></div>',
            f'<div class="weights" aria-hidden="true">{weights}</div><p class="small mut">{t("rating.weights")}</p>',
            f'<div class="formula">{e(t("rating.formula_text"))}</div>',
            # calculator
            f'<h2 id="calc">{t("rating.calc")}</h2><p class="mut small">{t("rating.calc_d")}</p>',
            '<div class="calc card"><div class="calc-out">'
            f'<div><span class="eyebrow">{t("rating.result")}</span><div class="big-rating" id="rv">0.00</div>'
            '<div class="rt-row"><span id="rb"></span><span class="chip" id="rt">BRONZE I</span></div><span class="small mut" id="rn"></span></div>'
            f'<div class="ladder">{ladder}<b id="rm"></b></div><p class="small mono mut" id="req"></p></div>'
            f'<span class="eyebrow">{t("rating.lookup")}</span><div class="lookup"><input id="lk" maxlength="8" placeholder="NICKNAME" aria-label="{t("rating.lookup")}">'
            f'<button class="btn" id="lkb">{t("rating.lookup_btn")}</button><span class="small mut" id="lkm"></span></div>'
            f'<div class="calc-rows"><table><thead><tr><th class="n">{t("rating.slot")}</th><th>{t("rating.song")}</th><th>{t("col.tier")}</th>'
            f'<th class="n">{t("rating.score")}</th><th class="n">{t("rating.value")}</th><th></th></tr></thead><tbody id="rows"></tbody></table></div>'
            f'<p style="display:flex;gap:8px;flex-wrap:wrap"><button class="btn" id="add">{t("rating.add")}</button>'
            f'<button class="btn" id="sample">{t("rating.sample")}</button><button class="btn ghost" id="clr">{t("rating.clear")}</button></p>'
            f'<div class="grid g2"><div><span class="eyebrow">{t("rating.courses")}</span><div class="cks" id="cks"></div></div>'
            f'<div><span class="eyebrow">{t("rating.ladder")}</span><div class="cks" id="lad"></div></div></div></div>',
            f'<h2>{t("rating.rules")}</h2><ul class="plain">' + "".join(f"<li>{t('rating.b' + str(i))}</li>" for i in range(1, 8)) + "</ul>"]
    body.append(f'<h2>{t("rating.tiers")}</h2><div class="tierwall">')
    for i, (n, lo) in enumerate(RATING_TIERS):
        rng = f"{lo:.2f} ~ {RATING_TIERS[i + 1][1] - .01:.2f}" if i + 1 < len(RATING_TIERS) else f"{lo:.2f} +"
        body.append(f'<div class="tw-t" style="--c:{tier_color(n)}">{tier_badge(n, 46)}<span class="tt"><b>{n}</b><span class="mono">{rng}</span></span></div>')
    body.append(f'</div><p class="small mut">{t("rating.tiers_note")}</p>')
    ladder_rows = "".join(f'<tr><td>{t("ladder.r" + str(i))}</td><td class="n">{b}</td></tr>' for i, b in enumerate(["0.5", "0.4", "0.3", "0.2", "0.1"], 1))
    body.append(f'<h2>{t("rating.bonus")}</h2><div class="grid g2"><div class="card"><h3 style="margin-top:0">{t("rating.bonus_stepup")}</h3>'
                f'<p class="small">{t("rating.bonus_stepup_text")} <a href="stepup.html">{t("rating.courses_link")}</a></p></div>'
                f'<div class="card"><h3 style="margin-top:0">{t("rating.bonus_ladder")}</h3><p class="small">{t("rating.bonus_ladder_text")}</p>'
                f'<div class="tw"><table><thead><tr><th>{t("col.rank")}</th><th class="n">{t("col.bonus")}</th></tr></thead><tbody>{ladder_rows}</tbody></table></div>'
                f'<p class="small mut">{t("rating.ladder_note")}</p></div></div>')
    ma, mb = f'<b class="mono">{chart_max:.3f}</b>', f'<b class="mono">{chart_max + 1:.3f}</b>'
    body.append(f'<h2>{t("rating.max")}</h2><p>{t("rating.max_text", a=ma, b=mb)}</p>')
    body.append(f'<h2>{t("rating.top")}</h2><div class="tw"><table><thead><tr><th class="n">#</th><th>{t("col.song")}</th><th>{t("col.tier")}</th>'
                f'<th class="n">{t("col.internal")}</th><th class="n">{t("col.shownlv")}</th></tr></thead><tbody>')
    for i, (v, s, k) in enumerate(vals[:20]):
        body.append(f'<tr><td class="n">{i + 1}</td><td><span class="songcell">{mini_led(s["rows"], cities[s["city"]]["color"])}<a href="songs/{s["id"]}.html">{e(s["title"])}</a></span></td>'
                    f'<td>{tier_chip(k)}</td><td class="n">{v:.3f}</td><td class="n">{s["tiers"][k]["level"]}</td></tr>')
    body.append('</tbody></table></div>')
    script = ("<script>window.RD=" + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";window.RL="
              + json.dumps(dict(next=t("rating.next", tier="{tier}", n="{n}"), ok=t("rating.lookup_ok", name="{name}", n="{n}"), none=t("rating.lookup_none")), ensure_ascii=False)
              + ";</script>" + CALC_JS + LOOKUP_JS.replace("'API'", "'" + API_BASE + "'"))
    return page("rating.html", "rating.html", t("rating.title"), t("rating.desc"), "".join(body), script)


CALC_JS = r"""<script>
(()=>{const D=window.RD,KEY='bbwiki.rating.v1',tiers=['easy','normal','hard','extreme'];
let st={rows:[],courses:[],ladder:0};try{const s=JSON.parse(localStorage.getItem(KEY));if(s&&s.rows)st=s}catch(e){}
const byId=Object.fromEntries(D.songs.map(s=>[s.id,s]));const tb=document.getElementById('rows');
function save(){try{localStorage.setItem(KEY,JSON.stringify(st))}catch(e){}}
function val(r){const s=byId[r.id];if(!s)return 0;return s.lv[r.tier]*Math.min(1,Math.max(0,r.score)/1e6)}
function trunc(x){return (Math.floor(x*100+1e-4)/100).toFixed(2)}
function tierOf(x){let t=D.tiers[0];for(const k of D.tiers)if(x>=k.lo)t=k;return t}
function render(){st.rows.sort((a,b)=>val(b)-val(a));tb.innerHTML='';const vals=st.rows.map((r,i)=>({i,v:val(r)})).sort((a,b)=>b.v-a.v);const rank={};vals.forEach((o,k)=>rank[o.i]=k+1);
 st.rows.forEach((r,i)=>{const tr=document.createElement('tr');const rk=rank[i];tr.className=rk<=5?'top5':rk<=20?'top20':'out';
  tr.innerHTML='<td class="n">'+(rk<=20?'#'+rk:'–')+'</td><td><select class="s">'+D.songs.map(s=>'<option value="'+s.id+'"'+(s.id===r.id?' selected':'')+'>'+s.t+'</option>').join('')+'</select></td>'+
  '<td><select class="t">'+tiers.map(t=>'<option value="'+t+'"'+(t===r.tier?' selected':'')+'>'+t.toUpperCase()+' '+byId[r.id].lv[t].toFixed(2)+'</option>').join('')+'</select></td>'+
  '<td class="n"><input class="sc" type="number" min="0" max="1100000" step="1000" value="'+r.score+'"></td><td class="n mono">'+val(r).toFixed(3)+'</td><td><button class="x" aria-label="remove">×</button></td>';
  tr.querySelector('.t').style.color=D.tierColors[r.tier];
  tr.querySelector('.s').onchange=e=>{r.id=e.target.value;save();render()};tr.querySelector('.t').onchange=e=>{r.tier=e.target.value;save();render()};
  tr.querySelector('.sc').onchange=e=>{r.score=+e.target.value||0;save();render()};tr.querySelector('.x').onclick=()=>{st.rows.splice(i,1);save();render()};tb.appendChild(tr)});
 const sorted=vals.map(o=>o.v);let head=0,tail=0;sorted.slice(0,20).forEach((v,k)=>{if(k<5)head+=v/10;else tail+=v/30});
 const bonus=Math.min(.5,st.courses.reduce((a,i)=>a+D.courses[i].b,0))+st.ladder;const total=head+tail+bonus;
 const rv=document.getElementById('rv');const old=parseFloat(rv.textContent)||0;const target=total;const t0=performance.now();
 const tok=(rv._tok=(rv._tok||0)+1);(function anim(now){if(rv._tok!==tok)return;const k=Math.min(1,(now-t0)/450);const x=old+(target-old)*(1-Math.pow(1-k,3));rv.textContent=trunc(k<1?x:target);if(k<1)requestAnimationFrame(anim)})(t0);setTimeout(()=>{if(rv._tok===tok)rv.textContent=trunc(target)},520);
 const tr=tierOf(total);const chip=document.getElementById('rt');chip.textContent=tr.n;chip.style.color=tr.c;rv.style.color=tr.c;document.getElementById('rb').innerHTML=tr.b;
 const nx=D.tiers.find(k=>k.lo>total);document.getElementById('rn').textContent=nx?window.RL.next.replace('{tier}',nx.n).replace('{n}',(nx.lo-total).toFixed(2)):'';
 document.getElementById('rm').style.left=Math.min(100,total/11*100)+'%';
 document.getElementById('req').textContent=head.toFixed(3)+' + '+tail.toFixed(3)+' + '+bonus.toFixed(2)+' = '+total.toFixed(3);}
document.getElementById('add').onclick=()=>{const used=new Set(st.rows.map(r=>r.id+r.tier));const s=D.songs.find(s=>!used.has(s.id+'hard'))||D.songs[0];st.rows.push({id:s.id,tier:'hard',score:950000});save();render()};
document.getElementById('clr').onclick=()=>{st={rows:[],courses:[],ladder:0};save();build();render()};
document.getElementById('sample').onclick=()=>{const pick=[...D.songs].sort((a,b)=>b.lv.hard-a.lv.hard).slice(26,46);
 st.rows=pick.map((s,i)=>({id:s.id,tier:i<3?'extreme':'hard',score:[952000,918000,884000,861000,903000,842000][i%6]}));st.courses=[0,1];st.ladder=0;save();build();render()};
function build(){const ck=document.getElementById('cks');ck.innerHTML='';D.courses.forEach((c,i)=>{const b=document.createElement('button');b.className='pill'+(st.courses.includes(i)?' on':'');b.textContent=c.t+' +'+c.b.toFixed(2);
  b.onclick=()=>{const j=st.courses.indexOf(i);j<0?st.courses.push(i):st.courses.splice(j,1);b.classList.toggle('on');save();render()};ck.appendChild(b)});
 const ld=document.getElementById('lad');ld.innerHTML='';[0,.1,.2,.3,.4,.5].forEach(v=>{const b=document.createElement('button');b.className='pill'+(st.ladder===v?' on':'');b.textContent=v.toFixed(1);
  b.onclick=()=>{st.ladder=v;ld.querySelectorAll('.pill').forEach(x=>x.classList.toggle('on',x===b));save();render()};ld.appendChild(b)})}
window.BBCalc={load(rows,ladder){st.rows=rows;st.ladder=ladder;save();build();render()}};
if(new URLSearchParams(location.search).get('name')){build();render()}else if(!st.rows.length){document.getElementById('sample').click()}else{build();render()}
})();</script>"""

COLLECT_CSS = r"""
.jump{display:flex;flex-wrap:wrap;gap:6px;margin:14px 0}.jump a{text-decoration:none;font:700 12px var(--mono);color:var(--muted);border:1px solid var(--line);border-radius:999px;padding:6px 12px}
.jump a:hover{color:var(--ink);border-color:var(--ink)}
.gear-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px;margin:10px 0}
.gear{position:relative;background:var(--face);border:1px solid var(--line);border-radius:14px;padding:14px 12px 12px;display:flex;flex-direction:column;gap:6px;transition:transform .2s,border-color .2s,box-shadow .2s}
.gear:hover{transform:translateY(-3px);border-color:var(--g);box-shadow:0 8px 24px color-mix(in srgb,var(--g) 25%,transparent)}
.gear b{font:800 15px var(--mono);letter-spacing:.04em}.gear .gc{font-size:12.5px;color:var(--muted)}
.gi{width:44px;height:44px;border-radius:11px;border:2px solid var(--g);background:color-mix(in srgb,var(--g) 18%,transparent);position:relative}
.gi-character:after{content:"";position:absolute;inset:9px;border-radius:5px;background:var(--g);box-shadow:0 0 10px var(--g)}
.gi-launchpad{display:grid;grid-template-columns:repeat(3,1fr);gap:3px;padding:5px;background-image:radial-gradient(circle,var(--g) 0 3px,transparent 3.5px);background-size:12px 12px;background-position:6px 6px}
.gi-marker:after{content:"";position:absolute;inset:7px;border-radius:5px;background:var(--g);transform:scale(.3);animation:fillup 1.6s ease-in infinite}
.gi-frame{background:none;border-style:dashed;animation:spinf 6s linear infinite}
.gear:hover .gi{animation-duration:.8s}
@keyframes fillup{0%{transform:scale(.25);opacity:.3}85%{transform:scale(1);opacity:1}100%{transform:scale(1);opacity:0}}
@keyframes spinf{to{transform:rotate(360deg)}}
.secret b,.secret .gc,.secret .word,.secret .sv,.secret-line span{filter:blur(6px);transition:filter .3s;user-select:none}
.secret,.secret-line{cursor:pointer}.secret.shown b,.secret.shown .gc,.secret.shown .word,.secret.shown .sv,.secret-line.shown span{filter:none;user-select:auto}
.reveal-all,.btn{font:700 12px var(--mono);color:#000;background:var(--accent);border:0;border-radius:8px;padding:8px 12px;cursor:pointer}.btn.ghost{background:none;color:var(--muted);border:1px solid var(--line)}
.word{font-family:var(--mono);letter-spacing:.02em}
ul.rewards{list-style:none;padding:0;display:grid;gap:6px;grid-template-columns:repeat(auto-fill,minmax(240px,1fr))}ul.rewards li{background:var(--face);border:1px solid var(--line);border-radius:10px;padding:8px 10px}
.eq{display:flex;align-items:stretch;gap:10px;flex-wrap:wrap;margin:10px 0 18px}.eqc{flex:1;min-width:150px;background:var(--face);border:1px solid var(--line);border-radius:14px;padding:14px 16px;display:flex;flex-direction:column;gap:2px;font-size:13px;color:var(--muted)}
.eqc .eqn{font:800 30px/1.1 var(--mono);color:var(--ink)}.eqc.hi{border-color:var(--accent);box-shadow:0 0 22px color-mix(in srgb,var(--accent) 25%,transparent)}.eqc.hi .eqn{color:var(--accent)}
.op{align-self:center;font:800 24px var(--mono);color:var(--dim)}
.weights{display:flex;align-items:flex-end;gap:4px;height:70px;margin:8px 0}.weights i{flex:1;border-radius:4px 4px 0 0;background:var(--accent);transition:transform .2s;transform-origin:bottom}
.weights i.h{height:100%}.weights i.t{height:33%;opacity:.55}.weights i:hover{transform:scaleY(1.08);opacity:1}
.calc-out{display:grid;grid-template-columns:auto 1fr;gap:12px 28px;align-items:center;margin-bottom:14px}
.big-rating{font:800 56px/1 var(--mono);letter-spacing:-.02em;transition:color .3s}
.ladder{position:relative;display:flex;height:16px;border-radius:999px;overflow:visible;gap:2px}.ladder i{background:var(--c);opacity:.75;border-radius:3px}.ladder i:first-child{border-radius:999px 3px 3px 999px}.ladder i:last-child{border-radius:3px 999px 999px 3px}
.ladder b{position:absolute;top:-7px;width:4px;height:30px;margin-left:-2px;border-radius:2px;background:#fff;box-shadow:0 0 10px #fff;transition:left .45s cubic-bezier(.2,.9,.3,1.1)}
#req{grid-column:1/-1;margin:0}
.calc-rows{overflow-x:auto;border:1px solid var(--line);border-radius:12px;margin:8px 0 12px}
.calc-rows select,.calc-rows input{font:13px var(--sans);color:var(--ink);background:var(--face2);border:1px solid var(--line);border-radius:7px;padding:5px 6px;max-width:190px}
.calc-rows input{width:110px;text-align:right;font-family:var(--mono)}
.calc-rows tr.top5 td:first-child{color:var(--accent);font-weight:800}.calc-rows tr.out{opacity:.45}
.calc-rows .x{background:none;border:0;color:var(--dim);font-size:18px;cursor:pointer}.calc-rows .x:hover{color:#ff5c8a}
.cks{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px}.pill{font:700 12px var(--mono);color:var(--muted);background:var(--face2);border:1px solid var(--line);border-radius:999px;padding:6px 10px;cursor:pointer}
.pill.on{color:#000;background:var(--accent);border-color:var(--accent)}
.tierwall{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px;margin:10px 0}
.tw-t{border:1px solid color-mix(in srgb,var(--c) 45%,transparent);border-radius:12px;padding:10px 12px;display:flex;flex-direction:column;gap:2px;background:color-mix(in srgb,var(--c) 8%,var(--face));transition:transform .2s,box-shadow .2s}
.tw-t:hover{transform:translateY(-2px);box-shadow:0 0 18px color-mix(in srgb,var(--c) 40%,transparent)}.tw-t b{color:var(--c);font:800 13px var(--mono);letter-spacing:.04em}.tw-t span{font-size:12.5px;color:var(--muted)}
@media(max-width:640px){.calc-out{grid-template-columns:1fr}.big-rating{font-size:44px}.op{display:none}}
"""


# ---------------------------------------------------------------- ranking (live, from api.memegames.dev)
API_BASE = "https://api.memegames.dev"


def ranking_page(songs, cities):
    tiers = [dict(n=n, lo=lo, c=tier_color(n), b=tier_badge(n, 34, rim=True)) for n, lo in RATING_TIERS]
    body = [f'<p class="eyebrow">Ranking</p><h1>{t("ranking.title")}</h1><p class="lead">{t("ranking.lead")}</p>',
            f'<p class="small mut">{t("ranking.note")}</p>',
            f'<div class="lookup"><input id="rq" type="search" maxlength="8" placeholder="{t("ranking.search")}" aria-label="{t("ranking.search")}"></div>',
            f'<div class="tw"><table class="rank-tbl"><thead><tr><th class="n">#</th><th></th><th>{t("col.player")}</th>'
            f'<th class="n">{t("col.total")}</th><th class="n">{t("col.charts")}</th></tr></thead><tbody id="rk"><tr><td colspan="5" class="mut">{t("ranking.loading")}</td></tr></tbody></table></div>',
            f'<p><button class="btn ghost" id="more" hidden>{t("ranking.more")}</button></p>']
    labels = dict(offline=t("ranking.offline"), empty=t("ranking.empty"))
    script = ("<script>window.RK=" + json.dumps(dict(api=API_BASE, tiers=tiers, l=labels), ensure_ascii=False, separators=(",", ":")) + ";</script>" + r"""<script>
(()=>{const R=window.RK,qs=new URLSearchParams(location.search),api=(qs.get('api')||R.api).replace(/\/$/,'');const tb=document.getElementById('rk'),more=document.getElementById('more'),q=document.getElementById('rq');
let rows=[],offset=0;const PAGE=100;
function tierOf(x){let t=R.tiers[0];for(const k of R.tiers)if(x>=k.lo)t=k;return t}
function trunc(x){return (Math.floor(x*100+1e-4)/100).toFixed(2)}
function esc(s){return String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
function render(){const f=q.value.trim().toLowerCase();const list=rows.filter(r=>!f||r.name.toLowerCase().includes(f));
 if(!list.length){tb.innerHTML='<tr><td colspan="5" class="mut">'+R.l.empty+'</td></tr>';return}
 tb.innerHTML=list.map(r=>{const t=tierOf(r.total);const named=!/^[0-9a-f]{8}$/.test(r.name);
  return '<tr><td class="n">'+r.rank+'</td><td class="badgecell">'+t.b+'</td><td>'+(named?'<a href="rating.html?name='+encodeURIComponent(r.name)+'#calc"><b>'+esc(r.name)+'</b></a>':'<span class="dim mono">'+esc(r.name)+'</span>')+
  ' <span class="small" style="color:'+t.c+'">'+t.n+'</span></td><td class="n" style="color:'+t.c+'">'+trunc(r.total)+'</td><td class="n dim">'+trunc(r.chartRating)+'</td></tr>'}).join('')}
async function load(){try{const r=await fetch(api+'/v1/public/ranking?offset='+offset+'&limit='+PAGE);if(!r.ok)throw 0;const page=await r.json();rows=rows.concat(page);offset+=page.length;more.hidden=page.length<PAGE;render()}
 catch(e){if(!rows.length)tb.innerHTML='<tr><td colspan="5"><div class="notice">'+R.l.offline+'</div></td></tr>'}}
q.oninput=render;more.onclick=load;load()})();</script>""")
    return page("ranking.html", "ranking.html", t("ranking.title"), t("ranking.desc"), "".join(body), script)


LOOKUP_JS = r"""<script>
(()=>{const api=(new URLSearchParams(location.search).get('api')||'API').replace(/\/$/,'');const box=document.getElementById('lk'),btn=document.getElementById('lkb'),msg=document.getElementById('lkm');
const TIER={4:'easy',0:'normal',3:'hard',2:'extreme'};
async function go(name){name=(name||'').trim();if(!name)return;msg.textContent='…';
 try{const r=await fetch(api+'/v1/public/player?name='+encodeURIComponent(name));if(!r.ok)throw 0;const p=await r.json();
  const rows=p.charts.filter(c=>TIER[c.tier]&&window.RD.songs.some(s=>s.id===c.song)).slice(0,20).map(c=>({id:c.song,tier:TIER[c.tier],score:c.score}));
  window.BBCalc.load(rows,Math.round((p.ladderBonus||0)*10)/10);msg.textContent=window.RL.ok.replace('{name}',p.name).replace('{n}',rows.length);
  history.replaceState(null,'','?name='+encodeURIComponent(p.name)+'#calc')}
 catch(e){msg.textContent=window.RL.none}}
btn.onclick=()=>go(box.value);box.onkeydown=e=>{if(e.key==='Enter')go(box.value)};
const n=new URLSearchParams(location.search).get('name');if(n){box.value=n;go(n)}})();</script>"""


def write_characters_js():
    """Extracts the character drawing code from the game's character review sheet into wiki/characters.js."""
    src_path = BB / "Design" / "character_proposals.html"
    if not src_path.exists():
        return
    src = src_path.read_text(encoding="utf-8")
    body = src[src.index("  const BPM = 128, SPB = 60 / BPM;"):src.index("  // ---------- 카드 하나")]
    body = body.replace("  let color = THEMES[5][1];\n  let realSize = false, paused = false;\n", "")
    body = body.replace("const n = (m.beat % 4) + 1;", "const n = (((m.beat % 4) + 4) % 4) + 1;")   # the sheet crashes on negative beats
    js = ("// BeatBound GEAR characters, drawn like the game's character review sheet (Design/character_proposals.html).\n"
          "(() => {\n" + body + """
  const EQ = { id: "EQ", draw(c, col, m) {
    frame(c, col, 12); c.fillStyle = col;
    const lv = [m.low, m.mid, m.high];
    [-30, 0, 30].forEach((x, i) => capsule(c, x, 40, 18, 22 + 54 * lv[i]));
  } };
  const byId = Object.fromEntries([EQ, ...CHARS].map((ch) => [ch.id, ch]));
  window.BBChars = {
    ids: Object.keys(byId),
    draw(c, id, col, t, local) {
      const ch = byId[id]; if (!ch) return;
      const mu = music(t);
      ch.draw(c, col, { ...mu, t, dt: 1 / 60, kick: mu.low, local: local || {} });
    },
  };
})();
""")
    (OUT / "characters.js").write_text(js, encoding="utf-8")


# ---------------------------------------------------------------- main
def write_data(songs):
    d = OUT / "data"
    d.mkdir(parents=True, exist_ok=True)
    keep = set()
    for s in songs:
        x = s["tiers"]["extreme"]
        demo_end = x["bar_starts"][min(16, len(x["bar_starts"]) - 1)]
        data = dict(id=s["id"], bpm=s["bpm"], demoEnd=demo_end,
                    tiers={k: dict(lead=round(s["tiers"][k]["lead_sec"] * 1000), hits=s["tiers"][k]["enc"]) for k, *_ in TIERS})
        (d / f"{s['id']}.json").write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
        keep.add(f"{s['id']}.json")
    for old in d.glob("*.json"):
        if old.name not in keep:
            old.unlink()


def main():
    global VERSION, BUILD_DATE, EVALUATOR, NEIGHBOURS, LANG, GEAR, SONG_WORDS
    import datetime
    BUILD_DATE = datetime.date.today().isoformat()
    VERSION = datetime.datetime.now().strftime("%Y%m%d%H%M")
    EVALUATOR = re.search(r"evaluatorVersion: (\S+)", (GD / "ChartLevelTable.asset").read_text(encoding="utf-8")).group(1)
    cities = load_cities()
    levels = load_levels()
    songs = load_songs(cities, levels)
    courses = load_courses()
    starters = load_starters()
    GEAR = load_gear()
    titles, SONG_WORDS = load_titles()
    loc = load_loc("title")
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

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "wiki.css").write_text((CSS + COLLECT_CSS + ART_CSS).strip() + "\n", encoding="utf-8")
    (OUT / "wiki.js").write_text(JS.strip() + "\n", encoding="utf-8")
    write_data(songs)
    write_characters_js()
    for LANG in LANGS:
        out = OUT if LANG == "ko" else OUT / "en"
        (out / "songs").mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(index_page(songs, cities), encoding="utf-8")
        (out / "rating.html").write_text(rating_page(songs, cities, courses), encoding="utf-8")
        (out / "gear.html").write_text(gear_page(songs, cities, courses, GEAR, titles, SONG_WORDS, loc), encoding="utf-8")
        (out / "stepup.html").write_text(stepup_page(songs, cities, courses, starters), encoding="utf-8")
        (out / "rules.html").write_text(rules_page(), encoding="utf-8")
        (out / "ranking.html").write_text(ranking_page(songs, cities), encoding="utf-8")
        keep = set()
        for s in songs:
            (out / "songs" / f"{s['id']}.html").write_text(song_page(s, cities, ranks, courses_by_song, starters_by_song), encoding="utf-8")
            keep.add(f"{s['id']}.html")
        for old in (out / "songs").glob("*.html"):
            if old.name not in keep:
                old.unlink()
    print(f"wrote {len(songs)} songs × {len(LANGS)} languages, {len(courses)} courses, {len(starters)} starter courses → {OUT}")


if __name__ == "__main__":
    main()
