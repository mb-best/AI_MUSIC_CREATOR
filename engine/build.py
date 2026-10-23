# 【免费分享声明】
# 创作者：reaesteve
# 本项目（技能说明、作曲引擎代码、示例曲与项目文档）由创作者 reaesteve 免费分享，仅供个人学习与非商业使用。
# 禁止以任何名义出售、转售或打包售卖本项目，禁止通过付费下载、付费会员、付费课程、付费社群、
# “打赏/关注后获取”、引流收费等任何形式收取费用或设置付费门槛。
# 可以免费转发与修改，但必须注明出处、保留本声明，并以相同许可免费分享。
# 用本技能创作的音乐归创作者本人所有；以上限制针对的是本项目本身。
# 许可：知识共享 署名-非商业性使用-相同方式共享 4.0 国际（CC BY-NC-SA 4.0）
# https://creativecommons.org/licenses/by-nc-sa/4.0/deed.zh-hans
# 第三方组件（GeneralUser GS 音色库、TinySoundFont）沿用其各自的原始许可。
# 如果你是付费获得本项目的，请注意：它本来就是免费的。
#
# [Free-sharing notice]
# This project (skill guide, composition engine code, example song and project documents) is shared by its creator, reaesteve, free of
# charge for personal, non-commercial use. Selling, reselling or bundling it for sale is prohibited, as is
# charging for access in any form or under any pretext: paid downloads, memberships, courses, paid groups,
# "tip/follow to unlock", or lead-generation paywalls. You may share and adapt it for free, with credit,
# keeping this notice, under the same licence. Music you create with it belongs to you; these limits apply
# to the project itself.
# Licence: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 (CC BY-NC-SA 4.0)
# https://creativecommons.org/licenses/by-nc-sa/4.0/
# Third-party components (GeneralUser GS SoundFont, TinySoundFont) keep their own original licences.
# If you paid for this project, you were charged for something that is free.


"""Portable build: python build.py [song.py] [--output-dir DIR]."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ENGINE = Path(__file__).resolve().parent
LIBRARY = ENGINE.parent / "sound_library" / "GeneralUser-GS"


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest() if hasattr(hashlib, "file_digest") else _digest(stream)


def _digest(stream):
    value = hashlib.sha256()
    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
        value.update(chunk)
    return value.hexdigest()


def soundfont():
    target = LIBRARY / "GeneralUser-GS.sf2"
    expected = (LIBRARY / "GeneralUser-GS.sf2.sha256").read_text(encoding="ascii").strip().split()[0]
    if target.exists():
        if digest(target) != expected:
            raise RuntimeError(f"SoundFont checksum mismatch: {target}")
        return target
    parts = [LIBRARY / f"GeneralUser-GS.sf2.part_{i:02d}" for i in range(4)]
    for part in parts:
        if not part.is_file():
            raise RuntimeError(f"Missing SoundFont segment: {part}")
    temporary = target.with_suffix(".sf2.tmp")
    try:
        with temporary.open("wb") as dest:
            for part in parts:
                with part.open("rb") as src:
                    shutil.copyfileobj(src, dest)
        if digest(temporary) != expected:
            raise RuntimeError("SoundFont checksum mismatch; download all four original segments again.")
        temporary.replace(target)
    finally:
        temporary.unlink(missing_ok=True)
    return target


def compiler():
    configured = os.environ.get("CC")
    if configured:
        # CC is one executable path, including paths with spaces.
        return [configured]
    for name in ("cc", "gcc", "clang", "cl"):
        if shutil.which(name):
            return [name]
    if shutil.which("zig"):
        return ["zig", "cc"]
    if importlib.util.find_spec("ziglang"):
        return [sys.executable, "-m", "ziglang", "cc"]
    raise RuntimeError("No C compiler found. Install gcc/clang, use a Visual Studio developer shell, or pip install ziglang.")


def run(args, cwd, env):
    print("+ " + subprocess.list2cmdline([str(x) for x in args]), flush=True)
    subprocess.run([str(x) for x in args], cwd=cwd, env=env, check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("song", nargs="?", default=str(ENGINE / "example_song.py"))
    parser.add_argument("--output-dir", type=Path, default=ENGINE / "build")
    args = parser.parse_args()
    song = Path(args.song).resolve()
    if not song.is_file():
        parser.error(f"Song script does not exist: {song}")
    for dependency in ("numpy", "scipy"):
        if importlib.util.find_spec(dependency) is None:
            raise RuntimeError(f"Missing {dependency}; run: python -m pip install -r {ENGINE / 'requirements.txt'}")
    sf2 = soundfont()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONPATH"] = str(ENGINE) + os.pathsep + env.get("PYTHONPATH", "")
    env.setdefault("ZIG_GLOBAL_CACHE_DIR", str(output / ".zig-cache"))
    env.setdefault("ZIG_LOCAL_CACHE_DIR", str(output / ".zig-local-cache"))
    renderer = output / ("render.exe" if os.name == "nt" else "render")
    sources = [ENGINE / "render.c", ENGINE / "tsf.h"]
    if not renderer.exists() or any(p.stat().st_mtime > renderer.stat().st_mtime for p in sources):
        cc = compiler()
        if Path(cc[0]).stem.lower() == "cl":
            command = cc + ["/nologo", "/O2", str(sources[0]), f"/Fe:{renderer}"]
        else:
            command = cc + ["-O2", "-o", str(renderer), str(sources[0]), "-lm"]
        run(command, output, env)
    run([sys.executable, "-X", "utf8", song], output, env)
    with (output / "mix.json").open(encoding="utf-8") as stream:
        config = json.load(stream)
    (output / "stems").mkdir(exist_ok=True)
    # Use only this score's channels, so stale files from a prior score cannot be mixed.
    for ch in config["channels"]:
        channel = f"{int(ch):02d}"
        run([renderer, sf2, output / f"events_ch{channel}.txt",
             output / "stems" / f"ch{channel}.raw", str(config["total"])], output, env)
    run([sys.executable, "-X", "utf8", ENGINE / "mix_kit.py"], output, env)
    print(f"Completed: {output / 'song.wav'}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        sys.exit(1)
