"""Tests for ignore check/explain."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from .command_test_base import _CommandTestBase


class TestIgnoreCommand(_CommandTestBase):
    @patch("qgis_manager.cli.base.find_project_root")
    def test_ignore_check_excluded(self, mock_find):
        root = Path(tempfile.mkdtemp())
        (root / ".qgisignore").write_text("*.log\n!keep.log\n", encoding="utf-8")
        mock_find.return_value = root
        exit_code, output, _ = self._invoke(
            ["ignore", "--project", str(root), "check", "debug.log"]
        )
        self.assertEqual(exit_code, 0)
        self.assertIn("excluded", output)

    @patch("qgis_manager.cli.base.find_project_root")
    def test_ignore_check_negated(self, mock_find):
        root = Path(tempfile.mkdtemp())
        (root / ".qgisignore").write_text("*.log\n!keep.log\n", encoding="utf-8")
        mock_find.return_value = root
        exit_code, output, _ = self._invoke(
            ["ignore", "--project", str(root), "check", "keep.log"]
        )
        self.assertEqual(exit_code, 1)
        self.assertIn("included", output)

    @patch("qgis_manager.cli.base.find_project_root")
    def test_ignore_explain_winning_rule(self, mock_find):
        root = Path(tempfile.mkdtemp())
        (root / ".qgisignore").write_text("*.log\n!keep.log\n", encoding="utf-8")
        mock_find.return_value = root
        exit_code, output, _ = self._invoke(
            ["ignore", "--project", str(root), "check", "keep.log", "--explain"]
        )
        self.assertEqual(exit_code, 1)
        self.assertIn("rule: root: !keep.log", output)

    @patch("qgis_manager.cli.base.find_project_root")
    def test_ignore_explain_no_rule(self, mock_find):
        root = Path(tempfile.mkdtemp())
        mock_find.return_value = root
        exit_code, output, _ = self._invoke(
            ["ignore", "--project", str(root), "check", "plugin.py", "--explain"]
        )
        self.assertEqual(exit_code, 1)
        self.assertIn("no matching rule", output)

    def test_ignore_requires_action(self):
        exit_code, _, stderr = self._invoke(["ignore"])
        self.assertEqual(exit_code, 1)
        self.assertIn("ignore check", stderr)
