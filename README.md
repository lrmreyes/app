# Project 1

Web Programming with Python and JavaScript

This project allows a user to register, login, and logout of a website.
While logged in, a user can search a city or zipcode, and pull up information
about that location, as well as the weather in that location.
The user can also check-in and comment at each location once.
Comments left for that location will appear at the bottom of the page.

Contents:
application.py - logic for the entire website
import.py - imports information about the location from a csv to the database

Templates:
index.html - homepage, contains a search bar
location.html - displays all the information about the location selected
login.html - register and login page
search.html - displays search results, with links to location pages
template.html - contains navbar, displays errors/successes flashed

Styles:
Bootstrap 4
style.css (in static/styles) - some basic css
Font Awesome - for umbrella and search logo

favicon.ico - icon for the title
requirements.txt - requirements
zips.csv - locations info
ddc5qk69cvs493.sql - database