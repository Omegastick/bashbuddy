from unittest.mock import MagicMock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from bashbuddy.tools.file_tree import FileTree, format_directory, format_file_tree, generate_file_tree, get_sorted_keys
from bashbuddy.tools.persistent_bash import PersistentBash


@pytest.fixture
def mock_bash():
    return MagicMock(spec=PersistentBash)


@pytest.fixture
def fs(fs: FakeFilesystem) -> FakeFilesystem:
    fs.create_dir("/test")
    fs.create_file("/test/file1.txt")
    fs.create_file("/test/dir1/file2.txt")
    fs.create_file("/test/dir1/dir2/file3.txt")
    return fs


def test_generate_file_tree(fs: FakeFilesystem):
    file_tree = generate_file_tree("/test")
    expected_tree = {"/test": {"dir1": {"dir2": {"file3.txt": None}, "file2.txt": None}, "file1.txt": None}}
    assert file_tree == expected_tree


def test_generate_file_tree_ignores_hidden_files(fs: FakeFilesystem):
    fs.create_file("/test/.hidden.txt")
    file_tree = generate_file_tree("/test")
    expected_tree = {"/test": {"dir1": {"dir2": {"file3.txt": None}, "file2.txt": None}, "file1.txt": None}}
    assert file_tree == expected_tree


def test_generate_file_tree_ignores_hidden_directories(fs: FakeFilesystem):
    fs.create_dir("/test/.hidden")
    fs.create_file("/test/.hidden/file.txt")
    file_tree = generate_file_tree("/test")
    expected_tree = {"/test": {"dir1": {"dir2": {"file3.txt": None}, "file2.txt": None}, "file1.txt": None}}
    assert file_tree == expected_tree


def test_generate_file_tree_handles_trailing_slash(fs: FakeFilesystem):
    file_tree = generate_file_tree("/test/")
    expected_tree = {"/test": {"dir1": {"dir2": {"file3.txt": None}, "file2.txt": None}, "file1.txt": None}}
    assert file_tree == expected_tree


def test_format_file_tree(fs: FakeFilesystem):
    file_tree = {"/test": {"dir1": {"dir2": {"file3.txt": None}, "file2.txt": None}, "file1.txt": None}}
    formatted_tree = format_file_tree(file_tree, "/test")
    expected_tree = """# /test
dir1/
file1.txt
# /test/dir1
dir2/
file2.txt
# /test/dir1/dir2
file3.txt
"""
    assert formatted_tree == expected_tree


def test_format_file_tree_truncates_if_too_many_lines(fs: FakeFilesystem):
    file_tree = {"/test": {"file1.txt": None, "file2.txt": None, "file3.txt": None, "file4.txt": None}}
    formatted_tree = format_file_tree(file_tree, "/test", max_items_per_directory=3)
    expected_tree = """# /test
file1.txt
file2.txt
file3.txt
Truncated due to too many items...
"""
    assert formatted_tree == expected_tree


def test_nested_large_file_tree(fs: FakeFilesystem):
    file_tree = {
        "/test": {
            "dir1": {
                "dir2": {"file1.txt": None, "file2.txt": None, "file3.txt": None, "file4.txt": None},
            },
            "file5.txt": None,
        }
    }
    formatted_tree = format_file_tree(file_tree, "/test", max_items_per_directory=3)
    expected_tree = """# /test
dir1/
file5.txt
# /test/dir1
dir2/
# /test/dir1/dir2
file1.txt
file2.txt
file3.txt
Truncated due to too many items...
"""
    assert formatted_tree == expected_tree


def test_get_file_tree(mock_bash, fs: FakeFilesystem):
    mock_bash.run.return_value = "/test"
    file_tree = FileTree(mock_bash)
    result = file_tree.get()
    expected_result = """# /test
dir1/
file1.txt
# /test/dir1
dir2/
file2.txt
# /test/dir1/dir2
file3.txt
"""
    assert result == expected_result


def test_format_directory(fs: FakeFilesystem):
    file_tree = {"/test": {"file1.txt": None, "file2.txt": None, "file3.txt": None, "file4.txt": None}}
    keys = sorted(file_tree["/test"].keys(), key=lambda x: (not isinstance(file_tree["/test"][x], dict), x))
    formatted_listing = format_directory(file_tree["/test"], keys, 3)
    expected_listing = """file1.txt
file2.txt
file3.txt
Truncated due to too many items...
"""
    assert formatted_listing == expected_listing


def test_get_sorted_keys():
    file_tree = {"/test": {"dir1": {"dir2": {"file3.txt": None}, "file2.txt": None}, "file1.txt": None}}
    keys = get_sorted_keys(file_tree["/test"])
    expected_keys = ["dir1", "file1.txt"]
    assert keys == expected_keys
