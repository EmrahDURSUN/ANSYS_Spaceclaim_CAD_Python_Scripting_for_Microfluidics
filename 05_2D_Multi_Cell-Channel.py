# 05_2D_Multi_Cell-Channel
# Create the fluid domain of the multi-cell and channel structures simultaneously in two dimensions. Then merge them.
# Emrah Dursun. 23/02/2023.
# Emrah Dursun. 07/04/2023.
from SpaceClaim.Api.V22.Geometry import Point
import math

Selection.Empty()
ClearAll()
Layers.DeleteEmpties()

# Get Input Parameters
periodicity=Parameters.Periodicity
subThick=Parameters.SubsThickness
hCr1=Parameters.ChromiumForAdhesion
hAu=Parameters.GoldLayer
#hCr2=Parameters.ChromiumForSurfacePassivationm
radius=Parameters.Radius
width=Parameters.Width 
angle=Parameters.Angle
oangle=Parameters.OpeningAngle
hEtch=Parameters.EtchHeight
dEtch=Parameters.EtchDepth
dnaT = Parameters.DNA
opRegion = Parameters.OpenRegion
channelWidth=Parameters.Channel_Width
numXElements=Parameters.X_direction_repeat
numYElements=Parameters.Y_direction_repeat
scaleChannelHeight = Parameters.ScaleChannelHeight
innerCurveState = Parameters.InnerCurveState
scaleFactorX=1
# End Parameters

# modify and define variables
per=periodicity/2
cw=channelWidth/2 
splineDistance = periodicity * 2.4e-06
channelHeight = periodicity * scaleChannelHeight 
innerSplineScale = 0.9

######################################################################
# Beginning Of MULTI Cell Fluid Domain
######################################################################
# Create Component and activate it
multiCellTwoDComp = ComponentHelper.CreateAtRoot("2D Multi Cell")
ComponentHelper.SetActive(multiCellTwoDComp)
 
# Allocate points and create a surface operation
def allocatePoints(distanceAwayFromOrigin, rotationBasedOrigin):
    # Create DatumPoint and rotate it
    selectedPoints = Selection.Create(DatumPointCreator.Create(Point.Create(0, MM(distanceAwayFromOrigin), 0)).CreatedPoint)
    move = Move.Rotate(selectedPoints, Line.Create(Point.Origin, Direction.DirZ), rotationBasedOrigin, MoveOptions())

# Create ring surface with given parameters
def createRingSurface(ring, nearPoint, farPoint, rotation):

    # Allocate points to create surface
    pointsDict = {1: [(nearPoint, rotation), (nearPoint, -rotation), (farPoint, rotation), (farPoint, -rotation)],
                   2: [(nearPoint, rotation), (nearPoint, -rotation), (farPoint, rotation), (farPoint, -rotation)]}

    for point in pointsDict[ring]:
        allocatePoints(point[0], point[1])

    # Get positions of DatumPoints
    start1 = multiCellTwoDComp.Content.DatumPoints[0].Position
    end1 = multiCellTwoDComp.Content.DatumPoints[1].Position
    start2 = multiCellTwoDComp.Content.DatumPoints[2].Position
    end2 = multiCellTwoDComp.Content.DatumPoints[3].Position
    
    # Delete DatumPoints
    while multiCellTwoDComp.Content.DatumPoints.Count > 0:
        multiCellTwoDComp.Content.DatumPoints[0].Delete()
    
    # Create curves and surface
    curves = List[ITrimmedCurve]()
    curves.Add(CurveSegment.CreateArc(Point.Origin, start1, end1, -Direction.DirZ))
    curves.Add(CurveSegment.CreateArc(Point.Origin, start2, end2, -Direction.DirZ))
    curves.Add(CurveSegment.Create(start1, start2))
    curves.Add(CurveSegment.Create(end1, end2))
        
    designResult = PlanarBody.Create(Plane.PlaneXY, curves)
    designBody1 = designResult.CreatedBody.SetName('Ring' + str(ring))
  
# Call Create ring surfaces with given parameters
createRingSurface(1, radius, radius + width, DEG(180) + angle)
createRingSurface(2, radius, radius + width, DEG(180) - angle - oangle)

# Create a rectangular channel surface and set its name
originRectang=Point.Create(-channelWidth/2, -periodicity/2,0)
result=RectangularSurface.Create( channelWidth, periodicity, originRectang)

# Merge all surfaces and rename
num = multiCellTwoDComp.Content.Bodies.Count-1
t=0
while t < num:
    selectionTarget = BodySelection.Create(multiCellTwoDComp.Content.Bodies[num-t])
    selectionOthers = BodySelection.Create(multiCellTwoDComp.Content.Bodies[num-1-t])
    result = Combine.Merge( selectionTarget , selectionOthers)
    t+=1
RenameObject.Execute(BodySelection.Create(multiCellTwoDComp.Content.Bodies[0]), 'SingleCellFluidDomain')

# First make a copy and then move that copy along the translation vector direction  
def CopyAndTranslate(body, translation):
    result = Copy.Execute(Selection.Create(body))
    if (result.Success == True):
        newBody = result.CreatedObjects[0]        
        Move.Translate(Selection.Create(newBody), translation, MoveOptions())
        RenameObject.Execute(Selection.Create(newBody),'Merged_Cell')
        return newBody

# Add Offset to base body
offSetY = ( numYElements * per ) - per
offSetX = ( numXElements * per ) - per
baseBody = multiCellTwoDComp.Content.Bodies[0]
selection = BodySelection.Create(baseBody)
directionY = -Direction.DirY
directionX = -Direction.DirX
options = MoveOptions()
options.MaintainOrientation = True
result = Move.Translate(selection, directionY, offSetY, options) 
result = Move.Translate(selection, directionX, offSetX, options)

# Make a body list
bodyList = List[IDocObject]()
bodyList.Add(baseBody)

# Run a loop to create cell array on Y axis
y = 0
while y< numYElements:
    translationY = Vector.Create ( 0, y*periodicity , 0 )
    newBody = CopyAndTranslate(baseBody, translationY)
    bodyList.Add(newBody)
    y = y + 1
#Delete  orginal reference body
multiCellTwoDComp.Content.Bodies[0].Delete()

# Merge Bodies created on Y direction, they are touching eachother so they shall be merge  01:15,06 min
while multiCellTwoDComp.Content.Bodies.Count > 1:    
    selectionT = BodySelection.Create(multiCellTwoDComp.Content.Bodies)
    result = Combine.Merge(selectionT)

# Run a loop to create cell array on X axis
baseMergedBody = multiCellTwoDComp.Content.Bodies[0]
x = 0
while x < numXElements:
    translationX = Vector.Create( x*periodicity, 0, 0 )
    newBody = CopyAndTranslate(baseMergedBody, translationX)
    bodyList.Add(newBody)
    x = x + 1
#Delete  orginal reference body
multiCellTwoDComp.Content.Bodies[0].Delete()


######################################################################
# End Of MULTI Cell Fluid Domain
######################################################################

# Create Component and activate it
multiChannelComp = ComponentHelper.CreateAtRoot("2D Multiple Channel")
ComponentHelper.SetActive(multiChannelComp)

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



######################################################################
# End Of MULTI Channels
######################################################################

# Create Datum Plane
result = DatumPlaneCreator.Create(Point.Origin, Direction.DirY)

# Mirror Multi Channels respect to created Plane
selection = BodySelection.Create(multiChannelComp.Content.Bodies[0])
mirrorPlane = Selection.Create(multiChannelComp.Content.DatumPlanes[0])
options = MirrorOptions()
result = Mirror.Execute(selection, mirrorPlane, options)
# EndBlock

# Change Datum Plane Object Visibility
selection =Selection.Create(multiChannelComp.Content.DatumPlanes[0])
visibility = VisibilityType.Hide
inSelectedView = False
faceLevel = False
ViewHelper.SetObjectVisibility(selection, visibility, inSelectedView, faceLevel)
# EndBlock

######################################################################
# Create a componet and move all bodies in it and Merge them
multiCellChannelComp = ComponentHelper.CreateAtRoot("Multi-Cell-Channel")

sel1 = Selection.Create(multiCellTwoDComp.Content.Bodies)
sel2  = Selection.Create(multiChannelComp.Content.Bodies)
selectedBodies = Selection.SelectAll(sel1 + sel2)
result = ComponentHelper.MoveBodiesToComponent ( selectedBodies ,multiCellChannelComp, False , None)
multiChannelComp.Delete()
multiCellTwoDComp.Delete()

selectedBodies = BodySelection.Create(multiCellChannelComp.Content.Bodies)
result = Combine.Merge(selectedBodies)

######################################################################
# End Of MULTI CELL CHANNEL
######################################################################

Selection.Clear()
ComponentHelper.SetRootActive()
mode = ViewHelper.ViewProjection.Isometric
result = ViewHelper.SetProjection(mode)
ViewHelper.ZoomToEntity(PartSelection.Create(GetRootPart()))
# EndBlock