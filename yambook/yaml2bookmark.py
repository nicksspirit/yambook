import yaml
import io
from pathlib import Path
from typing import Generator

HtmlTag = Generator[str, None, None]

DEFAULT_HTML_PATH = Path("./bookmarks.html")

SEPARATOR = "---"

HTML_TEMPLATE = """
<!DOCTYPE NETSCAPE-Bookmark-file-1>
<!-- This is an automatically generated file.
     It will be read and overwritten.
     DO NOT EDIT! -->
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">
<TITLE>Bookmarks</TITLE>
<H1>Bookmarks</H1>
{content}
"""


def load_yaml(yaml_input: str | Path) -> list[dict]:
    yaml_str = yaml_input if isinstance(yaml_input, str) else yaml_input.read_text()

    return yaml.safe_load(yaml_str)


def generate_html(yaml_bookmarks: list[dict], level: int = 0) -> HtmlTag:
    indent = "    " * level

    yield f"{indent}<DL><p>\n"

    for ymlbmark in yaml_bookmarks:
        if "folder" in ymlbmark:
            yield f"{indent}<DT><H3>{ymlbmark['folder']}</H3>\n"
            yield from generate_html(ymlbmark["bookmarks"], level + 1)

        else:
            url_attr = f'HREF="{ymlbmark["url"]}"' if "url" in ymlbmark else ""
            icon_attr = f'ICON="{ymlbmark["icon"]}"' if "icon" in ymlbmark else ""

            tags = ymlbmark["tags"] if "tags" in ymlbmark else []
            tag_attr = f'TAGS="{",".join(tags)}"' if tags else ""

            description = (
                f"<!--{ymlbmark['description']}-->\n"
                if "description" in ymlbmark
                else ""
            )

            yield f"""{indent}
                <DT>
                    {description}
                    <A {url_attr} {icon_attr} {tag_attr}>{ymlbmark["title"]}</A>
                </DT>\n
            """

    yield f"{indent}</DL><p>\n"


def write_html(yaml_bookmark: list[dict], output_file: Path = DEFAULT_HTML_PATH):
    html_body = io.StringIO()

    for html_tag in generate_html(yaml_bookmark):
        html_body.write(html_tag)

    bookmark_html = HTML_TEMPLATE.format(content=html_body.getvalue())

    output_file.write_text(bookmark_html)
