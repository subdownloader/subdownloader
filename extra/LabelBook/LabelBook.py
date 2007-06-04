# --------------------------------------------------------------------------- #
# LABELBOOK And FLATIMAGEBOOK Widgets wxPython IMPLEMENTATION
#
# Original C++ Code From Eran, embedded in the FlatMenu source code
#
#
# License: wxWidgets license
#
#
# Python Code By:
#
# Andrea Gavana, @ 03 Nov 2006
# Latest Revision: 03 Nov 2006, 22.30 GMT
#
#
# For All Kind Of Problems, Requests Of Enhancements And Bug Reports, Please
# Write To Me At:
#
# andrea.gavana@gmail.com
# gavana@kpo.kz
#
# Or, Obviously, To The wxPython Mailing List!!!
#
#
# End Of Comments
# --------------------------------------------------------------------------- #

"""
Description
===========

LabelBook and FlatImageBook are a quasi-full implementations of the wx.Notebook,
and designed to be a drop-in replacement for wx.Notebook. The API functions are
similar so one can expect the function to behave in the same way.
LabelBook anf FlatImageBook share their appearance with wx.Toolbook and
wx.Listbook, while having more options for custom drawings, label positioning,
mouse pointing and so on. Moreover, they retain also some visual characteristics
of the Outlook address book.

Some features:

  - They are generic controls;
  - Supports for left, right, top (FlatImageBook only), bottom (FlatImageBook
    only) book styles;
  - Possibility to draw images only, text only or both (FlatImageBook only);
  - Support for a "pin-button", that allows the user to shrink/expand the book
    tab area;
  - Shadows behind tabs (LabelBook only);
  - Gradient shading of the tab area (LabelBook only);
  - Web-like mouse pointing on tabs style (LabelBook only);
  - Many customizable colours (tab area, active tab text, tab borders, active
    tab, highlight) - LabelBook only.
  
And much more. See the demo for a quasi-complete review of all the functionalities
of LabelBook and FlatImageBook.


Events
======

LabelBook and FlatImageBook implement 4 events:

  - EVT_IMAGENOTEBOOK_PAGE_CHANGING;
  - EVT_IMAGENOTEBOOK_PAGE_CHANGED;
  - EVT_IMAGENOTEBOOK_PAGE_CLOSING;
  - EVT_IMAGENOTEBOOK_PAGE_CLOSED.


Supported Platforms
===================

LabelBook and FlatImageBook have been tested on the following platforms:
  * Windows (Windows XP);
  * Linux Ubuntu (Dapper 6.06)


License And Version:
===================

LabelBook and FlatImageBook are freeware and distributed under the wxPython license. 


Latest Revision: Andrea Gavana @ 03 Nov 2006, 22.30 GMT

Version 0.1.

"""

__docformat__ = "epytext"


#----------------------------------------------------------------------
# Beginning Of IMAGENOTEBOOK wxPython Code
#----------------------------------------------------------------------

import wx

from ArtManager import ArtManager, DCSaver
from Resources import *

# Check for the new method in 2.7 (not present in 2.6.3.3)
if wx.VERSION_STRING < "2.7":
    wx.Rect.Contains = lambda self, point: wx.Rect.Inside(self, point)

wxEVT_IMAGENOTEBOOK_PAGE_CHANGED = wx.NewEventType()
wxEVT_IMAGENOTEBOOK_PAGE_CHANGING = wx.NewEventType()
wxEVT_IMAGENOTEBOOK_PAGE_CLOSING = wx.NewEventType()
wxEVT_IMAGENOTEBOOK_PAGE_CLOSED = wx.NewEventType()

#-----------------------------------#
#        ImageNotebookEvent
#-----------------------------------#

EVT_IMAGENOTEBOOK_PAGE_CHANGED = wx.PyEventBinder(wxEVT_IMAGENOTEBOOK_PAGE_CHANGED, 1)
"""Notify client objects when the active page in L{ImageNotebook} 
has changed."""
EVT_IMAGENOTEBOOK_PAGE_CHANGING = wx.PyEventBinder(wxEVT_IMAGENOTEBOOK_PAGE_CHANGING, 1)
"""Notify client objects when the active page in L{ImageNotebook} 
is about to change."""
EVT_IMAGENOTEBOOK_PAGE_CLOSING = wx.PyEventBinder(wxEVT_IMAGENOTEBOOK_PAGE_CLOSING, 1)
"""Notify client objects when a page in L{ImageNotebook} is closing."""
EVT_IMAGENOTEBOOK_PAGE_CLOSED = wx.PyEventBinder(wxEVT_IMAGENOTEBOOK_PAGE_CLOSED, 1)
"""Notify client objects when a page in L{ImageNotebook} has been closed."""


# ---------------------------------------------------------------------------- #
# Class ImageNotebookEvent
# ---------------------------------------------------------------------------- #

class ImageNotebookEvent(wx.PyCommandEvent):
    """
    This events will be sent when a EVT_IMAGENOTEBOOK_PAGE_CHANGED,
    EVT_IMAGENOTEBOOK_PAGE_CHANGING, EVT_IMAGENOTEBOOK_PAGE_CLOSING,
    EVT_IMAGENOTEBOOK_PAGE_CLOSED is mapped in the parent.
    """

    def __init__(self, eventType, id=1, sel=-1, oldsel=-1):
        """ Default class constructor. """

        wx.PyCommandEvent.__init__(self, eventType, id)
        self._eventType = eventType
        self._sel = sel
        self._oldsel = oldsel
        self._allowed = True


    def SetSelection(self, s):
        """ Sets the event selection. """

        self._sel = s


    def SetOldSelection(self, s):
        """ Sets the event old selection. """

        self._oldsel = s


    def GetSelection(self):
        """ Returns the event selection. """

        return self._sel


    def GetOldSelection(self):
        """ Returns the old event selection. """

        return self._oldsel


    def Veto(self):
        """Vetos the event. """

        self._allowed = False


    def Allow(self):
        """Allows the event. """

        self._allowed = True


    def IsAllowed(self):
        """Returns whether the event is allowed or not. """

        return self._allowed


# ---------------------------------------------------------------------------- #
# Class ImageInfo
# ---------------------------------------------------------------------------- #

class ImageInfo:
    """
    This class holds all the information (caption, image, etc...) belonging to a
    single tab in L{ImageNotebook}.
    """
    def __init__(self, strCaption="", imageIndex=-1):    
        """
        Default Class Constructor.

        Parameters:
        @param strCaption: the tab caption;
        @param imageIndex: the tab image index based on the assigned (set) wx.ImageList (if any).
        """
        
        self._pos = wx.Point()
        self._size = wx.Size()
        self._strCaption = strCaption
        self._ImageIndex = imageIndex
        self._captionRect = wx.Rect()


    def SetCaption(self, value):
        """ Sets the tab caption. """

        self._strCaption = value


    def GetCaption(self):
        """ Returns the tab caption. """

        return self._strCaption


    def SetPosition(self, value):
        """ Sets the tab position. """

        self._pos = value


    def GetPosition(self):
        """ Returns the tab position. """

        return self._pos


    def SetSize(self, value):
        """ Sets the tab size. """

        self._size = value


    def GetSize(self):
        """ Returns the tab size. """

        return self._size


    def SetImageIndex(self, value):
        """ Sets the tab image index. """

        self._ImageIndex = value


    def GetImageIndex(self):
        """ Returns the tab image index. """

        return self._ImageIndex


    def SetTextRect(self, rect):
        """ Sets the rect available for the tab text. """

        self._captionRect = rect


    def GetTextRect(self):
        """ Returns the rect available for the tab text. """

        return self._captionRect


# ---------------------------------------------------------------------------- #
# Class ImageContainerBase
# ---------------------------------------------------------------------------- #

class ImageContainerBase(wx.Panel):
    """
    Base class for FlatImageBook image container.
    """
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, name="ImageContainerBase"):
        """
        Default class constructor.

        Parameters:
        @param parent - parent window
        @param id - Window id
        @param pos - Window position
        @param size - Window size
        @param style - possible style INB_XXX
        """

        self._nIndex = -1
        self._nImgSize = 16
        self._ImageList = None
        self._nHoeveredImgIdx = -1
        self._bCollapsed = False
        self._tabAreaSize = (-1, -1)
        self._nPinButtonStatus = INB_PIN_NONE
        self._pagesInfoVec = []
        self._pinBtnRect = wx.Rect()

        wx.Panel.__init__(self, parent, id, pos, size, style | wx.NO_BORDER | wx.NO_FULL_REPAINT_ON_RESIZE, name)


    def HasFlag(self, flag):
        """ Tests for existance of flag in the style. """
        
        style = self.GetParent().GetWindowStyleFlag()
        res = (style & flag and [True] or [False])[0]
        return res


    def ClearFlag(self, flag):
        """ Removes flag from the style. """
        
        style = self.GetParent().GetWindowStyleFlag()
        style &= ~(flag)
        wx.Panel.SetWindowStyleFlag(self, style)


    def AssignImageList(self, imglist):
        """ Assigns an image list to the ImageContainerBase. """
  
        if imglist and imglist.GetImageCount() != 0:
            self._nImgSize = imglist.GetBitmap(0).GetHeight()

        self._ImageList = imglist


    def GetImageList(self):
        """ Return the image list for ImageContainerBase. """

        return self._ImageList


    def GetImageSize(self):
        """ Returns the image size inside the ImageContainerBase image list. """

        return self._nImgSize

    
    def FixTextSize(self, dc, text, maxWidth):
        """
        Fixes the text, to fit maxWidth value. If the text length exceeds
        maxWidth value this function truncates it and appends two dots at
        the end. ("Long Long Long Text" might become "Long Long...)
        """

        return ArtManager.Get().TruncateText(dc, text, maxWidth)


    def CanDoBottomStyle(self):
        """
        Allows the parent to examine the children type. Some implementation
        (such as LabelBook), does not support top/bottom images, only left/right.
        """
        
        return False
    
        
    def AddPage(self, caption, selected=True, imgIdx=-1):
        """ Adds a page to the container. """
        
        self._pagesInfoVec.append(ImageInfo(caption, imgIdx))
        if selected or len(self._pagesInfoVec) == 1:
            self._nIndex = len(self._pagesInfoVec)-1

        self.Refresh()


    def ClearAll(self):
        """ Deletes all the pages in the container. """

        self._pagesInfoVec = []
        self._nIndex = wx.NOT_FOUND


    def DoDeletePage(self, page):
        """ Does the actual page deletion. """

        # Remove the page from the vector
        book = self.GetParent()
        self._pagesInfoVec.pop(page)

        if self._nIndex >= page:
            self._nIndex = self._nIndex - 1

        # The delete page was the last first on the array,
        # but the book still has more pages, so we set the
        # active page to be the first one (0)
        if self._nIndex < 0 and len(self._pagesInfoVec) > 0:
            self._nIndex = 0

        # Refresh the tabs
        if self._nIndex >= 0:
        
            book._bForceSelection = True
            book.SetSelection(self._nIndex)
            book._bForceSelection = False
        
        if not self._pagesInfoVec:        
            # Erase the page container drawings
            dc = wx.ClientDC(self)
            dc.Clear()

            
    def OnSize(self, event):
        """ Handles the wx.EVT_SIZE event for ImageContainerBase. """

        self.Refresh() # Call on paint
        event.Skip()


    def OnEraseBackground(self, event):
        """ Handles the wx.EVT_ERASE_BACKGROUND event for ImageContainerBase. """

        pass

    
    def HitTest(self, pt):
        """
        Returns the index of the tab at the specified position or wx.NOT_FOUND
        if None, plus the flag style of HitTest.
        """
        
        style = self.GetParent().GetWindowStyleFlag()
        
        if style & INB_USE_PIN_BUTTON:
            if self._pinBtnRect.Contains(pt):
                return -1, IMG_OVER_PIN        

        for i in xrange(len(self._pagesInfoVec)):
        
            if self._pagesInfoVec[i].GetPosition() == wx.Point(-1, -1):
                break
            
            # For Web Hover style, we test the TextRect
            if not self.HasFlag(INB_WEB_HILITE):
                buttonRect = wx.RectPS(self._pagesInfoVec[i].GetPosition(), self._pagesInfoVec[i].GetSize())
            else:
                buttonRect = self._pagesInfoVec[i].GetTextRect()
                
            if buttonRect.Contains(pt):
                return i, IMG_OVER_IMG
            
        if self.PointOnSash(pt):
            return -1, IMG_OVER_EW_BORDER
        else:
            return -1, IMG_NONE


    def PointOnSash(self, pt):
        """ Tests whether pt is located on the sash. """

        # Check if we are on a the sash border
        cltRect = self.GetClientRect()
        
        if self.HasFlag(INB_LEFT) or self.HasFlag(INB_TOP):
            if pt.x > cltRect.x + cltRect.width - 4:
                return True
        
        else:
            if pt.x < 4:
                return True
        
        return False


    def OnMouseLeftDown(self, event):
        """ Handles the wx.EVT_LEFT_DOWN event for ImageContainerBase. """

        newSelection = -1
        event.Skip()

        # Support for collapse/expand
        style = self.GetParent().GetWindowStyleFlag()
        if style & INB_USE_PIN_BUTTON:

            if self._pinBtnRect.Contains(event.GetPosition()):
            
                self._nPinButtonStatus = INB_PIN_PRESSED
                dc = wx.ClientDC(self)
                self.DrawPin(dc, self._pinBtnRect, not self._bCollapsed)
                return
            
        # Incase panel is collapsed, there is nothing 
        # to check 
        if self._bCollapsed:
            return

        tabIdx, where = self.HitTest(event.GetPosition())

        if where == IMG_OVER_IMG:
            self._nHoeveredImgIdx = -1        

        if tabIdx == -1:
            return
        
        self.GetParent().SetSelection(tabIdx)


    def OnMouseLeaveWindow(self, event):
        """ Handles the wx.EVT_LEAVE_WINDOW event for ImageContainerBase. """

        bRepaint = self._nHoeveredImgIdx != -1
        self._nHoeveredImgIdx = -1

        # Make sure the pin button status is NONE
        # incase we were in pin button style
        style = self.GetParent().GetWindowStyleFlag()
        
        if style & INB_USE_PIN_BUTTON:
        
            self._nPinButtonStatus = INB_PIN_NONE
            dc = wx.ClientDC(self)
            self.DrawPin(dc, self._pinBtnRect, not self._bCollapsed)
        
        # Restore cursor
        wx.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        
        if bRepaint:
            self.Refresh()


    def OnMouseLeftUp(self, event):
        """ Handles the wx.EVT_LEFT_UP event for ImageContainerBase. """

        style = self.GetParent().GetWindowStyleFlag()
        
        if style & INB_USE_PIN_BUTTON:
        
            bIsLabelContainer = not self.CanDoBottomStyle()
            
            if self._pinBtnRect.Contains(event.GetPosition()):
            
                self._nPinButtonStatus = INB_PIN_NONE
                self._bCollapsed = not self._bCollapsed

                if self._bCollapsed:
                
                    # Save the current tab area width
                    self._tabAreaSize = self.GetSize()
                    
                    if bIsLabelContainer:
                    
                        self.SetSizeHints(20, self._tabAreaSize.y)
                    
                    else:
                    
                        if style & INB_BOTTOM or style & INB_TOP:
                            self.SetSizeHints(self._tabAreaSize.x, 20)
                        else:
                            self.SetSizeHints(20, self._tabAreaSize.y)
                    
                else:
                
                    if bIsLabelContainer:
                    
                        self.SetSizeHints(self._tabAreaSize.x, -1)
                    
                    else:
                    
                        # Restore the tab area size
                        if style & INB_BOTTOM or style & INB_TOP:
                            self.SetSizeHints(-1, self._tabAreaSize.y)
                        else:
                            self.SetSizeHints(self._tabAreaSize.x, -1)
                    
                self.GetParent().GetSizer().Layout()
                self.Refresh()
                return
            

    def OnMouseMove(self, event):
        """ Handles the wx.EVT_MOTION event for ImageContainerBase. """

        style = self.GetParent().GetWindowStyleFlag()
        if style & INB_USE_PIN_BUTTON:
        
            # Check to see if we are in the pin button rect
            if not self._pinBtnRect.Contains(event.GetPosition()) and self._nPinButtonStatus == INB_PIN_PRESSED:
            
                self._nPinButtonStatus = INB_PIN_NONE
                dc = wx.ClientDC(self)
                self.DrawPin(dc, self._pinBtnRect, not self._bCollapsed)
            
        imgIdx, where = self.HitTest(event.GetPosition())
        self._nHoeveredImgIdx = imgIdx
        
        if not self._bCollapsed:
        
            if self._nHoeveredImgIdx >= 0 and self._nHoeveredImgIdx < len(self._pagesInfoVec):
            
                # Change the cursor to be Hand
                if self.HasFlag(INB_WEB_HILITE) and self._nHoeveredImgIdx != self._nIndex:
                    wx.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
            
            else:
            
                # Restore the cursor only if we have the Web hover style set,
                # and we are not currently hovering the sash
                if self.HasFlag(INB_WEB_HILITE) and not self.PointOnSash(event.GetPosition()):
                    wx.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            
        # Dont display hover effect when hoevering the 
        # selected label
        
        if self._nHoeveredImgIdx == self._nIndex:
            self._nHoeveredImgIdx = -1
        
        self.Refresh()


    def DrawPin(self, dc, rect, downPin):
        """ Draw a pin button, that allows collapsing of the image panel. """

        # Set the bitmap according to the button status

        if downPin:
            pinBmp = wx.BitmapFromXPMData(pin_down_xpm)
        else:
            pinBmp = wx.BitmapFromXPMData(pin_left_xpm)

        xx = rect.x + 2
        
        if self._nPinButtonStatus in [INB_PIN_HOVER, INB_PIN_NONE]:
            
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.SetPen(wx.BLACK_PEN)
            dc.DrawRectangle(xx, rect.y, 16, 16)

            # Draw upper and left border with grey color
            dc.SetPen(wx.WHITE_PEN)
            dc.DrawLine(xx, rect.y, xx + 16, rect.y)
            dc.DrawLine(xx, rect.y, xx, rect.y + 16)
            
        elif self._nPinButtonStatus == INB_PIN_PRESSED:
            
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.SetPen(wx.Pen(wx.NamedColor("LIGHT GREY")))
            dc.DrawRectangle(xx, rect.y, 16, 16)

            # Draw upper and left border with grey color
            dc.SetPen(wx.BLACK_PEN)
            dc.DrawLine(xx, rect.y, xx + 16, rect.y)
            dc.DrawLine(xx, rect.y, xx, rect.y + 16)
            
        # Set the masking
        pinBmp.SetMask(wx.Mask(pinBmp, wx.WHITE))

        # Draw the new bitmap
        dc.DrawBitmap(pinBmp, xx, rect.y, True)

        # Save the pin rect
        self._pinBtnRect = rect


# ---------------------------------------------------------------------------- #
# Class ImageContainer
# ---------------------------------------------------------------------------- #

class ImageContainer(ImageContainerBase):
    """
    Base class for FlatImageBook image container.
    """
    
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, name="ImageContainer"):
        """
        Default class constructor.

        Parameters:
        @param parent - parent window
        @param id - Window id
        @param pos - Window position
        @param size - Window size
        @param style - possible style INB_XXX
        """

        ImageContainerBase.__init__(self, parent, id, pos, size, style, name)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeaveWindow)


    def OnSize(self, event):
        """ Handles the wx.EVT_SIZE event for ImageContainer. """

        ImageContainerBase.OnSize(self, event)
        event.Skip()
        

    def OnMouseLeftDown(self, event):
        """ Handles the wx.EVT_LEFT_DOWN event for ImageContainer. """
        
        ImageContainerBase.OnMouseLeftDown(self, event)
        event.Skip()
            

    def OnMouseLeftUp(self, event):
        """ Handles the wx.EVT_LEFT_UP event for ImageContainer. """

        ImageContainerBase.OnMouseLeftUp(self, event)
        event.Skip()


    def OnEraseBackground(self, event):
        """ Handles the wx.EVT_ERASE_BACKGROUND event for ImageContainer. """

        ImageContainerBase.OnEraseBackground(self, event)


    def OnMouseMove(self, event):
        """ Handles the wx.EVT_MOTION event for ImageContainer. """

        ImageContainerBase.OnMouseMove(self, event)
        event.Skip()


    def OnMouseLeaveWindow(self, event):
        """ Handles the wx.EVT_LEAVE_WINDOW event for ImageContainer. """

        ImageContainerBase.OnMouseLeaveWindow(self, event)
        event.Skip()

        
    def CanDoBottomStyle(self):
        """
        Allows the parent to examine the children type. Some implementation
        (such as LabelBook), does not support top/bottom images, only left/right.
        """

        return True


    def OnPaint(self, event):
        """ Handles the wx.EVT_PAINT event for ImageContainer. """

        dc = wx.BufferedPaintDC(self)
        style = self.GetParent().GetWindowStyleFlag()

        backBrush = wx.WHITE_BRUSH
        if style & INB_BORDER:
            borderPen = wx.Pen(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DSHADOW))
        else:
            borderPen = wx.TRANSPARENT_PEN

        size = self.GetSize()

        # Background
        dc.SetBrush(backBrush)

        borderPen.SetWidth(1)
        dc.SetPen(borderPen)
        dc.DrawRectangle(0, 0, size.x, size.y)
        bUsePin = (style & INB_USE_PIN_BUTTON and [True] or [False])[0]

        if bUsePin:

            # Draw the pin button
            clientRect = self.GetClientRect()
            pinRect = wx.Rect(clientRect.GetX() + clientRect.GetWidth() - 20, 2, 20, 20)
            self.DrawPin(dc, pinRect, not self._bCollapsed)

            if self._bCollapsed:
                return

        borderPen = wx.BLACK_PEN
        borderPen.SetWidth(1)
        dc.SetPen(borderPen)
        dc.DrawLine(0, size.y, size.x, size.y)
        dc.DrawPoint(0, size.y)

        clientSize = 0
        bUseYcoord = (style & INB_RIGHT or style & INB_LEFT)

        if bUseYcoord:
            clientSize = size.GetHeight()
        else:
            clientSize = size.GetWidth()

        # We reserver 20 pixels for the 'pin' button
        
        # The drawing of the images start position. This is 
        # depenedent of the style, especially when Pin button
        # style is requested

        if bUsePin:
            if style & INB_TOP or style & INB_BOTTOM:
                pos = (style & INB_BORDER and [0] or [1])[0]
            else:
                pos = (style & INB_BORDER and [20] or [21])[0]
        else:
            pos = (style & INB_BORDER and [0] or [1])[0]

        nPadding = 4    # Pad text with 2 pixels on the left and right
        nTextPaddingLeft = 2

        count = 0
        
        for i in xrange(len(self._pagesInfoVec)):

            count = count + 1            
        
            # incase the 'fit button' style is applied, we set the rectangle width to the
            # text width plus padding
            # Incase the style IS applied, but the style is either LEFT or RIGHT
            # we ignore it
            normalFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
            dc.SetFont(normalFont)

            textWidth, textHeight = dc.GetTextExtent(self._pagesInfoVec[i].GetCaption())

            # Restore font to be normal
            normalFont.SetWeight(wx.FONTWEIGHT_NORMAL)
            dc.SetFont(normalFont)

            # Default values for the surronounding rectangle 
            # around a button
            rectWidth = self._nImgSize * 2  # To avoid the recangle to 'touch' the borders
            rectHeight = self._nImgSize * 2

            # Incase the style requires non-fixed button (fit to text)
            # recalc the rectangle width
            if style & INB_FIT_BUTTON and \
               not ((style & INB_LEFT) or (style & INB_RIGHT)) and \
               not self._pagesInfoVec[i].GetCaption() == "" and \
               not (style & INB_SHOW_ONLY_IMAGES):
            
                rectWidth = ((textWidth + nPadding * 2) > rectWidth and [nPadding * 2 + textWidth] or [rectWidth])[0]

                # Make the width an even number
                if rectWidth % 2 != 0:
                    rectWidth += 1

            # Check that we have enough space to draw the button
            # If Pin button is used, consider its space as well (applicable for top/botton style)
            # since in the left/right, its size is already considered in 'pos'
            pinBtnSize = (bUsePin and [20] or [0])[0]
            
            if pos + rectWidth + pinBtnSize > clientSize:
                break

            # Calculate the button rectangle
            modRectWidth = ((style & INB_LEFT or style & INB_RIGHT) and [rectWidth - 2] or [rectWidth])[0]
            modRectHeight = ((style & INB_LEFT or style & INB_RIGHT) and [rectHeight] or [rectHeight - 2])[0]

            if bUseYcoord:
                buttonRect = wx.Rect(1, pos, modRectWidth, modRectHeight)
            else:
                buttonRect = wx.Rect(pos , 1, modRectWidth, modRectHeight)

            # Check if we need to draw a rectangle around the button
            if self._nIndex == i:
            
                # Set the colors
                penColor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_ACTIVECAPTION)
                brushColor = ArtManager.Get().LightColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_ACTIVECAPTION), 75)

                dc.SetPen(wx.Pen(penColor))
                dc.SetBrush(wx.Brush(brushColor))

                # Fix the surrounding of the rect if border is set
                if style & INB_BORDER:
                
                    if style & INB_TOP or style & INB_BOTTOM:
                        buttonRect = wx.Rect(buttonRect.x + 1, buttonRect.y, buttonRect.width - 1, buttonRect.height)
                    else:
                        buttonRect = wx.Rect(buttonRect.x, buttonRect.y + 1, buttonRect.width, buttonRect.height - 1)
                
                dc.DrawRectangleRect(buttonRect)
            
            if self._nHoeveredImgIdx == i:
            
                # Set the colors
                penColor = wx.SystemSettings_GetColour(wx.SYS_COLOUR_ACTIVECAPTION)
                brushColor = ArtManager.Get().LightColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_ACTIVECAPTION), 90)

                dc.SetPen(wx.Pen(penColor))
                dc.SetBrush(wx.Brush(brushColor))

                # Fix the surrounding of the rect if border is set
                if style & INB_BORDER:
                
                    if style & INB_TOP or style & INB_BOTTOM:
                        buttonRect = wx.Rect(buttonRect.x + 1, buttonRect.y, buttonRect.width - 1, buttonRect.height)
                    else:
                        buttonRect = wx.Rect(buttonRect.x, buttonRect.y + 1, buttonRect.width, buttonRect.height - 1)
                
                dc.DrawRectangleRect(buttonRect)
            
            if bUseYcoord:
                rect = wx.Rect(0, pos, rectWidth, rectWidth)
            else:
                rect = wx.Rect(pos, 0, rectWidth, rectWidth)

            # Incase user set both flags:
            # INB_SHOW_ONLY_TEXT and INB_SHOW_ONLY_IMAGES
            # We override them to display both

            if style & INB_SHOW_ONLY_TEXT and style & INB_SHOW_ONLY_IMAGES:
            
                style ^= INB_SHOW_ONLY_TEXT
                style ^= INB_SHOW_ONLY_IMAGES
                wx.Panel.SetWindowStyleFlag(self, style)
            
            # Draw the caption and text
            imgTopPadding = 10
            if not style & INB_SHOW_ONLY_TEXT and self._pagesInfoVec[i].GetImageIndex() != -1:
            
                if bUseYcoord:
                
                    imgXcoord = self._nImgSize / 2
                    imgYcoord = (style & INB_SHOW_ONLY_IMAGES and [pos + self._nImgSize / 2] or [pos + imgTopPadding])[0]
                
                else:
                
                    imgXcoord = pos + (rectWidth / 2) - (self._nImgSize / 2)
                    imgYcoord = (style & INB_SHOW_ONLY_IMAGES and [self._nImgSize / 2] or [imgTopPadding])[0]

                self._ImageList.Draw(self._pagesInfoVec[i].GetImageIndex(), dc,
                                     imgXcoord, imgYcoord,
                                     wx.IMAGELIST_DRAW_TRANSPARENT, True)
                            
            # Draw the text
            if not style & INB_SHOW_ONLY_IMAGES and not self._pagesInfoVec[i].GetCaption() == "":
            
                dc.SetFont(normalFont)
                            
                # Check if the text can fit the size of the rectangle,
                # if not truncate it 
                fixedText = self._pagesInfoVec[i].GetCaption()
                if not style & INB_FIT_BUTTON or (style & INB_LEFT or (style & INB_RIGHT)):
                
                    fixedText = self.FixTextSize(dc, self._pagesInfoVec[i].GetCaption(), self._nImgSize *2 - 4)

                    # Update the length of the text
                    textWidth, textHeight = dc.GetTextExtent(fixedText)
                
                if bUseYcoord:
                
                    textOffsetX = ((rectWidth - textWidth) / 2 )
                    textOffsetY = (not style & INB_SHOW_ONLY_TEXT  and [pos + self._nImgSize  + imgTopPadding + 3] or \
                                       [pos + ((self._nImgSize * 2 - textHeight) / 2 )])[0]
                
                else:
                
                    textOffsetX = (rectWidth - textWidth) / 2  + pos + nTextPaddingLeft
                    textOffsetY = (not style & INB_SHOW_ONLY_TEXT and [self._nImgSize + imgTopPadding + 3] or \
                                       [((self._nImgSize * 2 - textHeight) / 2 )])[0]
                
                dc.SetTextForeground(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOWTEXT))
                dc.DrawText(fixedText, textOffsetX, textOffsetY)
            
            # Update the page info
            self._pagesInfoVec[i].SetPosition(buttonRect.GetPosition())
            self._pagesInfoVec[i].SetSize(buttonRect.GetSize())

            pos += rectWidth
        
        # Update all buttons that can not fit into the screen as non-visible
        for ii in xrange(count, len(self._pagesInfoVec)):
            self._pagesInfoVec[ii].SetPosition(wx.Point(-1, -1))

        # Draw the pin button
        if bUsePin:
        
            clientRect = self.GetClientRect()
            pinRect = wx.Rect(clientRect.GetX() + clientRect.GetWidth() - 20, 2, 20, 20)
            self.DrawPin(dc, pinRect, not self._bCollapsed)
        

# ---------------------------------------------------------------------------- #
# Class LabelContainer
# ---------------------------------------------------------------------------- #

class LabelContainer(ImageContainerBase):
    """ Base class for LabelBook. """
    
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, name="LabelContainer"):
        """
        Default class constructor.

        Parameters:
        @param parent - parent window
        @param id - Window id
        @param pos - Window position
        @param size - Window size
        @param style - possible style INB_XXX
        """

        ImageContainerBase.__init__(self, parent, id, pos, size, style, name)
        self._nTabAreaWidth = 100
        self._oldCursor = wx.NullCursor
        self._colorsMap = {}
        self._skin = wx.NullBitmap
        self._sashRect = wx.Rect()

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMove)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeaveWindow)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)


    def OnSize(self, event):
        """ Handles the wx.EVT_SIZE event for LabelContainer. """

        ImageContainerBase.OnSize(self, event)
        event.Skip()


    def OnEraseBackground(self, event):
        """ Handles the wx.EVT_ERASE_BACKGROUND event for LabelContainer. """

        ImageContainerBase.OnEraseBackground(self, event)        

        
    def GetTabAreaWidth(self):
        """ Returns the width of the tab area. """

        return self._nTabAreaWidth


    def SetTabAreaWidth(self, width):
        """ Sets the width of the tab area. """

        self._nTabAreaWidth = width


    def CanDoBottomStyle(self):
        """
        Allows the parent to examine the children type. Some implementation
        (such as LabelBook), does not support top/bottom images, only left/right.
        """

        return False        


    def SetBackgroundBitmap(self, bmp):
        """ Sets the background bitmap for the control"""

        self._skin = bmp


    def OnPaint(self, event):
        """ Handles the wx.EVT_PAINT event for LabelContainer. """

        dc = wx.BufferedPaintDC(self)
        backBrush = wx.Brush(self._colorsMap[INB_TAB_AREA_BACKGROUND_COLOR])
        if self.HasFlag(INB_BORDER):
            borderPen = wx.Pen(self._colorsMap[INB_TABS_BORDER_COLOR])
        else:
            borderPen = wx.TRANSPARENT_PEN
            
        size = self.GetSize()
        
        # Set the pen & brush
        dc.SetBrush(backBrush)
        dc.SetPen(borderPen)

        if self.HasFlag(INB_GRADIENT_BACKGROUND) and not self._skin.Ok():
        
            # Draw graident in the background area
            startColor = self._colorsMap[INB_TAB_AREA_BACKGROUND_COLOR]
            endColor   = ArtManager.Get().LightColour(self._colorsMap[INB_TAB_AREA_BACKGROUND_COLOR], 50)
            ArtManager.Get().PaintStraightGradientBox(dc, wx.Rect(0, 0, size.x / 2, size.y), startColor, endColor, False)
            ArtManager.Get().PaintStraightGradientBox(dc, wx.Rect(size.x / 2, 0, size.x / 2, size.y), endColor, startColor, False)
        
        else:
        
            # Draw the border and background
            if self._skin.Ok():
            
                dc.SetBrush(wx.TRANSPARENT_BRUSH)
                self.DrawBackgroundBitmap(dc)
            
            dc.DrawRectangleRect(wx.Rect(0, 0, size.x, size.y))
        
        # Draw border
        if self.HasFlag(INB_BORDER) and self.HasFlag(INB_GRADIENT_BACKGROUND):
        
            # Just draw the border with transparent brush
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRectangleRect(wx.Rect(0, 0, size.x, size.y))

        bUsePin = (self.HasFlag(INB_USE_PIN_BUTTON) and [True] or [False])[0]

        if bUsePin:
        
            # Draw the pin button
            clientRect = self.GetClientRect()
            pinRect = wx.Rect(clientRect.GetX() + clientRect.GetWidth() - 20, 2, 20, 20)
            self.DrawPin(dc, pinRect, not self._bCollapsed)

            if self._bCollapsed:
                return
        
        dc.SetPen(wx.BLACK_PEN)
        self.SetSizeHints(self._nTabAreaWidth, -1)

        # We reserve 20 pixels for the pin button
        posy = 20 
        count = 0
        
        for i in xrange(len(self._pagesInfoVec)):
            count = count+1        
            # Default values for the surronounding rectangle 
            # around a button
            rectWidth = self._nTabAreaWidth  
            rectHeight = self._nImgSize * 2

            # Check that we have enough space to draw the button
            if posy + rectHeight > size.GetHeight():
                break

            # Calculate the button rectangle
            posx = 0

            buttonRect = wx.Rect(posx, posy, rectWidth, rectHeight)
            indx = self._pagesInfoVec[i].GetImageIndex()

            if indx == -1:
                bmp = wx.NullBitmap
            else:
                bmp = self._ImageList.GetBitmap(indx)

            self.DrawLabel(dc, buttonRect, self._pagesInfoVec[i].GetCaption(), bmp,
                           self._pagesInfoVec[i], self.HasFlag(INB_LEFT) or self.HasFlag(INB_TOP),
                           i, self._nIndex == i, self._nHoeveredImgIdx == i)

            posy += rectHeight
        
        # Update all buttons that can not fit into the screen as non-visible
        for ii in xrange(count, len(self._pagesInfoVec)):
            self._pagesInfoVec[i].SetPosition(wx.Point(-1, -1))

        if bUsePin:
        
            clientRect = self.GetClientRect()
            pinRect = wx.Rect(clientRect.GetX() + clientRect.GetWidth() - 20, 2, 20, 20)
            self.DrawPin(dc, pinRect, not self._bCollapsed)
        

    def DrawBackgroundBitmap(self, dc):
        """ Draws a bitmap as the background of the control. """

        clientRect = self.GetClientRect()
        width = clientRect.GetWidth()
        height = clientRect.GetHeight()
        coveredY = coveredX = 0
        xstep = self._skin.GetWidth()
        ystep = self._skin.GetHeight()
        bmpRect = wx.Rect(0, 0, xstep, ystep)
        if bmpRect != clientRect:
        
            mem_dc = wx.MemoryDC()
            bmp = wx.EmptyBitmap(width, height)
            mem_dc.SelectObject(bmp)

            while coveredY < height:
            
                while coveredX < width:
                
                    mem_dc.DrawBitmap(self._skin, coveredX, coveredY, True)
                    coveredX += xstep
                
                coveredX = 0
                coveredY += ystep
            
            mem_dc.SelectObject(wx.NullBitmap)
            #self._skin = bmp
            dc.DrawBitmap(bmp, 0, 0)
        
        else:
        
            dc.DrawBitmap(self._skin, 0, 0)
        

    def OnMouseLeftUp(self, event):
        """ Handles the wx.EVT_LEFT_UP event for LabelContainer. """

        if self.HasFlag(INB_NO_RESIZE):
        
            ImageContainerBase.OnMouseLeftUp(self, event)
            return
        
        if self.HasCapture():
            self.ReleaseMouse()

        # Sash was being dragged?
        if not self._sashRect.IsEmpty():
        
            # Remove sash
            ArtManager.Get().DrawDragSash(self._sashRect)
            self.Resize(event)

            self._sashRect = wx.Rect()
            return
        
        self._sashRect = wx.Rect()

        # Restore cursor
        if self._oldCursor.Ok():
        
            wx.SetCursor(self._oldCursor)
            self._oldCursor = wx.NullCursor
        
        ImageContainerBase.OnMouseLeftUp(self, event)


    def Resize(self, event):
        """ Actually resizes the tab area. """

        # Resize our size
        self._tabAreaSize = self.GetSize()
        newWidth = self._tabAreaSize.x
        x = event.GetX()

        if self.HasFlag(INB_BOTTOM) or self.HasFlag(INB_RIGHT):
        
            newWidth -= event.GetX()
        
        else:
        
            newWidth = x
        
        if newWidth < 100: # Dont allow width to be lower than that 
            newWidth = 100

        self.SetSizeHints(newWidth, self._tabAreaSize.y)

        # Update the tab new area width
        self._nTabAreaWidth = newWidth
        self.GetParent().Freeze()
        self.GetParent().GetSizer().Layout()
        self.GetParent().Thaw()


    def OnMouseMove(self, event):
        """ Handles the wx.EVT_MOTION event for LabelContainer. """

        if self.HasFlag(INB_NO_RESIZE):
        
            ImageContainerBase.OnMouseMove(self, event)
            return

        # Remove old sash
        if not self._sashRect.IsEmpty():
            ArtManager.Get().DrawDragSash(self._sashRect)

        if event.LeftIsDown():
        
            if not self._sashRect.IsEmpty():
            
                # Progress sash, and redraw it
                clientRect = self.GetClientRect()
                pt = self.ClientToScreen(wx.Point(event.GetX(), 0))
                self._sashRect = wx.RectPS(pt, wx.Size(4, clientRect.height))
                ArtManager.Get().DrawDragSash(self._sashRect)
            
            else:
            
                # Sash is not being dragged
                if self._oldCursor.Ok():
                    wx.SetCursor(self._oldCursor)
                    self._oldCursor = wx.NullCursor
                
        else:
        
            if self.HasCapture():
                self.ReleaseMouse()

            if self.PointOnSash(event.GetPosition()):
            
                # Change cursor to EW cursor
                self._oldCursor = self.GetCursor()
                wx.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))
            
            elif self._oldCursor.Ok():
            
                wx.SetCursor(self._oldCursor)
                self._oldCursor = wx.NullCursor
            
            self._sashRect = wx.Rect()
            ImageContainerBase.OnMouseMove(self, event)
        

    def OnMouseLeftDown(self, event):
        """ Handles the wx.EVT_LEFT_DOWN event for LabelContainer. """

        if self.HasFlag(INB_NO_RESIZE):
        
            ImageContainerBase.OnMouseLeftDown(self, event)
            return

        imgIdx, where = self.HitTest(event.GetPosition())

        if IMG_OVER_EW_BORDER == where and not self._bCollapsed:
            
            # We are over the sash
            if not self._sashRect.IsEmpty():
                ArtManager.Get().DrawDragSash(self._sashRect)
            else:
                # first time, begin drawing sash
                self.CaptureMouse()

                # Change mouse cursor
                self._oldCursor = self.GetCursor()
                wx.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))
            
            clientRect = self.GetClientRect()
            pt = self.ClientToScreen(wx.Point(event.GetX(), 0))
            self._sashRect = wx.RectPS(pt, wx.Size(4, clientRect.height))

            ArtManager.Get().DrawDragSash(self._sashRect)
        
        else:
            ImageContainerBase.OnMouseLeftDown(self, event)


    def OnMouseLeaveWindow(self, event):
        """ Handles the wx.EVT_LEAVE_WINDOW event for LabelContainer. """

        if self.HasFlag(INB_NO_RESIZE):
        
            ImageContainerBase.OnMouseLeaveWindow(self, event)
            return
        
        # If Sash is being dragged, ignore this event
        if not self.HasCapture():        
            ImageContainerBase.OnMouseLeaveWindow(self, event)      

        
    def DrawRegularHover(self, dc, rect):
        """ Draws a rounded rectangle around the current tab. """
        
        # The hovered tab with default border
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.SetPen(wx.Pen(wx.WHITE))

        # We draw CCW
        if self.HasFlag(INB_RIGHT) or self.HasFlag(INB_TOP):
        
            # Right images
            # Upper line
            dc.DrawLine(rect.x + 1, rect.y, rect.x + rect.width, rect.y)

            # Right line (white)
            dc.DrawLine(rect.x + rect.width, rect.y, rect.x + rect.width, rect.y + rect.height)

            # Bottom diagnol - we change pen
            dc.SetPen(wx.Pen(self._colorsMap[INB_TABS_BORDER_COLOR]))

            # Bottom line
            dc.DrawLine(rect.x + rect.width, rect.y + rect.height, rect.x, rect.y + rect.height)
        
        else:
        
            # Left images
            # Upper line white
            dc.DrawLine(rect.x, rect.y, rect.x + rect.width - 1, rect.y)

            # Left line
            dc.DrawLine(rect.x, rect.y, rect.x, rect.y + rect.height)

            # Bottom diagnol, we change the pen
            dc.SetPen(wx.Pen(self._colorsMap[INB_TABS_BORDER_COLOR]))

            # Bottom line
            dc.DrawLine(rect.x, rect.y + rect.height, rect.x + rect.width, rect.y + rect.height)
        

    def DrawWebHover(self, dc, caption, xCoord, yCoord):
        """ Draws a web style hover effect (cursor set to hand & text is underlined). """

        # Redraw the text with underlined font
        underLinedFont = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
        underLinedFont.SetUnderlined(True)
        dc.SetFont(underLinedFont)
        dc.DrawText(caption, xCoord, yCoord)


    def SetColour(self, which, color):
        """ Sets a colour for a parameter. """

        self._colorsMap[which] = color


    def GetColour(self, which):
        """ Returns a colour for a parameter. """

        if not self._colorsMap.has_key(which):
            return wx.Colour()

        return self._colorsMap[which]        


    def InitializeColors(self):
        """ Initializes the colors map to be used for this control. """

        # Initialize map colors
        self._colorsMap.update({INB_TAB_AREA_BACKGROUND_COLOR: ArtManager.Get().LightColour(ArtManager.Get().FrameColour(), 50)})
        self._colorsMap.update({INB_ACTIVE_TAB_COLOR: ArtManager.Get().GetMenuFaceColour()})
        self._colorsMap.update({INB_TABS_BORDER_COLOR: wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DSHADOW)})
        self._colorsMap.update({INB_HILITE_TAB_COLOR: wx.NamedColor("LIGHT BLUE")})
        self._colorsMap.update({INB_TEXT_COLOR: wx.WHITE})
        self._colorsMap.update({INB_ACTIVE_TEXT_COLOR: wx.BLACK})

        # dont allow bright colour one on the other
        if not ArtManager.Get().IsDark(self._colorsMap[INB_TAB_AREA_BACKGROUND_COLOR]) and \
           not ArtManager.Get().IsDark(self._colorsMap[INB_TEXT_COLOR]):
        
            self._colorsMap[INB_TEXT_COLOR] = ArtManager.Get().DarkColour(self._colorsMap[INB_TEXT_COLOR], 100)
        

    def DrawLabel(self, dc, rect, text, bmp, imgInfo, orientationLeft, imgIdx, selected, hover):
        """ Draws label using the specified dc. """

        dcsaver = DCSaver(dc)
        nPadding = 6
        
        if orientationLeft:
        
            rect.x += nPadding
            rect.width -= nPadding
        
        else:
        
            rect.width -= nPadding
        
        textRect = wx.Rect(*rect)
        imgRect = wx.Rect(*rect)
        
        dc.SetFont(wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT))

        # First we define the rectangle for the text
        w, h = dc.GetTextExtent(text)
        
        #-------------------------------------------------------------------------
        # Label layout:
        # [ nPadding | Image | nPadding | Text | nPadding ]
        #-------------------------------------------------------------------------

        # Text bounding rectangle
        textRect.x += nPadding
        textRect.y = rect.y + (rect.height - h)/2
        textRect.width = rect.width - 2 * nPadding

        if bmp.Ok():
            textRect.x += (bmp.GetWidth() + nPadding)
            textRect.width -= (bmp.GetWidth() + nPadding)
        
        textRect.height = h

        # Truncate text if needed
        caption = ArtManager.Get().TruncateText(dc, text, textRect.width)

        # Image bounding rectangle
        if bmp.Ok():
        
            imgRect.x += nPadding
            imgRect.width = bmp.GetWidth()
            imgRect.y = rect.y + (rect.height - bmp.GetHeight())/2
            imgRect.height = bmp.GetHeight()
        
        # Draw bounding rectangle
        if selected:
        
            # First we colour the tab
            dc.SetBrush(wx.Brush(self._colorsMap[INB_ACTIVE_TAB_COLOR]))

            if self.HasFlag(INB_BORDER):
                dc.SetPen(wx.Pen(self._colorsMap[INB_TABS_BORDER_COLOR]))
            else: 
                dc.SetPen(wx.Pen(self._colorsMap[INB_ACTIVE_TAB_COLOR]))
            
            labelRect = wx.Rect(*rect)

            if orientationLeft: 
                labelRect.width += 3
            else: 
                labelRect.width += 3
                labelRect.x -= 3
            
            dc.DrawRoundedRectangleRect(labelRect, 3)

            if not orientationLeft and self.HasFlag(INB_DRAW_SHADOW):
                dc.SetPen(wx.BLACK_PEN)
                dc.DrawPoint(labelRect.x + labelRect.width - 1, labelRect.y + labelRect.height - 1)
            
        # Draw the text & bitmap
        if caption != "":
        
            if selected:
                dc.SetTextForeground(self._colorsMap[INB_ACTIVE_TEXT_COLOR])
            else:
                dc.SetTextForeground(self._colorsMap[INB_TEXT_COLOR])
                
            dc.DrawText(caption, textRect.x, textRect.y)
            imgInfo.SetTextRect(textRect)
        
        else:
        
            imgInfo.SetTextRect(wx.Rect())
        
        if bmp.Ok():
            dc.DrawBitmap(bmp, imgRect.x, imgRect.y, True)

        # Drop shadow
        if self.HasFlag(INB_DRAW_SHADOW) and selected:
        
            sstyle = 0
            if orientationLeft:
                sstyle = BottomShadow
            else:
                sstyle = BottomShadowFull | RightShadow
            
            if self.HasFlag(INB_WEB_HILITE):
            
                # Always drop shadow for this style
                ArtManager.Get().DrawBitmapShadow(dc, rect, sstyle)
            
            else:
            
                if imgIdx+1 != self._nHoeveredImgIdx:
                
                    ArtManager.Get().DrawBitmapShadow(dc, rect, sstyle)
                
        # Draw hover effect 
        if hover:
        
            if self.HasFlag(INB_WEB_HILITE) and caption != "":   
                self.DrawWebHover(dc, caption, textRect.x, textRect.y)
            else:
                self.DrawRegularHover(dc, rect)
        
        # Update the page information bout position and size
        imgInfo.SetPosition(rect.GetPosition())
        imgInfo.SetSize(rect.GetSize())


# ---------------------------------------------------------------------------- #
# Class FlatBookBase
# ---------------------------------------------------------------------------- #

class FlatBookBase(wx.Panel):
    """ Base class for the containing window for LabelBook and FlatImageBook. """

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, name="FlatBookBase"):
        """
        Default class constructor.

        Parameters:
        @param parent - parent window
        @param id - Window id
        @param pos - Window position
        @param size - Window size
        @param style - possible style INB_XXX
        """
        
        self._pages = None
        self._bInitializing = True
        self._pages = None
        self._bForceSelection = False
        self._windows = []

        style |= wx.TAB_TRAVERSAL
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        self._bInitializing = False


    def SetWindowStyleFlag(self, style):
        """ Sets the window style. """

        wx.Panel.SetWindowStyleFlag(self, style)
        
        # Check that we are not in initialization process
        if self._bInitializing:
            return

        if not self._pages:
            return

        # Detach the windows attached to the sizer
        if self.GetSelection() >= 0:
            self._mainSizer.Detach(self._windows[self.GetSelection()])

        self._mainSizer.Detach(self._pages)
        
        # Create new sizer with the requested orientaion
        className = self.GetName()

        if className == "LabelBook":
            self._mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        else:
            if style & INB_LEFT or style & INB_RIGHT:
                self._mainSizer = wx.BoxSizer(wx.HORIZONTAL)
            else:
                self._mainSizer = wx.BoxSizer(wx.VERTICAL)
        
        self.SetSizer(self._mainSizer)
        
        # Add the tab container and the separator
        self._mainSizer.Add(self._pages, 0, wx.EXPAND)
        
        if className == "FlatImageBook":
        
            if style & INB_LEFT or style & INB_RIGHT:
                self._pages.SetSizeHints(self._pages._nImgSize * 2, -1)
            else:
                self._pages.SetSizeHints(-1, self._pages._nImgSize * 2)
        
        # Attach the windows back to the sizer to the sizer
        if self.GetSelection() >= 0:
            self.DoSetSelection(self._windows[self.GetSelection()])

        self._mainSizer.Layout()
        dummy = wx.SizeEvent()
        wx.PostEvent(self, dummy)
        self._pages.Refresh()


    def AddPage(self, page, text, select=True, imageId=-1):
        """
        Adds a page to the book.
        The call to this function generates the page changing events
        """

        if not page:
            return

        page.Reparent(self)

        self._windows.append(page)
        
        if select or len(self._windows) == 1:
            self.DoSetSelection(page)
        else:
            page.Hide()

        self._pages.AddPage(text, select, imageId)            
        self.Refresh()


    def DeletePage(self, page):
        """
        Deletes the specified page, and the associated window.
        The call to this function generates the page changing events.
        """

        if page >= len(self._windows) or page < 0:
            return

        # Fire a closing event
        event = ImageNotebookEvent(wxEVT_IMAGENOTEBOOK_PAGE_CLOSING, self.GetId())
        event.SetSelection(page)
        event.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(event)

        # The event handler allows it?
        if not event.IsAllowed():
            return

        self.Freeze()

        # Delete the requested page
        pageRemoved = self._windows[page]

        # If the page is the current window, remove it from the sizer
        # as well
        if page == self.GetSelection():
            self._mainSizer.Detach(pageRemoved)
        
        # Remove it from the array as well
        self._windows.pop(page)

        # Now we can destroy it in wxWidgets use Destroy instead of delete
        pageRemoved.Destroy()
        self._mainSizer.Layout()
        
        self.Thaw()

        self._pages.DoDeletePage(page)
        self.Refresh()

        # Fire a closed event
        closedEvent = ImageNotebookEvent(wxEVT_IMAGENOTEBOOK_PAGE_CLOSED, self.GetId())
        closedEvent.SetSelection(page)
        closedEvent.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(closedEvent)

        
    def DeleteAllPages(self):
        """ Deletes all the pages in the book. """

        if not self._windows:
            return

        self.Freeze()
        
        for win in self._windows:
            win.Destroy()
        
        self._windows = []
        self.Thaw()

        # remove old selection
        self._pages.ClearAll()
        self._pages.Refresh()


    def SetSelection(self, page):
        """
        Changes the selection from currently visible/selected page to the page
        given by page.
        """

        if page >= len(self._windows):
            return

        if page == self.GetSelection() and not self._bForceSelection:
            return

        oldSelection = self.GetSelection()

        # Generate an event that indicates that an image is about to be selected
        event = ImageNotebookEvent(wxEVT_IMAGENOTEBOOK_PAGE_CHANGING, self.GetId())
        event.SetSelection(page)
        event.SetOldSelection(oldSelection)
        event.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(event)

        # The event handler allows it?
        if not event.IsAllowed() and not self._bForceSelection:
            return

        self.DoSetSelection(self._windows[page])
        # Now we can update the new selection
        self._pages._nIndex = page

        # Refresh calls the OnPaint of this class
        self._pages.Refresh()

        # Generate an event that indicates that an image was selected
        eventChanged = ImageNotebookEvent(wxEVT_IMAGENOTEBOOK_PAGE_CHANGED, self.GetId())
        eventChanged.SetEventObject(self)
        eventChanged.SetOldSelection(oldSelection)
        eventChanged.SetSelection(page)
        self.GetEventHandler().ProcessEvent(eventChanged)


    def AssignImageList(self, imglist):
        """ Assigns an image list to the control. """

        self._pages.AssignImageList(imglist)

        # Force change
        self.SetWindowStyleFlag(self.GetWindowStyleFlag())


    def GetSelection(self):
        """ Returns the current selection. """

        if self._pages:
            return self._pages._nIndex
        else:
            return -1


    def DoSetSelection(self, window):
        """ Select the window by the provided pointer. """

        curSel = self.GetSelection()
        style = self.GetWindowStyleFlag()
        # Replace the window in the sizer
        self.Freeze()

        # Check if a new selection was made
        bInsertFirst = (style & INB_BOTTOM or style & INB_RIGHT)

        if curSel >= 0:
        
            # Remove the window from the main sizer
            self._mainSizer.Detach(self._windows[curSel])
            self._windows[curSel].Hide()
        
        if bInsertFirst:
            self._mainSizer.Insert(0, window, 1, wx.EXPAND)
        else:
            self._mainSizer.Add(window, 1, wx.EXPAND)

        window.Show()
        self._mainSizer.Layout()
        self.Thaw()


    def GetImageList(self):
        """ Returns the associated image list. """

        return self._pages.GetImageList()


    def GetPageCount(self):
        """ Returns the number of pages in the book. """

        return len(self._windows)
    

# ---------------------------------------------------------------------------- #
# Class FlatImageBook
# ---------------------------------------------------------------------------- #
        
class FlatImageBook(FlatBookBase):
    """
    Default implementation of the image book, it is like a wx.Notebook, except that
    images are used to control the different pages. This container is usually used
    for configuration dialogs etc.
    Currently, this control works properly for images of 32x32 and bigger.
    """

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, name="FlatImageBook"):
        """
        Default class constructor.

        Parameters:
        @param parent - parent window
        @param id - Window id
        @param pos - Window position
        @param size - Window size
        @param style - possible style INB_XXX
        """
        
        FlatBookBase.__init__(self, parent, id, pos, size, style, name)
        
        self._pages = self.CreateImageContainer()

        if style & INB_LEFT or style & INB_RIGHT:
            self._mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        else:
            self._mainSizer = wx.BoxSizer(wx.VERTICAL)

        self.SetSizer(self._mainSizer)

        # Add the tab container to the sizer
        self._mainSizer.Add(self._pages, 0, wx.EXPAND)

        if style & INB_LEFT or style & INB_RIGHT:
            self._pages.SetSizeHints(self._pages.GetImageSize() * 2, -1)
        else:
            self._pages.SetSizeHints(-1, self._pages.GetImageSize() * 2)

        self._mainSizer.Layout()
        
        
    def CreateImageContainer(self):

        return ImageContainer(self, wx.ID_ANY)


# ---------------------------------------------------------------------------- #
# Class LabelBook
# ---------------------------------------------------------------------------- #

class LabelBook(FlatBookBase):
    """
    An implementation of a notebook control - except that instead of having
    tabs to show labels, it labels to the right or left (arranged horozontally).
    """
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, name="LabelBook"):
        """
        Default class constructor.

        Parameters:
        @param parent - parent window
        @param id - Window id
        @param pos - Window position
        @param size - Window size
        @param style - possible style INB_XXX
        """
        
        FlatBookBase.__init__(self, parent, id, pos, size, style, name)
        
        self._pages = self.CreateImageContainer()

        # Label book specific initialization
        self._mainSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self._mainSizer)

        # Add the tab container to the sizer
        
        self._mainSizer.Add(self._pages, 0, wx.EXPAND)
        self._pages.SetSizeHints(self._pages.GetTabAreaWidth(), -1)
        # Initialize the colors maps
        self._pages.InitializeColors()
        
        self.Bind(wx.EVT_SIZE, self.OnSize)
        

    def CreateImageContainer(self):
        """ Creates the image container (LabelContainer). """

        return LabelContainer(self, wx.ID_ANY)


    def SetColour(self, which, color):
        """ Sets the colour for the specified parameter. """

        self._pages.SetColour(which, color)


    def GetColour(self, which):
        """ Returns the colour for the specified parameter. """

        return self._pages.GetColour(which)


    def OnSize(self, event):
        """ Handles the wx.EVT_SIZE for LabelBook. """

        self._pages.Refresh()
        event.Skip()

