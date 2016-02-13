var React = require('react');
var Actions = require('../actions');
var Reflux = require('reflux');
var DocumentStore = require('../stores/document-store');
var Result = require('./result');

module.exports = React.createClass({
	mixins: [
		Reflux.listenTo(DocumentStore, 'onChange')
	],

	getInitialState: function(){
		return {
			search_results: {'undefined':true}
		}
	},

	componentWillReceiveProps: function(nextProps){
		Actions.getDocumentsForTopics(nextProps.params.topicslist);
	},

	render: function(){
		return <div className="panel-group">
			{this.renderResult()}
		</div>
	},

	renderResult: function(){
			if (!this.state.search_results.undefined){
				return 	<div className="panel panel-default">
							<div className="panel-heading">
								<h3 className="panel-title">Search Results</h3>
							</div>
							<div className="panel-body">
								<p>These documents match the given topics: {this.props.params.topicslist}</p>
							</div>
							<div className="list-group">
								{this.renderResultItems()}
							</div>
						</div>
			}else{
				return "Enter a term to begin your search";
			}
	},

	renderResultItems: function(){
		return this.state.search_results.documents.map(function(result){
			return <Result result={result} topics={this.props.params.topicslist} />
		}.bind(this));
	},

	onChange: function(event, search_results){
		this.setState({
			search_results: search_results
		})
	}

});