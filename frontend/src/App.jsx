import {useState} from 'react'

function App() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])

  async function handleSearch() {
    const response = await fetch(`http://127.0.0.1:8000/search?q=${query}`)
    const data = await response.json()
    setResults(data)
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
      <button onClick={handleSearch}>Search</button>
      
      <ul>
        {results.map((r) => (
          <li key={r.question_id}>{r.title}</li>
        ))}
      </ul>

    </div>
  )
}

export default App