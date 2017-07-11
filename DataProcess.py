"""
Copyright 2017 Air Force Institute of Technology

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
import AutoLib
import argparse
import TimelineEntry
import USB
import Users
import Timestamp
import WindowsInfo
import InternetHist
import subprocess
import Event
from pathlib import Path

parser = argparse.ArgumentParser(description='This program automatically finds provenance related to a file on an image')
parser.add_argument("folder", help="Folder of interest created by DataGather.py")
args = parser.parse_args()

threshold = 30  # 30 minute threshold

eventHead = None
filename = ""

print "All times are presented in UTC\n"

#Process metadata
with open('%s/namelocation.txt' % args.folder, 'r') as namelocationfile:
    filename = namelocationfile.next()
    filename = filename.rstrip()
    location = namelocationfile.next()
    metadata = Meta.Meta(filename, location)
    AutoLib.parse_meta(metadata, filename)

    if metadata.created_date != "None provided":
        createdEvent = Event.Event()
        date = metadata.created_date
        time = metadata.created_time
        datesplit = date.split(":")
        timesplit = time.split(":")
        createdEvent.year = int(datesplit[0])
        createdEvent.month = int(datesplit[1])
        createdEvent.day = int(datesplit[2])
        createdEvent.hour = int(timesplit[0])
        createdEvent.minute = int(timesplit[1])
        if '+' in timesplit[2]:
            ttimesplit = timesplit[2].split("+")
            timesplit[2] = ttimesplit[0]
        createdEvent.second = int(timesplit[2])
        createdEvent.description = "***%s Created*** (Date: %s, Time: %s)" % (filename, date, time)
        eventHead = AutoLib.insertEvent(eventHead, createdEvent)

    if metadata.modification_date != "None provided":
        modifiedEvent = Event.Event()
        date = metadata.modification_date
        time = metadata.modification_time
        datesplit = date.split(":")
        timesplit = time.split(":")
        modifiedEvent.year = int(datesplit[0])
        modifiedEvent.month = int(datesplit[1])
        modifiedEvent.day = int(datesplit[2])
        modifiedEvent.hour = int(timesplit[0])
        modifiedEvent.minute = int(timesplit[1])
        if '+' in timesplit[2]:
            ttimesplit = timesplit[2].split("+")
            timesplit[2] = ttimesplit[0]
        modifiedEvent.second = int(timesplit[2])
        modifiedEvent.description = "***%s Modified*** (Date: %s, Time: %s)" % (filename, date, time)
        eventHead = AutoLib.insertEvent(eventHead, modifiedEvent)

if (metadata.creator != metadata.modifier) and (metadata.modifier != "None provided") and (metadata.modifier != metadata.author):
    print "File was modified by someone other than the creator"
    print "Modifier = %s\n" % (metadata.modifier)

#Check for torrent
torrentfile = False
with open('%s/namelocation.txt' % args.folder, 'r') as namelocationfile:
    for line in namelocationfile:
        if "torrent" in line:
            torrentfile = True

filetype = AutoLib.find_file_type(filename)

#Parse Timezone info
bias = 0
with open('%s/timezone.txt' % args.folder, 'r') as timezonefile:
    for line in timezonefile:
        if "ActiveTimeBias" in line:
            line_split = line.split(">")
            bias = line_split[1]
            bias = bias.lstrip()
            bias_split = bias.split(" ", 1)
            bias = bias_split[0].rstrip()
            bias = int(bias)

            bias = bias / 60 #convert to hours

#Get local machine bias
lmbias = subprocess.Popen(['date', '+%z'], stdout=subprocess.PIPE)
lmbias = lmbias.stdout.read()
lmbias = lmbias.rstrip() #strip white space
lmbias = lmbias.replace("0", "")
lmbias = lmbias.replace("-", "")
lmbias = int(lmbias)
#Parse wininfo
with open('%s/wininfo.txt' % filename, 'r') as winfile:
    wininfo = WindowsInfo.WindowsInfo()
    AutoLib.parseWinInfo(wininfo, winfile)

#check for user match
users = open('%s/users.txt' % filename, 'r')
systemuser = False
for user in users:
    user = user.rstrip()
    if metadata.creator == user or metadata.author == user:
        systemuser = True

systemmod = False
for user in users:
    user = user.rstrip()
    if metadata.modifier == user:
        systemmod = True

users = open('%s/users.txt' % filename, 'r')
userlist = []
for line in users:
    line = line.rstrip()
    userlist.append(line)

#Parse timestamps
with open('%s/timefile.txt' % filename, 'r') as timefile:
    timestamps = Timestamp.Timestamp()
    AutoLib.parsetimestamps(timestamps, timefile)

################################
"""timeline processing"""
################################

    #Process NTUSER Timeline data
ntuser_relevant_entries = []
with open('%s/timeline1.txt' % args.folder, 'r') as ntuser_timeline:
    for line in ntuser_timeline:
        if filename in line:
            timeline_entry = TimelineEntry.TimelineEntry(filename)
            ntuser_relevant_entries.append(AutoLib.create_entry(line, timeline_entry)) #Relevant entries found with ntuser filter

execute = []
with open('%s/timeline1.txt' % args.folder, 'r') as ntuser_timeline:
  for line in ntuser_timeline:
    if "winreg/userassist" in line:
      timeline_entry = TimelineEntry.TimelineEntry(filename)
      execute.append(AutoLib.create_entry(line, timeline_entry))

for e in execute:
  message = e.message
  msplit = message.split(" ", 1)
  soft = msplit[1]
  #ssplit = soft.split(":", 1)
  #soft = ssplit[1]
  if e.date == ntuser_relevant_entries[0].date:
    etime = e.time
    firsttime = ntuser_relevant_entries[0].time
    esplit = etime.split(":")
    ftsplit = firsttime.split(":")
    ehour = int(esplit[0])
    fthour = int(ftsplit[0])
    if (ehour > fthour - 6) and (ehour < fthour + 6):
        if "%csidl2%" not in soft:
            exevent = Event.Event()
            date = e.date
            time = e.time
            datesplit = date.split(":")
            timesplit = time.split(":")
            exevent.year = int(datesplit[0])
            exevent.month = int(datesplit[1])
            exevent.day = int(datesplit[2])
            exevent.hour = int(timesplit[0])
            exevent.minute = int(timesplit[1])
            second = timesplit[2]
            second = second[:2]
            exevent.second = int(second)
            exuser = ""
            for u in userlist:
                if u in e.display_name:
                    exuser = u
            exevent.description = "%s is executed by %s (Date: %s, Time: %s)" % (soft, exuser, date, time)
            eventHead = AutoLib.insertEvent(eventHead, exevent)

  if (e.date.rstrip() == metadata.modification_date) and (e.date != ntuser_relevant_entries[0].date):
    etime = e.time
    modtime = metadata.modification_time
    esplit = etime.split(":")
    modsplit = modtime.split(":")
    ehour = int(esplit[0])
    modhour = int(modsplit[0])
    if (ehour > modhour - 6) and (ehour < modhour + 6):
        if "%csidl2%" not in soft:
            exevent = Event.Event()
            date = e.date
            time = e.time
            datesplit = date.split(":")
            timesplit = time.split(":")
            exevent.year = int(datesplit[0])
            exevent.month = int(datesplit[1])
            exevent.day = int(datesplit[2])
            exevent.hour = int(timesplit[0])
            exevent.minute = int(timesplit[1])
            second = timesplit[2]
            second = second[:2]
            exevent.second = int(second)
            exuser = ""
            for u in userlist:
              if u in e.display_name:
                exuser = u
            exevent.description = "%s is executed by %s (Date: %s, Time: %s)" % (soft, exuser, date, time)
            eventHead = AutoLib.insertEvent(eventHead, exevent)

#Check for FrostWire usage
frostwire_entries = []
with open('%s/timeline1.txt' % args.folder, 'r') as ntuser_timeline:
    for line in ntuser_timeline:
        if ("FrostWire.exe" in line) and ("winreg/userassist" in line): #userassist = recently used
            timeline_entry = TimelineEntry.TimelineEntry(filename)
            frostwire_entries.append(AutoLib.create_entry(line, timeline_entry))

#Check for Skype usage
skype_entries = []
with open ('%s/timeline1.txt' % args.folder, 'r') as ntuser_timeline:
    for line in ntuser_timeline:
        if (("Skype.exe" in line) or ("Skype.lnk" in line)) and ("winreg/userassist" in line):
            timeline_entry = TimelineEntry.TimelineEntry(filename)
            skype_entries.append(AutoLib.create_entry(line, timeline_entry))

fwiredatematch1 = False
for fentry in frostwire_entries:
    if fentry.date == ntuser_relevant_entries[0].date:
        fwiredatematch1 = True

        '''fwevent = Event.Event()
        date = fentry.date
        time = fentry.time
        datesplit = date.split(":")
        timesplit = time.split(":")
        fwevent.year = int(datesplit[0])
        fwevent.month = int(datesplit[1])
        fwevent.day = int(datesplit[2])
        fwevent.hour = int(timesplit[0])
        fwevent.minute = int(timesplit[1])
        fwevent.second = int(timesplit[2])
        fwevent.description = "Frostwire is executed (Date: %s, Time: %s)" % (filename, date, time)
        eventHead = AutoLib.insertEvent(eventHead, fwevent)'''



#Check if created locally on using Word
word_entries = []
with open('%s/timeline1.txt' % args.folder, 'r') as ntuser_timeline:
    for line in ntuser_timeline:
        if ("WINWORD.EXE" in line):
            timeline_entry = TimelineEntry.TimelineEntry(filename)
            nentry = AutoLib.create_entry(line, timeline_entry)
            word_entries.append(nentry)

word_appear_day = False
word_create_day = False
word_modify_day = False
for wentry in word_entries:
    print wentry.date, ntuser_relevant_entries[0].date
    if wentry.date == ntuser_relevant_entries[0].date:
        word_appear_day = True

    if wentry.date == metadata.created_date:
        word_create_day = True

    if wentry.date == metadata.modification_date:
        word_modify_day = True


#Office/Recent and file name
officeinteract = False
for entry in ntuser_relevant_entries:
    if "Microsoft/Office" in entry.display_name:
        officeinteract = True

skypedatematch = False
skype30min = False
for sentry in skype_entries:
    if sentry.date == ntuser_relevant_entries[0].date:
        skypedatematch = True
        skype_split = sentry.time.split(":")
        skype_hours = int(skype_split[0])
        ntsplit = ntuser_relevant_entries[0].time.split(":")
        ntuser_hours = int(ntsplit[0])
        if skype_hours == ntuser_hours:
            skype_minutes = int(skype_split[1])
            nt_minutes = int(ntsplit[1])
            if (skype_minutes >= (nt_minutes - threshold)) and (skype_minutes <= (nt_minutes + threshold)):
                skype30min = True
                skypedatematch = False
        else:
            skyevent = Event.Event()
            date = sentry.date
            time = sentry.time
            datesplit = date.split(":")
            timesplit = time.split(":")
            skyevent.year = int(datesplit[0])
            skyevent.month = int(datesplit[1])
            skyevent.day = int(datesplit[2])
            skyevent.hour = int(timesplit[0])
            skyevent.minute = int(timesplit[1])
            second = timesplit[2]
            second = second[:2]
            skyevent.second = int(second)
            skyuser = ""
            for u in userlist:
                if u in sentry.display_name:
                    skyuser = u
            skyevent.description = "Skype is executed by %s (Date: %s, Time: %s)" % (skyuser, date, time)
            eventHead = AutoLib.insertEvent(eventHead, skyevent)

        '''date = sentry.date
        time = sentry.time

        sevent = Event.Event()
        datesplit = date.split(":")
        timesplit = time.split(":")
        sevent.year = int(datesplit[0])
        sevent.month = int(datesplit[1])
        sevent.day = int(datesplit[2])
        sevent.hour = int(timesplit[0])
        sevent.minute = int(timesplit[1])
        second = timesplit[2]
        second = second[:second.index('.')]
        sevent.second = int(second)
        sevent.description = "Skype is executed (Date: %s, Time: %s)" % (date, time)
        eventHead = AutoLib.insertEvent(eventHead, sevent)'''

timelinerelevant_removable_disk_usage = False
for n in ntuser_relevant_entries:  # Check if relevant entries also contain any mention of a removable disk
    if "Removable Disk" in n.message:
      timelinerelevant_removable_disk_usage = True

ie5_content = False
for n in ntuser_relevant_entries:
    if "Content.IE5" in n.message:
        ie5_content = True

userinteract = []
for n in ntuser_relevant_entries:
    for u in userlist:
        u = u.rstrip()
        if (u in n.display_name) and (u not in userinteract):
            userinteract.append(u)

#Compare results with metadata
date_check = False

time_check = False
impossiblelocal = False
timespan_relevant_entries = []
if metadata.created_date == "None provided":
    print "No created date within metadata, skipping metadata time/date verification.\n"
else: #Proceed with checks, as relevant data is available.
    for n in ntuser_relevant_entries:
      if n.date == metadata.created_date: #Check if dates are the same
        date_check = True

    if date_check == False:
        print "NTUSER Timeline entries are not within a timespan that infers local creation\n"
    else:
        time_split = metadata.created_time.split(":")
        meta_hours = int(time_split[0])
        meta_minutes = int(time_split[1])

        for n in ntuser_relevant_entries: #Check if timeline events happened in close proximity to creation time
            reltime_split = n.time.split(":")
            timeline_hours = int(reltime_split[0])
            if timeline_hours == meta_hours:
                timeline_minutes = int(reltime_split[1])
                if (timeline_minutes >= (meta_minutes - threshold)) and (timeline_minutes <= (meta_minutes + threshold)):
                    timespan_relevant_entries.append(n)

        if timespan_relevant_entries:
            time_check = True

    ##################
    '''System Check'''
    ##################
    # Check if OS created after file
    winsplit = wininfo.installdate.split(":")
    wininstallyear = winsplit[0]
    wininstallmonth = winsplit[1]
    wininstallday = winsplit[2]
    metasplit = metadata.created_date.split(":")
    createdyear = metasplit[0]
    createdmonth = metasplit[1]
    createdday = metasplit[2]
    if wininstallyear > createdyear:
        impossiblelocal = True
    elif (wininstallyear == createdyear) and (wininstallmonth > createdmonth):
        impossiblelocal = True
    elif (wininstallyear == createdyear) and (wininstallmonth == createdmonth) and (wininstallday > createdday):
        impossiblelocal = True

#########################
'''Registry Processing'''
#########################

#Recently used docs


recentuser = []
for user in userlist:
    recent = open('%s/%s/recent.txt' % (filename, user))
    for line in recent:
        line = line.rstrip()
        if (filename in line) and (user not in recentuser):
            recentuser.append(user)

#USB info
rawusb = open('%s/usbdevices.txt' % filename, 'r')
devices = []
monthdictionary = {'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6, 'Jul': 7,
                   'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}

for line in rawusb: #Gets date and time USB was last seen on system, as well as Serial Number
    if "SN" in line:
        usbentry = USB.USB()
        splitline = line.split(':')
        serial = (splitline[1].lstrip()).rstrip()
        usbentry.serial = serial
        datetime = rawusb.next()
        splitline = datetime.split(' ')
        while '' in splitline:
          splitline.remove('')
        month = splitline[2]
        month = monthdictionary[month]
        day = splitline[3]
        time = splitline[4]
        timesplit = time.split(":")
        hours = timesplit[0]
        hours = hours.replace('0', '', 1)
        minutes = timesplit[1]
        minutes = minutes.replace('0', '', 1)
        seconds = timesplit[2]
        seconds = seconds.replace('0', '', 1)
        time = "%s:%s:%s" % (hours, minutes, seconds)

        year = splitline[5].rstrip()
        formatdate = "%s:%s:%s" % (year, month, day)
        usbentry.lastwritedate = formatdate
        usbentry.lastwritetime = time
        devices.append(usbentry)

usbdatematch = False
usbEvent = None
for device in devices:
    if ntuser_relevant_entries[0].date == device.lastwritedate:  # Check if dates are the same
        usbdatematch = True
        usbEvent = Event.Event()

        date = device.lastwritedate
        time = device.lastwritetime
        datesplit = date.split(":")
        timesplit = time.split(":")
        usbEvent.year = int(datesplit[0])
        usbEvent.month = int(datesplit[1])
        usbEvent.day = int(datesplit[2])
        usbEvent.hour = int(timesplit[0])
        usbEvent.minute = int(timesplit[1])
        usbEvent.second = int(timesplit[2])
        usbEvent.description = "A USB device was connected to the system (Date: %s, Time: %s)" % (date, time)

        eventHead = AutoLib.insertEvent(eventHead, usbEvent)


    #User info
samparse = open('%s/samparse.txt' % filename, 'r')
samusers = AutoLib.getUsers(samparse)

samedaylogin = []
for samuser in samusers:
    if ntuser_relevant_entries:
      if samuser.last_login_date == ntuser_relevant_entries[0].date:
        samedaylogin.append(samuser.username)

        uevent = Event.Event()
        date = samuser.last_login_date
        time = samuser.last_login_time

        datesplit = date.split(":")
        timesplit = time.split(":")
        uevent.year = int(datesplit[0])
        uevent.month = int(datesplit[1])
        uevent.day = int(datesplit[2])
        uevent.hour = int(timesplit[0])
        uevent.minute = int(timesplit[1])
        uevent.second = int(timesplit[2])
        uevent.description = "User: %s logged into the system (Date: %s, Time: %s)" % (samuser.username, date, time)

        eventHead = AutoLib.insertEvent(eventHead, uevent)

#################
'''Web History'''
#################
chrome_visits = []
for user in userlist:
  if Path('%s/%s/chrome.txt' % (args.folder, user)).is_file():
    with open('%s/%s/chrome.txt' % (args.folder, user), 'r') as chrome_links:
      for line in chrome_links:
        line = line.replace("\x00", "") #Strip out garbage hex characters
        if ("URL" in line) and ("URL Length" not in line):
            hist = InternetHist.InternetHist()
            hist.user = user
            line_split = line.split(":", 1)
            url = line_split[1].rstrip().lstrip()
            hist.url = url
            chrome_links.next()
            visit_on = chrome_links.next()
            visit_on = visit_on.replace("\x00", "")
            visit_date_time = AutoLib.get_chrome_visit(visit_on, lmbias)
            hist.visit_date = visit_date_time[0]
            hist.visit_time = visit_date_time[1]

            chrome_visits.append(hist)

ie_visits = []
for user in userlist:
    with open('%s/%s/ie.txt' % (filename, user), 'r') as ie_links:
        for line in ie_links:
            line = line.replace("\x00", "") #Strip out garbage hex characters
            if ("URL" in line) and ("URL Length" not in line):
                hist = InternetHist.InternetHist()
                hist.user = user
                line_split = line.split(":", 1)
                hist.url = line_split[1].rstrip().lstrip()
                ie_links.next()
                ie_links.next()
                visit_on = ie_links.next()
                visit_on = visit_on.replace("\x00", "")
                visit_date_time = AutoLib.get_chrome_visit(visit_on, lmbias)
                hist.visit_date = visit_date_time[0]
                hist.visit_time = visit_date_time[1]
                ie_visits.append(hist)

relevant_chrome_visits = []
for link in chrome_visits:
  if ntuser_relevant_entries:
    if link.visit_date == ntuser_relevant_entries[0].date:
        visit_time = link.visit_time

        time_split = visit_time.split(":")
        visit_hours = int(time_split[0])
        firstentry_time = ntuser_relevant_entries[0].time
        firstentry_split = firstentry_time.split(":")
        firstentry_hours = int(firstentry_split[0])
        if (firstentry_hours >= visit_hours - 2) and (firstentry_hours <= visit_hours + 2):
            relevant_chrome_visits.append(link)

relevant_ie_visits = []
for link in ie_visits:
  if ntuser_relevant_entries:
    if link.visit_date == ntuser_relevant_entries[0].date:
        visit_time = link.visit_time
        time_split = visit_time.split(":")
        visit_hours = int(time_split[0])
        firstentry_time = ntuser_relevant_entries[0].time
        firstentry_split = firstentry_time.split(":")
        firstentry_hours = int(firstentry_split[0])
        if (firstentry_hours >= visit_hours - 2) and (firstentry_hours <= visit_hours + 2):
            relevant_ie_visits.append(link)

######################################
'''Comparing and outputting Results'''
######################################


if metadata.created_date != "None provided":
  print "The file was created on %s, at %s\n" % (metadata.created_date, metadata.created_time)

if ntuser_relevant_entries:
  print "The file is first seen on the system on %s, at %s\n" % (ntuser_relevant_entries[0].date, ntuser_relevant_entries[0].time)


if ntuser_relevant_entries:
  firstSeen = ntuser_relevant_entries[0]
  firstSeenDate = firstSeen.date
  firstSeenTime = firstSeen.time
  fsdatesplit = firstSeenDate.split(":")
  fstimesplit = firstSeenTime.split(":")

  fsEntry = Event.Event()
  fsEntry.year = int(fsdatesplit[0])
  fsEntry.month = int(fsdatesplit[1])
  fsEntry.day = int(fsdatesplit[2])
  fsEntry.hour = int(fstimesplit[0])
  fsEntry.minute = int(fstimesplit[1])
  fsSeconds = fstimesplit[2]
  if '.' in fsSeconds:
    fsSeconds = fsSeconds[:fsSeconds.index('.')]
  fsEntry.second = int(fsSeconds)
  fsEntry.description = "***%s FIRST SEEN*** (Date: %s, Time: %s)" % (filename, firstSeenDate, firstSeenTime)
  eventHead = AutoLib.insertEvent(eventHead, fsEntry)

if recentuser or userinteract:
    usercombine = recentuser + userinteract
    print "User/s: %s interacted with the file of interest" % usercombine


if date_check:
    print "There are entries in the timeline referencing the file of interest on the same date that it was created."
if time_check:
    print "Relevant NTUSER timeline entries exist for this file within 30 minutes of its creation!"
if systemuser:
    print "Username that created file is a user name that exists on this system."
    print "Creator = %s" % (metadata.author)
if systemmod:
    print "Username that last modified file is a user name that exists on this system."
    print "Modifier = %S" % (metadata.modifier)
if word_create_day:
    print "Microsoft Word was executed on this computer, on the same day that this file was created."
if word_appear_day:
    print "Microsoft Word was executed on this computer, on the first day this file was seen on this computer"
if word_modify_day:
    print "Microsoft Word was executed on this computer, on the same day that this file was last modified."
if officeinteract:
    print "A microsoft office product was used to interact with the file at some point"


if impossiblelocal:
    print "This system was created after the file was created, therefore the file could not have been created locally.\n"

#Check for possible movement of file
movement = AutoLib.timecheck(timestamps.mtime_date, timestamps.mtime_time, timestamps.ctime_date,
                             timestamps.ctime_time, ntuser_relevant_entries[0].date, ntuser_relevant_entries[0].time)
if movement:
    print "The file appears to have been moved within the system: ctime and mtime are not relatively close."
    print "mtime: Date = %s, Time = %s" % (timestamps.mtime_date, timestamps.mtime_time)
    print "ctime: Date = %s, Time = %s\n" % (timestamps.ctime_date, timestamps.ctime_time)

#Check for possible editing of file
if ntuser_relevant_entries:
    firstentry = ntuser_relevant_entries[0]
    editing = AutoLib.editcheck(timestamps.mtime_date, timestamps.mtime_time, firstentry.date, firstentry.time)
    if editing:
        print "The file appears to have been edited or copied within the system: mtime is not relatively close to first file reference."
        print "mtime: Date = %s, Time = %s\n" % (timestamps.mtime_date, timestamps.mtime_time)

usbfactors = 0
if timelinerelevant_removable_disk_usage:
  usbfactors = usbfactors + 1
  print "Timeline entry referencing filename also references a removable disk"
if usbdatematch:
  usbfactors = usbfactors + 1
  print "Removable disk was used on the same day the file was first referenced on system."

torrentfactors = 0
if torrentfile:
  torrentfactors = torrentfactors + 1
  print "A torrent file with the same name as the file of interest is present on the system."
if fwiredatematch1:
  torrentfactors = torrentfactors + 1
  print "FrostWire was used on the day that the file was first seen on system"

skypefactors = 0
if skypedatematch:
    skypefactors = skypefactors + 1
    print "Skype was used on the day that the file was first seen on system"
if skype30min:
    skypefactors = skypefactors + 1
    print "Skype was used within 30 minutes of the file first being seen on system"

if samedaylogin:
    for login in samedaylogin:
        print "The user: %s - last logged in the same day the file was first seen on system." % login

if relevant_chrome_visits:
    for visit in relevant_chrome_visits:
        entry = Event.Event()
        entry.description = "%s visited: %s (Date: %s, Time: %s)" % (visit.user, visit.url, visit.visit_date, visit.visit_time)
        date = visit.visit_date
        datesplit = date.split(':')
        entry.year = int(datesplit[0])
        entry.month = int(datesplit[1])
        entry.day = int(datesplit[2])

        time = visit.visit_time
        timesplit = time.split(':')
        entry.hour = int(timesplit[0])
        entry.minute = int(timesplit[1])
        entry.second = int(timesplit[2])

        eventHead = AutoLib.insertEvent(eventHead, entry)


if relevant_ie_visits:
    for visit in relevant_ie_visits:
        entry = Event.Event()
        entry.description = "%s visited: %s (Date: %s, Time: %s)" % (
                            visit.user, visit.url, visit.visit_date, visit.visit_time)
        date = visit.visit_date
        datesplit = date.split(':')
        entry.year = int(datesplit[0])
        entry.month = int(datesplit[1])
        entry.day = int(datesplit[2])

        time = visit.visit_time
        timesplit = time.split(':')
        entry.hour = int(timesplit[0])
        entry.minute = int(timesplit[1])
        entry.second = int(timesplit[2])

        eventHead = AutoLib.insertEvent(eventHead, entry)

if ie5_content:
    print "References to %s found within Internet Explorer Temporary Internet Files" % filename

print "\n"
print "%%%%%%%%%%   BEGIN TIMELINE   %%%%%%%%%%\n"
AutoLib.printEvents(eventHead)
