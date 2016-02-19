var React = require('react');
var Router = require('react-router');
var Link = Router.Link;

module.exports = React.createClass({
	render: function(){
		return <div className="list-group-item" href="#">
					<Link to={'documentdetails/'+this.props.result.name}>
				        {this.props.result.name}
					</Link>
					<ul className="list-group-item-text list-inline">
						<br/>
						{this.renderSemanticSignature()}
					</ul>
	    </div>
	},

	renderSemanticSignature: function(){
		return this.props.result.semantic_signature.map(function(topic){
			return <li><Link 
						className={this.btnClassByRelevance(topic.relevance)}
						type="button"
						to={'searchbytopics/['+this.buildListSelectedTopics(topic.label.en)+']'}>
				{topic.label.en}
			</Link></li>
		}.bind(this));
	},

	buildListSelectedTopics: function(signatureTopic){
		var topicsList = signatureTopic;
		this.props.topics.forEach(function(topic){
			topicsList += ","+topic.label.en;
		});
		return topicsList;
	},

	btnClassByRelevance: function(relevance){
		if (relevance === 'H') {
			return "btn btn-success btn-xs";
		}else {
			return "btn btn-default btn-xs";
		}
	}

});