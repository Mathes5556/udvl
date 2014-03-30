# na cviceni cislo 5 sme si ukazovali metodu ako pouzit kniznicu pickle ,
#  ta vsak od pythnu 3.x robi s BytesIO a nie zo STringIo ako je v testoch
# ,kniznica teda vyzdauje vyzaduje BytesIO ,aby to fungovalo staci prepisat v testoch na dvoch miestach
# zo StringIO na BytesIO(riadok 103 a 105)
#         oF = io.BytesIO()
#         varMap.writeToFile(oF)
#         iF = io.BytesIO(oF.getvalue())
# po tejto zmene zbehnu vsetkky testy.. dakujem za pochopenie

import pickle

class VariableMap:
    def __init__(self, variables = []):
        self.map = {}
        self.max = 0
        for v in variables:
            self.addVar(v)

    def addVar(self, variable):
        if not variable in self.map:
            self.max += 1
            self.map[variable] = self.max
        return self
            
    def __getitem__(self, variable):
        return self.map[variable]

    def get(self, variable):
        return self.map[variable]

    def keys(self):
        return self.map.keys()

    def toString(self):
        return str(self.map)

    def reverse(self):
        r = {}
        for k,v in self.map.items():
            r[v] = k
        return r
    
    def writeToFile(self, outFile):
        pickle.dump(self, outFile)

        # zapisat tuto triedu do dakeho suboru


    @staticmethod
    def readFromFile(inFile):

        return pickle.load(inFile)
        #m = VariableMap([])
        # nacitam do m

        
class CnfLit:
    def __init__(self, name):
        self.name = name
        self.neg = False

    @staticmethod
    def Not(name):
        r = CnfLit(name)
        r.neg = True
        return r

    def __neg__(self):
        r = CnfLit(self.name)
        r.neg = not self.neg
        return r

    def toString(self):
        if self.neg :
            return "-" + self.name
        else:
            return self.name

    def eval(self, interpretation):
        if self.neg:
            return not interpretation[self.name]
        else:
            return interpretation[self.name] 

    def extendVarMap(self, varMap):
        #doplna dany literal (self) do mapy v varMap(arita 1)
        varMap.addVar(self.name)

    def  writeToFile(self,outFile, varMap):
        if self.neg:
            outFile.write("-")
        outFile.write(str(varMap[self.name]))
        
    # nemusi mat read
class CnfClause(list):
    def __init__(self, literals):
        list.__init__(self,literals)

    # to exxtendvarmapr preiturej cez kazdy literal a zapisem ho do varmapy
    # Clausa je disjunkcia cize def eval bude pravda ak aspon n
    def toString(self):
        # final = ""
        # for lit in self:
        #     final
        return " ".join([lit.toString() for lit in self])

    def eval(self, interpretation):
        return any([x.eval(interpretation) for x in self])
        # for each in self:
        #     if each.eval(interpretation):
        #         return True
        # else:
        #     return False

    def extendVarMap(self, varMap):
        for lit in self:
            lit.extendVarMap(varMap)

    def writeToFile(self, outFile, varMap):
        for lit in self:
            lit.writeToFile(outFile, varMap)
            outFile.write(" ")
        outFile.write("0\n")

    @staticmethod
    def readFromFile(inFile, varMap):
        reverseMap = varMap.reverse()
        clause = CnfClause([])
        line = inFile.readline()
        numbers = [int(x) for x in line.split()]
        if len(numbers) == 0 :
            raise IOError("prazdny riadok")
        if numbers[-1] != 0:
            raise IOError("zly riadok")

        for n in numbers[:-1]:
            name = reverseMap[abs(n)]
            lit = CnfLit(name)
            lit.neg = n < 0
            clause.append(lit)
        return clause

class Cnf(list):
    def __init__(self, literals):
        list.__init__(self,literals)

    def extendVarMap(self, varMap):
        for clause in self:
            clause.extendVarMap(varMap)

    def toString(self):
        string = ""
        for vyraz in self:
            string += vyraz.toString()
            string += "\n"
        return  string

    def writeToFile(self, outFile, varMap):
        for clause in self:
            clause.writeToFile(outFile, varMap)

    def eval(self, interpretation):
        return all([ x.eval(interpretation) for x in self])

    # ma to byt list CnfClause  stym ze citat budem takym spsoboom ze bude citat
    #podobne ako CnfClause az pokym to nepadne ...  Try ; except ;
    @staticmethod
    def readFromFile(inFile, varMap):
        cnf = Cnf([])
        try:
            while(True):
                temp = CnfClause.readFromFile(inFile, varMap)
                cnf.append(temp)
        except IOError:
            pass
        return cnf


                   
if __name__ == "__main__":
    cnf = VariableMap(["a"])
    print( cnf.keys ())
    lit = CnfLit('a')
    list_cnf = CnfClause([CnfLit('a')])
    print(list_cnf)
