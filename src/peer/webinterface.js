
function show_message(message_text, message_type='info') {

    var css_class = 'alert-' + message_type;

    var message_container = document.getElementById('alert-box');

    message_container.className = '';

    message_container.classList.add('alert');
    message_container.classList.add(css_class);

    message_container.innerHTML = message_text;
}



var P2PSearch = function() {


    // timeout for the requests in ms
    var REQUEST_TIMEOUT_MS = 300;
    var POLL_INTERVAL_MS = 250;
    var POLL_MAX_TIMES = 5;

    var currentQuery = null;
    var timesPolled = 0;
    var activeTimeout = null;

    var gotResultsCallback = null;
    var progressChangedCallback = null;

    //
    // private methods
    //


    var requestTimeoutCallback = function() {
	show_message('The service could not be reached. Is p2psearch running?',
		     'danger');

	currentQuery = null;
    };

    var pollResults = function(query, continued_query) {
	var request = new XMLHttpRequest();

	request.responseType = 'json';

	request.onreadystatechange = function() {
	    if (request.readyState !== 4) return;


	    if (request.status == 200) {

		progressChangedCallback(
		    100 * timesPolled / POLL_MAX_TIMES);

		if (request.response.length > 0) {
		    gotResultsCallback(request.response);
		}

		schedulePolling();
	    }
	    else {
		show_message('An error occurred. Is p2psearch running?',
			     'danger');
	    }

	}

	request.onTimeout = requestTimeoutCallback;

	if (continued_query) {
	    continued_query_str = 'true';
	}
	else {
	    continued_query_str = 'false';
	}

	request.open("GET", "/query?query=" + query + "&continued_query=" + continued_query_str, true);

	request.timeout = REQUEST_TIMEOUT_MS;

	request.send();
    };

    var conditionallyPollMoreResults = function() {
	if (activeTimeout === null) {
	    throw new Exception('conditionalPollMoreResults is supposed to be called by a timeout, but activeTimeout was found null');
	}

	activeTimeout = null;

	if (currentQuery !== null && timesPolled < POLL_MAX_TIMES) {
	    
	    timesPolled++;

	    pollResults(currentQuery, true);

	}
	else {
	    currentQuery = null;
	    timesPolled = 0;
	}
    };

    var schedulePolling = function() {
	if (activeTimeout !== null) {
	    throw new Exception('about to set up a timeout, but activeTimeout was not null');
	}

	activeTimeout = setTimeout(conditionallyPollMoreResults, POLL_INTERVAL_MS);
    };

    

    //
    // public methods
    //

    this.poseQuery = function(query) {

	timesPolled = 0;
	currentQuery = query;
	progressChangedCallback(0);

	if (activeTimeout !== null) {

	    window.clearTimeout(activeTimeout);
	    activeTimeout = null;
	}

	pollResults(currentQuery, false);

    };

    this.setProgressChangedCallback = function(callback) {
	if (typeof(callback) !== 'function') {
	    throw new Exception('expected a function as callback');
	}

	progressChangedCallback = callback;
    };

    this.setGotResultsCallback = function(callback) {
	if (typeof(callback) !== 'function') {
	    throw new Exception('expected a function as callback');
	}

	gotResultsCallback = callback;
    };
};

var SearchInterface = function(button_id, input_id,
			       results_list_id, progress_bar_id) {
    
    var resultsList = document.getElementById(results_list_id);

    if (resultsList === null) {
	throw new Exception('could not find the results list');
    }

    var button = document.getElementById(button_id);

    if (button === null) {
    	throw new Exception('could not find the search button');
    }

    var input = document.getElementById(input_id);

    if (input === null) {
    	throw new Exception('could not find the input field');
    }

    var progressBar = document.getElementById(
	progress_bar_id);

    if (progressBar === null) {
	throw new Exception('could not find the progress bar');
    }


    var createListElement = function(title, url) {
	var div_node = document.createElement('div');

	div_node.classList.add('list-group-item');

	var a_node = document.createElement('a');

	div_node.appendChild(a_node);

	a_node.href = url;

	var h4_node = document.createElement('h4');

	a_node.appendChild(h4_node);

	h4_node.classList.add('list-group-item-heading');

	h4_node.innerHTML = title;

	var item_text = document.createElement('p');

	a_node.appendChild(item_text);

	item_text.classList.add('list-group-item-text')
	item_text.classList.add('text-muted')

	item_text.innerHTML = url;

	return div_node;
    };


    var userPosesQueryCallback = function(event) {
	resultsList.innerHTML = '';

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
	var ENTER_KEYCODE = 13;

	if (event.which == ENTER_KEYCODE
	    || event.keyCode == ENTER_KEYCODE) {

	    userPosesQueryCallback();

	    return false;
	}
	return true;
    });



    var p2psearch = new P2PSearch();

    p2psearch.setGotResultsCallback(function(results) {

	//tfor (var i = 0; i < results.length; i++) {

	results.forEach(function(doc) {

	    var new_entry = createListElement(
		doc.title,
		doc.url);

	    resultsList.appendChild(new_entry);
	});

    });

    p2psearch.setProgressChangedCallback(function(progress) {

	progressBar.style.width = progress.toString() + '%';
    });
};



window.onload = function() {
    var searchinterface = new SearchInterface('search-button',
					      'query-field',
					      'results-list',
					      'search-progress-bar');
};


    
