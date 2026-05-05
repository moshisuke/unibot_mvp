from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ==================== CONFIGURAÇÃO DE PERSISTÊNCIA ====================
# Usa o diretório de trabalho do app como base
# No Render, se você criar um Disk, o arquivo ficará lá
DATA_DIR = os.environ.get('RENDER_DISK_PATH', '.')
DATA_FILE = os.path.join(DATA_DIR, 'dados.json')

print(f"📁 Arquivo de dados: {DATA_FILE}")

# ==================== FUNÇÕES ====================
def carregar():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "alunos": [],
        "professores": [],
        "disciplinas": [],
        "notificacoes": [],
        "ouvidorias": [],
        "proximo_id": 1
    }

def salvar(dados):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

# ==================== ROTAS ====================
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/aluno.html')
def aluno():
    return send_from_directory('.', 'aluno.html')

@app.route('/professor.html')
def professor():
    return send_from_directory('.', 'professor.html')

@app.route('/secretaria.html')
def secretaria():
    return send_from_directory('.', 'secretaria.html')

# ==================== LOGIN ====================
@app.route('/api/login', methods=['POST'])
def login():
    dados = carregar()
    data = request.json
    email = data.get('email')
    senha = data.get('senha')
    tipo = data.get('tipo')
    
    if tipo == 'aluno':
        for a in dados['alunos']:
            if a['email'] == email and a['senha'] == senha:
                a_copy = {k: v for k, v in a.items() if k != 'senha'}
                return jsonify({'ok': True, 'usuario': a_copy, 'tipo': 'aluno'})
    elif tipo == 'professor':
        for p in dados['professores']:
            if p['email'] == email and p['senha'] == senha:
                p_copy = {k: v for k, v in p.items() if k != 'senha'}
                return jsonify({'ok': True, 'usuario': p_copy, 'tipo': 'professor'})
    elif tipo == 'secretaria':
        if email == 'admin@unibot.com' and senha == 'admin':
            return jsonify({'ok': True, 'usuario': {'nome': 'Secretaria'}, 'tipo': 'secretaria'})
    
    return jsonify({'ok': False}), 401

# ==================== ALUNOS ====================
@app.route('/api/alunos', methods=['GET'])
def get_alunos():
    try:
        dados = carregar()
        alunos = []
        for a in dados['alunos']:
            alunos.append({
                'id': a.get('id'),
                'nome': a.get('nome', ''),
                'email': a.get('email', ''),
                'nota': a.get('nota', 0),
                'frequencia': a.get('frequencia', 0),
                'turma': a.get('turma', '')
            })
        return jsonify(alunos)
    except Exception as e:
        print(f"Erro em /api/alunos: {e}")
        return jsonify([])

@app.route('/api/alunos', methods=['POST'])
def add_aluno():
    dados = carregar()
    data = request.json
    data['id'] = dados['proximo_id']
    data['senha'] = '123'
    data['nota'] = 0
    data['frequencia'] = 0
    dados['alunos'].append(data)
    dados['proximo_id'] += 1
    salvar(dados)
    return jsonify({'ok': True})

@app.route('/api/alunos/<int:id>', methods=['DELETE'])
def delete_aluno(id):
    dados = carregar()
    dados['alunos'] = [a for a in dados['alunos'] if a['id'] != id]
    salvar(dados)
    return jsonify({'ok': True})

# ==================== PROFESSORES ====================
@app.route('/api/professores', methods=['GET'])
def get_professores():
    dados = carregar()
    return jsonify(dados['professores'])

@app.route('/api/professores', methods=['POST'])
def add_professor():
    dados = carregar()
    data = request.json
    data['id'] = dados['proximo_id']
    data['senha'] = '123'
    dados['professores'].append(data)
    dados['proximo_id'] += 1
    salvar(dados)
    return jsonify({'ok': True})

@app.route('/api/professores/<int:id>', methods=['DELETE'])
def delete_professor(id):
    dados = carregar()
    dados['professores'] = [p for p in dados['professores'] if p['id'] != id]
    salvar(dados)
    return jsonify({'ok': True})

# ==================== DISCIPLINAS ====================
@app.route('/api/disciplinas', methods=['GET'])
def get_disciplinas():
    dados = carregar()
    return jsonify(dados['disciplinas'])

@app.route('/api/disciplinas', methods=['POST'])
def add_disciplina():
    dados = carregar()
    data = request.json
    data['id'] = dados['proximo_id']
    dados['disciplinas'].append(data)
    dados['proximo_id'] += 1
    salvar(dados)
    return jsonify({'ok': True})

@app.route('/api/disciplinas/<int:id>', methods=['DELETE'])
def delete_disciplina(id):
    dados = carregar()
    dados['disciplinas'] = [d for d in dados['disciplinas'] if d['id'] != id]
    salvar(dados)
    return jsonify({'ok': True})

# ==================== NOTAS ====================
@app.route('/api/nota', methods=['POST'])
def atualizar_nota():
    dados = carregar()
    data = request.json
    for a in dados['alunos']:
        if a['id'] == data['alunoId']:
            a['nota'] = data['nota']
            salvar(dados)
            return jsonify({'ok': True})
    return jsonify({'ok': False}), 404

@app.route('/api/frequencia', methods=['POST'])
def atualizar_frequencia():
    dados = carregar()
    data = request.json
    for a in dados['alunos']:
        if a['id'] == data['alunoId']:
            a['frequencia'] = data['frequencia']
            salvar(dados)
            return jsonify({'ok': True})
    return jsonify({'ok': False}), 404

# ==================== NOTIFICAÇÕES ====================
@app.route('/api/notificacoes', methods=['GET'])
def get_notificacoes():
    dados = carregar()
    return jsonify(dados['notificacoes'])

@app.route('/api/notificacoes', methods=['POST'])
def add_notificacao():
    dados = carregar()
    data = request.json
    data['id'] = dados['proximo_id']
    data['data'] = datetime.now().strftime('%d/%m/%Y')
    dados['notificacoes'].append(data)
    dados['proximo_id'] += 1
    salvar(dados)
    return jsonify({'ok': True})

@app.route('/api/notificacoes/<int:id>', methods=['DELETE'])
def delete_notificacao(id):
    dados = carregar()
    dados['notificacoes'] = [n for n in dados['notificacoes'] if n['id'] != id]
    salvar(dados)
    return jsonify({'ok': True})

# ==================== OUVIDORIA ====================
@app.route('/api/ouvidorias', methods=['GET'])
def get_ouvidorias():
    dados = carregar()
    return jsonify(dados['ouvidorias'])

@app.route('/api/ouvidorias', methods=['POST'])
def add_ouvidoria():
    dados = carregar()
    data = request.json
    data['id'] = dados['proximo_id']
    data['data'] = datetime.now().strftime('%d/%m/%Y %H:%M')
    data['status'] = 'pendente'
    data['resposta'] = ''
    dados['ouvidorias'].append(data)
    dados['proximo_id'] += 1
    salvar(dados)
    return jsonify({'ok': True})

@app.route('/api/responder', methods=['POST'])
def responder():
    dados = carregar()
    data = request.json
    for o in dados['ouvidorias']:
        if o['id'] == data['id']:
            o['resposta'] = data['resposta']
            o['status'] = 'respondido'
            salvar(dados)
            return jsonify({'ok': True})
    return jsonify({'ok': False}), 404

# ==================== CHATBOT ====================
@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    msg = data.get('mensagem', '').lower()
    
    respostas = {
        'nota': '📊 Suas notas estão no Dashboard.',
        'notas': '📊 Suas notas estão no Dashboard.',
        'frequencia': '📈 Sua frequência está no Dashboard.',
        'horario': '📅 Horário: Segunda a Sexta, 8h às 18h.',
        'bolsa': '💰 Contate a secretaria para informações sobre bolsas.',
        'contato': '📞 Secretaria: (11) 99999-8888',
        'ouvidoria': '💬 Use a aba "Ouvidoria" para enviar mensagens.',
        'professor': '👨‍🏫 Seus professores estão listados no sistema.',
        'biblioteca': '📚 Biblioteca: 8h às 22h.',
        'matricula': '📝 Matrículas em Junho e Dezembro.',
        'secretaria': 'O telefone da secretaria é (11) 99999-8888'
    }
    
    for palavra, resposta in respostas.items():
        if palavra in msg:
            return jsonify({'ok': True, 'resposta': resposta})
    
    return jsonify({'ok': True, 'resposta': '🤔 Não entendi. Pergunte sobre: notas, horários, bolsas, contato ou ouvidoria.'})

# ==================== DADOS INICIAIS ====================
def inicializar():
    # Garantir que o diretório existe (apenas para o caso de ser um caminho customizado)
    data_dir = os.path.dirname(DATA_FILE)
    if data_dir and not os.path.exists(data_dir):
        try:
            os.makedirs(data_dir, exist_ok=True)
        except:
            pass  # Se não conseguir criar, usa o diretório atual
    
    if not os.path.exists(DATA_FILE):
        dados = {
            "alunos": [
                {"id": 1, "nome": "Ana Silva", "email": "ana@unibot.com", "senha": "123", "nota": 8.5, "frequencia": 85, "turma": "ADS-1A"},
                {"id": 2, "nome": "Bruno Mendes", "email": "bruno@unibot.com", "senha": "123", "nota": 6.0, "frequencia": 70, "turma": "ADS-1A"}
            ],
            "professores": [
                {"id": 1, "nome": "Prof. Ricardo", "email": "prof@unibot.com", "senha": "123", "disciplina": "Programação"}
            ],
            "disciplinas": [],
            "notificacoes": [],
            "ouvidorias": [],
            "proximo_id": 3
        }
        salvar(dados)
        print("✅ Banco de dados inicializado!")
    else:
        print(f"📁 Banco de dados já existe: {DATA_FILE}")

if __name__ == '__main__':
    inicializar()
    print("\n" + "="*50)
    print("🚀 UniBot MVP - Rodando")
    print("="*50)
    print("📍 http://localhost:5000")
    print(f"📁 Arquivo de dados: {DATA_FILE}")
    print("\n🔐 LOGIN:")
    print("   Aluno: ana@unibot.com / 123")
    print("   Professor: prof@unibot.com / 123")
    print("   Secretaria: admin@unibot.com / admin")
    print("="*50 + "\n")
    
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
