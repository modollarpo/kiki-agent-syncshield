import { NextSeo } from 'next-seo';
import Link from 'next/link';
import { blogArticles } from './articles';

export default function BlogPage() {
  return (
    <div className="max-w-3xl mx-auto py-12">
      <NextSeo title="KIKI Blog" description="Insights on OaaS, SyncTwin™, and performance marketing." />
      <h1 className="text-3xl font-bold mb-8 text-gradient bg-gradient-to-r from-pink-400 via-fuchsia-500 to-blue-400 bg-clip-text text-transparent">KIKI Blog</h1>
      <ul className="flex flex-col gap-8">
        {blogArticles.map(post => (
          <li key={post.slug} className="bg-zinc-800 rounded-xl p-6 shadow-lg hover:scale-[1.02] transition-transform border border-zinc-700">
            <Link href={`/blog/${post.slug}`} className="text-xl font-semibold hover:underline">
              {post.title}
            </Link>
            <div className="mt-2 text-slate-400 italic">{post.excerpt}</div>
            <div className="mt-4 flex items-center gap-4 text-xs text-slate-500">
              <span>By {post.author}</span>
              <span>{post.readTime} read</span>
              <span>{post.date}</span>
              <Link href="/dashboard" className="ml-auto text-blue-400 hover:underline">Go to Dashboard</Link>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
