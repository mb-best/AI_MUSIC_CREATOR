"""Check that export produces a structurally readable Standard MIDI file."""
import importlib.util
import os
from pathlib import Path
import struct
import tempfile
import unittest


class MidiExportChecks(unittest.TestCase):
    def test_standard_header_and_track_chunks(self):
        spec = importlib.util.spec_from_file_location("score_fixture", Path(__file__).parents[1] / "engine" / "compose_kit.py")
        score = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(score)
        score.channel(0, "piano", 0)
        score.note(0, "C4", 0, 1, 80, hum=0)
        original = Path.cwd()
        with tempfile.TemporaryDirectory() as temporary:
            try:
                os.chdir(temporary)
                score.export(end_beat=4)
                data = Path("song.mid").read_bytes()
            finally:
                os.chdir(original)
        self.assertEqual(data[:4], b"MThd")
        header_length = struct.unpack(">I", data[4:8])[0]
        self.assertEqual(header_length, 6)
        fmt, tracks, division = struct.unpack(">HHH", data[8:8 + header_length])
        self.assertEqual((fmt, tracks, division), (1, 2, 480))
        offset = 8 + header_length
        for _ in range(tracks):
            self.assertEqual(data[offset:offset + 4], b"MTrk")
            length = struct.unpack(">I", data[offset + 4:offset + 8])[0]
            track = data[offset + 8:offset + 8 + length]
            self.assertTrue(track.endswith(b"\x00\xff\x2f\x00"))
            offset += 8 + length
        self.assertEqual(offset, len(data))


if __name__ == "__main__":
    unittest.main()
