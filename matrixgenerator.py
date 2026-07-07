import numpy as np
import matplotlib.pyplot as plt
import math
import os
import sys
from matplotlib.colors import LogNorm, LinearSegmentedColormap

DEBUG = True

def compute_pmfs_and_joint(lambda1, lambda2, n):
    x_plot = np.arange(0, n)
    pmf1_plot = np.array([(math.exp(-lambda1) * (lambda1 ** k)) / math.factorial(k) for k in x_plot])
    pmf2_plot = np.array([(math.exp(-lambda2) * (lambda2 ** k)) / math.factorial(k) for k in x_plot])
    joint_matrix = np.outer(pmf2_plot, pmf1_plot)
    return x_plot, pmf1_plot, pmf2_plot, joint_matrix

def save_joint_matrix(joint_matrix, folder, filename):
    os.makedirs(folder, exist_ok=True)
    full_path = os.path.join(folder, filename)
    np.savetxt(full_path, joint_matrix, delimiter=",", fmt="%.10f")
        

def info_plots(x_plot, pmf1_plot, pmf2_plot, lambda1, lambda2, n, matrix):
    if DEBUG:
        plt.plot(x_plot, pmf1_plot, 'o-', label=f'Poisson 1 (λ={lambda1})', markersize=5)
        plt.plot(x_plot, pmf2_plot, 'o-', label=f'Poisson 2 (λ={lambda2})', markersize=5)
        plt.xlabel('x')
        plt.ylabel('P(X=x)')
        plt.xticks(x_plot)
        plt.legend()
        plt.title(f'Poisson Distributions (from 0 to {n})')
        plt.grid(True, linestyle=':', alpha=0.5)
        plt.show()
        
        n = matrix.shape[0]
        fig, ax = plt.subplots(figsize=(8, 6))
        # Custom colormap: deep blue → deep purple → bright red
        colors = ['#00008B', '#4B0082', '#FF0000']   # deep blue, deep purple, bright red
        cmap = LinearSegmentedColormap.from_list('blue_purple_red', colors, N=256)
        vmin = matrix[matrix > 0].min() if np.any(matrix > 0) else 1e-12
        # --- Origin at top left: origin='upper' ---
        im = ax.imshow(matrix, cmap=cmap, origin='upper', aspect='auto',
                       norm=LogNorm(vmin=vmin, vmax=matrix.max()))
        ax.set_xticks(np.arange(n))
        ax.set_yticks(np.arange(n))
        ax.set_xticklabels(np.arange(n))
        ax.set_yticklabels(np.arange(n))
        ax.set_xlabel('x (Poisson 1)')
        ax.set_ylabel('y (Poisson 2)')
        plt.colorbar(im, ax=ax, label='Probability (log)')
        # Annotate each cell with probability (3sf) – text always white
        for i in range(n):
            for j in range(n):
                val = matrix[i, j]
                ax.text(j, i, f'{val:.3g}', ha='center', va='center', color='white', fontsize=8)
        ax.set_title('Joint PMF Matrix')
        plt.tight_layout()
        plt.show()
        

n = 10

lambda1 = float(input("Enter lambda for first Poisson distribution: "))
lambda2 = float(input("Enter lambda for second Poisson distribution: "))

x_plot, pmf1_plot, pmf2_plot, joint_matrix = compute_pmfs_and_joint(lambda1, lambda2, n)

info_plots(x_plot, pmf1_plot, pmf2_plot, lambda1, lambda2, n, joint_matrix)

folder = "outputs"
filename = "jointpmfmatrix.csv"
save_joint_matrix(joint_matrix, folder, filename)