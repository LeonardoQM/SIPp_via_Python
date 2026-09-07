import subprocess
from dataclasses import dataclass


@dataclass
class TestResult:
    name: str
    passed: bool
    return_code: int
    stdout: str
    stderr: str


def run_sipp_test(name: str, scenario: str, target: str) -> TestResult:

    command = [
        "sipp",
        target,
        "-sf", scenario,
        "-m", "1",
        "-trace_err",
        "-timeout", "10s",
    ]

    print(f"Running test: {name}")
    print(f"Command: {' '.join(command)}")

    process = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    return TestResult(
        name=name,
        passed=process.returncode == 0,
        return_code=process.returncode,
        stdout=process.stdout,
        stderr=process.stderr,
    )


def main():

    result = run_sipp_test(
        name="REGISTER user 1001",
        scenario="/app/scenarios/register.xml",
        target="asterisk:5060",
    )

    print()
    print("=" * 60)
    print(f"TEST:   {result.name}")
    print(f"RESULT: {'PASS' if result.passed else 'FAIL'}")
    print(f"EXIT:   {result.return_code}")
    print("=" * 60)

    if result.stdout:
        print("\nSIPp output:")
        print(result.stdout)

    if result.stderr:
        print("\nSIPp errors:")
        print(result.stderr)

    if not result.passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()