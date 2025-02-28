import json
import logging
import subprocess
from pathlib import Path

import rich
from rich.console import Console
from rich.table import Table

import nf_core.utils
from nf_core.utils import plural_s as _s

log = logging.getLogger(__name__)

# Create a console used by all lint tests
console = Console(force_terminal=nf_core.utils.rich_force_colors())


def print_joint_summary(lint_obj, module_lint_obj):
    """Print a joint summary of the general pipe lint tests and the module lint tests"""
    nbr_passed = len(lint_obj.passed) + len(module_lint_obj.passed)
    nbr_ignored = len(lint_obj.ignored)
    nbr_fixed = len(lint_obj.fixed)
    nbr_warned = len(lint_obj.warned) + len(module_lint_obj.warned)
    nbr_failed = len(lint_obj.failed) + len(module_lint_obj.failed)

    summary_colour = "red" if nbr_failed > 0 else "green"
    table = Table(box=rich.box.ROUNDED, style=summary_colour)
    table.add_column("LINT RESULTS SUMMARY", no_wrap=True)
    table.add_row(rf"[green][✔] {nbr_passed:>3} Test{_s(nbr_passed)} Passed")
    if nbr_fixed:
        table.add_row(rf"[bright blue][?] {nbr_fixed:>3} Test{_s(nbr_fixed)} Fixed")
    table.add_row(rf"[grey58][?] {nbr_ignored:>3} Test{_s(nbr_ignored)} Ignored")
    table.add_row(rf"[yellow][!] {nbr_warned:>3} Test Warning{_s(nbr_warned)}")
    table.add_row(rf"[red][✗] {nbr_failed:>3} Test{_s(nbr_failed)} Failed")
    console.print(table)


def print_fixes(lint_obj):
    """Prints available and applied fixes"""

    if lint_obj.could_fix:
        fix_flags = "".join([f" --fix {fix}" for fix in lint_obj.could_fix])
        wf_dir = "" if lint_obj.wf_path == "." else f"--dir {lint_obj.wf_path}"
        fix_cmd = f"nf-core lint {wf_dir} {fix_flags}"
        console.print(
            "\nTip: Some of these linting errors can automatically be resolved with the following command:\n\n"
            f"[blue]    {fix_cmd}\n"
        )
    if len(lint_obj.fix):
        console.print(
            "Automatic fixes applied. "
            "Please check with 'git diff' and revert any changes you do not want with 'git checkout <file>'."
        )


def run_prettier_on_file(file):
    """Run the pre-commit hook prettier on a file.

    Args:
        file (Path | str): A file identifier as a string or pathlib.Path.

    Warns:
        If Prettier is not installed, a warning is logged.
    """

    nf_core_pre_commit_config = Path(nf_core.__file__).parent / ".pre-commit-prettier-config.yaml"
    try:
        subprocess.run(
            ["pre-commit", "run", "--config", nf_core_pre_commit_config, "prettier", "--files", file],
            capture_output=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        if ": SyntaxError: " in e.stdout.decode():
            log.critical(f"Can't format {file} because it has a syntax error.\n{e.stdout.decode()}")
        elif "files were modified by this hook" in e.stdout.decode():
            all_lines = [line for line in e.stdout.decode().split("\n")]
            files = "\n".join(all_lines[3:])
            log.debug(f"The following files were modified by prettier:\n {files}")
        elif e.stderr.decode():
            log.warning(
                "There was an error running the prettier pre-commit hook.\n"
                f"STDOUT: {e.stdout.decode()}\nSTDERR: {e.stderr.decode()}"
            )


def dump_json_with_prettier(file_name, file_content):
    """Dump a JSON file and run prettier on it.
    Args:
        file_name (Path | str): A file identifier as a string or pathlib.Path.
        file_content (dict): Content to dump into the JSON file
    """
    with open(file_name, "w") as fh:
        json.dump(file_content, fh, indent=4)
    run_prettier_on_file(file_name)
