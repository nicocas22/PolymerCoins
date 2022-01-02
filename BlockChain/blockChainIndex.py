# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 16:27:17 2022

@author: Nicog
"""

# Modulo uno como crear una cadena de bloques

# iNSTALAR FLASK PARA CREAR CADENA DE BLOQUES
# PARA INSTALAR FLASK
# Flas==0.12.2: pip install Flask==0.12.2
# Cleinte HTTTP POSTMAN


# Importar las librerias
import datetime
import hashlib
import json
from flask import Flask, jsonify

# Parte 1 - Crear La Cadena de bloques


class blockChain:
    # contructor de una clase, Self referencia el objeto creado
    def __init__(self):
        self.chain = []  # Crear variables para cadena un arreglo
        self.createBlock(proof=1, previousHash='0')  # LLamar una funcion

    def createBlock(self, proof, previousHash):
        # Crear un dicionario con las claves para el bloque
        block = {'index': len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previousHash': previousHash}
        # anaede al arreglo el bloque creado, es como realizar un .push() en Ts
        self.chain.append(block)
        return block
    # llamado al bloque previo en la cadena

    def getPreviousBlock(self):
        # Buscamos en la cadena el ultimo bloque agregado llamando a la cadena en su posicion -1
        return self.chain[-1]

    def proofOfWork(self, previousProof):
        newProof = 1
        checkProof = False
        while checkProof is False:  # Hasta que checkproof sea verdadera tienen que seguir biscando el un proof que le sirva BAJO CIERTA CONDICIONES
            hashOperation = hashlib.sha256(
                str(newProof**2 - previousProof**2).encode()).hexdigest()
            if hashOperation[:4] == '0000':
                checkProof = True
            else:
                newProof += 1
        return newProof

    # (OBTENER EL HASH DE UN BLOQUE)
    def hash(self, block):
        encodeBlock = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encodeBlock).hexdigest()

    # Comprobar la cadena de bloques (Importante)
    def isChainValid(self, chain):
        previousBlock = chain[0]
        blockIndex = 1
        while blockIndex < len(chain):
            block = chain[blockIndex]
            if block['previousHash'] != self.hash(previousBlock):
                return False
            previousProof = previousBlock['proof']
            proof = block['proof']
            hashOperation = hashlib.sha256(
                str(proof**2 - previousProof**2).encode()).hexdigest()
            if hashOperation[:4] != '0000':
                return False
            previousBlock = block
            blockIndex += 1
        return True


# Parte 2 - Minado de un bloque de la Cadena

# Crear Aplicacion Web
app = Flask(__name__)
# Por si falla  app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False si se optiene un error 500

# Crear una BLOCKCHAIN
blockchain = blockChain()

# Minar un nuevo Bloque

@app.route('/mine_block', methods=['GET'])
def mineBlock():
    try:
        previousBlock = blockchain.getPreviousBlock()
        previousProof = previousBlock['proof']
        proof = blockchain.proofOfWork(previousProof)
        previousHash = blockchain.hash(previousBlock)
        block = blockchain.createBlock(proof, previousHash)
        response = {'message': "Felicidades por tu nuevo bloque minado",
                    'index': block['index'],
                    'timestamp': block['timestamp'],
                    'proof': block['proof'],
                    'previousHash': block['previousHash']}
        return jsonify(response), 200
    except Exception:
        return jsonify(Exception), 404

#Obtener la cadena de bloqus al completo
@app.route('/getChain', methods=['GET'])
def getChain():
    try:
        response = {'chain': blockchain.chain,
                    'length' : len(blockchain.chain)}
        return jsonify(response), 200
    except Exception:
        return jsonify(Exception), 404 

#Ejecucion de la App
app.run(host = '0.0.0.0', port= 5000)




