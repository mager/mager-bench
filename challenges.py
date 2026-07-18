"""Benchmark challenges — each is a coding task sent verbatim to each model."""

from __future__ import annotations

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
    Challenge(
        name="test-writing",
        description="Write pytest tests for a provided function — tests edge-case thinking and assertion quality",
        prompt=(
            "Write a comprehensive pytest test suite for the following Python function:\n\n"
            "```python\n"
            "def parse_duration(s: str) -> int:\n"
            "    \"\"\"Parse a human duration string into total seconds.\n\n"
            "    Accepted formats: '1h', '30m', '45s', '1h30m', '2h15m30s'.\n"
            "    Raises ValueError on unrecognized input.\n"
            "    \"\"\"\n"
            "    import re\n"
            "    pattern = r'^(?:(\\d+)h)?(?:(\\d+)m)?(?:(\\d+)s)?$'\n"
            "    m = re.fullmatch(pattern, s.strip())\n"
            "    if not m or not s.strip():\n"
            "        raise ValueError(f'Invalid duration: {s!r}')\n"
            "    h, mi, sec = (int(x) if x else 0 for x in m.groups())\n"
            "    return h * 3600 + mi * 60 + sec\n"
            "```\n\n"
            "Requirements:\n"
            "- Use pytest (plain functions, no unittest classes)\n"
            "- Use `@pytest.mark.parametrize` for the happy-path cases\n"
            "- Cover at least 3 edge/error cases with `pytest.raises`\n"
            "- Name tests descriptively so failures are self-explaining\n"
            "- No mocking needed — the function is pure\n"
            "- Do not reimplement the function; test it as a black box\n"
        ),
        rubric={
            "correctness": (
                "Do the parametrized cases cover all documented formats (h, m, s, hm, hms, ms)? "
                "Are the expected values arithmetically correct? Do error cases actually trigger ValueError?"
            ),
            "quality": (
                "Is parametrize used instead of copy-paste test functions? "
                "Are test names descriptive? Are assertions tight (not just 'assert result')? "
                "Is there any unnecessary complexity?"
            ),
            "documentation": (
                "Do test names read like specs ('test_hours_only', 'test_invalid_raises')? "
                "Are fixture/parametrize IDs meaningful? Any comments where the tested behavior is non-obvious?"
            ),
        },
    ),
    Challenge(
        name="debug",
        description="Find and fix 3 bugs in broken Python code — tests careful reading and correctness reasoning",
        prompt=(
            "The following Python function is supposed to return the top-N most frequent words "
            "in a string, sorted by frequency descending and alphabetically for ties. "
            "It has exactly 3 bugs. Find each bug, explain what it does wrong, fix it, and show the corrected function.\n\n"
            "```python\n"
            "from collections import Counter\n\n"
            "def top_words(text: str, n: int = 10) -> list[str]:\n"
            "    words = text.lower().split()\n"
            "    words = [w.strip('.,!?;:\\'\"') for w in words]\n"
            "    counts = Counter(words)\n"
            "    ranked = sorted(counts.items(), key=lambda x: (-x[1], x[0]))\n"
            "    return [word for word, count in ranked[:n] if count > 1]\n"
            "```\n\n"
            "Test cases that expose the bugs:\n"
            "- `top_words('the cat sat on the mat the', 3)` should return `['the', 'cat', 'mat']`\n"
            "  (3 most frequent; cat/mat/sat tie at 1 occurrence — alphabetical breaks the tie)\n"
            "- `top_words('a a b b c', 2)` should return `['a', 'b']`\n"
            "- `top_words('hello world', 5)` should return `['hello', 'world']`\n\n"
            "For each bug: (1) quote the buggy line, (2) explain what it does wrong, (3) show the fix."
        ),
        rubric={
            "correctness": (
                "Is the `count > 1` filter identified as a bug (drops valid hapax words)? "
                "Is the empty-string entry problem identified (stripping punctuation-only tokens creates '' in counter)? "
                "Is a third genuine defect found (e.g. no deduplication of empty strings, or missing n=0 guard)? "
                "Does the corrected function pass all three test cases?"
            ),
            "quality": (
                "Are fixes minimal (not a full rewrite)? "
                "Does the model explain WHY each line is wrong, not just show a diff? "
                "Is the corrected function clean Python?"
            ),
            "documentation": (
                "Is each bug explained clearly enough that a junior dev would understand? "
                "Are code quotes used to anchor each explanation? "
                "Is the structure (bug → explanation → fix) followed for each of the 3?"
            ),
        },
    ),
    Challenge(
        name="async-fetch",
        description="Write async Python for concurrent HTTP fetching with timeout and retry",
        prompt=(
            "Write a Python async function `fetch_all(urls: list[str], timeout: float = 5.0, retries: int = 2) -> list[dict]` "
            "that fetches all URLs concurrently using `aiohttp` and returns a list of result dicts.\n\n"
            "Each result dict must have:\n"
            "  - `url`: the original URL\n"
            "  - `status`: HTTP status code (int), or None on error\n"
            "  - `body`: response text (str), or None on error\n"
            "  - `error`: error message string, or None on success\n\n"
            "Requirements:\n"
            "1. All URLs must be fetched concurrently (not sequentially)\n"
            "2. Each fetch must respect the `timeout` (per-request, not total)\n"
            "3. Retry up to `retries` times on network errors or 5xx responses (exponential backoff: 0.5s, 1s, ...)\n"
            "4. Never raise — errors go into the result dict\n"
            "5. Type-hint everything; add a docstring\n"
            "6. Show a `__main__` block that fetches 3 URLs and prints results\n"
        ),
        rubric={
            "correctness": (
                "Is `asyncio.gather` (or equivalent) used for actual concurrency? "
                "Is timeout applied per-request via `aiohttp.ClientTimeout`? "
                "Does retry logic actually retry on 5xx and network errors (not just any exception)? "
                "Is exponential backoff implemented (not fixed sleep)? "
                "Does the function never raise on individual URL errors?"
            ),
            "quality": (
                "Is the session created once (not per-request)? "
                "Is the retry loop clean (not deeply nested)? "
                "Are asyncio patterns idiomatic (async with, await)? "
                "Is the main block runnable with `asyncio.run`?"
            ),
            "documentation": (
                "Does the docstring explain all parameters including units (timeout in seconds)? "
                "Are result dict keys documented? "
                "Is the backoff behavior described?"
            ),
        },
    ),
    Challenge(
        name="sql",
        description="Write a complex SQL query with CTEs, window functions, and aggregations",
        prompt=(
            "Write a single SQL query (PostgreSQL dialect) against the following schema:\n\n"
            "```sql\n"
            "CREATE TABLE orders (\n"
            "  id          SERIAL PRIMARY KEY,\n"
            "  customer_id INTEGER NOT NULL,\n"
            "  product_id  INTEGER NOT NULL,\n"
            "  amount      NUMERIC(10,2) NOT NULL,\n"
            "  created_at  TIMESTAMPTZ NOT NULL\n"
            ");\n\n"
            "CREATE TABLE customers (\n"
            "  id      SERIAL PRIMARY KEY,\n"
            "  name    TEXT NOT NULL,\n"
            "  country TEXT NOT NULL\n"
            ");\n"
            "```\n\n"
            "The query must return, for each country:\n"
            "1. `country` — the country name\n"
            "2. `total_revenue` — sum of all order amounts\n"
            "3. `order_count` — total number of orders\n"
            "4. `avg_order_value` — average order amount, rounded to 2 decimal places\n"
            "5. `top_customer` — the name of the customer with the highest total spend in that country\n"
            "   (break ties by customer name ascending)\n"
            "6. `revenue_pct` — this country's share of global revenue, as a percentage rounded to 1 decimal place\n\n"
            "Requirements:\n"
            "- Use at least one CTE\n"
            "- Use a window function for `revenue_pct`\n"
            "- Order results by `total_revenue` descending\n"
            "- Add a comment above each CTE explaining what it computes\n"
        ),
        rubric={
            "correctness": (
                "Is revenue per country summed correctly via JOIN + GROUP BY? "
                "Is `top_customer` correctly found using DISTINCT ON, ROW_NUMBER(), or a correlated subquery? "
                "Is `revenue_pct` computed with a window function (SUM(...) OVER ()) rather than a scalar subquery? "
                "Is rounding applied correctly (2dp for avg, 1dp for pct)?"
            ),
            "quality": (
                "Is the query readable — CTEs named clearly, columns aliased cleanly? "
                "Is there a single final SELECT rather than redundant nesting? "
                "Are aggregate functions used correctly?"
            ),
            "documentation": (
                "Does each CTE have a comment explaining what it computes? "
                "Are column aliases self-explanatory? "
                "Is the overall query structure easy to follow top-to-bottom?"
            ),
        },
    ),
    Challenge(
        name="go-test",
        description="Write idiomatic Go table-driven tests — tests knowledge of Go testing conventions",
        prompt=(
            "Write a Go test file for the following function:\n\n"
            "```go\n"
            "// WordCount returns a map of each unique word in s to the number\n"
            "// of times it appears. Words are case-insensitive and separated by\n"
            "// whitespace. Punctuation attached to words is stripped.\n"
            "func WordCount(s string) map[string]int\n"
            "```\n\n"
            "Requirements:\n"
            "- Package: `wordcount` (test file: `wordcount_test.go`)\n"
            "- Use Go's standard `testing` package — no third-party libraries\n"
            "- Use a table-driven test with a `[]struct{ name, input string; want map[string]int }` slice\n"
            "- Include at least 6 test cases: empty string, single word, mixed case, punctuation, "
            "repeated words, multi-word sentence\n"
            "- Use `t.Run(tc.name, ...)` for subtests so failures are identifiable\n"
            "- Use `reflect.DeepEqual` or `maps.Equal` to compare maps\n"
            "- Add a benchmark `BenchmarkWordCount` that runs on a realistic sentence\n"
        ),
        rubric={
            "correctness": (
                "Do the 6+ test cases cover empty input, case-insensitivity, punctuation stripping, "
                "and repeated words with correct expected counts? "
                "Is the map comparison correct (not == on maps)? "
                "Does the benchmark compile and follow Go benchmark conventions (b.N loop)?"
            ),
            "quality": (
                "Is the table-driven pattern used correctly (slice of structs, not parallel variables)? "
                "Are subtests used with t.Run? "
                "Is the test file in the right package (wordcount or wordcount_test)? "
                "Is the code idiomatic Go (no unnecessary imports, proper error handling)?"
            ),
            "documentation": (
                "Are test case names descriptive ('empty string', 'mixed case punctuation')? "
                "Is there a comment on the test function explaining what it covers? "
                "Is the benchmark named and commented correctly?"
            ),
        },
    ),
    Challenge(
        name="elixir-test",
        description="Write idiomatic Elixir ExUnit tests — tests knowledge of Elixir testing conventions",
        prompt=(
            "Write an ExUnit test module for the following Elixir function:\n\n"
            "```elixir\n"
            "defmodule StringUtils do\n"
            "  @doc \"\"\"\n"
            "  Truncates a string to at most `max_len` characters.\n"
            "  If truncated, appends `suffix` (default: \"...\").\n"
            "  Returns the original string if it is already within `max_len`.\n"
            "  Raises ArgumentError if max_len is negative.\n"
            "  \"\"\"\n"
            "  @spec truncate(String.t(), non_neg_integer(), String.t()) :: String.t()\n"
            "  def truncate(str, max_len, suffix \\\\ \"...\")\n"
            "end\n"
            "```\n\n"
            "Requirements:\n"
            "- Module name: `StringUtilsTest`, `use ExUnit.Case`\n"
            "- Use `describe` blocks to group related cases\n"
            "- At least 2 `describe` blocks: one for happy path, one for edge/error cases\n"
            "- At least 8 test cases total covering: string shorter than limit, exact length, "
            "longer string (suffix appended), empty string, custom suffix, max_len of 0, "
            "negative max_len (should raise), unicode string\n"
            "- Use `assert`, `assert_raise`, and pattern matching appropriately\n"
            "- Add at least one doctest-style `## Examples` in a module comment showing usage\n"
        ),
        rubric={
            "correctness": (
                "Do the 8+ tests cover all specified cases with correct expected values? "
                "Does `assert_raise ArgumentError` correctly test the negative max_len case? "
                "Are unicode string lengths handled via `String.length/1`, not `byte_size/1`?"
            ),
            "quality": (
                "Are `describe` blocks used to group related tests logically? "
                "Are test names written as plain English specs ('truncates when string exceeds limit')? "
                "Is pattern matching used where it adds clarity (e.g. matching on {:ok, _} if the API returns tuples)? "
                "Is the module correctly structured with `use ExUnit.Case`?"
            ),
            "documentation": (
                "Are describe block labels and test names readable as a spec? "
                "Is the module-level Examples comment present and accurate? "
                "Does the overall file read like idiomatic Elixir test documentation?"
            ),
        },
    ),
    Challenge(
        name="doom",
        description="Build a Doom-style raycasting FPS engine in a single HTML file — the mager-bench signature challenge",
        prompt=(
            "Implement a first-person 3D raycasting engine in a single self-contained HTML file "
            "with no external libraries, no external images, and no CDN scripts. "
            "This is the hardest challenge in the benchmark. Partial credit is given per requirement met.\n\n"

            "## Rendering\n"
            "- DDA (Digital Differential Analysis) raycasting — not a simplified ray-box approximation\n"
            "- Fish-eye correction applied to all wall distances\n"
            "- **Procedurally generated wall textures** using canvas math only (no image files, no data URIs): "
            "at least 3 distinct texture patterns (e.g. checkerboard, brick, stripe) assigned to different wall types in the map\n"
            "- Perspective-correct texture mapping onto wall columns\n"
            "- Distance-based shading: walls darken smoothly as they recede (multiply shade by 1/distance, clamped)\n"
            "- Ceiling rendered as a flat dark color; floor as a slightly lighter flat color\n"
            "- Target: 60fps at 640×480 internal resolution scaled to fill the browser window\n\n"

            "## Map\n"
            "- Hard-coded map of at least 16×16 cells encoded as a 2D array\n"
            "- Non-trivial layout: at least 3 distinct rooms connected by corridors, one dead end, one secret area\n"
            "- At least 3 wall types (mapped to the 3 texture patterns)\n"
            "- One door cell (wall type 4) that opens when the player is within 1.5 cells and presses E; "
            "opened doors become passable and render as open archways\n"
            "- One exit cell — reaching it displays a 'LEVEL COMPLETE — [MM:SS]' overlay\n"
            "- Player spawn position defined in the map; facing toward the first corridor\n\n"

            "## Player\n"
            "- WASD movement with smooth speed (moveSpeed: 3 cells/sec, rotSpeed: 2 rad/sec)\n"
            "- Mouse-look for horizontal rotation using the Pointer Lock API (click canvas to lock)\n"
            "- Collision detection: AABB against all solid walls (player radius: 0.2 cells)\n"
            "- Field of view: 66 degrees\n\n"

            "## Z-buffer\n"
            "- Maintain a per-column Z-buffer (array of wall distances) for correct depth ordering\n"
            "- Use it to clip any future sprite/overlay rendering to avoid drawing behind walls\n\n"

            "## HUD\n"
            "- Minimap in top-left corner: draw map cells as colored squares, player as a dot with a "
            "direction arrow; scale: 6px per cell\n"
            "- FPS counter (rolling average over last 30 frames) in top-right corner\n"
            "- 'Press E to open door' hint rendered in the center-bottom when a door is within 1.5 cells\n\n"

            "## Code quality\n"
            "- Single HTML file, all JS inline in <script> tags, all CSS inline in <style>\n"
            "- requestAnimationFrame game loop with delta-time movement\n"
            "- Organized into clearly named functions: initMap(), castRay(), drawWallColumn(), "
            "drawHUD(), drawMinimap(), gameLoop(), handleInput()\n"
            "- No god-object — game state in a plain JS object, renderer functions take state as argument\n\n"

            "Scoring: the judge scores each major section (rendering, map, player, HUD, code) independently. "
            "A beautiful but mathematically wrong perspective loses on correctness. "
            "A correct raycaster with unreadable code loses on quality. "
            "Both must be right to score above 8."
        ),
        rubric={
            "correctness": (
                "Does the raycaster use real DDA with fish-eye correction? "
                "Are wall textures perspective-correct (texture column selected based on exact hit position)? "
                "Is distance shading applied (not just flat colors)? "
                "Does the door open on E and become passable? "
                "Does collision detection prevent wall clipping? "
                "Does reaching the exit show the LEVEL COMPLETE overlay with time? "
                "Is the Z-buffer maintained per column? "
            ),
            "quality": (
                "Is the game loop delta-time based (not frame-count based)? "
                "Does mouse look use Pointer Lock API correctly? "
                "Is the code organized into the named functions (initMap, castRay, drawWallColumn, drawHUD, etc.)? "
                "Is game state a plain JS object rather than scattered globals? "
                "Does the minimap show player position + direction correctly? "
                "Does the FPS counter use a rolling average? "
                "Is movement smooth (no jitter, correct WASD diagonals)?"
            ),
            "documentation": (
                "Are the named functions present and clearly scoped? "
                "Are magic numbers (FOV, moveSpeed, rotSpeed, minimap scale) named as constants? "
                "Is the map array readable — can you see the room layout by looking at the array? "
                "Are the three texture types distinguishable in code (not just wall type 1/2/3 with no explanation)?"
            ),
        },
    ),
    Challenge(
        name="slots",
        description="Build a Vegas-style slot machine in a single HTML file — reels, pay table, betting, wins",
        prompt=(
            "Build a fully playable Vegas-style slot machine in a single self-contained HTML file "
            "with no external libraries and no external assets.\n\n"

            "## Reels\n"
            "- 3 reels, each with these 7 symbols (use emoji or Unicode): "
            "🍒 Cherry, 🍋 Lemon, 🍊 Orange, 🍇 Grape, 🔔 Bell, ⭐ Star, 7️⃣ Seven\n"
            "- Spin animation: each reel spins independently for a randomized duration "
            "(reel 1 stops first ~800ms, reel 2 ~1200ms, reel 3 ~1600ms), "
            "showing symbols scrolling upward at ~12 symbols/sec before snapping to the result\n"
            "- While spinning, the SPIN button is disabled\n\n"

            "## Pay table (multipliers applied to the current bet)\n"
            "- 7️⃣ 7️⃣ 7️⃣ → 100×\n"
            "- ⭐ ⭐ ⭐ → 50×\n"
            "- 🔔 🔔 🔔 → 20×\n"
            "- 🍇 🍇 🍇 → 15×\n"
            "- 🍊 🍊 🍊 → 10×\n"
            "- 🍋 🍋 🍋 → 5×\n"
            "- 🍒 🍒 🍒 → 3×\n"
            "- Any two 🍒 🍒 (in the first two positions) → 2×\n"
            "- All other outcomes → 0× (loss)\n\n"

            "## Betting & credits\n"
            "- Player starts with 100 credits\n"
            "- Bet buttons: 1, 5, 10 credits (highlighted active bet; default: 1)\n"
            "- Spinning deducts the bet immediately; winning adds bet × multiplier\n"
            "- If credits reach 0 and player has no bet they can cover: show 'GAME OVER' with a 'Play Again' button that resets to 100 credits\n\n"

            "## Win feedback\n"
            "- On a win: flash the matching symbols (CSS animation), show '+[amount] credits' in gold text, "
            "display the winning combination name ('JACKPOT!', 'THREE BELLS', etc.) above the reels\n"
            "- On a loss: brief shake animation on the reels (CSS transform)\n"
            "- Credit balance updates after each spin with a count-up animation (increment from old to new value over 400ms)\n\n"

            "## Pay table display\n"
            "- Render the pay table as a visible panel on the page (not a modal) listing all combinations and their multipliers\n"
            "- Highlight the winning row in the pay table when that combination hits\n\n"

            "## Code quality\n"
            "- Single HTML file; all JS in <script>, all CSS in <style>\n"
            "- Game state in a plain JS object: { credits, bet, spinning, reels, result }\n"
            "- Named functions: initState(), spin(), checkWin(), animateReels(), updateUI()\n"
            "- RNG must use Math.random() — no seeding, no external library\n"
            "- No inline onclick= handlers; use addEventListener throughout\n"
        ),
        rubric={
            "correctness": (
                "Do all 8 pay table combinations pay the correct multiplier (including the any-two-cherries case)? "
                "Is the bet deducted before the spin result is known? "
                "Does the GAME OVER condition trigger correctly at 0 credits? "
                "Does the reel animation stop in the right order (reel 1 first, reel 3 last)? "
                "Does the credit count-up animation run from old to new value?"
            ),
            "quality": (
                "Is spinning state tracked so the SPIN button is disabled during animation? "
                "Is game state a plain JS object (not scattered globals)? "
                "Are the 5 named functions present and doing what they're named for? "
                "Does the win feedback (flash, shake, win name) appear correctly? "
                "Is the pay table panel visible on the page and does it highlight the winning row?"
            ),
            "documentation": (
                "Are the named functions present with clear scope? "
                "Are pay table multipliers defined as named constants (not magic numbers inline)? "
                "Is the game state object documented or self-describing? "
                "Are the reel timing constants named (not bare 800/1200/1600 ms literals)?"
            ),
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
