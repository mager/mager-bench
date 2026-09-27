import type { Metadata } from "next";
import Link from "next/link";
import { postDate, posts } from "@/lib/posts";

export const metadata: Metadata = {
  title: "Blog | mager-bench",
  description: "Notes on building mager-bench, testing coding models, and making the benchmark harder.",
  alternates: { canonical: "https://bench.mager.co/blog" },
};

export default function BlogPage() {
  return (
    <div className="px-4 py-10 sm:px-8 md:py-16">
      <div className="mx-auto max-w-3xl">
        <header className="mb-12 border-b border-amber-faint pb-6">
          <h1 className="font-display text-5xl tracking-wide text-amber sm:text-6xl">Blog</h1>
          <p className="mt-3 text-sm leading-relaxed text-fg-dim">
            Notes from building a benchmark that keeps asking more.
          </p>
        </header>
        <div className="space-y-10">
          {posts.map((post) => (
            <article key={post.slug} className="border-b border-amber-faint pb-10">
              <div className="mb-3 flex flex-wrap gap-x-4 gap-y-1 text-xs text-fg-dim">
                <time dateTime={post.publishedAt}>{postDate(post.publishedAt)}</time>
                <span>{post.readingMinutes} min read</span>
              </div>
              <h2 className="max-w-2xl font-display text-3xl leading-tight text-amber-bright sm:text-4xl">
                <Link href={`/blog/${post.slug}`} className="hover:text-amber hover:underline underline-offset-4">
                  {post.title} <span aria-hidden="true">→</span>
                </Link>
              </h2>
              <p className="mt-4 max-w-[68ch] text-sm leading-7 text-fg">{post.description}</p>
            </article>
          ))}
        </div>
      </div>
    </div>
  );
}
