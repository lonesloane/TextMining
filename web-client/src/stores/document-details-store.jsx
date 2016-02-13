var Reflux = require('reflux');
var Actions = require('../actions');
var SearchApi = require('../utils/api');

module.exports = Reflux.createStore({
	listenables: [Actions],

	getDocumentDetails: function(document_id){
		return SearchApi.post('document-details', document_id)
			.then(function(json){
				this.document_details = json.details;
				this.triggerChange();
			}.bind(this));
	},

	triggerChange: function(){
		this.trigger('change', this.document_details);
	}
});