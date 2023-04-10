# 02 2D Multi Cell
# Create the fluid domain of the multi-cell structure in two dimensions
# Emrah Dursun. 23/02/2023
# Emrah Dursun. 06/04/2023 
from SpaceClaim.Api.V22.Geometry import Point
import math

# Get Input Parameters
periodicity=Parameters.Periodicity
radius=Parameters.Radius
width=Parameters.Width 
angle=Parameters.Angle
oangle=Parameters.OpeningAngle
subThick=Parameters.SubsThickness
channelWidth=Parameters.Channel_Width
numXElements=Parameters.X_direction_repeat
numYElements=Parameters.Y_direction_repeat
# End Parameters

# Modify Parameters
per=Parameters.Periodicity/2

# Create Component and activate it
multiCellTwoDComp = ComponentHelper.CreateAtRoot("2D Multi Cell")
ComponentHelper.SetActive(multiCellTwoDComp)
 
######################################################################
# Beginning Of Single Cell Fluid Domain
######################################################################

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

######################################################################
# End Of Single Cell Fluid Domain
######################################################################

# First make a copy and then move that copy along the translation vector direction  
def CopyAndTranslate(body, translation):
    result = Copy.Execute(Selection.Create(body))
    if (result.Success == True):
        newBody = result.CreatedObjects[0]        
        Move.Translate(Selection.Create(newBody), translation, MoveOptions())
        RenameObject.Execute(Selection.Create(newBody),'Merged_Cell '+ (x+1).ToString()+' x '+ y.ToString())
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

# Merge Bodies created on Y direction, they are touching eachother so they shall be merge  
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

# Ending Arrangements
Selection.Clear()
ComponentHelper.SetRootActive()
mode = ViewHelper.ViewProjection.Isometric
result = ViewHelper.SetProjection(mode)
ViewHelper.ZoomToEntity(PartSelection.Create(GetRootPart()))