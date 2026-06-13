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
  const recent = await fetchRecent();

  return (
    <main className="mx-auto min-h-screen max-w-6xl p-6 text-sm md:p-10">
      <h1 className="text-3xl font-bold">Telegram Media Search</h1>
      <p className="mt-2 text-zinc-500">Fast personal media server powered by Telegram storage.</p>

      <form className="mt-6 flex gap-2" action="/">
        <input
          type="text"
          name="q"
          defaultValue={query}
          placeholder="Search movies, anime, series..."
          className="w-full rounded border border-zinc-300 px-3 py-2"
        />
        <button className="rounded bg-black px-4 py-2 text-white">Search</button>
      </form>

      <section className="mt-8">
        <h2 className="text-xl font-semibold">{query ? `Results for "${query}"` : "Recently Added"}</h2>
        <div className="mt-4 grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {(result?.items ?? recent).map((item) => (
            <Link key={item.id} href={`/media/${item.id}`} className="rounded border border-zinc-200 p-4 hover:bg-zinc-50">
              <h3 className="font-semibold">{item.title}</h3>
              <p className="mt-1 text-zinc-500">{item.year ?? "Unknown year"}</p>
              <p className="mt-2">Languages: {item.languages.join(", ") || "Unknown"}</p>
              <p>Qualities: {item.qualities.join(", ") || "Unknown"}</p>
            </Link>
          ))}
        </div>
      </section>
    </main>
  );
}
