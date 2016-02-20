var React = require('react');
var ReactDOM = require('react-dom');
var Router = require('react-router');
var Link = Router.Link;

module.exports = React.createClass({

  getInitialState: function(){
    return {
      search_query: '',
    };
  },

  handleChange: function(e) {
    console.log(e.target.value);
    this.setState({search_query: e.target.value});
  },

  componentDidMount: function() {

    // constructs the suggestion engine
    var suggest = new Bloodhound({
      datumTokenizer: Bloodhound.tokenizers.whitespace,
      queryTokenizer: Bloodhound.tokenizers.whitespace,
      prefetch: 'http://127.0.0.1:3000/topics'
    });

    ReactDOM.findDOMNode(this.refs.searchInput).focus();
    $ (ReactDOM.findDOMNode(this.refs.searchInput)).typeahead({
      hint: true,
      highlight: true,
      minLength: 2
    },
    {
      name: 'suggest',
      source: suggest
    });

  },

  render: function() {
    console.log('render typeahead search input');
    return (
        <div className="input-group" id="bloodhound">
          <input 
            id="typeahead"
            className="form-control typeahead"
            type="text" 
            placeholder="Enter a topic to search" 
            ref="searchInput" 
            name="sahan" 
            onChange={this.handleChange} 
            onBlur={this.handleChange}
          />
          <span className="input-group-btn">
            <Link
              className="btn btn-default" 
              type="button" 
              to={'searchbytopics/['+this.state.search_query+']'}>
              Search
            </Link>
          </span>
        </div>
    );
  }
});