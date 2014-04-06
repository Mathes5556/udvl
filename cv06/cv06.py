__author__ = 'mathes'
import subprocess
import os
import sys

class DimacsWriter(object):
    """ A helper class that writes clauses to a DIMACS format file. """
    def __init__(self, filename, mode = 'w'):
        """ Create a new writer that writes to *filename*.

            You can use ``mode='a'`` to append to an existing file
            instead of rewriting it.
        """
        self.fn = filename
        self.f = open(filename, mode)

    def filename(self):
        """ Returns the filename that this writer writes to as a string."""
        return self.fn

    def writeLiteral(self, lit):
        """ Writes a single literal (positive or negative integer).

            Use finishClause to finis this clause (write a zero).
        """
        self.f.write('{} '.format(lit))

    def finishClause(self):
        """" Finishes current clause (writes a zero).

            Note that if no clause was started (through *writeLiteral*),
            it will create an empty clause, which is always false!
        """
        self.f.write(' 0\n')
        self.f.flush()

    def writeClause(self, clause):
        """ Writes a single clause.

            *clause* must be a list of literals (positive or negative integers).
        """
        for l in clause:
            self.writeLiteral(l)
        self.finishClause()

    def writeImpl(self, left, right):
        """ Writes an implication *left* => *right*. """
        self.writeClause([-left, right])

    def closed(self):
        """ Returs True if the output file has been already closed. """
        return self.f.closed

    def close(self):
        """ Closes the output file. """
        self.f.close()


class SatSolver(object):
    """ A helper class that manages SAT solver invocation. """

    def __init__(self, solverPath = None):
        """ Creates a new SAT solver.

            Use *solverPath* to specify an optional location where to look
            for SAT solver binary (it will be looked for in a set of default
            locations).
        """

        self.paths = []
        if solverPath:
            self.paths.append(solverPath)

        if sys.platform.startswith('linux'):
            self.paths += [
#                    'minisat', 'MiniSat_v1.14_linux',
                    './minisat', './MiniSat_v1.14_linux',
                    '../tools/lin/minisat'
                ]
        elif sys.platform.startswith('win'):
            self.paths += [
                    'minisat.exe', 'MiniSat_v1.14.exe',
                    '../tools/win/minisat.exe',
                ]
        else:
            pass # empty solver paths will fall back to try 'minisat'

        # default fall for all
        self.paths.append('minisat')

    def getSolverPath(self):
        """ Returns the path to solver binary. """
        for fn in self.paths:
            try:
                subprocess.check_output([fn, '--help'], stderr = subprocess.STDOUT)
                #sys.stderr.write('using sat solver:  "%s"\n' % fn)
                return fn
            except OSError:
                pass
        raise IOError('Solver executable not found!')

    def solve(self, theory, output):
        """ Use SAT solver to solve a theory, which is either the name
            of a file (in DIMACS format) or an instance of DimacsWriter.

            Writes the SAT solvers output to a file named *output*.

            Returns a tuple (sat, solution), where sat is True or False
            and solution is a list of positive or negative integers
            (an empty list if sat is False).
        """
        if isinstance(theory, DimacsWriter):
            if not theory.closed():
                theory.close()
            theory = theory.filename()

        try:
            self.output = subprocess.check_output(
                    [self.getSolverPath(), theory, output],
                    stderr = subprocess.STDOUT,

                    )
        except subprocess.CalledProcessError:
            # minisat has weird return codes
            pass

        with open(output) as f:
            sat = f.readline()
            if sat.strip() == 'SAT':
                sol = f.readline()
                return (
                        True,
                        [int(x) for x in sol.split()][:-1]
                )
            else:
                return (False, [])


# vim: set sw=4 ts=4 sts=4 et :

# predikaty
#
#  killded(kto, koho)   -> (x,y)   je K
#  haters(kto,koho)   je  H
#  richer(x,y)    je  R

#  existuje X take ze killed(x, agatha)
#  A -> agatha
#  b - Batler
#  c -> charlses

# takze dakto zabil agatu  -> k(a,a) or k(b,a) or k(c,a)

# podmienky
# vrah vzdy nenavadi svoju obet t.j. -> pre vsetky x,y plati    k(x,y) -> h(x,y)
# vrah nikdy nie bohaci ako svoja obet t.j pre vsetky x,y plati k(x,y) -> not r(x,y)

#
# zapis do cisiel... a=0 b=1 c=1   killed=0 hate=1 richer=3
# cize potom napr r(a,c)  je 213  co moze byt trojkova sutava cize + 1 lebo nemoze to ist od jedna

import  sys


P = 3 # pocet ludi
Agatha = 0
Butler = 1
Charles = 2
w = DimacsWriter('agatha.cnf')

def killed(p1, p2):
    # p1 a p2 su vymenene
    # aby killed(X,Agatha) zodpovedalo 1, 2, 3
    return 0 * P * P + p2 * P + p1 + 1

def hates(p1, p2):
    return 1 * P * P + p1 * P + p2 + 1

def richer(p1, p2):
    return 2 * P * P + p1 * P + p2 + 1


def zapis_teoriu(w):
# Niekto v Dreadsburskom panstve zabil Agátu. Agáta,
    for x in range(P):  # pre vsetkych ludi
        w.writeLiteral(killed(x, Agatha))
    w.finishClause()
    #cize toto bolo killed(A,A) ,killed(B,A)killed(C,A)

    # vrah vzdy nenavidi obet
    for x in range(P):
        for y in range(P):
            w.writeImpl(killed(x,y), hates(x,y))

    # nie je od nich bohatsi
    for x in range(P):
        for y in range(P):
            w.writeImpl(killed(x,y), -richer(x,y))

    # hates(a,x) potom not hates(C,x)
    for x in range(P):
        w.writeImpl(hates(Agatha, x), -hates(Charles, x))

    # pre vsetkych okrem x = batler plati hates(A,x)
    # Agáta nenávidí každého okrem komorníka.
    for x in range(P):
        if x is not Butler:
            w.writeLiteral(hates(Agatha, x))
            w.finishClause()
    # w.writeClause([hates(Agatha,Agatha)])
    # w.writeClause([hates(Agatha,Butler)])


    # pre vsetky x ak not richer(x,A) potom hates(B,X)
    #Komorník nenávidí každého, kto nie je bohatší ako Agáta.
    for x in range(P):
        w.writeImpl(-richer(x, Agatha), hates(Butler, x))


    # hate(A,x) -> hate(B,x)
    #  Komorník nenávidí každého, koho nenávidí Agáta.
    for x in range(P):
        w.writeImpl(hates(Agatha, x), hates(Butler, x))


    #a posledna podmienka "Noone hates everyone"
    # pre vsetky x existuje y takzeze    not hates(x,y)  cize   pre kazde x plati ( not hate(x,A) ot not hate(x,B) ot not hate(x,C) )
    # Niet toho, kto by nenávidel všetkých.
    for x in range(P):
        w.writeClause(
                        [-hates(x,Agatha), -hates(x,Butler),  -hates(x,Charles) ]
                     )


# komorník a Karol bývajú v Dreadsburskom panstve a nikto iný okrem nich tam nebýva.
# Vrah vždy nenávidí svoje obete a nie je od nich bohatší.
# Z ľudí, ktorých Agáta nenávidí nie je taký, ktorého by Karol nenávidel.
# Agáta nenávidí každého okrem komorníka. Komorník nenávidí každého,
# kto nie je bohatší ako Agáta. Komorník nenávidí každého, koho nenávidí Agáta.
# Niet toho, kto by nenávidel všetkých. Kto zabil Agátu?




zapis_teoriu(w)
w.close()
s = SatSolver()
ok,sol = s.solve(w, 'agatha_out.txt')
if not ok:
    print('konfiltkna teoria')
    sys.exit(1)

print('riesenie: ' + repr(sol))

#tipujem ze komornik
# chceme dokazat ze z toerie vyplyva killed(B,A)
#zegovane: -killed(b,a)

vrah = Agatha
w = DimacsWriter('agatha_cnf_vrah.cnf')
zapis_teoriu(w)
w.writeClause( [-killed(vrah, Agatha)] )


w.close()
s = SatSolver()
ok,sol = s.solve(w, 'agatha_out.txt')
if not ok:
    print('ano, {} je vrahom'.format(["agatha", "burler", "charles"][vrah]))
else:
    print('problem ' + ["agatha", "burler", "charles"][vrah] + ' lebo ' + repr(sol))


