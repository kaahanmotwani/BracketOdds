#!/usr/bin/env python
from lib.bracket import Bracket, BracketType
from lib.bracket.sample import F4_A, E_8
from database import getBracket
from flask import Flask, request
import toml
import compare

app = Flask(__name__)
application = app

@app.route('/', methods=['GET'])
def generateJSON():  
    uid = None
    bt = None
    sfn = None
    bracket = None
    if 'id' in request.args:
        # Retrieves a bracket with a given id from the database
        uid = request.args['id']
    else:
        # Generates a new bracket with the given type and simulator
        # Setting the men's bracket as the default since most users choose this.
        bt = BracketType.MEN
        if 'type' in request.args:
            try:
                bt = BracketType(request.args['type'])
            except:
                return 'Invalid type parameter', 422     
        if 'sfn' in request.args:
            if request.args['sfn'] == 'f4a':
                sfn = F4_A()
            elif request.args['sfn'] == 'e8':
                sfn = E_8()
        # Don't allow women + sampling function
        if bt == BracketType.WOMEN and sfn is not None:
            return 'Invalid type parameter.', 422
    try:
        bracket = getBracket(uid=uid, bracket_type=bt, sampling_fn=sfn)
    except Exception as e:
        return str(e), 500

    if not bracket:
        return f'Bracket {uid} not found', 400
    return bracket, 200

@app.route('/calculateScore', methods=["GET"])
def calculateScore():
    bracket_type, bitstring = None, None
    if 'id' in request.args:
        try:
            bracket = getBracket(uid=request.args['id'])
            if not bracket:
                uid = request.args['id']
                return f'Bracket {uid} not found', 400
            bitstring, bracket_type = bracket['bitstring'], BracketType(bracket['type'])
        except Exception as e:
            return str(e), 500
    else:
        return "Missing id parameter.", 422
    comparison = compare.compareBrackets(bitstring, bracket_type)
    return {
        'score': comparison[0],
        'gamesCorrectByRound': comparison[1]
    }, 200

if __name__ == '__main__':
    app.run()
