import wx
import os
import cStringIO

from Resources import *

# ---------------------------------------------------------------------------- #
# Class DCSaver
# ---------------------------------------------------------------------------- #

class DCSaver:
    """
    Construct a DC saver. The dc is copied as-is.
    """

    def __init__(self, pdc):
        """
        Default class constructor. 
        """

        self._pdc = pdc
        self._pen = pdc.GetPen()
        self._brush = pdc.GetBrush()


    def __del__(self):
        """ While destructing, restores the dc pen and brush. """

        if self._pdc:
            self._pdc.SetPen(self._pen)
            self._pdc.SetBrush(self._brush)


# ---------------------------------------------------------------------------- #
# Class RendererBase
# ---------------------------------------------------------------------------- #

class RendererBase:
    """ Base class for all theme renderers. """
    
    def __init__(self):
        pass


    def DrawButtonBorders(self, dc, rect, penColor, brushColor):

        # Keep old pen and brush
        dcsaver = DCSaver(dc)
        dc.SetPen(wx.Pen(penColor))
        dc.SetBrush(wx.Brush(brushColor))
        dc.DrawRectangleRect(rect)


    def DrawBitmapArea(self, dc, xpm_name, rect, baseColor, flipSide):

        # draw the grandient area
        if not flipSide:
            ArtManager.Get().PaintDiagonalGradientBox(dc, rect, wx.WHITE,
                                                      ArtManager.Get().LightColour(baseColor, 20),
                                                      True, False)
        else:
            ArtManager.Get().PaintDiagonalGradientBox(dc, rect, ArtManager.Get().LightColour(baseColor, 20),
                                                      wx.WHITE, True, False)

        # draw arrow
        arrowDown = wx.BitmapFromXPMData(xpm_name)
        arrowDown.SetMask(wx.Mask(arrowDown, wx.WHITE))
        dc.DrawBitmap(arrowDown, rect.x + 1 , rect.y + 1, True)


    def DrawBitmapBorders(self, dc, rect, penColor, bitmapBorderUpperLeftPen):

        # Keep old pen and brush
        dcsaver = DCSaver(dc)

        # lower right size
        dc.SetPen(wx.Pen(penColor))
        dc.DrawLine(rect.x, rect.y + rect.height - 1, rect.x + rect.width, rect.y + rect.height - 1)
        dc.DrawLine(rect.x + rect.width - 1, rect.y, rect.x + rect.width - 1, rect.y + rect.height)
        
        # upper left side
        dc.SetPen(wx.Pen(bitmapBorderUpperLeftPen))
        dc.DrawLine(rect.x, rect.y, rect.x + rect.width, rect.y)
        dc.DrawLine(rect.x, rect.y, rect.x, rect.y + rect.height)


                
# ---------------------------------------------------------------------------- #
# Class RendererXP
# ---------------------------------------------------------------------------- #

class RendererXP(RendererBase):
    """ Xp-Style renderer. """
    
    def __init__(self):

        RendererBase.__init__(self)


    def DrawButton(self, dc, rect, state, input=None):
        """ Colors rectangle according to the XP theme. """

        if input is None or type(input) == type(False):
            self.DrawButtonTheme(dc, rect, state, input)
        else:
            self.DrawButtonColour(dc, rect, state, input)

            
    def DrawButtonTheme(self, dc, rect, state, useLightColours=None):
        """ Colors rectangle according to the XP theme. """

        # switch according to the status
        if state == ControlFocus:
            penColor = ArtManager.Get().FrameColour()
            brushColor = ArtManager.Get().BackgroundColor()
        elif state == ControlPressed:
            penColor = ArtManager.Get().FrameColour()
            brushColor = ArtManager.Get().HighlightBackgroundColor()
        else:
            penColor = ArtManager.Get().FrameColour()
            brushColor = ArtManager.Get().BackgroundColor()        

        # Draw the button borders
        self.DrawButtonBorders(dc, rect, penColor, brushColor)


    def DrawButtonColour(self, dc, rect, state, color):
        """ Colors rectangle according to the XP theme. """

        # switch according to the status        
        if statet == ControlFocus:
            penColor = color
            brushColor = ArtManager.Get().LightColour(color, 75)
        elif state == ControlPressed:
            penColor = color
            brushColor = ArtManager.Get().LightColour(color, 60)
        else:
            penColor = color
            brushColor = ArtManager.Get().LightColour(color, 75)

        # Draw the button borders
        self.DrawButtonBorders(dc, rect, penColor, brushColor)


    def DrawMenuBarBg(self, dc, rect):
        """ Draws the menu bar background according to the active theme. """

        # For office style, we simple draw a rectangle with a gradient colouring
        vertical = ArtManager.Get().GetMBVerticalGradient()

        dcsaver = DCSaver(dc)

        # fill with gradient
        startColor = ArtManager.Get().GetMenuBarFaceColour()
        if ArtManager.Get().IsDark(startColor):
            startColor = ArtManager.Get().LightColour(startColor, 50)

        endColor = ArtManager.Get().LightColour(startColor, 90)
        ArtManager.Get().PaintStraightGradientBox(dc, rect, startColor, endColor, vertical)

        # Draw the border
        if ArtManager.Get().GetMenuBarBorder():

            dc.SetPen(wx.Pen(startColor))
            dc.SetBrush(wx.TRANSPARENT_BRUSH)
            dc.DrawRectangleRect(rect)


    def DrawToolBarBg(self, dc, rect):
        """ Draws the toolbar background according to the active theme. """

        if not ArtManager.Get().GetRaiseToolbar():
            return

        # For office style, we simple draw a rectangle with a gradient colouring
        vertical = ArtManager.Get().GetMBVerticalGradient()

        dcsaver = DCSaver(dc)

        # fill with gradient
        startColor = ArtManager.Get().GetMenuBarFaceColour()
        if ArtManager.Get().IsDark(startColor):
            startColor = ArtManager.Get().LightColour(startColor, 50)
    
        startColor = ArtManager.Get().LightColour(startColor, 20)

        endColor   = ArtManager.Get().LightColour(startColor, 90)
        ArtManager.Get().PaintStraightGradientBox(dc, rect, startColor, endColor, vertical)
        ArtManager.Get().DrawBitmapShadow(dc, rect)


# ---------------------------------------------------------------------------- #
# Class RendererMSOffice2007 - Vista
# ---------------------------------------------------------------------------- #

class RendererMSOffice2007(RendererBase):
    """ Windows Vista style. """
    
    def __init__(self):

        RendererBase.__init__(self)


    def GetColorsAccordingToState(self, state):

        # switch according to the status        
        if state == ControlFocus:
            upperBoxTopPercent = 95
            upperBoxBottomPercent = 50
            lowerBoxTopPercent = 40
            lowerBoxBottomPercent = 90
            concaveUpperBox = True
            concaveLowerBox = True
            
        elif state == ControlPressed:
            upperBoxTopPercent = 75
            upperBoxBottomPercent = 90
            lowerBoxTopPercent = 90
            lowerBoxBottomPercent = 40
            concaveUpperBox = True
            concaveLowerBox = True

        elif state == ControlDisabled:
            upperBoxTopPercent = 100
            upperBoxBottomPercent = 100
            lowerBoxTopPercent = 70
            lowerBoxBottomPercent = 70
            concaveUpperBox = True
            concaveLowerBox = True

        else:
            upperBoxTopPercent = 90
            upperBoxBottomPercent = 50
            lowerBoxTopPercent = 30
            lowerBoxBottomPercent = 75
            concaveUpperBox = True
            concaveLowerBox = True

        return upperBoxTopPercent, upperBoxBottomPercent, lowerBoxTopPercent, lowerBoxBottomPercent, \
               concaveUpperBox, concaveLowerBox

        
    def DrawButton(self, dc, rect, state, useLightColours):
        """ Colors rectangle according to the Vista theme. """

        self.DrawButtonColour(dc, rect, state, ArtManager.Get().GetThemeBaseColour(useLightColours))


    def DrawButtonColour(self, dc, rect, state, colour):
        """ Colors rectangle according to the Vista theme. """
        
        # Keep old pen and brush
        dcsaver = DCSaver(dc)
        
        # Define the rounded rectangle base on the given rect
        # we need an array of 9 points for it        
        baseColour = colour

        # Define the middle points
        leftPt = wx.Point(rect.x, rect.y + (rect.height / 2))
        rightPt = wx.Point(rect.x + rect.width-1, rect.y + (rect.height / 2))

        # Define the top region
        top = wx.RectPP((rect.GetLeft(), rect.GetTop()), rightPt)
        bottom = wx.RectPP(leftPt, (rect.GetRight(), rect.GetBottom()))

        upperBoxTopPercent, upperBoxBottomPercent, lowerBoxTopPercent, lowerBoxBottomPercent, \
                            concaveUpperBox, concaveLowerBox = self.GetColorsAccordingToState(state)

        topStartColor = ArtManager.Get().LightColour(baseColour, upperBoxTopPercent)
        topEndColor = ArtManager.Get().LightColour(baseColour, upperBoxBottomPercent)
        bottomStartColor = ArtManager.Get().LightColour(baseColour, lowerBoxTopPercent)
        bottomEndColor = ArtManager.Get().LightColour(baseColour, lowerBoxBottomPercent)

        ArtManager.Get().PaintStraightGradientBox(dc, top, topStartColor, topEndColor)
        ArtManager.Get().PaintStraightGradientBox(dc, bottom, bottomStartColor, bottomEndColor)

        rr = wx.Rect(rect.x, rect.y, rect.width, rect.height)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)

        frameColor = ArtManager.Get().LightColour(baseColour, 60)
        dc.SetPen(wx.Pen(frameColor))
        dc.DrawRectangleRect(rr)

        wc = ArtManager.Get().LightColour(baseColour, 80)
        dc.SetPen(wx.Pen(wc))
        rr.Deflate(1, 1)
        dc.DrawRectangleRect(rr)


    def DrawMenuBarBg(self, dc, rect):
        """ Draws the menu bar background according to the active theme. """

        # Keep old pen and brush
        dcsaver = DCSaver(dc)
        baseColour = ArtManager.Get().GetMenuBarFaceColour()

        dc.SetBrush(wx.Brush(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)))
        dc.SetPen(wx.Pen(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)))
        dc.DrawRectangleRect(rect)

        # Define the rounded rectangle base on the given rect
        # we need an array of 9 points for it
        regPts = [wx.Point() for ii in xrange(9)]
        radius = 2
        
        regPts[0] = wx.Point(rect.x, rect.y + radius)
        regPts[1] = wx.Point(rect.x+radius, rect.y)
        regPts[2] = wx.Point(rect.x+rect.width-radius-1, rect.y)
        regPts[3] = wx.Point(rect.x+rect.width-1, rect.y + radius)
        regPts[4] = wx.Point(rect.x+rect.width-1, rect.y + rect.height - radius - 1)
        regPts[5] = wx.Point(rect.x+rect.width-radius-1, rect.y + rect.height-1)
        regPts[6] = wx.Point(rect.x+radius, rect.y + rect.height-1)
        regPts[7] = wx.Point(rect.x, rect.y + rect.height - radius - 1)
        regPts[8] = regPts[0]

        # Define the middle points

        factor = ArtManager.Get().GetMenuBgFactor()
        
        leftPt1 = wx.Point(rect.x, rect.y + (rect.height / factor))
        leftPt2 = wx.Point(rect.x, rect.y + (rect.height / factor)*(factor-1))

        rightPt1 = wx.Point(rect.x + rect.width, rect.y + (rect.height / factor))
        rightPt2 = wx.Point(rect.x + rect.width, rect.y + (rect.height / factor)*(factor-1))

        # Define the top region
        topReg = [wx.Point() for ii in xrange(7)]
        topReg[0] = regPts[0]
        topReg[1] = regPts[1]
        topReg[2] = wx.Point(regPts[2].x+1, regPts[2].y)
        topReg[3] = wx.Point(regPts[3].x + 1, regPts[3].y)
        topReg[4] = wx.Point(rightPt1.x, rightPt1.y+1)
        topReg[5] = wx.Point(leftPt1.x, leftPt1.y+1)
        topReg[6] = topReg[0]

        # Define the middle region
        middle = wx.RectPP(leftPt1, wx.Point(rightPt2.x - 2, rightPt2.y))
            
        # Define the bottom region
        bottom = wx.RectPP(leftPt2, wx.Point(rect.GetRight() - 1, rect.GetBottom()))

        topStartColor   = ArtManager.Get().LightColour(baseColour, 90)
        topEndColor = ArtManager.Get().LightColour(baseColour, 60)
        bottomStartColor = ArtManager.Get().LightColour(baseColour, 40)
        bottomEndColor   = ArtManager.Get().LightColour(baseColour, 20)
        
        topRegion = wx.RegionFromPoints(topReg)

        ArtManager.Get().PaintGradientRegion(dc, topRegion, topStartColor, topEndColor)
        ArtManager.Get().PaintStraightGradientBox(dc, bottom, bottomStartColor, bottomEndColor)
        ArtManager.Get().PaintStraightGradientBox(dc, middle, topEndColor, bottomStartColor)
     

    def DrawToolBarBg(self, dc, rect):
        """ Draws the toolbar background according to the active theme. """

        if not ArtManager.Get().GetRaiseToolbar():
            return

        # Keep old pen and brush
        dcsaver = DCSaver(dc)
        
        baseColour = ArtManager.Get().GetMenuBarFaceColour()
        baseColour = ArtManager.Get().LightColour(baseColour, 20)

        dc.SetBrush(wx.Brush(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)))
        dc.SetPen(wx.Pen(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)))
        dc.DrawRectangleRect(rect)

        radius = 2
        
        # Define the rounded rectangle base on the given rect
        # we need an array of 9 points for it
        regPts = [None]*9
        
        regPts[0] = wx.Point(rect.x, rect.y + radius)
        regPts[1] = wx.Point(rect.x+radius, rect.y)
        regPts[2] = wx.Point(rect.x+rect.width-radius-1, rect.y)
        regPts[3] = wx.Point(rect.x+rect.width-1, rect.y + radius)
        regPts[4] = wx.Point(rect.x+rect.width-1, rect.y + rect.height - radius - 1)
        regPts[5] = wx.Point(rect.x+rect.width-radius-1, rect.y + rect.height-1)
        regPts[6] = wx.Point(rect.x+radius, rect.y + rect.height-1)
        regPts[7] = wx.Point(rect.x, rect.y + rect.height - radius - 1)
        regPts[8] = regPts[0]

        # Define the middle points
        factor = ArtManager.Get().GetMenuBgFactor()

        leftPt1 = wx.Point(rect.x, rect.y + (rect.height / factor))
        rightPt1 = wx.Point(rect.x + rect.width, rect.y + (rect.height / factor))
        
        leftPt2 = wx.Point(rect.x, rect.y + (rect.height / factor)*(factor-1))
        rightPt2 = wx.Point(rect.x + rect.width, rect.y + (rect.height / factor)*(factor-1))

        # Define the top region
        topReg = [None]*7
        topReg[0] = regPts[0]
        topReg[1] = regPts[1]
        topReg[2] = wx.Point(regPts[2].x+1, regPts[2].y)
        topReg[3] = wx.Point(regPts[3].x + 1, regPts[3].y)
        topReg[4] = wx.Point(rightPt1.x, rightPt1.y+1)
        topReg[5] = wx.Point(leftPt1.x, leftPt1.y+1)
        topReg[6] = topReg[0]

        # Define the middle region
        middle = wx.RectPP(leftPt1, wx.Point(rightPt2.x - 2, rightPt2.y))

        # Define the bottom region
        bottom = wx.RectPP(leftPt2, wx.Point(rect.GetRight() - 1, rect.GetBottom()))
        
        topStartColor   = ArtManager.Get().LightColour(baseColour, 90)
        topEndColor = ArtManager.Get().LightColour(baseColour, 60)
        bottomStartColor = ArtManager.Get().LightColour(baseColour, 40)
        bottomEndColor   = ArtManager.Get().LightColour(baseColour, 20)
        
        topRegion = wx.RegionFromPoints(topReg)

        ArtManager.Get().PaintGradientRegion(dc, topRegion, topStartColor, topEndColor)
        ArtManager.Get().PaintStraightGradientBox(dc, bottom, bottomStartColor, bottomEndColor)
        ArtManager.Get().PaintStraightGradientBox(dc, middle, topEndColor, bottomStartColor)

        ArtManager.Get().DrawBitmapShadow(dc, rect)


# ---------------------------------------------------------------------------- #
# Class ArtManager
# ---------------------------------------------------------------------------- #

class ArtManager(wx.EvtHandler):

    """
    This class provides various art utilities, such as creating shadow, providing
    lighter / darker colors for a given color, etc...
    """
    
    _alignmentBuffer = 7
    _menuTheme = StyleXP
    _verticalGradient = False
    _renderers = {StyleXP: None, Style2007: None}
    _bmpShadowEnabled = False
    _ms2007sunken = False
    _drowMBBorder = True
    _menuBgFactor = 5
    _menuBarColourScheme = "Default"
    _raiseTB = True
    _bitmaps = {}

    def __init__(self):
        """ Default class constructor. """

        wx.EvtHandler.__init__(self)
        self._menuBarBgColour = wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE)
        
        # connect an event handler to the system colour change event
        self.Bind(wx.EVT_SYS_COLOUR_CHANGED, self.OnSysColourChange)
    

    def ConvertToBitmap(self, xpm, alpha=None):
        """ Convert the given image to a bitmap. """

        if alpha is not None:

            img = wx.BitmapFromXPMData(xpm)
            img = img.ConvertToImage()
            x, y = img.GetWidth(), img.GetHeight()
            img.InitAlpha()
            for jj in xrange(y):
                for ii in xrange(x):
                    img.SetAlpha(ii, jj, alpha[jj*x+ii])
                    
        else:

            stream = cStringIO.StringIO(xpm)
            img = wx.ImageFromStream(stream)
            
        return wx.BitmapFromImage(img)

                
    def Initialize(self):
        """ Initializes the bitmaps and colours. """

        # create wxBitmaps from the xpm's
        self._rightBottomCorner = self.ConvertToBitmap(shadow_center_xpm, shadow_center_alpha)
        self._bottom = self.ConvertToBitmap(shadow_bottom_xpm, shadow_bottom_alpha)
        self._bottomLeft = self.ConvertToBitmap(shadow_bottom_left_xpm, shadow_bottom_left_alpha)
        self._rightTop = self.ConvertToBitmap(shadow_right_top_xpm, shadow_right_top_alpha)
        self._right = self.ConvertToBitmap(shadow_right_xpm, shadow_right_alpha)

        # initialise the colour map
        self.InitColours()
        self.SetMenuBarColour(self._menuBarColourScheme)
        
        # Create common bitmaps
        self.FillStockBitmaps()


    def FillStockBitmaps(self):

        bmp = self.ConvertToBitmap(arrow_down, alpha=None)
        bmp.SetMask(wx.Mask(bmp, wx.Color(0, 128, 128)))
        self._bitmaps.update({"arrow_down": bmp})

        bmp = self.ConvertToBitmap(arrow_up, alpha=None)
        bmp.SetMask(wx.Mask(bmp, wx.Color(0, 128, 128)))
        self._bitmaps.update({"arrow_up": bmp})


    def GetStockBitmap(self, name):
        """ Gets a bitmap from a stock. If bitmap does not exist, return wx.NullBitmap. """

        if self._bitmaps.has_key(name):
            return self._bitmaps[name]

        return wx.NullBitmap


    def Get(self):

        if not hasattr(self, "_instance"):
        
            self._instance = ArtManager()
            self._instance.Initialize()

            # Initialize the renderers map
            self._renderers[StyleXP] = RendererXP()
            self._renderers[Style2007] = RendererMSOffice2007()
        
        return self._instance

    Get = classmethod(Get)
    
    def Free(self):

        if hasattr(self, "_instance"):
        
            del self._instance

    Free = classmethod(Free)


    def OnSysColourChange(self, event):
        """ Handles the wx.EVT_SYS_COLOUR_CHANGED event for ArtManager. """

        # reinitialise the colour map
        self.InitColours()


    def LightColour(self, color, percent):
        """
        Return light contrast of color. The color returned is from the scale of
        color -> white. The percent determines how light the color will be.
        Percent = 100 return white, percent = 0 returns color.
        """

        end_color = wx.WHITE
        rd = end_color.Red() - color.Red()
        gd = end_color.Green() - color.Green()
        bd = end_color.Blue() - color.Blue()
        high = 100

        # We take the percent way of the color from color -. white
        i = percent
        r = color.Red() + ((i*rd*100)/high)/100
        g = color.Green() + ((i*gd*100)/high)/100
        b = color.Blue() + ((i*bd*100)/high)/100

        return wx.Color(r, g, b)


    def DarkColour(self, color, percent):
        """ Like the LightColour() function, but create the color darker by percent. """

        end_color = wx.BLACK
        rd = end_color.Red() - color.Red()
        gd = end_color.Green() - color.Green()
        bd = end_color.Blue() - color.Blue()
        high = 100

        # We take the percent way of the color from color -. white
        i = percent
        r = color.Red() + ((i*rd*100)/high)/100
        g = color.Green() + ((i*gd*100)/high)/100
        b = color.Blue() + ((i*bd*100)/high)/100

        return wx.Color(r, g, b)


    def PaintStraightGradientBox(self, dc, rect, startColor, endColor, vertical=True):
        """
        Paint the rectangle with gradient coloring; the gradient lines are either
        horizontal or vertical.
        """

        rd = endColor.Red() - startColor.Red()
        gd = endColor.Green() - startColor.Green()
        bd = endColor.Blue() - startColor.Blue()

        # Save the current pen and brush
        savedPen = dc.GetPen()
        savedBrush = dc.GetBrush()

        if vertical:
            high = rect.GetHeight()-1
        else:
            high = rect.GetWidth()-1

        if high < 1:
            return

        for i in xrange(high+1):
        
            r = startColor.Red() +  ((i*rd*100)/high)/100
            g = startColor.Green() + ((i*gd*100)/high)/100
            b = startColor.Blue() + ((i*bd*100)/high)/100

            p = wx.Pen(wx.Color(r, g, b))
            dc.SetPen(p)

            if vertical:
                dc.DrawLine(rect.x, rect.y+i, rect.x+rect.width, rect.y+i)
            else:
                dc.DrawLine(rect.x+i, rect.y, rect.x+i, rect.y+rect.height)
        
        # Restore the pen and brush
        dc.SetPen(savedPen)
        dc.SetBrush(savedBrush)


    def PaintGradientRegion(self, dc, region, startColor, endColor, vertical=True):
        """ Paint a region with gradient coloring. """

        # The way to achieve non-rectangle 
        memDC = wx.MemoryDC()
        rect = region.GetBox()
        bitmap = wx.EmptyBitmap(rect.width, rect.height)
        memDC.SelectObject(bitmap)

        # Color the whole rectangle with gradient
        rr = wx.Rect(0, 0, rect.width, rect.height)
        self.PaintStraightGradientBox(memDC, rr, startColor, endColor, vertical)

        # Convert the region to a black and white bitmap with the white pixels being inside the region
        # we draw the bitmap over the gradient colored rectangle, with mask set to white, 
        # this will cause our region to be colored with the gradient, while area outside the 
        # region will be painted with black. then we simply draw the bitmap to the dc with mask set to 
        # black
        tmpRegion = wx.Region(rect.x, rect.y, rect.width, rect.height)
        tmpRegion.Offset(-rect.x, -rect.y)
        regionBmp = tmpRegion.ConvertToBitmap()
        regionBmp.SetMask(wx.Mask(regionBmp, wx.WHITE))

        # The function ConvertToBitmap() return a rectangle bitmap
        # which is shorter by 1 pixl on the height and width (this is correct behavior, since 
        # DrawLine does not include the second point as part of the line)
        # we fix this issue by drawing our own line at the bottom and left side of the rectangle
        memDC.SetPen(wx.BLACK_PEN)
        memDC.DrawBitmap(regionBmp, 0, 0, True)
        memDC.DrawLine(0, rr.height - 1, rr.width, rr.height - 1)
        memDC.DrawLine(rr.width - 1, 0, rr.width - 1, rr.height)

        memDC.SelectObject(wx.NullBitmap)
        bitmap.SetMask(wx.Mask(bitmap, wx.BLACK))
        dc.DrawBitmap(bitmap, rect.x, rect.y, True)


    def PaintDiagonalGradientBox(self, dc, rect, startColor, endColor,
                                 startAtUpperLeft=True, trimToSquare=True):
        """
        Paint rectagnle with gradient coloring; the gradient lines are diagonal
        and may start from the upper left corner or from the upper right corner.
        """

        # Save the current pen and brush
        savedPen = dc.GetPen()
        savedBrush = dc.GetBrush()

        # gradient fill from colour 1 to colour 2 with top to bottom
        if rect.height < 1 or rect.width < 1:
            return

        # calculate some basic numbers
        size = rect.width
        sizeX = sizeY = 0
        proportion = 1
        
        if rect.width > rect.height:
        
            if trimToSquare:
            
                size = rect.height
                sizeX = sizeY = rect.height - 1
            
            else:
            
                proportion = float(rect.height)/float(rect.width)
                size = rect.width
                sizeX = rect.width - 1
                sizeY = rect.height -1
            
        else:
        
            if trimToSquare:
            
                size = rect.width
                sizeX = sizeY = rect.width - 1
            
            else:
            
                sizeX = rect.width - 1
                size = rect.height
                sizeY = rect.height - 1
                proportion = float(rect.width)/float(rect.height)

        # calculate gradient coefficients
        col2 = endColor
        col1 = startColor

        rf, gf, bf = 0, 0, 0
        rstep = float(col2.Red() - col1.Red())/float(size)
        gstep = float(col2.Green() - col1.Green())/float(size)
        bstep = float(col2.Blue() - col1.Blue())/float(size)
        
        # draw the upper triangle
        for i in xrange(size):
        
            currCol = wx.Colour(col1.Red() + rf, col1.Green() + gf, col1.Blue() + bf)
            dc.SetBrush(wx.Brush(currCol, wx.SOLID))
            dc.SetPen(wx.Pen(currCol))
            
            if startAtUpperLeft:
            
                if rect.width > rect.height:
                
                    dc.DrawLine(rect.x + i, rect.y, rect.x, int(rect.y + proportion*i))
                    dc.DrawPoint(rect.x, int(rect.y + proportion*i))
                
                else:
                
                    dc.DrawLine(int(rect.x + proportion*i), rect.y, rect.x, rect.y + i)
                    dc.DrawPoint(rect.x, rect.y + i)
                
            else:
            
                if rect.width > rect.height:
                
                    dc.DrawLine(rect.x + sizeX - i, rect.y, rect.x + sizeX, int(rect.y + proportion*i))
                    dc.DrawPoint(rect.x + sizeX, int(rect.y + proportion*i))
                
                else:
                
                    xTo = (int(rect.x + sizeX - proportion * i) > rect.x and [int(rect.x + sizeX - proportion*i)] or [rect.x])[0]
                    dc.DrawLine(xTo, rect.y, rect.x + sizeX, rect.y + i)
                    dc.DrawPoint(rect.x + sizeX, rect.y + i)
                
            rf += rstep/2
            gf += gstep/2
            bf += bstep/2
        
        # draw the lower triangle
        for i in xrange(size):

            currCol = wx.Colour(col1.Red() + rf, col1.Green() + gf, col1.Blue() + bf)        
            dc.SetBrush(wx.Brush(currCol, wx.SOLID))
            dc.SetPen(wx.Pen(currCol))
            
            if startAtUpperLeft:
            
                if rect.width > rect.height:
                
                    dc.DrawLine(rect.x + i, rect.y + sizeY, rect.x + sizeX, int(rect.y + proportion * i))
                    dc.DrawPoint(rect.x + sizeX, int(rect.y + proportion * i))
                
                else:
                
                    dc.DrawLine(int(rect.x + proportion * i), rect.y + sizeY, rect.x + sizeX, rect.y + i)
                    dc.DrawPoint(rect.x + sizeX, rect.y + i)
                
            else:
            
                if rect.width > rect.height:
                
                    dc.DrawLine(rect.x, (int)(rect.y + proportion * i), rect.x + sizeX - i, rect.y + sizeY)
                    dc.DrawPoint(rect.x + sizeX - i, rect.y + sizeY)
                
                else:
                
                    xTo = (int(rect.x + sizeX - proportion*i) > rect.x and [int(rect.x + sizeX - proportion*i)] or [rect.x])[0]
                    dc.DrawLine(rect.x, rect.y + i, xTo, rect.y + sizeY)
                    dc.DrawPoint(xTo, rect.y + sizeY)
                
            rf += rstep/2
            gf += gstep/2
            bf += bstep/2
        

        # Restore the pen and brush
        dc.SetPen( savedPen )
        dc.SetBrush( savedBrush )


    def PaintCrescentGradientBox(self, dc, rect, startColor, endColor, concave=True):
        """
        Paint a region with gradient coloring. The gradient is in crescent shape
        which fits the 2007 style.
        """

        diagonalRectWidth = rect.GetWidth()/4
        spare = rect.width - 4*diagonalRectWidth
        leftRect = wx.Rect(rect.x, rect.y, diagonalRectWidth, rect.GetHeight())
        rightRect = wx.Rect(rect.x + 3 * diagonalRectWidth + spare, rect.y, diagonalRectWidth, rect.GetHeight())
        
        if concave:
        
            self.PaintStraightGradientBox(dc, rect, self.MixColors(startColor, endColor, 50), endColor)
            self.PaintDiagonalGradientBox(dc, leftRect, startColor, endColor, True, False) 
            self.PaintDiagonalGradientBox(dc, rightRect, startColor, endColor, False, False) 
        
        else:
        
            self.PaintStraightGradientBox(dc, rect, endColor, self.MixColors(endColor, startColor, 50))
            self.PaintDiagonalGradientBox(dc, leftRect, endColor, startColor, False, False) 
            self.PaintDiagonalGradientBox(dc, rightRect, endColor, startColor, True, False) 


    def FrameColour(self):
        """ Return the surrounding color for a control. """

        return wx.SystemSettings_GetColour(wx.SYS_COLOUR_ACTIVECAPTION)


    def BackgroundColor(self):
        """ Returns the background color of a control when not in focus. """

        return self.LightColour(self.FrameColour(), 75)


    def HighlightBackgroundColor(self):
        """ Returns the background color of a control when it is in focus. """

        return self.LightColour(self.FrameColour(), 60)


    def MixColors(self, firstColor, secondColor, percent):
        """ Return mix of input colors. """

        # calculate gradient coefficients
        redOffset = float((secondColor.Red() * (100 - percent) / 100) - (firstColor.Red() * percent / 100))
        greenOffset = float((secondColor.Green() * (100 - percent) / 100) - (firstColor.Green() * percent / 100))
        blueOffset = float((secondColor.Blue() * (100 - percent) / 100) -  (firstColor.Blue() * percent / 100))

        return wx.Color(firstColor.Red() + redOffset, firstColor.Green() + greenOffset,
                        firstColor.Blue() + blueOffset)


    def RandomColour(): 
        """ Creates a random colour. """
        
        r = random.randint(0, 255) # Random value betweem 0-255
        g = random.randint(0, 255) # Random value betweem 0-255
        b = random.randint(0, 255) # Random value betweem 0-255

        return wx.Colour(r, g, b)


    def IsDark(self, color):
        """ Returns whether a color is dark or light. """

        evg = (color.Red() + color.Green() + color.Blue())/3
        
        if evg < 127:
            return True

        return False


    def TruncateText(self, dc, text, maxWidth):
        """
        Truncates a given string to fit given width size. if the text does not fit
        into the given width it is truncated to fit. the format of the fixed text
        is <truncate text ..>.
        """

        textLen = len(text)
        tempText = text
        rectSize = maxWidth

        fixedText = ""
        
        textW, textH = dc.GetTextExtent(text)

        if rectSize >= textW:        
            return text
        
        # The text does not fit in the designated area, 
        # so we need to truncate it a bit
        suffix = ".."
        w, h = dc.GetTextExtent(suffix)
        rectSize -= w

        for i in xrange(textLen, -1, -1):
        
            textW, textH = dc.GetTextExtent(tempText)
            if rectSize >= textW:
                fixedText = tempText
                fixedText += ".."
                return fixedText
            
            tempText = tempText[:-1]


    def DrawButton(self, dc, rect, theme, state, input=None):
        """ Color rectangle according to the theme. """

        if input is None or type(input) == type(False):
            self.DrawButtonTheme(dc, rect, theme, state, input)
        else:
            self.DrawButtonColour(dc, rect, theme, state, input)
            
                           
    def DrawButtonTheme(self, dc, rect, theme, state, useLightColours=True):
        """ Color rectangle according to the theme. """

        renderer = self._renderers[theme]
        
        # Set background color if non given by caller
        renderer.DrawButton(dc, rect, state, useLightColours)


    def DrawButtonColour(self, dc, rect, theme, state, color):
        """ Color rectangle according to the theme. """

        renderer = self._renderers[theme]
        renderer.DrawButton(dc, rect, state, color)


    def CanMakeWindowsTransparent(self):
        """ Used internally. """

        if wx.Platform == "__WXMSW__":

            version = wx.GetOsDescription()
            found = version.find("XP") >= 0 or version.find("2000") >= 0 or version.find("NT") >= 0
            return found

        elif wx.Platform == "__WXMAC__" and _carbon_dll:
            return True
        else:
            return False
        

    # on supported windows systems (Win2000 and greater), this function
    # will make a frame window transparent by a certain amount
    def MakeWindowTransparent(self, wnd, amount):
        """ Used internally. """

        if wnd.GetSize() == (0, 0):
            return

        if not self.CanMakeWindowsTransparent():
            return
        
        # this API call is not in all SDKs, only the newer ones, so
        # we will runtime bind this
        if wx.Platform == "__WXMSW__":
            hwnd = wnd.GetHandle()
    
            if not hasattr(self, "_winlib"):
                if _libimported == "MH":
                    self._winlib = win32api.LoadLibrary("user32")
                elif _libimported == "ctypes":
                    self._winlib = ctypes.windll.user32
                    
            if _libimported == "MH":
                pSetLayeredWindowAttributes = win32api.GetProcAddress(self._winlib,
                                                                      "SetLayeredWindowAttributes")
                
                if pSetLayeredWindowAttributes == None:
                    return
                    
                exstyle = win32api.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                if 0 == (exstyle & 0x80000):
                    win32api.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, exstyle | 0x80000)  
                         
                winxpgui.SetLayeredWindowAttributes(hwnd, 0, amount, 2)
    
            elif _libimported == "ctypes":
                style = self._winlib.GetWindowLongA(hwnd, 0xffffffecL)
                style |= 0x00080000
                self._winlib.SetWindowLongA(hwnd, 0xffffffecL, style)
                self._winlib.SetLayeredWindowAttributes(hwnd, 0, amount, 2)
                
        elif wx.Platform == "__WXMAC__" and _carbon_dll:
            handle = _carbon_dll.GetControlOwner(wnd.GetHandle())
            if amount == 0:
                amnt = float(0)
            else:
                amnt = float(amount)/255.0  #convert from the 0-255 amount to the float that Carbon wants
            _carbon_dll.SetWindowAlpha(handle, ctypes.c_float(amnt))
        else:
            #shouldn't be called, but just in case...
            return


    # assumption: the background was already drawn on the dc
    def DrawBitmapShadow(self, dc, rect, where=BottomShadow|RightShadow):
        """ Draws a shadow using background bitmap. """
    
        shadowSize = 5

        # the rect must be at least 5x5 pixles
        if rect.height < 2*shadowSize or rect.width < 2*shadowSize:
            return

        # Start by drawing the right bottom corner
        if where & BottomShadow or where & BottomShadowFull:
            dc.DrawBitmap(self._rightBottomCorner, rect.x+rect.width, rect.y+rect.height, True)

        # Draw right side shadow
        xx = rect.x + rect.width
        yy = rect.y + rect.height - shadowSize

        if where & RightShadow:
            while yy - rect.y > 2*shadowSize:
                dc.DrawBitmap(self._right, xx, yy, True)
                yy -= shadowSize
            
            dc.DrawBitmap(self._rightTop, xx, yy - shadowSize, True)

        if where & BottomShadow:
            xx = rect.x + rect.width - shadowSize
            yy = rect.height + rect.y
            while xx - rect.x > 2*shadowSize:
                dc.DrawBitmap(self._bottom, xx, yy, True)
                xx -= shadowSize
                
            dc.DrawBitmap(self._bottomLeft, xx - shadowSize, yy, True)

        if where & BottomShadowFull:
            xx = rect.x + rect.width - shadowSize
            yy = rect.height + rect.y
            while xx - rect.x >= 0:
                dc.DrawBitmap(self._bottom, xx, yy, True)
                xx -= shadowSize
            
            dc.DrawBitmap(self._bottom, xx, yy, True)


    def DropShadow(self, wnd, drop=True):
        """ Adds a shadow under the window (Windows Only). """

        if not self.CanMakeWindowsTransparent() or not _libimported:
            return
        
        if "__WXMSW__" in wx.Platform:

            hwnd = wnd.GetHandle()
            
            if not hasattr(self, "_winlib"):
                if _libimported == "MH":
                    self._winlib = win32api.LoadLibrary("user32")
                elif _libimported == "ctypes":
                    self._winlib = ctypes.windll.user32
            
            if _libimported == "MH":
                csstyle = win32api.GetWindowLong(hwnd, win32con.GCL_STYLE)
            else:
                csstyle = self._winlib.GetWindowLongA(hwnd, win32con.GCL_STYLE)
            
            if drop:
                if csstyle & CS_DROPSHADOW:
                    return
                else:
                    csstyle |= CS_DROPSHADOW     #Nothing to be done
                    
            else:

                if csstyle & CS_DROPSHADOW:
                    csstyle &= ~(CS_DROPSHADOW)
                else:
                    return  #Nothing to be done

            win32api.SetWindowLong(hwnd, win32con.GCL_STYLE, csstyle)
            

    def GetBitmapStartLocation(self, dc, rect, bitmap, text="", style=0):
        """ Returns the top left x & y cordinates of the bitmap drawing. """

        alignmentBuffer = self.GetAlignBuffer()

        # get the startLocationY
        fixedTextWidth = fixedTextHeight = 0

        if not text:
            fixedTextHeight = bitmap.GetHeight()
        else:
            fixedTextWidth, fixedTextHeight = dc.GetTextExtent(text)
            
        startLocationY = rect.y + (rect.height - fixedTextHeight)/2

        # get the startLocationX
        if style & BU_EXT_RIGHT_TO_LEFT_STYLE:
        
            startLocationX = rect.x + rect.width - alignmentBuffer - bitmap.GetWidth()
        
        else:
        
            if style & BU_EXT_RIGHT_ALIGN_STYLE:
            
                maxWidth = rect.x + rect.width - (2 * alignmentBuffer) - bitmap.GetWidth() # the alignment is for both sides
                
                # get the truncaed text. The text may stay as is, it is not a must that is will be trancated
                fixedText = self.TruncateText(dc, text, maxWidth)

                # get the fixed text dimentions
                fixedTextWidth, fixedTextHeight = dc.GetTextExtent(fixedText)

                # calculate the start location
                startLocationX = maxWidth - fixedTextWidth
            
            elif style & BU_EXT_LEFT_ALIGN_STYLE:
            
                # calculate the start location
                startLocationX = alignmentBuffer
            
            else: # meaning BU_EXT_CENTER_ALIGN_STYLE
            
                maxWidth = rect.x + rect.width - (2 * alignmentBuffer) - bitmap.GetWidth() # the alignment is for both sides

                # get the truncaed text. The text may stay as is, it is not a must that is will be trancated
                fixedText = self.TruncateText(dc, text, maxWidth)

                # get the fixed text dimentions
                fixedTextWidth, fixedTextHeight = dc.GetTextExtent(fixedText)

                if maxWidth > fixedTextWidth:
                
                    # calculate the start location
                    startLocationX = (maxWidth - fixedTextWidth) / 2
                
                else:
                
                    # calculate the start location
                    startLocationX = maxWidth - fixedTextWidth                    
        
        # it is very important to validate that the start location is not less than the alignment buffer
        if startLocationX < alignmentBuffer:
            startLocationX = alignmentBuffer

        return startLocationX, startLocationY            


    def GetTextStartLocation(self, dc, rect, bitmap, text, style=0):
        """
        Returns the top left x & y cordinates of the text drawing.
        In case the text is too long, the text is being fixed (the text is cut and
        a '...' mark is added in the end).
        """

        alignmentBuffer = self.GetAlignBuffer()

        # get the bitmap offset
        bitmapOffset = 0
        if bitmap != wx.NullBitmap:
            bitmapOffset = bitmap.GetWidth()

        # get the truncated text. The text may stay as is, it is not a must that is will be trancated
        maxWidth = rect.x + rect.width - (2 * alignmentBuffer) - bitmapOffset # the alignment is for both sides

        fixedText = self.TruncateText(dc, text, maxWidth)

        # get the fixed text dimentions
        fixedTextWidth, fixedTextHeight = dc.GetTextExtent(fixedText)
        startLocationY = (rect.height - fixedTextHeight) / 2 + rect.y

        # get the startLocationX
        if style & BU_EXT_RIGHT_TO_LEFT_STYLE:
        
            startLocationX = maxWidth - fixedTextWidth + alignmentBuffer
        
        else:
        
            if style & BU_EXT_LEFT_ALIGN_STYLE:
            
                # calculate the start location
                startLocationX = bitmapOffset + alignmentBuffer
            
            elif style & BU_EXT_RIGHT_ALIGN_STYLE:
            
                # calculate the start location
                startLocationX = maxWidth - fixedTextWidth + bitmapOffset + alignmentBuffer
            
            else: # meaning wxBU_EXT_CENTER_ALIGN_STYLE
            
                # calculate the start location
                startLocationX = (maxWidth - fixedTextWidth) / 2 + bitmapOffset + alignmentBuffer
            
        
        # it is very important to validate that the start location is not less than the alignment buffer
        if startLocationX < alignmentBuffer:
            startLocationX = alignmentBuffer

        return startLocationX, startLocationY, fixedText
    

    def DrawTextAndBitmap(self, dc, rect, text, enable=True, font=wx.NullFont,
                          fontColor=wx.BLACK, bitmap=wx.NullBitmap,
                          grayBitmap=wx.NullBitmap, style=0):
        """ Draws the text & bitmap on the input dc. """

        # enable colors
        if enable:
            dc.SetTextForeground(fontColor)
        else:
            dc.SetTextForeground(wx.SystemSettings_GetColour(wx.SYS_COLOUR_GRAYTEXT))
        
        # set the font
        
        if font == wx.NullFont:
            font = wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT)
            
        dc.SetFont(font)
        
        startLocationX = startLocationY = 0
        
        if bitmap != wx.NullBitmap:
        
            # calculate the bitmap start location
            startLocationX, startLocationY = self.GetBitmapStartLocation(dc, rect, bitmap, text, style)

            # draw the bitmap
            if enable:
                dc.DrawBitmap(bitmap, startLocationX, startLocationY, True)
            else:
                dc.DrawBitmap(grayBitmap, startLocationX, startLocationY, True)
   
        # calculate the text start location
        location, labelOnly = self.GetAccelIndex(text)
        startLocationX, startLocationY, fixedText = self.GetTextStartLocation(dc, rect, bitmap, labelOnly, style)

        # after all the caculations are finished, it is time to draw the text
        # underline the first letter that is marked with a '&'
        if location == -1 or font.GetUnderlined() or location >= len(fixedText):
            # draw the text
            dc.DrawText(fixedText, startLocationX, startLocationY)
        
        else:
            
            # underline the first '&'
            before = fixedText[0:location]
            underlineLetter = fixedText[location] 
            after = fixedText[location+1:]

            # before
            dc.DrawText(before, startLocationX, startLocationY)

            # underlineLetter
            if "__WXGTK__" not in wx.Platform:
                w1, h = dc.GetTextExtent(before)
                font.SetUnderlined(True)
                dc.SetFont(font)
                dc.DrawText(underlineLetter, startLocationX + w1, startLocationY)
            else:
                w1, h = dc.GetTextExtent(before)
                dc.DrawText(underlineLetter, startLocationX + w1, startLocationY)

                # Draw the underline ourselves since using the Underline in GTK, 
                # causes the line to be too close to the letter
                uderlineLetterW, uderlineLetterH = dc.GetTextExtent(underlineLetter)

                curPen = dc.GetPen()
                dc.SetPen(wx.BLACK_PEN)

                dc.DrawLine(startLocationX + w1, startLocationY + uderlineLetterH - 2,
                            startLocationX + w1 + uderlineLetterW, startLocationY + uderlineLetterH - 2)
                dc.SetPen(curPen)

            # after
            w2, h = dc.GetTextExtent(underlineLetter)
            font.SetUnderlined(False)
            dc.SetFont(font)
            dc.DrawText(after, startLocationX + w1 + w2, startLocationY)


    def CalcButtonBestSize(self, label, bmp):
        """ Returns the best fit size for the supplied label & bitmap. """

        if "__WXMSW__" in wx.Platform:
            HEIGHT = 22
        else:
            HEIGHT = 26

        dc = wx.MemoryDC()
        dc.SelectBitmap(wx.EmptyBitmap(1, 1))

        dc.SetFont(wx.SystemSettings_GetFont(wx.SYS_DEFAULT_GUI_FONT))
        width, height, dummy = dc.GetMultiLineTextExtent(label)

        width += 2*self.GetAlignBuffer() 

        if bmp.Ok():
        
            # allocate extra space for the bitmap
            heightBmp = bmp.GetHeight() + 2
            if height < heightBmp:
                height = heightBmp

            width += bmp.GetWidth() + 2
        
        if height < HEIGHT:
            height = HEIGHT

        dc.SelectBitmap(wx.NullBitmap)
        
        return wx.Size(width, height)


    def GetMenuFaceColour(self):
        " Returns the colour used for menu face. """

        return self.LightColour(wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE), 80)


    def GetAccelIndex(self, label):
        """
        Returns the menomonic index of the label.
        (e.g. 'lab&el' --> will result in 3 and labelOnly = label)
        """

        indexAccel = -1
        labelOnly = ""

        if label.find("&") < 0:
            return indexAccel, label

        indexAccel = label.index("&")
        labelOnly = label[0:indexAccel] + label[indexAccel+1:]

        return indexAccel, labelOnly
        

    def GetThemeBaseColour(self, useLightColours=True):
        """
        Returns the theme (Blue, Silver, Green etc.) base color, if no theme is active
        it return the active caption colour, lighter in 30%.
        """

        if not useLightColours and not self.IsDark(self.FrameColour()):
            return wx.NamedColor("GOLD")
        else:
            return self.LightColour(self.FrameColour(), 30)


    def GetAlignBuffer(self):
        """ Return the padding buffer for a text or bitmap. """

        return self._alignmentBuffer


    def SetMenuTheme(self, theme):
        """ Set the menu theme, possible values (Style2007, StyleXP). """
        
        self._menuTheme = theme


    def GetMenuTheme(self):
        """ Returns the menu theme. """

        return self._menuTheme


    def SetMS2007ButtonSunken(self, sunken):
        """ Sets MS 2007 button style sunken. """
        
        self._ms2007sunken = sunken


    def GetMS2007ButtonSunken(self):
        """ Returns the sunken flag for MS 2007 buttons. """

        return self._ms2007sunken


    def GetMBVerticalGradient(self):
        """ Returns True if the meun bar should be painted with vertical gradient. """

        return self._verticalGradient


    def SetMBVerticalGradient(self, v):
        """ Sets the menu bar gradient style. """

        self._verticalGradient = v


    def DrawMenuBarBorder(self, border):
        """ Enables menu border drawing (XP style only). """

        self._drowMBBorder = border
        

    def GetMenuBarBorder(self):
        """ Returns menu bar morder drawing flag. """

        return self._drowMBBorder


    def GetMenuBgFactor(self):
        """
        Gets the visibility depth of the menu in Metallic style.
        The higher the value, the menu bar will look more raised
        """

        return self._menuBgFactor        


    def DrawDragSash(self, rect):
        """ Draws resize sash. """
  
        dc = wx.ScreenDC()
        mem_dc = wx.MemoryDC()
        
        bmp = wx.EmptyBitmap(rect.width, rect.height)
        mem_dc.SelectObject(bmp)
        mem_dc.SetBrush(wx.WHITE_BRUSH)
        mem_dc.SetPen(wx.Pen(wx.WHITE, 1))
        mem_dc.DrawRectangle(0, 0, rect.width, rect.height)

        dc.Blit(rect.x, rect.y, rect.width, rect.height, mem_dc, 0, 0, wx.XOR)


    def TakeScreenShot(self, rect, bmp):
        """ Takes a screenshot of the screen at give pos & size (rect). """

        #Create a DC for the whole screen area
        dcScreen = wx.ScreenDC()

        #Create a Bitmap that will later on hold the screenshot image
        #Note that the Bitmap must have a size big enough to hold the screenshot
        #-1 means using the current default colour depth
        bmp = wx.EmptyBitmap(rect.width, rect.height)

        #Create a memory DC that will be used for actually taking the screenshot
        memDC = wx.MemoryDC()

        #Tell the memory DC to use our Bitmap
        #all drawing action on the memory DC will go to the Bitmap now
        memDC.SelectObject(bmp)

        #Blit (in this case copy) the actual screen on the memory DC
        #and thus the Bitmap
        memDC.Blit( 0, #Copy to this X coordinate
            0, #Copy to this Y coordinate
            rect.width, #Copy this width
            rect.height, #Copy this height
            dcScreen, #From where do we copy?
            rect.x, #What's the X offset in the original DC?
            rect.y  #What's the Y offset in the original DC?
            )

        #Select the Bitmap out of the memory DC by selecting a new
        #uninitialized Bitmap
        memDC.SelectObject(wx.NullBitmap)


    def DrawToolBarBg(self, dc, rect):
        """ Draws the toolbar background according to the active theme. """

        renderer = self._renderers[self.GetMenuTheme()]
        
        # Set background color if non given by caller
        renderer.DrawToolBarBg(dc, rect)


    def DrawMenuBarBg(self, dc, rect):
        """ Draws the menu bar background according to the active theme. """

        renderer = self._renderers[self.GetMenuTheme()]
        # Set background color if non given by caller
        renderer.DrawMenuBarBg(dc, rect)


    def SetMenuBarColour(self, scheme):
        """ Sets the menu bar color scheme to use. """

        self._menuBarColourScheme = scheme
        # set default colour
        if scheme in self._colorSchemeMap.keys():
            self._menuBarBgColour = self._colorSchemeMap[scheme]


    def GetMenuBarColourScheme(self):
        """ Returns the current colour scheme. """

        return self._menuBarColourScheme


    def GetMenuBarFaceColour(self):
        """ Returns the menu bar face colour. """

        return self._menuBarBgColour


    def GetMenuBarSelectionColour(self):
        """ Returns the menu bar selection color. """

        return self._menuBarSelColour


    def InitColours(self):
        """ Initialise the colour map. """

        self._colorSchemeMap = {"Default": wx.SystemSettings_GetColour(wx.SYS_COLOUR_3DFACE),
                                "Dark": wx.BLACK,
                                "Dark Olive Green": wx.NamedColour("DARK OLIVE GREEN"),
                                "Generic": wx.SystemSettings_GetColour(wx.SYS_COLOUR_ACTIVECAPTION)}


    def CreateGreyBitmap(self, bmp):
        """ Creates a grey bitmap image from bmp. """

        # save the file to PNG format
        if not bmp.SaveFile("__art_manager_tmp_png_file.png", wx.BITMAP_TYPE_PNG):
            return bmp

        greyBitmap = wx.Bitmap("__art_manager_tmp_png_file.png", wx.BITMAP_TYPE_PNG)
        os.remove("__art_manager_tmp_png_file.png")

        image = greyBitmap.ConvertToImage()
        image.SetOption(wx.IMAGE_OPTION_PNG_FORMAT, str(wx.PNG_TYPE_GREY_RED)) 
        image.SaveFile("__art_manager_tmp_png_file_GREY.png", wx.BITMAP_TYPE_PNG)
        gb = wx.Bitmap("__art_manager_tmp_png_file_GREY.png", wx.BITMAP_TYPE_PNG)
        os.remove("__art_manager_tmp_png_file_GREY.png")

        return gb


    def GetRaiseToolbar(self):
        """ Do Drop shadow under toolbar?. """

        return self._raiseTB


    def SetRaiseToolbar(self, rais):
        """ Enables/Disables toobar shadow drop. """

        self._raiseTB = rais


