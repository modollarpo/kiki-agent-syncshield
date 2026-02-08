import { NextSeo, ArticleJsonLd } from 'next-seo';

export function JsonLdLearningHub({
  title,
  description,
  url,
  authorName,
  publishDate,
  imageUrl,
}: {
  title: string;
  description: string;
  url: string;
  authorName: string;
  publishDate: string;
  imageUrl: string;
}) {
  return (
    <>
      <NextSeo
        title={title}
        description={description}
        openGraph={{
          url,
          title,
          description,
          images: [{ url: imageUrl }],
          site_name: 'KIKI Agent™ Learning Hub',
        }}
        twitter={{ cardType: 'summary_large_image' }}
      />
      <ArticleJsonLd
        type="Article"
        url={url}
        title={title}
        images={[imageUrl]}
        datePublished={publishDate}
        authorName={authorName}
        description={description}
        publisherName="KIKI Agent™"
        publisherLogo="https://kikiagent.com/logo.png"
      />
    </>
  );
}
