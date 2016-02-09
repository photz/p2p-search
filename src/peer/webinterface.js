function show_warning(warning_text) {
    var warning_container = document.getElementById('search-warning');

    warning_container.innerHTML = warning_text;
}

function show_message(message_text, message_type='info') {

    css_class = 'alert-' + message_type;

    var message_container = document.getElementById('search-message');

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

function p2psearch() {

    var query_field = document.getElementById("query-field");
    var QueryFieldValue = document.createTextNode(query_field.value);
    var statusDisplay = document.getElementById('status-display');
    var ResponseList = document.getElementById("ResponseList");
    
    statusDisplay.innerHTML = '';
    ResponseList.innerHTML = '';

    if (query_field.value == ""){
	show_message('Please enter a search query', 'info');
    }
    else {
	show_message('Results for ' + QueryFieldValue, 'info');
	
	var xhttp = new XMLHttpRequest();
	xhttp.onreadystatechange = function() {
	    if (xhttp.readyState == 4 && xhttp.status == 200) {
		
		response = xhttp.response;
		console.log(response.length);
		for (i = 0; i < response.length; i++) {
		    var entry = createNewListElement(response[i].title,
						     response[i].url);


		    ResponseList.appendChild(entry);
		    //console.log("Listeneintrag ergänzt");
		}
	    }
	};
	xhttp.responseType = 'json';
	xhttp.open("GET", "/query?query=" + query_field.value + "&continued_query=false", true);
	xhttp.send();
	
	for (i = 1; i < 5; i++){
	    setTimeout(function() {
		xhttp.open("GET", "/query?query=" + query_field.value + "&continued_query=true", true);
		xhttp.send();
	    }, i*3000);
	    //		console.log(i);
	}
    }
}

function doItOnInterval() {
    doItOnInterval();
    setInterval("doItOnInterval()", 5000);
}

