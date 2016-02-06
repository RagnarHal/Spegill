var calendar = {
	event_list : [],
	holiday_list : [],
	update_interval : 60*60*1000,
	max_events : 10,
	max_holidays : 10
};

calendar.init = function() {
	this.update();

	setInterval(function() {
		this.update();
	}.bind(this), this.update_interval);
};

calendar.update = function() {
	this.update_data("events", this.update_calendar.bind(this));
	this.update_data("holidays", this.update_holidays.bind(this));
};

calendar.update_data = function(which, callback) {
	// Update the calendar
	$.get("http://" + location.host + "/" + which, function(data) {
		console.log("Got response from " + which + " API. Updating " + which + "list");
		if (which === "events") {
			this.event_list = data.results.sort(calendar.compare).slice(0, calendar.max_events);
			if (typeof callback == 'function') {
				callback(this.event_list);
			}
		}
		else if (which === "holidays") {
			this.holiday_list = data.results.sort(calendar.compare).slice(0, calendar.max_holidays);
			if (typeof callback == 'function') {
				callback(this.holiday_list);
			}
		}
	}).fail(function(data) {
		console.log("Attempt to get " + which + " data failed");
		var msg = $(data.responseText).filter('p').html();
		console.log("Error code: " + data.status + ': ' + msg);
	});
};

calendar.update_calendar = function(events) {
	$("#calendar-error").hide();
	$("#calendar-list").empty();

	if (events.length === 0) {
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

calendar.update_holidays = function(holidays) {
	$("#holidays-error").hide();
	$("#holidays-list").empty();

	if (holidays.length === 0) {
		$(".holidays .list-header").empty();
		$("#holidays-list").empty();
	}

	holidays.forEach(function(holiday) {
		var date_field = (holiday.start == clock.today ? 'Today' : normalize_date(holiday.start));
		$("#holidays-list").append(	'<tr>\
										<td>' + holiday.summary.split('[')[0] + '</td>\
		  								<td>' + date_field + '</td>\
	  								</tr>');
	});
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