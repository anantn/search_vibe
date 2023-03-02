import React, { useState } from 'react';
import SearchBar from './SearchBar';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = { search_results: [], query: '' };
    this.handleChange = this.handleChange.bind(this);
    this.search = this.search.bind(this);
  }

  render() {
    return (
      <div>
      <SearchBar onSearch={this.search} />
      {/* Render the search results */}
      <ul>
        {this.state.search_results.map(result => (
          <li key={result.id}>{result.text}</li>
        ))}
      </ul>
    </div>
    );
  }

  handleChange(e) {
    this.setState({ query: e.target.value });
  }

  search(query) {
    if (query.length === 0) {
      return;
    }
    const newItem = {
      text: query,
      id: Date.now()
    };
    this.setState(state => ({
      search_results: state.search_results.concat(newItem),
      query: ''
    }));
  }

}

export default App;

