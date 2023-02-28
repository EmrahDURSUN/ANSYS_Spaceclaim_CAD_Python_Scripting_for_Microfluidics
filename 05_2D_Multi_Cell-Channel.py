# 05_2D_Multi_Cell-Channel
# Create the fluid domain of the multi-cell and channel structures simultaneously in two dimensions. Then merge them.
# Emrah Dursun. 23/02/2023. 
# Python Script, API Version = V22 Beta
from SpaceClaim.Api.V22.Geometry import Point
import math

#Selection.Empty()
#ClearAll()
#Layers.DeleteEmpties()

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
scaleFactorY= Parameters.Scale_Channel_Along_Y
scaleFactorX=1
# End Parameters

# Create Component and activate it
multiCellTwoDComp = ComponentHelper.CreateAtRoot("2D Multi Cell")
ComponentHelper.SetActive(multiCellTwoDComp)
 
# Beginning of Surface Creation
######################################################################
    
def pointAllocateFirst( distP, angP):
    seloc =Selection.Create(DatumPointCreator.Create(Point.Create(0, MM(distP), 0)).CreatedPoint)
    move = Move.Rotate(seloc, Line.Create(Point.Origin, Direction.DirZ),  angP, MoveOptions())
    
def pointAllocateSecond(distP,angP):
    seloc =Selection.Create(DatumPointCreator.Create(Point.Create(0, MM(distP), 0)).CreatedPoint)
    move = Move.Rotate(seloc, Line.Create(Point.Origin, Direction.DirZ), angP, MoveOptions())
    
def surfaceCutOperation(ring, nearPoint, farPoint, rotation):
    if (ring == 1 or ring == 3):
        pointAllocateFirst( nearPoint, rotation)
        pointAllocateFirst( nearPoint, -rotation)
        pointAllocateFirst( farPoint, rotation)
        pointAllocateFirst( farPoint, -rotation)
    if (ring == 2 or ring ==  4 or ring ==  5):
        pointAllocateSecond( nearPoint, rotation)
        pointAllocateSecond( nearPoint, -rotation)
        pointAllocateSecond( farPoint, rotation)
        pointAllocateSecond( farPoint, -rotation)
       
    start1 =(multiCellTwoDComp.Content.DatumPoints[0]).Position
    end1 = (multiCellTwoDComp.Content.DatumPoints[1]).Position
    start2 =(multiCellTwoDComp.Content.DatumPoints[2]).Position
    end2 = (multiCellTwoDComp.Content.DatumPoints[3]).Position
    
    while multiCellTwoDComp.Content.DatumPoints.Count > 0:
        multiCellTwoDComp.Content.DatumPoints[0].Delete()
        
    curves = List[ITrimmedCurve]()
    curves.Add(CurveSegment.CreateArc(Point.Origin,start1,end1, -Direction.DirZ))
    curves.Add(CurveSegment.CreateArc(Point.Origin,start2,end2, -Direction.DirZ))
    curves.Add(CurveSegment.Create(start1,start2))
    curves.Add(CurveSegment.Create(end1,end2))
        
    designResult = PlanarBody.Create(Plane.PlaneXY, curves)
    designBody1 = designResult.CreatedBody.SetName('Surface' + ring.ToString() )
  
######################################################################
# Create Operations
surfaceCutOperation( 1, radius,             radius+width,                    DEG(180) +angle)  #Cut Up
surfaceCutOperation( 2, radius,             radius+width,                    DEG(180) - angle - oangle)  #Cut Up
#######################################################################

###############################################################

originRectang=Point.Create(-channelWidth/2, -periodicity/2,0)
result=RectangularSurface.Create( channelWidth, periodicity, originRectang)
body = result.CreatedBody.SetName('Channel')

## Merge Bodies
#targets = Selection.CreateByNames('Channel','surface1')
#result = Combine.Merge(targets)
#targets = Selection.CreateByNames('surface2','surface1')
#result = Combine.Merge(targets)
## EndBlock
#seloc =  Selection.CreateByNames('surface1')

num = multiCellTwoDComp.Content.Bodies.Count-1
t=0
while t < num:
    selectionTarget = BodySelection.Create(multiCellTwoDComp.Content.Bodies[num-t])
    selectionOthers = BodySelection.Create(multiCellTwoDComp.Content.Bodies[num-1-t])
    result = Combine.Merge( selectionTarget , selectionOthers)
    t+=1

RenameObject.Execute(BodySelection.Create(multiCellTwoDComp.Content.Bodies[0]), 'Combined_Surface')
    
#move = Move.Rotate(seloc, Line.Create(Point.Origin, Direction.DirX), DEG(90), MoveOptions())

#######################################################################


numSteps = numZElements-1
offSet =(numZElements*(periodicity/2))-(periodicity/2)

# Translate Along Z Handle
baseBody = multiCellTwoDComp.Content.Bodies[0]
selection = BodySelection.Create(baseBody)
direction = -Direction.DirY
options = MoveOptions()
options.MaintainOrientation = True
result = Move.Translate(selection, direction, offSet, options)
# EndBlock

# Make a body list
bodyList = List[IDocObject]()
bodyList.Add(baseBody)

# Declare a function to copy and translate the base step 
def CopyAndTranslate(body, translation):
    result = Copy.Execute(Selection.Create(body))
    if (result.Success == True):
        newBody = result.CreatedObjects[0]        
        Move.Translate(Selection.Create(newBody), translation, MoveOptions())
        RenameObject.Execute(Selection.Create(newBody),'Y_dir'+t.ToString())
        return newBody

# Run a loop ToolCommand make the steps 
t = 0
while t < numZElements:
    translation = Vector.Create(UM(0),MM(t*periodicity),UM(0))
    newBody = CopyAndTranslate(baseBody, translation)
    bodyList.Add(newBody)
    t = t + 1
    
#print bodyList
multiCellTwoDComp.Content.Bodies[0].Delete()

# Make Components
selectionT = BodySelection.Create(multiCellTwoDComp.Content.Bodies)
result = Combine.Merge(selectionT)

#Merge Bodies
selection = BodySelection.Create(multiCellTwoDComp.Content.Bodies)
#result = ComponentHelper.MoveBodiesToComponent(selection)

#selection = PartSelection.Create(GetRootPart().Components[0].Content)
#result = RenameObject.Execute(selection,"X_dir")
# EndBlock

#######################################################################

numSteps = numXElements-1
offSet =(numXElements*(periodicity/2))-(periodicity)

# Translate Along X Handle
baseBody = multiCellTwoDComp.Content.Bodies[0]
selection = BodySelection.Create(baseBody)
direction = -Direction.DirX
options = MoveOptions()
options.MaintainOrientation = True
result = Move.Translate(selection, direction, offSet, options)
# EndBlock

# Make a body list
bodyList = List[IDocObject]()
bodyList.Add(baseBody)

# Declare a function to copy and translate the base step 
def CopyAndTranslate(body, translation):
    result = Copy.Execute(Selection.Create(body))
    if (result.Success == True):
        newBody = result.CreatedObjects[0]        
        Move.Translate(Selection.Create(newBody), translation, MoveOptions())
        RenameObject.Execute(Selection.Create(newBody),'X'+t.ToString())
        return newBody

# Run a loop ToolCommand make the steps 
t = 0
while t < numXElements:
    translation = Vector.Create(MM(t*periodicity-periodicity/2),UM(0),UM(0))
    newBody = CopyAndTranslate(baseBody, translation)
    bodyList.Add(newBody)
    t = t + 1
    
#print bodyList
multiCellTwoDComp.Content.Bodies[0].Delete()


#######################################################################


# Create Component and activate it
multiChannelComp = ComponentHelper.CreateAtRoot("2D Multiple Channel")
ComponentHelper.SetActive(multiChannelComp)


def CurvedChannel (splEn, splLen):    
    # Set Sketch Plane
    result = ViewHelper.SetSketchPlane(Plane.PlaneXY)
    cw=channelWidth
    # Define Points for Sketch Splines
    
    startA = Point.Create(  MM(0),                             0,           0)
    startAa= Point.Create(  MM(0),                             splEn ,      0)
    endA   = Point.Create(  MM(channelWidth),                              0,           0)
    endAa  = Point.Create(  MM(channelWidth),                              splEn,       0)
    startB = Point.Create(  MM(per-cw/2),         splLen,      0)
    startBb= Point.Create(  MM(per-cw/2),         splLen-splEn,0)
    endB   = Point.Create(  MM(per+cw/2),                          splLen,      0)
    endBb  = Point.Create(  MM(per+cw/2),                          splLen-splEn,0)
    startC = Point.Create(  MM(periodicity),        0,              0)
    startCc= Point.Create(  MM(periodicity),        splEn,          0)    
    endC   = Point.Create(  MM(periodicity+cw),     0,              0)
    endCc  = Point.Create(  MM(periodicity+cw),     splEn,          0)    
    startD = Point.Create(  MM(per+cw/2),           splLen,         0)
    startDd= Point.Create(  MM(per+cw/2),           splLen-splEn,   0)    
    endD   = Point.Create(  MM(per+3*cw/2), splLen,         0)
    endDd  = Point.Create(  MM(per+3*cw/2), splLen-splEn,   0)    
    
    
    #these are just the point locations that i want     
    endRrrrrrrrr    = Point.Create( MM(per+cw/2) - UM(120.0134) ,     splLen - UM(474.359) ,  0)
    endRrrrrrrr     = Point.Create( MM(per+cw/2) - UM(74.648) ,       splLen - UM(348.2007),  0)
    endRrrrrrr      = Point.Create( MM(per+cw/2) - UM(37.8512) ,      splLen - UM(235.23) ,   0)
    endRrrrrr       = Point.Create( MM(per+cw/2) - UM(20.8406) ,      splLen - UM(170.121) ,   0)
    endRrrrr        = Point.Create( MM(per+cw/2) - UM(16.367) ,      splLen - UM(149.664),         0)
    endRrrr         = Point.Create( MM(per+cw/2) - UM(12) ,      splLen - UM(135),         0)
    endRrr          = Point.Create( MM(per+cw/2) - UM(7.4),         splLen - UM(128),        0)
    endRr           = Point.Create( MM(per+cw/2) - UM(2),             splLen - UM(124.7),           0)
    endR            = Point.Create( MM(per+cw/2) ,                    splLen - UM(124.5),           0)
    
    #these are just the point locations that i want 
    endMrrrrrrrr    = Point.Create( MM(per+cw/2) + UM(120.0134) ,     splLen - UM(474.359) ,  0)
    endMrrrrrrr     = Point.Create( MM(per+cw/2) + UM(74.648) ,       splLen - UM(348.2007),  0)
    endMrrrrrr      = Point.Create( MM(per+cw/2) + UM(37.8512) ,      splLen - UM(235.23) ,   0)
    endMrrrrr       = Point.Create( MM(per+cw/2) + UM(20.8406) ,      splLen - UM(170.121) ,   0)
    endMrrrr        = Point.Create( MM(per+cw/2) + UM(16.367) ,      splLen - UM(149.66),         0)
    endMrrr         = Point.Create( MM(per+cw/2) + UM(12) ,      splLen - UM(135),         0)
    endMrr          = Point.Create( MM(per+cw/2) + UM(7.4),         splLen - UM(128),        0)
    endMr           = Point.Create( MM(per+cw/2) + UM(2),             splLen - UM(124.7),           0)
    endM            = Point.Create( MM(per+cw/2) ,                    splLen - UM(124.5),           0)
      
    
    # Sketch Line 1st and 2nd
    SketchLine.Create(startA, endA)
    SketchLine.Create(startB, endB)
    
    # Sketch Line 3rd and 4th
    SketchLine.Create(startC, endC)
    SketchLine.Create(startD, endD)
    
    # Sketch Spline 1st
    points = [startA, startAa, startBb, startB]
    SketchNurbs.CreateFrom3DPoints(False, points)
    
    # Sketch Spline 2nd
    #points = [endA, endAa,  endBb, endB]
    #SketchNurbs.CreateFrom3DPoints(False, points)


    #Sketch Spline 2nd Curved        
    points = [endA, endAa, endRrrrrrrrr, endRrrrrrrr, endRrrrrrr,  endRrrrrr, endRrrrr, endRrrr, endRrr, endRr, endR]
    SketchNurbs.CreateFrom3DPoints(False, points)
    
    # Sketch Spline 3rd Curved
    points = [startC, startCc, endMrrrrrrrr, endMrrrrrrr, endMrrrrrr,  endMrrrrr, endMrrrr, endMrrr, endMrr, endMr, endM]
    SketchNurbs.CreateFrom3DPoints(False, points)

    # Sketch Spline 3rd
    #points = [startC, startCc, startDd, startD]
    #SketchNurbs.CreateFrom3DPoints(False, points)
    
    # Sketch Spline 4th
    points = [endC, endCc, endDd, endD]
    SketchNurbs.CreateFrom3DPoints(False, points)
    # EndBlock - Define Points for Sketch Splines
    
    # Solidify Sketch
    ViewHelper.SetViewMode(InteractionMode.Solid, None)

CurvedChannel(MM(0.001),MM(2*periodicity))


# Copy and Translate the already created base steps
def CopyAndTranslate_AlongX(body, translationX):   
    result = Copy.Execute(body)    
    if (result.Success == True):
        newBody = result.CreatedObjects[0]        
        Move.Translate(Selection.Create(newBody), translationX, MoveOptions())
        RenameObject.Execute(Selection.Create(newBody), 'Cell '+k.ToString())
        return newBody
    
#*#
numSteps = numZElements-1
offSetYdirection =(numZElements*(periodicity/2))

# Translate Along Y direction as half of the cell-number on Y direction 
baseBody = multiChannelComp.Content.Bodies[0]
selection = BodySelection.Create(baseBody)
direction = Direction.DirY
options = MoveOptions()
options.MaintainOrientation = True
result = Move.Translate(selection, direction, offSetYdirection, options, Info1)
# EndBlock

offSetXdirection =(numXElements/2*periodicity)-per

# Translate Along Y direction as half of the cell-number on Y direction 
baseBody = multiChannelComp.Content.Bodies[0]
selection = BodySelection.Create(baseBody)
direction = -Direction.DirX
options = MoveOptions()
options.MaintainOrientation = True
result = Move.Translate(selection, direction, offSetXdirection, options, Info1)
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
        position=multiChannelComp.Content.Bodies[t+1].Edges[0].GetChildren[ICurvePoint]()[0].Position
        selectionScale=Selection.Create(result.CreatedObjects[0])
        #Scale along x axis but, not recommended to play wirh scaleFactorX; so it can mis allign the cell connections
        result = Scale.Execute(selectionScale,Point.Create(position.X, position.Y, position.Z), Direction.DirX ,scaleFactorX)
        #Scale along Y axis; change scaleFactorY to scale input channel total lenght
        result = Scale.Execute(selectionScale,Point.Create(position.X, position.Y, position.Z), Direction.DirY ,scaleFactorY)
        RenameObject.Execute(Selection.Create(newBody),'Layer'+t.ToString())
        return newBody


# Run a loop to make the steps along the layer height, layer numbers change respect to number of cell, under this section one can also adjust to scale along y-axis
scaleFactorY= Parameters.Scale_Channel_Along_Y
strech= scaleFactorY
t = 0
numChannelLayers=math.log(numXElements/2,2)
while t <= numChannelLayers:
    translation = Vector.Create((math.pow(2,t)*(per-channelWidth/2)) - per, strech*((math.pow(2,t) * 2 * periodicity)-2*periodicity), 0 )    
    newBody = CopyAndTranslate_Scale(baseBody, translation,scaleFactorX,scaleFactorY)
    bodyList.Add(newBody)
    scaleFactorX*=2
    scaleFactorY*=2
    t = t + 1

# run nested to loop to create x cell for each layer
m=numXElements/2
k=0
n=0
#how many layers ? 4 for 16 cells. 4^2=16
while n <=numChannelLayers:
    stringName =str('Layer'+n.ToString())
    selectionO = Selection.CreateByNames(stringName)
    k=0
    while k<m:
        translationX = Vector.Create((math.pow(2,n) * k * 2 * periodicity), 0 ,0)
        newBody = CopyAndTranslate_AlongX(selectionO, translationX)
        bodyList.Add(newBody)
        k+=1    
    m/=2
    Delete.Execute(selectionO)    
    n+=1
    
multiChannelComp.Content.Bodies[0].Delete()

######################################
# Merge channel surfaces
selectedBodies = BodySelection.Create(multiChannelComp.Content.Bodies)
result = Combine.Merge(selectedBodies)

# Create Datum Plane
result = DatumPlaneCreator.Create(Point.Origin, Direction.DirY)

# Mirror
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

#######################################################################

# Create a componet and move all bodies in it
#multiCellChannelComp = ComponentHelper.CreateAtRoot("Multi-Cell-Channel")
#selectedBodies = BodySelection.Create(GetRootPart().GetAllBodies())
#result = ComponentHelper.MoveBodiesToComponent( selectedBodies ,multiCellChannelComp, False , None)
#multiChannelComp.Delete()
#multiCellTwoDComp.Delete()

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

################

## Create a parent componet
#result = ComponentHelper.CreateAtRoot("Multi-Cell-Channel")
#selectedCreated = Selection.CreateByNames("Multi-Cell-Channel")
#selectedComp = ComponentSelection.Create( multiChannelComp , multiCellTwoDComp)
#result = ComponentHelper.MoveBodiesToComponent (selectedComp, selectedCreated)
#Selection.Clear()


Selection.Clear()
ComponentHelper.SetRootActive()
mode = ViewHelper.ViewProjection.Top
result = ViewHelper.SetProjection(mode)
ViewHelper.ZoomToEntity(PartSelection.Create(GetRootPart()))
# EndBlock