from Crypto.Signature import pss
from collections import OrderedDict
from flask import Flask, jsonify, request, render_template, Response
from flask_socketio import SocketIO, emit
import json
import os
from funcion_analitico import create_transcript
from crear_llaves import generar_llaves
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA3_256
from block import Block
from blockchain import Blockchain
from sing import sing_function  # Asegúrate de importar sing_function

app = Flask(__name__)
socketio = SocketIO(app)

# Inicializar la blockchain
blockchain = Blockchain()

# Estructura para almacenar las claves de los estudiantes
student_keys = {}

# Estructura para almacenar las claves de la institución
institution_keys = {}

# Estructura para almacenar los analíticos de los estudiantes
student_transcripts = {}

@app.route('/')
def index():
    blockchain.reset_chain()  # Reiniciar la blockchain
    return render_template('index.html')

@app.route('/generate_keys')
def generate_keys():
    private_key, public_key = generar_llaves()
    return jsonify({'private_key': private_key, 'public_key': public_key})

@app.route('/generate_public_key', methods=['POST'])
def generate_public_key():
    data = request.get_json()
    private_key = RSA.import_key(data['private_key'].encode())
    public_key = private_key.publickey().export_key().decode()
    return jsonify({'public_key': public_key})

@app.route('/transcript', methods=['GET'])
def get_transcript():
    student_id = request.args.get('studentId')
    if not student_id:
        return jsonify({'error': 'Student ID is required'}), 400
    if student_id in student_transcripts:
        transcript = student_transcripts[student_id]
        transcript_json = json.dumps(transcript, sort_keys=False)
        return Response(transcript_json, mimetype='application/json')
    else:
        return jsonify({'error': 'Student ID not found'}), 404

@socketio.on('submit_data')
def handle_submit_data(data):
    student_id = data['studentId']
    modification_institute_key = data['modification_institute_key']

    # Almacenar las claves del estudiante
    student_keys[student_id] = {
        'private_key': data['student_private_key'],
        'public_key': data['student_public_key']
    }

    # Almacenar las claves de la institución
    institution_keys['institution'] = {
        'private_key': data['institution_private_key'],
        'public_key': data['institution_public_key']
    }

    transcript = create_transcript(
        data['name'],
        data['dni'],
        data['institution'],
        data['courses'],
        data['issue_date']
    )
    transcript_json = json.dumps(transcript, sort_keys=False)
    hash_object = SHA3_256.new(transcript_json.encode())
    hex_dig = hash_object.hexdigest()

    # Actualizar el analítico del estudiante
    student_transcripts[student_id] = transcript

    ultimo_digito = int(student_id[-1])

    # Verificar y limpiar las claves privadas
    student_private_key_str = data['student_private_key'].strip()
    institution_private_key_str = data['institution_private_key'].strip()

    # Verificar que las claves no estén vacías
    if not student_private_key_str or not institution_private_key_str:
        emit('hash_result', {'hash': None, 'studentId': student_id, 'error': 'Claves privadas vacías'})
        return

    # Convertir las claves privadas a objetos RSA.RsaKey
    try:
        student_private_key = RSA.import_key(student_private_key_str.encode())
        institution_private_key = RSA.import_key(institution_private_key_str.encode())
    except ValueError as e:
        emit('hash_result', {'hash': None, 'studentId': student_id, 'error': str(e)})
        return
    
    if modification_institute_key:
        for block in blockchain.chain:
            student_signature = block.student_signature
            institute_signature = sing_function(student_signature, institution_private_key)
            block.institute_signature = institute_signature
            block.calculate_hash_block()
    else:
        if blockchain.block_by_index(ultimo_digito):
            student_signature = sing_function(hash_object, student_private_key)
            institute_signature = sing_function(student_signature, institution_private_key)
            blockchain.modify_chain(ultimo_digito, hex_dig, student_signature, institute_signature)
        else:
            # Agregar un bloque a la blockchain
            student_signature = sing_function(hash_object, student_private_key)
            institute_signature = sing_function(student_signature, institution_private_key)
            blockchain.add_block(hash_object, student_signature, institute_signature)

    # Almacenar las firmas en el transcript del estudiante
    student_transcripts[student_id]['student_signature'] = student_signature.hex()
    student_transcripts[student_id]['institute_signature'] = institute_signature.hex()

    blockchain.recalculate_chain()


    # Emitir información actualizada del bloque modificado
    for block in blockchain.chain:
        info = block.info()
        emit('hash_result', {
            'hash': info["transcript_hash"],
            'studentId': f'student_{block.index}',
            'block_hash': info['hash'],
            'previous_hash': info['previous_hash'],
            'student_signature': info['student_signature'],
            'institute_signature': info['institute_signature']
        }, broadcast=True)

@socketio.on('verify_signature')
def handle_verify_signature(data):
    student_id = data['studentId']
    signature_type = data['type']
    signature = data['signature']

    if signature_type == 'student':
        public_key_str = student_keys[student_id]['public_key']
        transcript = student_transcripts[student_id].copy()
        transcript.pop('student_signature', None)
        transcript.pop('institute_signature', None)
        transcript_json = json.dumps(transcript, sort_keys=False)
        hash_object = SHA3_256.new(transcript_json.encode())
    else:
        public_key_str = institution_keys['institution']['public_key']
        student_signature = blockchain.block_by_index(int(student_id[-1])).student_signature
        if isinstance(student_signature, bytes):
            student_signature = student_signature.hex()
        hash_object = SHA3_256.new(bytes.fromhex(student_signature))

    public_key = RSA.import_key(public_key_str.encode())

    try:
        pss.new(public_key).verify(hash_object, bytes.fromhex(signature))
        valid = True
    except (ValueError, TypeError):
        valid = False

    emit('verify_signature_result', {
        'studentId': student_id,
        'type': signature_type,
        'valid': valid
    })

@app.route('/blockchain', methods=['GET'])
def get_blockchain():
    chain_data = [block.info() for block in blockchain.chain]

    # Print each block's info in the console
    for block in chain_data:
        print(block)

    # Return JSON without sorting the keys
    return app.response_class(
        response=json.dumps(chain_data, indent=4, sort_keys=False),
        mimetype='application/json'
    )

@app.route('/verify_blockchain', methods=['GET'])
def verify_blockchain():
    is_valid = blockchain.verify_chain()
    return jsonify({'is_valid': is_valid})

@app.route('/student_keys', methods=['GET'])
def get_student_keys():
    return jsonify(student_keys)

@app.route('/institution_keys', methods=['GET'])
def get_institution_keys():
    return jsonify(institution_keys)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)