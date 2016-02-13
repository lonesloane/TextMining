var React = require('react');
var Router = require('react-router');
var Link = Router.Link;

module.exports = React.createClass({
	getInitialState: function(){
		return {
			search_query: ''
		}
	},

	render: function(){
		return <nav className="navbar navbar-default header">

	  			<div className="container-fluid">
	    			<Link to="/" className="navbar-brand">
	    				Semantic Search 0.1
	    			</Link>

			  		<div className="col-lg-10 navbar-form">
					    <div className="input-group">
						  <input 
							value={this.state.search_query}
							onChange={this.handleInputChange} 
						  	type="text" 
						  	className="form-control" 
						  	placeholder="Enter a topic to search" />
						  <span className="input-group-btn">
							<Link
								className="btn btn-default" 
								type="button" 
								to={'searchbytopics/['+this.state.search_query+']'}>
								Search
							</Link>
					      </span>
					    </div>
					</div>

	  			</div>

			</nav>
	},

	handleInputChange: function(e){
		this.setState({search_query: e.target.value});
	},
});