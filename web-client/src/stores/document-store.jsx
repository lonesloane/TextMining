var Reflux = require('reflux');
var Actions = require('../actions');
var SearchApi = require('../utils/api');

module.exports = Reflux.createStore({
	listenables: [Actions],

	getDocumentsForTopics: function(topics_list){
		return SearchApi.get('documents/topic_labels/'+topics_list)
			.then(function(json){
				this.search_results = json.search_results;
				this.triggerChange();
			}.bind(this));
	},

	triggerChange: function(){
		this.trigger('change', this.search_results);
	}


});