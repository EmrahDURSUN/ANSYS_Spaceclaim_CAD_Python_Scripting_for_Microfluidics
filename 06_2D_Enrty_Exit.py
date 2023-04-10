# 06 2D Entry Exit
# Create the fluid domain of the entry and exit channel structures in two dimensions.
# Emrah Dursun. 02/03/2023.
# Emrah Dursun. 07/04/2023.
from SpaceClaim.Api.V22.Geometry import Point
import math

# Get Input Parameters
per=Parameters.Periodicity/2
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
scaleFactorX=1
numOfEntryPins = Parameters.Num_of_Entry_Pins
# End Parameters

#ClearAll()
#Layers.DeleteEmpties()

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

# Set Sketch Plane
sectionPlane = Plane.PlaneXY
result = ViewHelper.SetSketchPlane(sectionPlane, None)

# run nested while loops to create circles at the entry and exit locations
m=0
while m < 2:
    t=0
    while t < numOfEntryPins:
        # Sketch Circle
        origin = Point2D.Create(circleStartX + t*circleGap,  circleStartY)
        result = SketchCircle.Create(origin, circleRadius)
        t+=1
    circleStartY=-1*circleStartY
    m+=1

# Solidify Sketch
mode = InteractionMode.Solid
result = ViewHelper.SetViewMode(mode, None)
# EndBlock

ComponentHelper.SetRootActive()
# comp = ComponentHelper.CopyToRoot(comp)

########################################################################################
########################################################################################

# Declare a function to copy, translate created base steps
def CopyAndTranslate_AlongX(body, translationX):   
    result = Copy.Execute(body)    
    if (result.Success == True):
        newBody = result.CreatedObjects[0]        
        Move.Translate(Selection.Create(newBody), translationX, MoveOptions())      
        return newBody


# Declare a function to copy, translate and scale the base steps
def CopyAndTranslate_Scale(body, translation, scaleFactorX, scaleFactorY):
    result = Copy.Execute(Selection.Create(body))
    if (result.Success == True):
        newBody = result.CreatedObjects[0]        
        Move.Translate(Selection.Create(newBody), translation, MoveOptions())        
        position=multiEnteringChannelComp.Content.Bodies[t+1].Edges[0].GetChildren[ICurvePoint]()[0].Position
        selectionScale=Selection.Create(result.CreatedObjects[0])
        #Scale along x axis but, not recommended to play wirh scaleFactorX; so it can mis allign the cell connections
        result = Scale.Execute(selectionScale,Point.Create(position.X, position.Y, position.Z), Direction.DirX ,scaleFactorX)
        #Scale along Y axis; change scaleFactorY to scale input channel total lenght
        result = Scale.Execute(selectionScale,Point.Create(position.X, position.Y, position.Z), Direction.DirY ,scaleFactorY)
        RenameObject.Execute(Selection.Create(newBody),'Layer'+t.ToString())
        return newBody


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
    startSelPoint = SelectionPoint.Create(multiEnteringChannelComp.Content.Curves[5], innerCurveState)
    endSelPoint = SelectionPoint.Create(multiEnteringChannelComp.Content.Curves[6], innerCurveState)
    end = Point2D.Create( endSelPoint.Point.X, endSelPoint.Point.Y)
    options = SketchArcOptions()
    options.ArcSense = ArcSense.Normal
    result = SketchArc.CreateTangentArc( startSelPoint, end, options)    
    
    # Solidify Sketch    
    ViewHelper.SetViewMode(InteractionMode.Solid, None)
   
    # Trim Sketch Curve
    numOfCurves = multiEnteringChannelComp.Content.Curves.Count
    while numOfCurves > 0:
        selectedPoint = SelectionPoint.Create(multiEnteringChannelComp.Content.Curves[numOfCurves-1], innerCurveState )
        result = TrimSketchCurve.Execute(selectedPoint)
        numOfCurves -= 1

CurvedChannel(splineDistance, initialEnteringChannelHeight, innerCurveState)

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
    newBody = CopyAndTranslate_Scale( baseBody, translation, scaleFactorX, scaleAmountForEnteringChannelLayersToFillTheGap )
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
        newBody = CopyAndTranslate_AlongX( selectionO, translationX)
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

#######################################################################################
Selection.Clear()
ComponentHelper.SetRootActive()
mode = ViewHelper.ViewProjection.Isometric
result = ViewHelper.SetProjection(mode)
ViewHelper.ZoomToEntity(PartSelection.Create(GetRootPart()))