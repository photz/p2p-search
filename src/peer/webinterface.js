
function show_message(message_text, message_type='info') {

    css_class = 'alert-' + message_type;

    var message_container = document.getElementById('alert-box');

    message_container.className = '';

    message_container.classList.add('alert');
    message_container.classList.add(css_class);

    message_container.innerHTML = message_text;
}

function createNewListElement(title, url) {
    var div_node = document.createElement('div');

    div_node.classList.add('list-group-item');

    var a_node = document.createElement('a');

    div_node.appendChild(a_node);

    a_node.href = url;

    var h4_node = document.createElement('h4');

    a_node.appendChild(h4_node);

    h4_node.classList.add('list-group-item-heading');

    h4_node.innerHTML = title;

    return div_node;
}



var P2PSearch = function(results_list_id) {


    var resultsList = document.getElementById(results_list_id);

    if (resultsList === null) {
	throw new Exception('could not find the results list');
    }

    var POLL_INTERVAL_S = 3;
    var POLL_MAX_TIMES = 5;

    var currentQuery = null;
    var timesPolled = 0;


    //
    // private methods
    //

    var displayResults = function(results) {

	for (var i = 0; i < results.length; i++) {

	    var new_entry = createNewListElement(
		results[i].title,
		results[i].url);

	    resultsList.appendChild(new_entry);
	}

    };

    var pollResults = function(query, continued_query) {
	var request = new XMLHttpRequest();

	request.responseType = 'json';

	request.onreadystatechange = function() {
	    if (request.readyState == 4 && request.status == 200) {

		displayResults(request.response);

		schedulePolling();

	    }
	}

	if (continued_query) {
	    continued_query_str = 'true';
	}
	else {
	    continued_query_str = 'false';
	}

	request.open("GET", "/query?query=" + query + "&continued_query=" + continued_query_str, true);

	request.send();
    };

    var conditionallyPollMoreResults = function() {
	if (currentQuery !== null && timesPolled < POLL_MAX_TIMES) {
	    
	    timesPolled++;

	    pollResults(currentQuery, true);


	}
    };

    var schedulePolling = function() {
	setTimeout(conditionallyPollMoreResults, POLL_INTERVAL_S);
    };

    //
    // public methods
    //

    this.poseQuery = function(query) {

	resultsList.innerHTML = '';

	currentQuery = query;

	pollResults(currentQuery, false);

    };
};

var SearchInterface = function(button_id, input_id) {
    
    var button = document.getElementById(button_id);

    if (button === null) {
    	throw new Exception('could not find the search button');
    }

    var input = document.getElementById(input_id);

    if (input === null) {
    	throw new Exception('could not find the input field');
    }

    var p2psearch = new P2PSearch('ResponseList');

    var userPosesQueryCallback = function(event) {
	if (input.value === '') {
	    show_message('Please enter a query.', 'warning');
	}
	else {
	    p2psearch.poseQuery(input.value);
	    show_message('Searching for ' + input.value + '...');
	}
    };

    button.addEventListener('click', function (event) {
	userPosesQueryCallback();
    });

    input.addEventListener('keydown', function (event) {
	if (event.which == 13 || event.keyCode == 13) {
	    userPosesQueryCallback();
	    return true;
	}
	return true;
    });
};



window.onload = function() {
    var searchinterface = new SearchInterface('search-button',
					      'query-field');
};


    
