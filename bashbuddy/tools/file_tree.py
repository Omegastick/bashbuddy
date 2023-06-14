import os

from bashbuddy.tools.persistent_bash import PersistentBash

TRUNCATED_MESSAGE = "Truncated due to too many items..."


def generate_file_tree(root_dir: str) -> dict:
    if root_dir.endswith(os.sep):
        root_dir = root_dir[:-1]

    file_tree: dict = {root_dir: {}}

    for root, dirs, files in os.walk(root_dir):
        if root.split(os.sep)[-1].startswith("."):
            continue

        path_parts = root.replace(root_dir, "").split(os.sep)[1:]

        parent_dict = file_tree[root_dir]
        for part in path_parts:
            parent_dict = parent_dict.get(part, {})

        for directory in dirs:
            if directory.startswith("."):
                continue
            parent_dict[directory] = {}

        for file in files:
            if file.startswith("."):
                continue
            parent_dict[file] = None

        file_tree

    return file_tree


def format_file_tree(file_tree: dict, parent_path: str = ".", max_items_per_directory: int = 50) -> str:
    """
    Given a file tree as a nested dict, return a string representation of the tree, formatted as follows:

    # /path/to/directory
    dir1/
    file1.txt
    # /path/to/directory/dir1
    file2.txt

    If a directory contains more than `max_items_per_directory`, the directory listing is truncated.
    """
    if parent_path.endswith(os.sep):
        parent_path = parent_path[:-1]

    formatted_tree = f"# {parent_path}\n"

    if parent_path in file_tree:
        file_tree = file_tree[parent_path]

    keys = get_sorted_keys(file_tree)

    formatted_tree += format_directory(file_tree, keys, max_items_per_directory)

    for key in keys:
        if isinstance(file_tree[key], dict):
            formatted_tree += format_file_tree(file_tree[key], os.path.join(parent_path, key), max_items_per_directory)

    return formatted_tree


def get_sorted_keys(file_tree: dict) -> list:
    """Return a sorted list of keys from a directory in the file tree."""
    return sorted(file_tree.keys(), key=lambda x: (not isinstance(file_tree[x], dict), x))


def format_directory(file_tree: dict, keys: list, max_items_per_directory: int) -> str:
    """Format the directory listing, and truncate if it exceeds `max_items_per_directory`."""
    formatted_listing = ""
    item_count = 0

    for key in keys:
        if item_count >= max_items_per_directory:
            formatted_listing += TRUNCATED_MESSAGE + "\n"
            return formatted_listing

        if isinstance(file_tree[key], dict):
            formatted_listing += key + "/\n"
        else:
            formatted_listing += key + "\n"

        item_count += 1

    return formatted_listing


class FileTree:
    def __init__(self, persistent_bash: PersistentBash):
        self.bash = persistent_bash

    def _truncate_file_tree(self, file_tree: str, max_lines: int) -> str:
        lines = file_tree.split("\n")
        if len(lines) > max_lines:
            return "\n".join(lines[:max_lines]) + "\n" + TRUNCATED_MESSAGE + "\n"
        return file_tree

    def get(self, path: str = ".", max_lines=100) -> str:
        if path == ".":
            current_dir = self.bash.run("pwd").strip()
        else:
            current_dir = os.path.join(self.bash.run("pwd").strip(), path)
        file_tree = generate_file_tree(current_dir)
        formatted_file_tree = format_file_tree(file_tree, current_dir)
        truncated_file_tree = self._truncate_file_tree(formatted_file_tree, max_lines)
        return truncated_file_tree
