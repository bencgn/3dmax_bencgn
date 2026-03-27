-- Define MacroScripts that will be executed when clicking menu items
macroScript Run_CheckSameColorMtl
category:"BENCGNDEMO"
buttonText:"Check Same Color Material"
tooltip:"Run checksameColormtl.py"
(
    on execute do
    (
        try( python.ExecuteFile @"d:\3dmax_bencgn\3dmax_bencgn\3DsMax Script\checksameColormtl.py" ) catch()
    )
)

macroScript Run_IDMaterial
category:"BENCGNDEMO"
buttonText:"ID Material Editor"
tooltip:"Run IDmaterial.py"
(
    on execute do
    (
        try( python.ExecuteFile @"d:\3dmax_bencgn\3dmax_bencgn\3DsMax Script\IDmaterial.py" ) catch()
    )
)

macroScript Run_DeleteFace
category:"BENCGNDEMO"
buttonText:"Delete Face"
tooltip:"Run deleteface.py"
(
    on execute do
    (
        try( python.ExecuteFile @"d:\3dmax_bencgn\3dmax_bencgn\3DsMax Script\deleteface.py" ) catch()
    )
)

macroScript Run_CheckMaterial
category:"BENCGNDEMO"
buttonText:"Check Material"
tooltip:"Run checkmaterial.py"
(
    on execute do
    (
        try( python.ExecuteFile @"d:\3dmax_bencgn\3dmax_bencgn\3DsMax Script\checkmaterial.py" ) catch()
    )
)

macroScript Run_InstanceReplace
category:"BENCGNDEMO"
buttonText:"Instance Replace"
tooltip:"Run instance replace.ms"
(
    on execute do
    (
        try( fileIn @"d:\3dmax_bencgn\3dmax_bencgn\3DsMax Script\instance replace.ms" ) catch()
    )
)

-- Execute in a block to avoid top-level local declaration errors
(
    -- Check 3ds Max version to use the correct Menu API
    local maxVer = (maxVersion())[1]

    if maxVer >= 27000 then
    (
        -- ============== 3ds Max 2025+ Hybrid Python Qt Injection ==============
        global pyMenuScript2025 = "
import qtmax
from PySide6 import QtWidgets, QtCore
import pymxs

def inject_cui_menu():
    try:
        main_window = qtmax.GetQMaxMainWindow()
        menu_bar = main_window.menuBar()
        
        # Remove old if exists
        for action in menu_bar.actions():
            if action.text() == 'BENCGNDEMO':
                menu_bar.removeAction(action)
                
        bencgn_menu = QtWidgets.QMenu('BENCGNDEMO', main_window)
        
        act1 = bencgn_menu.addAction('Check Same Color Mtl')
        act1.triggered.connect(lambda: pymxs.runtime.macros.run('BENCGNDEMO', 'Run_CheckSameColorMtl'))
        
        act2 = bencgn_menu.addAction('ID Material Editor')
        act2.triggered.connect(lambda: pymxs.runtime.macros.run('BENCGNDEMO', 'Run_IDMaterial'))
        
        bencgn_menu.addSeparator()
        
        act3 = bencgn_menu.addAction('Delete Face')
        act3.triggered.connect(lambda: pymxs.runtime.macros.run('BENCGNDEMO', 'Run_DeleteFace'))
        
        act4 = bencgn_menu.addAction('Check Material')
        act4.triggered.connect(lambda: pymxs.runtime.macros.run('BENCGNDEMO', 'Run_CheckMaterial'))
        
        act5 = bencgn_menu.addAction('Instance Replace')
        act5.triggered.connect(lambda: pymxs.runtime.macros.run('BENCGNDEMO', 'Run_InstanceReplace'))
        
        menu_bar.addMenu(bencgn_menu)
        print('Menu BENCGNDEMO mapped via PySide6 to Max 2025 QMenuBar.')
    except Exception as e:
        print('Error injecting menu:', e)

# Trigger 2.5 seconds after the CUI callback fires, to ensure Workspaces have finished loading UI!
QtCore.QTimer.singleShot(2500, inject_cui_menu)
"
        global ExecutePyMenu2025
        fn ExecutePyMenu2025 = (
            try ( python.Execute pyMenuScript2025 ) catch()
        )
        
        -- Móc trực tiếp vào sự kiện 'cuiRegisterMenus' - Đây là lúc Max 2025 đập đi xây lại giao diện!
        callbacks.removeScripts id:#BencgnCuiMenu
        callbacks.addScript #cuiRegisterMenus "ExecutePyMenu2025()" id:#BencgnCuiMenu
        
        -- Kích hoạt ngay lập tức nếu bạn load code này bằng tay lần đầu
        ExecutePyMenu2025()
        print "BENCGNDEMO queued for PySide6 Injection (Max 2025 Hybrid)..."
    )
    else
    (
        -- ============== 3ds Max Pre-2025 Legacy menuMan System ==============
        fn createBencgnLegacyMenu =
        (
            local mainMenu = menuMan.getMainMenuBar()
            local menuName = "BENCGNDEMO"
            
            -- Create new SubMenu
            local newMenu = menuMan.createMenu menuName
            local item1 = menuMan.createActionItem "Run_CheckSameColorMtl" "BENCGNDEMO"
            local item2 = menuMan.createActionItem "Run_IDMaterial" "BENCGNDEMO"
            local sep1 = menuMan.createSeparatorItem()
            local item3 = menuMan.createActionItem "Run_DeleteFace" "BENCGNDEMO"
            local item4 = menuMan.createActionItem "Run_CheckMaterial" "BENCGNDEMO"
            local item5 = menuMan.createActionItem "Run_InstanceReplace" "BENCGNDEMO"
            
            newMenu.addItem item1 -1
            newMenu.addItem item2 -1
            newMenu.addItem sep1 -1
            newMenu.addItem item3 -1
            newMenu.addItem item4 -1
            newMenu.addItem item5 -1

            local subMenuItem = menuMan.createSubMenuItem menuName newMenu
            mainMenu.addItem subMenuItem -1
            menuMan.updateMenuBar()
            print "Menu 'BENCGNDEMO' created successfully (Legacy system)."
        )

        createBencgnLegacyMenu()
    )
)
