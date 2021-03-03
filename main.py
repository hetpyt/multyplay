import sys
import pygame
from pygame.locals import *
import tkinter as TK
from tkinter.filedialog import askopenfilename

def play():
    s1 = pygame.mixer.Sound(file="./test/1.mp3")
    s1.set_volume(0.2)
    s1.play()

class Player(TK.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, borderwidth = 3, relief = TK.RIDGE) 
        self.__parent = parent

        self.volume = 0.5
        self.paused = False
        self.fileName = ""
        self.sound = None

        self.channelId = kwargs.get('channel_id', None)
        if (self.channelId == None): return None
        self.channel = pygame.mixer.Channel(self.channelId)

        self.btnPlay = TK.Button(self, text = '>', command = self.btnPlay_on_click)
        self.btnPlay.pack(side = TK.LEFT, padx = 2, pady = 1)

        self.btnPause = TK.Button(self, text = '||', command = self.btnPause_on_click)
        self.btnPause.pack(side = TK.LEFT, padx = 2, pady = 1)

        self.btnStop = TK.Button(self, text = '[]', command = self.btnStop_on_click)
        self.btnStop.pack(side = TK.LEFT, padx = 2, pady = 1)

        self.sclVol = TK.Scale(self, orient = "horizontal", from_ = 0, to = 1, resolution = 0.01, showvalue = 0, command = self.sclVol_change)
        self.sclVol.set(self.volume)
        self.sclVol.pack(side = TK.LEFT, padx = 2)


        self.fldFileName = TK.Entry(self, width = 100)
        self.fldFileName.pack(side = TK.LEFT, padx = 3, pady = 1)

        self.btnOpen = TK.Button(self, text = '^', command = self.btnOpen_on_click)
        self.btnOpen.pack(side = TK.LEFT, padx = 3, pady = 1)

        #self.btnPlay.bind('<Button-1>', self.btnPlay_on_click)
        #self.btnStop.bind('<Button-1>', self.btnStop_on_click)
        #self.btnOpen.bind('<Button-1>', self.btnStop_on_click)


    def on_tick(self):
        #print("on_tick id=", self.channelId)
        color = "snow"
        if (self.channel.get_busy()):
            color = "pale green"
            if (self.paused):
                color = "yellow"
        self.fldFileName.config(bg = color)

    def open_file(self):
        fn = askopenfilename()
        print("open_file.fn=", fn)
        if (fn):
            self.fileName = fn
            self.fldFileName_set(self.fileName)
            self.stop() 
            self.sound = pygame.mixer.Sound(file = self.fileName)

    def play(self):
        if (self.sound and not self.channel.get_busy()):
            self.channel.play(self.sound) #, fade_ms = self.fadein_ms)
            self.channel.set_volume(self.volume)
            self.paused = False
            
    def stop(self):
        if (self.channel.get_busy()):
            self.channel.fadeout(self.__parent.get_fadeout())

    def is_playing(self):
        return self.channel.get_busy()

    def set_volume(self, volume):
        #print(self.channelId, volume)
        self.volume = volume
        if (self.channel.get_busy() or self.paused):
            self.channel.set_volume(self.volume)

    def fldFileName_set(self, text):
        self.fldFileName.delete(0, TK.END)
        self.fldFileName.insert(0, text)

    def btnPlay_on_click(self):
        self.play()

    def btnPause_on_click(self):
        if (self.paused): 
            self.channel.unpause()
            self.paused = False
        else:
            self.channel.pause()
            self.paused = True

    def btnStop_on_click(self):
        self.stop()

    def btnOpen_on_click(self):
        self.open_file()

    def sclVol_change(self, value):
        self.set_volume(float(value))

class PlayerList(TK.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, relief = TK.SUNKEN, borderwidth = 3) #, width = self.canvas_width, height = self.canvas_height)
        self.parent = parent
        self.__next_channel_id = 0
        self.__fadeout_ms = 500
        self.__fadein_ms = 500
        self.__players = []

        self.frControl = TK.Frame()
        self.frControl.pack(side = TK.TOP)

        self.lblFadeout = TK.Label(self.frControl, text = "Fadeout (ms)")
        self.lblFadeout.pack(side = TK.LEFT, padx = 1, pady = 1)
        self.sclFadeout = TK.Scale(self.frControl, orient = "horizontal", from_ = 0, to = 5000, resolution = 100, command = self.sclFadeout_change)
        self.sclFadeout.pack(side = TK.LEFT, padx = 3, pady = 1)
        self.sclFadeout.set(self.__fadeout_ms)

        self.tick()

    def init(self):
        #self.set_players_volume()
        pass

    def tick(self):
        for pl in self.__players:
            pl.on_tick()
        self.after(200, self.tick)

    def get_fadeout(self):
        return self.__fadeout_ms

    def next_channel(self):
        result = self.__next_channel_id
        self.__next_channel_id += 1
        if (self.__next_channel_id >= pygame.mixer.get_num_channels()):
            self.__next_channel_id = None
        return result

    def fill_players(self):
        for i in range(pygame.mixer.get_num_channels()):
            pl = Player(self, channel_id = self.next_channel())
            pl.pack(side = TK.BOTTOM)
            self.__players.append(pl)

    def field_set(self, field, text):
        field.delete(0, TK.END)
        field.insert(0, text)

    def sclFadeout_change(self, value):
        self.__fadeout_ms = int(value)

def main():
    pygame.init()
    print('channels=', pygame.mixer.get_num_channels())
    root = TK.Tk()
    #play()
    plList = PlayerList(root)
    plList.pack()
    plList.fill_players()
    plList.init()

    root.mainloop()


if __name__ == '__main__':
    main()
