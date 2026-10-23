"""Regression checks for corrupt/missing sample data and failed build stages."""
import importlib.util
from pathlib import Path
import hashlib
import subprocess
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("music_build", Path(__file__).parents[1] / "engine" / "build.py")
build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build)


class BuildChecks(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.library = Path(self.temporary.name)
        self.original = build.LIBRARY
        build.LIBRARY = self.library
        self.data = b"soundfont fixture"
        (self.library / "GeneralUser-GS.sf2.sha256").write_text(hashlib.sha256(self.data).hexdigest())

    def tearDown(self):
        build.LIBRARY = self.original
        self.temporary.cleanup()

    def parts(self):
        for i, data in enumerate([self.data[:4], self.data[4:8], self.data[8:12], self.data[12:]]):
            (self.library / f"GeneralUser-GS.sf2.part_{i:02d}").write_bytes(data)

    def test_join_and_verify(self):
        self.parts()
        self.assertEqual(build.soundfont().read_bytes(), self.data)

    def test_corrupt_parts_do_not_publish_font(self):
        self.parts()
        (self.library / "GeneralUser-GS.sf2.part_01").write_bytes(b"truncated")
        with self.assertRaisesRegex(RuntimeError, "checksum"):
            build.soundfont()
        self.assertFalse((self.library / "GeneralUser-GS.sf2").exists())
        self.assertFalse((self.library / "GeneralUser-GS.sf2.tmp").exists())

    def test_existing_corrupt_font_is_rejected(self):
        (self.library / "GeneralUser-GS.sf2").write_bytes(b"bad")
        with self.assertRaisesRegex(RuntimeError, "checksum"):
            build.soundfont()

    def test_missing_part_reports_filename(self):
        with self.assertRaisesRegex(RuntimeError, "part_00"):
            build.soundfont()

    def test_failed_child_process_stops_build(self):
        with patch.object(build.subprocess, "run", side_effect=subprocess.CalledProcessError(3, "render")):
            with self.assertRaises(subprocess.CalledProcessError):
                build.run(["render"], self.library, {})


if __name__ == "__main__":
    unittest.main()
