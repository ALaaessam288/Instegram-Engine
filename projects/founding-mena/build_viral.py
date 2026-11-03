#!/usr/bin/env python3
"""Viral cut of the Founding MENA clip: seamless loop, animated number graphics,
stack checklist, glitch / flash / shake hits, smooth push-ins.

Usage: build_viral.py <out_dir>
"""
import subprocess, sys, os

SRC = "/root/.claude/uploads/8fe25ed8-490f-5926-961b-1bee0c6952de/44940410-V2_founding_mena_vertical_raw_sfx.mov"
W, H = 1080, 1920
RLM = "‏"
YEL = r"\c&H0AD6FF&"
YT = "{" + YEL + "}"  # colour tag for use outside an override block
FOCUS = {"A": (0.46, 0.47), "B1": (0.57, 0.44), "B2": (0.54, 0.44)}

# name: (src_in, src_out, camera, zoom_start, zoom_end, video_out_override)
# The cut ends on "...the ambition to bring a" (src 28.20) and opens on "6.6 gigawatt"
# (src 28.20) at the same zoom, so the replay is one continuous sentence.
SEG = [
    ("H1",  28.20, 30.12, "A", 1.15, 1.30, None),
    ("H2",  30.70, 34.62, "A", 1.05, 1.25, None),
    ("C1",  0.05, 1.20, "A", 1.00, 1.06, None),
    ("C2",  1.80, 2.96, "A", 1.12, 1.18, None),
    ("C3",  3.24, 4.50, "A", 1.00, 1.06, None),
    ("C4",  4.88, 5.48, "A", 1.15, 1.20, None),
    ("V1a", 6.74, 7.50, "B1", 1.10, 1.16, None),
    ("V1b", 7.52, 8.72, "A", 1.30, 1.36, None),
    ("V2",  9.14, 9.76, "A", 1.00, 1.04, None),
    ("V3",  10.16, 11.98, "A", 1.08, 1.18, None),
    ("V4",  12.56, 15.62, "A", 1.00, 1.14, None),
    ("V5",  16.10, 16.80, "A", 1.20, 1.24, None),
    ("V6",  17.32, 17.72, "A", 1.05, 1.08, None),
    ("V7",  18.08, 19.36, "A", 1.15, 1.22, 19.20),
    ("P1",  39.04, 39.60, "B2", 1.00, 1.03, None),
    ("P2",  40.46, 44.76, "B2", 1.05, 1.22, None),
    ("P2b", 44.76, 45.70, "B2", 1.40, 1.45, None),
    ("P3",  45.84, 46.78, "B2", 1.10, 1.14, None),
    ("L1",  24.16, 24.88, "A", 1.00, 1.04, None),
    ("L2",  25.24, 26.16, "A", 1.04, 1.09, None),
    ("L3",  27.34, 28.20, "A", 1.09, 1.15, None),
]

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
    (42.62, 44.16, "المملكة", True), (44.16, 44.76, "العربية السعودية", True),
    (45.84, 46.78, "حاجة مش طبيعية", False),
    (24.16, 24.88, "بس لو بصّيت", False), (25.24, 26.16, "على طموحهم إنهم", False),
    (27.34, 28.20, "يجيبوا...", False),
]

TL, t = [], 0.0
for name, s, e, cam, z0, z1, vend in SEG:
    TL.append((name, s, e, t)); t += e - s
TOTAL = t


def o(src):
    for name, s, e, off in TL:
        if s - 1e-6 <= src <= e + 1e-6:
            return off + (src - s)
    raise ValueError(src)


def seg_start(name):
    return next(off for n, s, e, off in TL if n == name)


def ts(x):
    x = max(0.0, x)
    return f"{int(x // 3600)}:{int(x % 3600 // 60):02d}:{x % 60:05.2f}"


def dlg(layer, a, b, style, text):
    return f"Dialogue: {layer},{ts(a)},{ts(b)},{style},,0,0,0,,{text}"


def build_ass():
    ev = []
    hook_end = seg_start("C1")
    # white flash on the payoff slam (none on frame 1, so the loop seam stays clean)
    rect = r"{\an7\pos(0,0)\p1\c&HFFFFFF&\fad(0,%d)}m 0 0 l 1080 0 l 1080 1920 l 0 1920{\p0}"
    slam = o(44.76)
    ev.append(dlg(5, slam, slam + 0.25, "Box", rect % 230))

    # progress bar across the top, fills over the whole loop
    ev.append(dlg(4, 0, TOTAL, "Box",
                  r"{\an7\pos(0,0)\p1\c&H0AD6FF&\fscx0\t(0,%d,\fscx100)}m 0 0 l 1080 0 l 1080 12 l 0 12{\p0}"
                  % int(TOTAL * 1000)))

    # HOOK 1: kicker + counter 0 -> 6.6 GW
    ev.append(dlg(3, 0, o(30.12), "Kick", r"{\an5\pos(540,300)\fad(80,0)}" + RLM + "خطة HUMAIN:" + RLM))
    steps = 14
    for i in range(steps + 1):
        a = i * 0.05
        b = o(30.12) if i == steps else (i + 1) * 0.05
        val = 6.6 * i / steps
        big = r"{\an5\pos(540,470)\fscx%d\fscy%d}" % ((118, 118) if i == steps else (100, 100))
        ev.append(dlg(3, a, b, "Big", big + YT + f"{val:.1f}"))
    ev.append(dlg(3, 0.15, o(30.12), "Kick", r"{\an5\pos(540,640)\fad(120,0)}" + RLM + "جيجاوات كهربا" + RLM))

    # HOOK 2: 10% of Saudi consumption, bar fills to 10%
    h2 = o(30.74); h2e = hook_end
    ev.append(dlg(3, o(31.50), h2e, "Big", r"{\an5\pos(540,430)\fscx40\fscy40\t(0,140,\fscx115\fscy115)\t(140,260,\fscx100\fscy100)}" + YT + "10٪"))
    ev.append(dlg(3, h2, h2e, "Kick", r"{\an5\pos(540,620)\fad(100,0)}" + RLM + "من كهربا السعودية كلها" + RLM))
    ev.append(dlg(2, h2, h2e, "Box", r"{\an7\pos(140,700)\p1\c&HFFFFFF&\alpha&H90&\fad(100,0)}m 0 0 l 800 0 l 800 46 l 0 46{\p0}"))
    ev.append(dlg(3, o(31.50), h2e, "Box", r"{\an7\pos(860,700)\p1" + YEL + r"\fscx0\t(0,450,\fscx100)}m 0 0 l 80 0 l 80 46 l 0 46{\p0}"))

    # +10 billion stamp
    b10 = o(7.52)
    ev.append(dlg(3, b10, o(9.76), "Big", r"{\an5\pos(540,430)\frz-6\fscx160\fscy160\t(0,150,\fscx100\fscy100)}" + YT + RLM + "+10 مليار" + RLM))
    ev.append(dlg(3, b10 + 0.1, o(9.76), "Kick", r"{\an5\pos(540,610)\fad(80,0)}" + RLM + "استثمار في HUMAIN" + RLM))

    # Stack checklist, items land with the words
    items = [(13.56, "محطات كهربا"), (14.20, "داتا سنترز"), (15.20, "موديلات"),
             (17.34, "نموذج لغوي خاص"), (18.50, "تطبيقات")]
    end = o(19.36)
    ev.append(dlg(3, o(12.56), end, "Kick", r"{\an6\pos(1000,250)\fad(120,0)}" + RLM + YT + "كل المراحل:" + RLM))
    for k, (src_t, label) in enumerate(items):
        y = 360 + k * 105
        ev.append(dlg(3, o(src_t), end, "List",
                      r"{\an6\pos(1000,%d)\fad(60,0)\fscx60\fscy60\t(0,120,\fscx100\fscy100)}" % y
                      + RLM + label + r" {\fnDejaVu Sans" + YEL + "}✔"))

    # payoff slam
    ev.append(dlg(3, slam, o(45.70), "Big", r"{\an5\pos(540,450)\fscx170\fscy170\t(0,140,\fscx100\fscy100)}" + YT + RLM + "عصر الـAI" + RLM))
    ev.append(dlg(3, slam + 0.08, o(45.70), "Kick", r"{\an5\pos(540,620)}" + RLM + "السعودية داخلة" + RLM))

    # captions
    for s, e, text, accent in CUES:
        col = YEL if accent else ""
        ev.append(dlg(1, o(s), o(e), "Cap", r"{\pos(500,1190)\fscx85\fscy85\t(0,90,\fscx100\fscy100)" + col + "}" + RLM + text + RLM))

    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Noto Kufi Arabic,86,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,7,3,5,90,170,0,1
Style: Big,Noto Kufi Arabic,210,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,12,6,5,40,40,0,1
Style: Kick,Noto Kufi Arabic,78,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,7,3,5,40,40,0,1
Style: List,Noto Kufi Arabic,74,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,6,3,6,40,40,0,1
Style: Box,Noto Kufi Arabic,10,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    return head + "\n".join(ev) + "\n"


def seg_video(i, name, s, e, cam, z0, z1, vend):
    d = e - s
    ve = vend or e
    fx, fy = FOCUS[cam]
    # smooth push-in: scale grows linearly from z0 to z1, crop stays on the face
    sc = f"(({z0})+({z1}-{z0})*t/{d:.3f})"
    zf = (f"scale=w='trunc({W}*{sc}/2)*2':h='trunc({H}*{sc}/2)*2':eval=frame:flags=bicubic,"
          f"crop={W}:{H}:x='min(max({fx}*iw-{W}/2,0),iw-{W})':y='min(max({fy}*ih-{H}/2,0),ih-{H})'")
    pad = f",tpad=stop_mode=clone:stop_duration={e - ve:.3f}" if vend else ""
    return (f"[0:v]trim=start={s}:end={ve},setpts=PTS-STARTPTS,fps=30000/1001{pad},"
            f"trim=duration={d:.3f},{zf},setsar=1[v{i}]")


def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    ass = os.path.join(outdir, "captions_viral.ass")
    open(ass, "w", encoding="utf-8").write(build_ass())

    fc, pairs = [], []
    for i, (name, s, e, cam, z0, z1, vend) in enumerate(SEG):
        d = e - s
        fc.append(seg_video(i, name, s, e, cam, z0, z1, vend))
        fc.append(f"[0:a]atrim=start={s}:end={e},asetpts=PTS-STARTPTS,"
                  f"afade=t=in:d=0.012,afade=t=out:st={d - 0.015:.3f}:d=0.015[a{i}]")
        pairs.append(f"[v{i}][a{i}]")
    fc.append("".join(pairs) + f"concat=n={len(SEG)}:v=1:a=1[vc][ac]")

    # camera hits: impact shakes on the hook, +10B, 10% and the payoff slam
    hits = [0.0, o(31.50), o(7.52), o(44.76)]
    shake = "+".join(f"if(between(t,{h:.3f},{h + 0.4:.3f}),sin((t-{h:.3f})*95)*(1-(t-{h:.3f})/0.4),0)" for h in hits)
    hook_end = seg_start("C1")
    fc.append(f"[vc]scale=1144:2034,crop={W}:{H}:x='32+26*({shake})':y='57+18*({shake})',"
              f"rgbashift=rh=-18:bh=18:enable='lt(t,0.28)+between(t,{o(44.76):.3f},{o(44.76)+0.2:.3f})',"
              f"eq=brightness=-0.12:saturation=1.1:enable='lt(t,{hook_end:.3f})',"
              f"ass={ass}[vout]")

    # sound design (synthesised, licence-free)
    bass = [0.0, o(7.52), o(44.76)]
    pops = [o(31.50)] + [o(x) for x in (13.56, 15.20, 18.50)]
    whoosh = [seg_start("C1") - 0.3, seg_start("V4") - 0.3, seg_start("L1") - 0.3]
    riser_end = o(44.76)
    srcs = {"bass": (1, bass), "pop": (2, pops), "whoosh": (3, whoosh)}
    mix = ["[voice]"]
    for tag, (idx, times) in srcs.items():
        fc.append(f"[{idx}:a]asplit={len(times)}" + "".join(f"[{tag}{k}]" for k in range(len(times))))
        for k, tt in enumerate(times):
            fc.append(f"[{tag}{k}]adelay={int(max(tt, 0) * 1000)}:all=1[{tag}d{k}]"); mix.append(f"[{tag}d{k}]")
    fc.append(f"[4:a]adelay={int(max(riser_end - 1.2, 0) * 1000)}:all=1[riser]"); mix.append("[riser]")
    fc.append("[ac]highpass=f=80,afftdn=nr=10:nf=-45,acompressor=threshold=-20dB:ratio=3:attack=5:release=120[voice]")
    fc.append("".join(mix) + f"amix=inputs={len(mix)}:duration=first:normalize=0,"
              "loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[aout]")

    out = os.path.join(outdir, "founding_mena_tiktok_viral.mp4")
    st = "aformat=channel_layouts=stereo"
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", SRC,
           "-f", "lavfi", "-i", f"sine=f=52:d=0.6,afade=t=out:st=0.02:d=0.58,volume=0.9,{st}",
           "-f", "lavfi", "-i", f"sine=f=880:d=0.09,afade=t=out:st=0.01:d=0.08,volume=0.16,{st}",
           "-f", "lavfi", "-i", f"anoisesrc=c=pink:d=0.5:a=0.5,bandpass=f=1800:w=1400,afade=t=in:d=0.3,afade=t=out:st=0.3:d=0.2,volume=0.22,{st}",
           "-f", "lavfi", "-i", f"aevalsrc='0.07*sin(2*PI*(180*t+420*t*t))':d=1.2:s=48000,afade=t=in:d=1.0,afade=t=out:st=1.1:d=0.1,{st}",
           "-filter_complex", ";".join(fc), "-map", "[vout]", "-map", "[aout]",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p",
           "-r", "30000/1001", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(f"{TOTAL:.2f}s -> {out}")


if __name__ == "__main__":
    main()
