from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path


class ResearchLoaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        (root / "deep-dive-training").mkdir()
        (root / "deep-dive-training" / "weekly.md").write_text(
            "# Wochenstruktur\n\nLange Radausfahrten brauchen Abstand zum harten Lauftraining. " * 10,
            encoding="utf-8",
        )
        (root / "nutrition.md").write_text(
            "# Ernährung\n\nKohlenhydrate und Flüssigkeit sind im Wettkampf entscheidend. " * 10,
            encoding="utf-8",
        )
        os.environ["COACH_RESEARCH_DIR"] = self.tmp.name
        from backend import research_loader
        research_loader._sections.cache_clear()

    def tearDown(self) -> None:
        from backend import research_loader
        research_loader._sections.cache_clear()
        os.environ.pop("COACH_RESEARCH_DIR", None)
        self.tmp.cleanup()

    def test_retrieves_relevant_section(self) -> None:
        from backend.research_loader import retrieve_research
        result = retrieve_research("Wie plane ich eine lange Radausfahrt und einen harten Lauf?")
        self.assertIn("weekly.md", result)
        self.assertIn("Radausfahrten", result)

    def test_respects_size_limit(self) -> None:
        from backend.research_loader import retrieve_research
        result = retrieve_research("Training Ernährung Lauf Radausfahrt", max_chars=700)
        self.assertLessEqual(len(result), 700)


if __name__ == "__main__":
    unittest.main()
