def calcular_nc(v2: float, v1: float, ctc: float, prnt: float) -> float:
    """Calcula a necessidade de calagem (NC) em t/ha.

    Args:
      v2: Saturação por bases desejada (%).
      v1: Saturação por bases atual (%).
      ctc: Capacidade de Troca Catiônica (CTC) do solo (cmolc/dm³).
      prnt: Poder Relativo de Neutralização Total do calcário (%).

    Returns:
      A necessidade de calagem (NC) em t/ha.
    """
    f = 100 / prnt
    nc = (v2 - v1) * ctc * f / 100
    return nc

# Dados do exemplo
v2 = 70.0
v1 = 42.3
ctc = 5.2
prnt = 80.0

# Calculando a necessidade de calagem
nc = calcular_nc(v2, v1, ctc, prnt)

# Imprimindo o resultado
print(f"A necessidade de calagem é: {nc:.2f} t/ha")