/*$(".crossButton").click(function() { // or $("input#<input id, if it has one>")...
	$.post('/',{'button': event.target.id});
	//$.post('/', {'button': 'olivier'});
    // If you want to post to the backend instead, do
    // $.post('/button');
});*/

$(".crossButton").mousedown(function() { // or $("input#<input id, if it has one>")...
	$.post('/',{'button': event.target.id, 'stop': "False"});
});

$(".crossButton").mouseup(function() { // or $("input#<input id, if it has one>")...
	$.post('/',{'button': event.target.id, 'stop': "True"});
	//$.post('/', {'button': 'olivier'});
    // If you want to post to the backend instead, do
    // $.post('/button');
});