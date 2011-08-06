# *  This Program is free software; you can redistribute it and/or modify
# *  it under the terms of the GNU General Public License as published by
# *  the Free Software Foundation; either version 2, or (at your option)
# *  any later version.
# *
# *  This Program is distributed in the hope that it will be useful,
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *  GNU General Public License for more details.
# *
# *  You should have received a copy of the GNU General Public License
# *  along with XBMC; see the file COPYING.  If not, write to
# *  the Free Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# *  http://www.gnu.org/copyleft/gpl.html

import os
import sys
import time
import xbmcaddon, xbmc
import dbus
import dbus.service
from dbus.mainloop.glib import DBusGMainLoop
import gobject
import MediaPlayer2

__scriptname__ = "mpris"
__author__     = "topfs2"
__settings__   = xbmcaddon.Addon()
__language__   = __settings__.getLocalizedString
__cwd__        = __settings__.getAddonInfo('path')
__layoutDir__  = xbmc.translatePath( os.path.join( __cwd__, 'resources', 'layout' ) )

def log(msg):
  xbmc.log("%s::%s" % (__scriptname__,msg,),level=xbmc.LOGDEBUG )

DBusGMainLoop(set_as_default=True)
loop = gobject.MainLoop()
myservice = MediaPlayer2.Service()
context = loop.get_context()

while (not xbmc.abortRequested):
  context.iteration(False)
  xbmc.sleep(100)

log("exiting")
