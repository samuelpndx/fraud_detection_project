# app.py
from flask import Flask, render_template, jsonify, request
import xgboost as xgb
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime
import random
from sklearn.metrics import recall_score, precision_score, f1_score

app = Flask(__name__)

# Variáveis globais para armazenar dados e modelo
model = None
positive_data = None
negative_data = None
current_data = []
predictions = []
fraud_count = 0
non_fraud_count = 0
metrics = {
    'recall': 0,
    'precision': 0,
    'f1': 0,
}

# Carregar o modelo e os dados
def load_model_and_data():
    global model, positive_data, negative_data
    
    # Carregar o modelo XGBoost
    model = xgb.Booster()
    model.load_model('models/xgboost_ros.json')
    
    # Carregar dados de teste
    try:
        positive_data = pd.read_csv('data/fraud_data.csv')
        negative_data = pd.read_csv('data/legit_data.csv')
        print(f"Dados carregados com sucesso. Positivos: {len(positive_data)}, Negativos: {len(negative_data)}")
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota para inicializar o sistema
@app.route('/api/init', methods=['GET'])
def initialize():
    load_model_and_data()
    return jsonify({'status': 'success', 'message': 'Sistema inicializado com sucesso'})

# Rota para obter dados atuais
@app.route('/api/data', methods=['GET'])
def get_data():
    global current_data, predictions, metrics, fraud_count, non_fraud_count
    return jsonify({
        'current_data': current_data[-50:],  # Limitar para os últimos 50 pontos
        'predictions': predictions[-50:],    # Limitar para os últimos 50 pontos
        'metrics': metrics,
        'distribution': {
            'fraud': fraud_count,
            'non_fraud': non_fraud_count
        }
    })

# Rota para gerar nova previsão
@app.route('/api/predict', methods=['GET'])
def make_prediction():
    global current_data, predictions, metrics, fraud_count, non_fraud_count
    
    # Obter o parâmetro de balanceamento (0-100%)
    balance = int(request.args.get('balance', 10))  # Default: 10% de fraudes
    
    # Selecionar um exemplo com base no balanceamento
    if random.random() * 100 < balance:
        # Selecionar um dado positivo (fraude)
        sample = positive_data.sample(1)
        expected = 1
    else:
        # Selecionar um dado negativo (não fraude)
        sample = negative_data.sample(1)
        expected = 0
    
    # Preparar dados para previsão
    features = sample.drop('is_fraud', axis=1)
    dmatrix = xgb.DMatrix(features)
    
    # Fazer previsão
    prediction = int(model.predict(dmatrix)[0] > 0.5)
    
    # Atualizar contadores
    if expected == 1:
        fraud_count += 1
    else:
        non_fraud_count += 1
    
    # Preparar dados para enviar ao frontend
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    new_data = {
        'timestamp': timestamp,
        'features': features.iloc[0].to_dict(),
        'prediction': prediction,
        'expected': expected
    }
    
    current_data.append(new_data)
    predictions.append({
        'timestamp': timestamp,
        'prediction': prediction,
        'expected': expected
    })
    
    # Calcular métricas se tivermos dados suficientes
    if len(predictions) >= 10:
        y_true = [p['expected'] for p in predictions[-100:]]
        y_pred = [p['prediction'] for p in predictions[-100:]]
        
        metrics['recall'] = round(recall_score(y_true, y_pred, zero_division=0), 3)
        metrics['precision'] = round(precision_score(y_true, y_pred, zero_division=0), 3)
        metrics['f1'] = round(f1_score(y_true, y_pred, zero_division=0), 3)
    
    return jsonify({'status': 'success', 'data': new_data})

# Rota para reiniciar o sistema
@app.route('/api/reset', methods=['POST'])
def reset_system():
    global current_data, predictions, metrics, fraud_count, non_fraud_count
    current_data = []
    predictions = []
    fraud_count = 0
    non_fraud_count = 0
    metrics = {
        'recall': 0,
        'precision': 0,
        'f1': 0,
    }
    return jsonify({'status': 'success', 'message': 'Sistema reiniciado com sucesso'})

if __name__ == '__main__':
    # Criar diretórios necessários
    os.makedirs('model', exist_ok=True)
    os.makedirs('data', exist_ok=True)
    
    # Verificar se o modelo existe, caso contrário criar um modelo simples
    if not os.path.exists('model/fraud_detection_model.json'):
        print("Modelo não encontrado. Criando modelo simplificado para demonstração...")
        # Criar um modelo XGBoost simples para demonstração
        dtrain = xgb.DMatrix(np.random.rand(1000, 5), label=np.random.randint(0, 2, 1000))
        params = {
            'max_depth': 3,
            'eta': 0.3,
            'objective': 'binary:logistic',
            'eval_metric': 'auc'
        }
        temp_model = xgb.train(params, dtrain, num_boost_round=10)
        temp_model.save_model('model/fraud_detection_model.json')
    
    # Inicializar o modelo e os dados
    load_model_and_data()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
