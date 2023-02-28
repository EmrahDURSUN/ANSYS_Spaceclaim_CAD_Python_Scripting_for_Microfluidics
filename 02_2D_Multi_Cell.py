# 02_2D_Multi_Cell
# Create the fluid domain of the multi-cell structure in two dimensions
# Emrah Dursun. 23/02/2023. 
# Python Script, API Version = V22 Beta
from SpaceClaim.Api.V22.Geometry import Point
import math

#Selection.Empty()
ClearAll()
Layers.DeleteEmpties()

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


Selection.Clear()
ComponentHelper.SetRootActive()
mode = ViewHelper.ViewProjection.Top
result = ViewHelper.SetProjection(mode)
ViewHelper.ZoomToEntity(PartSelection.Create(GetRootPart()))


