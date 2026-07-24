import {useState} from 'react'

function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [searched, setSearched] = useState(false)


  async function handleSearch() {
    if (query.trim() === ''){
      setResults([])
      setError(null)
      setSearched(false)
      return
    }
    setLoading(true)
    setError(null)
    setSearched(true)
    try{
      const response = await fetch(
        `http://127.0.0.1:8000/search?q=${encodeURIComponent(query)}`
      )
      if (!response.ok){
        throw new Error(`Server returned ${response.status}`)
      }
      const data = await response.json()
      setResults(data)
    } 
    catch (err) {
      setError(err.message)
      setResults([])
    } 
    finally {
      setLoading(false)
    }
      

    
  }

  return(
    <div>
      <h1>Stack Overflow Semantic Search</h1>
      <input 
      type = "text" 
      placeholder="Search 500,000 questions..." 
      value = {query}
      onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={handleSearch} disabled={query.trim() === ''}>Search</button>

      {loading && <p>Searching...</p>}
      {error && <p>Something went wrong: {error}</p>}
      {searched && !loading && !error && results.length === 0 && (
        <p>No results found.</p>
      )}

      <ul>
        {results.map((r) => (
          <li key={r.question_id}>{r.title}</li>
        ))}
      </ul>

    </div>
  )
}

export default App