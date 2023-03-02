const WEB_SERVER_URL = 'http://localhost:8000';

export default function search_server(query, limit, callback) {
    fetch(WEB_SERVER_URL + `/search?query=${query}&limit=${limit}`)
        .then(response => response.text().then(value => 
            callback(JSON.parse(value))))
        .then(data => {
            return data.split(',');
        })
        .catch(error => {
            console.error(error);
        });
}