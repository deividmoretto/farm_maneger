import numpy as np

def calcular_nc_np(v2: np.ndarray, v1: np.ndarray, ctc: np.ndarray, prnt: np.ndarray) -> np.ndarray:
    """Calcula a necessidade de calagem (NC) em t/ha usando NumPy.

    Args:
      v2: Saturação por bases desejada (%), array do NumPy.
      v1: Saturação por bases atual (%), array do NumPy.
      ctc: Capacidade de Troca Catiônica (CTC) do solo (cmolc/dm³), array do NumPy.
      prnt: Poder Relativo de Neutralização Total do calcário (%), array do NumPy.

    Returns:
      Um array com a necessidade de calagem (NC) em t/ha.
    """
    f = 100 / prnt
    nc = (v2 - v1) * ctc * f / 100
    return nc

# Dados do exemplo como arrays NumPy
v2 = np.array([70.0])  # Saturação desejada (%)
v1 = np.array([42.3])  # Saturação atual (%)
ctc = np.array([5.2])  # CTC do solo (cmolc/dm³)
prnt = np.array([80.0])  # PRNT do calcário (%)

# Calculando a necessidade de calagem
nc = calcular_nc_np(v2, v1, ctc, prnt)

# Imprimindo o resultado
print(f"A necessidade de calagem é: {nc[0]:.2f} t/ha")