def get_default_database(namespace: str, base_name: str):
    """
    Return default database which is cnpg postgres
    
    :param namespace: Description
    :type namespace: str
    :param base_name: Description
    :type base_name: str
    """
    database = {
        "apiVersion": "postgresql.cnpg.io/v1",
        "kind": "Cluster",
        "metadata": {
            "name": f"{base_name}-db",
            "namespace": namespace,
        },
    }
    return database
