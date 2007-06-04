import wx

class SaveasReplaceDialog(wx.Dialog):
    def __init__(self,text="", *args, **kwds):
        self.text = text
        # begin wxGlade: SaveasReplaceDialog.__init__
        kwds["style"] = wx.DEFAULT_DIALOG_STYLE
        wx.Dialog.__init__(self, *args, **kwds)
        self.label_text = wx.StaticText(self, -1, "")
        self.button_replace = wx.Button(self, wx.ID_REPLACE, "")
        self.button_saveas = wx.Button(self, wx.ID_SAVEAS, "")
        self.button_cancel = wx.Button(self, wx.ID_CANCEL, "")

        self.__set_properties()
        self.__do_layout()
        # end wxGlade

    def __set_properties(self):
        self.Bind(wx.EVT_BUTTON, self.OnButtonReplace, self.button_replace)
        self.Bind(wx.EVT_BUTTON, self.OnButtonCancel, self.button_cancel)
        self.Bind(wx.EVT_BUTTON, self.OnButtonSaveAS, self.button_saveas)
        # begin wxGlade: SaveasReplaceDialog.__set_properties
        self.SetTitle(_("Replacing subtitle"))
        self.button_replace.SetDefault()
        # end wxGlade

    def __do_layout(self):
        self.label_text.SetLabel(self.text)
        # begin wxGlade: SaveasReplaceDialog.__do_layout
        sizer_7 = wx.BoxSizer(wx.VERTICAL)
        sizer_8 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_7.Add(self.label_text, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ADJUST_MINSIZE, 0)
        sizer_8.Add(self.button_replace, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 25)
        sizer_8.Add(self.button_saveas, 0, wx.RIGHT|wx.ADJUST_MINSIZE, 25)
        sizer_8.Add(self.button_cancel, 0, wx.ADJUST_MINSIZE, 0)
        sizer_7.Add(sizer_8, 1, wx.TOP|wx.EXPAND, 20)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_7)
        sizer_7.Fit(self)
        sizer_7.SetSizeHints(self)
        self.Layout()
        # end wxGlade
        
    def OnButtonCancel(self,evt):
        self.EndModal(wx.ID_CANCEL)
    def OnButtonReplace(self,evt):
        self.EndModal(wx.ID_REPLACE)
    def OnButtonSaveAS(self,evt):
        self.EndModal(wx.ID_SAVEAS)

# end of class SaveasReplaceDialog


