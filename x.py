#!/usr/bin/env python3

import argparse
from subprocess import call


def format(args):
    """
    Auto-formats project using black.
    """
    black_args = ["pipenv", "run", "black", "-l", "79", "."]
    print("Formatting code:", " ".join(black_args))
    return call(black_args)


def lint(args):
    """
    Lints project using pycodestyle
    """
    print("Linting project...")
    return call(["pipenv", "run", "pycodestyle", "api"])


def test(args):
    """
    Tests project using pytest.
    """
    pytest_args = ["pipenv", "run", "pytest"]
    if args.coverage:
        pytest_args.append("--cov")

    return call(pytest_args)


def dev(args):
    """
    Runs local API server
    """
    print("running local API server")
    return call(["pipenv", "run", "uvicorn", "api.main:app", "--reload"])


commands = (
    ("format", format),
    ("test", test, {"coverage": "Generate coverage report"}),
    ("dev", dev),
    ("lint", lint),
)


def main() -> int:
    parser = argparse.ArgumentParser()

    sub = parser.add_subparsers()

    for command in commands:
        sub_parser = sub.add_parser(command[0], help=command[1].__doc__)
        sub_parser.set_defaults(func=command[1])

        if len(command) > 2:
            for argument, doc in command[2].items():
                sub_parser.add_argument(f"--{argument}", action="store_true", help=doc)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    exit(main())
