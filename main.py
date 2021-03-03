#import sys
import pygame
#from pygame.locals import *
import tkinter as TK
from tkinter.filedialog import askopenfilename

class Player(TK.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, borderwidth = 3, relief = TK.RIDGE) 
        self.__parent = parent
        self.__pg_mixer = kwargs.get('pygame_mixer', None)

        self.volume = 0.5
        self.volume_resolution = .01
        self.paused = False
        self.fileName = ""
        self.sound = None

        self.pause_fdo_begin = False
        self.pause_fdo_ms = 500
        self.pause_fdo_steps = 0
        self.pause_fdo_dec = 0.0
        self.pause_fdo_end = None

        self.channelId = kwargs.get('channel_id', None)
        if (self.channelId == None): return None
        self.channel = self.__pg_mixer.Channel(self.channelId)

        self.lblId = TK.Label(self, text = self.channelId)
        self.lblId.pack(side = TK.LEFT, padx = 2, pady = 1)

        self.btnPlay = TK.Button(self, text = '>', command = self.btnPlay_on_click)
        self.btnPlay.pack(side = TK.LEFT, padx = 2, pady = 1)

        self.btnPause = TK.Button(self, text = '||', command = self.btnPause_on_click)
        self.btnPause.pack(side = TK.LEFT, padx = 2, pady = 1)

        self.btnStop = TK.Button(self, text = '[]', command = self.btnStop_on_click)
        self.btnStop.pack(side = TK.LEFT, padx = 2, pady = 1)

        self.sclVol = TK.Scale(self, orient = "horizontal", from_ = 0, to = 1, resolution = self.volume_resolution, showvalue = 0, command = self.sclVol_change)
        self.sclVol.set(self.volume)
        self.sclVol.pack(side = TK.LEFT, padx = 2)

        self.lblFileName = TK.Label(self, width = 100, text = "", justify = TK.LEFT)
        self.lblFileName.pack(side = TK.LEFT, padx = 2, pady = 1)

        self.btnOpen = TK.Button(self, text = '^', command = self.btnOpen_on_click)
        self.btnOpen.pack(side = TK.LEFT, padx = 3, pady = 1)

        #self.btnPlay.bind('<Button-1>', self.btnPlay_on_click)
        #self.btnStop.bind('<Button-1>', self.btnStop_on_click)
        #self.btnOpen.bind('<Button-1>', self.btnStop_on_click)

    def get_id(self):
        return self.channelId

    def on_tick(self):
        # pause fadeout
        if (self.pause_fdo_begin):
            if (self.pause_fdo_steps):
                self.pause_fdo_steps -= 1
                new_vol = self.channel.get_volume() - self.pause_fdo_dec
                if (new_vol > self.volume):
                    new_vol = self.volume
                elif (new_vol < 0):
                    new_vol = 0.0
                self.channel.set_volume(new_vol)
                print("new_vol=", new_vol)
            else:
                self.pause_fdo_end()
        # color setup
        color = "snow"
        if (self.channel.get_busy()):
            color = "pale green"
            if (self.paused):
                color = "yellow"
        self.lblFileName.config(bg = color)

    def open_file(self):
        fn = askopenfilename()
        print("open_file.fn=", fn)
        if (fn):
            self.fileName = fn
            #self.fldFileName_set(self.fileName)
            self.lblFileName.config(text = self.fileName)
            self.stop() 
            self.sound = self.__pg_mixer.Sound(file = self.fileName)

    def play(self):
        if (self.sound):
            # pause all other channels
            self.__parent.faded_pause_all(self.channelId)
            self.channel.play(self.sound) #, fade_ms = self.fadein_ms)
            self.channel.set_volume(self.volume)
            self.paused = False

    def faded_play(self):
        self.play()
        self.pause()
        self.faded_unpause()

    def pause(self):
        if (self.is_playing() and not self.paused):
            self.channel.pause()
            self.paused = True

    def faded_pause(self):
        if (self.is_playing() and not self.paused):
            # init fadeout
            self.pause_fdo_ms = self.__parent.get_fadeout()
            if (self.pause_fdo_ms < self.__parent.get_tick_interval()):
                self.pause()
                return
            self.pause_fdo_steps = int(self.pause_fdo_ms / self.__parent.get_tick_interval())
            self.pause_fdo_dec = self.volume / self.pause_fdo_steps
            self.pause_fdo_end = self.faded_pause_end
            self.pause_fdo_begin = True

    def faded_pause_end(self):
        self.pause_fdo_ms = 0
        self.pause_fdo_steps = 0
        self.pause_fdo_dec = 0.0
        self.pause_fdo_begin = False
        self.pause_fdo_end = None
        self.pause()

    def faded_unpause(self):
        if (self.is_playing() and self.paused):
            # init fadeout
            self.pause_fdo_ms = self.__parent.get_fadeout()
            if (self.pause_fdo_ms < self.__parent.get_tick_interval()):
                self.unpause()
                return
            self.pause_fdo_steps = int(self.pause_fdo_ms / self.__parent.get_tick_interval())
            self.pause_fdo_dec = -(self.volume / self.pause_fdo_steps)
            self.pause_fdo_end = self.faded_unpause_end
            self.unpause()
            self.channel.set_volume(0.0)
            self.pause_fdo_begin = True


    def faded_unpause_end(self):
        self.pause_fdo_ms = 0
        self.pause_fdo_steps = 0
        self.pause_fdo_dec = 0.0
        self.pause_fdo_begin = False
        self.pause_fdo_end = None
        self.channel.set_volume(self.volume)

    def unpause(self):
        if (self.is_playing() and self.paused):
            # pause all other channel
            self.__parent.faded_pause_all(self.channelId)
            self.channel.set_volume(self.volume)
            self.channel.unpause()
            self.paused = False

    def togle_pause(self):
        if (self.paused): 
            self.faded_unpause()
        else:
            #self.pause()
            self.faded_pause()

    def stop(self):
        if (self.channel.get_busy()):
            if (self.paused):
                self.unpause()
                self.channel.stop()
            else:
                self.channel.fadeout(self.__parent.get_fadeout())

    def is_playing(self):
        return self.channel.get_busy()

    def set_volume(self, volume):
        #print(self.channelId, volume)
        self.volume = volume
        if (self.channel.get_busy() or self.paused):
            self.channel.set_volume(self.volume)

    def inc_volume(self):
        vol = self.volume + self.volume_resolution
        if (vol > 1): vol = 1.0
        self.sclVol.set(vol)

    def dec_volume(self):
        vol = self.volume - self.volume_resolution
        if (vol < 0): vol = 0.0
        self.sclVol.set(vol)

    def btnPlay_on_click(self):
        self.faded_play()

    def btnPause_on_click(self):
        self.togle_pause()
        
    def btnStop_on_click(self):
        self.stop()

    def btnOpen_on_click(self):
        self.open_file()

    def sclVol_change(self, value):
        self.set_volume(float(value))


class PlayerList(TK.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, relief = TK.SUNKEN, borderwidth = 3) 

        self.__pg_mixer = kwargs.get('pygame_mixer', None)
        self.__parent = parent
        self.__tick_interval = 100
        self.__next_channel_id = 0
        self.__fadeout_ms = 500
        self.__fadein_ms = 500
        self.__players = []

        self.cur_player_id = None

        self.frControl = TK.Frame()
        self.frControl.pack(side = TK.TOP)

        self.lblFadeout = TK.Label(self.frControl, text = "Fadeout (ms)")
        self.lblFadeout.pack(side = TK.LEFT, padx = 1, pady = 1)
        self.sclFadeout = TK.Scale(self.frControl, orient = "horizontal", from_ = 0, to = 5000, resolution = 100, command = self.sclFadeout_change)
        self.sclFadeout.pack(side = TK.LEFT, padx = 3, pady = 1)
        self.sclFadeout.set(self.__fadeout_ms)

        self.fill_players()

        self.tick()

    def tick(self):
        for pl in self.__players:
            pl.on_tick()
        self.after(self.__tick_interval, self.tick)

    def get_tick_interval(self):
        return self.__tick_interval

    def get_fadeout(self):
        return self.__fadeout_ms

    def stop_all(self, exclude_id = None):
        for pl in self.__players:
            if (exclude_id != pl.get_id()):
                pl.stop()

    def pause_all(self, exclude_id = None):
        for pl in self.__players:
            if (exclude_id != pl.get_id()):
                pl.pause()

    def play_current(self):
        if (not self.cur_player_id == None):
            self.__players[self.cur_player_id].play()

    def togle_pause_current(self):
        if (not self.cur_player_id == None):
            self.__players[self.cur_player_id].togle_pause()

    def stop_current(self):
        if (not self.cur_player_id == None):
            self.__players[self.cur_player_id].stop()

    def inc_vol_current(self):
        if (not self.cur_player_id == None):
            self.__players[self.cur_player_id].inc_volume()

    def dec_vol_current(self):
        if (not self.cur_player_id == None):
            self.__players[self.cur_player_id].dec_volume()

    def faded_pause_all(self, exclude_id = None):
        for pl in self.__players:
            if (exclude_id != pl.get_id()):
                pl.faded_pause()

    def fill_players(self):
        for i in range(self.__pg_mixer.get_num_channels()):
            pl = Player(self, pygame_mixer = self.__pg_mixer, channel_id = i)
            pl.pack(side = TK.TOP)
            self.__players.append(pl)

    def field_set(self, field, text):
        field.delete(0, TK.END)
        field.insert(0, text)

    def sclFadeout_change(self, value):
        self.__fadeout_ms = int(value)

    def on_key(self, event):
        print("on_key.event=", event)
        if (event.keycode >= 48 and event.keycode <= 57):
            # keys 0 - 1
            self.cur_player_id = event.keycode - 48

        elif (event.keycode == 32):
            # space - togle pause
            self.togle_pause_current()

        elif (event.keycode == 80):
            # p - play
            self.play_current()

        elif (event.keycode == 83):
            # s - stop
            self.stop_current()
 
        elif (event.keycode == 38):
            # up arrow - volume increase
            self.inc_vol_current()
 
        elif (event.keycode == 40):
            # down arrow - volume decrease
            self.dec_vol_current()


def main():
    pygame.mixer.init()
    pygame.mixer.set_num_channels(10)
    print('channels=', pygame.mixer.get_num_channels())
    root = TK.Tk()
    plList = PlayerList(root, pygame_mixer = pygame.mixer)
    plList.pack()

    root.bind("<Key>", plList.on_key)
    root.mainloop()

if __name__ == '__main__':
    main()
