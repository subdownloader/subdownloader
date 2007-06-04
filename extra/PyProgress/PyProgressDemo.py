import wx
import wx.lib.colourselect as csel

import PyProgress as PP

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

class PyProgressDemo(wx.Frame):

    def __init__(self, parent, id=wx.ID_ANY, title="PyProgress wxPython Demo ;-)",
                 pos=wx.DefaultPosition, size=(500, 400)):

        wx.Frame.__init__(self, parent, id, title, pos, size)
        self.panel = wx.Panel(self, -1)
        
        statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
        statusbar.SetStatusWidths([-2, -1])
        # statusbar fields
        statusbar_fields = [("PyProgress wxPython Demo, Andrea Gavana @ 03 Nov 2006"),
                            ("Welcome To wxPython!")]

        for i in range(len(statusbar_fields)):
            statusbar.SetStatusText(statusbar_fields[i], i)
            
        self.CreateMenu()
        self.LayoutItems()

        self.SetIcon(GetMondrianIcon())  
        self.CenterOnScreen()


    def LayoutItems(self):

        mainsizer = wx.BoxSizer(wx.HORIZONTAL)
        rightsizer = wx.FlexGridSizer(7, 2, 5, 5)

        startbutton = wx.Button(self.panel, -1, "Start PyProgress!")

        self.elapsedchoice = wx.CheckBox(self.panel, -1, "Show Elapsed Time")
        self.elapsedchoice.SetValue(1)
        
        self.cancelchoice = wx.CheckBox(self.panel, -1, "Enable Cancel Button")
        self.cancelchoice.SetValue(1)
        
        static1 = wx.StaticText(self.panel, -1, "Gauge Proportion (%): ")
        self.slider1 = wx.Slider(self.panel, -1, 20, 1, 99, style=wx.SL_HORIZONTAL|
                                 wx.SL_AUTOTICKS|wx.SL_LABELS)
        self.slider1.SetTickFreq(10, 1)
        self.slider1.SetValue(20)
        
        static2 = wx.StaticText(self.panel, -1, "Gauge Steps: ")
        self.slider2 = wx.Slider(self.panel, -1, 50, 2, 100, style=wx.SL_HORIZONTAL|
                                 wx.SL_AUTOTICKS|wx.SL_LABELS)
        self.slider2.SetTickFreq(10, 1)
        self.slider2.SetValue(50)

        static3 = wx.StaticText(self.panel, -1, "Gauge Background Colour: ")
        self.csel3 = csel.ColourSelect(self.panel, -1, "Choose...", wx.WHITE)
        
        static4 = wx.StaticText(self.panel, -1, "Gauge First Gradient Colour: ")
        self.csel4 = csel.ColourSelect(self.panel, -1, "Choose...", wx.WHITE)
        
        static5 = wx.StaticText(self.panel, -1, "Gauge Second Gradient Colour: ")
        self.csel5 = csel.ColourSelect(self.panel, -1, "Choose...", wx.BLUE)

        rightsizer.Add(self.elapsedchoice, 0, wx.EXPAND|wx.TOP, 10)
        rightsizer.Add((10, 0))
        rightsizer.Add(self.cancelchoice, 0, wx.EXPAND|wx.TOP, 3)
        rightsizer.Add((10, 0))
        rightsizer.Add(static1, 0, wx.ALIGN_CENTER_VERTICAL, 10)
        rightsizer.Add(self.slider1, 0, wx.EXPAND|wx.TOP, 10)
        rightsizer.Add(static2, 0, wx.ALIGN_CENTER_VERTICAL, 10)
        rightsizer.Add(self.slider2, 0, wx.EXPAND|wx.TOP|wx.BOTTOM, 10)
        rightsizer.Add(static3, 0, wx.ALIGN_CENTER_VERTICAL)
        rightsizer.Add(self.csel3, 0)
        rightsizer.Add(static4, 0, wx.ALIGN_CENTER_VERTICAL)
        rightsizer.Add(self.csel4, 0)
        rightsizer.Add(static5, 0, wx.ALIGN_CENTER_VERTICAL)
        rightsizer.Add(self.csel5, 0)
        
        mainsizer.Add(startbutton, 0, wx.ALL, 20)
        mainsizer.Add(rightsizer, 1, wx.EXPAND|wx.ALL, 10)

        self.panel.SetSizer(mainsizer)
        mainsizer.Layout()

        framesizer = wx.BoxSizer(wx.VERTICAL)
        framesizer.Add(self.panel, 1, wx.EXPAND)
        self.SetSizer(framesizer)
        framesizer.Layout()

        startbutton.Bind(wx.EVT_BUTTON, self.OnStartProgress)
        
        
    def CreateMenu(self):

        menuBar = wx.MenuBar(wx.MB_DOCKABLE)
        fileMenu = wx.Menu()
        helpMenu = wx.Menu()
        
        item = wx.MenuItem(fileMenu, wx.ID_ANY, "E&xit")
        self.Bind(wx.EVT_MENU, self.OnQuit, item)
        fileMenu.AppendItem(item)
                
        item = wx.MenuItem(helpMenu, wx.ID_ANY, "About")
        self.Bind(wx.EVT_MENU, self.OnAbout, item)
        helpMenu.AppendItem(item)

        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        self.SetMenuBar(menuBar)


    def OnStartProgress(self, event):

        event.Skip()
                
        style = wx.PD_APP_MODAL
        if self.elapsedchoice.GetValue():
            style |= wx.PD_ELAPSED_TIME
        if self.cancelchoice.GetValue():
            style |= wx.PD_CAN_ABORT

        dlg = PP.PyProgress(None, -1, "PyProgress Example",
                            "An Informative Message",                            
                            style=style)

        proportion = self.slider1.GetValue()
        steps = self.slider2.GetValue()
        
        backcol = self.csel3.GetColour()
        firstcol = self.csel4.GetColour()
        secondcol = self.csel5.GetColour()

        dlg.SetGaugeProportion(proportion/100.0)
        dlg.SetGaugeSteps(steps)
        dlg.SetGaugeBackground(backcol)
        dlg.SetFirstGradientColour(firstcol)
        dlg.SetSecondGradientColour(secondcol)
        
        max = 400
        keepGoing = True
        count = 0

        while keepGoing and count < max:
            count += 1
            wx.MilliSleep(50)

            if count >= max / 2:
                keepGoing = dlg.UpdatePulse("Half-time!")
            else:
                keepGoing = dlg.UpdatePulse()

        dlg.Destroy()
        wx.SafeYield()


    def OnQuit(self, event):

    	self.Destroy()


    def OnAbout(self, event):

        msg = "This Is The About Dialog Of The PyProgress Demo.\n\n" + \
              "Author: Andrea Gavana @ 03 Nov 2006\n\n" + \
              "Please Report Any Bug/Requests Of Improvements\n" + \
              "To Me At The Following Adresses:\n\n" + \
              "andrea.gavana@gmail.com\n" + "gavana@kpo.kz\n\n" + \
              "Welcome To wxPython " + wx.VERSION_STRING + "!!"
              
        dlg = wx.MessageDialog(self, msg, "PyProgress wxPython Demo",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


def main():

    app = wx.PySimpleApp()
    frame = PyProgressDemo(None, -1)
    frame.Show()
    app.MainLoop()

    
if __name__ == "__main__":
    main()

    