import React, { useState } from 'react';
import SearchBar from './SearchBar';
import search_server from './api_calls';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = { search_results: [], query: '' };
    this.handleChange = this.handleChange.bind(this);
    this.search = this.search.bind(this);
    this.handleResults = this.handleResults.bind(this);
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

  handleResults(results) {
    var items = []

    results.forEach((result, i) => {
      const newItem = {
        text: result,
        id: i
      };
      items = items.concat(newItem);
    });

    this.setState(state => ({
      search_results: items,
      query: ''
    }));
  }

  search(query) {
    if (query.length === 0) {
      return;
    }
    search_server(query, 10, this.handleResults)
  }

}

export default App;

