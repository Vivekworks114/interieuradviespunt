export interface BlogPost {
  slug: string;
  title: string;
  date: string;
  excerpt: string;
  content: string;
  featuredImage: string;
}

export interface SitePage {
  slug: string;
  title: string;
  excerpt: string;
  content: string;
  featuredImage: string;
}

export function rewriteContent(html: string): string {
  return (html || '')
    .replace(/https?:\/\/(?:www\.)?interieuradviespunt\.nl\/wp-content\/uploads\//g, '/images/')
    .replace(/https?:\/\/(?:www\.)?interieuradviespunt\.nl\/([a-z0-9\-_/]+)\/?/gi, '/$1/');
}

export function createFallbackPage(slug: string) {
  const title = slug
    .replace(/^beste-/, '')
    .split('-')
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');

  const isProduct = slug.startsWith('beste-');
  const fallbacks = [
    '/images/2023/05/wanddecoratie.jpg',
    '/images/2023/05/meubels.jpg',
    '/images/2023/05/kussen-1024x1016.jpg',
    '/images/2023/05/bloemen.jpg',
  ];
  const hash = slug.split('').reduce((a, c) => a + c.charCodeAt(0), 0);

  return {
    slug,
    title: isProduct ? `Beste ${title}` : title,
    description: `Lees alles over ${title.toLowerCase()} op Interieuradviespunt.nl.`,
    featuredImage: fallbacks[hash % fallbacks.length],
    content: `<p>Op Interieuradviespunt.nl helpen we je de beste keuze te maken voor ${title.toLowerCase()}. We vergelijken producten, delen ervaringen en geven praktische tips zodat je interieur er professioneel en verzorgd uitziet.</p><p>Bekijk regelmatig onze website voor de nieuwste reviews, top 10 lijstjes en interieurtips.</p>`,
  };
}
