var React = require('react');
var Actions = require('../actions');
var Reflux = require('reflux');
var DocumentDetailsStore = require('../stores/document-details-store');
var SemanticSignature = require('./semantic-signature');
var Router = require('react-router');
var Link = Router.Link;

module.exports = React.createClass({
	mixins: [
		Reflux.listenTo(DocumentDetailsStore, 'onChange')
	],

	getInitialState: function(){
		return {
			document_details: {'undefined':true}
		}
	},

	componentWillReceiveProps: function(nextProps){
		Actions.getDocumentDetails(nextProps.params.document_id);
	},

	render: function(){
		return <div>
			<div className="panel panel-default">
				<div className="panel-heading">Document Details</div>
				<div className="panel-body">
					{this.renderSemanticSignature()}
				</div>
			</div>
			<div className="panel panel-default">
				<div className="panel-heading">Proximity Results</div>
				<ul className="list-group">
					{this.renderProximityResults()}
				</ul>
			</div>
		</div>
	},

	renderSemanticSignature: function(){
		if (!this.state.document_details.undefined){
			return <SemanticSignature document_name={this.props.params.document_id} signature={this.state.document_details.semantic_signature} />
		}else{
			return <span>Nothing to display...</span>
		}	
	},

	renderProximityResults: function(){
		if (!this.state.document_details.undefined){
			return this.state.document_details.proximity_results.map(function(result){
				return <li className="list-group-item">
					<div className="label label-warning" href="#">
						<Link to={'documentdetails/'+result.filename}>
					        {result.filename}
						</Link>
					</div>
					<ul className="list-group">{this.renderProximityDetaisl(result)}</ul>
				</li>
			}.bind(this));
		}else{
			return <span>Nothing to display...</span>
		}	
	},

	renderProximityDetaisl: function(result){
		return result.semantic_signature.map(function(detail){
					return <li className="list-group-item">{detail.lbl_en} <span className="badge">{detail.score}</span></li>
				});
	},

	onChange: function(event, document_details){
		this.setState({
			document_details: document_details
		})
	}
});