export function getVideoEmbedUrl(videoUrl: string): string | null {
  let parsed: URL;
  try {
    parsed = new URL(videoUrl);
  } catch {
    return null;
  }

  const host = parsed.hostname.replace(/^www\.|^m\./, '');

  if (host === 'youtube.com') {
    const id = parsed.searchParams.get('v');
    return id ? `https://www.youtube.com/embed/${id}` : null;
  }

  if (host === 'youtu.be') {
    const id = parsed.pathname.slice(1);
    return id ? `https://www.youtube.com/embed/${id}` : null;
  }

  if (host === 'vimeo.com') {
    const id = parsed.pathname.split('/').filter(Boolean)[0];
    return id ? `https://player.vimeo.com/video/${id}` : null;
  }

  if (host === 'tv.naver.com') {
    const parts = parsed.pathname.split('/').filter(Boolean);
    const id = parts[parts.length - 1];
    return id ? `https://tv.naver.com/embed/${id}` : null;
  }

  return null;
}
