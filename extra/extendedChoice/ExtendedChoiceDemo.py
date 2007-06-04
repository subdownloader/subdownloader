# ----------------------------------------------------------------------------
# ExtendedChoice Demo Implementation
#
# This Demo Shows How To Use The ExtendedChoice Control, With Different Styles
# And Actions.
# ----------------------------------------------------------------------------


import wx
import ExtendedChoice as EChoice

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


ArtIDs = [ "wx.ART_ADD_BOOKMARK",
           "wx.ART_DEL_BOOKMARK",
           "wx.ART_HELP_SIDE_PANEL",
           "wx.ART_HELP_SETTINGS",
           "wx.ART_HELP_BOOK",
           "wx.ART_HELP_FOLDER",
           "wx.ART_HELP_PAGE",
           "wx.ART_GO_BACK",
           "wx.ART_GO_FORWARD",
           "wx.ART_GO_UP",
           "wx.ART_GO_DOWN",
           "wx.ART_GO_TO_PARENT",
           "wx.ART_GO_HOME",
           "wx.ART_FILE_OPEN",
           "wx.ART_PRINT",
           "wx.ART_HELP",
           "wx.ART_TIP",
           "wx.ART_REPORT_VIEW",
           "wx.ART_LIST_VIEW",
           "wx.ART_NEW_DIR",
           "wx.ART_HARDDISK",
           "wx.ART_FLOPPY",
           "wx.ART_CDROM",
           "wx.ART_REMOVABLE",
           "wx.ART_FOLDER",
           "wx.ART_FOLDER_OPEN",
           "wx.ART_GO_DIR_UP",
           "wx.ART_EXECUTABLE_FILE",
           "wx.ART_NORMAL_FILE",
           "wx.ART_TICK_MARK",
           "wx.ART_CROSS_MARK",
           "wx.ART_ERROR",
           "wx.ART_QUESTION",
           "wx.ART_WARNING",
           "wx.ART_INFORMATION",
           "wx.ART_MISSING_IMAGE",
           ]

# ----------------------------------------------------------------------------
# Class To Handle The Message In The LogMessageWindow
# ----------------------------------------------------------------------------

class MyLog(wx.PyLog):

    def __init__(self, textCtrl, logTime=0):

        wx.PyLog.__init__(self)
        self.tc = textCtrl
        self.logTime = logTime

    def DoLogString(self, message, timeStamp):

        if self.tc:
            self.tc.AppendText(message + '\n')

# ----------------------------------------------------------------------------
# Beginning Of ExtendedChoice Demo
# ----------------------------------------------------------------------------

            
class ExtendedChoiceFrame(wx.Frame):

    def __init__(self, parent, id = wx.ID_ANY, title = "", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE):

        wx.Frame.__init__(self, parent, -1, title=title, size=size,
                          pos=pos, style=style)

        self.statusbar = self.CreateStatusBar(2, wx.ST_SIZEGRIP)
        self.statusbar.SetStatusWidths([-2, -1])
        # statusbar fields
        statusbar_fields = [("Welcome To WxPython " + wx.VERSION_STRING),
                            ("ExtendedChoice Demo")]
        
        for i in range(len(statusbar_fields)):
            self.statusbar.SetStatusText(statusbar_fields[i], i)

        self.SetIcon(GetMondrianIcon())
        self.SetMenuBar(self.CreateMenuBar())
        
        splitter = wx.SplitterWindow(self, -1, style=wx.CLIP_CHILDREN |
                                     wx.SP_LIVE_UPDATE | wx.SP_3D)

        panel = wx.Panel(splitter, -1)
        mainsizer = wx.GridSizer(cols=3, rows=4, vgap=2, hgap=2)
        
        Images = wx.ImageList(16,16)
        mychoices = []

        # Add The Images And The Choices
        for items in ArtIDs:
            bmp = wx.ArtProvider_GetBitmap(eval(items), wx.ART_TOOLBAR, (16,16))
            Images.Add(bmp)
            mychoices.append(items[7:])

        # Note: ExtendedChoice Accept A *TUPLE* As Input For Choices+ImageIds.
        # However, If You Pass Only A List Of Choices (And Not A Tuple), It
        # Will Create A Tuple Of ImageIds With ImageIDs = range(0, len(choices))

        # This Is A Simple One: No Particular Styles Or Features
        sizer1 = wx.BoxSizer(wx.VERTICAL)
        self.choiceicon1 = EChoice.ExtendedChoice(panel, -1, choices=mychoices,
                                                  icons=Images,
                                                  extrastyle=EChoice.EC_CHOICE,
                                                  name="SimpleExtendedChoice")

        text1 = wx.StaticText(panel, -1, "Basic Control (CHOICE Style)")
        sizer1.Add(text1, 0, wx.EXPAND | wx.BOTTOM, 4)
        sizer1.Add(self.choiceicon1, 0)

        # Here You Can Push A Button To Sort Items Ascending Or Descending
        sizer2 = wx.BoxSizer(wx.VERTICAL)
        self.choiceicon2 = EChoice.ExtendedChoice(panel, -1, choices=mychoices,
                                                  icons=Images,
                                                  extrastyle=EChoice.EC_COMBO,
                                                  name="SortingOptions")

        text2 = wx.StaticText(panel, -1, "Sorting Options (COMBO Style)")
        
        button = wx.Button(panel, -1, "Sort Ascending")
        button.Bind(wx.EVT_BUTTON, self.OnSortButton)
        
        hsizer2 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer2.Add(self.choiceicon2, 0, wx.EXPAND)
        hsizer2.Add(button, 0, wx.LEFT, 5)

        sizer2.Add(text2, 0, wx.EXPAND | wx.BOTTOM, 4)
        sizer2.Add(hsizer2, 0)

        # Here You Have The Same Icon For All The Items And An Item Composed By 2 Rows
        # Why The Top StaticText Does Not Resize Correctly In The Vertical Direction
        # If I Have More Than 1 Row For An Item?????
        sizer3 = wx.BoxSizer(wx.VERTICAL)
        choices3 = mychoices[0:8]
        choices3.append("Hello Mama!\nLook At Me!")
        self.choiceicon3 = EChoice.ExtendedChoice(panel, -1, choices=(choices3, [4]*10), 
                                                  icons=Images,
                                                  extrastyle=EChoice.EC_CHOICE,
                                                  name="SameIcon")

        text3 = wx.StaticText(panel, -1, "Same Icon (CHOICE Style)")

        sizer3.Add(text3, 0, wx.EXPAND | wx.BOTTOM, 4)
        sizer3.Add(self.choiceicon3, 0)

        # This Control Has A Different Font For All The Items
        sizer4 = wx.BoxSizer(wx.VERTICAL)
        self.choiceicon4 = EChoice.ExtendedChoice(panel, -1, choices=mychoices,
                                                  icons=Images,
                                                  extrastyle=EChoice.EC_COMBO,
                                                  name="FontAndColour1")

        text4 = wx.StaticText(panel, -1, "Font And Colour 1 (COMBO Style)")

        ecstyle = self.choiceicon4.GetChoiceStyle()
        ecstyle.SetControlColour(wx.RED)
        
        ecstyle.SetAllItemsFont(wx.Font(9, wx.SWISS, wx.NORMAL,
                                                     wx.BOLD, False, "Verdana"))

        sizer4.Add(text4, 0, wx.EXPAND | wx.BOTTOM, 4)
        sizer4.Add(self.choiceicon4, 0)

        # This One Has:
        # a) All The Items With Red ForegroundColour
        # b) The Selection Colour Is Yellow
        # c) The Text Selection Colour Is Blue
        # d) The Background Colour Of The Popup Window Is Your System Background Colour
        # e) All The Items Font Are Changed To Handwriting
        
        sizer5 = wx.BoxSizer(wx.VERTICAL)
        self.choiceicon5 = EChoice.ExtendedChoice(panel, -1,
                                                  choices=(mychoices[10:18], range(10,19)),
                                                  icons=Images,
                                                  extrastyle=EChoice.EC_CHOICE,
                                                  name="FontAndColour2")

        text5 = wx.StaticText(panel, -1, "Font And Colour 2 (CHOICE Style)")

        ecstyle = self.choiceicon5.GetChoiceStyle()
        
        ecstyle.SetAllItemsForegroundColour(wx.RED)
        ecstyle.SetSelectionColour(wx.NamedColour("YELLOW"))
        ecstyle.SetTextSelectionColour(wx.BLUE)
        ecstyle.SetAllItemsBackgroundColour(wx.SystemSettings_GetColour(0))
        ecstyle.SetBackControlColour(wx.SystemSettings_GetColour(0))
        ecstyle.SetAllItemsFont(wx.Font(13, wx.SCRIPT, wx.NORMAL, wx.NORMAL, False))

        sizer5.Add(text5, 0, wx.EXPAND | wx.BOTTOM, 4)
        sizer5.Add(self.choiceicon5, 0)

        # That's Becoming Harder... This Control Has:
        # a) Alternating Text Colour (Red, Green, Black)
        # b) Alternating Font For The Items
        
        sizer6 = wx.BoxSizer(wx.VERTICAL)
        self.choiceicon6 = EChoice.ExtendedChoice(panel, -1, choices=mychoices,
                                                  icons=Images,
                                                  extrastyle=EChoice.EC_COMBO,
                                                  name="FontAndColour3")

        text6 = wx.StaticText(panel, -1, "Font And Colour 3 (COMBO Style)")

        ecstyle = self.choiceicon6.GetChoiceStyle()

        for ii in xrange(len(mychoices)):
            if ii%3 == 0:
                ecstyle.SetItemForegroundColour(ii, wx.RED)
                font = wx.Font(9, wx.ROMAN, wx.NORMAL, wx.BOLD, False)
                ecstyle.SetItemFont(ii, font)
            elif ii%3 == 1:
                ecstyle.SetItemForegroundColour(ii, wx.GREEN)
                font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, True)
                ecstyle.SetItemFont(ii, font)
            else:
                ecstyle.SetItemForegroundColour(ii, wx.BLACK)
                font = wx.Font(13, wx.SCRIPT, wx.NORMAL, wx.NORMAL, False)
                ecstyle.SetItemFont(ii, font)

        sizer6.Add(text6, 0, wx.EXPAND | wx.BOTTOM, 4)
        sizer6.Add(self.choiceicon6, 0)

        # Even More Interesting:
        # a) Alternating Background Colours For The Items
        # b) Alternating Fonts
        sizer7 = wx.BoxSizer(wx.VERTICAL)
        self.choiceicon7 = EChoice.ExtendedChoice(panel, -1, choices=mychoices,
                                                  icons=Images,
                                                  extrastyle=EChoice.EC_CHOICE,
                                                  name="FontAndColour4")

        text7 = wx.StaticText(panel, -1, "Font And Colour 4 (CHOICE Style)")

        ecstyle = self.choiceicon7.GetChoiceStyle()

        for ii in xrange(len(mychoices)):
            if ii%3 == 0:
                ecstyle.SetItemBackgroundColour(ii, wx.RED)
                font = wx.Font(9, wx.ROMAN, wx.NORMAL, wx.NORMAL, False)
                ecstyle.SetItemFont(ii, font)
            elif ii%3 == 1:
                ecstyle.SetItemBackgroundColour(ii, wx.GREEN)
                font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.NORMAL, True)
                ecstyle.SetItemFont(ii, font)
            else:
                ecstyle.SetItemBackgroundColour(ii, wx.Colour(212, 208, 200))
                font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD, False, "Verdana")
                ecstyle.SetItemFont(ii, font)

        sizer7.Add(text7, 0, wx.EXPAND | wx.BOTTOM, 4)
        sizer7.Add(self.choiceicon7, 0)

        # That Is The Best One... Even If It Is A Mess:
        # a) Alternating Text Background Colours
        # b) Alternating Text Background Motifs (Styles)
        # c) First And Last Items Have Different Font And Text Colour
        
        sizer8 = wx.BoxSizer(wx.VERTICAL)
        self.choiceicon8 = EChoice.ExtendedChoice(panel, -1, choices=mychoices,
                                                  icons=Images,
                                                  extrastyle=EChoice.EC_COMBO,
                                                  name="FontAndColour5")

        text8 = wx.StaticText(panel, -1, "Font And Colour 5 (COMBO Style)")

        ecstyle = self.choiceicon8.GetChoiceStyle()

        for ii in xrange(len(mychoices)):
            if ii == 0:
                font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD, True, "Verdana")
                ecstyle.SetItemFont(ii, font)
                ecstyle.SetItemForegroundColour(ii, wx.NamedColor("GOLD"))
            if ii == len(mychoices) - 1:
                font = wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD, True, "Times New Roman")
                ecstyle.SetItemFont(ii, font)
                ecstyle.SetItemForegroundColour(ii, wx.RED)
            if ii%3 == 0:
                ecstyle.SetItemBackgroundColour(ii, wx.NamedColor("CYAN"))
                ecstyle.SetItemBackgroundMotif(ii, wx.CROSSDIAG_HATCH)
            elif ii%3 == 1:
                ecstyle.SetItemBackgroundColour(ii, wx.NamedColor("LIGHT GREY"))
                ecstyle.SetItemBackgroundMotif(ii, wx.SOLID)
            else:
                ecstyle.SetItemBackgroundColour(ii, wx.NamedColor("GOLD"))
                ecstyle.SetItemBackgroundMotif(ii, wx.VERTICAL_HATCH)

        sizer8.Add(text8, 0, wx.EXPAND | wx.BOTTOM, 4)
        sizer8.Add(self.choiceicon8, 0)

        # This Control Uses The EC_RULES Style. You Have These Changes:
        # a) The Global Control Colour;
        # b) The Selection Colour;
        # c) The Items Background Colour;
        # d) The Border Between Items Are Painted Dotted
        sizer9 = wx.BoxSizer(wx.VERTICAL)
        self.choiceicon9 = EChoice.ExtendedChoice(panel, -1, choices=mychoices,
                                                  icons=Images, style=EChoice.EC_RULES,
                                                  extrastyle=EChoice.EC_CHOICE,
                                                  name="Borders1")

        text9 = wx.StaticText(panel, -1, "Borders 1 (CHOICE Style)")

        ecstyle = self.choiceicon9.GetChoiceStyle()
        ecstyle.SetControlColour(wx.NamedColor("GOLD"))
        ecstyle.SetSelectionColour(wx.GREEN)
        ecstyle.SetBorder(wx.Pen(wx.BLACK, 0.4, wx.DOT))
        ecstyle.SetAllItemsBackgroundColour(wx.NamedColor("GOLD"))
        
        sizer9.Add(text9, 0, wx.EXPAND | wx.BOTTOM, 4)
        sizer9.Add(self.choiceicon9, 0)

        # Another Control That Uses The EC_RULES Style. You Have These Changes:
        # a) The Items Background Motif;
        # b) The Items Background Colour;
        # c) The Items Foreground Colour;
        # d) The Border Between Items Are Painted Dotted-Dashed
        sizer10 = wx.BoxSizer(wx.VERTICAL)
        self.choiceicon10 = EChoice.ExtendedChoice(panel, -1, choices=mychoices,
                                                  icons=Images, style=EChoice.EC_RULES,
                                                  extrastyle=EChoice.EC_COMBO,
                                                  itemsperpage=5, name="Borders2")

        text10 = wx.StaticText(panel, -1, "Borders 2 (COMBO Style)")

        ecstyle = self.choiceicon10.GetChoiceStyle()
        ecstyle.SetAllItemsBackgroundColour(wx.NamedColor("MEDIUM GREY"))
        ecstyle.SetAllItemsForegroundColour(wx.RED)
        ecstyle.SetAllItemsBackgroundMotif(wx.FDIAGONAL_HATCH)
        ecstyle.SetBorder(wx.Pen(wx.GREEN, 0.5, wx.DOT_DASH))
        
        sizer10.Add(text10, 0, wx.EXPAND | wx.BOTTOM, 4)
        sizer10.Add(self.choiceicon10, 0)

        # This Controls Shows How To Add Items/Choices In Runtime
        sizer11 = wx.BoxSizer(wx.VERTICAL)
        self.choiceicon11 = EChoice.ExtendedChoice(panel, -1, choices=mychoices,
                                                   icons=Images, itemsperpage=5,
                                                   extrastyle=EChoice.EC_CHOICE,
                                                   name="NewItems")

        text11 = wx.StaticText(panel, -1, "Inserting New Items... (CHOICE Style)")
        
        button = wx.Button(panel, -1, "Add Item")
        button.Bind(wx.EVT_BUTTON, self.OnInsertChoice)
        self.textctrl = wx.TextCtrl(panel, -1, "Add Me!", size=(70,-1))
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(self.textctrl, 0, wx.RIGHT, 5)
        vsizer.Add(button, 0, wx.TOP, 5)
        
        hsizer11 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer11.Add(self.choiceicon11, 0)
        hsizer11.Add(vsizer, 0, wx.LEFT | wx.RIGHT, 5)

        sizer11.Add(text11, 0, wx.EXPAND | wx.BOTTOM, 4)
        sizer11.Add(hsizer11, 1, wx.EXPAND)

        # This Controls Shows How To Remove Items/Choices In Runtime
        sizer12 = wx.BoxSizer(wx.VERTICAL)
        self.choiceicon12 = EChoice.ExtendedChoice(panel, -1, choices=mychoices,
                                                   icons=Images,
                                                   extrastyle=EChoice.EC_COMBO,
                                                   name="RemoveChoices")

        text12 = wx.StaticText(panel, -1, "Removing Choices... (COMBO Style)")
        button = wx.Button(panel, -1, "Remove Choice")
        button.Bind(wx.EVT_BUTTON, self.OnRemoveChoice)

        hsizer12 = wx.BoxSizer(wx.HORIZONTAL)
        hsizer12.Add(self.choiceicon12, 0)
        hsizer12.Add(button, 0, wx.LEFT | wx.RIGHT, 5)        

        sizer12.Add(text12, 0, wx.EXPAND)
        sizer12.Add(hsizer12, 0)
        
        mainsizer.Add(sizer1, 0, wx.LEFT | wx.TOP, 10)
        mainsizer.Add(sizer2, 0, wx.TOP, 10)
        mainsizer.Add(sizer3, 0, wx.TOP, 10)
        mainsizer.Add(sizer4, 0, wx.LEFT, 10)
        mainsizer.Add(sizer5, 0)
        mainsizer.Add(sizer6, 0)
        mainsizer.Add(sizer7, 0, wx.LEFT, 10)
        mainsizer.Add(sizer8, 0)
        mainsizer.Add(sizer9, 0)
        mainsizer.Add(sizer10, 0, wx.LEFT, 10)
        mainsizer.Add(sizer11, 0)
        mainsizer.Add(sizer12, 0)

        # Binding The Events...
        self.choiceicon1.Bind(EChoice.EVT_EXTENDEDCHOICE, self.OnChoice)
        self.choiceicon2.Bind(EChoice.EVT_EXTENDEDCHOICE, self.OnChoice)
        self.choiceicon3.Bind(EChoice.EVT_EXTENDEDCHOICE, self.OnChoice)
        self.choiceicon4.Bind(EChoice.EVT_EXTENDEDCHOICE, self.OnChoice)
        self.choiceicon5.Bind(EChoice.EVT_EXTENDEDCHOICE, self.OnChoice)
        self.choiceicon6.Bind(EChoice.EVT_EXTENDEDCHOICE, self.OnChoice)
        self.choiceicon7.Bind(EChoice.EVT_EXTENDEDCHOICE, self.OnChoice)
        self.choiceicon8.Bind(EChoice.EVT_EXTENDEDCHOICE, self.OnChoice)
        self.choiceicon9.Bind(EChoice.EVT_EXTENDEDCHOICE, self.OnChoice)
        self.choiceicon10.Bind(EChoice.EVT_EXTENDEDCHOICE, self.OnChoice)
        self.choiceicon11.Bind(EChoice.EVT_EXTENDEDCHOICE, self.OnChoice)
        self.choiceicon12.Bind(EChoice.EVT_EXTENDEDCHOICE, self.OnChoice)

        self.log = wx.TextCtrl(splitter, -1,
                               style = wx.TE_MULTILINE | wx.TE_READONLY
                               | wx.HSCROLL)

        panel.SetSizerAndFit(mainsizer)

        panel.SetAutoLayout(True)
        mainsizer.Layout()
        
        wx.Log_SetActiveTarget(MyLog(self.log))
        splitter.SplitHorizontally(panel, self.log, -100)
        splitter.SetMinimumPaneSize(60)
        

    def CreateMenuBar(self):

        # Make a menubar
        file_menu = wx.Menu()
        help_menu = wx.Menu()
        
        FPBTEST_QUIT = wx.NewId()
        FPBTEST_ABOUT = wx.NewId()
        
        file_menu.Append(FPBTEST_QUIT, "&Exit")
        help_menu.Append(FPBTEST_ABOUT, "&About")

        menu_bar = wx.MenuBar()

        menu_bar.Append(file_menu, "&File")
        menu_bar.Append(help_menu, "&Help")

        self.Bind(wx.EVT_MENU, self.OnAbout, id=FPBTEST_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnQuit, id=FPBTEST_QUIT)

        return menu_bar


    def OnChoice(self, event):

        obj = event.GetEventObject()    
        self.log.write(obj.GetName() + ": " + event.GetValue() + "\n")


    def OnSortButton(self, event):

        button = event.GetEventObject()
        label = button.GetLabel()
        if label.find("Ascending") > 0:
            self.choiceicon2.SortChoices("ascending")
            button.SetLabel("Sort Descending")
            self.log.write("Choices Sorted Ascending\n")
        else:
            self.choiceicon2.SortChoices("descending")
            button.SetLabel("Sort Ascending")
            self.log.write("Choices Sorted Descending\n")
        
        event.Skip()


    def OnInsertChoice(self, event):

        newitem = self.textctrl.GetValue()
        
        if newitem.strip() == "":
            errstr = "Error: Empty Value For The Text Control! "
            errstr = errstr + "Please Put Some Text On It Before Adding A New Item."
            dlg = wx.MessageDialog(self, errstr, "ExtendedChoiceDemo Error",
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        self.choiceicon11.InsertChoice(newitem)
        self.log.write("Inserted New Choice: " + newitem + "\n")


    def OnRemoveChoice(self, event):

        selection = self.choiceicon12.GetValue()

        if selection in self.choiceicon12.GetChoices():
            
            self.choiceicon12.RemoveChoice(selection)
            self.log.write("Removed Choice: " + selection + "\n")
        else:
            errstr = "Error: Possible Empty Choice? "
            errstr = errstr + "Please Select Some Item From The ExtendedChoice Control."
            dlg = wx.MessageDialog(self, errstr, "ExtendedChoiceDemo Error",
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        

    def OnQuit(self, event):
 
        self.Destroy()


    def OnAbout(self, event):

        msg = "This is the about dialog of the ExtendedChoice demo.\n\n" + \
              "Author: Andrea Gavana @ 16 May 2005\n\n" + \
              "Please report any bug/requests or improvements\n" + \
              "To me at the following adresses:\n\n" + \
              "andrea.gavana@agip.it\n" + "andrea_gavana@tin.it\n\n" + \
              "Welcome To wxPython " + wx.VERSION_STRING + "!!"
              
        dlg = wx.MessageDialog(self, msg, "ExtendedChoice Demo",
                               wx.OK | wx.ICON_INFORMATION)
        dlg.SetFont(wx.Font(8, wx.NORMAL, wx.NORMAL, wx.NORMAL, False, "Verdana"))
        dlg.ShowModal()
        dlg.Destroy()
        
    
def main():

    app = wx.PySimpleApp()
    frame = ExtendedChoiceFrame(None, -1, "ExtendedChoice Demo", size=(750,550))
    frame.CenterOnParent()
    frame.Show()
    app.MainLoop()


if __name__ == "__main__":
    
    main()