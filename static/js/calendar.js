var calendar = {
	'event_list' : [],
	'update_interval' : 60*60*1000,
	'max_events' : 10,
	'url' : 'https://calendar.google.com/calendar/ical/en.is%23holiday%40group.v.calendar.google.com/public/basic.ics'
};

calendar.init = function() {
	this.update();

	setInterval(function() {
		this.update();
	}.bind(this), this.update_interval);
};

calendar.update = function() {
	this.update_data(this.update_calendar.bind(this));
}

calendar.update_data = function(callback) {
	var url = calendar.url;

	// TODO: IP Configurable in config. If another computer on the network tries to run the mirror, for example running the options interface, this will try to access the localhost of that machine. Need to have the IP of the flask server here.
	$.get("http://127.0.0.1:5000/events", {'url' : encodeURI(url), 'debugging' : 'true'}, function(data) {
		console.log("Got response from Calendar API. Updating calendar event list");
		this.event_list = data.results.sort(calendar.compare);
		this.event_list = this.event_list.slice(0, calendar.max_events);

		if (typeof callback == 'function') {
			callback(this.event_list);
		}
		else {
			console.log("Callback function received for updating calendar data is not a function, cannot update calendar.")
		}
	})
	.fail(function(data) {
		console.log("Attempt to get calendar data failed");
		var msg = $(data.responseText).filter('p').html();
		console.log("Error code: " + data.status + ': ' + msg);
	});
};

calendar.update_calendar = function(events) {
	$("#calendar-error").hide();
	$("#calendar-list").empty();

	if (events.length == 0) {
		$("#calendar-list").html('<tr><td>No upcoming events!</td></tr>');
	}

	for (var i in events) {
		var e = events[i];

		var start = e.start.split(' ');
		var end = e.end.split(' ');
		var time_field = (clock.today() == start[0] ? (start.length == 1 ? 'Today' : 'Today at ' + start[1].slice(0,5) + ' - ' + end[1].slice(0,5)) : normalize_date(start[0]));
		
		$("#calendar-list").append(	'<tr>\
										<td>' + (e.summary.length < 20 ? e.summary : e.summary.slice(0, 20) + '...') + '</td>\
		  								<td>' + time_field + '</td>\
	  								</tr>');
	}
};

calendar.compare = function (a, b) {
	if (a.start < b.start) {
		return -1;
	}
	if (a.start > b.start) {
		return 1;
	}
	return 0;
};