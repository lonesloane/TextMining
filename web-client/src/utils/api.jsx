var Fetch = require('whatwg-fetch');

var rootUrl = 'http://127.0.0.1:3000/semantic-search/api/1.0/';

module.exports = window.api = {
	get: function(url){
		return fetch(rootUrl + url)
			.then(function(response){
				return response.json();
			});
	},

	post: function(url, document_id){
		return fetch(rootUrl + url, {
			method: 'post',
			headers: {
				'Accept': 'application/json',
				'Content-Type': 'application/json'
			},
			body: JSON.stringify({
				documentId: document_id
			})
		})
		.then(function(response){
			return response.json();
		});
	}
};