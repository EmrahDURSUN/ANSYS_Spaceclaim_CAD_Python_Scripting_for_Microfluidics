# 04_2D_Multi_Channel
# Create the fluid domain of the multi-channel structure in two dimensions
# Emrah Dursun. 23/02/2023.
# Emrah Dursun. 07/04/2023.
from SpaceClaim.Api.V22.Geometry import Point
import math

#ClearAll()
#Layers.DeleteEmpties()

# Get Input Parameters
periodicity=Parameters.Periodicity
subThick=Parameters.SubsThickness
radius=Parameters.Radius
width=Parameters.Width 
angle=Parameters.Angle
oangle=Parameters.OpeningAngle
hEtch=Parameters.EtchHeight
dEtch=Parameters.EtchDepth
dnaT = Parameters.DNA
opRegion = Parameters.OpenRegion
channelWidth=Parameters.Channel_Width
numXElements =Parameters.X_direction_repeat
numYElements =Parameters.Y_direction_repeat
scaleChannelHeight = Parameters.ScaleChannelHeight
innerCurveState = Parameters.InnerCurveState
# End Parameters

# Create Component and activate it
multiChannelComp = ComponentHelper.CreateAtRoot("2D Multiple Channel")
ComponentHelper.SetActive(multiChannelComp)

# modify and define variables
per=periodicity/2
cw=channelWidth/2 
splineDistance = periodicity * 2.4e-06
channelHeight = periodicity * scaleChannelHeight 
innerSplineScale = 0.9

# DEFINE THE FUNCTIONS
# Declare a function to copy, translate along one dirction
def CopyAndTranslate_Along(body, translation):   
    result = Copy.Execute(body)    
    if (result.Success == True):
        newBody = result.CreatedObjects[0]        
        Move.Translate(Selection.Create(newBody), translation, MoveOptions())
        RenameObject.Execute(Selection.Create(newBody), 'Chanbel Along X '+k.ToString())
        return newBody

# Declare a function to copy, translate and scale the base body along two direction
def CopyAndTranslate_Scale(body, translation, scaleFactorX, scaleFactorY):
    result = Copy.Execute(Selection.Create(body))
    if (result.Success == True):
        newBody = result.CreatedObjects[0]        
        Move.Translate(Selection.Create(newBody), translation, MoveOptions())        
        position=multiChannelComp.Content.Bodies[t+1].Edges[0].GetChildren[ICurvePoint]()[0].Position
        selectionScale=Selection.Create(result.CreatedObjects[0])
        #Scale along x axis but, not recommended to play wirh scaleFactorX; so it can mis allign the cell connections
        result = Scale.Execute(selectionScale,Point.Create(position.X, position.Y, position.Z), Direction.DirX ,scaleFactorX)
        #Scale along Y axis; change scaleFactorY to scale input channel total lenght
        result = Scale.Execute(selectionScale,Point.Create(position.X, position.Y, position.Z), Direction.DirY ,scaleFactorY)
        RenameObject.Execute(Selection.Create(newBody), 'Layer'+t.ToString())
        return newBody

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
    startSelPoint = SelectionPoint.Create(multiChannelComp.Content.Curves[5], innerCurveState)
    endSelPoint = SelectionPoint.Create(multiChannelComp.Content.Curves[6], innerCurveState)
    end = Point2D.Create( endSelPoint.Point.X, endSelPoint.Point.Y)
    options = SketchArcOptions()
    options.ArcSense = ArcSense.Normal
    result = SketchArc.CreateTangentArc( startSelPoint, end, options)    
    
    # Solidify Sketch    
    ViewHelper.SetViewMode(InteractionMode.Solid, None)
   
    # Trim Sketch Curve
    numOfCurves = multiChannelComp.Content.Curves.Count
    while numOfCurves > 0:
        selectedPoint = SelectionPoint.Create(multiChannelComp.Content.Curves[numOfCurves-1], innerCurveState )
        result = TrimSketchCurve.Execute(selectedPoint)
        numOfCurves -= 1
        
CurvedChannel(splineDistance, channelHeight, innerCurveState)
#### End Of Single Channel ####

# Add offset to the Base Channel 
offSetYdirection = ( ( numYElements / 2 ) * periodicity )
offSetXdirection = ( ( ( numXElements / 2 ) -1 ) * periodicity )
baseBody = multiChannelComp.Content.Bodies[0]
selection = BodySelection.Create(baseBody)
directionY = Direction.DirY
directionX = -Direction.DirX
options = MoveOptions()
options.MaintainOrientation = True
result = Move.Translate(selection, directionY, offSetYdirection, options)
result = Move.Translate(selection, directionX, offSetXdirection, options)

# Make a body list
bodyList = List[IDocObject]()
bodyList.Add(baseBody)

# Run a loop to make the steps along the layer height, layer numbers change respect to number of cell, under this section one can also adjust to scale along y-axis
scaleFactorY = 1
scaleFactorX = 1
t = 0
numChannelLayers=math.log(numXElements,2)
while t < numChannelLayers:
    Xoff = math.pow (2, t ) -1
    Yoff = math.pow (2, t ) -1
    translation = Vector.Create( Xoff *(( (periodicity+channelWidth) / 2) - channelWidth)  ,  channelHeight * Yoff,  0 )    
    newBody = CopyAndTranslate_Scale( baseBody, translation, scaleFactorX, scaleFactorY )
    bodyList.Add( newBody )
    scaleFactorX *=2
    scaleFactorY *=2
    t = t + 1

# run nested to loop to create x cell for each layer
m = numXElements /2
k=0
n=0
while n < numChannelLayers:
    stringName =str('Layer'+n.ToString())
    selectionO = Selection.CreateByNames(stringName)
    k=0
    while k<m:
        translation = Vector.Create( math.pow(2,n) * k * 2 * periodicity, 0 ,0)
        newBody = CopyAndTranslate_Along(selectionO, translation)
        bodyList.Add(newBody)
        k+=1    
    m/=2
    Delete.Execute(selectionO)    
    n+=1    

multiChannelComp.Content.Bodies[0].Delete()

## Takes long time to combine
## Merge Bodies created on Y direction, they are touching eachother so they shall be merge  
#while multiChannelComp.Content.Bodies.Count > 1:    
#    selectionT = BodySelection.Create(multiChannelComp.Content.Bodies)
#    result = Combine.Merge(selectionT)

# Maybe this method faster
numberOfUnmergedBodies = multiChannelComp.Content.Bodies.Count-1
while numberOfUnmergedBodies > 0:
    mainBody = BodySelection.Create(multiChannelComp.Content.Bodies[numberOfUnmergedBodies])
    secondaryBodies = BodySelection.Create(multiChannelComp.Content.Bodies[numberOfUnmergedBodies-1])
    result = Combine.Merge(mainBody, secondaryBodies)
    numberOfUnmergedBodies -=1
    if numberOfUnmergedBodies == 0:
        RenameObject.Execute(BodySelection.Create(multiChannelComp.Content.Bodies[0]), 'Merged Channels')
        break


# Ending Arrangements
Selection.Clear()
ComponentHelper.SetRootActive()
mode = ViewHelper.ViewProjection.Isometric
result = ViewHelper.SetProjection(mode)
ViewHelper.ZoomToEntity(PartSelection.Create(GetRootPart()))