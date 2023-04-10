# 12 2D Combine Merge
# Combine and merge 2D surfaces
# Emrah Dursun. 23/02/2023. 
# Emrah Dursun. 09/04/2023. 

#Create a parent componet and move all bodies in it
mergedComp = ComponentHelper.CreateAtRoot("Merged Component")
selectedBodies = BodySelection.Create(GetRootPart().GetAllBodies())
result = ComponentHelper.MoveBodiesToComponent( selectedBodies ,mergedComp , False , None)

# new approach to Merge Bodies
numberOfUnmergedBodies = mergedComp.Content.Bodies.Count-1
while numberOfUnmergedBodies > 0:
    mainBody = BodySelection.Create(mergedComp.Content.Bodies[0])
    secondaryBodies = BodySelection.Create(mergedComp.Content.Bodies[numberOfUnmergedBodies])
    result = Combine.Merge(mainBody, secondaryBodies)
    numberOfUnmergedBodies -=1
    if numberOfUnmergedBodies == 0:
        RenameObject.Execute(BodySelection.Create(mergedComp.Content.Bodies[0]), 'Merged Bodies')
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