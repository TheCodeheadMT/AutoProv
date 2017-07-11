# AutoProvLinux

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

Plaso: This provides the back-end log2timeline capability to extract file system time stamps.

```
sudo add-apt-repository ppa:gift/stable
sudo apt-get install python-pip
sudo apt-get install python-artifacts
sudo apt-get install python-bencode
sudo apt-get install plaso
```

Exiftool: This provides the capability to read metadata (Exif, IPTC, XMP, etc.) from multiple files (JPEG, TIFF, PNG, PDF, RAW, etc.)

```
sudo apt-get install exiftool
```

Wine: This is necessary to permit the Windows applications to run on Linux

```
sudo apt-get install wine
```

[regripper](https://github.com/keydet89/RegRipper2.8m): This is leveraged to read keys from a Windows registry without the Windows API. Download and install it, placing the plugins in the plugin folder.
 

```
sudo cpan App::cpanminus
sudo cpanm Parse::Win32Registry
chmod u+x rip.pl
````

Add this line to the end of ~/.bashrc, replacing (user name) and (RegRipper folder) appropriately.:

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

Ryan Good, and Gilbert Peterson, 'Automated Collection and Correlation of File Provenance Information', *Advances in Digital Forensics XIII*, G. Peterson and S. Shenoi, Eds., pp. TBD, 2017. 

