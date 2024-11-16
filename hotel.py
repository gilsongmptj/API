from flask import Flask, request, jsonify
import pandas as pd 
from werkzeug.utils import secure_filename
import os


app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'no file part'}), 400
    
    f = request.files['file']
        
    if f.filename == '':
        return jsonify({'error': 'not select file'}), 400 
    
    if f.filename.endswith(".csv"):
        f.save(secure_filename(f.filename))
        df = pd.read_csv(f.filename)
        jsonfilename = f.filename.replace(".csv",".json")
        df.to_json(jsonfilename, orient= 'records')
        return jsonify(df.head().to_dict(orient= 'records')), 202
    
    else:
        return jsonify({'error':'file is not csv'}), 400
    #enviar a requisição mas retorna erro 500
   
if __name__ == '__main__':
    app.run(debug=True)