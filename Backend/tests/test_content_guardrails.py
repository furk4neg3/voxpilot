"""Text guardrails for product positioning."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _term(*parts: str) -> str:
    return "".join(parts)


RESTRICTED_TERMS = [
    _term("voice ", "clo", "ning"),
    _term("zero", "-shot"),
    _term("speaker ", "clo", "ning"),
    _term("ref", "erence audio"),
    _term("ref", "erence voice"),
    _term("voice ", "sample"),
    _term("uploaded ", "voice"),
    _term("voice ", "conditioning"),
    _term("clo", "ne a voice"),
]


def _read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8").lower()



def test_ui_docs_and_demo_do_not_use_restricted_positioning_terms():
    checked_files = [
        "ui/streamlit_app.py",
        "docs/aws_architecture.md",
        "demo/README.md",
        "demo/audio/README.md",
        "demo/screenshots/README.md",
        "demo/video/README.md",
    ]

    for relative_path in checked_files:
        content = _read(relative_path)
        for term in RESTRICTED_TERMS:
            assert term not in content, f"{term!r} found in {relative_path}"
