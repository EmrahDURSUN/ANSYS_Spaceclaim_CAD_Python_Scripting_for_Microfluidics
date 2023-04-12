# 07 2D Final
# Create the combined final fluid domain structures in two dimensions.
# Emrah Dursun. 02/03/2023.
# Emrah Dursun. 10/04/2023.
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
hCr2=Parameters.ChromiumForSurfacePassivation
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
fluidChipLength = Parameters.FluidChip_Length
fluidChipWidth = Parameters.FluidChip_Width
scaleChannelHeight = Parameters.ScaleChannelHeight
innerCurveState = Parameters.InnerCurveState
InnerCurveStateForEntry = Parameters.InnerCurveStateForEntry
numOfEntryPins = Parameters.Num_of_Entry_Pins
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
def CopyAndTranslate_Scale(activeComp, body, translation, scaleFactorX, scaleFactorY):
    result = Copy.Execute(Selection.Create(body))
    if (result.Success == True):
        newBody = result.CreatedObjects[0]        
        Move.Translate(Selection.Create(newBody), translation, MoveOptions())        
        position=activeComp.Content.Bodies[t+1].Edges[0].GetChildren[ICurvePoint]()[0].Position
        selectionScale=Selection.Create(result.CreatedObjects[0])
        #Scale along x axis but, not recommended to play wirh scaleFactorX; so it can mis allign the cell connections
        result = Scale.Execute(selectionScale,Point.Create(position.X, position.Y, position.Z), Direction.DirX ,scaleFactorX)
        #Scale along Y axis; change scaleFactorY to scale input channel total lenght
        result = Scale.Execute(selectionScale,Point.Create(position.X, position.Y, position.Z), Direction.DirY ,scaleFactorY)
        RenameObject.Execute(Selection.Create(newBody), 'Layer'+t.ToString())
        return newBody

def CurvedChannel (activeComp, splineDistance, channelHeight, curveState):
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
    startSelPoint = SelectionPoint.Create(activeComp.Content.Curves[5], curveState)
    endSelPoint = SelectionPoint.Create(activeComp.Content.Curves[6], curveState)
    end = Point2D.Create( endSelPoint.Point.X, endSelPoint.Point.Y)
    options = SketchArcOptions()
    options.ArcSense = ArcSense.Normal
    result = SketchArc.CreateTangentArc( startSelPoint, end, options)    
    
    # Solidify Sketch    
    ViewHelper.SetViewMode(InteractionMode.Solid, None)
   
    # Trim Sketch Curve
    numOfCurves = activeComp.Content.Curves.Count
    while numOfCurves > 0:
        selectedPoint = SelectionPoint.Create(activeComp.Content.Curves[numOfCurves-1], curveState )
        result = TrimSketchCurve.Execute(selectedPoint)
        numOfCurves -= 1
        
CurvedChannel(multiChannelComp, splineDistance, channelHeight, innerCurveState)
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
    newBody = CopyAndTranslate_Scale( multiChannelComp, baseBody, translation, scaleFactorX, scaleFactorY )
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
# Create a componet and move all bodies in it and Merge them

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

# Create Component and activate it
enterExitComp = ComponentHelper.CreateAtRoot("2D_Entry_Exit_Pins")
ComponentHelper.SetActive(enterExitComp)

# Parameter modifications
hWi = fluidChipWidth/2
hLe = fluidChipLength/2
circleRadius = MM(0.5)
circleGap = MM(3)
circleStartY = -(-hLe+(2*circleGap))
circleStartX= -hWi + ( ( fluidChipWidth-((numOfEntryPins-1)*circleGap)) / 2 )

# Parameter modifications for entering Channels
scaleFactorX=1
totalLengthOfCellOnYAxis = ( numYElements / 2) * periodicity 
numOfCellChannelLayers = math.log(numXElements,2)

# Determine the distance between entering inlet and channel inlet
totalLengthOfCellChannelsOnYAxis = 0
z = 0
while z < numOfCellChannelLayers:
    result = ( periodicity * scaleChannelHeight ) * (math.pow(2,z))
    totalLengthOfCellChannelsOnYAxis += result    
    z = z + 1

totalLengthOfCellPlusChannelsOnYAxis = totalLengthOfCellChannelsOnYAxis + totalLengthOfCellOnYAxis 
totalGapBetweenEntryPinsAndChannelEnd = circleStartY - totalLengthOfCellPlusChannelsOnYAxis

finalCellChannelWidth = channelWidth * math.pow ( 2, numOfCellChannelLayers )

## Draw Enter and Exit Pins
#sectionPlane = Plane.PlaneXY
#result = ViewHelper.SetSketchPlane(sectionPlane, None)

## run nested while loops to create circles at the entry and exit locations
#m=0
#while m < 2:
#    t=0
#    while t < numOfEntryPins:
#        # Sketch Circle
#        origin = Point2D.Create(circleStartX + t*circleGap,  circleStartY)
#        result = SketchCircle.Create(origin, circleRadius)
#        t+=1
#    circleStartY=-1*circleStartY
#    m+=1

## Solidify Sketch
#mode = InteractionMode.Solid
#result = ViewHelper.SetViewMode(mode, None)
## EndBlock

ComponentHelper.SetRootActive()

########################################################################################

########################################################################################

# Create Component and activate it
multiEnteringChannelComp = ComponentHelper.CreateAtRoot("2D Multiple Entry Exit Channel")
ComponentHelper.SetActive(multiEnteringChannelComp)

scaleFactorX=1
scaleFactorY= Parameters.ScaleChannelHeight

# modify and define variables
splineDistance = periodicity * 2.4e-06
initialEnteringChannelHeight = circleGap
innerSplineScale = 0.9
numOfEnteringChannelLayers = math.log(numOfEntryPins ,2)
cwS = finalCellChannelWidth / math.pow(2, numOfEnteringChannelLayers)
per = circleGap/2
cw = cwS / 2 

# if curved entry selected
CurvedChannel(multiEnteringChannelComp, splineDistance, initialEnteringChannelHeight, InnerCurveStateForEntry)

# if rectangular is choosen
rectangularEntryExit = Parameters.RectangularEntryExit

rectOrigin = Point.Create(-finalCellChannelWidth/2, totalLengthOfCellPlusChannelsOnYAxis, 0 )
RectangularSurface.Create(finalCellChannelWidth, totalGapBetweenEntryPinsAndChannelEnd, rectOrigin)

# Move to Start Entry Pins Start Location
offSetEnteringYdirection = circleStartY
offSetEnteringXdirection = ( ( numOfEntryPins / 2 ) -1 )  *  circleGap  
baseBody = multiEnteringChannelComp.Content.Bodies[0]
selectedBaseBody = BodySelection.Create(baseBody)
directionY = -Direction.DirY
directionX = -Direction.DirX
options = MoveOptions()
options.MaintainOrientation = True
result = Move.Translate(selectedBaseBody, directionY, offSetEnteringYdirection, options)
result = Move.Translate(selectedBaseBody, directionX, offSetEnteringXdirection, options)
# EndBlock

# Make a body list
bodyList = List[IDocObject]()
bodyList.Add(baseBody)

# Calculate the scale amount for entering channel height to fill the gap
initialTotalLengthOfEnteringChannelLayers = 0
z = 0
numOfEnteringChannelLayers = math.log( numOfEntryPins, 2 )
while z < numOfEnteringChannelLayers:
    result = ( initialEnteringChannelHeight ) * (math.pow(2,z))
    initialTotalLengthOfEnteringChannelLayers += result    
    z = z + 1
scaleAmountForEnteringChannelLayersToFillTheGap = totalGapBetweenEntryPinsAndChannelEnd / initialTotalLengthOfEnteringChannelLayers
# end of calculation

scaleFactorX = 1
scaleFactorY = scaleAmountForEnteringChannelLayersToFillTheGap
scaledEnteringChannelHeight = scaleAmountForEnteringChannelLayersToFillTheGap * initialEnteringChannelHeight
periodicityEnteringChannels = circleGap
halfPeriodicityEnteringChannels = circleGap/2
t = 0
numOfEnteringChannelLayers=math.log(numOfEntryPins,2)
while t < numOfEnteringChannelLayers: 
    Xoff = math.pow (2, t ) -1
    Yoff = math.pow (2, t ) -1
    translation = Vector.Create( Xoff *(( (periodicityEnteringChannels + cwS ) / 2) - cwS)  ,  scaledEnteringChannelHeight * Yoff,  0 )
    newBody = CopyAndTranslate_Scale(multiEnteringChannelComp, baseBody, translation, scaleFactorX, scaleAmountForEnteringChannelLayersToFillTheGap )
    bodyList.Add(newBody)    
    scaleFactorX*=2
    scaleAmountForEnteringChannelLayersToFillTheGap*=2
    t = t + 1

# run nested to loop to create x cell for each layer
m = numOfEntryPins/2
k=0
n=0
while n <numOfEnteringChannelLayers:
    stringName =str('Layer'+n.ToString())
    selectionO = Selection.CreateByNames(stringName)
    k=0
    while k < m:
        translationX = Vector.Create((math.pow(2,n) * k * 2 * circleGap ), 0 ,0)
        newBody = CopyAndTranslate_Along ( selectionO, translationX)
        bodyList.Add(newBody)
        k+=1    
    m/=2
    Delete.Execute(selectionO)    
    n+=1
    
multiEnteringChannelComp.Content.Bodies[0].Delete()

if multiEnteringChannelComp.Content.Bodies.Count > 1 :
    selection = BodySelection.Create(multiEnteringChannelComp.Content.Bodies)
    result = Combine.Merge(selection)

RenameObject.Execute(BodySelection.Create(multiEnteringChannelComp.Content.Bodies[0]), 'Entry Channels')

# Create Datum Plane
result = DatumPlaneCreator.Create(Point.Origin, Direction.DirY)
# EndBlock

# Mirror
selection = BodySelection.Create(multiEnteringChannelComp.Content.Bodies[0])
mirrorPlane = Selection.Create(multiEnteringChannelComp.Content.DatumPlanes[0])
options = MirrorOptions()
result = Mirror.Execute(selection, mirrorPlane, options)
RenameObject.Execute(BodySelection.Create(multiEnteringChannelComp.Content.Bodies[1]), 'Exit Channels')
# EndBlock

# Change Object Visibility
selection = Selection.Create(multiEnteringChannelComp.Content.DatumPlanes[0])
visibility = VisibilityType.Hide
inSelectedView = False
faceLevel = False
ViewHelper.SetObjectVisibility(selection, visibility, inSelectedView, faceLevel)
# EndBlock

#######################################################################
#######################################################################

#Create a parent componet and move all bodies in it
twoFinalComp = ComponentHelper.CreateAtRoot("2D Final Component")
selectedBodies = BodySelection.Create(GetRootPart().GetAllBodies())
result = ComponentHelper.MoveBodiesToComponent( selectedBodies ,twoFinalComp , False , None)

# new approach to Merge Bodies
numberOfUnmergedBodies = twoFinalComp.Content.Bodies.Count-1
while numberOfUnmergedBodies > 0:
    mainBody = BodySelection.Create(twoFinalComp.Content.Bodies[0])
    secondaryBodies = BodySelection.Create(twoFinalComp.Content.Bodies[numberOfUnmergedBodies])
    result = Combine.Merge(mainBody, secondaryBodies)
    numberOfUnmergedBodies -=1
    if numberOfUnmergedBodies == 0:
        RenameObject.Execute(BodySelection.Create(twoFinalComp.Content.Bodies[0]), 'Merged Bodies')
        break

def deleteEmptyComponets():
    numComp = GetRootPart().Components.Count
    n = numComp-1
    while 0 < numComp :
        bodyCount = GetRootPart().Components[n].Content.Bodies.Count
        if bodyCount == 0:
            Delete.Execute(ComponentSelection.Create(GetRootPart().Components[n]))
        n -=1
        if n == -1:
            break   

deleteEmptyComponets()

Selection.Clear()
ComponentHelper.SetRootActive()
mode = ViewHelper.ViewProjection.Isometric
result = ViewHelper.SetProjection(mode)
ViewHelper.ZoomToEntity(PartSelection.Create(GetRootPart()))
# EndBlock