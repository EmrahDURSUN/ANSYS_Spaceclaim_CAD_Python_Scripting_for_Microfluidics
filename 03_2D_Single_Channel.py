# 03_2D_Single_Channel
# Create the fluid domain of the single channel structure in two dimensions
# Emrah Dursun. 22/03/2023.
from SpaceClaim.Api.V22.Geometry import Point
import math

ClearAll()
Layers.DeleteEmpties()

# Get Input Parameters
periodicity=Parameters.Periodicity
channelWidth=Parameters.Channel_Width
# End Parameters

# Create Component and activate it
twoDSingleChannelComponent = ComponentHelper.CreateAtRoot("2D Single Channel")
ComponentHelper.SetActive(twoDSingleChannelComponent)

# modify and define variables
per=periodicity/2
cw=channelWidth/2 
splEn = 0.001
heigthCh = 2*periodicity
scaleDown = 0.9
curveScale = 1

def CurvedChannel (splEn, heigthCh, curveState):      
    # Set Sketch Plane
    result = ViewHelper.SetSketchPlane(Plane.PlaneXY)
    
    # Define Points for Sketch Splines
    startA = Point.Create(  -per+cw,   0,                    0)
    startAa= Point.Create(  -per+cw,   splEn ,               0)
    endA   = Point.Create(  -per-cw,   0,                    0)
    endAa  = Point.Create(  -per-cw,   splEn,                0)
    
    startB = Point.Create(  -cw*2,       heigthCh,             0)
    startBb= Point.Create(  -cw*2,       heigthCh-splEn,       0)
    endB   = Point.Create(  cw*2,        heigthCh,             0)
    endBb  = Point.Create(  cw*2,        heigthCh-splEn,       0)
    
    startC = Point.Create(  per-cw,     0,                   0)
    startCc= Point.Create(  per-cw,     splEn,               0)    
    endC   = Point.Create(  per+cw,     0,                   0)
    endCc  = Point.Create(  per+cw,     splEn,               0)    
    
    startD    = Point.Create( -splEn  ,   heigthCh*scaleDown,                 0)
    startDd  = Point.Create( -splEn  ,   (heigthCh-splEn)*scaleDown,      0)    
    endD     = Point.Create( splEn   ,    heigthCh*scaleDown,                0)
    endDd   = Point.Create( splEn   ,    (heigthCh-splEn)*scaleDown,     0)  
    
    # Sketch Straight Lines
    SketchLine.Create(startA, endA)
    SketchLine.Create(startB, endB)
    SketchLine.Create(startC, endC)
    
    # Sketch Spline 1st, FarLeft
    points = [endA, endAa, startBb, startB]
    SketchNurbs.CreateFrom3DPoints(False, points)
    
    # Sketch Spline 2nd, FarRight
    points = [endC, endCc, endBb, endB]
    SketchNurbs.CreateFrom3DPoints(False, points)
    
    # Sketch Spline 3rd, nearLeft
    points = [startA, startAa, startDd, startD]
    SketchNurbs.CreateFrom3DPoints(False, points)
    
    # Sketch Spline 4th nearRight
    points = [startC, startCc, endDd, endD]
    SketchNurbs.CreateFrom3DPoints(False, points)
    
    # Create Tangent Arc
    startSelPoint = SelectionPoint.Create(twoDSingleChannelComponent.Content.Curves[5], curveState)
    endSelPoint = SelectionPoint.Create(twoDSingleChannelComponent.Content.Curves[6], curveState)
    end = Point2D.Create( endSelPoint.Point.X, endSelPoint.Point.Y)
    options = SketchArcOptions()
    options.ArcSense = ArcSense.Normal
    result = SketchArc.CreateTangentArc( startSelPoint, end, options)
    
    # Solidify Sketch    
    ViewHelper.SetViewMode(InteractionMode.Solid, None)
    if curveScale is not 1:
        # Trim Sketch Curve
        selectedCurve = SelectionPoint.Create(twoDSingleChannelComponent.Content.Curves[1], curveState )
        TrimSketchCurve.Execute(  selectedCurve  )
        curveSelPoint = SelectionPoint.Create(twoDSingleChannelComponent.Content.Curves[0], curveState )
        result = TrimSketchCurve.Execute(curveSelPoint)
    
CurvedChannel(splEn, heigthCh, curveScale)
                      
Selection.Clear()
ComponentHelper.SetRootActive()
mode = ViewHelper.ViewProjection.Top
result = ViewHelper.SetProjection(mode)
ViewHelper.ZoomToEntity(PartSelection.Create(GetRootPart()))