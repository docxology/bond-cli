"""Color-safe table rendering for the front door.

``format_table`` aligns columns with fixed-width padding **only** — it never
emits ANSI SGR (color) escape sequences. That is the "color-safe" contract: a
table that renders identically in a terminal, a pipe, a log file, and test
capture, and never leaks escape codes into machine-read output. Alignment is
deterministic: widths derive from the header + cell text, columns join on two
spaces, and no cell content is ever truncated or wrapped.

Determinism: for identical inputs the rendered text is byte-identical (no
terminal-width probing, no environment dependence).
"""

from __future__ import annotations

from collections.abc import Sequence


def format_table(headers: Sequence[str], rows: Sequence[Sequence[object]]) -> str:
    """Render ``rows`` under ``headers`` as an aligned, color-safe table.

    Args:
        headers: Column titles (one per column).
        rows: One sequence of cell values per row; cells are stringified.

    Returns:
        The rendered table (header line, then one line per row). Empty
        ``rows`` yields just the header line; empty ``headers`` yields ``""``.

    Example:
        >>> format_table(["A", "B"], [("1", "x"), ("longer", "y")])
        'A       B\\n1       x\\nlonger  y'
    """
    if not headers:
        return ""
    cells: list[list[str]] = [list(headers)]
    cells.extend([str(cell) for cell in row] for row in rows)
    widths = [max(len(row[column]) for row in cells) for column in range(len(headers))]
    rendered = [
        "  ".join(row[column].ljust(widths[column]) for column in range(len(headers)))
        for row in cells
    ]
    return "\n".join(rendered)
