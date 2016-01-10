var clock = {
	'update_interval' : 1000,
	'location' : '.clock'
};

clock.init = function() {
	this.update();
	setInterval(function() {
		this.update();
	}.bind(this), this.update_interval);
};

clock.update = function() {
	$(this.location).text(this.now().slice(0, 5));
};

clock.now = function() {
	var d = new Date();
	return (('0'+d.getHours()).slice(-2) + ':' + ('0'+d.getMinutes()).slice(-2) + ':' + ('0'+d.getSeconds()).slice(-2));
};

clock.today = function() {
	d = new Date();
	yyyy = d.getFullYear();
	mm = ('0' + d.getMonth() + 1).slice(-2);
	dd = ('0' + d.getDate()).slice(-2);
	return (yyyy + '-' + mm + '-' + dd);
};

clock.datetime = function() {
	return (this.today() + ' ' + this.now());
};