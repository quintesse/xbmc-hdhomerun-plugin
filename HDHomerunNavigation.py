'''
   HDHomerun plugin for XBMC
   Copyright (C) 2012 Tako Schotanus

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation, either version 3 of the License, or
   (at your option) any later version.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU General Public License for more details.
   
   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import os
import xbmc
import xbmcgui
import xbmcplugin
import urllib
import hdhomerun

from operator import itemgetter

class HDHomerunNavigation:     
    __settings__ = sys.modules[ "__main__" ].__settings__
    __language__ = sys.modules[ "__main__" ].__language__
    __plugin__ = sys.modules[ "__main__"].__plugin__    
    __dbg__ = sys.modules[ "__main__" ].__dbg__
    
    plugin_thumbnail_path = os.path.join( __settings__.getAddonInfo('path'), "thumbnails" )

    #==================================== Main Entry Points===========================================
    def listMenu(self, params = {}):
        cache = True
        
        if (self.__dbg__):
            print self.__plugin__ + " listMenu params = " + str(params)

        info = {}
        dd = None
        dev = None
        disc = hdhomerun.HdhrDiscovery()

        devid = int(params.get("device", -1))
        if (devid != -1):
            dd = disc.device(devid)
            info["device"] = devid
            
        tuner = int(params.get("tuner", -1))
        if (tuner != -1):
            dev = dd.connect(tuner)
            info["tuner"] = tuner
        
        type = params.get("type")
        if (not type):
            devs = disc.devices()
            if (len(devs) > 0):
                # Show the list of devices
                for dd in devs:
                    devinfo = dict({ 'thumbnail':"explore", 'type':"device" }, **info)
                    devinfo["Title"] = "Device " + self.id2str(dd.device_id) + " (" + str(dd.tuner_count) + " tuners)"
                    devinfo["device"] = dd.device_id
                    self.addListItem(params, devinfo)
            else:
                self.addListItem(params, {'Title':"No devices found!", 'thumbnail':"explore" })
        elif (type == "device"):
            # Show the list of tuners
            for i in range(dd.tuner_count):
                tunerinfo = dict({ 'thumbnail':"explore", 'type':"tuner" }, **info)
                tunerinfo["Title"] = "Tuner " + str(i)
                tunerinfo["tuner"] = i
                self.addListItem(params, tunerinfo)
        elif (type == "tuner"):
            chid = "channel_list_" + str(devid) + "_" + str(tuner)
            try:
                chlist = eval(self.__settings__.getSetting(chid))
            except:
                chlist = None
            if (chlist):
		chlist = sorted(chlist, key=itemgetter("name"))
                # Show the list of channels for the selected tuner
                for ch in chlist:
                    #try:
                        chinfo = dict({'thumbnail':"explore", 'type':"channel" }, **info)
                        chinfo["Title"] = ch.get("name")
                        chinfo["channel"] = ch.get("channel")
                        chinfo["program"] = ch.get("program")
                        self.addChannelListItem(params, chinfo)
                    #except:
                    #    pass
                # Show the option to re-scan the channel list
                scaninfo = dict({'Title':"Rescan for channels...", 'thumbnail':"explore", 'type':"scan" }, **info)
                self.addListItem(params, scaninfo)
            else:
                # Show the option to start scanning
                scaninfo = dict({'Title':"Scan for channels...", 'thumbnail':"explore", 'type':"scan" }, **info)
                self.addListItem(params, scaninfo)
        elif (type == "scan"):
            # Scan for available channels (adding them to the dialog list at the same time)
            chid = "channel_list_" + str(devid) + "_" + str(tuner)
            (res, chlists) = dev.scan(self.scan_callback, info)
            if res == 1:
                # First flatten the list
                chlist = sum(chlists, [])
                # Now we store it for future use
                self.__settings__.setSetting(chid, repr(chlist))
        else:
            self.addListItem(params, {'Title':"NYI", 'thumbnail':"explore" })

        video_view = self.__settings__.getSetting("list_view") == "1"
        if (self.__dbg__):
            print self.__plugin__ + " view mode: " + self.__settings__.getSetting("list_view")
        
        if (video_view):
            if (self.__dbg__):
                print self.__plugin__ + " setting view mode"
            xbmc.executebuiltin("Container.SetViewMode(500)")
        
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True, cacheToDisc=cache )

    def scan_callback(self, dev, detres, scan, info):
        res = []
        if detres != None:
            for i in range(detres.program_count):
                p = detres.programs[i]
                res.append({ 'name':p.name, 'channel':scan.frequency, 'program':p.program_number })
                # Add the info to the dialog list so we can see the progress of the scan
                chinfo = dict({'thumbnail':"explore", 'type':"channel" }, **info)
                chinfo["Title"] = p.name
                chinfo["channel"] = scan.frequency
                chinfo["program"] = p.program_number
                self.addChannelListItem({}, chinfo)
            if (self.__dbg__):
                print self.__plugin__ + " scan progres " + dev.channelscan_get_progress()
        return res
        
    def listOptionFolder(self, params = {}):
        get = params.get
        item_favorites = {'Title':self.__language__( 30020 ), 'path':get("path"), 'external':"true", 'thumbnail':"favorites", 'feed':"favorites", "contact":get("contact")}
        self.addFolderListItem(params, item_favorites, 1)
        item_playlists = {'Title':self.__language__( 30023 ), 'path':get("path"), 'external':"true", 'thumbnail':"playlists", 'feed':"playlists", "contact":get("contact")}
        self.addFolderListItem(params, item_playlists, 2)
        item_subscriptions = {'Title':self.__language__( 30021 ), 'path':get("path"), 'external':"true", 'thumbnail':"subscriptions", 'feed':"subscriptions", "contact":get("contact")}
        self.addFolderListItem(params, item_subscriptions, 3)
        item_uploads = {'Title':self.__language__( 30022 ), 'path':get("path"), 'external':"true", 'thumbnail':"uploads", 'feed':"uploads", "contact":get("contact") }
        self.addFolderListItem(params, item_uploads, 4)
        
        xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True, cacheToDisc=False)

    #================================== List Item manipulation =========================================    
    
    # common function for adding folder items
    def addListItem(self, params = {}, item_params = {}, size = 0):
        get = params.get
        item = item_params.get
        
        icon = "DefaultFolder.png"        
        thumbnail = item("thumbnail")
        if (item("thumbnail", "DefaultFolder.png").find("http://") == -1):    
            thumbnail = self.getThumbnail(item("thumbnail"))
        
        cm = self.addContextMenuItems(params, item_params)
        
        listitem=xbmcgui.ListItem( item("Title"), iconImage=icon, thumbnailImage=thumbnail )
        url = '%s?path=%s&' % ( sys.argv[0], item("path") )
        url = self.buildItemUrl(item_params, url)
        
        if len(cm) > 0:
            listitem.addContextMenuItems( cm, replaceItems=False )
        
        listitem.setProperty( "Folder", "true" )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=True, totalItems=size)
    
    def addChannelListItem(self, params = {}, item_params = {}, size = 0):
        get = params.get
        item = item_params.get
        
        listitem=xbmcgui.ListItem(item("Title"), "", "DefaultVideo.png")
        
        url = 'hdhomerun://%s/tuner%s?channel=auto:%s&program=%s' % ( self.id2str(item("device")), item("tuner"), item("channel"), item("program"));
        
        listitem.setProperty( "Video", "true" )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem)
    
    # common function for adding video items
    def addVideoListItem(self, params = {}, item_params = {}, listSize = 0): 
        get = params.get
        item = item_params.get
        
        icon = "DefaultVideo.png"        
        thumbnail = item("thumbnail")
        if (item("thumbnail", "DefaultVideo.png").find("http://") == -1):    
            thumbnail = self.getThumbnail(item("thumbnail"))
            
        cm = self.addContextMenuItems(params, item_params)
                
        listitem=xbmcgui.ListItem( item("Title"), iconImage=icon, thumbnailImage=thumbnail )

        url = 'hdhomerun://%s/tuner%s?channel=auto:%s&program=%s' % ( item("device"), item("tuner"), item("channel"), item("program"));
            
        if len(cm) > 0:
            listitem.addContextMenuItems( cm, replaceItems=False )

        listitem.setProperty( "Video", "true" )
        listitem.setProperty( "IsPlayable", "true")
        listitem.setInfo(type='Video', infoLabels=item_params)
        xbmcplugin.setContent( handle=int( sys.argv[ 1 ] ), content="movies" )
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False, totalItems=listSize + 1)
    
    #=================================== Tool Box ======================================= 
    # shows a more userfriendly notification
    def showMessage(self, heading, message):
        duration = ([5, 10, 15, 20, 25, 30][int(self.__settings__.getSetting( 'notification_length' ))]) * 1000
        xbmc.executebuiltin('XBMC.Notification("%s", "%s", %s)' % ( heading, message, duration) )

    # create the full thumbnail path for skins directory
    def getThumbnail( self, title ):
        if (not title):
            title = "DefaultFolder.png"
        
        thumbnail = os.path.join( sys.modules[ "__main__" ].__plugin__, title + ".png" )
        
        if ( not xbmc.skinHasImage( thumbnail ) ):
            thumbnail = os.path.join( self.plugin_thumbnail_path, title + ".png" )
            if ( not os.path.isfile( thumbnail ) ):
                thumbnail = "DefaultFolder.png"    
        
        return thumbnail

    # raise a keyboard for user input
    def getUserInput(self, title = "Input", default="", hidden=False):
        result = None

        # Fix for when this functions is called with default=None
        if not default:
            default = ""
            
        keyboard = xbmc.Keyboard(default, title)
        keyboard.setHiddenInput(hidden)
        keyboard.doModal()
        
        if keyboard.isConfirmed():
            result = keyboard.getText()
        
        return result

    # converts the request url passed on by xbmc to our plugin into a dict  
    def getParameters(self, parameterString):
        commands = {}
        splitCommands = parameterString[parameterString.find('?')+1:].split('&')
        
        for command in splitCommands: 
            if (len(command) > 0):
                splitCommand = command.split('=')
                name = splitCommand[0]
                value = splitCommand[1]
                commands[name] = value
        
        return commands

    # generic function for building the item url filters out many item params to reduce unicode problems
    def buildItemUrl(self, item_params = {}, url = ""):
        for k, v in item_params.items():
            if (k != "path" and k != "thumbnail" and k!= "Title" ):
                url += k + "=" + str(v) + "&"
        return url

    def addContextMenuItems(self, params = {}, item_params = {}):
        cm = []
        get = params.get
        item = item_params.get

        title = self.makeAscii(item("Title"))
        url_title = urllib.quote_plus(title)
        
        if (item("videoid")): 
            if (self.pr_video_quality):
                cm.append( (self.__language__(30520), "XBMC.PlayMedia(%s?path=%s&action=play_video&quality=1080p&videoid=%s)" % ( sys.argv[0],  item("path"), item("videoid") ) ) )
                cm.append( (self.__language__(30521), "XBMC.PlayMedia(%s?path=%s&action=play_video&quality=720p&videoid=%s)" % ( sys.argv[0],  item("path"), item("videoid") ) ) )
                cm.append( (self.__language__(30522), "XBMC.PlayMedia(%s?path=%s&action=play_video&quality=SD&videoid=%s)" % ( sys.argv[0],  item("path"), item("videoid") ) ) )
            
            cm.append( ( self.__language__(30501), "XBMC.RunPlugin(%s?path=%s&action=download&videoid=%s)" % ( sys.argv[0],  item("path"), item("videoid") ) ) )

            if ( self.__settings__.getSetting( "username" ) != "" and self.__settings__.getSetting( "auth" ) ):
                if ( get("feed") == "favorites" and not get("contact") ):
                    cm.append( ( self.__language__( 30506 ), 'XBMC.RunPlugin(%s?path=%s&action=remove_favorite&editid=%s&)' % ( sys.argv[0], item("path"), item("editid") ) ) )
                else:
                    cm.append( ( self.__language__( 30503 ), 'XBMC.RunPlugin(%s?path=%s&action=add_favorite&videoid=%s&)' % ( sys.argv[0],  item("path"), item("videoid") ) ) )
                if (get("external") == "true" or (get("feed") != "subscriptions_favorites" and get("feed") != "subscriptions_uploads" and get("feed") != "subscriptions_playlists")):
                    cm.append( ( self.__language__( 30512 ) % item("Studio"), 'XBMC.RunPlugin(%s?path=%s&channel=%s&action=add_subscription)' % ( sys.argv[0], item("path"), item("Studio") ) ) )        

            studio = self.makeAscii(item("Studio","Unknown Author"))
            url_studio = urllib.quote_plus(studio)
            
            if (get("feed") != "subscriptions_favorites" and get("feed") != "subscriptions_uploads" and get("feed") != "subscriptions_playlists"):
                cm.append( ( self.__language__( 30516 ) % studio, "XBMC.Container.Update(%s?path=%s&feed=subscriptions_uploads&view_mode=subscriptions_uploads&channel=%s)" % ( sys.argv[0],  get("path"), url_studio ) ) )
            
            if (get("action") == "search_disco"):
                cm.append( ( self.__language__( 30523 ) % title, "XBMC.Container.Update(%s?path=%s&action=search_disco&search=%s)" % ( sys.argv[0],  get("path"), url_title ) ) )
            
            cm.append( ( self.__language__( 30514 ), "XBMC.Container.Update(%s?path=%s&action=search&search=%s)" % ( sys.argv[0],  get("path"), url_title ) ) )
            cm.append( ( self.__language__( 30529 ), "XBMC.Container.Update(%s?path=%s&action=list_related&videoid=%s)" % ( sys.argv[0],  get("path"), item("videoid") ) ) )
            cm.append( ( self.__language__( 30527 ), "XBMC.ActivateWindow(VideoPlaylist)"))
            cm.append( ( self.__language__( 30504 ), "XBMC.Action(Queue)", ) )
            cm.append( ( self.__language__( 30502 ), "XBMC.Action(Info)", ) )
        elif (item("next","false") == "false"):
            if (item("action") == "search"):
                cm.append( ( self.__language__( 30515 ), 'XBMC.Container.Update(%s?path=%s&action=edit_search&search=%s&)' % ( sys.argv[0], item("path"), item("search") ) ) )
                cm.append( ( self.__language__( 30505 ), 'XBMC.RunPlugin(%s?path=%s&action=refine_user&search=%s&)' % ( sys.argv[0], item("path"), item("search") ) ) )
                cm.append( ( self.__language__( 30508 ), 'XBMC.RunPlugin(%s?path=%s&action=delete_search&delete=%s&)' % ( sys.argv[0], item("path"), item("search") ) ) )
                try:
                    searches = eval(self.__settings__.getSetting("stored_searches_author"))
                except :
                    searches = {}
                
                if item("Title") in searches:
                    cm.append( ( self.__language__( 30500 ), 'XBMC.RunPlugin(%s?path=%s&action=delete_refinements&search=%s&)' % ( sys.argv[0], item("path"), item("search") ) ) )

            if (item("action") == "search_disco" and not get("scraper")):
                cm.append( ( self.__language__( 30524 ), 'XBMC.Container.Update(%s?path=%s&action=edit_disco&search=%s&)' % ( sys.argv[0], item("path"), item("search") ) ) )
                cm.append( ( self.__language__( 30525 ), 'XBMC.RunPlugin(%s?path=%s&action=delete_disco&delete=%s&)' % ( sys.argv[0], item("path"), item("search") ) ) )                                

            if (item("view_mode")):
                cm_url = 'XBMC.RunPlugin(%s?path=%s&channel=%s&action=change_subscription_view&view_mode=%s&' % ( sys.argv[0], item("path"), item("channel"), "%s")
                if (item("external")):
                    cm_url += "external=true&contact=" + get("contact") + "&"
                cm_url +=")"
            
                if (item("feed") == "subscriptions_favorites"):
                    cm.append ( (self.__language__( 30511 ), cm_url % ("subscriptions_uploads")))
                    cm.append( (self.__language__( 30528 ), cm_url % ("subscriptions_playlists")))
                elif(item("feed") == "subscriptions_playlists"):
                    cm.append( (self.__language__( 30511 ), cm_url % ("subscriptions_uploads"))) 
                    cm.append ( (self.__language__( 30510 ), cm_url % ("subscriptions_favorites")))
                elif (item("feed") == "subscriptions_uploads"):
                    cm.append ( (self.__language__( 30510 ), cm_url % ("subscriptions_favorites")))
                    cm.append( (self.__language__( 30528 ), cm_url % ("subscriptions_playlists")))

            if (item("channel")):
                if ( self.__settings__.getSetting( "username" ) != "" and self.__settings__.getSetting( "auth" ) ):
                    if (get("external")):
                        cm.append( ( self.__language__( 30512 ) % item("channel"), 'XBMC.RunPlugin(%s?path=%s&channel=%s&action=add_subscription)' % ( sys.argv[0], item("path"), item("channel") ) ) )
                    else:
                        cm.append( ( self.__language__( 30513 ) % item("channel"), 'XBMC.RunPlugin(%s?path=%s&editid=%s&action=remove_subscription)' % ( sys.argv[0], item("path"), item("editid") ) ) )
                    
            if (item("contact")):
                if ( self.__settings__.getSetting( "username" ) != "" and self.__settings__.getSetting( "auth" ) ):
                    if (item("external")):
                        cm.append( (self.__language__(30026), 'XBMC.RunPlugin(%s?path=%s&action=add_contact&)' % ( sys.argv[0], item("path") ) ) )
                    else:
                        cm.append( (self.__language__(30025), 'XBMC.RunPlugin(%s?path=%s&action=remove_contact&contact=%s&)' % ( sys.argv[0], item("path"), item("Title") ) ) )
                            
            if ( item("feed") == "favorites"  or get("feed") == "playlists" or item("feed") == "uploads" or item("feed") == "newsubscriptions" or (item("action") == "search_disco" and not get("scraper"))):
                cm.append( ( self.__language__( 30507 ), "XBMC.Action(Queue)" ) )
            
            cm.append( ( self.__language__( 30527 ), "XBMC.ActivateWindow(MusicPlaylist)"))
        return cm

    def makeAscii(self, str):
        try:
            return str.encode('ascii')
        except:
            if self.__dbg__:
                print self.__plugin__ + " makeAscii hit except on : " + repr(str)
            s = ""
            for i in str:
                try:
                    i.encode("ascii")
                except:
                    continue
                else:
                    s += i
            return s

    def errorHandling(self, title = "", result = "", status = 500):
        if title == "":
            title = self.__language__(30600)
        if result == "":
            result = self.__language__(30617)
            
        if ( status == 303):
            self.showMessage(title, result)
        elif ( status == 500):
            self.showMessage(title, self.__language__(30606))
        elif ( status != 0):
            self.showMessage(title, self.__language__(30617))

    def ip2str(self, ip):
        return '%d.%d.%d.%d' % (ip >> 24, (ip >> 16) & 0xff, (ip >> 8) & 0xff, ip & 0xff)

    def id2str(self, id):
        return '%08X' % id
