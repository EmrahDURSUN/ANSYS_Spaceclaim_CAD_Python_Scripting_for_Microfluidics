# 12 2D Combine Merge
# Combine and merge 2D surfaces
# Emrah Dursun. 23/02/203. 



########Does Not Works

numC = GetRootPart().GetAllComponents().Count
while numC > 0 :
    print("Number of Components is = " + numC.ToString())

    # Move Cell 0
    selectedBodies = Selection.Create(GetActivePart().GetAllBodies())
    #pdmsComp = ComponentHelper.CreateAtRoot("PjdhgfndfgnDMS")
    #ComponentHelper.SetActive(pdmsComp)
    selectedComp = PartSelection.Create(GetRootPart())
    #= ComponentSelection.CreateByNames(pdmsComp.GetName())
    result = ComponentHelper.MoveBodiesToComponent(selectedBodies, selectedComp, False)
    
    ComponentHelper.DeleteEmptyComponents(GetRootPart())
    pdmsComp = ComponentHelper.CreateAtRoot("PDMS")
    #ComponentHelper.SetRootActive()
    # EndBlock
    break


#when there are many components these function will create new comp and move all bodies into it, then combine them
numC =  GetRootPart().Components.Count
while numC ==2: 
    print(GetRootPart().Components.Count)    
    
    selection = BodySelection.Create(GetRootPart().Components[1].Content.GetAllBodies())
    
    component = PartSelection.Create(GetRootPart().Components[0].Content)
    
    result = ComponentHelper.MoveBodiesToComponent(selection, component, False, None)
    
    selection = PartSelection.Create(GetRootPart().Components[0].Content)
    result = RenameObject.Execute(selection,"Inlet_Cell_Outlet_Combined")
    
    selection = ComponentSelection.Create(GetRootPart().Components[1])
    result = Delete.Execute(selection)
    
    selectionB = BodySelection.Create(GetRootPart().Components[0].Content.Bodies )
    result = Combine.Merge(selectionB)
    selection=BodySelection.Create(GetRootPart().Components[0].Content.Bodies[0])
    RenameObject.Execute(selection, 'Combined_Surface')
    numC +=1
    
# when there are only bodies without component: create a component and move all in then combine them    
numC =  GetRootPart().Components.Count
numB = GetRootPart().Bodies.Count
while numC  ==  0 and numB >1:
    selection = BodySelection.Create(GetRootPart().Bodies)
    result = ComponentHelper.MoveBodiesToComponent(selection)
    selection = PartSelection.Create(GetRootPart().Components[0].Content)
    result = RenameObject.Execute(selection,"Combined_Surface")
        
    selection = BodySelection.Create(GetRootPart().Components[0].Content.GetAllBodies())
    result = Combine.Merge(selection)
    numB ==1
    break
       
# When there are different surfaces round the channels and touches the channels, this function will combine them
numC =  GetRootPart().Components.Count
numBb = GetRootPart().Bodies.Count + GetRootPart().Components[0].Content.Bodies.Count
while numC == 1 and numBb >1:
    print(GetRootPart().Components.Count)    
    print(GetRootPart().Bodies.Count)   
    
    tools = BodySelection.Create(GetRootPart().Bodies[0])
    
    #component = ComponentSelection.Create(GetRootPart().Components[0]) 
    
    #result = ComponentHelper.MoveBodiesToComponent(selections, component, False)
    
    targets= BodySelection.Create(GetRootPart().Components[0].Content.Bodies)
     
    result = Combine.Merge(targets, tools)   
   
    
    selection=BodySelection.Create(GetRootPart().Components[0].Content.Bodies[0])
    RenameObject.Execute(selection, 'Combined_Surface')
    if GetRootPart().Bodies.Count == 0:
        numC+=1 
    break


#######################################################################

# Create a componet and move all bodies in it
#multiCellChannelComp = ComponentHelper.CreateAtRoot("Multi-Cell-Channel")
#selectedBodies = BodySelection.Create(GetRootPart().GetAllBodies())
#result = ComponentHelper.MoveBodiesToComponent( selectedBodies ,multiCellChannelComp, False , None)
#multiChannelComp.Delete()
#multiCellTwoDComp.Delete()

# Create a componet and move all bodies in it and Merge them
combinedAndMergedComp = ComponentHelper.CreateAtRoot("Combined and Merged")

sel1 = Selection.Create(multiCellTwoDComp.Content.Bodies)
sel2  = Selection.Create(multiChannelComp.Content.Bodies)
selectedBodies = Selection.SelectAll(sel1 + sel2)
result = ComponentHelper.MoveBodiesToComponent ( selectedBodies ,combinedAndMergedComp, False , None)
multiChannelComp.Delete()
multiCellTwoDComp.Delete()

selectedBodies = BodySelection.Create(multiCellChannelComp.Content.Bodies)
result = Combine.Merge(selectedBodies)

################