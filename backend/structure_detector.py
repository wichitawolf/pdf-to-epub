import re

def transform_to_html(structured_data):
    """
    Transforms fixed PDF blocks into a reflowable HTML stream.
    """
    if not structured_data:
        return ""

    html_blocks = []
    current_paragraph = []
    last_size = None

    for item in structured_data:
        text = item['text'].strip()
        size = item['size']

        # 1. Detect Heading Change (Text > 14pt is usually a header)
        if size > 14:
            if current_paragraph:
                html_blocks.append(f"<p>{' '.join(current_paragraph)}</p>")
                current_paragraph = []
            
            html_blocks.append(f"<h1>{text}</h1>")
            continue

        # 2. Paragraph Logic: Detect if the flow continues
        # If the font size is similar, we keep appending to the current paragraph
        if last_size is not None and abs(size - last_size) > 1:
            if current_paragraph:
                html_blocks.append(f"<p>{' '.join(current_paragraph)}</p>")
                current_paragraph = []

        # 3. Clean line-end hyphens
        if text.endswith('-'):
            text = text[:-1]
        else:
            text += " "

        current_paragraph.append(text)
        last_size = size

    if current_paragraph:
        html_blocks.append(f"<p>{' '.join(current_paragraph)}</p>")

    return "\n".join(html_blocks)