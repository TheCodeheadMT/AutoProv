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
import sqlite3 as lite
import sys
import MozHist
import time


#Build array of MozHist entries based on places.sqlite file
def build_history(file):
  entries = []
  con = lite.connect(file)
  with con:
    cur = con.cursor()
    cur.execute('SELECT * FROM moz_historyvisits')
    history = cur.fetchall()
    for entry in history:
      histEnt = MozHist.MozHist()
      index = entry[2]
      histEnt.addr = retrieve_addr(index, cur)
      datetime_enc = str(entry[3])
      datetime_enc = int(datetime_enc[:10]) #Epoch encoded time
      datetime_unenc = time.strftime('%Y:%m:%d %H:%M:%S', time.gmtime(datetime_enc)) #Time converted to UTC

      datetime_split = datetime_unenc.split(" ") #split date and time
      date = datetime_split[0]
      gmtime = datetime_split[1]
      histEnt.date = date
      histEnt.time = gmtime

      entries.append(histEnt)

  return entries

#Get the name of the website referenced
def retrieve_addr(index, cur):
  cur.execute('SELECT * FROM moz_places')
  addresses = cur.fetchall()
  for address in addresses:
    if index == address[0]:
      return address[1]

#entries = build_history('image/Documents and Settings/samrat/Application Data/Mozilla/Firefox/Profiles/lep2iz1h.default/places.sqlite')
#entries = build_history('image/Documents and Settings/sandeep/Application Data/Mozilla/Firefox/Profiles/r71200q5.default/places.sqlite')

#con = lite.connect('image/Documents and Settings/samrat/Application Data/Mozilla/Firefox/Profiles/lep2iz1h.default/places.sqlite')
#cur = con.cursor()
#cur.execute('SELECT * FROM moz_places')
#addresses = cur.fetchall()
#for entry in entries:
  #print "%s, %s, %s" % (entry.addr, entry.date, entry.time)