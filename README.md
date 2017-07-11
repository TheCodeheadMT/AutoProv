# AutoProvLinux

AutoProv is a two phase script for recreating the provenance of a file from several 
temporal artifacts from digital forensics media. It identifies relevant temporal 
and user correlations between the artifacts and presents them to the examiner.

AutoProv leverages 19 temporal artifacts that include file system, registry, file 
and OS metadata, and web browser, Skype, and torrent application data. Additional 
details can be found in the paper referenced below.s 
 
## Setup 

Valid as of Ubuntu 16.04 LTS

**Requires**

+ Python v2.7
+ perl v5.18

Make sure the system is up to date

```
sudo apt-get update
````

The Sleuth Kit (TSK): This provides the ability to mount a drive image for analysis

```
sudo apt-get install sleuthkit
```

Plaso: This provides the back-end log2timeline capability to extract file system 
time stamps.

```
sudo add-apt-repository ppa:gift/stable
sudo apt-get install python-pip
sudo apt-get install python-artifacts
sudo apt-get install python-bencode
sudo apt-get install plaso
```

Exiftool: This provides the capability to read metadata (Exif, IPTC, XMP, etc.) 
from multiple files (JPEG, TIFF, PNG, PDF, RAW, etc.)

```
sudo apt-get install exiftool
```

Wine: This is necessary to permit the Windows applications to run on Linux

```
sudo apt-get install wine
```

[regripper](https://github.com/keydet89/RegRipper2.8m): This is leveraged to read 
keys from a Windows registry without the Windows API. Download and install it, place the plugins in to a `plugin` subfolder of the main project.
 

```
sudo cpan App::cpanminus
sudo cpanm Parse::Win32Registry
chmod u+x rip.pl
````

Add this line to the end of ~/.bashrc, replacing (user name) and (RegRipper folder) 
appropriately.:

```
export PATH=$PATH:/home/(user name)/Documents/(RegRipper folder)
```

## Execution

```
python DataGather.py {image} {file}
```

_image_ - the hard drive image that the file of interest resides on. Must be openable by TSK.

_file_ - The file of interest for analysis.

```
python DataProcess.py {folder}
```

_folder_ - This is the folder that DataGather.py created.

## Reference

If you use or extend this, please reference the following related article:

Ryan Good, and Gilbert Peterson, 'Automated Collection and Correlation of File 
Provenance Information', *Advances in Digital Forensics XIII*, G. Peterson and 
S. Shenoi, Eds., pp. TBD, 2017. 

## License

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

The views expressed in this work are those of the authors, and do not reflect 
the official policy or position of the United States Air Force, Department of 
Defense, or the U.S. Government.