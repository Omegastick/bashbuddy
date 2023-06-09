from unittest.mock import MagicMock

import pytest
from pyfakefs.fake_filesystem import FakeFilesystem

from bashbuddy.tools.file_tree import FileTree, format_file_tree, generate_file_tree
from bashbuddy.tools.persistent_bash import PersistentBash


@pytest.fixture
def mock_bash():
    return MagicMock(spec=PersistentBash)


@pytest.fixture
def fs(fs: FakeFilesystem) -> FakeFilesystem:
    fs.create_dir("/test")
    fs.create_file("/test/file1.txt", contents="File 1 content")
    fs.create_file("/test/dir1/file2.txt", contents="File 2 content")
    fs.create_file("/test/dir1/dir2/file3.txt", contents="File 3 content")
    return fs


def test_generate_file_tree(fs: FakeFilesystem):
    file_tree = generate_file_tree("/test")
    expected_tree = {"/test": {"dir1": {"dir2": {"file3.txt": None}, "file2.txt": None}, "file1.txt": None}}
    assert file_tree == expected_tree


def test_format_file_tree(fs: FakeFilesystem):
    file_tree = {"/test": {"dir1": {"dir2": {"file3.txt": None}, "file2.txt": None}, "file1.txt": None}}
    formatted_tree = format_file_tree(file_tree, "/test")
    expected_tree = (
        "# /test\ndir1/\nfile1.txt\n###\n# /test/dir1\ndir2/\nfile2.txt\n###\n# /test/dir1/dir2\nfile3.txt\n###\n"
    )
    assert formatted_tree == expected_tree


def test_get_file_tree(mock_bash, fs: FakeFilesystem):
    mock_bash.run.return_value = "/test"
    file_tree = FileTree(mock_bash)
    result = file_tree.get()
    expected_result = (
        "# /test\ndir1/\nfile1.txt\n###\n# /test/dir1\ndir2/\nfile2.txt\n###\n# /test/dir1/dir2\nfile3.txt\n###\n"
    )
    assert result == expected_result
