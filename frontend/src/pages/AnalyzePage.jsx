import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Loader, AlertCircle } from 'lucide-react'

export default function AnalyzePage() {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('article')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const [articleForm, setArticleForm] = useState({
    title: '',
    content: '',
    source: '',
    author: '',
    url: '',
  })

  const [searchForm, setSearchForm] = useState({
    query: '',
    numArticles: 10,
  })

  const handleArticleChange = (e) => {
    const { name, value } = e.target
    setArticleForm(prev => ({ ...prev, [name]: value }))
  }

  const handleSearchChange = (e) => {
    const { name, value } = e.target
    setSearchForm(prev => ({ ...prev, [name]: value }))
  }

  const handleArticleSubmit = async (e) => {
    e.preventDefault()
    if (!articleForm.title.trim() || !articleForm.content.trim()) {
      setError('Please fill in title and content')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8000/analyze/article', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: articleForm.title,
          content: articleForm.content,
          source: articleForm.source || 'Unknown',
          author: articleForm.author || '',
          url: articleForm.url || '',
          description: '',
          published_at: new Date().toISOString(),
        }),
      })

      if (!response.ok) throw new Error('Analysis failed')

      const data = await response.json()
      navigate(`/results/${data.analysis_id}`)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  const handleSearchSubmit = async (e) => {
    e.preventDefault()
    if (!searchForm.query.trim()) {
      setError('Please enter a search query')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const response = await fetch('http://localhost:8000/search/news', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchForm.query,
          num_articles: parseInt(searchForm.numArticles),
          detect_misinformation: true,
          detect_bias: true,
        }),
      })

      if (!response.ok) throw new Error('Search failed')

      const data = await response.json()
      navigate(`/results/${data.query.replace(/\s+/g, '-')}`)
    } catch (err) {
      setError(err.message)
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 pt-24 pb-16">
      <div className="max-w-4xl mx-auto px-6">
        <div className="space-y-8">
          <div className="text-center space-y-4">
            <h1 className="text-5xl font-bold">Analyze News</h1>
            <p className="text-xl text-slate-400">
              Submit an article or search for news to detect misinformation and bias
            </p>
          </div>

          {error && (
            <div className="flex items-start gap-4 p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <AlertCircle size={20} className="text-red-400 mt-0.5 flex-shrink-0" />
              <p className="text-red-300">{error}</p>
            </div>
          )}

          {/* Tabs */}
          <div className="flex gap-2 border-b border-accent-500/10">
            <button
              onClick={() => setActiveTab('article')}
              className={`px-6 py-4 font-semibold transition-all ${
                activeTab === 'article'
                  ? 'text-accent-400 border-b-2 border-accent-500'
                  : 'text-slate-400 hover:text-slate-300'
              }`}
            >
              Single Article
            </button>
            <button
              onClick={() => setActiveTab('search')}
              className={`px-6 py-4 font-semibold transition-all ${
                activeTab === 'search'
                  ? 'text-accent-400 border-b-2 border-accent-500'
                  : 'text-slate-400 hover:text-slate-300'
              }`}
            >
              News Search
            </button>
          </div>

          {/* Forms */}
          <div className="card-dark p-8 rounded-xl">
            {activeTab === 'article' ? (
              <form onSubmit={handleArticleSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-2">
                    Article Title *
                  </label>
                  <input
                    type="text"
                    name="title"
                    value={articleForm.title}
                    onChange={handleArticleChange}
                    placeholder="Enter article title"
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-accent-500 transition"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-2">
                    Article Content *
                  </label>
                  <textarea
                    name="content"
                    value={articleForm.content}
                    onChange={handleArticleChange}
                    placeholder="Paste article text here..."
                    rows={8}
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-accent-500 transition"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-2">
                      Source
                    </label>
                    <input
                      type="text"
                      name="source"
                      value={articleForm.source}
                      onChange={handleArticleChange}
                      placeholder="e.g., BBC News, CNN"
                      className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-accent-500 transition"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-semibold text-slate-300 mb-2">
                      Author
                    </label>
                    <input
                      type="text"
                      name="author"
                      value={articleForm.author}
                      onChange={handleArticleChange}
                      placeholder="Optional"
                      className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-accent-500 transition"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-2">
                    URL
                  </label>
                  <input
                    type="url"
                    name="url"
                    value={articleForm.url}
                    onChange={handleArticleChange}
                    placeholder="https://example.com"
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-accent-500 transition"
                  />
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading && <Loader size={20} className="animate-spin" />}
                  {loading ? 'Analyzing...' : 'Analyze Article'}
                </button>
              </form>
            ) : (
              <form onSubmit={handleSearchSubmit} className="space-y-6">
                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-2">
                    Search Query *
                  </label>
                  <input
                    type="text"
                    name="query"
                    value={searchForm.query}
                    onChange={handleSearchChange}
                    placeholder="Enter news topic or keyword..."
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white placeholder-slate-500 focus:outline-none focus:border-accent-500 transition"
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-300 mb-2">
                    Number of Articles
                  </label>
                  <select
                    name="numArticles"
                    value={searchForm.numArticles}
                    onChange={handleSearchChange}
                    className="w-full px-4 py-3 bg-slate-900/50 border border-slate-700/50 rounded-lg text-white focus:outline-none focus:border-accent-500 transition"
                  >
                    <option value="5">5 articles</option>
                    <option value="10">10 articles</option>
                    <option value="20">20 articles</option>
                    <option value="30">30 articles</option>
                  </select>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50"
                >
                  {loading && <Loader size={20} className="animate-spin" />}
                  {loading ? 'Searching & Analyzing...' : 'Search & Analyze'}
                </button>
              </form>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="card-dark p-6 rounded-lg">
              <h3 className="font-semibold text-accent-400 mb-2">⚡ Fast</h3>
              <p className="text-sm text-slate-400">Get results in ~8 seconds</p>
            </div>
            <div className="card-dark p-6 rounded-lg">
              <h3 className="font-semibold text-accent-400 mb-2">🎯 Accurate</h3>
              <p className="text-sm text-slate-400">95%+ detection accuracy</p>
            </div>
            <div className="card-dark p-6 rounded-lg">
              <h3 className="font-semibold text-accent-400 mb-2">🧠 Smart</h3>
              <p className="text-sm text-slate-400">11 AI agents analyzing</p>
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
