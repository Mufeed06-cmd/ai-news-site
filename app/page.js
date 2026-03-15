import { supabase } from './supabase'

export default async function Home() {
  const { data: posts } = await supabase
    .from('posts')
    .select('*')
    .eq('status', 'published')
    .order('created_at', { ascending: false })

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
        
        {posts && posts.length > 0 ? (
          <div className="grid gap-6">
            {posts.map((post) => (
              <div key={post.id} className="border border-gray-800 rounded-lg p-6 hover:border-orange-500 transition">
                <span className="text-xs text-orange-500 uppercase">{post.source}</span>
                <h4 className="text-lg font-semibold mt-1">{post.title}</h4>
                <p className="text-gray-400 text-sm mt-2">{post.summary}</p>
                <div className="flex justify-between items-center mt-3">
                  <span className="text-xs text-gray-600">
                    {new Date(post.created_at).toLocaleDateString()}
                  </span>
                  <a href={post.source_url} target="_blank" 
                     className="text-xs text-orange-500 hover:underline">
                    Read original →
                  </a>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="border border-gray-800 rounded-lg p-6 text-center">
            <p className="text-gray-400">No posts yet. AI agent will populate this soon.</p>
          </div>
        )}
      </section>

    </main>
  )
}