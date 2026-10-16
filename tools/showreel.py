#!/usr/bin/env python3
"""Склейка ролика: заставка → вступление → чистка ×5 → результат → концовка.
Музыка (кусок из монтажа Славы) только на чистке и крупном плане, затухает перед его словами.
Запуск: python3 tools/showreel.py <intro.mp4> <clean.mp4> <result.mp4> <music.wav> <out.mp4>"""
import subprocess, sys, json, glob, os
FF = glob.glob(os.path.expanduser("~/.pyenv/versions/3.11.9/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-*"))[0]
intro, clean, result, music, out = sys.argv[1:6]
SPEED = 5; T_TITLE = 2.5; T_END = 3.5   # плашки «ускорено» на чистке нет (убрана по правке Дмитрия 16.10)
T_RESULT = 16.2  # клип результата режем здесь: дальше камера уходит на асфальт, контакты идут сразу после слов
T_RESULT_START = 0.0  # начало клипа результата не режем: музыка — фрагмент полного трека, длины хватает
T_WORDS = 4.75 - T_RESULT_START   # первые слова Славы (4,75 с от начала исходного клипа) относительно обрезанного начала
MUSIC_VOL = 0.6; FADE = 2.5
from pathlib import Path
CARDS = Path(__file__).resolve().parent.parent / "avito" / "video_cards"
def dur(f):
    p = subprocess.run([FF, "-i", f], capture_output=True, text=True).stderr
    import re; m = re.search(r"Duration: (\d+):(\d+):([\d.]+)", p); return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])
d1, d2, d3 = dur(intro), dur(clean), min(dur(result), T_RESULT) - T_RESULT_START; d2s = d2 / SPEED
total = T_TITLE + d1 + d2s + d3 + T_END
c_start, c_end = T_TITLE + d1, T_TITLE + d1 + d2s
m_len = d2s + T_WORDS - 0.3   # музыка сплошная с начала чистки, затухает к первым словам Славы; фрагмент трека должен быть не короче
assert dur(music) >= m_len, f"музыка {dur(music):.1f} с короче нужных {m_len:.1f} с"
HDR = "zscale=tin=arib-std-b67:t=linear:npl=203,format=gbrpf32le,zscale=p=bt709,tonemap=hable:desat=0,zscale=t=bt709:m=bt709:r=tv:p=bt709,format=yuv420p"
fc = f"""
[0:v]format=yuv420p,fade=t=in:st=0:d=0.5,fade=t=out:st={T_TITLE-0.4}:d=0.4,setsar=1[v0];
[1:v]{HDR},scale=1080:1920,fps=30,setsar=1[v1];
[2:v]setpts=PTS/{SPEED},fps=30,{HDR},scale=1080:1920,setsar=1[v2];
[3:v]{HDR},scale=1080:1920,fps=30,fade=t=out:st={d3-0.25:.2f}:d=0.25,setsar=1[v3];
[4:v]format=yuv420p,fade=t=in:st=0:d=0.4,fade=t=out:st={T_END-0.6}:d=0.6,setsar=1[v4];
[v0][v1][v2][v3][v4]concat=n=5:v=1:a=0[vout];
[6:a]aformat=sample_rates=48000:channel_layouts=stereo[a0];
[1:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=1.15[a1];
[2:a]aformat=sample_rates=48000:channel_layouts=stereo,atempo={SPEED},volume=0[a2];
[3:a]aformat=sample_rates=48000:channel_layouts=stereo,volume=1.15,afade=t=out:st={d3-0.25:.2f}:d=0.25[a3];
[7:a]aformat=sample_rates=48000:channel_layouts=stereo[a4];
[a0][a1][a2][a3][a4]concat=n=5:v=0:a=1[speech];
[5:a]aformat=sample_rates=48000:channel_layouts=stereo,atrim=0:{m_len:.2f},volume={MUSIC_VOL},afade=t=in:st=0:d=0.15,afade=t=out:st={m_len-FADE:.2f}:d={FADE},adelay={int(c_start*1000)}|{int(c_start*1000)},apad[mus];
[speech][mus]amix=inputs=2:duration=first:dropout_transition=0:normalize=0,alimiter=limit=0.95:level=false[aout]
"""
cmd = [FF, "-y", "-v", "error", "-stats",
       "-loop", "1", "-framerate", "30", "-t", str(T_TITLE), "-i", str(CARDS / "title.png"),
       "-i", intro, "-i", clean, "-ss", str(T_RESULT_START), "-t", str(T_RESULT - T_RESULT_START), "-i", result,
       "-loop", "1", "-framerate", "30", "-t", str(T_END), "-i", str(CARDS / "end.png"),
       "-i", music,
       "-f", "lavfi", "-t", str(T_TITLE), "-i", "anullsrc=r=48000:cl=stereo",
       "-f", "lavfi", "-t", str(T_END), "-i", "anullsrc=r=48000:cl=stereo",
       "-filter_complex", fc, "-map", "[vout]", "-map", "[aout]",
       "-c:v", "libx264", "-preset", "medium", "-crf", "23", "-pix_fmt", "yuv420p", "-r", "30",
       "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-t", f"{total:.2f}", out]
print(f"музыка {m_len:.1f} с с {c_start:.1f} с, затухание {FADE} с до {c_start+m_len:.1f} с; слова с {c_end+T_WORDS:.1f} с")
print(f"сегменты: заставка {T_TITLE} с | вступление {d1:.1f} с | чистка {d2:.1f} с → {d2s:.1f} с | результат {d3:.1f} с | концовка {T_END} с | итого {total:.1f} с")
r = subprocess.run(cmd, capture_output=True, text=True); print(r.stderr[-1500:] if r.returncode else "ffmpeg ok")
