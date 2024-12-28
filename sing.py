import os
from Crypto.Signature import pss
from Crypto.Hash import SHA3_256
from Crypto.PublicKey import RSA
import json

def sing_function(document, private_key):
    if isinstance(document, bytes):  # Si ya es bytes, no codificar
        hash_object = SHA3_256.new(document)
    elif isinstance(document, str):
        try:
            # Intentar convertir la cadena a bytes desde hexadecimal
            hash_object = SHA3_256.new(bytes.fromhex(document))
        except ValueError:
            # Si falla, tratar la cadena como texto y convertir a bytes
            hash_object = SHA3_256.new(document.encode())
    elif isinstance(document, dict):
        # Convertir el diccionario a una cadena JSON y luego a bytes
        document_json = json.dumps(document)
        hash_object = SHA3_256.new(document_json.encode())
    elif isinstance(document, SHA3_256.SHA3_256_Hash):
        # Si ya es un objeto de hash, usarlo directamente
        hash_object = document
    else:
        raise TypeError("El documento debe ser una cadena, bytes, diccionario o objeto de hash")
    
    signature = pss.new(private_key).sign(hash_object)
    return signature