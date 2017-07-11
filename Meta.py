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
class Meta(object):
  """Metadata for a file of interest with
     the following properties:

    Attributes:
      filename: A string representing the name of the file
      directory: The directory the file is located in
      modification_date: Date last modified
      modification_time: Time last modified
      access_date: Date last accessed
      access_time: Time last accessed
      creator: Who created the document
      modifier: Who last modified the document
      created_date: Date file was created
      created_time: Time file was created
  """

  modification_date = "None provided"
  modification_time = "None provided"
  access_date = "None provided"
  access_time = "None provided"
  creator = "None provided"
  author = "None provided"
  modifier = "None provided"
  created_date = "None provided"
  created_time = "None provided"

  #Returns a Meta object with the provided attributes.
  def __init__(self, filename, directory):
    self.filename = filename
    self.directory = directory