﻿# -*- coding: utf-8 -*-
__author__ = "Konstantin Klementiev, Roman Chernikov"
__date__ = "12 Mar 2017"
import os
import pickle
import numpy as np
#import matplotlib as mpl
import matplotlib.pyplot as plt

dataDir = os.path.dirname(__file__)

elementsList = (
    'none', 'H', 'He', 'Li', 'Be', 'B', 'C', 'N', 'O', 'F', 'Ne',
    'Na', 'Mg', 'Al', 'Si', 'P', 'S', 'Cl', 'Ar', 'K', 'Ca', 'Sc', 'Ti', 'V',
    'Cr', 'Mn', 'Fe', 'Co', 'Ni', 'Cu', 'Zn', 'Ga', 'Ge', 'As', 'Se', 'Br',
    'Kr', 'Rb', 'Sr', 'Y', 'Zr', 'Nb', 'Mo', 'Tc', 'Ru', 'Rh', 'Pd', 'Ag',
    'Cd', 'In', 'Sn', 'Sb', 'Te', 'I', 'Xe', 'Cs', 'Ba', 'La', 'Ce', 'Pr',
    'Nd', 'Pm', 'Sm', 'Eu', 'Gd', 'Tb', 'Dy', 'Ho', 'Er', 'Tm', 'Yb', 'Lu',
    'Hf', 'Ta', 'W', 'Re', 'Os', 'Ir', 'Pt', 'Au', 'Hg', 'Tl', 'Pb', 'Bi',
    'Po', 'At', 'Rn', 'Fr', 'Ra', 'Ac', 'Th', 'Pa', 'U')

outType = np.single
#outType = np.double


def read_f1f2_vs_E(elZ, table):
    if table == 'Henke':
        fname = elementsList[elZ].lower() + '.nff'
    elif table == 'Chantler':
        fname = elementsList[elZ] + '.ch'
    elif table == 'BrCo':
        fname = 'BrCo.dat'
    pname = os.path.join(dataDir, 'raw', fname)

    if table == 'Henke':
        E, f1, f2 = np.loadtxt(pname, skiprows=1, unpack=True, dtype=outType)
        f1 -= elZ
    elif table == 'Chantler':
        with open(pname, "r") as f:
            for ili, li in enumerate(f):
                if "Photoelectric" in li:
                    break
        E, f1, f2 = np.loadtxt(pname, skiprows=ili+2, unpack=True,
                               usecols=[0, 1, 2], dtype=outType)
        E = E[f1 > -9999]
        f2 = f2[f1 > -9999]
        f1 = f1[f1 > -9999]
        f1 -= elZ
        E *= 1000
    elif table == 'BrCo':
        with open(pname, "r") as f:
            for li in f:
                if li.startswith("#S"):
                    fields = li.split()
                    if int(fields[1]) == elZ:
                        break
            for li in f:
                if li.startswith("#L"):
                    break
            E, f1, f2 = [], [], []
            for li in f:
                if li.startswith("#S"):
                    break
                locE, locf1, locf2 = [float(x) for x in li.split()]
                E.append(locE)
                f1.append(locf1)
                f2.append(locf2)
            E = np.array(E, dtype=outType)
            f1 = np.array(f1, dtype=outType)
            f2 = np.array(f2, dtype=outType)

    return E, f1, f2


def main():
    table = 'Henke'
#    table = 'Chantler'
#    table = 'BrCo'

    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_axes([0.15*6/7, 0.15, 0.7*6/7, 0.7])
    ax.set_xlabel(u'energy (keV)')
    ax.set_ylabel(u'f1, f2 (e/atom)')

    maxZ = 0
    out = {}
    outnp = {}
    for element in elementsList:
#    for element in ['Cu', 'Zn']:
#    for element in ['Si']:
        if element == 'none':
            continue
        elZ = elementsList.index(element)
        print(elZ, element)
        maxZ = max(maxZ, elZ)
        E, f1, f2 = read_f1f2_vs_E(elZ, table)
        out[elZ] = E, f1, f2
        outnp[element+'_E'] = E
        outnp[element+'_f1'] = f1
        outnp[element+'_f2'] = f2
        ax.plot(E*1e-3, f1+elZ, '-')
        ax.plot(E*1e-3, f2, '.')
    ax.set_ylim(0, maxZ*1.1)

    pickleName = os.path.join(dataDir, table+'.pickle')
    with open(pickleName, 'wb') as f:
        pickle.dump(out, f, protocol=2)

    saveName = os.path.join(dataDir, table+'.npz')
    with open(saveName, 'wb') as f:
        np.savez_compressed(f, **outnp)

    print("Done")

    plt.show()


if __name__ == '__main__':
    main()
