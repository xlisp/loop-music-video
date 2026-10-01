# 视频循环配乐工具

把一段短视频（比如几秒钟的婚礼"囍"字动画）**循环播放**，配上**几首背景音乐**，自动生成一个完整视频。
视频总长度 = 所有歌曲时长加起来。

## 准备

只需要安装 ffmpeg（Python 3 用系统自带的即可，不需要装其他库）：

```bash
brew install ffmpeg
```

## 最简单的用法

```bash
cd /Users/xlisp/PyPro/mv_change

python3 loop_music_video.py 视频.mp4 歌1.mp3 歌2.mp3 歌3.mp3 -o 输出.mp4
```

- 第一个文件是**要循环的视频**，后面跟**任意多首歌**。
- 歌曲按你写的**顺序**依次播放。
- 原视频自带的声音会被去掉，只保留背景音乐。
- 不写 `-o` 时，输出文件会保存在视频旁边，名字是 `<视频名>_配乐循环版.mp4`。

运行时会先显示歌曲总时长和循环次数，然后显示进度，最后显示"完成"。

## 实际例子

文件名里有**空格、括号或中文**时，要用**双引号**把路径括起来：

```bash
python3 loop_music_video.py \
  "/Users/xlisp/Desktop/10.3婚礼资料/红色双喜.MP4" \
  "/Users/xlisp/Desktop/ViccyC - 今天你要嫁给我（纯音乐版）.mp3" \
  "/Users/xlisp/Desktop/人民·藝術 - 相许（交响乐版）.mp3" \
  "/Users/xlisp/Desktop/昼夜 - 【钢琴】就是爱你（Cover David Tao）.mp3" \
  -o "/Users/xlisp/Desktop/婚礼视频.mp4"
```

> 小技巧：在终端里输入命令时，可以直接把文件从访达**拖进终端窗口**，路径会自动填好。

## 可选参数

| 参数 | 默认值 | 作用 |
|---|---|---|
| `-o 文件名` | 视频旁边自动命名 | 输出文件路径 |
| `--fade-in 秒数` | 1 | 开头画面淡入的秒数，`0` 表示不淡入 |
| `--fade-out 秒数` | 3 | 结尾画面和音乐一起淡出的秒数，`0` 表示不淡出 |
| `--crf 数字` | 18 | 画质。数字越小越清晰、文件越大（常用 18～23） |
| `--preset 速度` | medium | 生成速度：`fast` 更快，`slow` 更慢但文件更小 |
| `--audio-bitrate` | 256k | 音质，一般不用改 |
| `--dry-run` | — | 只看总时长和循环次数，不真正生成视频 |

例子：

```bash
# 先看看会生成多长的视频，不真正生成
python3 loop_music_video.py 视频.mp4 歌1.mp3 歌2.mp3 --dry-run

# 想快点出结果、文件小一点
python3 loop_music_video.py 视频.mp4 歌1.mp3 歌2.mp3 --crf 23 --preset fast

# 不要淡入淡出
python3 loop_music_video.py 视频.mp4 歌1.mp3 --fade-in 0 --fade-out 0
```

查看帮助：

```bash
python3 loop_music_video.py -h
```

## 需要多长时间？

1080p 视频大约按 **1.4 倍速**生成：10 分钟的视频大约需要 7 分钟。用 `--preset fast` 会更快。
生成过程中不要关闭终端窗口。

## 常见问题

**提示"找不到文件"**
路径写错了，或者路径里有空格但没加双引号。最简单的办法是把文件拖进终端。

**提示 `command not found: ffmpeg`**
还没有安装 ffmpeg，先运行 `brew install ffmpeg`。

**歌曲格式**
mp3、m4a、flac、wav 等常见格式都可以，几首歌的格式不一样也没关系。

**每次循环衔接处画面跳一下**
这是原视频本身首尾不连贯造成的，脚本只负责循环播放，不会修改视频内容。
