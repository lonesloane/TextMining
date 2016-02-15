var React = require('react');
var Router = require('react-router');
var Link = Router.Link;
var TypeaheadSearch = require('./typeahead-search');

module.exports = React.createClass({

	getInitialState: function(){
		return {
			search_query: '',
		};
	},


	render: function(){
		return <nav className="navbar navbar-default header">

	  			<div className="container-fluid">
	    			<Link to="/" className="navbar-brand">
	    				Semantic Search 0.1
	    			</Link>

			  		<div className="col-lg-10 navbar-form">
			  			<TypeaheadSearch />
					</div>

	  			</div>

			</nav>
	},

	handleInputChange: function(e){
		this.setState({search_query: e.target.value});
	},
});