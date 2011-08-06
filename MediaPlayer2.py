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

import xbmc
import dbus
import dbus.service

Playback_Status = [ "Playing", "Paused", "Stopped" ]
Loop_Status = [ 
                "None",     # if the playback will stop when there are no more tracks to play
                "Track",    # if the current track will start again from the begining once it has finished playing
                "Playlist"  # if the playback loops through a list of tracks
              ]

""" Metadata map
# Required
  s   mpris:trackid
  l   mpris:length
  s   xesam:url
  s   xesam:title
  s   xesam:album
# Optional
  as  xesam:artist
  as  xesam:albumArtist
  as  xesam:genre
  as  xesam:comment
  i   xesam:trackNUmber
  s   xesam:contentCreated
  s   mpris:artUrl
"""

def log(msg):
  xbmc.log("mpris::%s" % msg,level=xbmc.LOGDEBUG )

class Service(dbus.service.Object, xbmc.Player):
  def __init__(self):
    xbmc.Player.__init__(self)
    bus_name = dbus.service.BusName('org.mpris.MediaPlayer2.xbmc', bus=dbus.SessionBus())
    dbus.service.Object.__init__(self, bus_name, '/org/mpris/MediaPlayer2')

    self.Playlist = None

    # Defaults of the MediaPlayer2 properties
    self.CanQuit = False
    self.CanRaise = False
    self.HasTrackList = False
    self.Identity = 'xbmc'
    self.DesktopEntry = 'xbmc'
    self.SupportedUriSchemes = [ 'file' ]
    self.SupportedMimeTypes = [ 'audio/mpeg' ]

    # Defaults of the MediaPlayer2.Player
    self.PlaybackStatus = 'Stopped'
    self.LoopStatus = 'None'
    self.Rate = 1.0
    self.Shuffle = False
    self.Metadata = {
                      'mpris:trackid': '',
#                      "mpris:length": int(0),
                      'xesam:url': '',
                      'xesam:title"': '',
                      'xesam:album': ''
                    }
    self.Volume = 1.0
    self.Position = 0
    self.MinimumRate = 1.0
    self.MaximumRate = 1.0
    self.CanGoNext = False
    self.CanGoPrevious = False
    self.CanPlay = False
    self.CanPause = False
    self.CanSeek = False
    self.CanControl = True

    # Fill in real properties
    if self.isPlaying():
      self.onPlaybackStarted()

  # org.mpres.MediaPlayer2 Methods
  @dbus.service.method('org.mpris.MediaPlayer2')
  def Raise(self):
    raise NotImplementedError("@dbus.service.method('org.mpris.MediaPlayer2') Raise != implemented by this player.")

  @dbus.service.method('org.mpris.MediaPlayer2')
  def Quit(self):
    xbmc.executebuiltin('Quit()')

  # org.mpris.MediaPlayer2.Player Methods
  @dbus.service.method('org.mpris.MediaPlayer2.Player')
  def Next(self):
    self.playnext()

  @dbus.service.method('org.mpris.MediaPlayer2.Player')
  def Previous(self):
    self.playprevious()

  @dbus.service.method('org.mpris.MediaPlayer2.Player')
  def Pause(self):
    self.pause()

  @dbus.service.method('org.mpris.MediaPlayer2.Player')
  def PlayPause(self):
    xbmc.executebuiltin('PlayerControl(Play)')

  @dbus.service.method('org.mpris.MediaPlayer2.Player')
  def Stop(self):
    self.stop()

  @dbus.service.method('org.mpris.MediaPlayer2.Player')
  def Play(self):
    if self.PlaybackStatus != 'Playing':
      xbmc.executebuiltin('PlayerControl(Play)')

  @dbus.service.method('org.mpris.MediaPlayer2.Player', in_signature='x')
  def Seek(self, Offset):
    raise NotImplementedError("@dbus.service.method('org.mpris.MediaPlayer2.Seek') Next != implemented by this player.")

  @dbus.service.method('org.mpris.MediaPlayer2.Player', in_signature='ox')
  def SetPosition(self, TrackId, Position):
    raise NotImplementedError("@dbus.service.method('org.mpris.MediaPlayer2.SetPosition') Next != implemented by this player.")

  @dbus.service.method('org.mpris.MediaPlayer2.Player', in_signature='s')
  def OpenUri(self, Uri):
    self.play(Uri)

  # XBMC callbacks
  def onPlayBackStarted(self):
    log('onPlaybackStarted')
    if self.isPlaying():
      log('isPlaying')
      self.SetInternal('org.mpris.MediaPlayer2.Player', 'PlaybackStatus', 'Playing')

      if self.isPlayingAudio():
        self._UpdatePlayerPropertiesAudio(self.getMusicInfoTag())
      elif player.isPlayingVideo():
        self._UpdatePlayerPropertiesVideo(self.getVideoInfoTag())
      else:
        xbmc.log("org.mpris.MediaPlayer2::onPlayBackStarted called but is neither playing Audio or Video", level=xbmc.LOGERROR)
    else:
      xbmc.log("org.mpris.MediaPlayer2::onPlayBackStarted called but is not playing", level=xbmc.LOGERROR)

  def _UpdatePlayerPropertiesAudio(self, tag):
    self.Playlist = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
    log("Playlist.size = " + str(self.Playlist.size()))
    log("Playlist.getposition() = " + str(self.Playlist.getposition()))
    if tag != None:
      self.SetInternal('org.mpris.MediaPlayer2.Player', 'Rate', 1.0)
      self.SetInternal('org.mpris.MediaPlayer2.Player', 'Shuffle', False)
      self.SetInternal('org.mpris.MediaPlayer2.Player', 'Metadata', {
                                                                      'mpris:trackid': '',
                                                                      'xesam:url': tag.getURL(),
                                                                      'xesam:title"': tag.getTitle(),
                                                                      'xesam:album': tag.getAlbum()
                                                                    } )
      self.SetInternal('org.mpris.MediaPlayer2.Player', 'CanGoPrevious', self.Playlist.getposition() > 0)
      self.SetInternal('org.mpris.MediaPlayer2.Player', 'CanGoNext', (self.Playlist.getposition() + 1) < self.Playlist.size())
      self.SetInternal('org.mpris.MediaPlayer2.Player', 'CanPause', True)
      self.SetInternal('org.mpris.MediaPlayer2.Player', 'CanSeek', False)
    else:
      xbmc.log("org.mpris.MediaPlayer2::UpdatePlayerPropertiesAudio called without tag", level=xbmc.LOGERROR)

  def _UpdatePlayerPropertiesVideo(self, tag):
    self.Playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    if tag != None:
      self.SetInternal('org.mpris.MediaPlayer2.Player', 'Rate', 1.0)
      self.SetInternal('org.mpris.MediaPlayer2.Player', 'Shuffle', False)
      self.SetInternal('org.mpris.MediaPlayer2.Player', 'Metadata', {
                                                                      'mpris:trackid': '',
                                                                      'xesam:url': tag.getURL(),
                                                                      'xesam:title"': tag.getTitle(),
                                                                      'xesam:album': ''
                                                                    } )
      self.SetInternal('org.mpris.MediaPlayer2.Player', 'CanGoPrevious', self.Playlist.getposition() > 0)
      self.SetInternal('org.mpris.MediaPlayer2.Player', 'CanGoNext', (self.Playlist.getposition() + 1) < self.Playlist.size())
      self.SetInternal('org.mpris.MediaPlayer2.Player', 'CanPause', True)
      self.SetInternal('org.mpris.MediaPlayer2.Player', 'CanSeek', False)
    else:
      xbmc.log("org.mpris.MediaPlayer2::UpdatePlayerPropertiesVideo called without tag", level=xbmc.LOGERROR)

  def onPlayBackStopped(self):
    self.onPlayBackEnded()

  def onPlayBackEnded(self):
    self.Playlist = None
    self.SetInternal('org.mpris.MediaPlayer2.Player', 'PlaybackStatus', 'Stopped')
    self.SetInternal('org.mpris.MediaPlayer2.Player', 'LoopStatus', 'None')
    self.SetInternal('org.mpris.MediaPlayer2.Player', 'Rate', 1.0)
    self.SetInternal('org.mpris.MediaPlayer2.Player', 'Shuffle', False)
    self.SetInternal('org.mpris.MediaPlayer2.Player', 'Metadata', { 'mpris:trackid': '', 'xesam:url': '', 'xesam:title"': '', 'xesam:album': '' })
    self.SetInternal('org.mpris.MediaPlayer2.Player', 'CanGoPrevious', False)
    self.SetInternal('org.mpris.MediaPlayer2.Player', 'CanGoNext', False)
    self.SetInternal('org.mpris.MediaPlayer2.Player', 'CanPause', False)
    self.SetInternal('org.mpris.MediaPlayer2.Player', 'CanSeek', False)

  def onPlayBackPaused(self):
    self.SetInternal('org.mpris.MediaPlayer2.Player', 'PlaybackStatus', 'Paused')

  def onPlayBackResumed(self):
    self.SetInternal('org.mpris.MediaPlayer2.Player', 'PlaybackStatus', 'Playing')

  # org.freedesktop.DBus.Properties methods
  @dbus.service.signal(dbus_interface=dbus.PROPERTIES_IFACE, signature='sa{sv}as')
  def PropertiesChanged(self, interface_name, changed_properties, invalidated_properties):
    pass

  @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ss', out_signature='v')
  def Get(self, interface_name, property_name):
    return getattr(self, property_name)

  @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='s', out_signature='a{sv}')
  def GetAll(self, interface_name):
    if interface_name == "org.mpris.MediaPlayer2":
      return {
                "CanQuit": self.CanQuit,
                "HasTrackList": self.HasTrackList,
                "Identity": self.Identity,
                "DesktopEntry": self.DesktopEntry,
                "SupportedUriSchemes": self.SupportedUriSchemes,
                "SupportedMimeTypes": self.SupportedMimeTypes,
             }
    elif interface_name == "org.mpris.MediaPlayer2.Player":
      return {
                "PlaybackStatus": self.PlaybackStatus,
                "LoopStatus": self.LoopStatus,
                "Rate": self.Rate,
                "Shuffle": self.Shuffle,
                "Metadata": self.Metadata,
                "Volume": self.Volume,
                "Position": self.Position,
                "LoopStatus": self.LoopStatus,
                "MinimumRate": self.MinimumRate,
                "MaximumRate": self.MaximumRate,
                "CanGoNext": self.CanGoNext,
                "CanGoPrevious": self.CanGoPrevious,
                "CanPlay": self.CanPlay,
                "CanPause": self.CanPause,
                "CanSeek": self.CanSeek,
                "CanControl": self.CanControl,
             }
    else:
      xbmc.log("org.mpris.MediaPlayer2::GetAll called with bad interface '%s'" % interface_name, level=xbmc.LOGERROR)
      raise NotImplementedError("@dbus.service.method('" + dbus.PROPERTIES_IFACE + ".GetAll') called with bad interface '" + interface_name + "')")

  @dbus.service.method(dbus.PROPERTIES_IFACE, in_signature='ssv')
  def Set(self, interface_name, property_name, value):
    if interface_name == "org.mpris.MediaPlayer2.Player":
      if (property_name == 'LoopStatus' or property_name == 'Rate' or property_name == 'Shuffle' or property_name == 'Volume'):
        self.SetInternal(interface_name, property_name, value)
      else:
        xbmc.log("org.mpris.MediaPlayer2::Set called with bad property '%s' on interface '%s'" % (property_name,interface_name), level=xbmc.LOGERROR)
    else:
      xbmc.log("org.mpris.MediaPlayer2::Set called with bad interface '%s'" % interface_name, level=xbmc.LOGERROR)

  def SetInternal(self, interface_name, property_name, value):
    if interface_name == "org.mpris.MediaPlayer2":
      if property_name == 'CanQuit' and self.CanQuit != value:
        self.CanQuit = value
      elif property_name == 'HasTrackList' and self.HasTrackList != value:
        self.HasTrackList = value
      elif property_name == 'Identity' and self.Identity != value:
        self.Identity = value
      elif property_name == 'DesktopEntry' and self.DesktopEntry != value:
        self.DesktopEntry = value
      elif property_name == 'SupportedUriSchemes' and self.SupportedUriSchemes != value:
        self.SupportedUriSchemes = value
      elif property_name == 'SupportedMimeTypes' and self.SupportedMimeTypes != value:
        self.SupportedMimeTypes = value
      else:
        return False
    elif interface_name == "org.mpris.MediaPlayer2.Player":
      if property_name == 'PlaybackStatus' and self.PlaybackStatus != value:
        self.PlaybackStatus = value
      elif property_name == 'HasTrackList' and self.HasTrackList != value:
        self.HasTrackList = value
      elif property_name == 'LoopStatus' and self.LoopStatus != value:
        # TODO actually set the LoopStatus
        self.LoopStatus = value
      elif property_name == 'Rate' and self.Rate != value:
        # TODO actually set Rate
        self.Rate = value
      elif property_name == 'Shuffle' and self.Shuffle != value and self.Playlist != None:
        if self.Shuffle:
          self.Playlist.unshuffle()
        else:
          self.Playlist.shuffle()
        self.Shuffle = value
      elif property_name == 'Metadata' and self.Metadata != value:
        self.Metadata = value
      elif property_name == 'Volume' and self.Volume != value:
        self.Volume = value
        # TODO actually set Volume
      elif property_name == 'Position' and self.Position != value:
        self.Position = value
      elif property_name == 'MinimumRate' and self.MinimumRate != value:
        self.MinimumRate = value
      elif property_name == 'MaximumRate' and self.MaximumRate != value:
        self.MaximumRate = value
      elif property_name == 'CanGoNext' and self.CanGoNext != value:
        self.CanGoNext = value
      elif property_name == 'CanGoPrevious' and self.CanGoPrevious != value:
        self.CanGoPrevious = value
      elif property_name == 'CanPlay' and self.CanPlay != value:
        self.CanPlay = value
      elif property_name == 'CanPause' and self.CanPause != value:
        self.CanPause = value
      elif property_name == 'CanSeek' and self.CanSeek != value:
        self.CanSeek = value
      elif property_name == 'CanControl' and self.CanControl != value:
        self.CanControl = value
      else:
        return False
    else:
      xbmc.log("org.mpris.MediaPlayer2::SetInternal called with bad interface '%s'" % interface_name, level=xbmc.LOGERROR)
      return False

    xbmc.log("org.mpris.MediaPlayer2::SetInternal alters value of property '%s' on interface '%s'" % (property_name,interface_name), level=xbmc.LOGDEBUG)
    self.PropertiesChanged(interface_name, { property_name: value }, [])

    return True
