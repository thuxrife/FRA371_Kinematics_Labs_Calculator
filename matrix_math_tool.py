"""
General-Purpose Symbolic & Numerical Matrix / Jacobian Calculator Tool.

Designed for quick symbolic derivation + numerical substitution:
  - Analytic Jacobian: J = df / dq
  - Matrix Inverse via Adjoint / Cofactor Method (with step-by-step C, adj, det, M^-1)
  - Linear System Solver: A x = b (square inverse or Moore-Penrose pseudoinverse)
  - Manipulability & Eigenvalue / Ellipsoid Analysis: A = J J^T
"""

from __future__ import annotations
import numpy as np
import sympy as sp


def eval_matrix(M: sp.Matrix, subs: dict | None = None, deg_vars: set | list | None = None) -> np.ndarray:
    """Substitute numerical values into a SymPy Matrix and return a NumPy float64 array."""
    if subs is None:
        return np.array(M.evalf(), dtype=np.float64)
    clean_subs = {}
    deg_set = set(deg_vars or [])
    for k, v in subs.items():
        clean_subs[k] = np.deg2rad(v) if k in deg_set else v
    return np.array(M.subs(clean_subs).evalf(), dtype=np.float64)


def analytic_jacobian(
    exprs: list[sp.Expr] | sp.Matrix,
    variables: list[sp.Symbol] | sp.Matrix,
    subs: dict | None = None,
    deg_vars: set | list | None = None,
    simplify: bool = True,
    verbose: bool = True,
) -> dict:
    """Compute the symbolic (and optional numerical) Analytic Jacobian J = d(exprs)/d(variables)."""
    f_vec = sp.Matrix(exprs)
    q_vec = sp.Matrix(variables)
    J = f_vec.jacobian(q_vec)
    if simplify:
        J = sp.trigsimp(J)

    result = {"J_sym": J}
    if subs is not None:
        result["J_num"] = eval_matrix(J, subs, deg_vars=deg_vars)

    if verbose:
        print("=== ANALYTIC JACOBIAN J = d(f)/d(q) (Symbolic) ===")
        sp.pprint(J)
        if "J_num" in result:
            print("\n=== ANALYTIC JACOBIAN (Numerical) ===")
            print(np.round(result["J_num"], 4))
    return result


def invert_matrix_adjoint(
    M: sp.Matrix | list,
    subs: dict | None = None,
    deg_vars: set | list | None = None,
    simplify: bool = True,
    verbose: bool = True,
) -> dict:
    """
    Invert any square matrix M symbolically (and optionally numerically) using the
    Adjoint / Cofactor Method: M^-1 = (1 / det(M)) * C^T.
    """
    M = sp.Matrix(M)
    if M.rows != M.cols:
        raise ValueError(f"Matrix must be square for standard inverse, got {M.rows}x{M.cols}. Use solve_linear_system() for pseudoinverse.")

    det_M = sp.trigsimp(M.det()) if simplify else M.det()
    if det_M == 0:
        raise ValueError("Matrix is identically singular (det = 0); inverse does not exist.")

    # Build cofactor matrix C_ij = (-1)^(i+j) * minor(i, j)
    C = M.cofactor_matrix()
    if simplify:
        C = sp.trigsimp(C)
    adj_M = C.T
    M_inv = adj_M / det_M
    if simplify:
        M_inv = sp.trigsimp(M_inv)

    result = {
        "det_sym": det_M,
        "cofactor_sym": C,
        "adj_sym": adj_M,
        "inv_sym": M_inv,
    }

    if subs is not None:
        clean_subs = {k: (np.deg2rad(v) if deg_vars and k in deg_vars else v) for k, v in subs.items()}
        det_num = float(det_M.subs(clean_subs).evalf())
        result["det_num"] = det_num
        if abs(det_num) < 1e-10:
            result["inv_num"] = None
            result["singular"] = True
        else:
            result["inv_num"] = eval_matrix(M_inv, subs, deg_vars=deg_vars)
            result["singular"] = False

    if verbose:
        print("=== 1. DETERMINANT det(M) ===")
        sp.pprint(det_M)
        print("\n=== 2. COFACTOR MATRIX C ===")
        sp.pprint(C)
        print("\n=== 3. ADJUGATE MATRIX adj(M) = C^T ===")
        sp.pprint(adj_M)
        print("\n=== 4. INVERSE MATRIX M^(-1) = adj(M) / det(M) ===")
        sp.pprint(M_inv)
        if subs is not None:
            print(f"\n=== NUMERICAL EVALUATION: det(M) = {result['det_num']:.6g} ===")
            if result.get("singular"):
                print("[WARN] SINGULAR at these numbers (det ~ 0)!")
            else:
                print(np.round(result["inv_num"], 4))
    return result


def solve_linear_system(
    A: sp.Matrix | list,
    b: sp.Matrix | list,
    subs: dict | None = None,
    deg_vars: set | list | None = None,
    simplify: bool = True,
    verbose: bool = True,
) -> dict:
    """
    Solve A * x = b symbolically and/or numerically.
      - Square (m == n): exact inverse x = A^(-1) b
      - Wide (m < n, redundant): right pseudoinverse x = A^T (A A^T)^(-1) b
      - Tall (m > n, overdetermined): left pseudoinverse x = (A^T A)^(-1) A^T b
    """
    A = sp.Matrix(A)
    b = sp.Matrix(b)
    m, n = A.shape

    if m == n:
        method = "Exact Inverse: A^(-1) * b"
        A_pinv = A.inv()
    elif m < n:
        method = "Right Pseudoinverse (Redundant): A^T (A A^T)^(-1) * b"
        A_pinv = A.T * (A * A.T).inv()
    else:
        method = "Left Pseudoinverse (Least-Squares): (A^T A)^(-1) A^T * b"
        A_pinv = (A.T * A).inv() * A.T

    x_sym = A_pinv * b
    if simplify:
        x_sym = sp.trigsimp(x_sym)

    result = {"method": method, "x_sym": x_sym, "A_pinv_sym": sp.trigsimp(A_pinv) if simplify else A_pinv}
    if subs is not None:
        A_num = eval_matrix(A, subs, deg_vars=deg_vars)
        b_num = eval_matrix(b, subs, deg_vars=deg_vars).reshape(-1)
        x_num = np.linalg.pinv(A_num) @ b_num
        result["x_num"] = x_num

    if verbose:
        print(f"=== LINEAR SOLVER ({method}) ===")
        print("Symbolic x:")
        sp.pprint(x_sym)
        if "x_num" in result:
            print("\nNumerical x:")
            print(np.round(result["x_num"], 4))
    return result


def manipulability_and_eigen(
    J: sp.Matrix | list,
    subs: dict | None = None,
    deg_vars: set | list | None = None,
    simplify: bool = True,
    verbose: bool = True,
) -> dict:
    """Compute A = J J^T, det(A), manipulability w = sqrt(det(A)), and numerical eigenvalues/semi-axes."""
    J = sp.Matrix(J)
    A = J * J.T
    if simplify:
        A = sp.trigsimp(A)
    det_A = sp.trigsimp(A.det()) if simplify else A.det()
    w_sym = sp.sqrt(det_A)

    result = {"A_sym": A, "det_A_sym": det_A, "w_sym": w_sym}
    if subs is not None:
        A_num = eval_matrix(A, subs, deg_vars=deg_vars)
        eigvals, eigvecs = np.linalg.eigh(A_num)
        eigvals = np.maximum(eigvals, 0.0)
        semi_axes = np.sqrt(eigvals)
        w_num = float(np.sqrt(max(np.linalg.det(A_num), 0.0)))
        result.update({
            "A_num": A_num,
            "eigenvalues": eigvals,
            "eigenvectors": eigvecs,
            "semi_axes": semi_axes,
            "w_num": w_num,
        })

    if verbose:
        print("=== A = J * J^T (Symbolic) ===")
        sp.pprint(A)
        print("\n=== det(A) & Manipulability w = sqrt(det(A)) ===")
        print("det(A) =", det_A)
        print("w      =", w_sym)
        if subs is not None:
            print(f"\n=== NUMERICAL: w = {result['w_num']:.4f} ===")
            print("Eigenvalues (lambda):", np.round(result["eigenvalues"], 4))
            print("Semi-axes   (sigma) :", np.round(result["semi_axes"], 4))
    return result
