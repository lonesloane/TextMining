var React = require('react');
var DocumentsList = require('./documents-list');
var SearchBox = require('./search-box');

module.exports = React.createClass({
	render: function(){
		return <div>
			<SearchBox />
			{this.content()}
		</div>
	},

	content: function(){
		if (this.props.children){
			return this.props.children;
		}else{
			return "Enter a term to begin your search";
		}
	}
});