var MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sept", "Oct", "Nov", "Dec"];
var WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

$( document ).ready(function($) {
	console.log("Document ready");

	// Debug button for updating the calendar instantly when needed
	$("#update-cal").click(function() {
		console.log("Update calendar clicked.");
		calendar.init();
	});
	$("#update-weather").click(function() {
		update_weather();
	})

	clock.init();
});

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

	$.get("http://127.0.0.1:5000/weather-current", {'url' : encodeURI(current), 'debugging' : 'true'}, function(data) {
		console.log("Got response from Current Weather API");
		$("#weather-current-error").hide();
		$("#weather-current").empty();
		var weather = data;
		if(weather.length == 0) $("#weather-current").text("No weather :(");
		
		$("#weather-current").append('<tr>\
										<td>City:</td>\
										<td>' + data.city + '</td>\
									</tr>\
									<tr>\
										<td>Country:</td>\
										<td>' + data.country + '</td>\
									</tr>\
									<tr>\
										<td>Time:</td>\
										<td>' + normalize_date(data.time.split(" ")[0]) + ' ' + data.time.split(" ")[1].slice(0, 5) + '</td>\
									</tr>\
									<tr>\
										<td>Weather Main</td>\
										<td>' + data.weather[0].main + '</td>\
									</tr>\
									<tr>\
										<td>Weather Description</td>\
										<td>' + data.weather[0].description + '</td>\
									</tr>\
									<tr>\
										<td>Wind direction</td>\
										<td>' + data.wind.deg + '°</td>\
									</tr>\
									<tr>\
										<td>Wind speed</td>\
										<td>' + data.wind.speed + ' m/s</td>\
									</tr>\
									<tr>\
										<td>Wind gusts</td>\
										<td>' + data.wind.gust + ' m/s</td>\
									</tr>\
									<tr>\
										<td>Cloud Percent</td>\
										<td>' + data.cloudpercent + '%</td>\
									</tr>\
									<tr>\
										<td>Temperature</td>\
										<td>' + (Math.round((data.temp.current - 273.15) * 10) / 10).toFixed(1) + '°C</td>\
										<td>' + (Math.round((data.temp.max - 273.15) * 10) / 10).toFixed(1) + '°C</td>\
										<td>' + (Math.round((data.temp.min - 273.15) * 10) / 10).toFixed(1) + '°C</td>\
									</tr>');
	})
	.fail(function(data) {
		var msg = $(data.responseText).filter("p").html();
		$("#weather-current-error").text("Request for weather went wrong. Error code: " + data.status + ": " + msg);
		$("#weather-current-error").show();
	});

	$.get("http://127.0.0.1:5000/weather-forecast", {'url' : encodeURI(forecast), 'debugging' : 'true'}, function(data) {
		console.log("Got response from Forecast Weather API");
		$("#weather-forecast-error").hide();
		$("#weather-forecast").empty();
		var weather = data;
		if(weather.length == 0) $("#weather-forecast").text("No weather :(");
		
		for(var fc in data.forecasts) {
			console.log(data.forecasts[fc])
			var time = data.forecasts[fc].time.split(" ")[1]
			if(time == '12:00:00' || time == '15:00:00' || time == '18:00:00') {
				$("#weather-forecast").append('<tr>\
												<td>' + normalize_date(data.forecasts[fc].time.split(" ")[0]) + ' ' + data.forecasts[fc].time.split(" ")[1].slice(0, 5) + '</td>\
												<td>' + data.forecasts[fc].weather[0].main + '</td>\
												<td>' + data.forecasts[fc].wind.speed + ' m/s</td>\
												<td>' + (Math.round((data.forecasts[fc].temp.current - 273.15) * 10) / 10).toFixed(1) + '°C</td>\
											</tr>');
			}
			
		}
		
	})
	.fail(function(data) {
		var msg = $(data.responseText).filter("p").html();
		$(".widget-weather-error").text("Request for weather went wrong. Error code: " + data.status + ": " + msg);
		$(".widget-weather-error").show();
	})
}

function normalize_date(date) {
	var tokens = date.split('-');
	var year = parseInt(tokens[0]);
	var month = parseInt(tokens[1]) - 1;
	var day = parseInt(tokens[2]);

	return day + '. ' + MONTHS[month] + ' ' + year;
}

function round_to_two(num) {  
    return +(Math.round(num + "e+2")  + "e-2");
}
