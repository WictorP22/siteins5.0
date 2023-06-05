import time

from flask import Flask, render_template, request, jsonify, json, session, redirect
import gspread, json, requests
from datetime import datetime
from flask_moment import Moment
from lista_membros import *
from db import *
from blogger import *
import mysql.connector
from mysql.connector import errorcode
from flask_bcrypt import Bcrypt
from random import *

db_connection = mysql.connector.connect(host='us-cdbr-east-06.cleardb.net', user='b5010672adeb65', password='b5d9fcae', database='heroku_40a73087811b6c2')
cursor = db_connection.cursor()
#gc = gspread.service_account(filename='service_acoount.json')
#sh = gc.open_by_key('1SkdGGG_ke6rE_-PACEw8EIr5PeHEPRh-t0fnp46PX88')
#worksheet = sh.worksheet("Página120")
#valor = worksheet.get('A1:D3')
app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
bcrypt = Bcrypt(app)
moment = Moment()
moment.init_app(app)
# criar a 1ª página
# route -> localhost
#template

# cria JSON
@app.route("/_relatorios")
def relatorios():
    respostas = relatoriosEst.get('B6:I')
    return jsonify(respostas)

#login
@app.route("/login", methods=['GET', 'POST'])
def login():
    if 'logado' in session:
        return redirect('/')
    if request.method == 'POST':
        enviou = logar(request.form['nick'], request.form['senha'])
        if enviou['resultado'] == 'false':
            session['logado'] = True
            session['nick'] = request.form['nick']
            return redirect('/')
        else:
            return render_template("login/login.html", enviou=enviou['msg'])
    else:
        enviou="Preencha os dados para acessar o sistema"
        return render_template("login/login.html", enviou=enviou)

#registro
@app.route("/registro", methods=['GET', 'POST'])
def registro():
    if 'logado' in session:
        return redirect('/')
    if request.method == 'POST':
        enviou = registrar(request.form['nick'], request.form['tag'], request.form['email'], request.form['senha'], request.form['confirmasenha'], session['codigo'])
        return render_template("login/register.html", enviou=enviou, codigo=session['codigo'])
    else:
        aleatorio = str(randint(0, 100))
        motto = "Ativar-INS" + aleatorio
        session['codigo'] = motto
        enviou="Preencha os dados para registrar"
    return render_template("login/register.html", enviou=enviou, codigo=session['codigo'])

#recuperar
@app.route("/recuperar", methods=['GET', 'POST'])
def recuperar():
    if 'logado' in session:
        return redirect('/')
    if request.method == 'POST':
        enviou = recuperando(request.form['nick'], session['codigo'], request.form['senha'], request.form['confirmasenha'])
        return render_template("login/recuperar.html", enviou=enviou, codigo=session['codigo'])
    else:
        aleatorio = str(randint(0, 100))
        motto = "Recuperar-INS" + aleatorio
        session['codigo'] = motto
        enviou = "Você esqueceu sua senha? Aqui você pode facilmente recuperar uma nova senha"
        return render_template("login/recuperar.html", enviou=enviou, codigo=session['codigo'])

@app.route("/convidado", methods=['GET', 'POST'])
def convidado():
    if 'logado' in session:
        return redirect('/')
    if request.method == 'POST':
        nick = request.form['nick']
        usuario = requests.get(f"https://www.habbo.com.br/api/public/users?name={nick}")
        membro = json.loads(usuario.content)
        if not 'error' in membro:
            session['logado'] = True
            session['nick'] = nick
            return redirect("/")
        else:
            return render_template("login/convidado.html", enviou="<span class='text-danger'>Não é um Habbo válido.</span>")
    else:
        return render_template("login/convidado.html", enviou="Insira seu nick para entrar como convidado")

#logou
@app.route("/logout")
def logout():
    if 'logado' in session:
        session.pop('nick', None)
        session.pop('logado', None)
    return redirect('/login')

#index
@app.route("/")
def index():
    if not 'logado' in session:
        return redirect('/login')
    return render_template("indexmeu.html", podio=busca_podio())

#documentos
@app.route("/documentos")
def documentos():
    if not 'logado' in session:
        return redirect('/login')
    return render_template("docs.html", regimento=busca_anuncio('3073735437882198575'), penal=busca_anuncio('2651698189980401399'), apostilas=busca_apostilas())

#anuncios
@app.route("/anuncios")
def anuncios():
    if not 'logado' in session:
        return redirect('/login')
    return render_template("anuncios.html", anuncios=anuncios_blogger())

#anuncio
@app.route("/anuncio/<id>")
def anuncio(id):
    if not 'logado' in session:
        return redirect('/login')
    return render_template("anuncio.html", anuncio=busca_anuncio(id))


#url variavel
@app.route("/instrutor")
def instrutores():
    if not 'logado' in session:
        return redirect('/login')
    instrutor = request.args.get('policial')
    if instrutor == '':
        return render_template("indexmeu.html")
    else:
        return render_template("instrutor.html", instrutor=instrutor, dados=consulta_instrutor(instrutor))

@app.route("/projetos")
def projetos():
    if not 'logado' in session:
        return redirect('/login')
    return render_template("projetos.html", projetos=lista_projetos())

@app.route("/membros")
def membros():
    if not 'logado' in session:
        return redirect('/login')
    return render_template("membros.html", lista=lista_membro())

@app.route("/auditoria")
def auditoria():
    if not 'logado' in session:
        return redirect('/login')
    return render_template("auditoria.html", mes=busca_auditoria('2023'))

#consultar instrutor
def consulta_instrutor(id):
    usuario = requests.get(f"https://www.habbo.com.br/api/public/users?name={id}")
    todo = json.loads(usuario.content)
    grupos = requests.get(f"https://www.habbo.com.br/api/public/groups/g-hhbr-16af3c950e9e4a38a510bd220f05c634/members")
    membros = json.loads(grupos.content)
    for membro in membros:
        if membro['uniqueId'] == todo['uniqueId']:
            grupo = 'true'
            break
        else:
            grupo = 'false'
    membro = busca_lista(id)
    return {
        "Nome": id,
        "Habbo": {
            "Missão": todo['motto'],
            "ID": todo['uniqueId'],
            "Online": todo['online'],
            "UltimaVez": todo['lastAccessTime'],
            "Visibilidade": todo['profileVisible'],
            "Grupo": grupo
        },
        "Membro": membro,
        "Historico": busca_historico_metas(id),
        "Avaliações": busca_avaliacoes(id),
        "Projetos": busca_projetos(id),
        "Infracoes": busca_infracoes(id),
        "História": busca_historia(id),
        "Parciais": busca_parcial(id, membro['Cargo'])
    }

#colocar site no ar
if __name__ == "__main__":
    app.run(debug=True)