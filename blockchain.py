import time
import os
from Crypto.Signature import pss
from Crypto.Hash import SHA3_256
from Crypto.PublicKey import RSA
from block import Block

class Blockchain:
    def __init__(self):
        self.chain = []  # Comienza la cadena vacía

    def add_block(self, transcript_hash, student_signature, institute_signature):
        if not self.chain:  # Crear bloque génesis
            empty_hash = SHA3_256.new(b"").hexdigest()
            new_block = Block(1, empty_hash, transcript_hash, student_signature, institute_signature)
        else:
            previous_block = self.chain[-1]
            new_block = Block(len(self.chain) + 1, previous_block.hash, transcript_hash, student_signature, institute_signature)
        
        self.chain.append(new_block)

    def verify_chain(self):
        # Iterar sobre la cadena desde el segundo bloque
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # Verificar que el hash previo coincide con el hash del bloque anterior
            if current_block.previous_hash != previous_block.hash:
                print(f"Error en bloque {current_block.index}: Hash previo no coincide.")
                return False

            # Recalcular el hash actual y verificar que coincida
            recalculated_hash = current_block.calculate_hash_block()
            if current_block.hash != recalculated_hash:
                print(f"Error en bloque {current_block.index}: El hash del bloque no coincide con su contenido.")
                return False

        print("La blockchain es válida.")
        return True

    def block_by_index(self, number):
        for i_block in self.chain:
            if int(i_block.get_index()) == int(number):
                return i_block
        return False

    def modify_chain(self, index, transcript_hash, student_signature, institute_signature):
        var_block = self.block_by_index(index)
        if not var_block:
            return False
        var_block.transcript_hash = transcript_hash
        var_block.calculate_hash_block()
        var_block.student_signature = student_signature
        var_block.institute_signature = institute_signature

    def recalculate_chain(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            current_block.previous_hash = previous_block.hash
            current_block.calculate_hash_block()

    def reset_chain(self):
        self.chain = []  # Reiniciar la cadena
    