from typing import List
from unittest.mock import patch

from .base import IntrospectionBaseTest
from introspection.inspector import title, subtitle
from introspection.colors import colors


class IntrospectionTestConf(IntrospectionBaseTest):
    @patch("builtins.print")
    def test_titles(self, mock_print):
        lines: List[str] = ["========================================================"]
        lines.append("                     text                     ")
        lines.append("========================================================")
        title("text")
        mock_print.assert_called_with(lines[0])
        subtitle("text")
        st = "-------------- text --------------"
        mock_print.assert_called_with(st)

    def test_colors(self):
        msg = "msg"
        c = colors.red(msg)
        self.assertEqual(c, f"\033[91m{msg}\033[0m")
        c = colors.blue(msg)
        self.assertEqual(c, f"\033[94m{msg}\033[0m")
        c = colors.green(msg)
        self.assertEqual(c, f"\033[92m{msg}\033[0m")
        c = colors.yellow(msg)
        self.assertEqual(c, f"\033[93m{msg}\033[0m")
        c = colors.purple(msg)
        self.assertEqual(c, f"\033[95m{msg}\033[0m")
        c = colors.bold(msg)
        self.assertEqual(c, f"\033[1m{msg}\033[0m")
        c = colors.underline(msg)
        self.assertEqual(c, f"\033[4m{msg}\033[0m")
