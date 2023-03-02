# 06 2D Entry Exit
# Create the fluid domain of the entry and exit channel structures in two dimensions.
# Emrah Dursun. 02/03/2023.
from SpaceClaim.Api.V22.Geometry import Point
import math

# Get Input Parameters
per=Parameters.Periodicity/2
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
numZElements=Parameters.Z_direction_repeat
fluidChipLength = Parameters.FluidChip_Length
fluidChipWidth = Parameters.FluidChip_Width
scaleFactorY= Parameters.Scale_Channel_Along_Y
scaleFactorX=1
numOfEntryPins = Parameters.Num_of_Entry_Pins
# End Parameters

#ClearAll()
#Layers.DeleteEmpties()

# Create Component and activate it
enterExitComp = ComponentHelper.CreateAtRoot("2D_Entry_Exit_Pins")
ComponentHelper.SetActive(enterExitComp)

# Parameter modifications
# half Length half widht
hWi = fluidChipWidth/2
hLe = fluidChipLength/2

#
circleRadius = MM(0.5)
circleGap = MM(3)
circleStartY = -(-hLe+(2*circleGap))
#number of inlets 4
numInlet = numOfEntryPins
circleStartX= -hWi + ( ( fluidChipWidth-((numInlet-1)*circleGap)) / 2 )

# Parameter modifications for entering Channels
scaleFactorX=1
scaleFactorY= Parameters.Scale_Channel_Along_Y

strech = scaleFactorY
distanceCellY = (numZElements*periodicity)/2
numOfChannelLayers = math.log(numXElements,2)

# Determine the distance between entering inlet and channel inlet
distanceChannelsY = 0
z = 0
while z < numOfChannelLayers:
    result = ( 2 * periodicity ) * (math.pow(2,z))
    distanceChannelsY += result    
    strech*=2
    z = z + 1

distanceChannelsY = distanceChannelsY*scaleFactorY

distanceSumCellChannelY = distanceChannelsY+distanceCellY
distanceGapEnterCelChannelY= circleStartY - distanceSumCellChannelY

print(distanceGapEnterCelChannelY)

finalChannelWidth = channelWidth * math.pow(2, numOfChannelLayers)
print(finalChannelWidth)

# Set Sketch Plane
sectionPlane = Plane.PlaneXY
result = ViewHelper.SetSketchPlane(sectionPlane, None)

## run nested while loops to create circles at the entry and exit locations
#m=0
#while m < 2:
#    t=0
#    while t < numInlet:
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
# comp = ComponentHelper.CopyToRoot(comp)

########################################################################################

########################################################################################

# Create Component and activate it
multiEnteringChannelComp = ComponentHelper.CreateAtRoot("2D Multiple Entry Exit Channel")
ComponentHelper.SetActive(multiEnteringChannelComp)

scaleFactorX=1
scaleFactorY= Parameters.Scale_Channel_Along_Y

def CurvedChannel (splEn, splLen, channelWidthS, periodicityS):    
    # Set Sketch Plane
    result = ViewHelper.SetSketchPlane(Plane.PlaneXY)
    chamferRadius = splLen - UM(200)
    cwS=channelWidthS
    perS = periodicityS/2
    # Define Points for Sketch Splines
    
    startA = Point.Create(  MM(0),                             0,           0)
    startAa= Point.Create(  MM(0),                             splEn ,      0)
    
    endA   = Point.Create(  MM(cwS),                              0,           0)
    endAa  = Point.Create(  MM(cwS),                              splEn,       0)
    
    startB = Point.Create(  MM(perS-cwS/2),         splLen,      0)
    startBb= Point.Create(  MM(perS-cwS/2),         splLen-splEn,0)
    
    endB   = Point.Create(  MM(perS+cwS/2),                          splLen,      0)
    endBb  = Point.Create(  MM(perS+cwS/2),                          splLen-splEn,0)
    
    startC = Point.Create(  MM(periodicityS),        0,              0)
    startCc= Point.Create(  MM(periodicityS),        splEn,          0)    
    
    endC   = Point.Create(  MM(periodicityS+cwS),     0,              0)
    endCc  = Point.Create(  MM(periodicityS+cwS),     splEn,          0)    
    
    startD = Point.Create(  MM(perS+cwS/2),           splLen,         0)
    startDd= Point.Create(  MM(perS+cwS/2),           splLen-splEn,   0)
    
    endD   = Point.Create(  MM(perS+3*cwS/2), splLen,         0)
    endDd  = Point.Create(  MM(perS+3*cwS/2), splLen-splEn,   0)    
    
   #these are just the point locations that i want     
    endRrrrrrr       = Point.Create( MM(perS+cwS/2) - UM(740) ,    chamferRadius - UM(335) ,        0)
    endRrrrrr       = Point.Create( MM(perS+cwS/2) - UM(417) ,    chamferRadius - UM(236) ,        0)
    endRrrrr        = Point.Create( MM(perS+cwS/2) - UM(60) ,      chamferRadius - UM(35.5),         0)
    endRrrr         = Point.Create( MM(perS+cwS/2) - UM(42) ,      chamferRadius - UM(15.5),         0)
    endRrr          = Point.Create( MM(perS+cwS/2) - UM(32),      chamferRadius - UM(6.5),          0)
    endRr           = Point.Create( MM(perS+cwS/2) - UM(20),         chamferRadius - UM(2),           0)
    endR            = Point.Create( MM(perS+cwS/2) ,                    chamferRadius,                         0)
    
    #these are just the point locations that i want 
    endMrrrrrr       = Point.Create( MM(perS+cwS/2) + UM(740) ,   chamferRadius - UM(335) ,    0)
    endMrrrrr       = Point.Create( MM(perS+cwS/2) + UM(417) ,   chamferRadius - UM(236) ,    0)
    endMrrrr        = Point.Create( MM(perS+cwS/2) + UM(60) ,     chamferRadius - UM(35.5),     0)
    endMrrr         = Point.Create( MM(perS+cwS/2) + UM(42) ,     chamferRadius - UM(15.5),     0)
    endMrr          = Point.Create( MM(perS+cwS/2) + UM(32),     chamferRadius - UM(6.5),        0)
    endMr           = Point.Create( MM(perS+cwS/2) + UM(20),        chamferRadius - UM(2),           0)
    endM            = Point.Create( MM(perS+cwS/2) ,                    chamferRadius,                         0)
      
    # Sketch Line 1st and 2nd
    SketchLine.Create(startA, endA)
    SketchLine.Create(startB, endB)
    
    # Sketch Line 3rd and 4th
    SketchLine.Create(startC, endC)
    SketchLine.Create(startD, endD)
    
    # Sketch Spline 1st
    points = [startA, startAa, startBb, startB]
    SketchNurbs.CreateFrom3DPoints(False, points)
    
#    # Sketch Spline 2nd
#    points = [endA, endAa,  endBb, endB]
#    SketchNurbs.CreateFrom3DPoints(False, points)

    #Sketch Spline 2nd Curved        
    points = [endA, endAa , endRrrrrrr, endRrrrrr, endRrrrr, endRrrr, endRrr, endRr, endR]
    SketchNurbs.CreateFrom3DPoints(False, points)
    
    # Sketch Spline 3rd Curved
    points = [startC, startCc, endMrrrrrr, endMrrrrr, endMrrrr, endMrrr, endMrr, endMr, endM]
    SketchNurbs.CreateFrom3DPoints(False, points)

#    # Sketch Spline 3rd
#    points = [startC, startCc, startDd, startD]
#    SketchNurbs.CreateFrom3DPoints(False, points)
    
    # Sketch Spline 4th
    points = [endC, endCc, endDd, endD]
    SketchNurbs.CreateFrom3DPoints(False, points)
    # EndBlock - Define Points for Sketch Splines
    
    # Solidify Sketch
    ViewHelper.SetViewMode(InteractionMode.Solid, None)

numOfEnteringChannelLayers=math.log(numOfEntryPins ,2)
cwS = finalChannelWidth / math.pow(2, numOfEnteringChannelLayers)
lengthOfSpline = MM(1)
CurvedChannel(MM(0.001), MM( lengthOfSpline ), MM(cwS), MM(circleGap))


# Copy and Translate the already created base steps
def CopyAndTranslate_AlongX(body, translationX):   
    result = Copy.Execute(body)    
    if (result.Success == True):
        newBody = result.CreatedObjects[0]        
        Move.Translate(Selection.Create(newBody), translationX, MoveOptions())      
        return newBody
    
#*#
#numSteps = numZElements-1
#offSetYdirection =(numZElements*(periodicity/2))
offSetEnteringYdirection = -circleStartY

# Translate Along Y direction as half of the cell-number on Y direction 
baseBody = multiEnteringChannelComp.Content.Bodies[0]
selection = BodySelection.Create(baseBody)
direction = Direction.DirY
options = MoveOptions()
options.MaintainOrientation = True
result = Move.Translate(selection, direction, offSetEnteringYdirection, options)
# EndBlock

#offSetXdirection = (numXElements*periodicity)-per
offSetEnteringXdirection = ( (numInlet-1)  * (circleGap/2)) 

# Translate Along Y direction as half of the cell-number on Y direction 
baseBody = multiEnteringChannelComp.Content.Bodies[0]
selection = BodySelection.Create(baseBody)
direction = -Direction.DirX
options = MoveOptions()
options.MaintainOrientation = True
result = Move.Translate(selection, direction, offSetEnteringXdirection, options)
# EndBlock

# Make a body list
bodyList = List[IDocObject]()
bodyList.Add(baseBody)

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


scaleFactorYS = 1
strechS=scaleFactorYS
periodicityS = circleGap
perS = circleGap/2
# Determine the *Scale factor for Entering splines channels*
distanceEnteringChannelsY = 0
z = 0
numOfEnteringChannelLayers=math.log(numInlet,2)
while z < numOfEnteringChannelLayers:
    result = ( lengthOfSpline ) * (math.pow(2,z))
    distanceEnteringChannelsY += result    
#    if z > 0:
#        BlockBody.Create( Point.Origin, Point.Create(MM(10), MM(total), MM(10)), ExtrudeType.ForceIndependent)
    z = z + 1

#distanceChannelsY = distanceChannelsY*scaleFactorY

#distanceSumCellChannelY = distanceChannelsY+distanceCellY
#distanceGapEnterCelChannelY= circleStartY - distanceSumCellChannelY

scaleFactorYS = distanceGapEnterCelChannelY / distanceEnteringChannelsY

# Run a loop to make the steps along the layer height, layer numbers change respect to number of cell, under this section one can also adjust to scale along y-axis
#distanceGapEnterCelChannelY

strechS=scaleFactorYS

periodicityS = lengthOfSpline
perS = circleGap/2

t = 0
numOfEnteringChannelLayers=math.log(numInlet,2)
while t < numOfEnteringChannelLayers:    
#    translation = Vector.Create((math.pow(2,t)*(per-channelWidth/2)) - per, strech*((math.pow(2,t) * 2 * periodicity)-2*periodicity), 0 )
    translation = Vector.Create( (math.pow(2,t) * (perS - cwS/2) ) - perS,    strechS*((math.pow(2,t) * periodicityS)- periodicityS), 0 )   
    newBody = CopyAndTranslate_Scale(baseBody, translation,scaleFactorX, scaleFactorYS)
    bodyList.Add(newBody)
    scaleFactorX*=2
    scaleFactorYS*=2
    t = t + 1

# run nested to loop to create x cell for each layer
m = numInlet/2
k=0
n=0
# 
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


#######################################################################################
Selection.Clear()
ComponentHelper.SetRootActive()
mode = ViewHelper.ViewProjection.Top
result = ViewHelper.SetProjection(mode)
ViewHelper.ZoomToEntity(PartSelection.Create(GetRootPart()))

