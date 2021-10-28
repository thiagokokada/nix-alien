import json
from collections import namedtuple
from unittest.mock import patch

from nix_alien import libs

CompletedProcessMock = namedtuple("CompletedProcessMock", ["stdout"])
DependencyMock = namedtuple("DependencyMock", ["soname", "path", "found"])


@patch("nix_alien.libs.subprocess", autospec=True)
def test_find_lib_candidates(mock_subprocess):
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


@patch("nix_alien.libs.lddwrap", autospec=True)
@patch("nix_alien.libs.subprocess", autospec=True)
def test_find_libs_when_no_candidates_found(mock_subprocess, mock_lddwrap):
    mock_lddwrap.list_dependencies.return_value = [
        DependencyMock(soname="libfoo.so", path="/lib/libfoo.so", found=False),
        DependencyMock(soname="libbar.so", path="/lib/libbar.so", found=False),
    ]
    mock_subprocess.run.return_value = CompletedProcessMock(stdout="")
    assert libs.find_libs("xyz") == {
        "libfoo.so": None,
        "libbar.so": None,
    }


@patch("nix_alien.libs.lddwrap", autospec=True)
@patch("nix_alien.libs.subprocess", autospec=True)
@patch("nix_alien.libs.fzf", autospec=True)
def test_find_libs_when_one_candidate_found(
    mock_fzfprompt,
    mock_subprocess,
    mock_lddwrap,
):
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


@patch("nix_alien.libs.lddwrap", autospec=True)
@patch("nix_alien.libs.subprocess", autospec=True)
@patch("nix_alien.libs.fzf", autospec=True)
def test_find_libs_when_multiple_candidates_found(
    mock_fzfprompt,
    mock_subprocess,
    mock_lddwrap,
):
    mock_lddwrap.list_dependencies.return_value = [
        DependencyMock(soname="libfoo.so", path="/lib/libfoo.so", found=False),
        DependencyMock(soname="libbar.so", path="/lib/libbar.so", found=False),
    ]
    mock_subprocess.run.return_value = CompletedProcessMock(stdout="foo.out\nbar.out")
    # On the second time, this will take the candidate from intersection
    mock_fzfprompt.prompt.side_effect = [["foo.out"]]
    assert libs.find_libs("xyz") == {
        "libfoo.so": "foo.out",
        "libbar.so": "foo.out",
    }


def test_get_unique_packages():
    assert libs.get_unique_packages({}) == []

    assert (
        libs.get_unique_packages(
            {
                "libfoo.so": "foo.out",
                "libbar.so": "bar.out",
                "libnone.so": None,
            }
        )
        == ["bar.out", "foo.out"]
    )

    assert (
        libs.get_unique_packages(
            {
                "libfoo.so": "foo.out",
                "libbar.so": "foo.out",
                "libnone.so": None,
            }
        )
        == ["foo.out"]
    )


@patch("nix_alien.libs.lddwrap", autospec=True)
@patch("nix_alien.libs.subprocess", autospec=True)
def test_main_wo_args(mock_subprocess, mock_lddwrap, capsys):
    mock_lddwrap.list_dependencies.return_value = [
        DependencyMock(soname="libfoo.so", path="/lib/libfoo.so", found=False),
        DependencyMock(soname="libbar.so", path="/lib/libbar.so", found=False),
    ]
    mock_subprocess.run.return_value = CompletedProcessMock(stdout="foo.out")
    libs.main(["xyz"])

    out, err = capsys.readouterr()
    assert out == "foo.out\n"
    assert (
        err
        == """\
Selected candidate for 'libfoo.so': foo.out
Selected candidate for 'libbar.so': foo.out
"""
    )


@patch("nix_alien.libs.lddwrap", autospec=True)
@patch("nix_alien.libs.subprocess", autospec=True)
def test_main_with_args(mock_subprocess, mock_lddwrap, capsys):
    mock_lddwrap.list_dependencies.return_value = [
        DependencyMock(soname="libfoo.so", path="/lib/libfoo.so", found=False),
        DependencyMock(soname="libbar.so", path="/lib/libbar.so", found=False),
    ]
    mock_subprocess.run.return_value = CompletedProcessMock(stdout="foo.out")
    libs.main(["xyz", "--json"])

    out, err = capsys.readouterr()
    assert json.loads(out) == {
        "libfoo.so": "foo.out",
        "libbar.so": "foo.out",
    }
    assert (
        err
        == """\
Selected candidate for 'libfoo.so': foo.out
Selected candidate for 'libbar.so': foo.out
"""
    )
