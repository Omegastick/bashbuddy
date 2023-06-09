import os

from bashbuddy.tools.persistent_bash import PersistentBash


def generate_file_tree(root_dir: str) -> dict:
    file_tree: dict = {root_dir: {}}

    for root, dirs, files in os.walk(root_dir):
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


def format_file_tree(file_tree: dict, parent_path=".") -> str:
    formatted_tree = f"# {parent_path}\n"

    if parent_path in file_tree:
        file_tree = file_tree[parent_path]

    keys = sorted(file_tree.keys(), key=lambda x: (not isinstance(file_tree[x], dict), x))

    for key in keys:
        if isinstance(file_tree[key], dict):
            formatted_tree += key + "/\n"
        else:
            formatted_tree += key + "\n"

    formatted_tree += "###\n"

    for key in keys:
        if isinstance(file_tree[key], dict):
            formatted_tree += format_file_tree(file_tree[key], os.path.join(parent_path, key))

    return formatted_tree


class FileTree:
    def __init__(self, persistent_bash: PersistentBash):
        self.bash = persistent_bash

    def get(self, path: str = ".") -> str:
        if path == ".":
            current_dir = self.bash.run("pwd").strip()
        else:
            current_dir = os.path.join(self.bash.run("pwd").strip(), path)
        file_tree = generate_file_tree(current_dir)
        return format_file_tree(file_tree, current_dir)
