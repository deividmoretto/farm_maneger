"""
Módulo para gerenciamento de tokens JWT revogados.
Este módulo mantém um conjunto de tokens JWT que foram revogados (por exemplo, após logout).
Tokens neste conjunto não serão aceitos para autenticação.
"""

# Conjunto para armazenar tokens JWT revogados
BLACKLIST = set()

def add_to_blacklist(jti):
    """
    Adiciona um token JWT à blacklist.
    
    Args:
        jti (str): O identificador único do token JWT.
    """
    BLACKLIST.add(jti)
    
def remove_from_blacklist(jti):
    """
    Remove um token JWT da blacklist.
    
    Args:
        jti (str): O identificador único do token JWT.
    
    Returns:
        bool: True se o token foi removido, False se não estava na blacklist.
    """
    if jti in BLACKLIST:
        BLACKLIST.remove(jti)
        return True
    return False

def is_blacklisted(jti):
    """
    Verifica se um token JWT está na blacklist.
    
    Args:
        jti (str): O identificador único do token JWT.
    
    Returns:
        bool: True se o token está na blacklist, False caso contrário.
    """
    return jti in BLACKLIST