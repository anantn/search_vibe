import React, { useState } from 'react';

function SearchBar({ onSearch }) {
  const [searchTerm, setSearchTerm] = useState('');

  const handleChange = event => {
    setSearchTerm(event.target.value);
  };

  const handleSubmit = event => {
    event.preventDefault();
    onSearch(searchTerm);
  };

  return (
    // Generate a button that, when clicked, will call the onSearch function
    // with the current value of the search term
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="Search..."
        value={searchTerm}
        onChange={handleChange}
      />
      <button type="submit">Search</button>
    </form>
  );
}

export default SearchBar;
