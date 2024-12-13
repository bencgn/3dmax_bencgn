
(


bm2 = getclipboardBitmap()
if bm2==undefined then (messagebox "First copy the image to the clipboard!!")
else
(
result=(yesNoCancelBox "Yes:ImageBox / No:RenderBox")
if result==#yes then
(
retCode = getclipboardBitmap()
if (doesFileExist ((GetDir #autoback) + "\\captureimage"))==false do
	(makeDir ((GetDir #autoback) + "\\captureimage"))
	
date=getUniversalTime()
datestring=""
for i in date do (datestring+=i as string)

	
name_=(GetDir #autoback) + "\\captureimage\\"+datestring+".png"
--name_="bb.png"
retCode.filename=name_

save retCode

b=plane()
b.length=retCode.height
b.width=retCode.width
rotate b (angleaxis 90 [1,0,0])
b.lengthsegs = 1
b.widthsegs = 1
b.backfacecull = on
	
newmat = StandardMaterial()
newmat.diffuseMap = Bitmaptexture fileName:name_
newmat.selfIllumAmount = 100
b.material=newmat
showTextureMap newmat on
move b [0,0,(b.length/2)]

)

else if result==#no then 
(
retCode = getclipboardBitmap
format "Return Code: %\n" retCode

bm2 = getclipboardBitmap()
display bm2)

else ()
)

)