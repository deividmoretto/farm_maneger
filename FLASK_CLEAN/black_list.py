# Lista global que armazena itens que foram bloqueados
blacklisted_items = []

def add_to_blacklist(item):
    """
    Adiciona um item à lista de bloqueio se ele ainda não estiver presente na lista.

    Args:
        item: O item a ser adicionado à lista de bloqueio. Pode ser de qualquer tipo que suporte comparação, como uma string ou um número.

    Returns:
        None
    """
    # Verifica se o item não está na lista de bloqueio
    if item not in blacklisted_items:
        # Se não estiver, adiciona o item à lista
        blacklisted_items.append(item)

def is_blacklisted(item):
    """
    Verifica se um item está presente na lista de bloqueio.

    Args:
        item: O item a ser verificado. Pode ser de qualquer tipo que suporte comparação, como uma string ou um número.

    Returns:
        bool: Retorna True se o item estiver na lista de bloqueio, False caso contrário.
    """
    # Verifica se o item está na lista de bloqueio e retorna o resultado
    return item in blacklisted_items
