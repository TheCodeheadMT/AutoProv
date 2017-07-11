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
import argparse
import AutoLib
import subprocess
import os
import FFhistory
from pathlib import Path

# Handling command line arguments
parser = argparse.ArgumentParser(
    description='This program automatically finds provenance related to a file on an image. '
)
parser.add_argument("image", help="Disk image in .dd format")
parser.add_argument("file", help="Name of file to be analyzed")
args = parser.parse_args()

# Find file type
filename = args.file
filetype = AutoLib.find_file_type(filename)
subprocess.call(["mkdir", filename.replace('\\', '')])

# mount image
outfile = open('%s/mmlsoutput.txt' % filename.replace('\\', ''), 'w')
subprocess.call(["mmls", args.image], stdout=outfile)
start_block = AutoLib.parse_mmls(filename.replace('\\', ''))
start_block = int(start_block) * 512
subprocess.call(["sudo", "mount", "-t", "ntfs", "-o", "loop,offset=%d,ro,noexec" % start_block, args.image, "image"])

# Get OS version and install date
win7plus = False
xp = False
with open('%s/wininfo.txt' % filename.replace('\\', ''), 'w') as out:
    if Path("image/Windows/System32/config/SOFTWARE").is_file():
        subprocess.call(['rip.pl', '-r', 'image/Windows/System32/config/SOFTWARE', '-p', 'winver'], stdout=out)
        win7plus = True
    elif Path("image/WINDOWS/system32/config/software").is_file():
        subprocess.call(['rip.pl', '-r', 'image/WINDOWS/system32/config/software', '-p', 'winver'], stdout=out)
        xp = True

# Get location of file of interest
print "Searching for %s" % filename
location = subprocess.Popen(['find', 'image', '-name', filename], stdout=subprocess.PIPE)
location = location.stdout.read()
location = location.rstrip()  # strip white space
torrentcheck = subprocess.Popen(['find', 'image', '-name', filename + ".torrent"],
                                stdout=subprocess.PIPE)  # Check for torrent file
torrentcheck = torrentcheck.stdout.read()
torrentcheck = torrentcheck.rstrip()

filename = filename.replace('\\', '')
namelocationfile = open('%s/namelocation.txt' % filename, 'w')
namelocationfile.write(filename + '\n')
namelocationfile.write(location)
if torrentcheck != "":
    namelocationfile.write("torrentcheck")

# Get atime, ctime, mtime
with open('%s/timefile.txt' % filename, 'w') as timefile:
    subprocess.call(["stat", location], stdout=timefile)

# Get metadata from file
with open('%s/meta.txt' % filename, 'w') as outfile:
    subprocess.call(["exiftool", location], stdout=outfile)

print "Creating Timelines"
# Create timeline based on NTUSER
with open('%s/timeline1.txt' % filename, 'w') as outfile:
    filt = "filt1.txt"

    subprocess.call(["log2timeline.py", "-f", "filts/%s" % filt, "%s/timeline1.plaso" % filename, args.image])
    print "Processing timeline using psort"
    subprocess.call(["psort.py", "%s/timeline1.plaso" % filename], stdout=outfile)

######Regripper Stuff######
# Get list of users on image
if xp:
    users = subprocess.Popen(['ls', 'image/Documents and Settings/'], stdout=subprocess.PIPE)
else:
    users = subprocess.Popen(['ls', 'image/Users/'], stdout=subprocess.PIPE)
users = users.stdout.read()
users = users.rstrip()

user_list = users.split('\n')
nuser_list = []
for user in user_list:  # Strip out users we aren't interested in (Defaults)
    if (user != "All Users") and (user != "desktop.ini") and (user != "Default") and (user != "Default User") \
            and (user != "Public") and (user != "NetworkService") and (user != "LocalService"):
        nuser_list.append(user)

with open('%s/users.txt' % filename, 'w') as userfile:
    for n in nuser_list:
        userfile.write(n + '\n')

# Get list of recent explorer items for each user.
for n in nuser_list:
    subprocess.call(["mkdir", "%s/%s" % (filename, n)])
    with open('%s/%s/recent.txt' % (filename, n), 'w') as out:
        if xp:
            subprocess.call(['rip.pl', '-r', 'image/Documents and Settings/%s/NTUSER.DAT' % n, '-p', 'recentdocs_tln'],
                            stdout=out)
        else:
            subprocess.call(['rip.pl', '-r', 'image/Users/%s/NTUSER.DAT' % n, '-p', 'recentdocs_tln'], stdout=out)

# Get USB usage data
with open('%s/usbdevices.txt' % filename, 'w') as out:
    if xp:
        subprocess.call(['rip.pl', '-r', 'image/WINDOWS/system32/config/system', '-p', 'usbdevices'],
                        stdout=out)
    else:
        subprocess.call(['rip.pl', '-r', 'image/Windows/System32/config/SYSTEM', '-p', 'usbdevices'],
                        stdout=out)

# Get User info
with open('%s/samparse.txt' % filename, 'w') as out:
    if xp:
        subprocess.call(['rip.pl', '-r', 'image/WINDOWS/system32/config/SAM', '-p', 'samparse'],
                        stdout=out)
    else:
        subprocess.call(['rip.pl', '-r', 'image/Windows/System32/config/SAM', '-p', 'samparse'],
                        stdout=out)

# Get Timezone info
with open('%s/timezone.txt' % filename, 'w') as out:
    if xp:
        subprocess.call(['rip.pl', '-r', 'image/WINDOWS/system32/config/system', '-p', 'timezone'],
                        stdout=out)
    else:
        subprocess.call(['rip.pl', '-r', 'image/Windows/System32/config/SYSTEM', '-p', 'timezone'],
                        stdout=out)

# Get Chrome History
for user in nuser_list:
    os.system(
        'wine ChromeHistoryView.exe /UseHistoryFile 1 /HistoryFile "image/Documents and Settings/%s/Local Settings/Application Data/Google/Chrome/User Data/Default/History" /stext %s/%s/chrome.txt' % (
            user, filename, user))

# Get IE History
for user in nuser_list:
    if xp:
        subprocess.call(['wine', 'iehv.exe', '/stext', '%s/%s/ie.txt' % (filename, user), '-folder',
                         'image/Documents and Settings/%s/Local Settings/History/' % user])
    else:
        subprocess.call(['wine', 'iehv.exe', '/stext', '%s/%s/ie.txt' % (filename, user), '-folder',
                         'image/Users/%s/AppData/Local/Microsoft/Windows/History/' % user])

# Get Safari History
for user in nuser_list:
    if xp:
        subprocess.call(['wine', 'SafariHistoryView.exe', '/stext', '%s/%s/safari.txt' % (filename, user),
                         '/loadfile' 'image/Documents and Settings/%s/Application Data/Apple Computer/Safari/History.plist' % user])

# Get FireFox History

for user in nuser_list:
    if Path("image/Documents and Settings/%s/Application Data/Mozilla/Firefox/Profiles/").is_file():
        ffprofs = subprocess.Popen(
            ['ls', 'image/Documents and Settings/%s/Application Data/Mozilla/Firefox/Profiles/' % user],
            stdout=subprocess.PIPE)
        ffprofs = ffprofs.stdout.read()
        ffprofs = ffprofs.rstrip()

        ffprof_list = ffprofs.split('\n')
        for prof in ffprof_list:
            ffloc = ""
            if xp:
                ffloc = 'image/Documents and Settings/%s/Application Data/Mozilla/Firefox/Profiles/%s/places.sqlite' % (
                    user, prof)
            else:
                ffloc = 'image/Users/%s/Application Data/Mozilla/Firefox/Profiles/%s/places.sqlite' % (user, prof)

            history = FFhistory.build_history(ffloc)
            with open('%s/%s/ffhist.txt' % (filename, user), 'a') as ffhistfile:
                for entry in history:
                    ffhistfile.write(
                        "%s visited: %s (Date: %s, Time: %s)" % (user, entry.addr, entry.date, entry.time) + '\n')
