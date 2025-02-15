import pymysql
pymysql.install_as_MySQLdb()

from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user


# Configurações do app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/users_db'  # Usando MySQL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Desativa o monitoramento de modificações (opcional)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modelo do Usuário
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    telefone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    login = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(100), nullable=False)

    def __repr__(self):
        return f"<User {self.nome}>"

# Carregar usuário pelo ID
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Rota para a página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Rota para cadastro de usuário
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nome = request.form['nome']
        telefone = request.form['telefone']
        email = request.form['email']
        login = request.form['login']
        senha = request.form['senha']
        hashed_senha = bcrypt.generate_password_hash(senha).decode('utf-8')  # Criptografando a senha

        new_user = User(nome=nome, telefone=telefone, email=email, login=login, senha=hashed_senha)
        db.session.add(new_user)
        db.session.commit()

        flash('Usuário cadastrado com sucesso!', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

# Rota para login de usuário
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        senha = request.form['senha']
        user = User.query.filter_by(login=login).first()

        if user and bcrypt.check_password_hash(user.senha, senha):
            login_user(user)
            flash('Login bem-sucedido!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Login ou senha inválidos', 'danger')
    
    return render_template('login.html')

# Rota para o perfil do usuário
@app.route('/profile')
@login_required
def profile():
    return f'Bem-vindo, {current_user.nome}!'

# Rota para logout
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Rota para pesquisar usuários
@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        search_query = request.form['search_query']
        users = User.query.filter(User.nome.like(f'%{search_query}%')).all()
        return render_template('search_results.html', users=users)
    return render_template('search.html')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Cria as tabelas no banco de dados
    app.run(debug=True)

