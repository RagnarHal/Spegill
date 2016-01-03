$( document ).ready(function($) {
	console.log("Document ready");

	$(".widget-calendar-error").hide();
	// Initialize the event list. Will go into its own init function along with more functionality
	update_calendar();

	// Debug button for updating the calendar instantly when needed
	$("#update-cal").click(function() {
		update_calendar();
	});

	init_clock();

	update_interval = 60*60*1000;
	setInterval(function() {
		update_calendar();
	}, update_interval);
});

function init_clock() {
	setInterval(function() {
		var d = new Date();
		$('.clock').text(('0'+d.getHours()).slice(-2) + ':' + ('0'+d.getMinutes()).slice(-2));
	}, 1000);
}

function update_calendar() {
	// Corrent URL:
	// https://calendar.google.com/calendar/ical/ragnarhal%40gmail.com/private-3aaff115768f7c84e5b9ab1d4655344c/basic.ics
	var url = "https://calendar.google.com/calendar/ical/ragnarhal%40gmail.com/private-3aaff115768f7c84e5b9ab1d4655344c/basic.ics";
	// Get the calendar from the server
	$.get("http://127.0.0.1:5000/getevents", {url : url}, function(data) {
		console.log("Success");
		$(".widget-calendar-error").hide();
		$(".widget-calendar").empty();
		var calendar = data.results;
		if(calendar.length == 0) $(".widget-calendar").text('No upcoming events!');
		calendar.sort(compare_events);
		for (var e in calendar) {
			console.log(calendar[e].summary);
			var today = (calendar[e].is_today == 1 ? true : false)
			// TODO: Find a better way of building the markup
			$(".widget-calendar").append('<div class="list-group event">\
											<div class="list-group-item-heading"><h3>' + calendar[e].summary + '</h3></div>\
		  									<div class="list-group-item-text calendar-description"><h5>' + (today ? calendar[e].start_time + ' - ' + calendar[e].end_time : calendar[e].start_day) + '</h5></div>\
	  								 	  </div>');
		};
	})
	.fail(function(data) {
		var msg = $(data.responseText).filter("p").html();
		$(".widget-calendar-error").text('Request for calendar went wrong. Error code: ' + data.status + ': ' + msg);
		$(".widget-calendar-error").show();
	});
};

function compare_events(a, b) {
	if (a.start_day < b.start_day) {
		return -1;
	}
	if (a.start_day > b.start_day) {
		return 1;
	}
	return 0;
}