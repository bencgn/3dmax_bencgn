rollout testFocus "Test Focus"
(
  edittext text1 "Test"
  edittext text2 "Focus"
)
createDialog testFocus 200 100
setFocus testFocus.text2 -- the second text field gets focus!