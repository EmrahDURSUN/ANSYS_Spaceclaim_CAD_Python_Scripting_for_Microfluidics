# 08 3D Fluid Domain Single Unit Cell
# Create a 3D fluid domain from a unit cell
# Emrah Dursun. 23/02/2023. 

# Python Script, API Version = V22 Beta
from SpaceClaim.Api.V22.Geometry import Point
import math

ClearAll()
Layers.DeleteEmpties()

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
# End Parameters

# Constructor Show Each Layer Seperately 
def showLayersSeparated(distance=0):
    t = 1
    while t <6:
        GetRootPart().Components[0].Content.Bodies[t].Transform(Matrix.CreateTranslation(Vector.Create(0,0,distance)))
        distance+=distance
        t = t + 1
        
def createPlane(ang):
   if (ang != 0):      
       plane = DatumPlaneCreator.Create(Point.Origin, -Direction.DirZ, -Direction.DirX, False)
       selectionPlane = Selection.Create(GetRootPart().DatumPlanes[0])
       result = RenameObject.Execute(selectionPlane, (180*ang/math.pi).ToString()+' DegPlane')
       result = Move.Rotate(selectionPlane, Move.GetAxis(selectionPlane, HandleAxis.X), ang, MoveOptions())
       return result

## Create Substrate
#result = BlockBody.Create(Point.Create(MM(-per), MM(-per), MM(0)), Point.Create(MM(per), MM(per), MM(-subThick)), ExtrudeType.ForceAdd)
#body = result.CreatedBody.SetName('Substrate')
#ColorHelper.SetColor(Selection.CreateByNames('Substrate'), Color.FromArgb(255, 128, 128, 255))
## EndBlock


## Create GoldLayer
#result = BlockBody.Create(Point.Create(MM(-per), MM(-per), MM(0)), Point.Create(MM(per), MM(per), MM(hAu)), ExtrudeType.ForceIndependent)
#body = result.CreatedBody.SetName('Gold Layer')
#ColorHelper.SetColor(Selection.CreateByNames('Gold Layer'), Color.Gold)
## EndBlock

  
# Beginning of Face Cut   
######################################################################

gap = dEtch/radius*(180/math.pi)
dnaGap = dnaT/(radius)*(180/math.pi)
dnaGapUzakFar = dnaT/(radius + width - dnaT)*(180/math.pi)
    
def pointAllocateFirst( distP, angP):
    seloc =Selection.Create(DatumPointCreator.Create(Point.Create(0, MM(distP), 0)).CreatedPoint)
    move = Move.Rotate(seloc, Line.Create(Point.Origin, Direction.DirZ),  angP, MoveOptions())
    
def pointAllocateSecond(distP,angP):
    seloc =Selection.Create(DatumPointCreator.Create(Point.Create(0, MM(distP), 0)).CreatedPoint)
    move = Move.Rotate(seloc, Line.Create(Point.Origin, Direction.DirZ), angP, MoveOptions())
    
def surfaceCutOperation(ring, nearPoint, farPoint, rotation, extrudeDistance):
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
       
    start1 =(GetRootPart().DatumPoints[0]).Position
    end1 = (GetRootPart().DatumPoints[1]).Position
    start2 =(GetRootPart().DatumPoints[2]).Position
    end2 = (GetRootPart().DatumPoints[3]).Position
    
    while GetRootPart().DatumPoints.Count > 0:
        GetRootPart().DatumPoints[0].Delete()
        
    curves = List[ITrimmedCurve]()
    curves.Add(CurveSegment.CreateArc(Point.Origin,start1,end1, -Direction.DirZ))
    curves.Add(CurveSegment.CreateArc(Point.Origin,start2,end2, -Direction.DirZ))
    curves.Add(CurveSegment.Create(start1,start2))
    curves.Add(CurveSegment.Create(end1,end2))
        
    designResult = PlanarBody.Create(Plane.PlaneXY, curves)
    designBody1 = designResult.CreatedBody
        
    # Cut substrate
    if (ring == 1 or ring == 2 or ring == 4):
        selection = Selection.Create(designBody1.Faces)
        options = ExtrudeFaceOptions()
#        off = OffsetFaces.Execute(selection, offset, OffsetFaceOptions())
        options.ExtrudeType = ExtrudeType.ForceAdd
        result = ExtrudeFaces.Execute(selection, extrudeDistance, options)   # ForceCut
    if (ring == 3 or ring == 5):
        selection = Selection.Create(designBody1.Faces)
        options = ExtrudeFaceOptions()
#        off = OffsetFaces.Execute(selection, offset, OffsetFaceOptions())
        options.ExtrudeType = ExtrudeType.ForceAdd
        result = ExtrudeFaces.Execute(selection, extrudeDistance, options)   # ForceCut
    return result


######################################################################
# Cut Operations
#surfaceCutOperation(ring, nearPoint,     farPoint,                            rotation,                                              offset,       extrudeDistance)
surfaceCutOperation( 1, radius,             radius+width,                    DEG(180) +angle ,                                             hAu)  #Cut Up
surfaceCutOperation( 1, radius - dEtch,  radius + width + dEtch,      DEG(180) + angle +DEG(gap),                        - hEtch)  #Cut Down
surfaceCutOperation( 2, radius,             radius+width,                     DEG(180) - angle - oangle,                              hAu)  #Cut Up
surfaceCutOperation( 2, radius - dEtch,  radius + width + dEtch,       DEG(180) - angle -oangle + DEG(gap),         -hEtch)  #Cut Down
#######################################################################


# Cut Fluid Channel
result = BlockBody.Create(Point.Create(MM(-channelWidth/2), MM(-per), MM(0)), Point.Create(MM(channelWidth/2), MM(per), MM(hAu)), ExtrudeType.ForceAdd)
#body = result.CreatedBody.SetName('Gold Layer')
#ColorHelper.SetColor(Selection.CreateByNames('Gold Layer'), Color.Gold)
# EndBlock

# Cut Fluid Channel
result = BlockBody.Create(Point.Create(MM(-channelWidth/2-dEtch), MM(-per), MM(-hEtch)), Point.Create(MM(channelWidth/2+dEtch), MM(per), MM(0)), ExtrudeType.Add)
#body = result.CreatedBody.SetName('Gold Layer')
#ColorHelper.SetColor(Selection.CreateByNames('Gold Layer'), Color.Gold)
# EndBlock


######################################################################

######################################################################




######################################################################

######################################################################

## Create Radiation Region
#upperFace =( (opRegion - subThick) / 2 ) + hAu
#lowerFace = opRegion - upperFace + hAu
#result = BlockBody.Create(Point.Create(MM(-per), MM(-per), MM(subThick+hAu)), Point.Create(MM(per), MM(per), MM(hAu)), ExtrudeType.ForceIndependent)
#result.CreatedBody.SetName('Region')

#selection = Selection.CreateByNames('Region')
#options = SetColorOptions()
#options.FaceColorTarget = FaceColorTarget.Body
#ColorHelper.SetColor(selection, options,  Color.FromArgb(255, 192, 192, 192))
#ColorHelper.SetFillStyle(selection, FillStyle.Transparent)
## EndBlock


## Change Object Visibility
#selection = Selection.CreateByNames('Region')
#visibility = VisibilityType.Hide
#inSelectedView = False
#faceLevel = False
#ViewHelper.SetObjectVisibility(selection, visibility, inSelectedView, faceLevel)
## EndBlock

###############################################################

# Fix 2 Interferences
#selection = Selection.CreateByNames('Substrate','ChromiumForAdhesion','Gold Layer','ChromiumForSurfacePassivation',"DNA Large Ring","DNA Small Ring")
options = FixInterferenceOptions()
options.CutSmallerBody = True
result = FixInterference.FindAndFix(options)
# EndBlock

## Change Object Visibility
#selection = Selection.CreateByNames('Region')
#visibility = VisibilityType.Show
#ViewHelper.SetObjectVisibility(selection,visibility,False,False)

###############################################################

# Move All Bodies to New Component and Rename it
selection = BodySelection.Create(GetRootPart().GetAllBodies())
result = ComponentHelper.MoveBodiesToComponent(selection, None)
# Rename 'Component1' to 'Single_Cell'
selection = PartSelection.Create(GetRootPart().Components[0].Content)
result = RenameObject.Execute(selection,"Single_Cell")
# EndBlock

################################################################

###############################################################
###############################################################
# Set Section View and Zoom to Entity
#showLayersSeparated(0.1)
createPlane(Parameters.PlaneAngle)
#ViewHelper.SetSectionPlane(Selection.Create(GetRootPart().DatumPlanes[0]), None)
#ViewHelper.SetSectionPlane(Plane.PlaneYZ)
Selection.Clear()
#ViewHelper.ZoomToEntity()
###############################################################

## Rename 'Solid' to 'GoldLayer2'
#selection = BodySelection.Create(GetRootPart().Components[0].Content.Bodies[2])
#result = RenameObject.Execute(selection,"GoldLayer2")
## EndBlock


## Expand Tree Node
selection = Selection.Create(GetRootPart().Components[0].Content.GetAllBodies())
MergeBodies.Execute(selection,MergeBodiesOptions())


# Round Edges to show edged region

#selection1= EdgeSelection.Create(GetRootPart().Components[0].Content.Bodies[0].Faces[14].Edges)
#result = ConstantRound.Execute(selection1, MM(hEtch), ConstantRoundOptions())

Selection.Clear()
ComponentHelper.SetRootActive()
mode = ViewHelper.ViewProjection.Isometric
result = ViewHelper.SetProjection(mode)
ViewHelper.ZoomToEntity(PartSelection.Create(GetRootPart()))
# EndBlock

