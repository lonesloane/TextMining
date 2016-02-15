var React = require("react");
var Router = require('react-router');
var Link = Router.Link;

module.exports = React.createClass({

	render: function(){
		return <div className="list-group-item" href="#">
		        <h4><span className="label label-primary">{this.props.document_name}</span></h4>
			<ul className="list-group-item-text list-inline">
				{this.renderSemanticSignature()}
			</ul>
	    </div>
	},

	renderSemanticSignature: function(){
		return this.props.signature.map(function(topic){
			if (topic.relevance==='H'){
				return <li><Link 
							className="btn btn-success btn-xs" 
							type="button"
							to={'searchbytopics/['+topic.label.en+']'}>
					<b>{topic.label.en}</b>
				</Link></li>
			}else{
				return <li><Link 
							className="btn btn-default btn-xs" 
							type="button"
							to={'searchbytopics/['+topic.label.en+']'}>
					{topic.label.en}
				</Link></li>
			}
		});
	}
});