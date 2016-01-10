var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"];
var WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

$( document ).ready(function($) {
	console.log("Document ready");

	// Debug button for updating the calendar instantly when needed
	$("#update-cal").click(function() {
		calendar.init();
		calendar.update_holidays();
	});
	$("#update-weather").click(function() {
		weather.update_weather();
		weather.update_forecast();
	})

	clock.init();
	calendar.init();
	weather.init();
});

function normalize_date(date) {
	var tokens = date.split('-');
	var year = parseInt(tokens[0]);
	var month = parseInt(tokens[1]) - 1;
	var day = parseInt(tokens[2]);

	return day + '. ' + MONTHS[month] + ' ' + year;
}
