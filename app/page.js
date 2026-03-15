export default function Home() {
  return (
    <main className="min-h-screen bg-black text-white">
      
      {/* Header */}
      <header className="border-b border-gray-800 px-6 py-4">
        <h1 className="text-2xl font-bold text-orange-500">AI Pulse</h1>
        <p className="text-gray-400 text-sm">Latest AI updates, curated daily</p>
      </header>

      {/* Hero */}
      <section className="px-6 py-16 text-center">
        <h2 className="text-5xl font-bold mb-4">Stay Ahead of AI</h2>
        <p className="text-gray-400 text-lg">
          Trusted updates from Anthropic, OpenAI, Google DeepMind and more.
        </p>
      </section>

      {/* Posts */}
      <section className="px-6 py-8 max-w-4xl mx-auto">
        <h3 className="text-xl font-semibold mb-6 text-orange-500">Latest Updates</h3>
        <div className="grid gap-6">
          <div className="border border-gray-800 rounded-lg p-6 hover:border-orange-500 transition">
            <span className="text-xs text-orange-500 uppercase">Anthropic</span>
            <h4 className="text-lg font-semibold mt-1">Post title will appear here</h4>
            <p className="text-gray-400 text-sm mt-2">Summary will appear here once our AI agent starts fetching updates...</p>
            <span className="text-xs text-gray-600 mt-3 block">March 15, 2026</span>
          </div>
        </div>
      </section>

    </main>
  )
}