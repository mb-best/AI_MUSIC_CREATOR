# AI_MUSIC_CREATOR — reproduction

Reproduced fork: [mb-best/AI_MUSIC_CREATOR](https://github.com/mb-best/AI_MUSIC_CREATOR).

Original project: [maxtinnate/AI_MUSIC_CREATOR](https://github.com/maxtinnate/AI_MUSIC_CREATOR).
Creator credited by the project: **reaesteve**.
Reproduction baseline: `9604264dc134df72eda7e8b51eb2b8341b783635`.

The original README, notices, licence files and source notice headers are retained.
Original material and these adaptations are shared free under **CC BY-NC-SA 4.0**.
TinySoundFont keeps its MIT licence; GeneralUser GS keeps its own licence.
See [LICENSE_许可.txt](LICENSE_许可.txt), [免费分享声明_FREE_SHARING_NOTICE.txt](免费分享声明_FREE_SHARING_NOTICE.txt),
[TinySoundFont licence](engine/TinySoundFont-LICENSE.txt) and
[GeneralUser GS licence](sound_library/GeneralUser-GS/LICENSE.txt).

## What it does

This is a code-based composition toolkit, not a hosted text-to-music model or web app.
A human or coding assistant writes a Python score, then the engine exports MIDI and timed events,
renders instrument stems with the bundled SoundFont, and mixes a stereo WAV.
No model weights, GPU or model API key are required.

| Location | Purpose |
| --- | --- |
| `SKILL.md` | Instructions for an assistant writing scores |
| `engine/compose_kit.py` | Notes, chords, drums, tempo maps, MIDI/event export |
| `engine/example_song.py` | Included five-part demonstration |
| `engine/render.c`, `tsf.h` | Native SoundFont renderer |
| `engine/mix_kit.py` | Mixing, reverb, compression, limiting |
| `sound_library/GeneralUser-GS/` | Four SoundFont parts, SHA-256 and third-party licence |
| `提示词与资料/` | Original reference documents and MIDI |

## Run on Windows

Use Python 3.10+; the pinned reproduction environment below was tested on **3.12.14**.
Run these commands from the repository root in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-repro.txt
.\.venv\Scripts\python.exe engine/build.py --output-dir "engine/build"
```

`requirements-repro.txt` includes the optional Zig compiler.
If using another Python version or an existing C compiler, use:

```powershell
.\.venv\Scripts\python.exe -m pip install -r engine/requirements.txt
```

Then make gcc/clang available, use a Visual Studio developer shell, or install `ziglang`
in the same environment. The `CC` environment variable may point to one compiler executable.
Activation is optional when calling the environment's Python directly.

## Run on Linux/macOS

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r engine/requirements.txt
# Install the operating system's C compiler, or: .venv/bin/python -m pip install ziglang
.venv/bin/python engine/build.py --output-dir engine/build
```

The portable entry point was verified on Windows; Linux/macOS commands are provided but were not executed here.
The convenience wrappers still work from the engine directory:
`build.bat example_song.py` / `sh build.sh example_song.py`.
They use `python` / `python3` from PATH, so activate your environment first.

## Outputs and custom scores

The default output directory is `engine/build/`:
`song.wav`, `song.mid`, `notes.json`, `mix.json`, event lists and `stems/`.
The first run joins and verifies all four SoundFont parts, then compiles the renderer.
Subsequent builds reuse the renderer until its sources change.

Copy `engine/example_song.py` to `engine/my_song.py`, edit the notes and run:

```powershell
.\.venv\Scripts\python.exe engine/build.py engine/my_song.py --output-dir "engine/build"
```

## Reproduction changes

- Added a Python build entry point for consistent error handling across platforms.
- Verify the provided SoundFont SHA-256, including pre-existing merged files.
- Use the running Python environment and support an optional workspace-local Zig compiler.
- Stop on a failed composer, compiler, renderer or mixer; report success only after mixing.
- Keep generated output separate from source; render only channels declared by the current score.
- Check renderer file errors and write exactly the requested number of audio frames.
- Fix the missing Standard MIDI header length so exported MIDI is readable.
- Preserve all upstream licences and notices, and add ignored generated paths and regression checks.

## Checks

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Six regression checks cover incomplete/corrupt SoundFont data, failed child processes and valid MIDI structure.
See `REPRODUCTION.md` for the actual end-to-end result and limitations.
