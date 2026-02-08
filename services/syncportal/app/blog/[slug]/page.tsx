import { NextSeo } from 'next-seo';
import Link from 'next/link';
import { blogArticles } from '../articles';

export default function BlogDetailPage({ params }: { params: { slug: string } }) {
  const article = blogArticles.find(a => a.slug === params.slug);
  if (!article) return <div className="max-w-2xl mx-auto py-12">Article not found.</div>;
  return (
    <div className="max-w-2xl mx-auto py-12">
      <NextSeo title={article.title} description={article.content.slice(0, 120)} />
      <h1 className="text-3xl font-bold mb-4">{article.title}</h1>
      <div className="text-slate-400 mb-6">By {article.author} • {article.date}</div>
      <div className="prose prose-invert text-lg mb-8 whitespace-pre-line">{article.content}</div>
      <Link href="/blog" className="text-blue-400 hover:underline">← Back to Blog</Link>
    </div>
  );
}
