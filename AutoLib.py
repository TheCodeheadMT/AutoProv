"""
This software project was created in 2017 by the U.S. Federal government.
See INTENT.md for information about what that means. See CONTRIBUTORS.md and
LICENSE.md for licensing, copyright, and attribution information.

Copyright 2017 U.S. Federal Government (in countries where recognized)
Copyright 2017 Ryan Good and Gilbert Peterson

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import Meta
import TimelineEntry
import Users
import Timestamp
import WindowsInfo

"""Input: The name of a file
   Output: The type of a file"""
def find_file_type(file):
    handledtypes = ('docx', 'xxxfillerxxx')
    filetype = "Not handled"
    for type in handledtypes:
        if type in file:
            filetype = type
    return filetype

"""Input: None
   Output: The start block of the NTFS partition of an image."""
def parse_mmls(filename):
    mmls = open("%s/mmlsoutput.txt" % filename, "r")
    start_block = 0
    for line in range(5): #Skip the first 5 lines
        mmls.next()
    for line in mmls: #Find start block of interest
        splitLine = line.split()
        for word in splitLine:
            if (word == "NTFS") and (start_block == 0):
                start_block = splitLine[2]
    return start_block

"""Input: metadata object
   Output: None, modifies metadata object"""
def parse_meta(metadata, filename):
    metatext = open("%s/meta.txt" % filename, "r")
    for line in metatext:
        line = line.rstrip()
        lsplit = line.split(":")
        l2split = line.split(" ")
        while '' in l2split:
            l2split.remove('')
        if "Creator" in line:
            creator = lsplit[1].lstrip()
            metadata.creator = creator
        if "Author" in line:
            author = lsplit[1].lstrip()
            metadata.author = author
        if "Last Modified By" in line:
            modifier = lsplit[1].lstrip()
            metadata.modifier = modifier
        if "Create Date" in line:
            year = lsplit[1].lstrip()
            month = lsplit[2].replace("0", "")
            day = lsplit[3].replace("0", "")
            day = day.split(" ") #strip out extra stuff
            day = day[0]
            date = "%s:%s:%s" % (year, month, day)
            date = remove_extra_zeros_date(date)
            metadata.created_date = date

            time = l2split[4]
            time = time.replace("Z", "")
            timesplit = time.split(":")
            hours = timesplit[0]
            minutes = timesplit[1]
            seconds = timesplit[2]
            time = "%s:%s:%s" % (hours, minutes, seconds)
            time = remove_extra_zeros_time(time)
            metadata.created_time = time
        if "Modify Date" in line:
            year = lsplit[1].lstrip()
            month = lsplit[2].replace("0", "")
            day = lsplit[3].replace("0", "")
            day = day.split(" ")  # strip out extra stuff
            day = day[0].rstrip()
            date = "%s:%s:%s" % (year, month, day)
            date = remove_extra_zeros_date(date)
            metadata.modification_date = date

            time = l2split[4]
            time = time.replace("Z", "")
            timesplit = time.split(":")
            hours = timesplit[0]
            minutes = timesplit[1]
            seconds = timesplit[2]
            time = "%s:%s:%s" % (hours, minutes, seconds)
            time = remove_extra_zeros_time(time)
            metadata.modification_time = time

def remove_extra_zeros_time(time):
    # Remove extra zeros for comparison compatibility
    timesplit = time.split(":")
    hours = timesplit[0]
    if hours[0] == '0':
        hours = hours[1]
    minutes = timesplit[1]
    if minutes[0] == '0':
        minutes = minutes[1]
    seconds = timesplit[2]
    if seconds[0] == '0':
        seconds = seconds[1]
    time = "%s:%s:%s" % (hours, minutes, seconds)
    return time

def remove_extra_zeros_date(date):
    datesplit = date.split(":")
    month = datesplit[1]
    day = datesplit[2]
    if month[0] == '0':
        month = month[1]
    if day[0] == '0':
        day = day[1]
    newdate = "%s:%s:%s" % (datesplit[0], month, day)
    return newdate

""" Input: An entry from log2timeline
    Output: A TimelineEntry class containing the parsed information"""
def create_entry(entry, Timeline):
    parsed_entry = entry.split(',')
    date_time = parsed_entry[0].split('T')
    timelinedate = date_time[0].replace('-', ':')
    timelinedate = remove_extra_zeros_date(timelinedate)
    Timeline.date = timelinedate
    if '.' in date_time[1]:
        badchar = date_time[1].index('.')#Find index of decimal in time
    if '+' in date_time[1]:
        badchar = date_time[1].index('+')#Find index of plus sign in time
    time = date_time[1]
    time = time[:badchar] #Remove everything after decimal
    Timeline.time = remove_extra_zeros_time(time)

    Timeline.time_description = parsed_entry[1]
    Timeline.source = parsed_entry[2]
    Timeline.long_source = parsed_entry[3]
    Timeline.message = parsed_entry[4]
    Timeline.parser = parsed_entry[5]
    Timeline.display_name = parsed_entry[6]
    Timeline.tag = parsed_entry[7]
    Timeline.store_number = parsed_entry[8]
    Timeline.store_index = parsed_entry[9]
    return Timeline

def samDateTime(timedatemix):
    monthdictionary = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7,
                       'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    mix = timedatemix[1] #this has hours in it as well unfortunately, and no year. more complex parsing.
    secondsyear = timedatemix[3] #contains seconds and the year
    secondsyear = secondsyear.split(" ")
    year = secondsyear[1]
    mix = mix.split(" ")
    month = monthdictionary[mix[2]]
    day = mix[3]
    date = "%s:%s:%s" % (year, month, day)

    hours = mix[4]
    minutes = timedatemix[2]
    seconds = secondsyear[0]
    time = "%s:%s:%s" % (hours, minutes, seconds)

    datetime = [date, time]
    return datetime

def getUsers(samparse):
    users = []
    for line in samparse:
        if "Username" in line:
            #Get usernames
            user = Users.User()
            username = line.split(":")
            username = username[1]
            username = username.lstrip().rstrip()
            username = username.split(" ")
            username = username[0]
            user.username = username

            #Get account type
            samparse.next()
            samparse.next()
            type = samparse.next()
            type = type.split(":")
            type = type[1]
            type = type.lstrip().rstrip()
            user.account_type = type

            #Get created date/time
            account_created = samparse.next()
            account_created = account_created.split(":")
            datetime = samDateTime(account_created)
            user.account_created_date = datetime[0]
            user.account_created_time = datetime[1]

            samparse.next()
            lastlogin = samparse.next()
            if "Never" in lastlogin:
                user.last_login_date = "Never"
                user.last_login_time = "Never"
            else:
                lastlogin = lastlogin.split(":")
                datetime = samDateTime(lastlogin)
                user.last_login_date = datetime[0]
                user.last_login_time = datetime[1]

            users.append(user)
    return users

def timestampfix(line):
    datetime = []
    linesplit = line.split(" ")
    date = linesplit[1]
    date = date.replace("-", ":")
    date = remove_extra_zeros_date(date)
    datetime.append(date)

    time = linesplit[2]
    timesplit = time.split(".")
    time = timesplit[0]
    time = remove_extra_zeros_time(time)
    datetime.append(time)

    offset = linesplit[3]
    datetime.append(offset)
    return datetime

def offsetfix(time, offset, date):
    time_split = time.split(":")
    hours = time_split[0]
    sign = offset[0]
    offset = offset[1:3]
    if offset[0] == '0':
        offset = offset[1]
    if sign == '-':
        hours = int(hours) + int(offset)
    elif sign == '+':
        hours = int(hours) - int(offset)

    if hours > 24:
        hours = hours - 24
        date_split = date.split(":")
        day = date_split[1]
        day = int(day) + 1
        date = "%s:%s:%s" % (date_split[0], str(day), date_split[2])
    elif hours < 0:
        hours = 24 + hours
        date_split = date.split(":")
        day = date_split[1]
        day = int(day) - 1
        date = "%s:%s:%s" % (date_split[0], str(day), date_split[2])
    time = "%s:%s:%s" % (str(hours), time_split[1], time_split[2])
    return [time, date]

def parsetimestamps(timestamps, timefile):
    for line in timefile:
        if ("Access" in line) and ("Uid" not in line):
            datetime = timestampfix(line)
            atime_date = datetime[0].rstrip()
            atime_time = datetime[1]
            offset = datetime[2]
            result = offsetfix(atime_time, offset, atime_date)
            timestamps.atime_date = result[1]
            timestamps.atime_time = result[0]
        if "Modify" in line:
            datetime = timestampfix(line)
            mtime_date = datetime[0].rstrip()
            mtime_time = datetime[1]
            offset = datetime[2]
            result = offsetfix(mtime_time, offset, mtime_date)
            timestamps.mtime_date = result[1]
            timestamps.mtime_time = result[0]
        if "Change" in line:
            datetime = timestampfix(line)
            ctime_date = datetime[0].rstrip()
            ctime_time = datetime[1]
            offset = datetime[2]
            result = offsetfix(ctime_time, offset, ctime_date)
            timestamps.ctime_date = result[1]
            timestamps.ctime_time = result[0]

def parseWinInfo(wininfo, winfile):
    monthdictionary = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7,
                       'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
    for line in winfile:
        lsplit = line.split("=")
        if "ProductName" in line:
            productname = lsplit[1]
            productname = productname.rstrip().lstrip()
            wininfo.productname = productname
        if "CSDVersion" in line:
            version = lsplit[1]
            version = version.rstrip().lstrip()
            wininfo.csdVersion = version
        if "InstallDate" in line:
            installdate = lsplit[1]
            installdate = installdate.rstrip().lstrip()
            tsplit = installdate.split(" ")
            month = tsplit[1]
            day = tsplit[2]
            year = tsplit[4]
            month = monthdictionary[month]
            time = tsplit[3]
            date = "%s:%s:%s" % (year, month, day)
            wininfo.installdate = date
            wininfo.installtime = time

def editcheck(mtime_date, mtime_time, arriv_date, arriv_time):
    mdatesplit = mtime_date.split(":")
    mtimesplit = mtime_time.split(":")
    arrdatesplit = arriv_date.split(":")
    arrtimesplit = arriv_time.split(":")

    myear = int(mdatesplit[0])
    mmonth = int(mdatesplit[1])
    mday = int(mdatesplit[2])
    mhour = int(mtimesplit[0])
    mminute = int(mtimesplit[1])

    arryear = int(arrdatesplit[0])
    arrmonth = int(arrdatesplit[1])
    arrday = int(arrdatesplit[2])
    arrhour = int(arrtimesplit[0])
    arrminute = int(arrtimesplit[1])

    if myear < arryear:
        return False
    if mmonth < arrmonth:
        return False
    if mday < arrday:
        return False
    if mhour < arrhour:
        return False
    if mminute < arrhour:
        return False


def timecheck(date_a, time_a, date_b, time_b, arriv_date, arriv_time):
    movement = False
    atimesplit = time_a.split(":")
    btimesplit = time_b.split(":")
    ahours = int(atimesplit[0])
    aminutes = int(atimesplit[1])
    bhours = int(btimesplit[0])
    bminutes = int(btimesplit[1])

    adatesplit = date_a.split(":")
    bdatesplit = date_b.split(":")
    ayear = int(adatesplit[0])
    amonth = int(adatesplit[1])
    aday = int(adatesplit[2])
    byear = int(bdatesplit[0])
    bmonth = int(bdatesplit[1])
    bday = int(bdatesplit[2])

    darriv_split = arriv_date.split(":")
    tarriv_split = arriv_time.split(":")
    arriv_year = int(darriv_split[0])
    arriv_month = int(darriv_split[1])
    arriv_day = int(darriv_split[2])
    arriv_hour = int(tarriv_split[0])
    arriv_minute = int(tarriv_split[1])

    #Check if all relevant dates/times are equal to or beyond arrival time
    if ((ayear >= arriv_year) and (byear >= arriv_year) and (amonth >= arriv_month) and (bmonth >= arriv_month) and
            (aday >= arriv_day) and (bday >= arriv_day) and (ahours >= arriv_hour) and (bhours >= arriv_hour) and
            (aminutes >= arriv_minute) and (bminutes >= arriv_minute)):
        #check for movement
        if date_a != date_b:
            movement = True
        elif ahours != bhours:
            movement = True
        elif (aminutes > bminutes) or (aminutes < bminutes):
            movement = True
    return movement

def get_chrome_visit(visit, offset):
    visit_split = visit.split(":", 1)
    visit = visit_split[1]
    visit_split = visit.split(" ")
    visit_date = visit_split[1]
    visit_time = visit_split[2]
    visit_mod = visit_split[3].rstrip().lstrip()
    visit_time_split = visit_time.split(":")
    hours = visit_time_split[0]
    hours = int(hours)
    if visit_mod == "PM": #increment by 12 hours to put in mil time
        hours = hours + 12
        if hours == 24:
            hours = 12
    elif (visit_mod == "AM") and (int(hours) == 12):
        hours = 0

    hours = hours + offset
    if hours > 24:
        hours = hours - 24
    hours = str(hours)
    visit_time = "%s:%s:%s" % (hours, visit_time_split[1], visit_time_split[2])

    visit_date = visit_date.replace("/", ":")
    visit_date_split = visit_date.split(":")
    month = visit_date_split[0]
    day = visit_date_split[1]
    year = visit_date_split[2]
    visit_date = "%s:%s:%s" % (year, month, day)

    return [visit_date, visit_time]

def isGreater(entry, current):
    if entry.year > current.year:
        return True
    if entry.year < current.year:
        return False
    if entry.month > current.month:
        return True
    if entry.month < current.month:
        return False
    if entry.day > current.day:
        return True
    if entry.day < current.day:
        return False
    if entry.hour > current.hour:
        return True
    if entry.hour < current.hour:
        return False
    if entry.minute > current.minute:
        return True
    if entry.minute < current.minute:
        return False
    if entry.second > current.second:
        return True
    if entry.second < current.second:
        return False
    else:
        return True


def insertEvent(eventHead, entry):
    if not eventHead:
        eventHead = entry
    else:
        current = eventHead
        while current is not None:
            if isGreater(entry, current):
                if current.next is not None:
                    current = current.next
                elif current.next == None:
                    current.next = entry
                    entry.prev = current
                    break
            else:
                prev = current.prev
                if prev is None:
                    current.prev = entry
                    entry.next = current
                    eventHead = entry
                else:
                    prev.next = entry
                    entry.prev = prev
                    entry.next = current
                    current.prev = entry
                break

    return eventHead

def printEvents(eventHead):
    current = eventHead
    while current is not None:
        print current.description
        current = current.next