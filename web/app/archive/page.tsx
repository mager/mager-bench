import type { Metadata } from "next";
import Link from "next/link";
import { Arrow } from "@/components/arrow";
import challenges from "@/data/challenges.json";
export const metadata: Metadata = {
  title: "Historical boards | mager-bench",
  description:
    "Preserved results from the original thirteen-task, LLM-judged benchmark. Separate from Counterexample Lab 1.1.",
};
export default function Archive() {
  return (
    <div className="site-width">
      <header className="page-header">
        <div className="eyebrow">The archive</div>
        <h1>
          Keep the history.
          <br />
          Change the test.
        </h1>
        <p>
          The original suite scored coding submissions from 0 to 10 using an LLM
          judge. Counterexample Lab 1.1 counts exposed faults out of eight.
          These are different measurements.
        </p>
      </header>
      <div className="archive-board">
        <div>
          <div className="eyebrow">Original thirteen-task suite</div>
          <h2>ChatGPT subscription board</h2>
          <p>
            The familiar Astra 9.3 and Sol 9.0 averages live here. Subjects ran
            through Codex CLI with GPT-5.6 Sol as judge. Every original score,
            response, and judge note is preserved.
          </p>
        </div>
        <Link className="text-link" href="/archive/subscription">
          Explore this board
          <Arrow />
        </Link>
      </div>
      <div className="archive-board">
        <div>
          <div className="eyebrow">Earlier API runs</div>
          <h2>Sonnet 5 board</h2>
          <p>
            The earlier board uses a different judge and access method. Its
            results remain separate from both the subscription board and the
            deterministic 1.1 challenge.
          </p>
        </div>
        <Link className="text-link" href="/archive/sonnet-5">
          Explore this board
          <Arrow />
        </Link>
      </div>
      <section className="section" id="challenges">
        <div className="section-heading">
          <div>
            <h2>The original challenges</h2>
            <p>
              FizzBuzz, binary search, and refactor are retired from the active
              suite. All thirteen historical prompts remain available for
              reproduction.
            </p>
          </div>
        </div>
        <ol className="fault-list">
          {challenges.map((challenge, index) => (
            <li key={challenge.name} className="fault-item">
              <span className="fault-number">
                {String(index + 1).padStart(2, "0")}
              </span>
              <div>
                <Link
                  className="text-link"
                  href={`/challenges/${challenge.name}`}
                >
                  {challenge.name}
                  <Arrow />
                </Link>
                <p>{challenge.description}</p>
              </div>
            </li>
          ))}
        </ol>
      </section>
      <div className="archive-teaser">
        <div>
          <h2>The current question: can a model find the bug?</h2>
          <p>Explore the new test and its first repeated calibration runs.</p>
        </div>
        <Link className="button-primary" href="/">
          Counterexample Lab
          <Arrow />
        </Link>
      </div>
    </div>
  );
}
