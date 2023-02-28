# 01 2D Single Cell
# Create two-dimensional fluid region
# Emrah Dursun. 23/02/203. 
# Python Script, API Version = V22 Beta
from SpaceClaim.Api.V22.Geometry import Point
import math

Selection.Empty()
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
# End Parameters
  
# Create Component and activate it
singleCellTwoDComp = ComponentHelper.CreateAtRoot("2D Single Cell")
ComponentHelper.SetActive(singleCellTwoDComp)
 
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
       
    start1 =(singleCellTwoDComp.Content.DatumPoints[0]).Position
    end1 = (singleCellTwoDComp.Content.DatumPoints[1]).Position
    start2 =(singleCellTwoDComp.Content.DatumPoints[2]).Position
    end2 = (singleCellTwoDComp.Content.DatumPoints[3]).Position
    
    while singleCellTwoDComp.Content.DatumPoints.Count > 0:
        singleCellTwoDComp.Content.DatumPoints[0].Delete()
        
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

num = singleCellTwoDComp.Content.Bodies.Count-1
t=0
while t < num:
    selectionTarget = BodySelection.Create(singleCellTwoDComp.Content.Bodies[num-t])
    selectionOthers = BodySelection.Create(singleCellTwoDComp.Content.Bodies[num-1-t])
    result = Combine.Merge( selectionTarget , selectionOthers)
    t+=1

RenameObject.Execute(BodySelection.Create(singleCellTwoDComp.Content.Bodies[0]), 'Combined_Surface')
    
#move = Move.Rotate(seloc, Line.Create(Point.Origin, Direction.DirX), DEG(90), MoveOptions())

#######################################################################

Selection.Clear()
ComponentHelper.SetRootActive()
mode = ViewHelper.ViewProjection.Top
result = ViewHelper.SetProjection(mode)
ViewHelper.ZoomToEntity(PartSelection.Create(GetRootPart()))
