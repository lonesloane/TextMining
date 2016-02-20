var React = require('react');
var Router = require('react-router');
var Link = Router.Link;

module.exports = React.createClass({


	render: function(){
		return <span>
			<ul className="list-group-item-text list-inline">
				{this.renderTopics()}
			</ul>
		</span>
	},

	renderTopics: function(){
		return this.props.topics.map(function(topic){
			return <li>
				<Link 
					className="btn btn-default btn-xs"
					type="button"
					to={this.buildToUrl(topic.label.en)}>
						{topic.label.en}
				</Link></li>
		}.bind(this));
	},

	buildToUrl: function(currentTopic){
		if (this.props.topics.length === 1){
			return "/";
		}
		else{
			var toUrl = "searchbytopics/["+this.buildListSelectedTopics(currentTopic)+"]"
			return toUrl;
		}
	}, 

	buildListSelectedTopics: function(currentTopic){
		var topicsList = "";
		var sep = "";
		this.props.topics.forEach(function(topic){
			if (topic.label.en != currentTopic){
				topicsList += sep+topic.label.en;
				sep = ",";
			}
		});
		return topicsList;

	}
});