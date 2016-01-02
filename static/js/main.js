$( document ).ready(function($) {
	console.log("Document ready");

	// Initialize the event list. Will go into its own init function along with more functionality
	update_calendar();

	// Debug button for updating the calendar instantly when needed
	$("#update-cal").click(function() {
		update_calendar();
	});

	setInterval(function() {
		var d = new Date();
		$('.clock').text(('0'+d.getHours()).slice(-2) + ':' + ('0'+d.getMinutes()).slice(-2));
	}, 1000);

	update_interval = 10*60*1000;
	setInterval(function() {
		update_calendar();
	}, update_interval);
});

function update_calendar() {
	var url = "https://calendar.google.com/calendar/ical/ragnarhal%40gmail.com/private-3aaff115768f7c84e5b9ab1d4655344c/basic.ics";
	// Get the calendar from the server
	// TODO: Ajax in an error message if the request failed
	$.get("http://127.0.0.1:5000/getevents", {url : url}, function(data) {
		$(".widget-calendar").empty();
		var calendar = data.results
		calendar.sort(compare);
		for (var e in calendar) {
			var today = (calendar[e].is_today == 1 ? true : false)
			// TODO: Find a better way of building the markup
			$(".widget-calendar").append('<div class="list-group event">\
											<div class="list-group-item-heading"><h3>' + calendar[e].summary + '</h3></div>\
		  									<div class="list-group-item-text calendar-description"><h5>' + (today ? calendar[e].start_time + ' - ' + calendar[e].end_time : calendar[e].start_day) + '</h5></div>\
		  								 </div>');
		};
	});
};

function compare(a, b) {
	if (a.start_day < b.start_day) {
		return -1;
	}
	if (a.start_day > b.start_day) {
		return 1;
	}
	return 0;
}