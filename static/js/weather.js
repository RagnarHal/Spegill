var weather = {
	'update_interval' : 30*60*1000,
	'api' : 'http://api.openweathermap.org/data',
	'api_version' : '2.5',
	'weather' : 'weather',
	'forecast' : 'forecast',
	'city_id' : '3413829',
	'appid' : '2de143494c0b295cca9337e1e96b00e0'
};

weather.init = function() {
	this.update_weather();
	this.update_forecast();

	setInterval(function() {
		this.update_weather();
		this.update_forecast();
	}.bind(this), this.update_interval);
}

weather.update_weather = function() {
	var url = weather.api + '/' + weather.api_version + '/' + weather.weather + '?id=' + weather.city_id + '&appid=' + weather.appid;
	console.log(url);
	$.get("http://127.0.0.1:5000/weather", {'url' : encodeURI(url), 'debugging' : 'true'}, function(data) {
		console.log("Got response from current weather API");
		$("#weather-current-error").hide();
		$("#weather-current").empty();

		if (data.length == 0) $("#weather-current").text("No weather :(");

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
										<td>Weather Icon</td>\
										<td><i class="wi wi-owm-' + data.weather[0].id + '"></i></td>\
									</tr>\
									<tr>\
										<td>Weather Description</td>\
										<td>' + data.weather[0].description + '</td>\
									</tr>\
									<tr>\
										<td>Wind direction</td>\
										<td>' + Math.round(data.wind.deg) + '°</td>\
									</tr>\
									<tr>\
										<td>Wind direction Icon</td>\
										<td><i class="wi wi-wind towards-' + Math.round(data.wind.deg) + '-deg"></i></td>\
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
};

weather.update_forecast = function() {
	var url = weather.api + '/' + weather.api_version + '/' + weather.forecast + '?id=' + weather.city_id + '&appid=' + weather.appid;
	console.log(url);

	$.get("http://127.0.0.1:5000/forecast", {'url' : encodeURI(url), 'debugging' : 'true'}, function(data) {
		$("#weather-forecast-error").hide();
		$("#weather-forecast").empty();

		if(data.length == 0) $("#weather-forecast").text("No weather :(");

		for(var i in data.forecasts) {
			var fc = data.forecasts[i];
			var time = fc.time.split(" ")[1]

			if(time == '12:00:00' || time == '15:00:00' || time == '18:00:00') {
				$("#weather-forecast").append('<tr>\
												<td>' + normalize_date(fc.time.split(" ")[0]) + ' ' + fc.time.split(" ")[1].slice(0, 5) + '</td>\
												<td>' + fc.weather[0].main + '</td>\
												<td>' + fc.wind.speed + ' m/s</td>\
												<td>' + (Math.round((fc.temp.current - 273.15) * 10) / 10).toFixed(1) + '°C</td>\
											</tr>');
			}
		}
	})
	.fail(function(data) {
		var msg = $(data.responseText).filter("p").html();
		$(".widget-forecast-error").text("Request for weather went wrong. Error code: " + data.status + ": " + msg);
		$(".widget-forecast-error").show();
	})
};