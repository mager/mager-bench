import { existsSync, mkdirSync, readdirSync, readFileSync, writeFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const web = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const source = path.resolve(web, "../posts");
const destination = path.join(web, "data/posts.json");

// A `vercel --prod` upload from web/ contains the committed export, not ../posts.
// Local/full-repository builds always regenerate it from the Markdown originals.
if (!existsSync(source)) {
  if (!existsSync(destination)) throw new Error("Missing posts source and generated data/posts.json");
  console.log("Using committed data/posts.json (Markdown source is outside this build root)");
  process.exit(0);
}

const posts = [];
const slugs = new Set();
for (const filename of readdirSync(source).filter((name) => name.endsWith(".md")).sort()) {
  const markdown = readFileSync(path.join(source, filename), "utf8").replaceAll("\r\n", "\n");
  const sections = markdown.trim().split(/\n\s*\n/);
  if (sections[1]?.startsWith("Draft ·")) continue;
  const title = /^# ([^\n]+)$/.exec(sections[0])?.[1];
  const publishedAt = /^Published · (\d{4}-\d{2}-\d{2})$/.exec(sections[1])?.[1];
  const match = /^\d{4}-\d{2}-\d{2}-(.+)\.md$/.exec(filename);
  const body = sections.slice(2).join("\n\n");
  if (!title || !publishedAt || !match || !body ||
      !Number.isFinite(Date.parse(publishedAt)) ||
      new Date(publishedAt).toISOString().slice(0, 10) !== publishedAt) {
    throw new Error(`Invalid published post: ${filename}; expected title, Published · YYYY-MM-DD, and body`);
  }
  const slug = match[1].replaceAll(".", "-");
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug) || slugs.has(slug)) {
    throw new Error(`Invalid or duplicate blog slug: ${slug}`);
  }
  slugs.add(slug);
  posts.push({
    slug,
    title,
    publishedAt,
    description: sections[2].replace(/\s+/g, " "),
    readingMinutes: Math.max(1, Math.ceil(body.split(/\s+/).length / 200)),
    sourceUrl: `https://github.com/mager/mager-bench/blob/main/posts/${filename}`,
    body,
  });
}
posts.sort((a, b) => b.publishedAt.localeCompare(a.publishedAt) || a.slug.localeCompare(b.slug));
mkdirSync(path.dirname(destination), { recursive: true });
writeFileSync(destination, JSON.stringify(posts, null, 2) + "\n");
console.log(`Wrote data/posts.json (${posts.length} published post${posts.length === 1 ? "" : "s"})`);
