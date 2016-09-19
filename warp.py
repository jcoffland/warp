#!/usr/bin/python

import wx
import random
import time
import math
import copy

# Must be first
app = wx.PySimpleApp()

class Main(wx.Frame):
    def __init__(self, size = wx.DisplaySize()):
        self.size = size
        self.width = width = 32.0
        self.hx = hx = self.size[0] * 0.5
        self.hy = hy = self.size[1] * 0.5
        self.cycle = False

        wx.Frame.__init__(self, None, wx.ID_ANY, 'Warp',
                          pos = (0, 0), size = self.size)

        # Setup screen
        self.Bind(wx.EVT_LEFT_DOWN, self.Quit)
        self.ShowFullScreen(True, style = wx.FULLSCREEN_ALL)
        self.Show(True)

        self.make_sides()
        self.make_clip()

        # Setup dubble buffer
        self.buffer = wx.EmptyBitmap(self.size[0], self.size[1])
        self.offset = 0
        self.sides = 3
        self.count = 0

        # Start draw timer
        self.timer = wx.Timer(self, 1)
        self.timer.Start(10)
        wx.EVT_TIMER(self, 1, self.run)


    def make_sides(self):
        width = self.width
        qw = width * 0.25
        hx = self.hx + width
        hy = self.hy + width

        # Make left side
        self.buffer = wx.EmptyBitmap(self.hx + self.width, self.size[1])
        self.dcLeft = dc = wx.MemoryDC(self.buffer)

        # Setup DC
        dc.SetBrush(wx.Brush('white'))
        dc.SetBackground(wx.Brush('black'))
        dc.Clear()

        # Draw the bars
        x1 = x2 = y1 = y2 = 0
        while x2 <= hx or y2 <= hy:
            if x1 <= hx: x1 += width
            else: y2 += width
            if y1 <= hy: y1 += width
            else: x2 += width

            dc.DrawPolygon(
                [wx.Point(x2, y1 - qw), wx.Point(x1 - qw, y2),
                 wx.Point(x1 + qw, y2), wx.Point(x2, y1 + qw)])

        img = self.buffer.ConvertToImage()
        img = img.Mirror(False)
        bDC = wx.MemoryDC(img.ConvertToBitmap())
        dc.Blit(0, self.hy, self.hx + width, self.hy, bDC, 0, self.hy)

        # Make right side
        img = self.buffer.ConvertToImage()
        img = img.Mirror()
        self.dcRight = wx.MemoryDC(img.ConvertToBitmap())


    def make_clip(self, sides = 64):
        points = []
        radius = self.hy * 0.5
        
        step = 2 * math.pi / sides
        for i in range(sides):
            t = step * i
            if i % 2: r = radius
            else: r = radius * 0.5
            points.append(wx.Point(self.hx + r * math.cos(t),
                                   self.hy + r * math.sin(t)))

        self.clip = wx.RegionFromPoints(points)


    def cycle_clip(self):
        if self.count == 256:
            self.count = 0

            if self.sides >= 64: self.sides = 4
            else: self.sides *= 2
            self.make_clip(self.sides)

        else: self.count += 1


    def run(self, event):
        if self.cycle: self.cycle_clip()

        dc = wx.BufferedPaintDC(self, self.buffer)

        dc.Blit(0, 0, self.hx, self.size[1], self.dcLeft, self.offset, 0)
        dc.Blit(self.hx, 0, self.hx, self.size[1], self.dcRight,
                self.width - self.offset, 0)

        dc.SetClippingRegionAsRegion(self.clip)

        dc.Blit(0, 0, self.hx, self.size[1], self.dcLeft,
                self.width - self.offset, 0)
        dc.Blit(self.hx, 0, self.hx, self.size[1], self.dcRight,
                self.offset, 0)

        if self.offset == self.width: self.offset = 0
        else: self.offset += 1


    def Quit(self, event):
        self.timer.Stop()
        self.Destroy()


size = wx.DisplaySize()
window = Main(size)
app.MainLoop()

