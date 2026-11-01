#!/usr/bin/env python3
"""Build the two TikTok cuts of the Founding MENA clip with ffmpeg.

Usage: build.py <A|B> <out_dir>
"""
import subprocess, sys, os

SRC = "/root/.claude/uploads/8fe25ed8-490f-5926-961b-1bee0c6952de/44940410-V2_founding_mena_vertical_raw_sfx.mov"
W, H = 1080, 1920
RLM = "\u200f"
# face centres (fraction of frame) per camera, measured from source frames
FOCUS = {"A": (0.46, 0.47), "B1": (0.57, 0.44), "B2": (0.54, 0.44)}

# Segments: name -> (src_in, src_out, camera, zoom, video_out_override)
SEG = {
    "H1":  (28.20, 30.12, "A", 1.25, None),
    "H2a": (30.70, 31.48, "A", 1.10, None),
    "H2b": (31.48, 32.78, "A", 1.32, None),
    "H2c": (32.78, 34.62, "A", 1.15, None),
    "C1":  (0.05, 1.20, "A", 1.00, None),
    "C2":  (1.80, 2.96, "A", 1.12, None),
    "C3":  (3.24, 4.50, "A", 1.00, None),
    "C4":  (4.88, 5.48, "A", 1.15, None),
    "V1a": (6.74, 7.50, "B1", 1.12, None),
    "V1b": (7.52, 8.72, "A", 1.25, None),
    "V2":  (9.14, 9.76, "A", 1.00, None),
    "V3":  (10.16, 11.98, "A", 1.12, None),
    "V4a": (12.56, 14.18, "A", 1.00, None),
    "V4b": (14.18, 15.62, "A", 1.20, None),
    "V5":  (16.10, 16.80, "A", 1.00, None),
    "V6":  (17.32, 17.72, "A", 1.15, None),
    "V7":  (18.08, 19.36, "A", 1.00, 19.20),  # camera B starts 19.22: freeze A's last frame
    "P1":  (39.04, 39.60, "B2", 1.00, None),
    "P2a": (40.46, 42.62, "B2", 1.12, None),
    "P2b": (42.62, 44.16, "B2", 1.00, None),
    "P2c": (44.16, 45.70, "B2", 1.25, None),
    "P3":  (45.84, 46.78, "B2", 1.10, None),
}
ORDER = {
    "A": ["H1", "H2a", "H2b", "H2c", "C1", "C2", "C3", "C4", "V1a", "V1b", "V2", "V3",
          "V4a", "V4b", "V5", "V6", "V7", "P1", "P2a", "P2b", "P2c", "P3"],
    "B": ["V1a", "V1b", "V2", "C1", "C2", "C3", "C4", "V3", "V4a", "V4b", "V5", "V6", "V7",
          "H1", "H2a", "H2b", "H2c", "P1", "P2a", "P2b", "P2c", "P3"],
}
HOOK = {"A": r"{\c&H0AD6FF&}10٪{\c&HFFFFFF&} من كهربا\Nالسعودية",
        "B": r"{\c&H0AD6FF&}+10 مليار{\c&HFFFFFF&}\Nللذكاء الاصطناعي"}

# Arabic caption cues on SOURCE time: (in, out, text, accent)
CUES = [
    (28.28, 29.50, "6.6 جيجاوات", True), (29.56, 30.12, "من الكهربا", False),
    (30.74, 31.48, "يعني حوالي", False), (31.50, 32.00, "10٪", True),
    (32.02, 32.78, "من اللي بتستهلكه", False), (32.80, 33.80, "السعودية", True),
    (33.82, 34.62, "النهارده", False),
    (0.05, 1.20, "HUMAIN طبعًا", True), (1.80, 2.96, "مدعومة من السعودية", False),
    (3.24, 4.50, "ذراع PIF", True), (4.88, 5.48, "للذكاء الاصطناعي", False),
    (6.74, 7.50, "حوالي", False), (7.52, 8.20, "+10 مليار", True), (8.20, 8.72, "اتستثمروا", False),
    (9.14, 9.76, "في HUMAIN", True),
    (10.16, 11.20, "وشغالين على", False), (11.20, 11.98, "كل المراحل", False),
    (12.56, 14.18, "من محطات الكهربا", False), (14.18, 14.95, "للداتا سنترز", False),
    (15.15, 15.62, "والموديلات", False),
    (16.10, 16.80, "وعندهم", False), (17.32, 17.72, "LLM خاص بيهم", True),
    (18.08, 18.48, "لحد", False), (18.48, 19.36, "التطبيقات", False),
    (39.04, 39.60, "ده مذهل!", False),
    (40.46, 41.30, "لوحدهم", False), (41.30, 42.62, "هيدخّلوا", False),
    (42.62, 44.16, "المملكة", True), (44.16, 44.78, "العربية السعودية", True),
    (44.78, 45.70, "عصر الذكاء الاصطناعي", True),
    (45.84, 46.78, "حاجة مش طبيعية", False),
]


def timeline(order):
    out, t = [], 0.0
    for name in order:
        s, e = SEG[name][0], SEG[name][1]
        out.append((name, s, e, t))
        t += e - s
    return out, t


def src_to_out(tl, t):
    for name, s, e, o in tl:
        if s - 1e-6 <= t <= e + 1e-6:
            return o + (t - s)
    return None


def ass_time(x):
    x = max(0, x)
    h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def build_ass(version, tl, total):
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Noto Kufi Arabic,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,7,3,5,90,170,0,1
Style: Hook,Noto Kufi Arabic,118,&H00FFFFFF,&H00FFFFFF,&H00000000,&HA0000000,-1,0,0,0,100,100,0,0,1,9,4,8,80,80,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    # hook title, top third, pops in
    ev.append(f"Dialogue: 2,{ass_time(0)},{ass_time(2.9)},Hook,,0,0,330,,"
              r"{\fad(0,150)\t(0,120,\fscx112\fscy112)\t(120,240,\fscx100\fscy100)}" + RLM + HOOK[version].replace(r"\N", "\\N" + RLM))
    # captions centred at ~62% height, left-shifted away from TikTok's right-side buttons
    for s, e, text, accent in CUES:
        a, b = src_to_out(tl, s), src_to_out(tl, e)
        if a is None or b is None:
            continue
        col = r"\c&H0AD6FF&" if accent else ""
        pop = r"\fscx85\fscy85\t(0,90,\fscx100\fscy100)"
        ev.append(f"Dialogue: 1,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,"
                  f"{{\\pos(500,1190){pop}{col}}}{RLM}{text}{RLM}")
    return head + "\n".join(ev) + "\n"


def crop_filter(cam, z):
    fx, fy = FOCUS[cam]
    cw, ch = int(W / z) // 2 * 2, int(H / z) // 2 * 2
    x = min(max(int(fx * W - cw / 2), 0), W - cw)
    y = min(max(int(fy * H - ch / 2), 0), H - ch)
    return f"crop={cw}:{ch}:{x}:{y},scale={W}:{H}:flags=lanczos,setsar=1"


def main():
    version, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    tl, total = timeline(ORDER[version])
    ass_path = os.path.join(outdir, f"captions_{version}.ass")
    open(ass_path, "w", encoding="utf-8").write(build_ass(version, tl, total))

    fc, vl, al = [], [], []
    for i, (name, s, e, o) in enumerate(tl):
        _, _, cam, z, vend = SEG[name]
        d = e - s
        ve = vend if vend else e
        pad = f",tpad=stop_mode=clone:stop_duration={e - ve:.3f}" if vend else ""
        fc.append(f"[0:v]trim=start={s}:end={ve},setpts=PTS-STARTPTS,{crop_filter(cam, z)}{pad},"
                  f"trim=duration={d:.3f},fps=30000/1001[v{i}]")
        fc.append(f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d=0.012,afade=t=out:st={d - 0.015:.3f}:d=0.015[a{i}]")
        vl.append(f"[v{i}]"); al.append(f"[a{i}]")
    n = len(tl)
    fc.append("".join(f"{v}{a}" for v, a in zip(vl, al)) + f"concat=n={n}:v=1:a=1[vc][ac]")
    fc.append(f"[vc]ass={ass_path}[vout]")

    # Synthesised, licence-free SFX: soft pops on numbers, whooshes on section turns
    def at(name, off=0.0):
        return next(o for nm, s, e, o in tl if nm == name) + off
    pops = [0.02, src_to_out(tl, 31.50), src_to_out(tl, 7.52), src_to_out(tl, 44.78)]
    whooshes = [at("C1") - 0.25, at("P1") - 0.25]
    if version == "B":
        whooshes = [at("C1") - 0.25, at("H1") - 0.25, at("P1") - 0.25]
    fc.append("[1:a]asplit=%d%s" % (len(pops), "".join(f"[p{k}]" for k in range(len(pops)))))
    fc.append("[2:a]asplit=%d%s" % (len(whooshes), "".join(f"[w{k}]" for k in range(len(whooshes)))))
    mix = ["[voice]"]
    for k, t in enumerate(pops):
        fc.append(f"[p{k}]adelay={int(max(t,0)*1000)}:all=1[pd{k}]"); mix.append(f"[pd{k}]")
    for k, t in enumerate(whooshes):
        fc.append(f"[w{k}]adelay={int(max(t,0)*1000)}:all=1[wd{k}]"); mix.append(f"[wd{k}]")
    fc.append("[ac]highpass=f=80,afftdn=nr=10:nf=-45,acompressor=threshold=-20dB:ratio=3:attack=5:release=120[voice]")
    fc.append("".join(mix) + f"amix=inputs={len(mix)}:duration=first:normalize=0,"
              "loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[aout]")

    out = os.path.join(outdir, f"founding_mena_tiktok_{version}.mp4")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", SRC,
           "-f", "lavfi", "-i", "sine=f=880:d=0.09,afade=t=out:st=0.01:d=0.08,volume=0.18,aformat=channel_layouts=stereo",
           "-f", "lavfi", "-i", "anoisesrc=c=pink:d=0.5:a=0.5,bandpass=f=1800:w=1400,afade=t=in:d=0.3,afade=t=out:st=0.3:d=0.2,volume=0.22,aformat=channel_layouts=stereo",
           "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-r", "30000/1001", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(f"{version}: {total:.2f}s -> {out}")


if __name__ == "__main__":
    main()
