# XBMC video plugin for HDHomerun #

**XBMC** - http://xbmc.org/

**HDHomerun** - http://www.hdhomerun.com/

For now this plug-in ONLY works for XBMC "_Eden_" on Linux and Mac because that's where it has been tested. Anyone who wants the help getting it to work on Windows is welcome.

### Installation ###

To make this plugin work some manual work is needed because the HDHomeRun library included with XBMC is not the version needed by this plugin so you'll have to download and install the proper version yourself.

The downloads can be found here:

http://www.silicondust.com/support/hdhomerun/downloads/

Although some Linux distributions already include hdhomerun in their repositories, so if for example you're using the "Live" version of XBMC which is based on Ubuntu, you can just type:

```
sudo apt-get install libhdhomerun1
```

After installation of the HDHomeRun software you can proceed to download the latest plugin zip file [here](http://code.google.com/p/xbmc-hdhomerun-plugin/downloads/list) and add to to XBMC in [the normal manner](http://wiki.xbmc.org/index.php?title=Add-ons#How_to_install_from_zip).

NB: because of this dependency on binary module this plugin will probably never be accepted into the official repository as-is. (No binaries allowed)