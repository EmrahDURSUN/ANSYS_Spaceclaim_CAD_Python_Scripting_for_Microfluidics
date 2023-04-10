# 01 2D Single Cell
# Create two-dimensional fluid region
# Emrah Dursun. 20/03/2023.
# Emrah Dursun. 05/04/2023.
from SpaceClaim.Api.V22.Geometry import Point
import math

Selection.Empty()
ClearAll()
Layers.DeleteEmpties()

# Get Input Parameters
periodicity=Parameters.Periodicity
radius=Parameters.Radius
width=Parameters.Width 
angle=Parameters.Angle
oangle=Parameters.OpeningAngle
channelWidth=Parameters.Channel_Width
# End Parameters
  
# Create Component and activate it
singleCellTwoDComp = ComponentHelper.CreateAtRoot("2D Single Cell Cmp")
ComponentHelper.SetActive(singleCellTwoDComp)
 
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
    start1 = singleCellTwoDComp.Content.DatumPoints[0].Position
    end1 = singleCellTwoDComp.Content.DatumPoints[1].Position
    start2 = singleCellTwoDComp.Content.DatumPoints[2].Position
    end2 = singleCellTwoDComp.Content.DatumPoints[3].Position
    
    # Delete DatumPoints
    while singleCellTwoDComp.Content.DatumPoints.Count > 0:
        singleCellTwoDComp.Content.DatumPoints[0].Delete()
    
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
body = result.CreatedBody.SetName('Channel')

# Merge all surfaces and rename
num = singleCellTwoDComp.Content.Bodies.Count-1
t=0
while t < num:
    selectionTarget = BodySelection.Create(singleCellTwoDComp.Content.Bodies[num-t])
    selectionOthers = BodySelection.Create(singleCellTwoDComp.Content.Bodies[num-1-t])
    result = Combine.Merge( selectionTarget , selectionOthers)
    t+=1
RenameObject.Execute(BodySelection.Create(singleCellTwoDComp.Content.Bodies[0]), 'SingleCellFluidDomain')

# Ending Arrangements
Selection.Clear()
ComponentHelper.SetRootActive()
mode = ViewHelper.ViewProjection.Top
result = ViewHelper.SetProjection(mode)
ViewHelper.ZoomToEntity(PartSelection.Create(GetRootPart()))