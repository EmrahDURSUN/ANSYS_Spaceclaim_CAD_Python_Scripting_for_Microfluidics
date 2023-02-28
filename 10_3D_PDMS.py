# 10 3D PDMS
# Create PDMS cover layer
# Emrah Dursun. 23/02/2023. 

from SpaceClaim.Api.V22.Geometry import Point
import math

#ClearAll()
#Layers.DeleteEmpties()

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
numZElements=Parameters.Z_direction_repeat
fluidChipLength = Parameters.FluidChip_Length
fluidChipWidth = Parameters.FluidChip_Width
# End Parameters

# Create Component and activate it
pdmsComp = ComponentHelper.CreateAtRoot("PDMS")
ComponentHelper.SetActive(pdmsComp)

# Parameter modifications

# half Length half widht
hWi = fluidChipWidth/2
hLe = fluidChipLength/2
circleR = MM(0.5)
circleGap = MM(3)
circleStartY = -(-hLe+(2*circleGap))
#number of inlets 4
numInlet= 4
circleStartX= -hWi + ( ( fluidChipWidth-((numInlet-1)*circleGap)) / 2 )

# Set Sketch Plane
sectionPlane = Plane.PlaneXY
result = ViewHelper.SetSketchPlane(sectionPlane, None)

# Sketch Rectangle
point1 = Point2D.Create(-hWi,-hLe)
point2 = Point2D.Create(hWi,-hLe)
point3 = Point2D.Create(hWi,hLe)
result = SketchRectangle.Create(point1, point2, point3)

# run nested while loops to create circles at their colcations
m=0
while m < 2:
    t=0
    while t < numInlet:
        # Sketch Circle
        origin = Point2D.Create(circleStartX + t*circleGap,  circleStartY)
        result = SketchCircle.Create(origin, circleR)
        t+=1
    circleStartY=-1*circleStartY
    m+=1

# Solidify Sketch
mode = InteractionMode.Solid
result = ViewHelper.SetViewMode(mode, None)
# EndBlock

# Extrude 1 Face on z direction 
selection=FaceSelection.Create( pdmsComp.Content.Bodies[0].Faces[0] )
options = ExtrudeFaceOptions()
options.ExtrudeType = ExtrudeType.Cut
result = ExtrudeFaces.Execute(selection, subThick, options)
# EndBlock

# Modify Color

selectedBody = BodySelection.Create(pdmsComp.Content.Bodies[0])
options = SetColorOptions()
options.FaceColorTarget = FaceColorTarget.Body
ColorHelper.SetColor(selectedBody, options, Color.FromArgb(102, 143, 175, 159))
# EndBlock

# Set Style
selectedBody = BodySelection.Create(pdmsComp.Content.Bodies[0])
ColorHelper.SetFillStyle(selectedBody, FillStyle.Transparent)
# EndBlock

mode = ViewHelper.ViewProjection.Isometric
result = ViewHelper.SetProjection(mode)
ViewHelper.ZoomToEntity(PartSelection.Create(GetRootPart()))

ComponentHelper.SetRootActive()
# comp = ComponentHelper.CopyToRoot(comp)


###########