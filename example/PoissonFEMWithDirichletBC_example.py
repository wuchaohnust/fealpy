#!/usr/bin/env python3
# 

import argparse

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
rc('text', usetex=True)
from mpl_toolkits.mplot3d import Axes3D

from fealpy.functionspace import LagrangeFiniteElementSpace
from fealpy.boundarycondition import DirichletBC 
from fealpy.tools.show import showmultirate

# solver
from scipy.sparse.linalg import spsolve



"""
TODO:
    1. 可以选择不同的解法器
"""

## 参数解析
parser = argparse.ArgumentParser(description=
        """
        单纯形网格（三角形、四面体）网格上任意次有限元方法
        """)

parser.add_argument('--degree',
        default=1, type=int,
        help='Lagrange 有限元空间的次数, 默认为 1 次.')

parser.add_argument('--dim',
        default=2, type=int,
        help='模型问题的维数, 默认求解 2 维问题.')

parser.add_argument('--nrefine',
        default=4, type=int,
        help='初始网格加密的次数, 默认初始加密 4 次.')

parser.add_argument('--maxit',
        default=4, type=int,
        help='默认网格加密求解的次数, 默认加密求解 4 次')

args = parser.parse_args()

degree = args.degree
dim = args.dim
nrefine = args.nrefine
maxit = args.maxit

if dim == 2:
    from fealpy.pde.poisson_2d import CosCosData as PDE
elif dim == 3:
    from fealpy.pde.poisson_3d import CosCosCosData as PDE

pde = PDE()
mesh = pde.init_mesh(n=nrefine)

errorType = ['$|| u - u_h||_{\Omega,0}$',
             '$||\\nabla u - \\nabla u_h||_{\Omega, 0}$'
             ]
errorMatrix = np.zeros((2, maxit), dtype=np.float64)
NDof = np.zeros(maxit, dtype=np.int_)

for i in range(maxit):
    print("The {}-th computation:".format(i))

    space = LagrangeFiniteElementSpace(mesh, p=degree)
    NDof[i] = space.number_of_global_dofs()
    bc = DirichletBC(space, pde.dirichlet) 

    uh = space.function() # uh 即是一个有限元函数，也是一个数组
    A = space.stiff_matrix()
    F = space.source_vector(pde.source)
    A, F = bc.apply(A, F, uh)
    uh[:] = spsolve(A, F)

    errorMatrix[0, i] = space.integralalg.error(pde.solution, uh)
    errorMatrix[1, i] = space.integralalg.error(pde.gradient, uh.grad_value)

    if i < maxit-1:
        mesh.uniform_refine()



if dim == 2:
    fig = plt.figure()
    axes = fig.add_subplot(1, 1, 1, projection='3d')
    uh.add_plot(axes, cmap='rainbow')
elif dim == 3:
    print('The 3d function plot is not been implemented!')

showmultirate(plt, 0, NDof, errorMatrix,  errorType, 
        propsize=20)

plt.show()
