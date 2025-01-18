import time
import os
from sing import sing_function
from Crypto.Hash import SHA3_256
from Crypto.Signature import pss


class Block:
    def __init__(self, index, previous_hash, transcript_hash, student_signature, institute_signature):
        self.index = index
        self.previous_hash = previous_hash
        self.transcript_hash = transcript_hash
        self.student_signature = student_signature
        self.institute_signature =  institute_signature
        self.hash = None
        self.calculate_hash_block()

    def get_index(self):
        return self.index
    
    def calculate_hash_block(self):
        block_string = f"{self.index}{self.previous_hash}{self.transcript_hash}{self.student_signature}{self.institute_signature}"
        self.hash = SHA3_256.new(block_string.encode()).hexdigest()
        return self.hash

    def recalculate_block(self, student_private_key, institute_private_key):
        self.student_signature = sing_function(self.transcript_hash, student_private_key)
        self.institute_signature = sing_function(self.student_signature, institute_private_key)
        self.calculate_hash_block()


    def info(self):
        return {
            "index": self.index,
            "previous_hash": self.previous_hash,
            "transcript_hash": self.transcript_hash.hexdigest() if hasattr(self.transcript_hash, "hexdigest") else self.transcript_hash,
            "student_signature": self.student_signature.hex() if hasattr(self.student_signature, "hex") else self.student_signature,
            "institute_signature": self.institute_signature.hex() if hasattr(self.institute_signature, "hex") else self.institute_signature,
            "hash": self.hash.hexdigest() if hasattr(self.hash, "hexdigest") else self.hash
        }
    def verify_sing_student(self, public_key):
        return self.verify_signature(self.transcript_hash, self.student_signature, public_key)
    
    def verify_sing_institution(self, public_key):
        return self.verify_signature(self.student_signature, self.institute_signature, public_key)


        

    # Verificar la firma de la universidad sobre la firma del alumno
    def verify_signature(self, document, signature, public_key):

        def ensure_bytes(data):
            """Asegurarse de que los datos sean de tipo bytes."""
            if isinstance(data, str):
                return data.encode()  # Si es una cadena, convertir a bytes
            elif isinstance(data, bytes):
                return data  # Si ya es bytes, devolverlo tal cual
            elif isinstance(data, SHA3_256.SHA3_256_Hash):
                return data.digest()  # Extraer los bytes del hash
            else:
                raise TypeError(f"Tipo de datos inesperado: {type(data)}")

        document_bytes = ensure_bytes(document)
        
        # Crear el hash del documento (analítico)
        document_hash = SHA3_256.new(document_bytes)

        # Verificar la firma de la universidad utilizando la clave pública de la universidad
        verifier = pss.new(public_key)
        try:
            verifier.verify(document_hash, signature)
            return True
        except (ValueError, TypeError):
            return False

    def __str__(self):
        return f"Block {self.index} [Hash: {self.hash.hexdigest()}]"
