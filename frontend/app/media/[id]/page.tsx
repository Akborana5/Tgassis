import Link from "next/link";
import { fetchMedia } from "@/lib/api";

export default async function MediaDetails({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const media = await fetchMedia(id);
  const api = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

  return (
    <main className="mx-auto min-h-screen max-w-4xl p-6 md:p-10">
      <Link href="/" className="text-sm text-blue-600">← Back to search</Link>
      <h1 className="mt-4 text-3xl font-bold">{media.title}</h1>
      <p className="mt-2 text-zinc-500">{media.description || "No description available"}</p>

      <div className="mt-6 grid gap-2 text-sm">
        <p><strong>Year:</strong> {media.year ?? "Unknown"}</p>
        <p><strong>Genres:</strong> {media.genre.join(", ") || "Unknown"}</p>
        <p><strong>Languages:</strong> {media.languages.join(", ") || "Unknown"}</p>
        <p><strong>Qualities:</strong> {media.qualities.join(", ") || "Unknown"}</p>
        <p><strong>Versions:</strong> {media.versions.join(", ") || "Unknown"}</p>
        <p><strong>Runtime:</strong> {media.runtime ? `${media.runtime} min` : "Unknown"}</p>
      </div>

      <div className="mt-8 flex flex-wrap gap-3">
        <a href={`${api}/stream/${id}`} className="rounded bg-black px-4 py-2 text-white">Watch Now</a>
        <a href={`${api}/download/${id}`} className="rounded border border-black px-4 py-2">Download</a>
      </div>
    </main>
  );
}
