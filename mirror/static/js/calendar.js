var calendar = {
	'event_list' : [],
	'update_interval' : 60*60*1000,
	'max_events' : 10
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
	$.get("http://" + location.host + "/events", function(data) {
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

calendar.update_holidays = function() {
	$.get("http://" + location.host + "/holidays", function(data) {
		console.log("Got response from Holidays API. Updating holidays event list");

		holidays = data.results.sort(calendar.compare).slice(0, 10);

		for (var i in holidays) {
			h = holidays[i];
			var date_field = (h.start == clock.today ? 'Today' : normalize_date(h.start));
			$("#holidays-list").append(	'<tr>\
											<td>' + h.summary.split('[')[0] + '</td>\
			  								<td>' + date_field + '</td>\
		  								</tr>');
		}
		
	})
	.fail(function(data) {
		console.log("Attempt to get holidays data failed");
		var msg = $(data.responseText).filter('p').html();
		console.log("Error code: " + data.status + ': ' + msg);
	});
}

calendar.compare = function (a, b) {
	if (a.start < b.start) {
		return -1;
	}
	if (a.start > b.start) {
		return 1;
	}
	return 0;
};