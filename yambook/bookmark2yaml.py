from pathlib import Path
from typing import cast

import yaml
from bs4 import BeautifulSoup
from bs4.element import Tag as HTMLTag

DEFAULT_YAML_PATH = Path("./bookmarks.yaml")


def load_html(html_input: str | Path) -> BeautifulSoup:
    html_str = html_input if isinstance(html_input, str) else html_input.read_text()

    return BeautifulSoup(html_str, "html.parser")


def clean_content(content: str):
    clean_content_ = content.replace("\n", "").replace("\t", " ").strip()
    words = clean_content_.split(" ")

    return " ".join(filter(bool, words))


def parse_anchor_tag(anchor_tag: HTMLTag) -> dict:
    anchor_attr = {
        "title": clean_content(anchor_tag.text),
        "url": anchor_tag.get("href"),
    }

    if icon := anchor_tag.get("icon"):
        anchor_attr["icon"] = icon

    if icon_uri := anchor_tag.get("icon_uri"):  # only in FF
        anchor_attr["icon_uri"] = icon_uri

    # tags = child.get('tags')
    # if tags:
    #     data['tags'] = tags.split(',')

    return anchor_attr


def parse_folder_tag(folder_tag: HTMLTag) -> dict:
    folder_attr = {"folder": clean_content(folder_tag.text), "ns_root": None}

    # data['add_date'] = child.get('add_date')
    # data['last_modified'] = child.get('last_modified')

    # for Bookmarks Toolbar in Firefox and Bookmarks bar in Chrome
    if folder_tag.get("personal_toolbar_folder"):
        folder_attr["ns_root"] = "toolbar"

    # FirfFox Other Bookmarks
    if folder_tag.get("unfiled_bookmarks_folder"):
        folder_attr["ns_root"] = "other_bookmarks"

    return folder_attr


def parse_node(node: HTMLTag):
    data = {}
    is_folder = False

    for c in node.children:
        child = cast(HTMLTag, c)

        if child.name == "a":
            data = parse_anchor_tag(child)
        elif child.name == "h3":
            is_folder = True
            data = parse_folder_tag(child)
        elif child.name == "dl":
            # Store DL element reference for further processing the child nodes
            data["__dir_dl"] = child

    if is_folder and not data.get("__dir_dl"):
        node_next_sibling = cast(HTMLTag, node.next_sibling)

        if node_next_sibling and node_next_sibling.name == "dd":
            dls = node_next_sibling.find_all("dl")
            if dls:
                data["__dir_dl"] = dls[0]

    return data


def parse_bookmark(root_tag: HTMLTag, level: int = 0):
    bookmarks = []
    menu_root = None

    nodes = root_tag.find_all("dt") if root_tag.name == "dl" else root_tag.p.children

    for c in nodes:
        child = cast(HTMLTag, c)

        if child.name != "dt":
            continue

        item_data = parse_node(child)

        if level == 0 and (not item_data.get("ns_root")):
            if menu_root is None:
                menu_root = {
                    "folder": "Bookmarks",
                    "bookmarks": [],
                    "ns_root": "menu",
                }

            if item_data.get("__dir_dl"):
                item_data["bookmarks"] = parse_bookmark(
                    item_data["__dir_dl"], level + 1
                )
                del item_data["__dir_dl"]

            if len(bookmarks) > 0:
                is_url = "url" in item_data
                first_item_is_folder = "folder" in bookmarks[0]

                if is_url and first_item_is_folder:
                    continue

            menu_root["bookmarks"].append(item_data)
        else:
            if item_data.get("__dir_dl"):
                item_data["bookmarks"] = parse_bookmark(
                    item_data["__dir_dl"], level + 1
                )
                del item_data["__dir_dl"]

            if len(bookmarks) > 0:
                is_url = "url" in item_data
                first_item_is_folder = "folder" in bookmarks[0]

                if is_url and first_item_is_folder:
                    continue

            bookmarks.append(item_data)

    if menu_root:
        bookmarks.append(menu_root)

    return bookmarks


def generate_yaml(bookmark_soup: BeautifulSoup):
    root_tag = bookmark_soup.select_one("dl")

    if root_tag is None:
        return []

    yaml_bookmarks = parse_bookmark(root_tag)

    return yaml_bookmarks


def write_yaml(html_bookmark: BeautifulSoup, output_file: Path = DEFAULT_YAML_PATH):
    yaml_bookmarks = generate_yaml(html_bookmark)
    yaml_str = yaml.dump_all(yaml_bookmarks, sort_keys=False, allow_unicode=True)

    output_file.write_text(yaml_str, encoding="utf-8")
