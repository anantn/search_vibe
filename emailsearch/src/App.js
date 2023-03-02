import React, { useState } from 'react';
import SearchBar from './SearchBar';

function App() {
  const [searchResults, setSearchResults] = useState([]);

  const handleSearch = searchTerm => {
    // Use the search term to fetch search results
    // and update the searchResults state
    setSearchResults([{ id: 1, name: 'John' }, { id: 2, name: 'Jane' }]);
  };

  return (
    <div>
      <SearchBar onSearch={handleSearch} />
      {/* Render the search results */}
      <ul>
        {searchResults.map(result => (
          <li key={result.id}>{result.name}</li>
        ))}
      </ul>
    </div>
  );
}

export default App;

