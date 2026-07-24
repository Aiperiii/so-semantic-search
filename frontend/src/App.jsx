import { useState } from 'react'
import './App.css'

function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searched, setSearched] = useState(false)
  const [mode, setMode] = useState('hybrid')

  async function handleSearch() {
    if (query.trim() === '') {
      setResults([])
      setError(null)
      setSearched(false)
      return
    }
    setLoading(true)
    setError(null)
    setSearched(true)
    try {
      const endpoint = mode === 'hybrid' ? '/hybrid' : '/search'
      const response = await fetch(
        `http://127.0.0.1:8000${endpoint}?q=${encodeURIComponent(query)}`
      )
      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`)
      }
      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError(err.message)
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      <h1>Stack Overflow Semantic Search</h1>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Search 500,000 questions..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') handleSearch() }}
        />
        <button onClick={handleSearch} disabled={query.trim() === ''}>Search</button>
        <div className="mode-toggle">
          <button className={mode === 'keyword' ? 'active' : ''} onClick={() => setMode('keyword')}>Keyword only</button>
          <button className={mode === 'hybrid' ? 'active' : ''} onClick={() => setMode('hybrid')}>Hybrid + AI rerank</button>
        </div>
      </div>
      
      {loading && <p className="message">Searching...</p>}
      {error && <p className="message error">Something went wrong: {error}</p>}
      {searched && !loading && !error && results.length === 0 && (
        <p className="message">No results found.</p>
      )}

      <div className="results">
        {results.map((r) => (
          <div className="result-card" key={r.question_id}>
            <a className="result-title" href={`https://stackoverflow.com/questions/${r.question_id}`} target="_blank" rel="noopener noreferrer">{r.title}</a>
          </div>
        ))}
      </div>
    </div>
  )
}

export default App