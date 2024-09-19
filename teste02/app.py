from flask import Flask, redirect, render_template, url_for, request, flash
import sqlite3
from models import User
from werkzeug.security import check_password_hash, generate_password_hash

# 1 - Adicionar o LoginManager
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
login_manager = LoginManager()

app = Flask(__name__)

# 2 - Configurar app para trabalhar junto com flask-login
login_manager.init_app(app)

# 3 - ncessário adicionar uma chave secreta para aplicaçãos
app.config['SECRET_KEY'] = 'ULTRAMEGADIFICIL'

database = 'database.db'

def obter_conexao():
    conn = sqlite3.connect(database)
    conn.row_factory = sqlite3.Row
    return conn

# 4-  Função utilizada para carregar o usuário da sessão (logado)
@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

@app.route('/')
def index():    
    return render_template('index.html',users = User.all())

@app.route('/cadastro', methods=['POST', 'GET'])
def cadastro():
    if request.method == 'POST':
        matricula = request.form['matricula']
        email = request.form['email']
        password = request.form['password']        
        if not User.exists(matricula):
            user = User(matricula=matricula, email=email, password=password)
            user.save()            
            # 6 - logar o usuário após cadatro
            login_user(user)
            flash("Cadastro realizado com sucesso")
            return redirect(url_for('index'))
        return render_template('login.html')
    return render_template('cadastro.html')


# 7 - logar um usuário já existente
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        matricula = request.form['matricula']
        password = request.form['password']   
        user = User.get_by_matricula(matricula)
        if check_password_hash(user['password'], password):
            login_user(User.get(user['id']))
            flash("Você está logado")
            return redirect(url_for('cadastro_exe'))
        else:
            return redirect(url_for('login'))
    return render_template('login.html')
             
@app.route('/cadastro_exe', methods=['GET', 'POST'])
@login_required
def cadastro_exe():
    if request.method == 'POST':
        nome_exer = request.form['nome_exercicio']
        descricao_exer = request.form['descricao_exercicio']

        conn = obter_conexao()  
        cursor = conn.cursor()      
        cursor.execute("INSERT INTO exercicios (nome_exe, descricao) VALUES (?,?)", (nome_exer, descricao_exer))
        conn.commit()
        conn.close()

        flash('exercicio adicionado com sucesso!', 'success')
        return redirect(url_for('listar_exercicio'))
    else:
        return render_template('cadastro_exe.html')

@app.route('/listar_exercicio', methods=['POST', 'GET'])
def listar_exercicio():
    conn = obter_conexao()  
    cursor = conn.cursor()      
    exercicios = cursor.execute("SELECT * FROM exercicios").fetchall()
    conn.close()
    return render_template("listar_exercicio.html", exercicios=exercicios)
    

# 5 - bloquear uma rota
@app.route('/dashboard')
@login_required
def dash():
    return render_template('dashboard.html')

# 8 - logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

