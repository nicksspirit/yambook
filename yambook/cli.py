import argparse
from pathlib import Path

from yambook.yaml2bookmark import load_yaml, write_html
from yambook.bookmark2yaml import load_html, write_yaml


def error_msg(msg: str) -> str:
    return "yaml2bookmark: error: %s\n" % (msg,)


def init_yaml2bookmark(parser: argparse.ArgumentParser):
    parser.add_argument("yaml_path", metavar="INPUT", help="YAML file.", type=Path)
    parser.add_argument(
        "-o",
        "--output-bookmark",
        help="output bookmark file.",
        default="bookmarks.html",
        type=Path,
    )

    def handle_args(yaml_path: Path, output_bookmark: Path, **kwargs) -> None:
        if not yaml_path.exists():
            parser.exit(1, error_msg(f"File {yaml_path} does not exist."))

        if not output_bookmark.exists():
            output_bookmark.parent.mkdir(parents=True, exist_ok=True)
            output_bookmark.touch(exist_ok=True)

        yaml_bookmark: list[dict] = load_yaml(yaml_path)

        write_html(yaml_bookmark, output_bookmark)

    return handle_args


def init_bookmark2mark(parser: argparse.ArgumentParser):
    parser.add_argument("html_path", metavar="INPUT", help="Bookmark file.", type=Path)
    parser.add_argument(
        "-o",
        "--output-yaml",
        help="output yaml file.",
        default="bookmarks.yaml",
        type=Path,
    )

    def handle_args(html_path: Path, output_yaml: Path, **kwargs) -> None:
        if not html_path.exists():
            parser.exit(1, error_msg(f"File {html_path} does not exist."))

        if not output_yaml.exists():
            output_yaml.parent.mkdir(parents=True, exist_ok=True)
            output_yaml.touch(exist_ok=True)

        bookmark_soup = load_html(html_path)

        write_yaml(bookmark_soup, output_yaml)

    return handle_args


def main() -> None:
    parser = argparse.ArgumentParser("")
    sub_parser = parser.add_subparsers(
        dest="command", title="available commands", metavar="command [options ...]"
    )

    y2b_parser = sub_parser.add_parser(
        "yaml2bookmark", help="Convert YAML to bookmark."
    )
    b2y_parser = sub_parser.add_parser(
        "bookmark2yaml", help="Convert bookmark to YAML."
    )

    handle_yaml2bmark_args = init_yaml2bookmark(y2b_parser)
    handle_bmark2yaml_args = init_bookmark2mark(b2y_parser)

    cmd_args = parser.parse_args()

    if cmd_args.command == "yaml2bookmark":
        handle_yaml2bmark_args(**vars(cmd_args))
    elif cmd_args.command == "bookmark2yaml":
        handle_bmark2yaml_args(**vars(cmd_args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
