import numpy as np
import matplotlib.pyplot as plt
import math

# --- Fixed n (you can change this to any value) ---
n = 10

# --- User inputs for lambdas ---
lambda1 = float(input("Enter lambda for first Poisson distribution: "))
lambda2 = float(input("Enter lambda for second Poisson distribution: "))

# --- x values from 0 to n (for plotting) ---
x_plot = np.arange(0, n + 1)

# --- Poisson PMF for plotting ---
pmf1_plot = np.array([(math.exp(-lambda1) * (lambda1 ** k)) / math.factorial(k) for k in x_plot])
pmf2_plot = np.array([(math.exp(-lambda2) * (lambda2 ** k)) / math.factorial(k) for k in x_plot])

# --- Tail probabilities P(X > n) ---
tail1 = 1.0 - np.sum(pmf1_plot)
tail2 = 1.0 - np.sum(pmf2_plot)

# --- Plot ---
plt.plot(x_plot, pmf1_plot, 'o-', label=f'Poisson(λ={lambda1})')
plt.plot(x_plot, pmf2_plot, 's-', label=f'Poisson(λ={lambda2})')

plt.text(0.05, 0.95, f'P(X > {n}) for λ₁ = {tail1:.3g}',
         transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')
plt.text(0.05, 0.90, f'P(X > {n}) for λ₂ = {tail2:.3g}',
         transform=plt.gca().transAxes, fontsize=10, verticalalignment='top')

plt.xlabel('x')
plt.ylabel('P(X=x)')
plt.xticks(x_plot)
plt.legend()
plt.title(f'Poisson Distributions (x = 0 to {n})')
plt.grid(True, linestyle=':', alpha=0.5)
plt.show()

# --- Console output ---
print(f"\nP(X > {n}) for λ={lambda1}: {tail1:.3g}")
print(f"P(X > {n}) for λ={lambda2}: {tail2:.3g}")

# --- Generate the n x n joint PMF matrix (x=0..n-1, y=0..n-1) ---
x_matrix = np.arange(0, n)   # columns (Poisson 1)
y_matrix = np.arange(0, n)   # rows    (Poisson 2)

pmf1_matrix = np.array([(math.exp(-lambda1) * (lambda1 ** k)) / math.factorial(k) for k in x_matrix])
pmf2_matrix = np.array([(math.exp(-lambda2) * (lambda2 ** k)) / math.factorial(k) for k in y_matrix])

# Joint probability: rows = y (Poisson 2), columns = x (Poisson 1)
joint_matrix = np.outer(pmf2_matrix, pmf1_matrix)   # shape (n, n)

# --- Always write the CSV (overwrites if exists, creates if not) ---
filename = "goalsjointpmfmatrix.csv"
np.savetxt(filename, joint_matrix, delimiter=",", fmt="%.10f")
print(f"\nWritten {n}x{n} joint probability matrix to '{filename}' (overwritten if it existed).")