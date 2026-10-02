import results from "@/data/results.json";
import challenges from "@/data/challenges.json";
import { lab } from "@/lib/counterexample";
import { modelHref, modelSlug } from "@/lib/model-path";

export const originalBoard = results;
export const challengeNotes: Record<
  string,
  { title: string; group: string; question: string; explains: string }
> = {
  fizzbuzz: {
    title: "FizzBuzz",
    group: "Warm-ups",
    question: "Can it get the basics right?",
    explains:
      "Generate the right output for multiples of 3 and 5, including their overlap. Small enough that correctness and clarity should both be easy.",
  },
  "binary-search": {
    title: "Binary search",
    group: "Warm-ups",
    question: "Does the algorithm survive the edges?",
    explains:
      "Find a value in a sorted list, return -1 when absent, and explain the search. Empty lists and boundary indices test precision.",
  },
  refactor: {
    title: "Refactor",
    group: "Warm-ups",
    question: "Can it improve code without changing its behavior?",
    explains:
      "Turn a messy loop into clearly named, typed, documented Python and explain each change.",
  },
  "api-client": {
    title: "API client",
    group: "Build",
    question: "Can it build an interface someone else can use?",
    explains:
      "Wrap HTTP GET and POST with authentication, useful exceptions, type hints, documentation, and a working example.",
  },
  "readme-writer": {
    title: "README writer",
    group: "Docs",
    question: "Can it explain a tool well enough to use it?",
    explains:
      "Document a directory comparison CLI: installation, flags, realistic examples, output formats, and how it works.",
  },
  "test-writing": {
    title: "Python tests",
    group: "Test & debug",
    question: "Does it test beyond the happy path?",
    explains:
      "Write parameterized pytest cases for a duration parser, including invalid input and edge cases with precise assertions.",
  },
  debug: {
    title: "Debugging",
    group: "Test & debug",
    question: "Can it diagnose the actual failure?",
    explains:
      "Repair a word-frequency function against the supplied examples, explain the bugs, and preserve frequency and alphabetical ordering.",
  },
  "async-fetch": {
    title: "Async fetch",
    group: "Build",
    question: "What happens when the network misbehaves?",
    explains:
      "Fetch URLs concurrently with per-request timeouts, retries, exponential backoff, and useful results even when requests fail.",
  },
  sql: {
    title: "SQL analysis",
    group: "Build",
    question: "Can it keep a complicated query correct?",
    explains:
      "Aggregate revenue by country, find each top customer with deterministic tie-breaking, and calculate shares of global revenue.",
  },
  "go-test": {
    title: "Go tests",
    group: "Test & debug",
    question: "Does it know how Go developers actually test?",
    explains:
      "Use table-driven subtests, exact map comparisons, at least six cases, and a benchmark for a word-count function.",
  },
  "elixir-test": {
    title: "Elixir tests",
    group: "Test & debug",
    question: "Can it handle another language’s conventions?",
    explains:
      "Write organized ExUnit tests for string truncation, covering boundaries, custom suffixes, errors, and Unicode.",
  },
  doom: {
    title: "Doom raycaster",
    group: "Build",
    question: "Can it ship a whole interactive system?",
    explains:
      "Build a first-person raycasting engine in one HTML file, with generated textures, perspective correction, movement, and the full supplied spec.",
  },
  slots: {
    title: "Slot machine",
    group: "Build",
    question: "Do the visuals and the state agree?",
    explains:
      "Build a playable three-reel game in one HTML file. Animation, payouts, betting, credits, and interaction all have to work together.",
  },
};

const modelIds = [
  ...new Set([
    ...results.models.map((model) => model.id),
    ...lab.models.map((model) => model.id),
  ]),
];

export const roster = modelIds.map((id, index) => {
  const original = results.models.find((model) => model.id === id);
  const calibration = lab.models.find((model) => model.id === id);
  return {
    id,
    name: original?.name ?? calibration!.name,
    original,
    challenges: original?.challenges ?? [],
    number: String(index + 1).padStart(2, "0"),
    slug: modelSlug(id),
    href: modelHref(id),
    calibration,
  };
});

export type CourtChallenge = {
  id: string;
  title: string;
  group: string;
  question: string;
  explains: string;
  href: string;
  retired: boolean;
  lab: boolean;
  scores: { model: string; label: string; unit: string; href: string }[];
};
export const courtChallenges: CourtChallenge[] = [
  ...challenges.map((challenge) => ({
    id: challenge.name,
    ...challengeNotes[challenge.name],
    href: `/challenges/${challenge.name}`,
    retired: ["fizzbuzz", "binary-search", "refactor"].includes(challenge.name),
    lab: false,
    scores: roster.map((model) => ({
      model: model.name,
      label:
        model.challenges
          .find((c) => c.name === challenge.name)
          ?.total.toFixed(1) ?? "—",
      unit: model.original ? "/10" : "not run",
      href: model.original
        ? modelHref(model.id, challenge.name)
        : `${model.href}#original`,
    })),
  })),
  {
    id: "counterexample-ledger",
    title: "Counterexample Lab",
    group: "Test & debug",
    question: "Can it design tests that expose broken code?",
    explains:
      "Write exact expectations for a tiny money-transfer ledger. Twelve events must expose as many of eight deliberately faulty implementations as possible.",
    href: "/challenges/counterexample-ledger",
    retired: false,
    lab: true,
    scores: roster.map((model) => ({
      model: model.name,
      label: model.calibration?.scores.join(" · ") ?? "—",
      unit: model.calibration?.failed
        ? `out of 8 · ${model.calibration.failed} unscored`
        : "out of 8, each run",
      href: `${model.href}#counterexample`,
    })),
  },
];
