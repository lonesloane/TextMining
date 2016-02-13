var React = require('react');

module.exports = React.createClass({
	getInitialState: function(){
		return {
			message: 'Please enter a topic to begin your search...'
		}
	},

	render: function() {
		return <span>
		    	{this.state.message}<br/>
		  	</span>
	},

});
