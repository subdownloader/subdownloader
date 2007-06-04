# --------------------------------------------------------------------------- #
# PIECTRL Control wxPython IMPLEMENTATION
# Python Code By:
#
# Andrea Gavana, @ 31 Oct 2005
# Latest Revision: 31 Oct 2005, 21.50 CET
#
#
# TODO List/Caveats
#
# 1. Maybe Integrate The Very Nice PyOpenGL Implementation Of A PieChart Coded
#    By Will McGugan?
#
# 2. Not Tested On Other Platforms, Only On Windows 2000/XP, With Python 2.4.1
#    And wxPython 2.6.1.0
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

PieCtrl/ProgressPie Are Simple Classes That Reproduce The Behavior Of A Pie
Chart. They Use Only Pure wxPython Classes/Methods, Without External Dependencies.
PieCtrl Is Somewhat A "Static" Control, That You May Create In Order To Display
A Simple Pie Chart On A wx.Panel Or Similar. ProgressPie Tries To Emulate The
Behavior Of wx.ProgressDialog, But Using A Pie Chart Instead Of A Gauge.


Usage:

An Example Of Use Of PieCtrl Is As Follows:

# Create A Simple PieCtrl With 3 Sectors
MyPie = PieCtrl(panel, -1, wx.DefaultPosition, wx.Size(180,270))

part = PiePart()

part.SetLabel("SeriesLabel_1")
part.SetValue(300)
part.SetColour(wx.Colour(200, 50, 50))
MyPie._series.append(part)

part = PiePart()        

part.SetLabel("Series Label 2")
part.SetValue(200)
part.SetColour(wx.Colour(50, 200, 50))
MyPie._series.append(part)

part = PiePart()

part.SetLabel("HelloWorld Label 3")
part.SetValue(50)
part.SetColour(wx.Colour(50, 50, 200))
MyPie._series.append(part)

An Example Of Use Of ProgressPie Is As Follows:

# Create A ProgressPie
MyProgressPie = ProgressPie(panel, 100, 50, -1, wx.DefaultPosition,
                            wx.Size(180, 200), wx.SIMPLE_BORDER)

MyProgressPie.SetBackColour(wx.Colour(150, 200, 255))
MyProgressPie.SetFilledColour(wx.Colour(255, 0, 0))
MyProgressPie.SetUnfilledColour(wx.WHITE)
MyProgressPie.SetHeight(20)
        
For The Full Listing Of The Input Parameters, See The PieCtrl __init__()
Method.


Methods And Settings:

With PieCtrl You Can:

- Create A PieCtrl With Different Sectors;
- Set The Sector Values, Colours And Labels;
- Assign A Legend To The PieCtrl;
- Use An Image As The PieCtrl Background;
- Change The Vertical Rotation (Perspective) Of The PieCtrl;
- Show/Hide The Segment Edges.

For More Info On Methods And Initial Styles, Please Refer To The __init__()
Method For PieCtrl Or To The Specific Functions.


PieCtrl Control Is Freeware And Distributed Under The wxPython License. 

Latest Revision: Andrea Gavana @ 31 Oct 2005, 21.50 CET

"""


#----------------------------------------------------------------------
# Beginning Of PIECTRL wxPython Code
#----------------------------------------------------------------------


import wx

from math import pi, sin, cos

#----------------------------------------------------------------------
# Class PieCtrlLegend
# This Class Handles The Legend For The Classic PieCtrl.
#----------------------------------------------------------------------

class PieCtrlLegend(wx.Window):

    def __init__(self, parent, title, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0):
        """ Default Class Constructor.

        No Special Parameters Are Required, Only The Standard wxPython Ones.        
        """
        
        wx.Window.__init__(self, parent, id, pos, size, style)

        self._title = title
        self._istransparent = False
        self._horborder = 5
        self._verborder = 5
        self._titlecolour = wx.Colour(0, 0, 127)
        self._labelcolour = wx.BLACK
        self._backcolour = wx.Colour(255, 255, 0)
        self._backgroundDC = wx.MemoryDC()
        self._parent = parent

        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x: None)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        

    def SetTransparent(self, value=False):
        """ Toggles The Legend Transparency (Visibility). """

        self._istransparent = value
        self.Refresh()


    def RecreateBackground(self, parentdc):
        """ Recreates The Legend Background. """

        w, h = self.GetSize()
        self._background = wx.EmptyBitmap(w, h)
        self._backgroundDC.SelectObject(self._background)
        
        if self.IsTransparent():
                
            self._backgroundDC.Blit(0, 0, w, h, parentdc, self.GetPosition().x,
                                    self.GetPosition().y)

        else:

            self._backgroundDC.SetBackground(wx.Brush(self._backcolour))
            self._backgroundDC.Clear()      

        self.Refresh()


    def SetHorizontalBorder(self, value):
        """ Sets The Legend's Horizontal Border. """

        self._horborder = value
        self.Refresh()


    def GetHorizontalBorder(self):
        """ Returns The Legend's Horizontal Border. """

        return self._horborder


    def SetVerticalBorder(self, value):
        """ Sets The Legend's Vertical Border. """

        self._verborder = value
        self.Refresh()


    def GetVerticalBorder(self):
        """ Returns The Legend's Vertical Border. """

        return self._verborder        


    def SetLabelColour(self, colour):
        """ Sets The Legend Label Colour. """

        self._labelcolour = colour
        self.Refresh()


    def GetLabelColour(self):
        """ Returns The Legend Label Colour. """

        return self._labelcolour
    

    def SetLabelFont(self, font):
        """ Sets The Legend Label Font. """

        self._labelfont = font
        self.Refresh()


    def GetLabelFont(self):
        """ Returns The Legend Label Font. """

        return self._labelfont

    
    def SetBackColour(self, colour):
        """ Sets The Legend Background Colour. """

        self._backcolour = colour
        self.Refresh()
        

    def GetBackColour(self):
        """ Returns The Legend Background Colour. """

        return self._backcolour

    
    def IsTransparent(self):
        """ Returns Whether The Legend Background Is Transparent Or Not. """

        return self._istransparent


    def OnPaint(self, event):
        """ Handles The wx.EVT_PAINT Event For The Legend. """

        pdc = wx.PaintDC(self)
        
        w, h = self.GetSize()
        bmp = wx.EmptyBitmap(w, h)
        mdc = wx.MemoryDC()
        mdc.SelectObject(bmp)
        
        if self.IsTransparent():
        
            parentdc = wx.ClientDC(self.GetParent())
            mdc.Blit(0, 0, w, h, self._backgroundDC, 0, 0)
        
        else:
        
            mdc.SetBackground(wx.Brush(self._backcolour))
            mdc.Clear()
        
        dy = self._verborder
        mdc.SetFont(self._labelfont)
        mdc.SetTextForeground(self._labelcolour)
        maxwidth = 0
        
        for ii in xrange(len(self._parent._series)):
        
            tw, th = mdc.GetTextExtent(self._parent._series[ii].GetLabel())
            mdc.SetBrush(wx.Brush(self._parent._series[ii].GetColour()))
            mdc.DrawCircle(self._horborder+5, dy+th/2, 5)
            mdc.DrawText(self._parent._series[ii].GetLabel(), self._horborder+15, dy)
            dy = dy + th + 3
            maxwidth = max(maxwidth, int(2*self._horborder+tw+15))
        
        dy = dy + self._verborder
        if w != maxwidth or h != dy:
            self.SetSize((maxwidth, dy))
            
        pdc.Blit(0, 0, w, h, mdc, 0, 0)


#----------------------------------------------------------------------
# Class PiePart
# This Class Handles The Legend Segments Properties, Such As Value,
# Colour And Label.
#----------------------------------------------------------------------

class PiePart:

    def __init__(self, value=0, colour=wx.BLACK, label=""):
        """ Default Class Constructor. """
        
        self._value = value
        self._colour = colour
        self._label = label


    def SetValue(self, value):
        """ Sets Segment Absolute Value. """

        self._value = value


    def GetValue(self):
        """ Returns Segment Absolute Value. """
        
        return self._value


    def SetColour(self, colour):
        """ Sets Segment Colour. """

        self._colour = colour


    def GetColour(self):
        """ Returns Segment Colour. """

        return self._colour


    def SetLabel(self, label):
        """ Sets Segment Label. """

        self._label = label


    def GetLabel(self):
        """ Returns Segment Label. """

        return self._label
    

#----------------------------------------------------------------------
# Class PieCtrl
# This Is The Main PieCtrl Implementation, Used Also By ProgressPie.
#----------------------------------------------------------------------

class PieCtrl(wx.Window):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=0, name="PieCtrl"):
        """ Default Class Constructor.

        No Special Parameters Are Required, Only The Standard wxPython Ones.        
        """
        
        wx.Window.__init__(self, parent, id, pos, size, style, name)
        
        self._angle = pi/12
        self._rotationangle = 0
        self._height = 10
        self._background = wx.NullBitmap
        self._canvasbitmap = wx.EmptyBitmap(1, 1)
        self._canvasDC = wx.MemoryDC()
        self._backcolour = wx.WHITE
        self._showedges = True
        self._series = []

        self.Bind(wx.EVT_ERASE_BACKGROUND, lambda x: None)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.RecreateCanvas()
        self._legend = PieCtrlLegend(self, "PieCtrl", -1, wx.Point(10,10), wx.Size(100,75))


    def SetBackground(self, bmp):
        """ Sets The PieCtrl Background Image. """

        self._background = bmp
        self.Refresh()


    def GetBackground(self):
        """ Returns The PieCtrl Background Image. """
        
        return self._background
    

    def OnSize(self, event):
        """ Handles The wx.EVT_SIZE Event For PieCtrl. """
        
        self.RecreateCanvas()
        self.Refresh()
        event.Skip()
        

    def RecreateCanvas(self):
        """ Recreates The PieCtrl Container (Canvas). """

        self._canvasbitmap = wx.EmptyBitmap(self.GetSize().GetWidth(),
                                            self.GetSize().GetHeight())
        self._canvasDC.SelectObject(self._canvasbitmap)


    def GetPartAngles(self):
        """ Returns The Angles Associated To All Segments. """

        angles = []
        total = 0.0

        for ii in xrange(len(self._series)):
            total = total + self._series[ii].GetValue()

        current = 0.0
        angles.append(current)
        
        for ii in xrange(len(self._series)):
        
            current = current + self._series[ii].GetValue()
            angles.append(360.0*current/total)

        return angles
    

    def SetAngle(self, angle):
        """ Sets The Orientation Angle For PieCtrl. """

        if angle < 0:
            angle = 0
        if angle > pi/2:
            angle = pi/2
            
        self._angle = angle
        self.Refresh()


    def GetAngle(self):
        """ Returns The Orientation Angle For PieCtrl. """
        
        return self._angle
    
            
    def SetRotationAngle(self, angle):
        """ Sets The Angle At Which The First Sector Starts. """

        if angle < 0:
            angle = 0
        if angle > 2*pi:
            angle = 2*pi
            
        self._rotationangle = angle
        self.Refresh()


    def GetRotationAngle(self):
        """ Returns The Angle At Which The First Sector Starts. """

        return self._rotationangle
    

    def SetShowEdges(self, value=True):
        """ Sets Whether The PieCtrl Edges Are Visble Or Not. """

        self._showedges = value
        self.Refresh()


    def GetShowEdges(self):
        """ Returns Whether The PieCtrl Edges Are Visble Or Not. """

        return self._showedges
    

    def SetBackColour(self, colour):
        """ Sets The PieCtrl Background Colour. """

        self._backcolour = colour
        self.Refresh()


    def GetBackColour(self):
        """ Returns The PieCtrl Background Colour. """
        
        return self._backcolour

    
    def SetHeight(self, value):
        """ Sets The Height (In Pixels) Of The PieCtrl. """

        self._height = value


    def GetHeight(self):
        """ Returns The Height (In Pixels) Of The PieCtrl. """

        return self._height
    

    def GetLegend(self):
        """ Returns The PieCtrl Legend. """

        return self._legend
    

    def DrawParts(self, dc, cx, cy, w, h):
        """ Here We Draw The PieCtrl External Edges. """

        angles = self.GetPartAngles()
        oldpen = dc.GetPen()
        
        if self._showedges:
            dc.SetPen(wx.BLACK_PEN)
            
        for ii in xrange(len(angles)):
        
            if ii > 0:
                            
                if not self._showedges:
                    dc.SetPen(wx.Pen(self._series[ii-1].GetColour()))
                    
                dc.SetBrush(wx.Brush(self._series[ii-1].GetColour()))

                if angles[ii-1] != angles[ii]:
                    dc.DrawEllipticArc(0, int((1-sin(self._angle))*(h/2)+cy), w,
                                       int(h*sin(self._angle)),
                                       angles[ii-1]+self._rotationangle/pi*180,
                                       angles[ii]+self._rotationangle/pi*180)           
            
        
        if len(self._series) == 1:
        
            dc.SetBrush(wx.Brush(self._series[0].GetColour()))
            dc.DrawEllipticArc(0, int((1-sin(self._angle))*(h/2)+cy), w,
                               int(h*sin(self._angle)), 0, 360)
        
        dc.SetPen(oldpen)


    def Draw(self, pdc):
        """ Here We Draw All The Sectors Of PieCtrl. """

        w, h = self.GetSize()
        
        self._canvasDC.BeginDrawing()   
        self._canvasDC.SetBackground(wx.WHITE_BRUSH)
        self._canvasDC.Clear()
        
        if self._background != wx.NullBitmap:
        
            for ii in xrange(0, w, self._background.GetWidth()):
            
                for jj in xrange(0, h, self._background.GetHeight()):
                
                    self._canvasDC.DrawBitmap(self._background, ii, jj)
                
        else:
        
            self._canvasDC.SetBackground(wx.Brush(self._backcolour))
            self._canvasDC.Clear()
            
        if len(self._series) > 0:

            if self._angle <= pi/2:
                self.DrawParts(self._canvasDC, 0, int(self._height*cos(self._angle)), w, h)             
            else:
                self.DrawParts(self._canvasDC, 0, 0, w, h)

            points = [[0, 0]]*4
            triangle = [[0, 0]]*3
            self._canvasDC.SetPen(wx.Pen(wx.BLACK))
            angles = self.GetPartAngles()
            angleindex = 0
            self._canvasDC.SetBrush(wx.Brush(wx.Colour(self._series[angleindex].GetColour().Red(),
                                                       self._series[angleindex].GetColour().Green(),
                                                       self._series[angleindex].GetColour().Blue())))       
            changeangle = False
            x = 0.0

            while x <= 2*pi:

                changeangle = False
                
                if angleindex < len(angles):
                
                    if x/pi*180.0 >= angles[angleindex+1]:
                                    
                        changeangle = True              
                        x = angles[angleindex+1]*pi/180.0                     
                    
                points[0] = points[1]
                px = int(w/2*(1+cos(x+self._rotationangle)))
                py = int(h/2-sin(self._angle)*h/2*sin(x+self._rotationangle)-1)
                points[1] = [px, py]
                triangle[0] = [w / 2, h / 2]
                triangle[1] = points[0]
                triangle[2] = points[1]
                
                if x > 0:
                
                    self._canvasDC.SetBrush(wx.Brush(self._series[angleindex].GetColour()))
                    oldPen = self._canvasDC.GetPen()
                    self._canvasDC.SetPen(wx.Pen(self._series[angleindex].GetColour()))
                    self._canvasDC.DrawPolygon([wx.Point(pts[0], pts[1]) for pts in triangle])
                    self._canvasDC.SetPen(oldPen)
                
                if changeangle:
                            
                    angleindex = angleindex + 1         

                x = x + 0.05

            x = 2*pi                
            points[0] = points[1]    
            px = int(w/2 * (1+cos(x+self._rotationangle)))
            py = int(h/2-sin(self._angle)*h/2*sin(x+self._rotationangle)-1)
            points[1] = [px, py]
            triangle[0] = [w / 2, h / 2]
            triangle[1] = points[0]
            triangle[2] = points[1]
            
            self._canvasDC.SetBrush(wx.Brush(self._series[angleindex].GetColour()))
            oldPen = self._canvasDC.GetPen()
            self._canvasDC.SetPen(wx.Pen(self._series[angleindex].GetColour()))
            self._canvasDC.DrawPolygon([wx.Point(pts[0], pts[1]) for pts in triangle])
            
            self._canvasDC.SetPen(oldPen)
            angleindex = 0

            x = 0.0

            while x <= 2*pi:

                changeangle = False
                if angleindex < len(angles):
                
                    if x/pi*180 >= angles[angleindex+1]:
                                    
                        changeangle = True              
                        x = angles[angleindex+1]*pi/180                     
                    
                points[0] = points[1]
                points[3] = points[2]
                px = int(w/2 * (1+cos(x+self._rotationangle)))
                py = int(h/2-sin(self._angle)*h/2*sin(x+self._rotationangle)-1)
                points[1] = [px, py]
                points[2] = [px, int(py+self._height*cos(self._angle))]

                if w > 0:

                    curColour = wx.Colour(self._series[angleindex].GetColour().Red()*(1.0-float(px)/w),
                                          self._series[angleindex].GetColour().Green()*(1.0-float(px)/w),
                                          self._series[angleindex].GetColour().Blue()*(1.0-float(px)/w))
                    
                    if not self._showedges:
                        self._canvasDC.SetPen(wx.Pen(curColour))
                        
                    self._canvasDC.SetBrush(wx.Brush(curColour))            
                        
                if sin(x+self._rotationangle) < 0 and sin(x-0.05+self._rotationangle) <= 0 and x > 0:
                    self._canvasDC.DrawPolygon([wx.Point(pts[0], pts[1]) for pts in points])
                    
                if changeangle:
                            
                    angleindex = angleindex + 1         

                x = x + 0.05
                
            x = 2*pi    
            points[0] = points[1]
            points[3] = points[2]
            px = int(w/2 * (1+cos(x+self._rotationangle)))
            py = int(h/2-sin(self._angle)*h/2*sin(x+self._rotationangle)-1)
            points[1] = [px, py]
            points[2] = [px, int(py+self._height*cos(self._angle))]
            
            if w > 0:
            
                curColour = wx.Colour(self._series[angleindex].GetColour().Red()*(1.0-float(px)/w),
                                          self._series[angleindex].GetColour().Green()*(1.0-float(px)/w),
                                          self._series[angleindex].GetColour().Blue()*(1.0-float(px)/w))
                                          
                if not self._showedges:
                    self._canvasDC.SetPen(wx.Pen(curColour))
                    
                self._canvasDC.SetBrush(wx.Brush(curColour))

            if sin(x+self._rotationangle) < 0 and sin(x-0.05+self._rotationangle) <= 0:
                self._canvasDC.DrawPolygon([wx.Point(pts[0], pts[1]) for pts in points])
            
            if self._angle <= pi/2:
                self.DrawParts(self._canvasDC, 0, 0, w, h)
            else:
                self.DrawParts(self._canvasDC, 0, int(self._height*cos(self._angle)), w, h)
    
        self._canvasDC.EndDrawing()

        pdc.Blit(0, 0, w, h, self._canvasDC, 0, 0)  
        self._legend.RecreateBackground(self._canvasDC)


    def OnPaint(self, event):
        """ Handles The wx.EVT_PAINT Event For PieCtrl. """

        pdc = wx.PaintDC(self)
        self.Draw(pdc)


#----------------------------------------------------------------------
# Class ProgressPie
# This Is The Main ProgressPie Implementation. Is Is A Subclassing Of
# PieCtrl, With 2 Sectors.
#----------------------------------------------------------------------

class ProgressPie(PieCtrl):

    def __init__(self, parent, maxvalue, value, id=wx.ID_ANY,
                 pos=wx.DefaultPosition, size=wx.DefaultSize, style=0):
        """ Default Class Constructor.

        No Special Parameters Are Required, Only The Standard wxPython Ones.        
        """
        
        PieCtrl.__init__(self, parent, id, pos, size, style)

        self._maxvalue = maxvalue
        self._value = value
        self.GetLegend().Hide()

        self._filledcolour = wx.Colour(0, 0, 127)
        self._unfilledcolour = wx.WHITE
        part = PiePart()
        part.SetColour(self._filledcolour)
        a = min(float(value), maxvalue)
        part.SetValue(max(a, 0.0))
        self._series.append(part)
        part = PiePart()
        part.SetColour(self._unfilledcolour)
        part.SetValue(max(0.0, maxvalue-part.GetValue()))
        self._series.append(part)


    def SetValue(self, value):
        """ Sets The ProgressPie Value. """

        self._value = min(value, self._maxvalue)
        self._series[0].SetValue(max(self._value, 0.0))
        self._series[1].SetValue(max(self._maxvalue-self._value, 0.0))
        self.Refresh()


    def GetValue(self):
        """ Returns The ProgressPie Value. """
        
        return self._value

    
    def SetMaxValue(self, value):
        """ Sets The ProgressPie Maximum Value. """

        self._maxvalue = value
        self._value = min(self._value, self._maxvalue)
        self._series[0].SetValue(max(self._value, 0.0))
        self._series[1].SetValue(max(self._maxvalue-self._value, 0.0))
        self.Refresh()


    def GetMaxValue(self):
        """ Returns The ProgressPie Maximum Value. """

        return self._maxvalue
    

    def SetFilledColour(self, colour):
        """ Sets The Colour That Progressively Fills The ProgressPie. """

        self._filledcolour = colour
        self._series[0].SetColour(self._filledcolour)
        self.Refresh()


    def SetUnfilledColour(self, colour):
        """ Sets The Colour That Is Filled. """

        self._unfilledcolour= colour
        self._series[1].SetColour(self._unfilledcolour)
        self.Refresh()


    def GetFilledColour(self):
        """ Returns The Colour That Progressively Fills The ProgressPie. """

        return self._filledcolour


    def GetUnfilledColour(self):
        """ Sets The Colour That Is Filled. """

        return self._unfilledcolour

