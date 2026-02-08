import { NextSeo } from 'next-seo';
import Link from 'next/link';
import { learningHubGuides } from '../guides';

export default function LearningHubDetailPage({ params }: { params: { slug: string } }) {
  const guide = learningHubGuides.find(g => g.slug === params.slug);
  if (!guide) return <div className="max-w-2xl mx-auto py-12">Guide not found.</div>;
  return (
    <div className="max-w-2xl mx-auto py-12">
      <NextSeo title={guide.title} description={guide.content.slice(0, 120)} />
      <h1 className="text-3xl font-bold mb-4">{guide.title}</h1>
      <div className="text-slate-400 mb-6">By {guide.author} • {guide.publishDate}</div>
      <div className="prose prose-invert text-lg mb-8 whitespace-pre-line">{guide.content}</div>
      <Link href="/learning-hub" className="text-blue-400 hover:underline">← Back to Learning Hub</Link>
    </div>
  );
}
