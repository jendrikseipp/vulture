# Vulture sometimes incorrectly classifies code as unused. You can use
# a separate python file to signal that the code is actually used:
#
# vulture vulture.py whitelist.py

from vulture import Vulture

v = Vulture()

v.visit_FunctionDef
v.visit_Attribute
v.visit_Name
v.visit_Assign
v.visit_For
v.visit_comprehension
v.visit_ClassDef
v.visit_Str
