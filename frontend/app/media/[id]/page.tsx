import Link from "next/link";
import { fetchMedia } from "@/lib/api";

export default async function MediaDetails({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const media = await fetchMedia(id);
  const api = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

  return (
    <main className="mx-auto min-h-screen max-w-4xl p-6 md:p-10">
      <Link href="/" className="text-sm text-blue-600 hover:underline">← Back to search</Link>
      
      <div className="mt-8 flex flex-col md:flex-row gap-8">
        {/* Poster / Details */}
        <div className="flex-none w-full md:w-1/3">
          <div className="aspect-[2/3] w-full rounded-lg bg-zinc-200 overflow-hidden shadow-md">
            {/* We will rely on an img tag for poster */}
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img 
              src={`${api}/thumb/${id}`} 
              alt={media.title}
              className="w-full h-full object-cover"
              onError={(e) => { e.currentTarget.style.display = 'none'; }}
            />
          </div>
        </div>
        
        {/* Info & Player */}
        <div className="flex-1">
          <h1 className="text-4xl font-bold">{media.title}</h1>
          <p className="mt-4 text-lg text-zinc-600 dark:text-zinc-400">{media.description || "No description available"}</p>

          <div className="mt-6 grid grid-cols-2 gap-4 text-sm text-zinc-700 dark:text-zinc-300">
            <div><span className="font-semibold text-black dark:text-white">Year:</span> {media.year ?? "Unknown"}</div>
            <div><span className="font-semibold text-black dark:text-white">Runtime:</span> {media.runtime ? `${media.runtime} min` : "Unknown"}</div>
            <div><span className="font-semibold text-black dark:text-white">Genres:</span> {media.genre.join(", ") || "Unknown"}</div>
            <div><span className="font-semibold text-black dark:text-white">Languages:</span> {media.languages.join(", ") || "Unknown"}</div>
            <div><span className="font-semibold text-black dark:text-white">Qualities:</span> {media.qualities.join(", ") || "Unknown"}</div>
            <div><span className="font-semibold text-black dark:text-white">Versions:</span> {media.versions.join(", ") || "Unknown"}</div>
          </div>
          
          <div className="mt-8">
            <h2 className="text-2xl font-bold mb-4">Watch Now</h2>
            <div className="w-full aspect-video bg-black rounded-xl overflow-hidden shadow-lg">
              <video 
                controls 
                className="w-full h-full"
                poster={`${api}/thumb/${id}`}
              >
                <source src={`${api}/stream/${id}`} type="video/mp4" />
                <source src={`${api}/stream/${id}`} type="video/x-matroska" />
                Your browser does not support the video tag.
              </video>
            </div>
            
            <div className="mt-4 flex gap-4">
              <a 
                href={`${api}/download/${id}`} 
                download
                className="inline-flex items-center justify-center rounded-lg bg-black dark:bg-white text-white dark:text-black px-6 py-3 font-semibold transition-transform hover:scale-105 active:scale-95"
              >
                Download File
              </a>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
