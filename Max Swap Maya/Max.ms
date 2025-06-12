-- 3ds Max Script: Send to Maya and Get from Maya Tool
-- Save this as a .ms file and run in 3ds Max

(
    -- Global variables
    global transferFolder = "C:\\temp\\"
    global transferDialog
    
    -- Ensure transfer folder exists
    fn ensureTransferFolder = (
        if not doesDirectoryExist transferFolder then (
            makeDir transferFolder
        )
    )
    
    -- Send to Maya function
    fn sendToMaya = (
        ensureTransferFolder()
        
        if selection.count == 0 then (
            messageBox "Please select objects to send to Maya" title:"Send to Maya"
            return false
        )
        
        -- Generate timestamp for unique filename
        local timeStr = (localTime as string)
        timeStr = substituteString timeStr ":" "-"
        timeStr = substituteString timeStr " " "_"
        timeStr = substituteString timeStr "/" "-"
        
        local fileName = "Max_to_Maya_" + timeStr + ".fbx"
        local fullPath = transferFolder + fileName
        
        -- Export selected objects as FBX
        try (
            select selection
            exportFile fullPath #noPrompt selectedOnly:true using:FBXEXP
            messageBox ("Objects exported to Maya!\nFile: " + fileName) title:"Send to Maya"
            
            -- Copy filename to clipboard for reference
            setClipBoardText fileName
            
        ) catch (
            messageBox ("Error exporting FBX file:\n" + getCurrentException()) title:"Export Error"
        )
    )
    
    -- Get from Maya function  
    fn getFromMaya = (
        ensureTransferFolder()
        
        -- Get all FBX files from transfer folder
        local fbxFiles = getFiles (transferFolder + "*.fbx")
        
        if fbxFiles.count == 0 then (
            messageBox "No FBX files found in transfer folder" title:"Get from Maya"
            return false
        )
        
        -- Sort by modification date (newest first)
        local fileInfoArray = #()
        for f in fbxFiles do (
            local fileInfo = getFileModDate f
            append fileInfoArray #(f, fileInfo)
        )
        
        -- Sort by date
        qsort fileInfoArray (fn cmp a b = if a[2] > b[2] then -1 else 1)
        
        -- Create file selection dialog
        local fileNames = #()
        for item in fileInfoArray do (
            local shortName = filenameFromPath item[1]
            append fileNames shortName
        )
        
        -- Show file selection dialog
        local selectedIndex = 1
        if fileNames.count > 1 then (
            selectedIndex = getUserProp fileNames "Select FBX file to import:" title:"Get from Maya"
            if selectedIndex == 0 then return false
        )
        
        local selectedFile = fileInfoArray[selectedIndex][1]
        
        -- Import the selected FBX file
        try (
            importFile selectedFile #noPrompt
            messageBox ("FBX file imported successfully!\nFile: " + (filenameFromPath selectedFile)) title:"Get from Maya"
            
        ) catch (
            messageBox ("Error importing FBX file:\n" + getCurrentException()) title:"Import Error"
        )
    )
    
    -- Create UI Dialog
    rollout transferDialog "Max ? Maya Transfer" width:300 height:150 (
        
        label lblTitle "Transfer FBX between Max and Maya" align:#center
        label lblFolder "Folder: C:\\temp\\" align:#center
        
        button btnSendToMaya "Send to Maya" width:250 height:35 pos:[25,40]
        button btnGetFromMaya "Get from Maya" width:250 height:35 pos:[25,80]
        
        button btnOpenFolder "Open Transfer Folder" width:120 height:25 pos:[25,120]
        button btnRefresh "Refresh" width:100 height:25 pos:[155,120]
        
        -- Send to Maya button action
        on btnSendToMaya pressed do (
            sendToMaya()
        )
        
        -- Get from Maya button action  
        on btnGetFromMaya pressed do (
            getFromMaya()
        )
        
        -- Open folder button action
        on btnOpenFolder pressed do (
            ensureTransferFolder()
            ShellLaunch "explorer.exe" transferFolder
        )
        
        -- Refresh button action
        on btnRefresh pressed do (
            lblFolder.text = "Folder: C:\\temp\\"
        )
    )
    
    -- Show the dialog
    createDialog transferDialog
    
    -- Create macroscript for the toolbar (can be manually added to toolbar)
    macroScript MaxMayaTransfer
    category:"Max Maya Transfer"
    tooltip:"Max ? Maya Transfer Tool"
    buttonText:"M"
    (
        -- Check if dialog exists and is open
        if transferDialog != undefined and transferDialog.isDisplayed then (
            -- Close dialog if already open
            destroyDialog transferDialog
        ) else (
            -- Recreate the dialog functions and show
            (
                -- Global variables
                global transferFolder = "C:\\temp\\"
                global transferDialog
                
                -- Ensure transfer folder exists
                fn ensureTransferFolder = (
                    if not doesDirectoryExist transferFolder then (
                        makeDir transferFolder
                    )
                )
                
                -- Send to Maya function
                fn sendToMaya = (
                    ensureTransferFolder()
                    
                    if selection.count == 0 then (
                        messageBox "Please select objects to send to Maya" title:"Send to Maya"
                        return false
                    )
                    
                    -- Generate timestamp for unique filename
                    local timeStr = (localTime as string)
                    timeStr = substituteString timeStr ":" "-"
                    timeStr = substituteString timeStr " " "_"
                    timeStr = substituteString timeStr "/" "-"
                    
                    local fileName = "Max_to_Maya_" + timeStr + ".fbx"
                    local fullPath = transferFolder + fileName
                    
                    -- Export selected objects as FBX
                    try (
                        select selection
                        exportFile fullPath #noPrompt selectedOnly:true using:FBXEXP
                        messageBox ("Objects exported to Maya!\nFile: " + fileName) title:"Send to Maya"
                        
                        -- Copy filename to clipboard for reference
                        setClipBoardText fileName
                        
                    ) catch (
                        messageBox ("Error exporting FBX file:\n" + getCurrentException()) title:"Export Error"
                    )
                )
                
                -- Get from Maya function  
                fn getFromMaya = (
                    ensureTransferFolder()
                    
                    -- Get all FBX files from transfer folder
                    local fbxFiles = getFiles (transferFolder + "*.fbx")
                    
                    if fbxFiles.count == 0 then (
                        messageBox "No FBX files found in transfer folder" title:"Get from Maya"
                        return false
                    )
                    
                    -- Sort by modification date (newest first)
                    local fileInfoArray = #()
                    for f in fbxFiles do (
                        local fileInfo = getFileModDate f
                        append fileInfoArray #(f, fileInfo)
                    )
                    
                    -- Sort by date
                    qsort fileInfoArray (fn cmp a b = if a[2] > b[2] then -1 else 1)
                    
                    -- Import the newest file
                    local selectedFile = fileInfoArray[1][1]
                    
                    -- Import the selected FBX file
                    try (
                        importFile selectedFile #noPrompt
                        messageBox ("FBX file imported successfully!\nFile: " + (filenameFromPath selectedFile)) title:"Get from Maya"
                        
                    ) catch (
                        messageBox ("Error importing FBX file:\n" + getCurrentException()) title:"Import Error"
                    )
                )
                
                -- Create UI Dialog
                rollout transferDialog "Max ? Maya Transfer" width:300 height:150 (
                    
                    label lblTitle "Transfer FBX between Max and Maya" align:#center
                    label lblFolder "Folder: C:\\temp\\" align:#center
                    
                    button btnSendToMaya "Send to Maya" width:250 height:35 pos:[25,40]
                    button btnGetFromMaya "Get from Maya" width:250 height:35 pos:[25,80]
                    
                    button btnOpenFolder "Open Transfer Folder" width:120 height:25 pos:[25,120]
                    button btnRefresh "Refresh" width:100 height:25 pos:[155,120]
                    
                    -- Send to Maya button action
                    on btnSendToMaya pressed do (
                        sendToMaya()
                    )
                    
                    -- Get from Maya button action  
                    on btnGetFromMaya pressed do (
                        getFromMaya()
                    )
                    
                    -- Open folder button action
                    on btnOpenFolder pressed do (
                        ensureTransferFolder()
                        ShellLaunch "explorer.exe" transferFolder
                    )
                    
                    -- Refresh button action
                    on btnRefresh pressed do (
                        lblFolder.text = "Folder: C:\\temp\\"
                    )
                )
                
                -- Show the dialog
                createDialog transferDialog
            )
        )
    )
    
    -- Instructions for adding to toolbar
    messageBox ("Max ? Maya Transfer tool is ready!\n\nTo add 'M' button to Main Toolbar:\n1. Right-click on Main Toolbar\n2. Choose 'Customize...'\n3. Go to 'Toolbars' tab\n4. Category: 'Max Maya Transfer'\n5. Drag 'MaxMayaTransfer' to toolbar\n6. Click 'Close'\n\nOr use the dialog that just opened!") title:"Setup Instructions"
)

-- Alternative simple function calls (can be assigned to toolbar buttons)
fn quickSendToMaya = (
    transferFolder = "C:\\temp\\"
    if not doesDirectoryExist transferFolder then makeDir transferFolder
    
    if selection.count == 0 then (
        messageBox "Select objects first!"
        return false  
    )
    
    local timeStr = substituteString (substituteString (localTime as string) ":" "-") " " "_"
    local fileName = "QuickSend_" + timeStr + ".fbx" 
    exportFile (transferFolder + fileName) #noPrompt selectedOnly:true using:FBXEXP
    messageBox "Sent to Maya!"
)

fn quickGetFromMaya = (
    transferFolder = "C:\\temp\\"
    local fbxFiles = getFiles (transferFolder + "*.fbx")
    if fbxFiles.count > 0 then (
        importFile fbxFiles[fbxFiles.count] #noPrompt
        messageBox "Got from Maya!"
    ) else (
        messageBox "No files found!"
    )
)