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
class TimelineEntry(object):
  """An Entry created by log2timeline, within a class structure
     to aid in manipulation.   """

  date = "None provided"
  time = "None provided"
  time_description = "None provided"
  source = "None provided"
  long_source = "None provided"
  message = "None provided"
  parser = "None provided"
  display_name = "None provided"
  tag = "None provided"
  store_number = "None provided"
  store_index = "None provided"

  #Returns a Meta object with the provided attributes.
  def __init__(self, filename):
    self.filename = filename