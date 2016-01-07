var monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

$( document ).ready(function($) {
	console.log("Document ready");

	$(".widget-calendar-error").hide();
	$(".widget-weather-error").hide();
	// Initialize the event list. Will go into its own init function along with more functionality

	// Debug button for updating the calendar instantly when needed
	$("#update-cal").click(function() {
		update_calendar();
	});
	$("#update-weather").click(function() {
		update_weather();
	})

	init_clock();
	//init_calendar(60*60*1000)
});

function init_calendar(interval) {
	setInterval(function() {
			update_calendar();
		}, interval);
}

function init_clock() {
	setInterval(function() {
		var d = new Date();
		$('.clock').text(('0'+d.getHours()).slice(-2) + ':' + ('0'+d.getMinutes()).slice(-2));
	}, 1000);
}

function update_weather() {
	// Correct URL:
	// Today:
	// http://api.openweathermap.org/data/2.5/weather?id=6692263&appid=2de143494c0b295cca9337e1e96b00e0
	// Forecast:
	// http://api.openweathermap.org/data/2.5/forecast?id=6692263&appid=2de143494c0b295cca9337e1e96b00e0
	var current = 'http://api.openweathermap.org/data/2.5/weather?id=3413829&appid=2de143494c0b295cca9337e1e96b00e0'
	var forecast = 'http://api.openweathermap.org/data/2.5/forecast?id=3413829&appid=2de143494c0b295cca9337e1e96b00e0'
	console.log(current)
	console.log(forecast)

	$.get("http://127.0.0.1:5000/weather", {'current' : encodeURI(current), 'forecast' : encodeURI(forecast), 'dbg' : 'true'}, function(data) {
		console.log("Got response from Weather API");
		$(".widget-weather-error").hide();
		var weather = data.results;
		console.log(data.results);
		if(weather.length == 0) $(".widget-weather").text("No weather :(");
		var date = new Date(weather.dt*1000)
		console.log(date);
		
		$("#weather-calc-date").text(monthNames[date.getMonth()] + " " + date.getDate() + " " + date.getFullYear());
		$("#weather-calc-time").text(('0' + date.getHours()).slice(-2) + ':' + ('0' + date.getMinutes()).slice(-2));
		$("#weather-temp").text(+(Math.round(weather.main.temp - 273.15 + "e+1") + "e-1") + "°C");
		$("#weather-main").text(weather.weather.main);
		$("#weather-desc").text(weather.weather[0].description);
		$("#weather-windspeed").text(weather.wind.speed + " m/s");
		$("#weather-winddirection").text(weather.wind.deg + "°");
		$("#weather-cloudpercent").text(weather.clouds.all + "% clouds");
	})
	.fail(function(data) {
		var msg = $(data.responseText).filter("p").html();
		$(".widget-weather-error").text("Request for weather went wrong. Error code: " + data.status + ": " + msg);
		$(".widget-weather-error").show();
	})
}

function update_calendar() {
	// Corrent URL:
	// https://calendar.google.com/calendar/ical/ragnarhal%40gmail.com/private-3aaff115768f7c84e5b9ab1d4655344c/basic.ics
	var url = "https://calendar.google.com/calendar/ical/ragnarhal%40gmail.com/private-3aaff115768f7c84e5b9ab1d4655344c/basic.ics";
	// Get the calendar from the server
	$.get("http://127.0.0.1:5000/events", {url : url}, function(data) {
		console.log("Got response from Calendar API");
		$(".widget-calendar-error").hide();
		$(".widget-calendar").empty();
		var calendar = data.results;
		if(calendar.length == 0) $(".widget-calendar").text('No upcoming events!');
		calendar.sort(compare_events);
		for (var e in calendar) {
			//console.log(calendar[e].summary);
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