import base64
import os

def get_query(tablename, fields):
    query = f"CREATE TABLE IF NOT EXISTS {tablename.upper()} ("
    for name, datatype in fields.items():
        query += f"{name} {datatype}, "
    return query.rstrip(", ") + ")"


def get_unique_id(length=8):
    """Generates random secure unique ID that is urlsafe ( i.e can be on url )"""
    return base64.urlsafe_b64encode(os.urandom(length)).decode().strip('=')
