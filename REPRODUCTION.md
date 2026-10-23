# 复现记录（2026-10-23）

来源：[maxtinnate/AI_MUSIC_CREATOR](https://github.com/maxtinnate/AI_MUSIC_CREATOR)。
原作者署名：**reaesteve**。
基线提交：`9604264dc134df72eda7e8b51eb2b8341b783635`。

## 结论

已在 Windows x64 完成“示例作曲 → 五声部分轨渲染 → 混音 WAV”的完整本地复现，
并修复 MIDI 文件头缺失长度字段的问题。
原始流程与适配后的 WAV 字节完全一致。

已使用连接账户 **mb-best** 创建 [mb-best/AI_MUSIC_CREATOR](https://github.com/mb-best/AI_MUSIC_CREATOR) 的公开 fork。
仓库保留上游提交历史、全部原始文件、来源归属和许可证；本次修复与复现说明提交到该 fork 的 main 分支。

## 环境

| 项目 | 实际使用 |
| --- | --- |
| 系统 | Windows x64 |
| Python | CPython 3.12.14 |
| NumPy | 2.5.4 |
| SciPy | 1.18.1 |
| C 编译器 | ziglang 0.16.0，使用其 C 编译器 |
| 硬件要求 | 本次使用 CPU，无模型权重、GPU 或模型 API |

依赖已装在本任务独立环境中，没有修改系统 Python。
项目原始最低要求为 Python 3.10+、NumPy >=1.24、SciPy >=1.10 和 C 编译器。
`requirements-repro.txt` 固定的是本次 Python 3.12 环境；其他 Python 版本可用原始
`engine/requirements.txt` 让包管理器选择兼容版本。

## 验证结果

| 检查 | 结果 |
| --- | --- |
| SoundFont 完整性 | 32,319,396 字节，SHA-256 与仓库一致 |
| 示例乐曲 | 286 音符，5 声部：钢琴、弦乐、大提琴、长笛、鼓 |
| WAV | 46.9845 秒；48,000 Hz；立体声；16-bit PCM |
| 音频峰值 | 0.92999054 |
| 全曲 RMS | 0.12105443 |
| 削波样本 | 0 |
| 限幅器最小增益 | 0.96 |
| 分轨 | 5 个声部均有非零音频，帧数与混音目标一致 |
| MIDI | 修复后标准格式 1，6 轨（含速度轨），480 ticks/beat；独立解析器 mido 1.3.3 成功读取 286 个音符 |
| 回归检查 | 6 项全部通过 |
| 依赖一致性 | 包依赖检查通过 |
| 含空格的输出路径 | 完整构建通过 |
| 原始与适配后的 WAV | 字节完全一致 |

SoundFont SHA-256：
`9575028c7a1f589f5770fccc8cff2734566af40cd26ed836944e9a5152688cfe`。

WAV SHA-256：
`f061c69232a501b23a819fedc5909782ed78daca4a8c9b332f83f58748e2affd`。

音频进行了数据与结构验证，未作主观听感评价。
末尾静音属于原示例的混响尾音及淡出设置。

## 修复内容

1. 原 `song.mid` 漏写 MThd 的 4 字节长度字段。现补为标准的 6 字节头数据长度，并增加结构回归检查。
2. 增加 `engine/build.py`，使用当前解释器，支持 gcc/clang/MSVC 和可选 Zig 编译器。
3. 合并音色库前确认四段齐全，并校验 SHA-256；已有合并文件也要校验。
4. 编译、作曲、分轨渲染、混音任一阶段失败立即返回错误，只有成功混音后才报告完成。
5. 默认将生成文件写到 `engine/build/`，避免与源码混杂；仅使用当前曲目声明的声部。
6. 渲染器检查输入/输出文件错误，并精确写出目标帧数，释放资源。
7. 明确关闭 JSON 文件，补充运行说明、固定环境版本与生成文件忽略规则。

## Windows 运行

在解压后的项目根目录打开 PowerShell，使用 Python 3.12：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-repro.txt
.\.venv\Scripts\python.exe engine/build.py
```

输出在 `engine/build/song.wav`、`song.mid`、`notes.json` 等文件。
第一次运行会自动校验并合并音色库、编译渲染器；再次运行可复用已编译文件。
要写自己的乐曲，可复制 `engine/example_song.py`，再传入新脚本路径。
Linux/macOS 的运行方法见 README；本次未在这些系统实测。

## 许可与限制

原项目原创部分采用 CC BY-NC-SA 4.0，并有免费分享、禁止售卖声明；
复制、修改和分享时须保留出处、创作者署名、许可和声明。
本次保留了所有原始许可证和源码声明，修复沿用相同许可。
TinySoundFont 为 MIT；GeneralUser GS 使用其自己的许可，文件均保留。
这里记录的是仓库声明，没有将项目标记为允许任意商用的 MIT 项目。

这不是输入提示词即可独立运行的模型服务。自然语言需求仍需由人或编程助手转成曲谱脚本。
MIDI 目前不包含 WAV 混音效果；原导出器也未写入表情 CC、音色 bank 及前置静音，
因此不能期待外部 MIDI 播放器与 WAV 完全同声同时间。
