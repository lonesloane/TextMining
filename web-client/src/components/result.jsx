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
			if (topic.relevance==='H'){
				return <li><Link 
							className="btn btn-success btn-xs" 
							type="button"
							to={'searchbytopics/['+topic.id+']'}>
					<b>{topic.label.en}</b>
				</Link></li>
			}else{
				return <li><Link 
							className="btn btn-default btn-xs" 
							type="button"
							to={'searchbytopics/['+topic.id+']'}>
					{topic.label.en}
				</Link></li>

			}
		});
	}
});