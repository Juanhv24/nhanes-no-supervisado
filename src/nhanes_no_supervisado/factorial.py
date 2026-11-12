"""Funciones de análisis factorial (KMO, Bartlett, ejes principales, varimax, promax,
análisis paralelo y alfa de Cronbach), tomadas del notebook «Más allá de la superficie»
del curso Técnicas de Análisis No Supervisado, Universidad de La Salle (2026)."""

import pandas as pd
import numpy as np
from scipy import stats

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

# ---------- Adecuación ----------
def kmo_from_corr(R):
    """KMO global y MSA por variable a partir de la matriz de correlaciones."""
    R = np.asarray(R, float)
    Rinv = np.linalg.pinv(R)
    d = np.sqrt(np.outer(np.diag(Rinv), np.diag(Rinv)))
    P = -Rinv / d                      # correlaciones parciales (anti-imagen)
    np.fill_diagonal(P, 0)
    R0 = R.copy()
    np.fill_diagonal(R0, 0)
    r2 = (R0 ** 2).sum(axis=0)
    p2 = (P ** 2).sum(axis=0)
    msa = r2 / (r2 + p2)
    kmo = (R0 ** 2).sum() / ((R0 ** 2).sum() + (P ** 2).sum())
    return msa, kmo


def bartlett_from_corr(R, n):
    """Prueba de esfericidad de Bartlett (H0: R = I). Devuelve chi2, gl, p-valor y determinante."""
    p = R.shape[0]
    sign, logdet = np.linalg.slogdet(R)
    chi2 = -(n - 1 - (2 * p + 5) / 6) * logdet
    df = p * (p - 1) / 2
    return chi2, df, stats.chi2.sf(chi2, df), np.exp(logdet)


# ---------- Extracción ----------
def pca_loadings(R, m):
    """Cargas de los m primeros componentes principales y todos los autovalores de R."""
    w, V = np.linalg.eigh(R)
    idx = np.argsort(w)[::-1]
    w, V = w[idx], V[:, idx]
    L = V[:, :m] * np.sqrt(w[:m])
    return L, w


def paf(R, m, max_iter=500, tol=1e-6, cota=None):
    """Ejes principales iterados (comunalidades iniciales = SMC).

    Con cota, las comunalidades se limitan a ese valor en cada iteración para evitar
    casos Heywood (equivale a la opción HEYWOOD de PROC FACTOR en SAS cuando cota = 1).
    """
    R = np.asarray(R, float)
    h2 = 1 - 1 / np.diag(np.linalg.inv(R))
    for it in range(max_iter):
        Rr = R.copy()
        np.fill_diagonal(Rr, h2)
        w, V = np.linalg.eigh(Rr)
        idx = np.argsort(w)[::-1][:m]
        L = V[:, idx] * np.sqrt(np.clip(w[idx], 0, None))
        h2_new = (L ** 2).sum(axis=1)
        if cota is not None:
            h2_new = np.minimum(h2_new, cota)
        if np.max(np.abs(h2_new - h2)) < tol:
            h2 = h2_new
            break
        h2 = h2_new
    return L, h2, it + 1


def align_signs(L):
    """Invierte las columnas cuya suma de cargas es negativa."""
    L = L.copy()
    for j in range(L.shape[1]):
        if L[:, j].sum() < 0:
            L[:, j] *= -1
    return L


# ---------- Rotaciones ----------
def varimax(L, normalize=True, max_iter=500, tol=1e-5):
    """Rotación varimax (ortogonal) con normalización de Kaiser."""
    X = np.array(L, float)
    p, k = X.shape
    if k < 2:
        return X, np.eye(k)
    if normalize:
        sc = np.sqrt((X ** 2).sum(axis=1))
        X = X / sc[:, None]
    T = np.eye(k)
    d = 0
    for _ in range(max_iter):
        d_old = d
        B = X @ T
        G = X.T @ (B ** 3 - B @ np.diag((B ** 2).sum(axis=0)) / p)
        u, s, vh = np.linalg.svd(G)
        T = u @ vh
        d = s.sum()
        if d < d_old * (1 + tol):
            break
    X = X @ T
    if normalize:
        X = X * sc[:, None]
    return X, T


def promax(L, power=4):
    """Promax (Hendrickson-White) con normalización de Kaiser, como en R/psych y factor_analyzer.
    Devuelve la matriz de patrón y la correlación entre factores (Phi)."""
    L = np.array(L, float)
    h = np.sqrt((L ** 2).sum(axis=1, keepdims=True))
    X, _ = varimax(L / h)                       # 1) varimax sobre cargas normalizadas
    Y = X * np.abs(X) ** (power - 1)            # 2) objetivo: potencia de las cargas
    U = np.linalg.solve(X.T @ X, X.T @ Y)       # 3) regresión de X sobre el objetivo
    d = np.diag(np.linalg.inv(U.T @ U))
    U = U @ np.diag(np.sqrt(d))                 # 4) columnas con norma adecuada
    Lp = (X @ U) * h                            # 5) patrón oblicuo (se des-normaliza)
    Uinv = np.linalg.inv(U)
    Phi = Uinv @ Uinv.T                         # correlación entre factores
    return Lp, Phi


def reflect_factors(L, Phi=None):
    """Invierte el signo de factores cuya suma de cargas es negativa (y ajusta Phi)."""
    L = np.array(L, float)
    s = np.where(L.sum(axis=0) < 0, -1.0, 1.0)
    L = L * s
    if Phi is None:
        return L
    return L, Phi * np.outer(s, s)


# ---------- Retención ----------
def parallel_analysis(n, p, n_iter=200, pct=95, seed=1):
    """Percentil de los autovalores de datos aleatorios normales con el mismo n y p (Horn, 1965)."""
    rng = np.random.default_rng(seed)
    eig = np.empty((n_iter, p))
    for i in range(n_iter):
        Z = rng.standard_normal((n, p))
        eig[i] = np.sort(np.linalg.eigvalsh(np.corrcoef(Z, rowvar=False)))[::-1]
    return np.percentile(eig, pct, axis=0)


# ---------- Confiabilidad ----------
def cronbach_alpha(X):
    """Alfa de Cronbach de un conjunto de ítems (columnas de X)."""
    X = pd.DataFrame(X)
    k = X.shape[1]
    return k / (k - 1) * (1 - X.var(ddof=1).sum() / X.sum(axis=1).var(ddof=1))


def alpha_if_dropped(X):
    """Alfa de Cronbach que resulta al retirar cada ítem."""
    X = pd.DataFrame(X)
    return pd.Series({c: cronbach_alpha(X.drop(columns=c)) for c in X.columns})


def item_total_corr(X):
    """Correlación de cada ítem con la suma de los demás (ítem-total corregida)."""
    X = pd.DataFrame(X)
    tot = X.sum(axis=1)
    return pd.Series({c: np.corrcoef(X[c], tot - X[c])[0, 1] for c in X.columns})


def alpha_from_corr(R):
    """Alfa estandarizado a partir de una matriz de correlaciones."""
    R = np.asarray(R, float); k = R.shape[0]
    rbar = (R.sum() - k) / (k * (k - 1))
    return k * rbar / (1 + (k - 1) * rbar)


# ---------- Diagnóstico integrado, ajuste y utilidades ----------
def diagnostico(R, n, nombres=None, verbose=True):
    """Resumen de los supuestos/requisitos del AF a partir de una matriz de correlaciones."""
    R = np.asarray(R, float)
    p = R.shape[0]
    off = R[np.triu_indices(p, 1)]
    msa, kmo = kmo_from_corr(R)
    chi2, gl, pval, det = bartlett_from_corr(R, n)
    out = {
        "n": n, "p": p, "n/p": n / p,
        "% pares |r|>0.30": 100 * np.mean(np.abs(off) > 0.30),
        "max |r|": np.abs(off).max(),
        "determinante": det,
        "KMO global": kmo,
        "MSA mínimo": msa.min(),
        "Bartlett chi2": chi2, "gl": gl, "p-valor": pval,
        "autovalor mínimo de R": np.linalg.eigvalsh(R).min(),
    }
    if verbose:
        print(pd.Series(out).to_string(float_format=lambda v: f"{v:,.4f}"))
        print("\nCalidad del KMO global:", calidad_kmo(kmo))
    msa = pd.Series(msa, index=nombres if nombres is not None else range(p), name="MSA")
    return out, msa


def calidad_kmo(k):
    """Calificación del KMO según los rangos de Kaiser (1974)."""
    if k >= .90: return "excelente"
    if k >= .80: return "muy bueno"
    if k >= .70: return "bueno"
    if k >= .60: return "aceptable"
    if k >= .50: return "malo"
    return "inaceptable"


def comunalidades(L, Phi=None):
    """h2 = diag(L Phi L'). Con factores ortogonales (Phi = I) es la suma de cargas al cuadrado."""
    L = np.asarray(L, float)
    if Phi is None:
        return (L ** 2).sum(axis=1)
    return np.einsum("ij,jk,ik->i", L, Phi, L)


def rmsr(R, L, Phi=None):
    """Raíz del error cuadrático medio de los residuales (fuera de la diagonal)."""
    R = np.asarray(R, float)
    Phi = np.eye(L.shape[1]) if Phi is None else Phi
    E = R - L @ Phi @ L.T
    return np.sqrt(np.mean(E[np.triu_indices(R.shape[0], 1)] ** 2))


def wmean(x, w):
    """Media ponderada de x con pesos w."""
    x = np.asarray(x, float); w = np.asarray(w, float)
    return (x * w).sum() / w.sum()


def congruencia(L1, L2):
    """Coeficiente de congruencia de Tucker entre columnas (factor a factor)."""
    return np.array([abs(L1[:, j] @ L2[:, j]) / np.sqrt((L1[:, j] ** 2).sum() * (L2[:, j] ** 2).sum())
                     for j in range(L1.shape[1])])


# ---------- Gráficos ----------
AZUL, NARANJA, AQUA, GRIS = "#2a78d6", "#eb6834", "#1baf7a", "#8c8b86"
CMAP_DIV = LinearSegmentedColormap.from_list("div", [NARANJA, "#f2f1ee", AZUL])
plt.rcParams.update({"figure.dpi": 110, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.alpha": .25, "axes.titleweight": "bold"})


def guardar_y_mostrar(ruta=None):
    """Guarda la figura actual si se indica una ruta y luego la muestra."""
    if ruta is not None:
        plt.savefig(ruta, dpi=150, bbox_inches="tight")
    plt.show()


def plot_corr(R, title="", annot=False, figsize=(9, 7.5), ruta=None):
    """Mapa de calor de una matriz de correlaciones."""
    plt.figure(figsize=figsize)
    sns.heatmap(R, cmap=CMAP_DIV, vmin=-1, vmax=1, center=0, annot=annot, fmt=".2f",
                annot_kws={"size": 7}, linewidths=.3, linecolor="white", square=True)
    plt.title(title); plt.grid(False); plt.tight_layout()
    guardar_y_mostrar(ruta)


def plot_loadings(L, index, title="", cols=None, figsize=None, ruta=None):
    """Mapa de calor de la matriz de cargas."""
    L = pd.DataFrame(L, index=index, columns=cols or [f"F{j+1}" for j in range(np.shape(L)[1])])
    plt.figure(figsize=figsize or (1.6 + 1.3 * L.shape[1], 0.38 * len(L) + 1.6))
    sns.heatmap(L, cmap=CMAP_DIV, vmin=-1, vmax=1, center=0, annot=True, fmt=".2f",
                linewidths=.4, linecolor="white", cbar_kws={"shrink": .7})
    plt.title(title); plt.grid(False); plt.tight_layout()
    guardar_y_mostrar(ruta)


def plot_scree(eig, pa=None, title="Gráfico de sedimentación", ruta=None):
    """Gráfico de sedimentación con la curva del análisis paralelo y el criterio de Kaiser."""
    k = np.arange(1, len(eig) + 1)
    plt.figure(figsize=(7.5, 4.2))
    plt.plot(k, eig, "o-", color=AZUL, label="Autovalores observados")
    if pa is not None:
        plt.plot(k, pa, "s--", color=NARANJA, label="Análisis paralelo (percentil 95)")
    plt.axhline(1, color=GRIS, lw=1, ls=":", label="Criterio de Kaiser (λ = 1)")
    plt.xlabel("Número de factor"); plt.ylabel("Autovalor"); plt.title(title)
    plt.xticks(k); plt.legend(frameon=False); plt.tight_layout()
    guardar_y_mostrar(ruta)


def tabla_cargas(L, index, umbral=0.40, cols=None):
    """Tabla de cargas con las que superan el umbral resaltadas en negrita."""
    D = pd.DataFrame(L, index=index, columns=cols or [f"F{j+1}" for j in range(np.shape(L)[1])])
    sty = D.style.format("{:.2f}").map(lambda v: "font-weight:bold;background:#dbe8f8" if abs(v) >= umbral else "color:#8c8b86")
    return sty
