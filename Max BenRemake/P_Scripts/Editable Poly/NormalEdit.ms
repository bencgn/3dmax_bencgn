modPanel.addModToSelection (Edit_Normals ()) ui:on
actionMan.executeAction 0 "40021"
$.modifiers[#Edit_Normals].EditNormalsMod.SetSelection #{1..1341}
$.modifiers[#Edit_Normals].EditNormalsMod.Break ()
$.modifiers[#Edit_Normals].EditNormalsMod.Average ()
$.modifiers[#Edit_Normals].EditNormalsMod.Reset ()
