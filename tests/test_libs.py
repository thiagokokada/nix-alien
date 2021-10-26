from unittest.mock import patch, Mock
from collections import namedtuple

from nix_alien import libs

CompletedProcessMock = namedtuple("CompletedProcess", ["stdout"])
DependencyMock = namedtuple("Dependency", ["soname", "path", "found"])


def test_find_lib_candidates():
    with patch("nix_alien.libs.subprocess", autospec=True) as mock_subprocess:
        # No candidates
        mock_subprocess.run.return_value = CompletedProcessMock(stdout="")
        assert libs.find_lib_candidates("xyz") == []

        # One candidate
        mock_subprocess.run.return_value = CompletedProcessMock(stdout="foo.out")
        assert libs.find_lib_candidates("xyz") == ["foo.out"]

        # Multiple candidates
        mock_subprocess.run.return_value = CompletedProcessMock(
            stdout="""\
foo.out
bar.out
        """
        )
        assert libs.find_lib_candidates("xyz") == ["foo.out", "bar.out"]

        mock_subprocess.run.return_value = CompletedProcessMock(
            stdout="foo.out\nbar.out\nquux.out"
        )
        assert libs.find_lib_candidates("xyz") == ["foo.out", "bar.out", "quux.out"]


def test_find_libs_when_no_candidates_found():
    with patch("nix_alien.libs.lddwrap", autospec=True) as mock_lddwrap, patch(
        "nix_alien.libs.subprocess", autospec=True
    ) as mock_subprocess:
        mock_lddwrap.list_dependencies.return_value = [
            DependencyMock(soname="libfoo.so", path="/lib/libfoo.so", found=False),
            DependencyMock(soname="libbar.so", path="/lib/libbar.so", found=False),
        ]
        mock_subprocess.run.return_value = CompletedProcessMock(stdout="")
        assert libs.find_libs("xyz") == {
            "libfoo.so": None,
            "libbar.so": None,
        }


def test_find_libs_when_one_candidate_found():
    with patch("nix_alien.libs.lddwrap", autospec=True) as mock_lddwrap, patch(
        "nix_alien.libs.subprocess", autospec=True
    ) as mock_subprocess, patch(
        "nix_alien.libs.FzfPrompt", spec_set=True
    ) as mock_fzfprompt:
        mock_lddwrap.list_dependencies.return_value = [
            DependencyMock(soname="libfoo.so", path="/lib/libfoo.so", found=False),
            DependencyMock(soname="libbar.so", path="/lib/libbar.so", found=False),
        ]
        mock_subprocess.run.return_value = CompletedProcessMock(stdout="foo.out")
        mock_fzfprompt.prompt.return_value = ["foo.out"]
        assert libs.find_libs("xyz") == {
            "libfoo.so": "foo.out",
            "libbar.so": "foo.out",
        }


def test_find_libs_when_multiple_candidates_found():
    with patch("nix_alien.libs.lddwrap", autospec=True) as mock_lddwrap, patch(
        "nix_alien.libs.subprocess", autospec=True
    ) as mock_subprocess, patch("nix_alien.libs.fzf", autospec=True) as mock_fzfprompt:
        mock_lddwrap.list_dependencies.return_value = [
            DependencyMock(soname="libfoo.so", path="/lib/libfoo.so", found=False),
            DependencyMock(soname="libbar.so", path="/lib/libbar.so", found=False),
        ]
        mock_subprocess.run.return_value = CompletedProcessMock(
            stdout="foo.out\nbar.out"
        )
        # On the second time, this will take the candidate from intersection
        mock_fzfprompt.prompt.side_effect = [["foo.out"]]
        assert libs.find_libs("xyz") == {
            "libfoo.so": "foo.out",
            "libbar.so": "foo.out",
        }
