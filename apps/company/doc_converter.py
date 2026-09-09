import os
import html
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".docx", ".pdf", ".md", ".markdown", ".html", ".htm", ".txt"}


def decode_bytes(data: bytes) -> str:
    """Декодирует байты в строку, перебирая популярные кодировки (включая CP1251)."""
    for enc in ["utf-8-sig", "utf-8", "cp1251", "latin-1"]:
        try:
            return data.decode(enc)
        except (UnicodeDecodeError, LookupError):
            continue
    return data.decode("utf-8", errors="replace")


def sanitize_and_clean_html(raw_html: str, demote_h1: bool = True) -> str:
    """Очищает HTML от опасных тегов и инлайнового мусора Microsoft Office."""
    if not raw_html or not raw_html.strip():
        return ""

    soup = BeautifulSoup(raw_html, "html.parser")

    for tag in soup(["script", "style", "meta", "link", "title", "head", "applet", "iframe", "object", "embed"]):
        tag.decompose()

    target = soup.body if soup.body else soup

    allowed_tags = {
        "h1", "h2", "h3", "h4", "h5", "h6",
        "p", "br", "hr",
        "strong", "b", "em", "i", "u", "s", "sub", "sup",
        "ul", "ol", "li",
        "table", "thead", "tbody", "tfoot", "tr", "th", "td",
        "blockquote", "code", "pre", "span", "div", "a"
    }

    if demote_h1:
        for h1 in target.find_all("h1"):
            h1.name = "h2"

    for tag in target.find_all(True):
        if tag.name not in allowed_tags:
            tag.unwrap()
            continue

        attrs_to_keep = {}
        if tag.name == "a" and tag.has_attr("href"):
            href = tag["href"].strip()
            if not href.lower().startswith("javascript:"):
                attrs_to_keep["href"] = href
                attrs_to_keep["target"] = "_blank"
                attrs_to_keep["rel"] = "noopener noreferrer"

        if tag.name in ["td", "th"]:
            if tag.has_attr("colspan"):
                attrs_to_keep["colspan"] = tag["colspan"]
            if tag.has_attr("rowspan"):
                attrs_to_keep["rowspan"] = tag["rowspan"]

        tag.attrs = attrs_to_keep

    for p in target.find_all("p"):
        if not p.get_text(strip=True) and not p.find_all(["br", "img", "table"]):
            p.decompose()

    clean_content = "".join(str(c) for c in target.contents).strip()
    return clean_content


def convert_document_to_html(uploaded_file) -> str:
    """Принимает загруженный файл Django (UploadedFile / FieldFile) и возвращает чистый HTML."""
    filename = getattr(uploaded_file, "name", "")
    ext = os.path.splitext(filename.lower())[1]

    if ext not in SUPPORTED_EXTENSIONS:
        supported_str = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise ValueError(f"Неподдерживаемый формат файла: '{ext}'. Поддерживаются: {supported_str}")

    if hasattr(uploaded_file, "seek"):
        uploaded_file.seek(0)

    raw_html = ""

    if ext == ".docx":
        import mammoth
        result = mammoth.convert_to_html(uploaded_file)
        raw_html = result.value
        if result.messages:
            logger.info("Mammoth messages: %s", result.messages)

    elif ext in [".md", ".markdown"]:
        import markdown
        content_bytes = uploaded_file.read()
        text = decode_bytes(content_bytes)
        raw_html = markdown.markdown(
            text,
            extensions=["extra", "sane_lists", "tables", "nl2br"]
        )

    elif ext in [".html", ".htm"]:
        content_bytes = uploaded_file.read()
        raw_html = decode_bytes(content_bytes)

    elif ext == ".txt":
        content_bytes = uploaded_file.read()
        text = decode_bytes(content_bytes)
        paragraphs = text.split("\n\n")
        parts = []
        for p in paragraphs:
            clean = p.strip()
            if clean:
                escaped = html.escape(clean).replace("\n", "<br/>")
                parts.append(f"<p>{escaped}</p>")
        raw_html = "\n".join(parts)

    elif ext == ".pdf":
        import pypdf
        reader = pypdf.PdfReader(uploaded_file)
        parts = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            for chunk in page_text.split("\n\n"):
                clean = chunk.strip()
                if clean:
                    escaped = html.escape(clean).replace("\n", " ")
                    parts.append(f"<p>{escaped}</p>")
        raw_html = "\n".join(parts)

    return sanitize_and_clean_html(raw_html)
