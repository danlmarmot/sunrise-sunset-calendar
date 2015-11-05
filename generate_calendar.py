#!/usr/bin/env python3
from calendar import HTMLCalendar
import calendar
from datetime import date, datetime, timedelta
import ephem
import pytz
import argparse


def main():
    args = parse_args()

    start_date, end_date = get_daterange(args.year)
    location = get_location(args.location)
    time_zone = get_timezone(args.timezone)

    sun_times_dict = create_sunrise_sunset_table(start_date, end_date, location, time_zone)
    write_calendar(sun_times_dict)


def parse_args():
    description_str = """
    Generates a calendar of sunrise and sunset times for a given location, year, and time zone.
    """

    parser = argparse.ArgumentParser(description=description_str)
    parser.add_argument('-l', '--loc', action="store_true", dest='location',
                        default="32.7,-117.1",
                        help="location as lat,long.  Default: 32.7,-117.1")
    parser.add_argument('-y', '--year', action="store_true", dest='year',
                        default=str(datetime.now().year),
                        help="year.  Default: the current year, " + str(datetime.now().year))
    parser.add_argument('-z', '--tz', action="store_true", dest='timezone',
                        default="US/Pacific",
                        help="timezone.  Default: US/Pacific")

    return parser.parse_args()


def get_daterange(year):
    start_date = date(int(year), 1, 1)
    end_date = date(int(year), 12, 31)
    return start_date, end_date


# noinspection PyUnresolvedReferences
def get_location(latlong):
    loc = ephem.Observer()
    loc.lat = latlong.split(",")[0]
    loc.lon = latlong.split(",")[1]
    loc.elevation = 0
    loc.pressure = 0

    # This adjustment is for atmospheric refraction, to keep this output inline with US Naval Obeservatory
    # More here: http://rhodesmill.org/pyephem/rise-set.html#naval-observatory-risings-and-settings
    loc.horizon = '-0:34'

    return loc


def get_timezone(timezone_name):
    return pytz.timezone(timezone_name)


def create_sunrise_sunset_table(start_date, end_date, location, local_time_zone, use_local_time=True):
    # Dictionary format is  {yy-mm-dd: {sunrise: UTC_time, sunset: UTC_time}}
    sun_times_dict = dict()

    for d in date_range(start_date, end_date):
        # Ephem module works in UTC; need to look for a sunrises/sets after a UTC time, not local midnight
        # Localize with the time_zone object from pytz to account for Daylight Savings Time
        local_midnight_utc = local_time_zone.localize(datetime(d.year, d.month, d.day, 0, 0, 0))

        # Convert local midnight explicitly to UTC, add to the location
        location.date = local_midnight_utc.astimezone(pytz.utc)

        # Get sunrise/sunset times as UTC
        sunrise = location.next_rising(ephem.Sun()).datetime().replace(tzinfo=pytz.utc)
        sunset = location.next_setting(ephem.Sun()).datetime().replace(tzinfo=pytz.utc)

        # Convert to local time (default is true)
        if use_local_time:
            sunrise = sunrise.astimezone(local_time_zone)
            sunset = sunset.astimezone(local_time_zone)

        sun_times_dict[d.strftime("%Y-%m-%d")] = {
            'sunrise': sunrise,
            'sunset': sunset
        }

    return sun_times_dict


def write_calendar(sun_times_dict):
    sun_cal = SunCalendar(
        firstweekday=calendar.SUNDAY,
        theyear=2015,
        sun_times_dict=sun_times_dict,
        css="calendar.css")
    html_out = sun_cal.formatyearpage(2015)
    print(html_out)

    with open("sun_calendar.html", 'w') as f:
        f.write(html_out.decode(encoding='UTF-8'))


def date_range(start_date, end_date):
    for n in range((end_date - start_date).days + 1):
        yield start_date + timedelta(n)


class SunCalendar(HTMLCalendar):
    def __init__(self, firstweekday, theyear, sun_times_dict=None, css=""):
        super(SunCalendar, self).__init__(firstweekday)
        self.theyear = theyear
        self.sun_times_dict = sun_times_dict
        self.css = css
        self.themonth = None

    def add_calendar_header(self):
        v = []
        a = v.append
        if self.css is not None:
            a('<link rel="stylesheet" type="text/css" href="%s" />' % self.css)
        a('\n\n<table class="titleTable" width="100%" cellPadding=4>\n')    # todo: pull the CSS out into calendar.css
        a('<tbody><tr>')
        a('\n<td class=titleCell>Sunrise/Sunset Calendar for %d</td>\n' % self.theyear)
        a('</tr></tbody>\n</table>\n\n')
        return ''.join(v)

    def formatday(self, day, weekday):
        if day == 0:
            return '<td class="emptyDayCell"></td>\n'  # day not in current month

        k = str(self.theyear) + '-' + ('00' + str(self.themonth))[-2:] + '-' + ('00' + str(day))[-2:]

        if k not in self.sun_times_dict:
            return '<td class="dayCell">%d</td>\n' % day

        sunrise = self.sun_times_dict[k]['sunrise']
        sunset = self.sun_times_dict[k]['sunset']

        # Format, stripping leading zeros and forcing AM/PM to am/pm
        time_format = "%I:%M%p"
        sunrise_str = sunrise.strftime(time_format).lstrip('0').lower()
        sunset_str = sunset.strftime(time_format).lstrip('0').lower()

        v = []
        a = v.append
        a('<td class="dayCell">%d<br>' % day)
        a('<span class="sunrise">%s</span><br>' % sunrise_str)
        a('<span class="sunset">%s</span>' % sunset_str)
        a('</td>\n')
        return ''.join(v)

    def formatmonthname(self, theyear, themonth, withyear=True):
        return '<tr><td colspan="7" class="currentMonth">%s</td>\n</tr>\n' % calendar.month_name[themonth]

    def formatmonth(self, theyear, themonth, withyear=True):
        v = []
        a = v.append
        a('<table class="monthCalendar" width="100%">')         # todo: pull the styling out into calendar.css

        a(self.formatmonthname(self.theyear, themonth=themonth, withyear=withyear))
        a(self.formatweekheader())
        a('\n')
        for week in self.monthdays2calendar(self.theyear, themonth):
            self.themonth = themonth
            a(self.formatweek(week))

        a('</table>\n')
        return ''.join(v)

    def formatyear(self, theyear, width=3):
        v = []
        a = v.append
        a(self.add_calendar_header())
        a('<table class="annualCalendar" width="100%">\n')      # todo: pull the CSS out into calendar.css
        for i in range(calendar.January, calendar.January + 12, max(width, 1)):
            months = range(i, min(i + width, 13))
            a('<tr>')
            for m in months:
                a('\n\n<td class="monthCell">\n')
                a(self.formatmonth(theyear, m, withyear=False))
                a('</td>\n')
            a('</tr>\n')
        a('</table>\n')
        return ''.join(v)

    def formatweekday(self, day):
        return '<td class="weekdayName">%s</td>\n' % (calendar.day_abbr[day][0])


if __name__ == '__main__':
    main()
