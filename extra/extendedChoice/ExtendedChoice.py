# --------------------------------------------------------------------------- #
# EXTENDEDCHOICE wxPython IMPLEMENTATION
# Python Code By:
#
# Andrea Gavana, @ 16 May 2005
# Latest Revision: 18 Dec 2005, 22.48 CET
#
#
# TODO List/Caveats
#
# 1. Multiple Choices With *The Same* Label Are Not Handled Very Well In
#    The wx.EVT_MOUSEWHEEL Event Binder For The Top StaticText Control.
#    Try Putting 2 Or More Choices With The Same Name And See It For Yourself.
#
# ---------------------------------------------------------------------------
# This Should Be Written In Big Red Blinking Colour:
# 2. On Windows 2000, Icons Have A *BAD* Black Background, Instead Of The
#    Transparent One.
# ---------------------------------------------------------------------------
#
# 3. Layout With Sizers May Be Handled Better. I Am Unable To Set Correctly
#    The Vertical Size Of The Top StaticText When An Item Spans More Than
#    1 Row (See The Demo, 3rd Control Called "Same Icon").
#    Moreover, I Am Unable To Set The Size Of The Top StaticText Control
#    *Without* A wx.EVT_SIZE Handler. Can This Be Avoided?
#
# 4. After The Failures Of wx.PopupTransientWindow And wx.PopupWindow, I Am
#    Using A wx.Dialog To Popup The Choices. By Looking At The wxPython Demo,
#    Under wx.lib.popupctl, It Seems That This Approach May Not Work On MAC.
#
# 5. Other Issues?
#
#
# For All Kind Of Problems, Requests Of Enhancements And Bug Reports, Please
# Write To Me At:
#
# andrea.gavana@agip.it
# andrea_gavan@tin.it
#
# Or, Obviously, To The wxPython Mailing List!!!
#
#
# End Of Comments
# --------------------------------------------------------------------------- #


"""Description:

The idea of an ExtendedChoice implementation that is (hopefully) portable to all
platforms supported by wxPython is interesting. Windows already have this kind
of feature.
ExtendedChoice is built using 4 different controls:

- A wx.StaticBitmap to handle the icons;
- A wx.lib.stattext.StaticText to simulate the behavior of a wx.TextCtrl (which
  does not line up correctly in a sizer if you use the wx.NO_BORDER style for it);
- A wx.lib.buttons.GenBitmapButton to simulate the wx.Choice/wx.ComboBox button;
- A wx.Dialog (to replace a wx.PopupTransientWindow) with a wx.VListBox inside
  to simulate the behavior of wx.Choice/wx.ComboBox expanded choice list.

What It Can Do:

- Behaves like wx.Choice or wx.ComboBox in handling Char/Key events;
- Set the whole control colour or change it in runtime;
- Set most Background/Foreground colour for choices, Background/Foreground
- Motifs/Styles, text colour and text selection colour;
- Set or change in runtime font associated to each or all the choices;
- Depending On The Class Construction (EC_RULES Style), You Can Have Borders
  And Customize Them;
- Sort ascending/descending the choices;
- Add or remove choices from the choice-list;
- Add icons/images in runtime to the wx.ImageList associated to the control;
- Change the order in which icons and choices are associated (change icon for
  an already present choice);
- Replace choices with other user-defined strings/labels.

Event Handlers:

- wx.EVT_CHAR events: ExtendedChoice handles char events by recognizing the char
  keycode, and these actions are taken accordingly:

  a) Special keys like TAB, SHIFT-TAB, ENTER: these are passed to the next control
     using wx.NavigationKeyEvent();
  b) wx.Choice navigation keys like UP/DOWN/LEFT/RIGHT ARROWS are used to move
     selection up/down/up/down; PAGEUP, PAGEDOWN, HOME and END keys select
     respectively the first/last/first/last choice in the choice-list;
  c) Other keys are used to navigate between choices in the choice-list just like
     wx.Choice/wx.ComboBox.

- wx.EVT_MOUSEWHEEL event: When the control has the focus, mouse wheeling up/down
  scrolls the choice-list up and down.

- wx.EVT_LEFT_DOWN event: the left mouse button down is used when the choice-list
  is displayed in the wx.PopupTransientWindow. It is used to select an item from
  the list. This events triggers the custom wxEVT_EXTENDEDCHOICE event. I have
  chosen this event instead of the wx.EVT_LISTBOX because the latest one does not
  get called when you are handling other mouse events.

- wx.EVT_ENTER_WINDOW/wx.EVT_LEAVE_WINDOW events: these events affect:

  a) The button in ExtendedChoice. When the mouse enters the button area, the
     button changes slightly the colour to simulate some kind of "3D rendering".
  b) The wx.VListBox in the choice-list when it is displayed inside the
     wx.Dialog. When the mouse enters a choice "region", the choice is
     highlighted, while when it leaves the region returns in its normal state.

- wx.EVT_BUTTON event: this event is used to trigger the button-down of the
  control. It displays the choice-list in the wx.Dialog.

- wx.EVT_KILL_FOCUS/wx.EVT_SET_FOCUS events: these events are used to somewhat
  reproduce "correctly" the text selection in the ExtendeChoice when it loses or
  aquires the focus.


ExtendedChoice is freeware and distributed under the wxPython license. 

Special Thanks To Franz Steinhausler And Robin Dunn For Their Nice Suggestions.

Latest Revision: Andrea Gavana @ 18 Dec 2005, 22.48 CET

"""


import wx
from wx.lib.stattext import GenStaticText as StaticText
from wx.lib.buttons import GenBitmapButton as BitmapButton


def GetChoiceIconData():
    return \
'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10\x08\x06\
\x00\x00\x00\x1f\xf3\xffa\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\
\x00\x00BIDAT8\x8dcddbf\xa0\x040Q\xa4{P\x18\xc0\x82.\xf0\xff\xdf\xdf\xff\xb8\
\x143213R\xdd\x05\x18\x06`\xb3\x05\x9f8m\x02\x11\xdd6\\\xb6\xd3\xce\x05\xc8\
\xb6\xe2\xb3\x9d*.`\x1c\xcd\x0b\x0c\x00\x9e\xbc\x04W\x19\xcfa\xb5\x00\x00\
\x00\x00IEND\xaeB`\x82' 


def GetChoiceIconBitmap():
    return wx.BitmapFromImage(GetChoiceIconImage())

def GetChoiceIconImage():
    import  cStringIO
    stream = cStringIO.StringIO(GetChoiceIconData())
    return wx.ImageFromStream(stream)


# ExtendedChoice Style
# If Called With This Style, You Will Have Borders Between Items And You
# Can Customize The Border Appearance With ExtendedChoiceStyle Class
EC_RULES = 1

# ExtendedChoice ExtraStyle
# Choosing EC_CHOICE As extrastyle Parameter (The Default), Will Cause
# ExtendedChoice To Behave Like wx.Choice In Handling wx.EVT_CHAR And
# wx.EVT_KEY_DOWN When The wx.VListBox Is Opened.
# If You Choose EC_COMBO, ExtendedChoice Will Behave Like wx.ComboBox
# In The Same Events.
EC_CHOICE = 2
EC_COMBO = 3

# Event Declarations
wxEVT_EXTENDEDCHOICE = wx.NewEventType()
EVT_EXTENDEDCHOICE = wx.PyEventBinder(wxEVT_EXTENDEDCHOICE, 1)

# ---------------------------------------------------------------
# Class ExtendedChoiceEvent
# ---------------------------------------------------------------
# This Class Implements The Event Listener For The ExtendedChoice
# ---------------------------------------------------------------

class ExtendedChoiceEvent(wx.PyCommandEvent):

    def __init__(self, eventType):
        """ Default Class Constructor.

        This Event Is Used When The Choice-List Is Displayed In The
        wx.Dialog.
        """
        
        wx.PyCommandEvent.__init__(self, eventType)
        self._eventType = eventType


    def SetValue(self, value):
        "Sets The Value For The Selected Item."
        
        self._value = value


    def GetValue(self):
        "Returns The Value For The Selected Item."
        
        return self._value


# ---------------------------------------------------------------
# Class ExtendedChoiceStyle
# ---------------------------------------------------------------
# General Class To Handle The Following Text/Item/Control Features:
# a) The Whole ExtendedChoice Control Colour
# b) The wx.VListBox BackgroundColour
# c) The Selection Colour In The wx.VListBox
# d) The Text Selection Colour In The wx.VListBox
# e) Individual Item Font
# f) Individual Item Background Colour
# g) Individual Item Foreground Colour
# h) Individual Item Background Motif/Style
# i) Borders Between Items (If style=EC_RULES Is Specified)
# ---------------------------------------------------------------

class ExtendedChoiceStyle:

    def __init__(self, parent):
        """ Default constructor for this class.

        The Parent Is ExtendedChoice.
        """

        self._parent = parent
        self._choices = self._parent._choices
        self._hasborders = self._parent._hasborders
        self.ResetDefaults()


    def ResetDefaults(self):
        """ Resets Default ExtendedChoiceStyle."""
        
        self._itemfont = [self._parent.GetFont()]*len(self._choices)
        self._itemforegroundcolour = [wx.BLACK]*len(self._choices)
        self._itembackgroundcolour = [wx.WHITE]*len(self._choices)
        self._itembackgroundmotif = [wx.SOLID]*len(self._choices)
        self._backcontrolcolour = wx.WHITE
        self._selectioncolour = wx.BLUE
        self._textselectioncolour = wx.WHITE
        self._controlcolour = wx.NamedColour("Light Grey")
        self._border = wx.TRANSPARENT_PEN


    def CheckInput(self, n, functionname):
        """Checks If All Input Arguments For The Set* Functions Are Correct."""
        
        if n is None:
            raise "ERROR: None Item Passed To " + functionname

        if n >= len(self._choices):
            raise "ERROR: Item Number Passed To " + functionname + " (" + \
                  str(n) + ") Exceed The Length Of Choices-List (" + \
                  str(len(self._choices)) + ")"

        if n < 0:
            raise "ERROR: Negative Item Index Passed To " + functionname


    def SetControlColour(self, colour=None):
        """Sets The Main Control Colour (Button And Small Background Window)."""
        
        if colour is None:
            colour = wx.NamedColour("Light Grey")
            
        self._parent.SetBackgroundColour(colour)
        self._parent._choicebutton.SetBackgroundColour(colour)
        self._controlcolour = colour
        self._parent.Refresh()
        

    def GetControlColour(self):
        """Returns The Main Control Colour (Button And Small Background Window)."""
        
        return self._controlcolour
    

    def SetBorder(self, border=None):
        """Sets The Border Between Items In The wx.VListBox.

        The Border Is A wx.Pen() Object, Defined As You Prefer.
        In Order To Call This Function, You Need To Call ExtendedChoice Class With
        The Keyword style=EC_RULES.
        """
        
        if border is None:
            border = wx.TRANSPARENT_PEN

        self._border = border


    def GetBorder(self):
        """Returns The Border (A wx.Pen) Between Items In The wx.VListBox.

        In Order To Call This Function, You Need To Call ExtendedChoice Class With
        The Keyword style=EC_RULES.
        """
        
        return self._border
    

    def SetTextSelectionColour(self, colour=None):
        """Sets The Text Selection Colour For The wx.VListBox.

        When The Mouse Is Hovering Over An Item In The wx.VListBox, The Text
        Foreground Colour Changes To The Value Set Here.
        """
        
        if colour is None:
            colour = wx.WHITE

        self._textselectioncolour = colour


    def GetTextSelectionColour(self):
        """Returns The Text Selection Colour For The wx.VListBox."""
        
        return self._textselectioncolour        
        
        
    def SetItemFont(self, n=None, font=None):
        """Sets The Font For A Particular Item In The Choices-List."""
        
        self.CheckInput(n, "SetItemFont")
        
        if font is None:
            font = self._itemfont[n]
            
        self._itemfont[n] = font
    
        dc = wx.MemoryDC()
        widths = []
        for indx, choice in enumerate(self._parent._choices):
            for line in choice.split('\n'):
                textext = dc.GetFullTextExtent(line, self.GetItemFont(indx))
                widths.append(textext[0])
            
        maxextent = max(widths)
        self._parent._textminsize = (maxextent, -1)
        self._parent._statictext.SetMinSize(self._parent._textminsize)
        

    def SetAllItemsFont(self, font=None):
        """Sets The Font For All The Items In The Choices-List."""
        
        if font is None:
            font = self._itemfont[n]

        self._itemfont = [font]*len(self._itemfont)
    
        dc = wx.MemoryDC()
        widths = []
        for indx, choice in enumerate(self._parent._choices):
            for line in choice.split('\n'):
                textext = dc.GetFullTextExtent(line, self.GetItemFont(indx))
                widths.append(textext[0])
            
        maxextent = max(widths)
        self._parent._textminsize = (maxextent, -1)
        self._parent._statictext.SetMinSize(self._parent._textminsize)
    

    def GetItemFont(self, n=None):
        """Returns The Font For A Particular Item In The Choices-List."""
        
        self.CheckInput(n, "GetItemFont")
        return self._itemfont[n]


    def SetItemForegroundColour(self, n=None, colour=None):
        """Sets The Foreground Colour For A Particular Item In The Choices-List."""
        
        self.CheckInput(n, "SetItemForegroundColour")

        if colour is None:
            colour = self.GetItemForegroundColour(n)
            
        self._itemforegroundcolour[n] = colour


    def SetAllItemsForegroundColour(self, colour=None):
        """Sets The Foreground Colour For All The Items In The Choices-List."""
        
        if colour is None:
            colour = self.GetItemForegroundColour(0)
            
        self._itemforegroundcolour = [colour]*len(self._itemforegroundcolour)
        

    def GetItemForegroundColour(self, n=None):
        """Returns The Foreground Colour For A Particular Item In The Choices-List."""
        
        self.CheckInput(n, "GetItemForegroundColour")
        return self._itemforegroundcolour[n]

    
    def SetItemBackgroundColour(self, n=None, colour=None):
        """Sets The Background Colour For A Particular Item In The Choices-List."""
        
        self.CheckInput(n, "SetItemBackgroundColour")

        if colour is None:
            colour = self.GetItemBackgroundColour(n)
            
        self._itembackgroundcolour[n] = colour


    def SetAllItemsBackgroundColour(self, colour=None):
        """Sets The Background Colour For All The Items In The Choices-List."""
        
        if colour is None:
            colour = self.GetItemBackgroundColour(0)
            
        self._itembackgroundcolour = [colour]*len(self._itembackgroundcolour)
        

    def GetItemBackgroundColour(self, n=None):
        """Returns The Background Colour For A Particular Item In The Choices-List."""
        
        self.CheckInput(n, "GetItemBackgroundColour")
        return self._itembackgroundcolour[n]


    def SetItemBackgroundMotif(self, n=None, motif=None):
        """Sets The Background Motif/Style For A Particular Item In The Choices-List.

        The Motif Is A wx.Brush() Object, Defined As You Wish.        
        """
        
        self.CheckInput(n, "SetItemBackgroundMotif")

        if motif is None:
            motif = self.GetItemBackgroundMotif(n)
            
        self._itembackgroundmotif[n] = motif


    def SetAllItemsBackgroundMotif(self, motif=None):
        """Sets The Background Motif/Style For All The Items In The Choices-List.

        The Motif Is A wx.Brush() Object, Defined As You Wish.        
        """
        
        if motif is None:
            motif = self.GetItemBackgroundMotif(0)
            
        self._itembackgroundmotif = [motif]*len(self._itembackgroundmotif)
        

    def GetItemBackgroundMotif(self, n=None):
        """Returns The Background Motif/Style For A Particular Item In The Choices-List."""
        
        self.CheckInput(n, "GetItemBackgroundMotif")
        return self._itembackgroundmotif[n]


    def SetBackControlColour(self, colour=None):
        """Sets The Background Colour For The wx.VListBox."""
        
        if colour is None:
            self._backcontrolcolour = self._parent.GetBackgroundColour()

        self._backcontrolcolour = colour
        

    def GetBackControlColour(self):
        """Returns The Background Colour For The wx.VListBox."""
        
        return self._backcontrolcolour

    
    def SetSelectionColour(self, colour=None):
        """Sets The Selection Colour For The wx.VListBox.

        When The Mouse Is Hovering Over An Item In The wx.VListBox, The Text
        Background Colour Changes To The Value Set Here.
        """        
        
        if colour is None:
            self._selectioncolour = wx.BLUE

        self._selectioncolour = colour            

                    
    def GetSelectionColour(self):
        """Returns The Selection Colour For The wx.VListBox."""
        
        return self._selectioncolour
    

# -----------------------------------------------------------------------
# This Class Implements The Scolling Window That Contains The Choice-List
# Used Internally.
# -----------------------------------------------------------------------

class TransientChoice(wx.Dialog):

    def __init__(self, parent, style):
        """ Default Class Constructor.

        Used Internally. Do Not Use It Directly In This Control!"""
        
        wx.Dialog.__init__(self, parent, -1, style=style | wx.WANTS_CHARS)

        self._parent = parent
        self.SetBackgroundColour(self._parent.GetBackgroundColour())

        self._vlistbox = VListChoice(self, -1, style=wx.SIMPLE_BORDER)
        self._vlistbox.SetItemCount(len(self._parent._choices))

        sz = self.GetBestSize()

        parentwidth = self._parent.GetSize()[0]
        
        if sz[0] < parentwidth:
            sz[0] = parentwidth

        minheight = self._vlistbox.MeasureAllItems()
        yvideo = wx.SystemSettings_GetMetric(wx.SYS_SCREEN_Y)

        pos = self._parent.ClientToScreen((0,0))
        sz =  self._parent.GetSize()

        if self._parent._itemsperpage is None:

            yvideo = wx.SystemSettings_GetMetric(wx.SYS_SCREEN_Y)
            vlistboxsize = self._vlistbox.GetSize()

            if minheight > 3*yvideo/7:
                minheight = 3*yvideo/7

            if pos[1] + sz[1] + minheight > yvideo:
                minheight = yvideo - pos[1] - sz[1] - 30
                
        else:
            
            minheight = self._vlistbox.CalculateBestSize(self._parent._itemsperpage)

        self._vlistbox.SetMinSize((sz.width, minheight))
        self.SetDimensions(pos[0], pos[1]+sz[1], -1, minheight)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._vlistbox, 0)
        
        self.SetSizerAndFit(sizer)
        self.Layout()
        
        currentvalue = self._parent.GetValue()
        if currentvalue in self._parent._choices:
            indx = self._parent._choices.index(currentvalue)
            self._vlistbox.SetSelection(indx)
        else:
            self._vlistbox.SetSelection(0)

        
    def ProcessLeftDown(self, evt):
        return False

    def OnDismiss(self):
        pass
    

# ---------------------------------------------------------------
# Class VListChoice
# ---------------------------------------------------------------
# This Class Handles The wx.VListBox That Pops-Up Together With
# The wx.Dialog. Mouse/Char/Focus Events Are Handled To Allow:
# a) The Selection Of Choices While The Mouse Is Hovering Over
#    An Item;
# b) The Scrolling Of The wx.VListBox Using The Mouse Wheel;
# c) The Correct Identification Of An Item By A Key Press;
# d) The Focus Lost Generate A Destroy() Event For The wx.Dialog.
# ---------------------------------------------------------------


class VListChoice(wx.VListBox):

    def __init__(self, parent, id, style=0):
        """ Default Class Constructor.

        This Class Is Used Internally. Do Not Call It Explicitly!
        """
        
        self._parent = parent._parent
        
        wx.VListBox.__init__(self, parent, id, pos=wx.DefaultPosition,
                             size=wx.DefaultSize,
                             style=wx.SIMPLE_BORDER | wx.LB_NEEDED_SB | wx.WANTS_CHARS)

        self.ecstyle = self._parent.ecstyle
        self.extrastyle = self._parent._extrastyle
        
        selectioncolour = self.ecstyle.GetSelectionColour()
        backcontrolcolour = self.ecstyle.GetBackControlColour()
        
        self.SetBackgroundColour(backcontrolcolour)
        self.SetSelectionBackground(selectioncolour)

        self.SetFocus()
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnterWindow)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeaveWindow)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_CHAR, self.OnChar)
        self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        

    def OnKillFocus(self, event):
        """ The wx.VListBox Has Lost The Focus.

        Sets The Focus To The Top StaticText And Destroy The Container Of
        wx.VListBox (wx.Dialog).
        """
        
        self.GetParent().Destroy()
        
        if self._parent.GetValue() not in self._parent._choices:
            self._parent._statictext.SetBackgroundColour(wx.WHITE)
            self._parent._statictext.GetParent().SetBackgroundColour(wx.WHITE)
            self._parent._staticbmp.SetBackgroundColour(wx.WHITE)
            self._parent._statictext.GetParent().Refresh()

        self._parent._statictext.SetFocus()
        event.Skip()


    def OnKeyDown(self, event):
        """Handles The wx.EVT_KEY_DOWN Event.

        Non-Characters Events (Like Page-up/Down etc...) Are Handled Here,
        While Characters Inputs Are Passed To The wx.EVT_CHAR Listener.
        """

        if self.extrastyle == EC_COMBO:
            self.Unbind(wx.EVT_KILL_FOCUS)

        charcode = event.GetKeyCode()

        if event.AltDown() and charcode == wx.WXK_DOWN:
            self.GetParent().Destroy()
            return
        
        if charcode in [wx.WXK_RETURN, wx.WXK_TAB, wx.WXK_ESCAPE]:
            if charcode == wx.WXK_RETURN:
                indx = self.GetSelection()
                newvalue = self._parent._choices[indx]
                self._parent.SetValue(newvalue)
                self.GetParent().Destroy()
                        
            elif charcode == wx.WXK_TAB:
                self.GetParent().Destroy()
                nav = wx.NavigationKeyEvent()
                nav.SetEventObject(self._parent._statictext.GetParent())
                nav.SetCurrentFocus(self._parent.GetParent())
                self._parent.GetParent().GetEventHandler().ProcessEvent(nav)
                
            else:
                self.GetParent().Destroy()
            
            return

        currentvalue = self._parent.GetValue()
        newvalue = currentvalue
        send_event = True
        
        if charcode in [wx.WXK_HOME, wx.WXK_PRIOR]:
            newvalue = self._parent._choices[0]
            self.SetSelection(0)
            self.Refresh()
            
        elif charcode in [wx.WXK_END, wx.WXK_NEXT]:
            newvalue = self._parent._choices[-1]
            self.SetSelection(self.GetItemCount()-1)
            self.Refresh()
            
        elif charcode in [wx.WXK_RIGHT, wx.WXK_DOWN]:
            if currentvalue != self._parent._choices[-1]:
                if currentvalue in self._parent._choices:
                    indx = self._parent._choices.index(currentvalue)
                    newvalue = self._parent._choices[indx+1]
                    self.SetSelection(self.GetSelection()+1)
                else:
                    newvalue = self._parent._choices[0]
                    self.SetSelection(0)

                self.Refresh()
                
        elif charcode in [wx.WXK_LEFT, wx.WXK_UP]:
            if currentvalue != self._parent._choices[0]:
                if currentvalue in self._parent._choices:
                    indx = self._parent._choices.index(currentvalue)
                    newvalue = self._parent._choices[indx-1]
                    self.SetSelection(self.GetSelection()-1)
                else:
                    newvalue = self._parent._choices[0]
                    self.SetSelection(0)
                    
                self.Refresh()

        else:
            send_event = False
            event.Skip()
            
        if send_event:
            self._parent.SetValue(newvalue)
            # Event Handler/Listener
            eventOut = ExtendedChoiceEvent(wxEVT_EXTENDEDCHOICE)
            eventOut.SetValue(newvalue)
            eventOut.SetEventObject(self._parent)
            self._parent.GetEventHandler().ProcessEvent(eventOut)

        if self.extrastyle == EC_COMBO:
            self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)

        
    def OnChar(self, event):
        """Handles The wx.EVT_CHAR Event.

        Input Characters Are Pre-Processed In Order To Find Some Match Between
        Typed Char And Starting Letters In The Choices-List.
        """

        if self.extrastyle == EC_COMBO:
            self.Unbind(wx.EVT_KILL_FOCUS)
        
        currentvalue = self._parent.GetValue()
        send_event = True
        
        charcode = event.GetKeyCode()
            
        try:
            
            typedchar = chr(charcode)
            startletters = [ch[0] for ch in self._parent._choices]
        
            if typedchar in startletters:
                
                indexes = [indx for indx, sts in enumerate(startletters) \
                           if sts == typedchar]

                if currentvalue in self._parent._choices:
                    indx = self._parent._choices.index(currentvalue)
                    startvalue = currentvalue[0]

                    if startvalue == typedchar:
                        if len(indexes) > 1:
                            if indx == max(indexes):
                                nextindex = indexes[0]
                            else:
                                nextindex = indexes[indexes.index(indx) + 1]
                        else:
                            nextindex = indx
                    else:
                        nextindex = startletters.index(typedchar)
                        
                    newvalue = self._parent._choices[nextindex]

                else:

                    nextindex = startletters.index(typedchar)
                    newvalue = self._parent._choices[nextindex]
                    
                send_event = True
                self.SetSelection(nextindex)
                self.Refresh()

            else:
                
                newvalue = currentvalue
                send_event = False

        except:

            newvalue = None                
            send_event = False
            
        if newvalue in self._parent._choices:
            self._parent.SetValue(newvalue)

            if send_event:
                # Event Handler/Listener
                eventOut = ExtendedChoiceEvent(wxEVT_EXTENDEDCHOICE)
                eventOut.SetValue(newvalue)
                eventOut.SetEventObject(self._parent)
                self._parent.GetEventHandler().ProcessEvent(eventOut)

        if self.extrastyle == EC_COMBO:
            self.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
            
        event.Skip()
        

    def MeasureAllItems(self):
        """Returns The Cumulative Height Of All The Items In The wx.VListBox."""
        
        height = 0
        for choice in self._parent._choices:
            for line in choice.split('\n'):
                w, h = self.GetTextExtent(line)
                height += h
        
        return height + 5
    

    def CalculateBestSize(self, number):
        """Returns The Approximate Height Of "number" Items.

        This Is Useful If You Have Decided To Use The itemsperpage Option In
        ExtendedChoice.
        """
        
        height = 0
        for choice in self._parent._choices[0:number]:
            for line in choice.split('\n'):
                w, h = self.GetTextExtent(line)
                if h < 18:
                    height = height + 18
                else:
                    height = height + h

        return height + 5
    

    def OnEnterWindow(self, event):
        """Handles The wx.EVT_ENTER_WINDOW Event.

        This Event Is Used Only To Activate wx.EVT_MOTION."""
        
        self.Bind(wx.EVT_MOTION, self.OnMotionWindow)
        event.Skip()


    def OnLeaveWindow(self, event):
        """Handles The wx.EVT_LEAVE_WINDOW Event.

        This Event Is Used Only To Deactivate wx.EVT_MOTION."""
        
        self.Unbind(wx.EVT_MOTION)
        event.Skip()
        

    def OnMotionWindow(self, event):
        """Handles The wx.EVT_MOTION Event.

        Noting That wx.VListBox Has No Automatic Way To Detect Mouse Hovering Over
        An Item, This Seems The Best Choice To Highlight Items When Mouse Is Over
        One Of Them, To Emulate The wx.Choice/wx.ComboBox Behavior.
        """
        
        if event.Moving():
            item = self.HitTest(event.GetPosition())
            if item >= 0:
                self.SetSelection(item)

        event.Skip()

    
    def OnMouseWheel(self, event):
        """Handles The Middle Mouse Wheel For The VListBox.

        When The VListBox Is Shown, Mouse Wheeling Up/Down Scrolls The
        Choice-List Up And Down.
        """

        self.Unbind(wx.EVT_MOTION)
        
        if event.GetWheelRotation() < 0:
            try:
                currentitem = self.GetSelection()
                self.SetSelection(currentitem+1)
            except:
                self.SetSelection(self.GetItemCount()-1)
        else:
            try:
                currentitem = self.GetSelection()
                self.SetSelection(currentitem-1)
            except:
                self.SetSelection(0)

        self.Bind(wx.EVT_MOTION, self.OnMotionWindow)
        event.Skip()
                

    def OnDrawItem(self, dc, rect, n):
        """Method Used To Draw Choices And Icons Of The wx.VListBox.

        Here Are Handled Also Text Selection Colour And Choices Foreground
        Colours.
        This Method Is Used By wx.VListBox And It Has Been Overridden.
        """
        
        if self.GetSelection() == n:
            c = self.ecstyle.GetTextSelectionColour()
        else:
            c = self.ecstyle.GetItemForegroundColour(n)
        
        dc.SetFont(self.ecstyle.GetItemFont(n))
        dc.SetTextForeground(c)

        x, y, w, h = rect
        textrect = (x + 20, y, w, h)

        bmp = self._parent._icons.GetBitmap(self._parent._iconindex[n])        
        dc.DrawBitmap(bmp, x, y+1, True)
        dc.DrawLabel(self._parent._choices[n], textrect,
                     wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL)

        
    def OnMeasureItem(self, n):
        """Returns The Height Of The Item "n" In The wx.VListBox.

        This Method Is Used By wx.VListBox And It Has Been Overridden.
        """
        
        height = 0
        for line in self._parent._choices[n].split('\n'):
            w, h = self.GetTextExtent(line)
            height += h
        
        return height + 5


    def OnDrawBackground(self, dc, rect, n):
        """Method Used To Draw Text/Icon Background In The wx.VListBox.

        Here Are Handled Also Selection Colour, Choices Background Colours
        And (Eventually) Item Borders.
        This Method Is Used By wx.VListBox And It Has Been Overridden.
        """
        
        if self.GetSelection() == n:
            brush = wx.Brush(self.ecstyle.GetSelectionColour(), wx.SOLID)
        else:
            brush = wx.Brush(self.ecstyle.GetItemBackgroundColour(n),
                             self.ecstyle.GetItemBackgroundMotif(n))

        if self._parent._hasborders:
            borderstyle = self.ecstyle.GetBorder()
            dc.SetPen(borderstyle)
        else:
            dc.SetPen(wx.TRANSPARENT_PEN)
            
        dc.SetBrush(brush)
        dc.DrawRectangle(rect[0], rect[1], rect[2], rect[3])
        

    def OnLeftDown(self, event):
        """Event Used To Choose In The Choice-List And Update The Top StaticText Control.

        This Event Update The Top StaticText Control And Propagate The Event To The Parent."
        """
       
        selection = self.GetSelection()
        textlabel = self._parent._choices[selection]
        self._parent.SetValue(textlabel)

        eventOut = ExtendedChoiceEvent(wxEVT_EXTENDEDCHOICE)
        eventOut.SetValue(textlabel)
        eventOut.SetEventObject(self._parent)
        self._parent.GetEventHandler().ProcessEvent(eventOut)        

        self.GetParent().Destroy()
        
    
# ---------------------------------------------------------------
# This Is The Main ExtendedChoice Implementation.
# ---------------------------------------------------------------

class ExtendedChoice(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, choices=(None, None),
                 icons=None, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0,
                 itemsperpage = None, extrastyle=EC_COMBO,
                 name="extendedchoice"):
        """ Default Class Constructor.

        ExtendedChoice.__init__(self, parent, id=wx.ID_ANY, choices=None, icons=None,
                                pos = wx.DefaultPosition, size=wx.DefaultSize,
                                style=0, name="extendedchoice")

        Non-Default Parameters Are:
            - choices: A Tuple Of Lists, Built As Follows:
              a) First List: A Sequence Of Strings (The Choices)
              b) Second List: A Sequence Of Image IDs, Which Is A List Of Integers
                 That Associate Each Icon To A Choice
                 Default: range(0, len(choices))
            - icons: A wx.ImageList That Contains Some Icons
            - itemsperpage: Number Of Items "Per Page" Of The wx.VListBox. This Is
              Useful In Order To Limit The wx.VListBox Vertical Size.
            - style: If It Is Declared As style=EC_RULES, ExtendedChoice Will Draw
              Borders Between Items. These Borders Are Customizable By The User (See,
              For Instance, ExtendedChoiceStyle Class).
            - extrastyle: This Input Is Used To Set The Behavior Of ExtendedChoice:
              When EC_COMBO Is Used, It Behaves Similarly To wx.ComboBox In Handling
              wx.EVT_CHAR And wx.EVT_KEY_DOWN. If EC_CHOICE Is Used, ExtendedChoice
              Behaves Like A wx.Choice Control.
              
        """
        
        wx.Panel.__init__(self, parent, id, pos=pos, size=size, style=wx.TAB_TRAVERSAL,
                          name=name)

        if len(choices) == 1:
            choices = choices[0]
            iconindex = range(icons.GetImageCount())
        elif type(choices[0]) != type(list()):
            choices = choices
            iconindex = range(icons.GetImageCount())
        else:
            iconindex = choices[1]
            choices = choices[0]
        
        if icons is None:
            raise "ERROR: Unable To Initialize ExtendedChoice: Missing Icons"

        if size[0] > 0:
            self.SetMinSize((size[0],-1))
        else:
            size = (-1,-1)

        if style & EC_RULES == EC_RULES:
            self._hasborders = 1
        else:
            self._hasborders = 0

        self._iconindex = iconindex[:]
        self._choices = choices[:]
        self._icons = icons
        self._sorted = False
        self._itemsperpage = itemsperpage
        self._extrastyle = extrastyle

        self.ecstyle = ExtendedChoiceStyle(self)
        
        self.SetBackgroundColour(self.ecstyle.GetControlColour())
        mainsizer = wx.BoxSizer(wx.VERTICAL)

        whitepanel = wx.Panel(self, -1)
        
        choicesizer = wx.BoxSizer(wx.HORIZONTAL)
        staticsizer = wx.BoxSizer(wx.VERTICAL)
        bitmapsizer = wx.BoxSizer(wx.VERTICAL)

        lengths = []
        
        for choice in choices:
            for line in choice.split("\n"):
                lengths.append(len(line))

        lengthtest = lengths.index(max(lengths))
        test = choices[lengthtest]
        
        self._statictext = ECTextCtrl(whitepanel, -1, test,
                                      style=wx.WANTS_CHARS | wx.NO_BORDER
                                      | wx.TAB_TRAVERSAL)

        self._textminsize = self._statictext.GetSize()
        
        emptybmp = wx.EmptyBitmap(16,16)
        mask = wx.Mask(emptybmp, wx.BLACK)
        emptybmp.SetMask(mask)
        
        self._staticbmp = wx.StaticBitmap(whitepanel, -1, emptybmp)
        
        self._choicebutton = ECButton(whitepanel, -1, bmp=GetChoiceIconBitmap(),
                                      size=(20,20), style=wx.BORDER_STATIC)

        self._choicebutton.SetUseFocusIndicator(False)
        
        bitmapsizer.Add((0,0),1)
        bitmapsizer.Add(self._staticbmp, 0, wx.ALIGN_CENTER_VERTICAL)
        bitmapsizer.Add((0,0),1)
        
        choicesizer.Add(bitmapsizer, 0, wx.ALIGN_LEFT | wx.ALIGN_CENTER_VERTICAL
                        | wx.RIGHT | wx.LEFT, 2)

        staticsizer.Add((0,0),1)
        staticsizer.Add(self._statictext, 0, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL
                        | wx.LEFT, 1)
        staticsizer.Add((0,0),1)
        
        choicesizer.Add(staticsizer, 1, wx.EXPAND | wx.ALIGN_BOTTOM | wx.RIGHT, 4)
        choicesizer.Add(self._choicebutton, 0, wx.EXPAND)
        whitepanel.SetSizer(choicesizer)
        
        mainsizer.Add(whitepanel, 1, wx.EXPAND | wx.ALL, 1)        
        self.SetSizer(mainsizer)
        mainsizer.Layout()
        
        self._choicebutton.Bind(wx.EVT_BUTTON, self.OnChoiceButton)
        self._choicebutton.Bind(wx.EVT_ENTER_WINDOW, self.OnChoiceEnter)
        self._choicebutton.Bind(wx.EVT_LEAVE_WINDOW, self.OnChoiceLeave)

        self._statictext.Bind(wx.EVT_CHAR, self.OnChar)        
        self._statictext.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self._statictext.Bind(wx.EVT_SET_FOCUS, self.OnSetFocus)
        self._statictext.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self._statictext.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        
        self._staticbmp.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)

        self._statictext.SetBackgroundColour(self.ecstyle.GetBackControlColour())
        self._staticbmp.SetBackgroundColour(self.ecstyle.GetBackControlColour())
        self._statictext.SetForegroundColour(self.ecstyle.GetBackControlColour())        
        whitepanel.SetBackgroundColour(self.ecstyle.GetBackControlColour())

        self.Bind(wx.EVT_SIZE, self.OnSize)
        
        self._statictext.SetLabel("")


    def OnSize(self, event):
        """Handles The Event Size, To Avoid Bad Resizing Of The Control."""
        
        self._statictext.SetMinSize(self._textminsize)
        self._statictext.Refresh()
        event.Skip()

        
    def OnLeftDown(self, event):
        """Handles The Mouse Click On The Top Static Text And Static Bitmap.

        The Mouse Click Opens The Choices-List.
        """
                
        if len(self._choices) == 0:
            return

        self._choicewindow = TransientChoice(self, style=wx.SIMPLE_BORDER)        
        self._choicewindow.Show()
        self._choicewindow.Refresh()
        
        event.Skip()
        

    def OnChoiceButton(self, event):
        """Handles The wx.EVT_LEFT_DOWN Event Of The Main Button Of The Control.

        This Action Causes The wx.Dialog That Contains Choices And Icons To
        Pop-Up. The Pop-Up Does Not Happen If The Choice-List Is Empty.
        """

        if len(self.GetChoices()) == 0:
            return
        
        self._choicewindow = TransientChoice(self, style=wx.SIMPLE_BORDER)        
        self._choicewindow.Show()
        self._choicewindow.Refresh()
        

    def OnChoiceLeave(self, event):
        """Handles The wx.EVT_LEAVE_WINDOW Event For The Main Control Button.

        When The Mouse Leaves The Button Area, The Button Returns To Its Initial State.
        """
        
        self._choicebutton.SetBackgroundColour(self.ecstyle.GetControlColour())
        self._choicebutton.Refresh()
        event.Skip()


    def OnChoiceEnter(self, event):
        """Handles The wx.EVT_ENTER_WINDOW Event For The Main Control Button.

        When The Mouse Enters The Button Area, The Button Changes Slightly The
        Colour To Simulate Some Kind Of "3D Rendering".
        """
        
        entercolour = self.ecstyle.GetControlColour()
        firstcolour  = entercolour.Red()
        secondcolour = entercolour.Green()
        thirdcolour = entercolour.Blue()
        
        if entercolour.Red() > 235:
            firstcolour = entercolour.Red() - 40
        if entercolour.Green() > 235:
            secondcolour = entercolour.Green() - 40
        if entercolour.Blue() > 235:
            thirdcolour = entercolour.Blue() - 40
            
        entercolour = wx.Colour(firstcolour+20, secondcolour+20, thirdcolour+20)
        
        self._choicebutton.SetBackgroundColour(entercolour)
        self._choicebutton.Refresh()
        event.Skip()


    def OnMouseWheel(self, event):
        """Handles The Middle Mouse Wheel For The Control.

        When The Control Has The Focus, Mouse Wheeling Up/Down Scrolls The
        Choice-List Up And Down.
        """

        currentvalue = self.GetValue()

        if currentvalue not in self._choices:
            return
        
        send_event = False
        indexes = [indx2 for indx2, sts in enumerate(self._choices) \
                  if sts == currentvalue]
                       
        if event.GetWheelRotation() < 0:
            indx = self._choices.index(currentvalue)
            if len(indexes) > 1:
                if indx == max(indexes):
                    nextindex = indx
                else:
                    nextindex = indexes[indexes.index(indx) + 1]
            else:
                nextindex = indx

            try:
                newvalue = self._choices[nextindex+1]
                self.SetValue(newvalue)
                send_event = True
            except:
                pass
                
        else:
            indx = self._choices.index(currentvalue)
            if len(indexes) > 1:
                if indx == min(indexes):
                    nextindex = indx
                else:
                    nextindex = indexes[indexes.index(indx) - 1]
            else:
                nextindex = indx
                
            try:
                newvalue = self._choices[nextindex-1]
                self.SetValue(newvalue)
                send_event = True
            except:
                pass

        if send_event:
            # Event Handler/Listener
            eventOut = ExtendedChoiceEvent(wxEVT_EXTENDEDCHOICE)
            eventOut.SetValue(newvalue)
            eventOut.SetEventObject(self)
            self.GetEventHandler().ProcessEvent(eventOut)
        
        event.Skip()
        

    def OnChar(self, event):
        """Handles The wx.EVT_CHAR Event For The Control.

        ExtendedChoice Handles Char Events By Recognizing The Char Keycode,
        And These Actions Are Taken Accordingly:

        a) Special Keys Like TAB, SHIFT-TAB, ENTER: These Are Passed To The Next Control
        Using wx.NavigationKeyEvent();
        b) wx.Choice Navigation Keys Like UP/DOWN/LEFT/RIGHT ARROWS Are Used To Move
        Selection Up/Down/Up/Down; PAGEUP, PAGEDOWN, HOME And END Keys Select
        Respectively The First/Last/First/Last Choice In The Choice-List;
        c) Other Keys Are Used To Navigate Between Choices In The Choice-List Just Like
        wx.Choice/wx.ComboBox.
        """
        
        charcode = event.GetKeyCode()
        currentvalue = self.GetValue()
        
        newvalue = currentvalue
        send_event = False

        if event.AltDown() and charcode == wx.WXK_DOWN:
            if hasattr(self, "_choicewindow"):
                if self._choicewindow:
                    self._choicewindow.Destroy()
                    return
                
            self._choicewindow = TransientChoice(self, style=wx.SIMPLE_BORDER)
            self._choicewindow.Show()
            self._choicewindow._vlistbox.SetFocus()
            self._choicewindow.Refresh()
            return
        
        if charcode in [wx.WXK_TAB, wx.WXK_RETURN, wx.WXK_ESCAPE]:
            if charcode == wx.WXK_RETURN:
                if hasattr(self, "_choicewindow"):
                    if self._choicewindow:
                        indx = self._choicewindow._vlistbox.GetSelection()
                        newvalue = self._choices[indx]
                        self.SetValue(newvalue)

            elif charcode == wx.WXK_TAB:
                nav = wx.NavigationKeyEvent()
                nav.SetEventObject(event.GetEventObject())
                nav.SetCurrentFocus(self.GetParent())
                self.GetParent().GetEventHandler().ProcessEvent(nav)

            if hasattr(self, "_choicewindow"):
                if self._choicewindow:                        
                    self._choicewindow.Destroy()
                                
            return
        
        if charcode in [wx.WXK_HOME, wx.WXK_PRIOR]:
            newvalue = self._choices[0]
            send_event = True
            
        elif charcode in [wx.WXK_END, wx.WXK_NEXT]:
            newvalue = self._choices[-1]
            send_event = True
            
        elif charcode in [wx.WXK_RIGHT, wx.WXK_DOWN]:
            if currentvalue != self._choices[-1]:
                if currentvalue not in self._choices:
                    newvalue = self._choices[0]
                else:
                    indx = self._choices.index(currentvalue)
                    newvalue = self._choices[indx+1]
                    
                send_event = True
                
        elif charcode in [wx.WXK_LEFT, wx.WXK_UP]:
            if currentvalue != self._choices[0]:
                if currentvalue not in self._choices:
                    newvalue = self._choices[0]
                else:
                    indx = self._choices.index(currentvalue)
                    newvalue = self._choices[indx-1]
                    
                send_event = True

        else:
            typedchar = chr(charcode)
            startletters = [ch[0] for ch in self._choices]
        
            if typedchar in startletters:
                
                indexes = [indx for indx, sts in enumerate(startletters) \
                           if sts == typedchar]
        
                indx = self._choices.index(currentvalue)
                startvalue = currentvalue[0]

                if startvalue == typedchar:
                    if len(indexes) > 1:
                        if indx == max(indexes):
                            nextindex = indexes[0]
                        else:
                            nextindex = indexes[indexes.index(indx) + 1]
                    else:
                        nextindex = indx
                else:
                    nextindex = startletters.index(typedchar)
                    
                newvalue = self._choices[nextindex]
                send_event = True

            else:

                if currentvalue not in self._choices:
                    return
                
                newvalue = currentvalue

        self.SetValue(newvalue)
        
        if hasattr(self, "_choicewindow"):
            if self._choicewindow:
                indx = self._choices.index(newvalue)
                self._choicewindow._vlistbox.SetSelection(indx)

        if send_event:
            # Event Handler/Listener
            eventOut = ExtendedChoiceEvent(wxEVT_EXTENDEDCHOICE)
            eventOut.SetValue(newvalue)
            eventOut.SetEventObject(self)
            self.GetEventHandler().ProcessEvent(eventOut)
            
        event.Skip()
        

    def OnKillFocus(self, event):
        """Handles The wx.EVT_KILL_FOCUS Event For The Control.

        When The Control Loses The Focus, The wx.Dialog Is Destroyed And The Top
        StaticText Control Background/Foreground Colour Are Restored.
        """

        currentchoice = self.GetValue()
        if currentchoice in self._choices:
            indx = self._choices.index(currentchoice)            
            self._statictext.SetBackgroundColour(wx.WHITE)
            self._statictext.GetParent().SetBackgroundColour(wx.WHITE)
            self._statictext.SetForegroundColour(self.ecstyle.GetItemForegroundColour(indx))
            self._staticbmp.SetBackgroundColour(wx.WHITE)
        else:
            self._statictext.GetParent().SetBackgroundColour(wx.WHITE)
            self._statictext.SetBackgroundColour(wx.WHITE)
            self._staticbmp.SetBackgroundColour(wx.WHITE)
            
        self._statictext.GetParent().Refresh()

        if self._extrastyle == EC_CHOICE:
            if hasattr(self, "_choicewindow"):
                if self._choicewindow:
                    self._choicewindow.Destroy()
        else:
            if hasattr(self, "_choicewindow"):
                if self._choicewindow:
                    self._choicewindow._vlistbox.SetFocus()
        
        event.Skip()
        

    def OnSetFocus(self, event):
        """Handles The wx.EVT_SET_FOCUS Event For The Control.

        When The Control Gets The Focus, The Top StaticText Control Background
        Colour Bacome The User-Defined (Or Default) One.
        """

        self._statictext.SetBackgroundColour(self.ecstyle.GetSelectionColour())
        self._staticbmp.SetBackgroundColour(self.ecstyle.GetSelectionColour())
        self._statictext.GetParent().SetBackgroundColour(self.ecstyle.GetSelectionColour())
        self._statictext.SetForegroundColour(self.ecstyle.GetTextSelectionColour())
        self._statictext.GetParent().Refresh()
        event.Skip()


    def GetIconByIndex(self, indx):
        """Returns The Image Associated To The Input Index."""
        
        if indx > self._icons.GetImageCount() - 1:
            raise "ERROR: Input Index Is Greater Than ImageList Image Count"

        return self._icons.GetBitmap(self._iconindex[indx])


    def GetIconByLabel(self, label):
        """Returns The Image Associated To The Choice."""
        
        if label not in self._choices:
            raise "ERROR: Input Label Is Not Present In Initial Choices"

        indx = self._choices.index(label)
        return self.GetIconByIndex(indx)


    def GetIndexByLabel(self, label):
        """Returns The Icon Index Associated To The Choice."""
        
        if label not in self._choices:
            raise "ERROR: Input Label Is Not Present In Initial Choices"

        indx = self._choices.index(label)
        return self._iconindex[indx]
    
    def SetStringSelection(self, label):
        self.SetValue(label)


    def SetIconIndexByLabel(self, label, indx):
        """Sets The Image Index Associated To The Choice."""
        
        if label not in self._choices:
            raise "ERROR: Input Label Is Not Present In Initial Choices"

        if indx > self._icons.GetImageCount() - 1:
            raise "ERROR: Input Index Is Greater Than ImageList Image Count"

        xind = self._choices.index(label)
        self._iconindex[xind] = indx


    def SetIconIndexByRange(self, iconrange):
        """Modifies Globally The iconindex Variable."""

        if max(iconrange) > self._icons.GetImageCount() - 1:
            raise "ERROR: Maximum Value Of Input Range Is Greater Then ImageList Image Count"

        if min(iconrange) < 0:
            raise "ERROR: Minimum Value Of Input Range Is Less Than Zero"

        self._iconindex = iconrange

        
    def InsertChoice(self, inputchoice, iconindex=None):
        """Inserts A New Choice Inside The Control, With Its (Optional) Associated Icon.

        The New Choice Is Appended At The End Of The List.
        """
        
        if iconindex is None:
            iconindex = 0

        if iconindex > self._icons.GetImageCount() - 1:
            raise "ERROR: Input Icon Index Is Greater Than ExtendedChoice ImageList Count"
        
        lengths = [len(item) for item in self._choices]
        lengthtest = lengths.index(max(lengths))

        oldchoice = self.GetValue()
        
        self._choices.append(inputchoice)
        self._iconindex.append(iconindex)
        self._icons.Add(self.GetIconByIndex(iconindex))

        lastitembackground = self.ecstyle._itembackgroundcolour[-1]
        self.ecstyle._itembackgroundcolour.append(lastitembackground)
        lastitemforeground = self.ecstyle._itemforegroundcolour[-1]
        self.ecstyle._itemforegroundcolour.append(lastitemforeground)

        lastitemstyle = self.ecstyle._itembackgroundmotif[-1]
        self.ecstyle._itembackgroundmotif.append(lastitemstyle)

        lastitemfont = self.ecstyle._itemfont[-1]
        self.ecstyle._itemfont.append(lastitemfont)
        
        if len(inputchoice) > lengths[lengthtest]:
            self.SetValue(inputchoice)
            self._textminsize = self._statictext.GetSize()
            
            if oldchoice in self._choices:
                self.SetValue(oldchoice)
                

    def RemoveChoice(self, label):
        """Removes A Choice From The Choice-List."""
        
        if label not in self._choices:
            raise "ERROR: Input Label Is Not Present In Initial Choices"

        if len(self._choices) == 0:
            self._statictext.SetLabel("")
            self._statictext.Refresh()
            return
        
        indx = self._choices.index(label)
        
        # Remove Background Colour For This Item
        backremove = self.ecstyle.GetItemBackgroundColour(indx)
        self.ecstyle._itembackgroundcolour.remove(backremove)

        # Remove Foreground Colour For This Item        
        foreremove = self.ecstyle.GetItemForegroundColour(indx)
        self.ecstyle._itemforegroundcolour.remove(foreremove)

        # Remove Background Motif/Style For This Item        
        styleremove = self.ecstyle.GetItemBackgroundMotif(indx)
        self.ecstyle._itembackgroundmotif.remove(styleremove)

        # Remove Font For This Item        
        fontremove = self.ecstyle.GetItemFont(indx)
        self.ecstyle._itemfont.remove(fontremove)

        self._choices.remove(label)
        self._iconindex.remove(self._iconindex[indx])        
        oldchoice = self.GetValue()

        if len(self._choices) == 0:
            self._statictext.SetLabel("")
            self._statictext.Refresh()
            emptybmp = wx.EmptyBitmap(16,16)
            mask = wx.Mask(emptybmp, wx.BLACK)
            emptybmp.SetMask(mask)
            self._staticbmp.SetBitmap(emptybmp)
            return
        
        if oldchoice == label:
            try:
                self._statictext.SetLabel("")
                emptybmp = wx.EmptyBitmap(16,16)
                mask = wx.Mask(emptybmp, wx.BLACK)
                emptybmp.SetMask(mask)
                self._staticbmp.SetBitmap(emptybmp)
            except:
                return
                

    def GetIconIndex(self):
        """Returns The Whole iconindex Variable."""
        
        return self._iconindex
    

    def SortIndex(self, inputlist):
        """Sort A List And Returns The Indexes."""
        
        pairs = [(value, offset) for (offset, value) in enumerate(inputlist)]
        pairs.sort()
        indexes = [offset for (value, offset) in pairs]
        return indexes


    def SortChoices(self, direction="ascending"):
        """Sorts The Choices, Also In Runtime.

        Depending On The Parameter "Direction", These Sorting Options Are Applied:
            - "ascending": List Sorted Alphabetically;
            - "descending": List Sorted In Reverse Alphabetical Order.
        """
        
        if not self._sorted:
            choices = self._choices[:]
            iconindex = self._iconindex[:]
            data = zip(choices, iconindex)
        else:
            data = self._data[:]
            
        data.sort()
                
        if direction == "descending":
            data.reverse()

        if not self._sorted:
            self._data = data
            self._sorted = True
            
        choices = []
        iconindex = []
        
        for choice, indx in data:
            choices.append(choice)
            iconindex.append(indx)
            
        self._choices = choices
        self._iconindex = iconindex
        

    def InsertIcon(self, icon):
        """Inserts A New Icon/Bitmap (From File) Into The ImageList Associated To The Control."""
        
        try:
            image = wx.Bitmap(icon)
            self._icons.Add(image)
            self._iconindex.append(max(self._iconindex) + 1)
        except:
            raise "ERROR: Unable To Insert The Image " + icon + " Into ExtendedChoice ImageList"


    def InsertImage(self, image):
        """Inserts A New Image Into The ImageList Associated To The Control."""
        
        try:
            self._icons.Add(image)
            self._iconindex.append(max(self._iconindex) + 1)
        except:
            raise "ERROR: Unable To Insert The Selected Image Into ExtendedChoice ImageList"

    
    def SetValue(self, label):
        """Sets The Top StaticText Value."""
        
        if label not in self._choices:
            raise "ERROR: Input Label Is Not Present In Initial Choices"

        xind = self._choices.index(label)
        icon = self.GetIconByIndex(xind)

        self._statictext.SetLabel(label)
        self._staticbmp.SetBitmap(icon)

        self._statictext.SetMinSize(self._textminsize)
            
        self._statictext.SetBackgroundColour(self.ecstyle.GetSelectionColour())
        self._statictext.SetForegroundColour(self.ecstyle.GetTextSelectionColour())
        self._statictext.SetFont(self.ecstyle.GetItemFont(xind))
        
        self._statictext.Refresh()
        self._statictext.SetFocus()
                
    def GetStringSelection(self):
        return self.GetValue()
    
    def GetValue(self):
        """Returns The Current Value In The Top StaticText Control."""
        
        return self._statictext.GetLabel()


    def GetChoices(self):
        """Returns The Whole List Of Choices."""
        
        return self._choices
    

    def Replace(self, start, end, label):
        """Replace One Or More Choices (In A Range) With The Input Label."""
        
        if start < 0:
            raise "ERROR: Start Value Is Less Than Zero"
        if end > len(self._choices) - 1:
            raise "ERROR: End Value Is Greater Than Choices List's Length"
        
        for ii in xrange(start, end+1):
            self._choices[ii] = label


    def GetChoiceStyle(self):
        """Retunrs The ExtendedChoiceStyle Associated To The ExtendedChoice Control.

        If The User Did Not Modify It, The Default Is Returned.
        """        
        return self.ecstyle



class ECTextCtrl(StaticText):

    def __init__(self, parent, id=wx.ID_ANY, label="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):

        StaticText.__init__(self, parent, id, label, pos, size, style)


    def AcceptsFocus(self):

        return True



class ECButton(BitmapButton):

    def __init__(self, parent, id, bmp, pos=wx.DefaultPosition,
                 size = wx.DefaultSize, style=0):

        BitmapButton.__init__(self, parent, id, bmp, pos, size, style)


    def AcceptsFocus(self):

        return False