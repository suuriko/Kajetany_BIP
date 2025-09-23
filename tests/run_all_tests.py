#!/usr/bin/env python3
"""
Master test script - runs all template tests and provides summary.
"""

import subprocess
import sys
from pathlib import Path


def run_test(script_path: str, test_name: str):
    """Run a test script and capture results."""
    print(f"{'=' * 60}")
    print(f"Running {test_name}")
    print(f"{'=' * 60}")

    try:
        result = subprocess.run(
            [sys.executable, script_path], capture_output=True, text=True, cwd=Path(__file__).parent.parent
        )

        if result.returncode == 0:
            print(result.stdout)
            print(f"✅ {test_name} completed successfully!")
            return True
        else:
            print(f"❌ {test_name} failed!")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False

    except Exception as e:
        print(f"❌ {test_name} failed with exception: {e}")
        return False


def main():
    """Run all template tests."""
    print("🧪 Template Test Suite")
    print("=" * 60)
    print("Running all template generation tests...\n")

    tests = [
        ("tests/test_email_template.py", "Email Template Test"),
        ("tests/test_bip_report.py", "BIP Report Template Test"),
    ]

    results = []

    for script_path, test_name in tests:
        success = run_test(script_path, test_name)
        results.append((test_name, success))
        print()  # Add spacing between tests

    # Summary
    print("=" * 60)
    print("🏁 Test Summary")
    print("=" * 60)

    total_tests = len(results)
    passed_tests = sum(1 for _, success in results if success)
    failed_tests = total_tests - passed_tests

    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"  {status} - {test_name}")

    print(f"\nTotal: {total_tests} tests")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")

    if failed_tests == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed_tests} test(s) failed!")

    # Show generated files
    test_outputs = ["tests/test_email_output.html", "tests/test_bip_report_output.html"]

    print("\n📄 Generated files:")
    for output_file in test_outputs:
        if Path(output_file).exists():
            full_path = Path(output_file).absolute()
            print(f"  • {output_file}")
            print(f"    file://{full_path}")

    return 0 if failed_tests == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
