from ebooklib import epub
import uuid
import zipfile
from datetime import datetime
import os

def build_epub(html_content: str, output_path: str, title: str = "Document"):
    """
    Create a minimal, valid reflowable EPUB (EPUB3) containing the provided HTML content.
    Ensures the 'mimetype' entry is first and uncompressed (required by the spec).
    After writing, validate that the file is a proper ZIP and raise with diagnostics if not.
    """
    uid = str(uuid.uuid4())
    pub_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

    container_xml = """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>"""

    nav_xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
  <head>
    <meta charset="utf-8"/>
    <title>Navigation</title>
  </head>
  <body>
    <nav epub:type="toc" id="toc">
      <h1>Table of Contents</h1>
      <ol>
        <li><a href="Text/chapter1.xhtml">Start</a></li>
      </ol>
    </nav>
  </body>
</html>"""

    chapter_html = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta charset="utf-8"/>
    <title>{title}</title>
  </head>
  <body>
    {html_content}
  </body>
</html>"""

    content_opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="uid" version="3.0" xml:lang="en">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="uid">{uid}</dc:identifier>
    <dc:title>{title}</dc:title>
    <dc:language>en</dc:language>
    <meta property="dcterms:modified">{pub_date}</meta>
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="chapter1" href="Text/chapter1.xhtml" media-type="application/xhtml+xml"/>
  </manifest>
  <spine>
    <itemref idref="chapter1"/>
  </spine>
</package>"""

    # Make sure output dir exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # write the EPUB file ensuring mimetype is uncompressed and first
    with zipfile.ZipFile(output_path, "w") as zf:
        # mimetype must be first and stored (no compression). Use str (no newline).
        zf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)

        # META-INF/container.xml
        zf.writestr("META-INF/container.xml", container_xml, compress_type=zipfile.ZIP_DEFLATED)

        # OPF and nav and content (under OEBPS to match container)
        zf.writestr("OEBPS/nav.xhtml", nav_xhtml, compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr("OEBPS/content.opf", content_opf, compress_type=zipfile.ZIP_DEFLATED)
        zf.writestr("OEBPS/Text/chapter1.xhtml", chapter_html, compress_type=zipfile.ZIP_DEFLATED)

    # Post-write validation: ensure the file is a valid ZIP and print first bytes if not
    if not zipfile.is_zipfile(output_path):
        # grab a small sample for debugging
        sample = b""
        try:
            with open(output_path, "rb") as f:
                sample = f.read(128)
        except Exception:
            pass
        raise Exception(f"Generated EPUB is not a ZIP file. First bytes: {sample!r}")

    return output_path