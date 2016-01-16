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
	$.get("http://" + location.host + "/weather", function(data) {
		console.log("Got response from current weather API");
		$("#weather-current-error").hide();

		var hour = (data.time.split(" ")[1].split(":")[0]);
		var day = (06 <= hour && hour <= 18) ? 'day' : 'night';

		$("#weather-icon").empty().html('<i class="wi wi-owm-' + day + '-' + data.weather[0].id + '"></i>');
		$("#weather-icon").append('<div id="weather-desc">' + data.weather[0].main + '</div>');
		$("#weather-temp").text((Math.round((data.temp.current - 273.15) * 10) / 10).toFixed(1) + '°C');
	})
	.fail(function(data) {
		var msg = $(data.responseText).filter("p").html();
		$("#weather-current-error").text("Request for weather went wrong. Error code: " + data.status + ": " + msg);
		$("#weather-current-error").show();
	});
};

weather.update_forecast = function() {
	$.get("http://" + location.host + "/forecast", function(data) {
		console.log("Got response from forecast weather API");
		$("#weather-forecast-error").hide();

		var forecast = data.forecasts.filter(function(e) {
			return e.time.split(" ")[1] === '12:00:00';
		});

		//$("#weather-forecast").empty();

		var day_row = '<tr>';
		var icon_row = '<tr>';
		var temp_row = '<tr>';

		forecast.forEach(function(e) {
			day_row += '<td class="sup">' + WEEKDAYS[new Date(e.time.split(" ")[0]).getDay()] + '</td>';
			icon_row += '<td><i class="wi wi-owm-' + e.weather[0].id + '"></i></td>';
			temp_row += '<td class="sup">' + (Math.round((e.temp.current - 273.15) * 10) / 10).toFixed(0) + '°</td>';
		});

		day_row += '</tr>';
		icon_row += '</tr>';
		temp_row += '</tr>';

		$("#weather-forecast").empty();
		$("#weather-forecast").html('<table>' + day_row + icon_row + temp_row + '</table>');
	})
	.fail(function(data) {
		var msg = $(data.responseText).filter("p").html();
		$(".widget-forecast-error").text("Request for weather went wrong. Error code: " + data.status + ": " + msg);
		$(".widget-forecast-error").show();
	})
};