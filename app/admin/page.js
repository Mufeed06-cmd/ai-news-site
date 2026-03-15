'use client'
import { useEffect, useState } from 'react'
import { supabase } from '../supabase'

export default function Admin() {
  const [posts, setPosts] = useState([])
  const [loading, setLoading] = useState(true)
  const [password, setPassword] = useState('')
  const [authenticated, setAuthenticated] = useState(false)

  const ADMIN_PASSWORD = "aipulse2026"

  function handleLogin() {
    if (password === ADMIN_PASSWORD) {
      setAuthenticated(true)
    } else {
      alert("Wrong password")
    }
  }

  useEffect(() => {
    if (authenticated) fetchPosts()
  }, [authenticated])

  async function fetchPosts() {
    const { data } = await supabase
      .from('posts')
      .select('*')
      .order('created_at', { ascending: false })
    setPosts(data)
    setLoading(false)
  }

  async function approve(id) {
    await supabase
      .from('posts')
      .update({ status: 'published' })
      .eq('id', id)
    fetchPosts()
  }

  async function reject(id) {
    await supabase
      .from('posts')
      .delete()
      .eq('id', id)
    fetchPosts()
  }

  if (!authenticated) {
    return (
      <div className="min-h-screen bg-black text-white flex items-center justify-center">
        <div className="border border-gray-800 rounded-lg p-8 w-80">
          <h1 className="text-xl font-bold text-orange-500 mb-6">Admin Login</h1>
          <input
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleLogin()}
            className="w-full bg-gray-900 border border-gray-700 rounded px-3 py-2 text-white mb-4 outline-none focus:border-orange-500"
          />
          <button
            onClick={handleLogin}
            className="w-full bg-orange-500 text-black font-bold py-2 rounded hover:bg-orange-400 transition"
          >
            Login
          </button>
        </div>
      </div>
    )
  }

  return (
    <main className="min-h-screen bg-black text-white p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-orange-500">Admin Dashboard</h1>
            <p className="text-gray-400 text-sm">Review and approve AI news drafts</p>
          </div>
          <a href="/" className="text-sm text-gray-400 hover:text-white">Back to site</a>
        </div>

        {loading ? (
          <p className="text-gray-400">Loading drafts...</p>
        ) : posts.length === 0 ? (
          <p className="text-gray-400">No posts found.</p>
        ) : (
          <div className="grid gap-4">
            {posts.map((post) => (
              <div key={post.id} className="border border-gray-800 rounded-lg p-6">
                <div className="flex justify-between items-start mb-3">
                  <span className="text-xs text-orange-500 uppercase">{post.source}</span>
                  <span className={`text-xs px-2 py-1 rounded ${post.status === 'published' ? 'bg-green-900 text-green-400' : 'bg-yellow-900 text-yellow-400'}`}>
                    {post.status}
                  </span>
                </div>
                <h3 className="text-lg font-semibold mb-2">{post.title}</h3>
                <p className="text-gray-400 text-sm mb-4">{post.summary}</p>
                <div className="flex gap-3 items-center">
                  {post.status === 'draft' && (
                    <button
                      onClick={() => approve(post.id)}
                      className="bg-green-700 hover:bg-green-600 text-white text-sm px-4 py-2 rounded transition"
                    >
                      Approve
                    </button>
                  )}
                  <button
                    onClick={() => reject(post.id)}
                    className="bg-red-900 hover:bg-red-800 text-white text-sm px-4 py-2 rounded transition"
                  >
                    Delete
                  </button>
                  <a href={post.source_url} target="_blank" className="text-sm text-orange-500 hover:underline">
                    Read original
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </main>
  )
}