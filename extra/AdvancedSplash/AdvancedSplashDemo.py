import wx
import wx.lib.buttons

import AdvancedSplash as AS

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
# Beginning Of ADVANCEDSPLASH Demo wxPython Code
#----------------------------------------------------------------------

class AdvancedSplashDemo(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "AdvancedSplash Demo ;-)",
                         wx.DefaultPosition,
                         size=(600,500),
                         style=wx.DEFAULT_FRAME_STYLE |
                         wx.NO_FULL_REPAINT_ON_RESIZE)


        # Create Some Maquillage For The Demo: Icon, StatusBar, MenuBar...
        
        self.SetIcon(GetMondrianIcon())
        self.statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)

        self.statusbar.SetStatusWidths([-2, -1])
        
        statusbar_fields = [("wxPython AdvancedSplash Demo, Andrea Gavana @ 10 Oct 2005"),
                            ("Welcome To wxPython!")]
        
        for i in range(len(statusbar_fields)):
            self.statusbar.SetStatusText(statusbar_fields[i], i)
        
        self.SetMenuBar(self.CreateMenuBar())

        mainsizer = wx.BoxSizer(wx.VERTICAL)

        panel = wx.Panel(self, -1)
        sizer = wx.FlexGridSizer(2, 3, 25, 25)

        self.helpbuttons = []
        self.ibuttons = []
        
        self.isalive = 0

        # We Have 6 Different Examples In Here. Use The "?" ToggleButton To Learn How
        # The Examples Have Been Built, And Click On The "Original Image" Button To
        # See The Original Bitmap
        
        for ind in range(6):

            bsizer = wx.BoxSizer(wx.HORIZONTAL)
            vsizer = wx.BoxSizer(wx.VERTICAL)
            
            button = wx.Button(panel, -1, "Example " + str(ind+1))
            button.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD, False, "Verdana"))
            
            ibutton = wx.Button(panel, -1, "Original\nImage")
            ibutton.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "Tahoma"))
            self.ibuttons.append(ibutton)
            
            helpbtn = wx.lib.buttons.GenToggleButton(panel, -1, "?",
                                                     size=(20,20), style=wx.NO_BORDER)

            helpbtn.SetFont(wx.Font(14, wx.SWISS, wx.NORMAL, wx.BOLD))
            helpbtn.SetForegroundColour(wx.BLUE)
            helpbtn.SetUseFocusIndicator(False)
            helpbtn.Bind(wx.EVT_ENTER_WINDOW, self.EnterWindow)
            helpbtn.Bind(wx.EVT_LEAVE_WINDOW, self.ExitWindow)
            self.helpbuttons.append(helpbtn)

            eventbutton = eval("self.OnButton" + str(ind+1))
            button.Bind(wx.EVT_BUTTON, eventbutton)
            
            ibutton.Bind(wx.EVT_BUTTON, self.OnOriginalImage)
            
            bsizer.Add(button, 1, wx.EXPAND | wx.RIGHT, 5)
            vsizer.Add(ibutton, 1, wx.EXPAND | wx.BOTTOM, 3)
            vsizer.Add(helpbtn, 0, wx.ALIGN_CENTER_HORIZONTAL)
            bsizer.Add(vsizer, 0, wx.EXPAND)
            sizer.Add(bsizer, 0)

        mainsizer.Add((1, 1), 1, wx.EXPAND)
        mainsizer.Add(sizer, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 25)
        mainsizer.Add((1, 1), 1, wx.EXPAND)

        panel.SetSizer(mainsizer)
        mainsizer.Layout()

        # Every Time A Button Is Clicked, The Main Application Frame Is Minimized To
        # Better Show The SplashScreen. The Main Frame Is Then Restored When The
        # AdvancedSplash Closes.


    def OnButton1(self, event):

        self.Iconize()
        wx.MilliSleep(50)
        
        bitm = wx.Bitmap("bg.png", wx.BITMAP_TYPE_PNG)
        frame = AS.AdvancedSplash(self, bitmap=bitm, extrastyle=AS.AS_NOTIMEOUT |
                                  AS.AS_CENTER_ON_SCREEN)

        frame.Bind(wx.EVT_CLOSE, self.OnCloseSplash)
        

    def OnButton2(self, event):

        self.Iconize()
        wx.MilliSleep(50)
        
        bitmap = wx.Bitmap("equation.bmp", wx.BITMAP_TYPE_BMP)
        shadow = wx.WHITE
        
        frame = AS.AdvancedSplash(self, bitmap=bitmap,
                                  extrastyle=AS.AS_NOTIMEOUT |
                                  AS.AS_CENTER_ON_SCREEN |
                                  AS.AS_SHADOW_BITMAP,
                                  shadowcolour=shadow)

        frame.Bind(wx.EVT_CLOSE, self.OnCloseSplash)
        

    def OnButton3(self, event):

        self.Iconize()
        wx.MilliSleep(50)
        
        bitmap = wx.Bitmap("Andrea.bmp", wx.BITMAP_TYPE_BMP)
        shadow = wx.WHITE
        
        frame = AS.AdvancedSplash(self, bitmap=bitmap, timeout=5000,
                                  extrastyle=AS.AS_TIMEOUT |
                                  AS.AS_CENTER_ON_PARENT |
                                  AS.AS_SHADOW_BITMAP,
                                  shadowcolour=shadow)

        frame.Bind(wx.EVT_CLOSE, self.OnCloseSplash)

        
    def OnButton4(self, event):

        self.Iconize()
        wx.MilliSleep(50)
        
        bitmap = wx.Bitmap("equation.bmp", wx.BITMAP_TYPE_BMP)
        shadow = wx.WHITE
        
        frame = AS.AdvancedSplash(self, bitmap=bitmap, timeout=5000,
                                  extrastyle=AS.AS_TIMEOUT |
                                  AS.AS_CENTER_ON_SCREEN |
                                  AS.AS_SHADOW_BITMAP,
                                  shadowcolour=shadow)

        frame.Bind(wx.EVT_CLOSE, self.OnCloseSplash)        


    def OnButton5(self, event):

        self.Iconize()
        wx.MilliSleep(50)
        
        bitmap = wx.Bitmap("splash.bmp", wx.BITMAP_TYPE_BMP)
        shadow = wx.Colour(255, 0, 255)
        
        frame = AS.AdvancedSplash(self, bitmap=bitmap,
                                  extrastyle=AS.AS_NOTIMEOUT |
                                  AS.AS_CENTER_ON_SCREEN |
                                  AS.AS_SHADOW_BITMAP,
                                  shadowcolour=shadow)

        frame.Bind(wx.EVT_CLOSE, self.OnCloseSplash)
        
        frame.SetText("You Can Place Some Text...")
        frame.SetTextColour(wx.WHITE)
        frame.SetTextPosition((125,75))
        wx.MilliSleep(2000)
        
        frame.SetText("Do Something Else...")
        frame.SetTextColour(wx.WHITE)
        wx.MilliSleep(2000)

        oldfont, fontsize = frame.GetTextFont()

        frame.SetText("Change The Text Appearance...")
        frame.SetTextColour(wx.RED)
        frame.SetTextFont(wx.Font(8, wx.DECORATIVE, wx.NORMAL, wx.BOLD, False))
        wx.MilliSleep(2000)

        frame.SetText("Just Call 'Close' When Finished")
        wx.MilliSleep(2000)                
        
        frame.SetText("Bye Bye")
        frame.SetTextFont(oldfont)
        frame.SetTextColour(wx.WHITE)
        wx.MilliSleep(2000)

        frame.Close()        
        
        event.Skip()


    def OnButton6(self, event):

        self.Iconize()
        wx.MilliSleep(50)
        
        bitmap = wx.Bitmap("wxsplash.png", wx.BITMAP_TYPE_PNG)
        
        frame = AS.AdvancedSplash(self, bitmap=bitmap,
                                  extrastyle=AS.AS_NOTIMEOUT |
                                  AS.AS_CENTER_ON_SCREEN)
        
        frame.Bind(wx.EVT_CLOSE, self.OnCloseSplash)
        
        frame.SetText("Loading Data...")
        frame.SetTextColour(wx.RED)
        frame.SetTextPosition((350,200))
        wx.MilliSleep(2000)
        
        frame.SetText("Do Something Else...")
        frame.SetTextColour(wx.BLUE)
        wx.MilliSleep(2000)

        oldfont, fontsize = frame.GetTextFont()

        frame.SetText("Change The Text Appearance")
        frame.SetTextColour(wx.RED)
        frame.SetTextFont(wx.Font(9, wx.TELETYPE, wx.NORMAL, wx.BOLD, False))
        wx.MilliSleep(2000)

        frame.SetText("I Hope You Like It")
        wx.MilliSleep(2000)                
        
        frame.SetText("Bye Bye")
        frame.SetTextFont(oldfont)
        frame.SetTextColour(wx.BLUE)
        wx.MilliSleep(2000)

        frame.Close()
        
        event.Skip()        
    

    def OnOriginalImage(self, event):

        indx = self.ibuttons.index(event.GetEventObject())

        if indx == 0:
            
            filename = "bg.png"
            img = wx.Image(filename, wx.BITMAP_TYPE_PNG)

            red = img.GetMaskRed()
            green = img.GetMaskGreen()
            blue = img.GetMaskBlue()
            
            img.SetMask(False)
            bmp = img.ConvertToBitmap()
            
        elif indx == 1:
                        
            filename = "equation.bmp"
            bmp = wx.Bitmap(filename, wx.BITMAP_TYPE_BMP)
            red = 255
            green = 255
            blue = 255

        elif indx == 2:
                        
            filename = "Andrea.bmp"
            bmp = wx.Bitmap(filename, wx.BITMAP_TYPE_BMP)
            red = 255
            green = 255
            blue = 255

        elif indx == 3:
                        
            filename = "equation.bmp"
            bmp = wx.Bitmap(filename, wx.BITMAP_TYPE_BMP)
            red = 255
            green = 255
            blue = 255

        elif indx == 4:
                        
            filename = "splash.bmp"
            bmp = wx.Bitmap(filename, wx.BITMAP_TYPE_BMP)
            red = 255
            green = 0
            blue = 255

        elif indx == 5:
                        
            filename = "wxsplash.png"
            bmp = wx.Bitmap(filename, wx.BITMAP_TYPE_PNG)
            
            
        frame = wx.Frame(self, -1, "Original Image " + str(indx+1))
        frame.SetIcon(GetMondrianIcon())
        
        panel = wx.Panel(frame, -1)

        maxlen = 0
        
        msizer = wx.BoxSizer(wx.VERTICAL)

        sbmp = wx.StaticBitmap(panel, -1, bmp)

        msizer.Add((0,5), 1, wx.EXPAND)

        hsizer = wx.BoxSizer(wx.HORIZONTAL)
        hsizer.Add(sbmp, 1)

        fsizer = wx.FlexGridSizer(4, 2, 5, 10)
        sts1 = wx.StaticText(panel, -1, "Image File Name:")
        sts2 = wx.StaticText(panel, -1, filename)

        sts1.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.NORMAL))
        sts2.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))
        fsizer.Add(sts1, 0)
        fsizer.Add(sts2, 0)

        mylen = sts1.GetSize()[0] + sts2.GetSize()[0]
        maxlen = max(maxlen, mylen)

        sts1 = wx.StaticText(panel, -1, "Image Size:")
        sts2 = wx.StaticText(panel, -1, "(" + str(bmp.GetWidth()) + " , " + \
                             str(bmp.GetHeight()) + ")")

        sts1.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.NORMAL))
        sts2.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))
        fsizer.Add(sts1, 0)
        fsizer.Add(sts2, 0)

        mylen = sts1.GetSize()[0] + sts2.GetSize()[0]
        maxlen = max(maxlen, mylen)

        sts1 = wx.StaticText(panel, -1, "Mask Colour:")

        if indx != 5:
            
            newmask = wx.EmptyBitmap(30, 20)
            
            mem = wx.MemoryDC() 
            mem.SelectObject(newmask)          
            mem.SetBackground(wx.Brush(wx.Colour(red, green, blue)))  
            mem.Clear() 
            
            sts2 = wx.StaticBitmap(panel, -1, newmask)

        else:

            sts2 = wx.StaticText(panel, -1, "None")
            sts2.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.BOLD))
            
        sts1.SetFont(wx.Font(9, wx.SWISS, wx.NORMAL, wx.NORMAL))
        fsizer.Add(sts1, 0)
        fsizer.Add(sts2, 0)

        mylen = sts1.GetSize()[0] + sts2.GetSize()[0]
        maxlen = max(maxlen, mylen)        

        hsizer.Add(fsizer, 0, wx.EXPAND | wx.LEFT, 10)
        msizer.Add(hsizer)
        
        msizer.Add((0,5), 1, wx.EXPAND) 
        
        panel.SetSizer(msizer)
        msizer.Layout()

        frame.SetMinSize((bmp.GetWidth(), bmp.GetHeight() + 20))
        frame.SetSize((bmp.GetWidth() + maxlen + 20, bmp.GetHeight() + 50))
        frame.Show()

        
    def OnOriginalImage2(self, event):

        event.Skip()


    def OnOriginalImage3(self, event):

        event.Skip()
        

    def OnOriginalImage4(self, event):

        event.Skip()


    def OnOriginalImage5(self, event):

        event.Skip()


    def OnOriginalImage6(self, event):

        event.Skip()        

    def OnCloseSplash(self, event):

        event.Skip()
        
        wx.MilliSleep(50)
        
        self.Raise()
        self.Iconize(False)


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


    def OnClose(self, event):
        
        self.Destroy()


    def OnAbout(self, event):

        msg = "This Is The About Dialog Of The AdvancedSplash Demo.\n\n" + \
              "Author: Andrea Gavana @ 10 Oct 2005\n\n" + \
              "Please Report Any Bug/Requests Of Improvements\n" + \
              "To Me At The Following Adresses:\n\n" + \
              "andrea.gavana@agip.it\n" + "andrea_gavana@tin.it\n\n" + \
              "Welcome To wxPython " + wx.VERSION_STRING + "!!"
              
        dlg = wx.MessageDialog(self, msg, "AdvancedSplash Demo",
                               wx.OK | wx.ICON_INFORMATION)
        
        dlg.SetFont(wx.Font(8, wx.NORMAL, wx.NORMAL, wx.NORMAL, False, "Verdana"))
        dlg.ShowModal()
        dlg.Destroy()
        

    def EnterWindow(self, event):

        if self.isalive == 1:
            return

        btn = event.GetEventObject()
        btn.SetForegroundColour(wx.RED)
        
        btn.SetToggle(True)
        self.isalive = 1
        self.selectedbutton = btn

        indx = self.helpbuttons.index(btn)

        win = MyTransientPopup(self, wx.SIMPLE_BORDER, helpid=indx)
        pos = btn.ClientToScreen((0,0))
        sz =  btn.GetSize()
        self.popup = win

        win.Position(pos, (0, sz[1]))
        win.Show()
        

    def ExitWindow(self, event):

        if hasattr(self, "popup"):
            self.popup.Destroy()
            del self.popup
            self.selectedbutton.SetToggle(False)

        self.isalive = 0
        self.selectedbutton.SetForegroundColour(wx.BLUE)

        
# Auxiliary Help Class. Just To Display Some Help Functionalities
# About AdvancedSplash Control Using TransientPopups When The User
# Enter With The Mouse The Help Button

class MyTransientPopup(wx.PopupWindow):
    
    def __init__(self, parent, style, helpid=None):
        
        wx.PopupWindow.__init__(self, parent, style)
        panel = wx.Panel(self, -1)
        panel.SetBackgroundColour(wx.Colour(255,255,190))

        self.parent = parent
        
        icon = wx.Icon("OK.ico", wx.BITMAP_TYPE_ICO, 16, 16)
        bmp = wx.EmptyBitmap(16,16)
        bmp.CopyFromIcon(icon)
        
        ontext, thehelp, moretext = self.GetStatic(helpid)

        sx = 0
        sy = 0
        
        txt = wx.StaticText(panel, -1, thehelp, pos=(5,5))
        txt.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD, False, "tahoma"))

        sz = txt.GetBestSize()
        sx = sx + sz[0]
        sy = sy + sz[1] + 5

        maxlen = 0

        for strs in ontext:
            txt = wx.StaticText(panel, -1, strs, pos=(30,20+sy))
            txt.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "tahoma"))
            sz = txt.GetBestSize()
            stbmp = wx.StaticBitmap(panel, -1, bmp, pos=(10, 5+sy+sz[1]))
            sy = sy + sz[1] + 5
            maxlen = max(maxlen, sz[0])

        txt = wx.StaticText(panel, -1, moretext, pos=(10,30+sy))
        txt.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, False, "tahoma"))
        sz = txt.GetBestSize()
        sy = sy + sz[1] + 20

        maxlen = max(maxlen, sz[0])
        panel.SetSize((maxlen+20, 25+sy))
        self.SetSize(panel.GetSize())
            

    def GetStatic(self, helpid):

        ontext = []
        
        if helpid == 0:
            ontext.append("AS_CENTER_ON_SCREEN")
            ontext.append("AS_NO_TIMEOUT")
            thehelp = "Example 1"
            moretext = "This Example Uses A PNG Image\nThat Already Has An Alpha\n" \
                       "Transparency, So There Is No\nNeed To Mask The Bitmap.\n" \
                       "There Is No Timeout, So Click\nOn The SplashScreen To Close."
        elif helpid == 1:
            ontext.append("AS_CENTER_ON_SCREEN")
            ontext.append("AS_NO_TIMEOUT")
            ontext.append("AS_SHADOW_BITMAP")
            thehelp = "Example 2"
            moretext = "This Example Uses A BMP Image\nThat Has No Transparency\n" \
                       "So We Need To Mask The Bitmap\nWith AS_SHADOW_BITMAP Style.\n" \
                       "There Is No Timeout, So Click\nOn The SplashScreen To Close."
        elif helpid == 2:
            ontext.append("AS_CENTER_ON_PARENT")
            ontext.append("AS_TIMEOUT")
            ontext.append("AS_SHADOW_BITMAP")
            thehelp = "Example 3"
            moretext = "This Example Uses A BMP Image\nThat Has No Transparency\n" \
                       "So We Need To Mask The Bitmap\nWith AS_SHADOW_BITMAP Style.\n" \
                       "There Is A 5 Seconds Timeout!"
        elif helpid == 3:
            ontext.append("AS_CENTER_ON_SCREEN")
            ontext.append("AS_TIMEOUT")
            ontext.append("AS_SHADOW_BITMAP")
            thehelp = "Example 4"
            moretext = "This Example Uses A BMP Image\nThat Has No Transparency\n" \
                       "So We Need To Mask The Bitmap\nWith AS_SHADOW_BITMAP Style.\n" \
                       "There Is A 5 Seconds Timeout!"
        elif helpid == 4:
            ontext.append("AS_CENTER_ON_SCREEN")
            ontext.append("AS_NOTIMEOUT")
            ontext.append("AS_SHADOW_BITMAP")
            thehelp = "Example 5"
            moretext = "This Example Uses A BMP Image\nThat Has No Transparency\n" \
                       "So We Need To Mask The Bitmap\nWith AS_SHADOW_BITMAP Style.\n" \
                       "There Is No Timeout, And We Can\nSet Some Text On The SplashScreen."
        elif helpid == 5:
            ontext.append("AS_CENTER_ON_SCREEN")
            ontext.append("AS_NOTIMEOUT")
            thehelp = "Example 6"
            moretext = "In This Example We Don't Shadow\nAnything, We Use The PNG As It\n" \
                       "Is. This Is The Standard wxPython\nDemo SplashScreen Image.\n" \
                       "There Is No Timeout, And We Can\nSet Some Text On The SplashScreen."

        
        return ontext, thehelp, moretext


    def ProcessLeftDown(self, evt):
        return False

    def OnDismiss(self):
        return False


        
def main():
    
    app = wx.PySimpleApp()

    frame = AdvancedSplashDemo()
    frame.Show()
    
    app.MainLoop()


if __name__ == "__main__":
    main()

    