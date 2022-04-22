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


@patch("nix_alien.libs.list_dependencies", autospec=True)
@patch("nix_alien.libs.subprocess", autospec=True)
def test_find_libs_when_no_candidates_found(
    mock_subprocess,
    mock_list_dependencies,
    capsys,
):
    mock_list_dependencies.return_value = [
        DependencyMock(soname="libfoo.so", path="/lib/libfoo.so", found=False),
        DependencyMock(soname="libbar.so", path="/lib/libbar.so", found=False),
    ]
    mock_subprocess.run.return_value = CompletedProcessMock(stdout="")
    assert libs.find_libs("xyz") == {
        "libfoo.so": None,
        "libbar.so": None,
    }

    _, err = capsys.readouterr()
    assert (
        err
        == """\
No candidate found for 'libfoo.so'
Selected candidate for 'libfoo.so': None
No candidate found for 'libbar.so'
Selected candidate for 'libbar.so': None
"""
    )


@patch("nix_alien.libs.list_dependencies", autospec=True)
@patch("nix_alien.libs.subprocess", autospec=True)
@patch("nix_alien.libs.fzf", autospec=True)
def test_find_libs_when_one_candidate_found(
    mock_fzf,
    mock_subprocess,
    mock_list_dependencies,
    capsys,
):
    mock_list_dependencies.return_value = [
        DependencyMock(soname="libfoo.so", path="/lib/libfoo.so", found=False),
        DependencyMock(soname="libbar.so", path="/lib/libbar.so", found=False),
        DependencyMock(soname="libquux.so", path="/lib/libbar.so", found=False),
    ]
    mock_subprocess.run.return_value = CompletedProcessMock(stdout="foo.out")
    mock_fzf.prompt.return_value = ["foo.out"]
    assert libs.find_libs("xyz") == {
        "libfoo.so": "foo.out",
        "libbar.so": "foo.out",
        "libquux.so": "foo.out",
    }

    _, err = capsys.readouterr()
    assert (
        err
        == """\
Selected candidate for 'libfoo.so': foo.out
Selected candidate for 'libbar.so': foo.out
Selected candidate for 'libquux.so': foo.out
"""
    )


@patch("nix_alien.libs.list_dependencies", autospec=True)
@patch("nix_alien.libs.subprocess", autospec=True)
@patch("nix_alien.libs.fzf", autospec=True)
def test_find_libs_when_multiple_candidates_found(
    mock_fzf,
    mock_subprocess,
    mock_list_dependencies,
    capsys,
):
    mock_list_dependencies.return_value = [
        DependencyMock(soname="libfoo.so", path="/lib/libfoo.so", found=False),
        DependencyMock(soname="libbar.so", path="/lib/libbar.so", found=False),
        DependencyMock(soname="libbar.so", path="/lib/libbar.so", found=False),
    ]
    mock_subprocess.run.return_value = CompletedProcessMock(stdout="foo.out\nbar.out")
    # On the second time, this will take the candidate from intersection
    mock_fzf.prompt.side_effect = [["foo.out"]]
    assert libs.find_libs("xyz", silent=True, additional_libs=["libquux.so"]) == {
        "libfoo.so": "foo.out",
        "libbar.so": "foo.out",
        "libquux.so": "foo.out",
    }

    _, err = capsys.readouterr()
    assert err == ""


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


@patch("nix_alien.libs.list_dependencies", autospec=True)
@patch("nix_alien.libs.subprocess", autospec=True)
def test_main_wo_args(mock_subprocess, mock_list_dependencies, capsys):
    mock_list_dependencies.return_value = [
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


@patch("nix_alien.libs.list_dependencies", autospec=True)
@patch("nix_alien.libs.subprocess", autospec=True)
def test_main_with_args(mock_subprocess, mock_list_dependencies, capsys):
    mock_list_dependencies.return_value = [
        DependencyMock(soname="libfoo.so", path="/lib/libfoo.so", found=False),
        DependencyMock(soname="libbar.so", path="/lib/libbar.so", found=False),
    ]
    mock_subprocess.run.return_value = CompletedProcessMock(stdout="foo.out")
    libs.main(["xyz", "--json", "--silent", "-l", "libqux.so", "-l", "libquux.so"])

    out, err = capsys.readouterr()
    assert json.loads(out) == {
        "libfoo.so": "foo.out",
        "libbar.so": "foo.out",
        "libqux.so": "foo.out",
        "libquux.so": "foo.out",
    }
    assert err == ""
