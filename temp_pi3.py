import time
import argparse
from decimal import Decimal
from time import localtime, strftime

parser = argparse.ArgumentParser(conflict_handler='resolve')
parser.add_argument('-rH', '--reset-hour', action='store_true', dest='hour', help='Reset min/max every hour', default=False)
parser.add_argument('-rD', '--reset-day', action='store_true', dest='day', help='Reset min/max every day', default=False)
parser.add_argument('-rM', '--reset-minute', action='store_true', dest='minute', help='Reset min/max every minute', default=False)
parser.add_argument('-lV', '--less-verbose', action='store_true', dest='less_verbose', help='printline only when min/max changes', default=False)
parser.add_argument('-d', '--delay', action='store', dest='delay', help='Delay between refresh', default=1)
options = parser.parse_args()

curr_hour = None
curr_day = None
curr_minute = None
min_temp = None
max_temp = None
temp = None


def setup():
    global curr_hour, curr_day, curr_minute
    curr_hour = strftime('%H', localtime())
    curr_day = strftime('%d', localtime())
    curr_minute = strftime('%M', localtime())


def read_temp():
    with open('/sys/class/thermal/thermal_zone0/temp', 'r') as temp_file:
        return round(Decimal(temp_file.readline()) / 1000, 1)


def check_reset():
    global curr_hour, curr_day, curr_minute, temp, min_temp, max_temp
    if options.hour is True:
        current = strftime('%H', localtime())
        if curr_hour != current:
            curr_hour = current
            return True
        else:
            return False

    if options.day is True:
        current = strftime('%d', localtime())
        if curr_day != current:
            curr_day = current
            return True
        else:
            return False

    if options.minute is True:
        current = strftime('%M', localtime())
        if curr_minute != current:
            curr_minute = current
            return True
        else:
            return False


if __name__ == '__main__':
    setup()
    temp = read_temp()

    min_temp = temp
    max_temp = temp

    while True:
        if check_reset():
            temp = read_temp()
            min_temp = temp
            max_temp = temp

        temp = read_temp()
        if temp < min_temp:
            min_temp = temp
            changed = True
        elif temp > max_temp:
            max_temp = temp
            changed = True
        else:
            changed = False

        if options.less_verbose is True:
            if changed is True:
                print(strftime('%Y-%m-%d %H:%M:%S', localtime()), 'min_temp:', min_temp, 'max_temp:', max_temp,
                      'curr_temp:', temp)
            elif changed is False:
                print(strftime('%Y-%m-%d %H:%M:%S', localtime()), 'min_temp:', min_temp, 'max_temp:', max_temp,
                      'curr_temp:', temp, end='\r')
        elif options.less_verbose is False:
            print(strftime('%Y-%m-%d %H:%M:%S', localtime()), 'min_temp:', min_temp, 'max_temp:', max_temp,
                  'curr_temp:', temp)
        changed = False
        time.sleep(float(options.delay))
