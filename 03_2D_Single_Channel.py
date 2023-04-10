# 03_2D_Single_Channel
# Create the fluid domain of the single channel structure in two dimensions
# Emrah Dursun. 23/03/2023.
from SpaceClaim.Api.V22.Geometry import Point
import math

ClearAll()
Layers.DeleteEmpties()

# Get Input Parameters
periodicity=Parameters.Periodicity
channelWidth=Parameters.Channel_Width
scaleChannelHeight = Parameters.ScaleChannelHeight
innerCurveState = Parameters.InnerCurveState
etchHeight = Parameters.EtchHeight
# End Parameters

# Create Component and activate it
twoDSingleChannelComponent = ComponentHelper.CreateAtRoot("2D Single Channel")
ComponentHelper.SetActive(twoDSingleChannelComponent)

# modify and define variables
per=periodicity/2
cw=channelWidth/2 
splineDistance = periodicity * 2.4e-06
channelHeight = periodicity * scaleChannelHeight 
innerSplineScale = 0.9

def CurvedChannel (splineDistance, channelHeight, curveState):      
    # Set Sketch Plane
    result = ViewHelper.SetSketchPlane(Plane.PlaneXY)
    
    # Define Points for Sketch Splines
    startA = Point.Create(  -per+cw,   0,                    0)
    startAa= Point.Create(  -per+cw,   splineDistance ,               0)
    endA   = Point.Create(  -per-cw,   0,                    0)
    endAa  = Point.Create(  -per-cw,   splineDistance,                0)
    
    startB = Point.Create(  -cw*2,       channelHeight,             0)
    startBb= Point.Create(  -cw*2,       channelHeight-splineDistance,       0)
    endB   = Point.Create(  cw*2,        channelHeight,             0)
    endBb  = Point.Create(  cw*2,        channelHeight-splineDistance,       0)
    
    startC = Point.Create(  per-cw,     0,                   0)
    startCc= Point.Create(  per-cw,     splineDistance,               0)    
    endC   = Point.Create(  per+cw,     0,                   0)
    endCc  = Point.Create(  per+cw,     splineDistance,               0)    
    
    startD    = Point.Create( -splineDistance  ,   channelHeight*innerSplineScale,                 0)
    startDd  = Point.Create( -splineDistance  ,   (channelHeight-splineDistance)*innerSplineScale,      0)    
    endD     = Point.Create( splineDistance   ,    channelHeight*innerSplineScale,                0)
    endDd   = Point.Create( splineDistance   ,    (channelHeight-splineDistance)*innerSplineScale,     0)  
    
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
    
    # Sketch Arch between the inner spline curves
    startSelPoint = SelectionPoint.Create(twoDSingleChannelComponent.Content.Curves[5], innerCurveState)
    endSelPoint = SelectionPoint.Create(twoDSingleChannelComponent.Content.Curves[6], innerCurveState)
    end = Point2D.Create( endSelPoint.Point.X, endSelPoint.Point.Y)
    options = SketchArcOptions()
    options.ArcSense = ArcSense.Normal
    result = SketchArc.CreateTangentArc( startSelPoint, end, options)    
    
    # Solidify Sketch    
    ViewHelper.SetViewMode(InteractionMode.Solid, None)
   
    # Trim Sketch Curve
    numOfCurves = twoDSingleChannelComponent.Content.Curves.Count
    while numOfCurves > 0:
        selectedPoint = SelectionPoint.Create(twoDSingleChannelComponent.Content.Curves[numOfCurves-1], innerCurveState )
        result = TrimSketchCurve.Execute(selectedPoint)
        numOfCurves -= 1
        
    
CurvedChannel(splineDistance, channelHeight, innerCurveState)

Selection.Clear()
ComponentHelper.SetRootActive()
mode = ViewHelper.ViewProjection.Isometric
result = ViewHelper.SetProjection(mode)
ViewHelper.ZoomToEntity(PartSelection.Create(GetRootPart()))
