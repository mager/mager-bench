import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import Markdown, { defaultUrlTransform } from "react-markdown";
import { postDate, posts } from "@/lib/posts";

type Props = { params: Promise<{ slug: string }> };

export const dynamicParams = false;

export function generateStaticParams() {
  return posts.map((post) => ({ slug: post.slug }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { slug } = await params;
  const post = posts.find((entry) => entry.slug === slug);
  if (!post) notFound();
  const url = `https://bench.mager.co/blog/${post.slug}`;
  return {
    title: `${post.title} | mager-bench`,
    description: post.description,
    alternates: { canonical: url },
    openGraph: {
      type: "article",
      title: post.title,
      description: post.description,
      url,
      publishedTime: post.publishedAt,
      siteName: "mager-bench",
    },
    twitter: { card: "summary", title: post.title, description: post.description },
  };
}

export default async function BlogPostPage({ params }: Props) {
  const { slug } = await params;
  const post = posts.find((entry) => entry.slug === slug);
  if (!post) notFound();

  return (
    <div className="px-4 py-10 sm:px-8 md:py-16">
      <article className="mx-auto max-w-[68ch]">
        <header className="mb-9 border-b border-amber-faint pb-7">
          <Link href="/blog" className="text-xs text-fg-dim hover:text-amber-bright">
            ← all posts
          </Link>
          <h1 className="mt-6 font-display text-4xl leading-[1.08] text-amber-bright sm:text-5xl">
            {post.title}
          </h1>
          <div className="mt-5 flex flex-wrap gap-x-4 gap-y-1 text-xs text-fg-dim">
            <time dateTime={post.publishedAt}>{postDate(post.publishedAt)}</time>
            <span>{post.readingMinutes} min read</span>
          </div>
        </header>
        <div className="space-y-6 text-[15px] leading-[1.9] text-fg sm:text-base">
          <Markdown
            urlTransform={(url) => {
              const safe = defaultUrlTransform(url);
              return /^\.{1,2}\//.test(safe) ? new URL(safe, post.sourceUrl).href : safe;
            }}
            components={{
              a: ({ href, children }) => (
                <a href={href} className="text-amber underline decoration-amber-faint underline-offset-4 hover:text-amber-bright hover:decoration-amber">
                  {children}
                </a>
              ),
              strong: ({ children }) => <strong className="font-semibold text-amber-bright">{children}</strong>,
            }}
          >
            {post.body}
          </Markdown>
        </div>
        <footer className="mt-12 flex flex-wrap gap-x-6 gap-y-3 border-t border-amber-faint pt-5 text-xs">
          <Link href="/" className="text-amber hover:text-amber-bright">← back to the leaderboard</Link>
          <a href={post.sourceUrl} className="text-fg-dim hover:text-amber-bright">read the Markdown source →</a>
        </footer>
      </article>
    </div>
  );
}
