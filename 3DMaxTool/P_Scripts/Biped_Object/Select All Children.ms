fn selectAllChildren =
(
for obj in selection do
(
if obj.children != undefined do
(
selectmore obj.children
)
)
)
selectAllChildren()