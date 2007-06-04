import wx
from math import pi

from PieCtrl import PieCtrl, ProgressPie, PiePart

#----------------------------------------------------------------------
# Get Some Icon/Data
#----------------------------------------------------------------------

def GetMondrianData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00 \x00\x00\x00 \x08\x06\x00\
\x00\x00szz\xf4\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00\x00qID\
ATX\x85\xed\xd6;\n\x800\x10E\xd1{\xc5\x8d\xb9r\x97\x16\x0b\xad$\x8a\x82:\x16\
o\xda\x84pB2\x1f\x81Fa\x8c\x9c\x08\x04Z{\xcf\xa72\xbcv\xfa\xc5\x08 \x80r\x80\
\xfc\xa2\x0e\x1c\xe4\xba\xfaX\x1d\xd0\xde]S\x07\x02\xd8>\xe1wa-`\x9fQ\xe9\
\x86\x01\x04\x10\x00\\(Dk\x1b-\x04\xdc\x1d\x07\x14\x98;\x0bS\x7f\x7f\xf9\x13\
\x04\x10@\xf9X\xbe\x00\xc9 \x14K\xc1<={\x00\x00\x00\x00IEND\xaeB`\x82' 

def GetMondrianBitmap():
    return wx.BitmapFromImage(GetMondrianImage())

def GetMondrianImage():
    import cStringIO
    stream = cStringIO.StringIO(GetMondrianData())
    return wx.ImageFromStream(stream)

def GetMondrianIcon():
    icon = wx.EmptyIcon()
    icon.CopyFromBitmap(GetMondrianBitmap())
    return icon


#----------------------------------------------------------------------
# Auxiliary Timer Class For The Demo (For The ProgressPie)
#----------------------------------------------------------------------

class MyTimer(wx.Timer):


    def __init__(self, parent):

        wx.Timer.__init__(self)
        self._parent = parent
        

    def Notify(self):
        
        if self._parent._progresspie.GetValue() <= 0:
            self._parent._incr = 1

        if self._parent._progresspie.GetValue() >= self._parent._progresspie.GetMaxValue():
            self._parent._incr = -1

        self._parent._progresspie.SetValue(self._parent._progresspie.GetValue() + self._parent._incr)
        self._parent._progresspie.Refresh()


#----------------------------------------------------------------------
# Beginning Of PIECTRL Demo wxPython Code
#----------------------------------------------------------------------

class PieCtrlDemo(wx.Frame):

    def __init__(self, parent, id=wx.ID_ANY, title="", pos=wx.DefaultPosition,
                 size=(600, 450)):

        wx.Frame.__init__(self, parent, id, title, pos, size)

        # Create Some Maquillage For The Demo: Icon, StatusBar, MenuBar...
        
        self.SetIcon(GetMondrianIcon())
        self.statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)

        self.statusbar.SetStatusWidths([-2, -1])
        
        statusbar_fields = [("wxPython PieCtrl Demo, Andrea Gavana @ 30 Oct 2005"),
                            ("Welcome To wxPython!")]
        
        for i in range(len(statusbar_fields)):
            self.statusbar.SetStatusText(statusbar_fields[i], i)
        
        self.SetMenuBar(self.CreateMenuBar())

        panel = wx.Panel(self, -1)
        self._incr = 1
        self._hiddenlegend = False
        
        panel.SetBackgroundColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNFACE))

        # Create A Simple PieCtrl With 3 Sectors
        self._pie = PieCtrl(panel, -1, wx.DefaultPosition, wx.Size(180,270))
        
        self._pie.GetLegend().SetTransparent(True)
        self._pie.GetLegend().SetHorizontalBorder(10)
        self._pie.GetLegend().SetWindowStyle(wx.STATIC_BORDER)
        self._pie.GetLegend().SetLabelFont(wx.Font(10, wx.FONTFAMILY_DEFAULT,
                                                   wx.FONTSTYLE_NORMAL,
                                                   wx.FONTWEIGHT_NORMAL,
                                                   False, "Courier New"))
        self._pie.GetLegend().SetLabelColour(wx.Colour(0, 0, 127))	
        
        self._pie.SetBackground(wx.Bitmap("background.png", wx.BITMAP_TYPE_PNG))
        self._pie.SetHeight(30)

        part = PiePart()
        
        part.SetLabel("SeriesLabel_1")
        part.SetValue(300)
        part.SetColour(wx.Colour(200, 50, 50))
        self._pie._series.append(part)

        part = PiePart()        
        part.SetLabel("Series Label 2")
        part.SetValue(200)
        part.SetColour(wx.Colour(50, 200, 50))
        self._pie._series.append(part)

        part = PiePart()
        part.SetLabel("HelloWorld Label 3")
        part.SetValue(50)
        part.SetColour(wx.Colour(50, 50, 200))
        self._pie._series.append(part)

        # Create A ProgressPie
        self._progresspie = ProgressPie(panel, 100, 50, -1, wx.DefaultPosition,
                                        wx.Size(180, 200), wx.SIMPLE_BORDER)

        self._progresspie.SetBackColour(wx.Colour(150, 200, 255))
        self._progresspie.SetFilledColour(wx.Colour(255, 0, 0))
        self._progresspie.SetUnfilledColour(wx.WHITE)
        self._progresspie.SetHeight(20)
        
        self._slider = wx.Slider(panel, -1, 25, 0, 90, wx.DefaultPosition, wx.DefaultSize, wx.SL_VERTICAL | wx.SL_LABELS)
        self._angleslider = wx.Slider(panel, -1, 200, 0, 360, wx.DefaultPosition, wx.DefaultSize, wx.SL_LABELS | wx.SL_TOP)
        sizer = wx.BoxSizer(wx.VERTICAL)
        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        btnsizer = wx.BoxSizer(wx.HORIZONTAL)
        panel.SetSizer(sizer)
        
        hsizer.Add(self._progresspie, 1, wx.EXPAND | wx.ALL, 5)
        hsizer.Add(self._pie, 1, wx.EXPAND | wx.ALL, 5)
        hsizer.Add(self._slider, 0, wx.GROW | wx.ALL, 5)

        btn1 = wx.Button(panel, -1, "Toggle Legend Transparency")
        btn2 = wx.Button(panel, -1, "Toggle Edges")
        btn3 = wx.Button(panel, -1, "Hide Legend")
        btnsizer.Add(btn1, 0, wx.ALL, 5)
        btnsizer.Add(btn2, 0, wx.ALL, 5)
        btnsizer.Add(btn3, 0, wx.ALL, 5)

        sizer.Add(hsizer, 1, wx.EXPAND | wx.ALL, 5)
        sizer.Add(self._angleslider, 0, wx.GROW | wx.ALL, 5)
        sizer.Add(btnsizer, 0, wx.ALIGN_RIGHT | wx.BOTTOM | wx.LEFT | wx.RIGHT, 5)	

        sizer.Layout()        
        sizer.Fit(panel)
        self._timer = MyTimer(self)
        self._timer.Start(50)
        self.Centre()

        self._slider.Bind(wx.EVT_SLIDER, self.OnSlider)
        self._angleslider.Bind(wx.EVT_SLIDER, self.OnAngleSlider)
        btn1.Bind(wx.EVT_BUTTON, self.OnToggleTransparency)
        btn2.Bind(wx.EVT_BUTTON, self.OnToggleEdges)
        btn3.Bind(wx.EVT_BUTTON, self.OnToggleLegend)
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.OnAngleSlider(None)
        self.OnSlider(None)


    def OnClose(self, event):

        self._timer.Stop()
        del self._timer

        self.Destroy()
        

    def OnToggleTransparency(self, event):

        self._pie.GetLegend().SetTransparent(not self._pie.GetLegend().IsTransparent())
        self._pie.Refresh()


    def OnToggleEdges(self, event):

        self._pie.SetShowEdges(not self._pie.GetShowEdges())
        self._progresspie.SetShowEdges(not self._progresspie.GetShowEdges())


    def OnToggleLegend(self, event):

        self._hiddenlegend = not self._hiddenlegend
        
        if self._hiddenlegend:
            self._pie.GetLegend().Hide()
        else:
            self._pie.GetLegend().Show()

        self._pie.Refresh()
        
        
    def OnSlider(self, event):

        self._pie.SetAngle(float(self._slider.GetValue())/180.0*pi)
        self._progresspie.SetAngle(float(self._slider.GetValue())/180.0*pi)


    def OnAngleSlider(self, event):

        self._pie.SetRotationAngle(float(self._angleslider.GetValue())/180.0*pi)
        self._progresspie.SetRotationAngle(float(self._angleslider.GetValue())/180.0*pi)


    def CreateMenuBar(self):

        file_menu = wx.Menu()
        
        AS_EXIT = wx.NewId()        
        file_menu.Append(AS_EXIT, "&Exit")
        self.Bind(wx.EVT_MENU, self.OnClose, id=AS_EXIT)

        help_menu = wx.Menu()

        AS_ABOUT = wx.NewId()        
        help_menu.Append(AS_ABOUT, "&About...")
        self.Bind(wx.EVT_MENU, self.OnAbout, id=AS_ABOUT)

        menu_bar = wx.MenuBar()

        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(help_menu, "&Help")        

        return menu_bar
    

    def OnAbout(self, event):

        msg = "This Is The About Dialog Of The PieCtrl Demo.\n\n" + \
              "Author: Andrea Gavana @ 31 Oct 2005\n\n" + \
              "Please Report Any Bug/Requests Of Improvements\n" + \
              "To Me At The Following Adresses:\n\n" + \
              "andrea.gavana@agip.it\n" + "andrea_gavana@tin.it\n\n" + \
              "Welcome To wxPython " + wx.VERSION_STRING + "!!"
              
        dlg = wx.MessageDialog(self, msg, "PieCtrl Demo",
                               wx.OK | wx.ICON_INFORMATION)
        
        dlg.SetFont(wx.Font(8, wx.NORMAL, wx.NORMAL, wx.NORMAL, False, "Verdana"))
        dlg.ShowModal()
        dlg.Destroy()
        

def main():

    app = wx.PySimpleApp()
    frame = PieCtrlDemo(None, -1, "PieCtrl Demo ;-)")
    app.SetTopWindow(frame)
    frame.Show()
    app.MainLoop()

    
if __name__ == "__main__":
    main()

