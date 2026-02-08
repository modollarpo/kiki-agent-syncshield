import { NextSeo } from 'next-seo';
import Link from 'next/link';
import { JsonLdLearningHub } from '../components/seo/JsonLdLearningHub';
import { learningHubGuides } from './guides';

export default function LearningHubPage() {
  return (
    <div className="max-w-3xl mx-auto py-12">
      <NextSeo title="Learning Hub" description="Expert guides on OaaS, SyncTwin™, and enterprise marketing." />
      <h1 className="text-3xl font-bold mb-8 text-gradient bg-gradient-to-r from-blue-400 via-cyan-500 to-green-400 bg-clip-text text-transparent">Learning Hub</h1>
      <ul className="flex flex-col gap-8">
        {learningHubGuides.map(article => (
          <li key={article.slug} className="bg-zinc-800 rounded-xl p-6 shadow-lg hover:scale-[1.02] transition-transform border border-zinc-700">
            <JsonLdLearningHub
              title={article.title}
              description={article.description}
              url={`https://kikiagent.com/learning-hub/${article.slug}`}
              authorName={article.author}
              publishDate={article.publishDate}
              imageUrl={article.imageUrl}
            />
            <Link href={`/learning-hub/${article.slug}`} className="text-xl font-semibold hover:underline">
              {article.title}
            </Link>
            <div className="mt-2 text-slate-400 italic">{article.description}</div>
            <div className="mt-4 flex items-center gap-4 text-xs text-slate-500">
              <span>By {article.author}</span>
              <span>{article.publishDate}</span>
              <Link href="/dashboard" className="ml-auto text-blue-400 hover:underline">Go to Dashboard</Link>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
