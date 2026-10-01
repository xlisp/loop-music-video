#!/usr/bin/env python3
"""把一段短视频循环播放，配上几首背景音乐，视频总长 = 所有歌曲时长之和。

用法示例：
    python3 loop_music_video.py 视频.mp4 歌1.mp3 歌2.mp3 歌3.mp3 -o 输出.mp4
    python3 loop_music_video.py 视频.mp4 歌1.mp3 歌2.mp3 --fade-out 3 --crf 20

说明：
- 歌曲按命令行给出的顺序依次播放，原视频自带的声音会被丢弃。
- 视频无缝循环到音乐结束为止，最后一轮在音乐结束处截断。
- 依赖 ffmpeg / ffprobe（brew install ffmpeg）。
"""
import argparse
import subprocess
import sys
from pathlib import Path


def duration(path):
    out = subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(path)], text=True)
    return float(out.strip())


def build_cmd(video, songs, output, fade_in, fade_out, crf, preset, audio_bitrate):
    total = sum(duration(s) for s in songs)

    cmd = ["ffmpeg", "-y", "-v", "error", "-stats", "-stream_loop", "-1", "-i", str(video)]
    for s in songs:
        cmd += ["-i", str(s)]

    # 统一每首歌的采样格式后拼接（concat 要求格式一致；同时忽略 mp3 里的封面图）
    filters = [
        f"[{i}:a]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo[a{i}]"
        for i in range(1, len(songs) + 1)
    ]
    audio = "".join(f"[a{i}]" for i in range(1, len(songs) + 1))
    audio += f"concat=n={len(songs)}:v=0:a=1"
    video_chain = "[0:v]format=yuv420p"
    if fade_in > 0:
        video_chain += f",fade=t=in:d={fade_in}"
    if fade_out > 0:
        audio += f",afade=t=out:st={total - fade_out:.3f}:d={fade_out}"
        video_chain += f",fade=t=out:st={total - fade_out:.3f}:d={fade_out}"
    filters += [audio + "[a]", video_chain + "[v]"]

    cmd += [
        "-filter_complex", ";".join(filters),
        "-map", "[v]", "-map", "[a]",
        "-t", f"{total:.3f}",
        "-c:v", "libx264", "-crf", str(crf), "-preset", preset,
        "-c:a", "aac", "-b:a", audio_bitrate,
        "-movflags", "+faststart",
        str(output),
    ]
    return cmd, total


def main():
    p = argparse.ArgumentParser(description="短视频循环 + 多首背景音乐，时长 = 歌曲总时长")
    p.add_argument("video", type=Path, help="要循环的视频")
    p.add_argument("songs", type=Path, nargs="+", help="背景音乐（按顺序播放）")
    p.add_argument("-o", "--output", type=Path,
                   help="输出文件（默认：视频同目录下 <视频名>_配乐循环版.mp4）")
    p.add_argument("--fade-in", type=float, default=1.0, help="开头画面淡入秒数，0 关闭（默认 1）")
    p.add_argument("--fade-out", type=float, default=3.0, help="结尾画面+音乐淡出秒数，0 关闭（默认 3）")
    p.add_argument("--crf", type=int, default=18, help="画质，越小越清晰文件越大（默认 18）")
    p.add_argument("--preset", default="medium", help="x264 编码速度，如 fast / medium / slow")
    p.add_argument("--audio-bitrate", default="256k", help="音频码率（默认 256k）")
    p.add_argument("--dry-run", action="store_true", help="只打印 ffmpeg 命令，不执行")
    args = p.parse_args()

    for f in [args.video, *args.songs]:
        if not f.exists():
            sys.exit(f"找不到文件：{f}")
    output = args.output or args.video.with_name(f"{args.video.stem}_配乐循环版.mp4")

    cmd, total = build_cmd(args.video, args.songs, output, args.fade_in,
                           args.fade_out, args.crf, args.preset, args.audio_bitrate)
    clip = duration(args.video)
    print(f"歌曲 {len(args.songs)} 首，总时长 {total:.1f}s（{int(total // 60)}分{total % 60:.0f}秒）")
    print(f"视频片段 {clip:.2f}s，约循环 {total / clip:.1f} 次")
    print(f"输出：{output}")

    if args.dry_run:
        print(" ".join(f"'{c}'" if " " in c or ";" in c else c for c in cmd))
        return
    subprocess.run(cmd, check=True)
    print(f"完成：{output}（{duration(output):.1f}s）")


if __name__ == "__main__":
    main()
