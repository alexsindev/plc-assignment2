from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat


def _fmt(color: str, bold: bool = False) -> QTextCharFormat:
    f = QTextCharFormat()
    f.setForeground(QColor(color))
    if bold:
        f.setFontWeight(QFont.Weight.Bold)
    return f


class PLCSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        self._rules: list[tuple[QRegularExpression, QTextCharFormat]] = []

        for kw in ("if", "else", "while", "func", "return"):
            self._rules.append((QRegularExpression(rf"\b{kw}\b"), _fmt("#c586c0", bold=True)))

        self._rules.append((QRegularExpression(r"\bprint\b"), _fmt("#dcdcaa")))

        for lit in ("true", "false"):
            self._rules.append((QRegularExpression(rf"\b{lit}\b"), _fmt("#569cd6")))

        self._rules.append((QRegularExpression(r"\b\d+\.\d+\b"), _fmt("#b5cea8")))
        self._rules.append((QRegularExpression(r"\b\d+\b"),       _fmt("#b5cea8")))

        self._rules.append((QRegularExpression(r'"[^"\n]*"'),      _fmt("#ce9178")))

    def highlightBlock(self, text: str) -> None:
        for pattern, fmt in self._rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), fmt)
