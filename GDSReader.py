import gdstk

gcString = "gc"

lib = gdstk.read_gds('fabrun5.gds')
lib1 = lib.cells

circuits = []
namesUsed = []

class Circuit:
  def __init__(self, name = "", origin = [0,0], ports = []):
    self.name = name
    self.origin = origin
    self.ports = ports
    
  def print(self):
      print(self.name + " with origin (" + str(self.origin[0]) + "," + str(self.origin[1]) + ") which contains:")
      for i in self.ports:
        i.print()



class Port:
  def __init__(self, position = [0,0], job = ""):
    self.position = position
    self.job = job

  def print(self):
      print(self.job + " port with position (" + str(self.position[0]) + "," + str(self.position[1]) + ")")


class Dependency:
    def __init__(self, refs=[], isCircuit=False, name=""):
        self.refs = refs
        self.isCircuit = isCircuit
        self.name = name


class Unit:
    def __init__(self, name="", origin=[]):
        self.name = name
        self.origin = origin


class refObject:
    def __init__(self, name="", origin=[]):
        self.name = name
        self.origin = origin


def containsGC(cell):
    references = cell.references
    for i in references:
        if gcString in str(i):
            return True
    return False

def getName(referenceString):
    string = str(referenceString)[19:]
    num = string.find("'")
    string = string[:num]
    return string

def createRefObjects(cell, namesUsed):
    refObjects = []
    refs = cell.references
    for i in refs:
        refName = getName(i)
        num = 1
        while ((refName + "_" + str(num)) in namesUsed):
            num += 1
        refObjects.append(refObject((refName + "_" + str(num)), i.origin))
        namesUsed.append((refName + "_" + str(num)))
    return refObjects



def dig(Units, dependencies, circuits, isFirst):
    newUnits = []
    nameToFind = ""
    for i in Units:
        if isFirst:
            nameToFind = i.name[:-2]
        else:
            nameToFind = i.name[i.name.rindex(':')+1:]
            nameToFind = nameToFind[:-2]
        dependencyMatch = [x for x in dependencies if x.name == nameToFind]
        if len(dependencyMatch) != 0:
            if (dependencyMatch[0].isCircuit):
                alreadyInList = [x for x in circuits if x.name == i.name]
                if len(alreadyInList) == 0:
                    circuits.append(Circuit(i.name, i.origin, []))
            else:
                for j in (dependencyMatch[0].refs):
                    if (len(j.name) > 5):
                        newUnit = Unit((i.name + "::" + j.name), [i.origin[0]+j.origin[0], i.origin[1]+j.origin[1]])
                        newUnits.append(newUnit)
            dig(newUnits, dependencies, circuits, False)
        else:
            print("Could not find match")
    

dependencies = []


cells = lib1[-1].dependencies(True)
for i in cells:
    if containsGC(i):
        dependencies.append(Dependency(createRefObjects(i, namesUsed), True, i.name))   
    else:
        dependencies.append(Dependency(createRefObjects(i, namesUsed), False, i.name))


Units = []
beforeUnits = lib1[-1].references
beforeUnits = [x for x in beforeUnits if "gc" not in getName(x) and "Wave" not in getName(x)]
beforeUnits = [x for x in beforeUnits if len(getName(x)) > 2]

for i in beforeUnits:
    if (str(i.repetition) != "No Repetition"):
        rows = i.repetition.rows
        columns = i.repetition.columns
        spacing = i.repetition.spacing
        origin = i.origin
        num = 1
        for r in range(rows):
            for c in range(columns):
                Units.append(Unit(getName(i) + "_" + str(num), [i.origin[0] + (r * spacing[0]), i.origin[1] + (c * spacing[1])]))
                num = num + 1
    else:
        Units.append(Unit(getName(i), i.origin))


dig(Units, dependencies, circuits, True)


for i in circuits:
    nameToFind = i.name[i.name.rindex(':')+1:]
    nameToFind = nameToFind[:-2]
    dependencyMatch = [x for x in dependencies if x.name == nameToFind]
    ports = []
    for j in dependencyMatch[0].refs:
        if "gc" in j.name:
            ports.append(Port([i.origin[0]+j.origin[0], i.origin[1]+j.origin[1]], "Lasor"))
    i.ports = ports


for h in circuits:
    h.print()
