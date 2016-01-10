# Spegill

## Introduction
My take on the Magic Mirror project. Unlike [MichMich's original implementation](https://github.com/MichMich/MagicMirror) (although heavily inspired by it), this project is intended to be runnable as a standalone application, requiring no external web server to run. The ultimate goal is to allow a user to simply install this application on a Raspberry Pi (or other platforms), run it and immediately be able to access the interface from any device on the local network, also offering a user-friendly and intuitive way to customize the mirror to suit anyone's needs.

## Description
The web server is written in Python using the awesome [Flask](http://flask.pocoo.org/) microframework. The client (browser) sends all requests for data to the local webserver, who in turns fetches the data from the specified APIs, sorts, parses and aggregates the required data, and returns a simple JSON string back to the client to display to the user.

## Modules used in project
* [Flask](http://flask.pocoo.org/)
* [iCalendar parser library for Python](https://github.com/collective/icalendar/)
* [Requests: HTTP for Humans](http://docs.python-requests.org/en/latest/)
* [Bootstrap](http://getbootstrap.com/css/)
* [JQuery](https://jquery.com/)
* [Weather Icons by Erik Flowers](https://erikflowers.github.io/weather-icons/)