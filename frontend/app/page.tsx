import Link from "next/link";
import { fetchRecent, fetchSearch } from "@/lib/api";

export default async function Home({
  searchParams,
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const params = await searchParams;
  const query = params.q?.trim() ?? "";
  const result = query ? await fetchSearch(query) : null;
  const items = result ? result.items : await fetchRecent();
  
  const api = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

  return (
    <main className="mx-auto min-h-screen max-w-7xl p-6 md:p-10">
      <header className="flex flex-col md:flex-row items-center justify-between gap-6 mb-12">
        <div>
          <h1 className="text-4xl font-extrabold tracking-tight">Tgassis</h1>
          <p className="text-zinc-500 mt-1">Telegram Media Search + Streaming Platform</p>
        </div>
        
        <form className="w-full md:max-w-md flex relative" action="/">
          <input
            type="text"
            name="q"
            defaultValue={query}
            placeholder="Search movies, anime, series..."
            className="w-full rounded-full border-2 border-zinc-200 px-6 py-3 pr-12 focus:border-black focus:outline-none dark:border-zinc-800 dark:bg-zinc-900 dark:focus:border-white transition-colors"
          />
          <button 
            className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full hover:bg-zinc-100 dark:hover:bg-zinc-800"
            aria-label="Search"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/></svg>
          </button>
        </form>
      </header>

      <section>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">{query ? `Results for "${query}"` : "Recently Added"}</h2>
          {query && result && <span className="text-sm text-zinc-500">{result.total} results</span>}
        </div>
        
        {items.length === 0 ? (
          <div className="py-20 text-center text-zinc-500">
            No media found. Try a different search term.
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6">
            {items.map((item) => (
              <Link key={item.id} href={`/media/${item.id}`} className="group relative flex flex-col gap-2 rounded-xl transition-transform hover:scale-105">
                <div className="aspect-[2/3] w-full overflow-hidden rounded-xl bg-zinc-200 dark:bg-zinc-800 shadow-sm relative">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img 
                    src={`${api}/thumb/${item.id}`} 
                    alt={item.title}
                    className="h-full w-full object-cover transition-all group-hover:brightness-75"
                    loading="lazy"
                  />
                  {item.qualities.length > 0 && (
                    <div className="absolute top-2 right-2 rounded bg-black/70 px-2 py-1 text-xs font-bold text-white backdrop-blur-sm">
                      {item.qualities[0]}
                    </div>
                  )}
                </div>
                <div>
                  <h3 className="font-bold leading-tight line-clamp-1">{item.title}</h3>
                  <p className="text-xs text-zinc-500">{item.year ?? "Unknown"}</p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
