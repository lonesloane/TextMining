var React = require('react');
var ReactRouter = require('react-router');
var Main = require('./components/main');
var DocumentsList = require('./components/documents-list');
var DocumentDetails = require('./components/document-details');

var Router = ReactRouter.Router;
var Route = ReactRouter.Route;

module.exports = (
	<Router>
		<Route path="/" component={Main} >
			<Route path="searchbytopics/:topicslist" component={DocumentsList} />
			<Route path="documentdetails/:document_id" component={DocumentDetails} />
		</Route>
	</Router>
);