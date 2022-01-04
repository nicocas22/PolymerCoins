# -*- coding: utf-8 -*-
"""
Created on Sun Jan  2 16:27:17 2022

@author: Nicog
"""

# Modulo Crear una CriptoMoneda

# iNSTALAR FLASK PARA CREAR CADENA DE BLOQUES
# PARA INSTALAR FLASK
# Flas==0.12.2: pip install Flask==0.12.2
# Cleinte HTTTP POSTMAN
# request== 2.18.4: pip install requests==2.18.4

# Importar las librerias
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Parte 1 - Crear La Cadena de bloques


class blockChain:
    # contructor de una clase, Self referencia el objeto creado
    def __init__(self):
        self.chain = []  # Crear variables para cadena un arreglo
        self.transactions = []
        self.createBlock(proof=1, previousHash='0')  # LLamar una funcion
        self.nodes = set() #Creamos un conjunto Vacio para los nodos ya que no tienen necesidad de ir en sucesion 
        
    def createBlock(self, proof, previousHash):
        # Crear un dicionario con las claves para el bloque
        block = {'index': len(self.chain)+1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previousHash': previousHash,
                 'transactions': self.transactions
                 }
        #vaciar Transaccion
        self.transactions = []
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

    def addTransaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                  'receiver': receiver,
                                  'amount' : amount
                                  })
        previousBlock = self.getPreviousBlock()
        return previousBlock['index'] + 1
    
    #   Dar de alta Nodos y decentralizar
    def addNode(self, address):
        parsedUrl = urlparse(address)
        self.nodes.add(parsedUrl.netloc)
    # Implementar concenso entre nodos
    #Remplazar cadena 
    def replaceChain(self):
        network = self.nodes
        longestChain = None
        max_length = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/getChain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.isChainValid(chain):
                    max_length = length
                    longestChain = chain
        if longestChain:
            self.chain = longestChain
            return True
        return False
                         
    ###########################################################################
    ###########################################################################
    
                
                
# Parte 2 - Minado de un bloque de la Cadena

# Crear Aplicacion Web
app = Flask(__name__)
# Por si falla  app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False si se optiene un error 500
#Direccion del nodo (Crear la direccion del nodo en el puerto 5000)
node_address = str(uuid4()).replace('-', '')

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
        blockchain.addTransaction(sender = node_address, receiver = "Mat DLC", amount= 1.5)
        block = blockchain.createBlock(proof, previousHash)
        response = {'message': "Felicidades por tu nuevo bloque minado",
                    'index': block['index'],
                    'timestamp': block['timestamp'],
                    'proof': block['proof'],
                    'previousHash': block['previousHash'],
                    'transactions': block['transactions']}
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
#Comprobar si la cadena es valida o no
@app.route('/isValid', methods=['GET'])
def validateChain():
    try:
        isValid = blockchain.isChainValid(blockchain.chain)
        if isValid:
            response = {'message': 'Muy bien, la blockChain es válida.'}
        else:
            response = {
                'message': 'Ups problema, la cadena de bloques es invalida'}
        return jsonify(response), 200
    except Exception:
        return jsonify(Exception), 404 
    
#Anadir las transaccioens y los nodos
@app.route('/addTransaction', methods=['POST'])    
def addTransaction():
    try: 
        body = request.get_json()
        transactionKeys = ['sender', 'receiver', 'amount']
        if not all(key in json for key in transactionKeys):
            return 'Faltan algunos elementros para la transaccion', 400
        index = blockchain.addTransaction(body['sender'], body['receiver'], body['amount'])
        response = {'message': f'La Transaccion sera anadida al bloque {index}'}
        return jsonify(response), 201
    except Exception:
        return jsonify(Exception), 404 
#Parte 3 - Descentralizar la cadena de bloques

#conectar nuevos nodos
@app.route('/conectNode', methods=['POST'])  
def conectNode():
    try:
        body = request.get_json()
        nodes = body.get('nodes')
        if nodes is None:
            return jsonify({'message': 'No hay nodos para aniadir'}), 400
        for node in nodes:
            blockchain.addNode(node)
        response = {'message': 'Todo a salido bien', 'nodos': list(blockchain.nodes)}    
        return jsonify(response), 201
    except Exception:
        return jsonify(Exception), 404 

#Reemplazar la cadena por la mas larga (Si fuese necesario)
@app.route('/replaceChain', methods=['GET'])
def replaceChain():
    isValidReplaceChain = blockchain.replaceChain()
    if isValidReplaceChain:
        response = {'Message': 'Nodos con diferentes Cadenas, pero tranquilo fueron remplazadas por las correctas',
                    'NewChain': blockchain.chain}
    else: 
        response = {'Message': 'Todo Correcto. La cadena en todos los nodos ya es la mas larga',
                    'CadenaActual': blockchain.chain}
    return jsonify(response), 200
#Ejecucion de la App
app.run(host = '0.0.0.0', port= 5002)




