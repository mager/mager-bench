"""Benchmark challenges — each is a coding task sent verbatim to each model."""

from dataclasses import dataclass


@dataclass
class Challenge:
    name: str
    description: str
    prompt: str
    # rubric hints passed to the judge
    rubric: dict


CHALLENGES: list[Challenge] = [
    Challenge(
        name="fizzbuzz",
        description="Classic FizzBuzz — tests basic correctness and code style",
        prompt=(
            "Write a Python function `fizzbuzz(n: int) -> list[str]` that returns a list "
            "of strings for numbers 1 through n: 'Fizz' for multiples of 3, 'Buzz' for "
            "multiples of 5, 'FizzBuzz' for multiples of both, and the number as a string otherwise. "
            "Include a docstring and at least one usage example."
        ),
        rubric={
            "correctness": "Does the function handle all four cases correctly? Does it return a list?",
            "quality": "Is the code clean, idiomatic Python? Good variable names? No unnecessary complexity?",
            "documentation": "Is there a clear docstring? Is there a usage example?",
        },
    ),
    Challenge(
        name="binary-search",
        description="Binary search implementation with full docs",
        prompt=(
            "Implement `binary_search(arr: list[int], target: int) -> int` in Python. "
            "It should return the index of target in a sorted list, or -1 if not found. "
            "Write a proper docstring with Args, Returns, and Raises sections. "
            "Add inline comments explaining the algorithm logic. Include 3 test cases as examples in the docstring."
        ),
        rubric={
            "correctness": "Is the binary search algorithm correct? Does it handle edge cases (empty list, target not found, duplicates)?",
            "quality": "Is the loop/recursion clean? Correct handling of integer overflow for mid calculation?",
            "documentation": "Does it have Args/Returns/Raises docstring? Are inline comments meaningful (not just restating the code)? Are the 3 examples correct?",
        },
    ),
    Challenge(
        name="api-client",
        description="Write a small HTTP API client class with error handling and docs",
        prompt=(
            "Write a Python class `APIClient` that wraps the `requests` library for a REST API. "
            "It should: (1) accept a base_url and optional api_key in __init__, "
            "(2) have a `get(path, params=None)` method and a `post(path, data)` method, "
            "(3) raise a custom `APIError` exception with the status code and message on non-2xx responses, "
            "(4) include type hints throughout, "
            "(5) have a complete docstring on the class and each public method. "
            "Show a usage example at the bottom."
        ),
        rubric={
            "correctness": "Does the class work as described? Are error cases handled? Are type hints correct?",
            "quality": "Is the code clean and well-structured? Is APIError a proper Exception subclass? Are session/connection concerns handled?",
            "documentation": "Does the class have a docstring? Do all public methods have docstrings? Is the usage example runnable?",
        },
    ),
    Challenge(
        name="readme-writer",
        description="Write a README for a CLI tool — tests documentation ability directly",
        prompt=(
            "Write a README.md for a command-line tool called `snapdiff` that compares two directories "
            "and reports added, removed, and changed files. The tool is written in Python, installable via pip. "
            "Include: a one-line description, installation instructions, usage examples with flags "
            "(--ignore-hidden, --output json|text, --depth N), output format explanation, "
            "and a short 'How it works' section. Use proper Markdown formatting."
        ),
        rubric={
            "correctness": "Does the README cover all the required sections? Are the flags documented correctly?",
            "quality": "Is the README well-structured and scannable? Would a new user understand the tool from this alone?",
            "documentation": "Is the Markdown formatting correct? Are code blocks used for commands? Is the writing clear and concise?",
        },
    ),
    Challenge(
        name="refactor",
        description="Refactor messy code and explain each change",
        prompt=(
            "Refactor the following Python function and explain each change you made:\n\n"
            "```python\n"
            "def p(d):\n"
            "    r = []\n"
            "    for i in range(len(d)):\n"
            "        x = d[i]\n"
            "        if x % 2 == 0:\n"
            "            r.append(x * x)\n"
            "        else:\n"
            "            r.append(x * x * x)\n"
            "    return r\n"
            "```\n\n"
            "Requirements: rename everything meaningfully, use a list comprehension or equivalent, "
            "add a docstring, add type hints. Then write a short explanation of each change."
        ),
        rubric={
            "correctness": "Does the refactored function produce the same output as the original?",
            "quality": "Are the names meaningful? Is the list comprehension idiomatic? Is it more readable?",
            "documentation": "Is the docstring clear? Is the explanation of changes clear and specific (not generic)?",
        },
    ),
]

_BY_NAME = {c.name: c for c in CHALLENGES}


def load_challenges(names: list[str] | None) -> list[Challenge]:
    if not names:
        return CHALLENGES
    result = []
    for name in names:
        if name not in _BY_NAME:
            print(f"Warning: unknown challenge '{name}', skipping")
            continue
        result.append(_BY_NAME[name])
    return result
