## sunrise-sunset-calendar

This is a short script to generate an HTML calendar of sunrise and sunset times for a given location.

### To get started

These instructions have been tested on a Mac running OS X 11 (El Capitan)

1.  Install Python 3.5
2.  Clone this repository
3.  Open a terminal window, and create the Python virtual environment for this project with these commands:

``` 
    pyvenv venv
    . venv/bin/activate
    pip install -r requirements.txt
```
   
### Running the script.

1.  Run the script with this command:

    ./generate_calendar.py
    
1.  Open the resulting HTML file in a browser.

### Customizing the calendar

The script defaults to a given location, year, and time zone, and accepts command line arguments.  Run the script with
the -h command for more info on changing these defaults:

    ./generate_calendar.py -h

#### Location
Specify a custom location with a string in the form of 'lat,long'.  

#### Year
Specify a year just by entering the year, such as 2015.  The default is the current year.

#### Time zone
Time zone can be customized by entering the time zone name, such as 'US/Pacific' that's recognized by the pytz module.
This is used to account for Daylight Savings Time or Summer Time.
