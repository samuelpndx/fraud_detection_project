# Sistema de Detecção de Fraudes com Flask e XGBoost

Um sistema completo e interativo para demonstração de detecção de fraudes em tempo real usando Flask e XGBoost.

## Live Preview

Acesse a demonstração ao vivo do sistema no seguinte link: [Live Preview](http://18.231.76.119/)

## Características

- **Modelo XGBoost**: Utiliza o algoritmo XGBoost para detecção de fraudes
- **Visualizações em tempo real**:
  - Gráfico principal mostrando previsões de probabilidade de fraude
  - Limite configurado para exibir apenas os últimos 50 pontos de dados
  - Gráfico de barras mostrando a distribuição de transações fraudulentas vs. normais
- **Métricas de desempenho**: Visualização em tempo real de métricas importantes:
  - Recall 
  - Precisão
  - F1-score
- **Controles interativos**:
  - Botão para iniciar/pausar a demonstração
  - Botão para reiniciar o sistema
  - Slider para balancear/desbalancear a proporção de fraudes (0-100%)
- **Design responsivo**: Interface adaptável para acesso via computador ou dispositivos móveis

## Processo de Treinamento do Modelo

O treinamento do modelo de detecção de fraudes foi realizado utilizando o algoritmo **XGBoost** e técnicas de balanceamento de dados para lidar com o desbalanceamento entre transações fraudulentas e normais. Abaixo está uma descrição detalhada do processo:

### 1. Pré-processamento dos Dados
- O dataset utilizado foi carregado a partir do arquivo `creditcard.csv`.
- Remoção de duplicatas para garantir a qualidade dos dados.
- Separação das variáveis:
  - `X`: Conjunto de características (features), excluindo as colunas `Time` e `Class`.
  - `y`: Rótulo (`Class`), indicando se a transação é fraudulenta (1) ou normal (0).
- Divisão dos dados em conjuntos de treino e teste utilizando **StratifiedKFold** para manter a proporção de classes:
  - 70% para treino.
  - 30% para teste.
- Normalização da coluna `Amount` utilizando **StandardScaler**.

---

### 2. Técnicas de Balanceamento
Para lidar com o desbalanceamento de classes, foram utilizadas as seguintes técnicas de oversampling:
- **SMOTE (Synthetic Minority Oversampling Technique)**.
- **ADASYN (Adaptive Synthetic Sampling)**.
- **RandomOverSampler (ROS)**.

Uma função foi criada para selecionar dinamicamente a técnica de oversampling com base nos parâmetros fornecidos.

---

### 3. Otimização de Hiperparâmetros
- Utilizou-se a biblioteca **Optuna** para realizar a busca pelos melhores hiperparâmetros do modelo **XGBoost**.
- Os hiperparâmetros otimizados incluem:
  - `n_estimators`: Número de árvores no modelo.
  - `max_depth`: Profundidade máxima das árvores.
  - `learning_rate`: Taxa de aprendizado.
  - `subsample`: Fração de amostras utilizadas para treinar cada árvore.
  - `colsample_bytree`: Fração de características utilizadas para treinar cada árvore.
  - `scale_pos_weight`: Peso atribuído à classe minoritária (fraudes).
- A métrica de avaliação utilizada foi o **F2-Score**, que dá mais peso ao recall.

---

### 4. Treinamento do Modelo
- O modelo foi treinado utilizando um pipeline que combina a técnica de oversampling selecionada e o classificador **XGBoost**.
- O treinamento foi realizado com validação cruzada (5 folds) para garantir a robustez do modelo.

---

### 5. Avaliação do Modelo
Após o treinamento, o modelo foi avaliado no conjunto de teste utilizando as seguintes métricas:
- **Matriz de Confusão**: Para analisar os erros de classificação.
- **Recall**: Proporção de fraudes corretamente identificadas.
- **Precisão**: Proporção de previsões de fraudes que são corretas.
- **F1-Score**: Média harmônica entre recall e precisão.
- **Acurácia**: Proporção total de previsões corretas.

---

### 6. Salvamento do Modelo
O modelo treinado foi salvo no formato JSON no diretório `models/`:
- Caminho: `models/xgboost_ros.json`.

Este modelo é utilizado pela aplicação Flask para realizar previsões em tempo real.

## Requisitos

- Python
- Flask
- XGBoost
- Pandas
- NumPy
- Scikit-learn

## Estrutura do Projeto

```
sistema-deteccao-fraudes/
│
├── app.py              # Aplicação Flask principal
├── requirements.txt    # Dependências do projeto
│
├── model/              # Diretório para armazenar o modelo
│   └── xgboost_ros.json  # Modelo XGBoost salvo em formato JSON
│
├── data/               # Diretório para dados de teste
│   ├── fraud_data.csv  # Dados de transações fraudulentas para demonstração
│   └── legit_data.csv  # Dados de transações normais para demonstração
│
└── templates/          # Templates HTML
    └── index.html      # Interface do usuário
```

## Instalação

1. Clone o repositório ou baixe os arquivos

2. Crie um ambiente virtual (recomendado):
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

1. Execute a aplicação:
```bash
python app.py
```

2. Acesse a interface web pelo navegador:
```
http://localhost:5000
```

3. Utilize os controles na interface para:
   - Iniciar a simulação
   - Pausar quando necessário
   - Reiniciar o sistema
   - Ajustar o balanceamento entre transações fraudulentas e normais

## Dados de Entrada

O sistema espera dois arquivos CSV:
- `fraud_data.csv`: Contém exemplos de transações fraudulentas
- `legit_data.csv`: Contém exemplos de transações normais

## API

O sistema disponibiliza os seguintes endpoints de API:

### 1. `GET /api/init`
- **Descrição**: Inicializa o sistema, carregando o modelo XGBoost e os dados de transações fraudulentas e normais.
- **Resposta**: Retorna um JSON com o status e uma mensagem de sucesso.
- **Exemplo de Resposta**:
  ```json
  {
    "status": "success",
    "message": "Sistema inicializado com sucesso"
  }
  ```

---

### 2. `GET /api/data`
- **Descrição**: Retorna os dados atuais, previsões realizadas, métricas de desempenho e a distribuição de transações fraudulentas e normais.
- **Resposta**: Retorna um JSON com as seguintes informações:
  - `current_data`: Últimos 50 pontos de dados processados.
  - `predictions`: Últimas 50 previsões realizadas.
  - `metrics`: Métricas de desempenho (Recall, Precisão e F1-Score).
  - `distribution`: Contagem de transações fraudulentas e normais.
- **Exemplo de Resposta**:
  ```json
  {
    "current_data": [...],
    "predictions": [...],
    "metrics": {
      "recall": 0.9,
      "precision": 0.85,
      "f1": 0.87
    },
    "distribution": {
      "fraud": 10,
      "non_fraud": 90
    }
  }
  ```

---

### 3. `GET /api/predict?balance=X`
- **Descrição**: Gera uma nova previsão com base no parâmetro de balanceamento de fraudes.
- **Parâmetro de Query**:
  - `balance` (opcional): Percentual de transações fraudulentas a ser considerado (padrão: 10%).
- **Resposta**: Retorna um JSON com os detalhes da previsão, incluindo:
  - `timestamp`: Horário da previsão.
  - `features`: Dados de entrada utilizados na previsão.
  - `prediction`: Resultado da previsão (fraude ou não fraude).
  - `expected`: Valor esperado (real).
- **Exemplo de Resposta**:
  ```json
  {
    "status": "success",
    "data": {
      "timestamp": "12:34:56",
      "features": {...},
      "prediction": 1,
      "expected": 1
    }
  }
  ```

---

### 4. `POST /api/reset`
- **Descrição**: Reinicia o sistema, limpando todos os dados, previsões e métricas.
- **Resposta**: Retorna um JSON com o status e uma mensagem de sucesso.
- **Exemplo de Resposta**:
  ```json
  {
    "status": "success",
    "message": "Sistema reiniciado com sucesso"
  }
  ```