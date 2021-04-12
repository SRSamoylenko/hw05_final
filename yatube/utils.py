from textwrap import fill, shorten


def wrap_text(text: str) -> str:
    """Return beautifully wrapped text."""
    text = shorten(text, width=250, placeholder='...', initial_indent='\t')
    return fill(text, width=70)
