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
            session['tag'] = 'WiT'
            session['membro'] = True
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
            session['membro'] = False
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
        session.pop('tag', None)
        session.pop('membro', None)
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
    return render_template("membros.html", lista=lista_membro(), departamentos=lista_membros_departamento())

@app.route("/auditoria")
def auditoria():
    if not 'logado' in session:
        return redirect('/login')
    return render_template("auditoria.html", mes=busca_auditoria('2023'))

@app.route("/scripts")
def scripts():
    if not 'logado' in session:
        return redirect('/login')
    if session['membro'] == False:
        return redirect('/')
    return render_template("scripts.html", scripts=busca_scripts(session['nick']))

@app.route("/script/<id>", methods=['GET', 'POST'])
def script(id):
    if not 'logado' in session:
        return redirect('/login')
    if session['membro'] == False:
        return redirect('/')
    if request.method == 'GET':
        return render_template("script.html", scripts=busca_script(id), agora=datetime.now().strftime("%d/%m/%Y %H:%M:%S"), enviou='nao enviou', teste=' ')
    elif request.method == 'POST':
        script=busca_script(id)
        presentes = request.form['presentes']
        aprovados = request.form['aprovados']
        inicio = request.form['inicio']
        tipo = request.form['tipo']
        cargo = request.form['cargo']
        comentarios = request.form['comentarios']
        fim = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if not 'final' in request.form:
            html = '<button type="button" id="btnmodal" class="btn btn-default" style="display:none;" data-toggle="modal" data-target="#modal-default">\
                  Confira os dados\
                </button>\
                <script>\
            $(function() {\
                $("#btnmodal").click();\
            });\
        </script>\
        <div class="modal fade show" id="modal-default" style="display: block; padding-right: 17px;" aria-modal="true" role="dialog">\
        <div class="modal-dialog">\
          <div class="modal-content">\
            <div class="modal-header card-outline card-primary">\
              <h4 class="modal-title">Confirme os dados</h4>\
              <button type="button" class="close" data-dismiss="modal" aria-label="Close">\
                <span aria-hidden="true">&times;</span>\
              </button>\
            </div>\
        <form name="final" method="post" action="/script/%s">\
            <input type="hidden" name="cargo" value="%s" />\
            <input type="hidden" name="tipo" value="%s" />\
            <input type="hidden" name="final" value="1">\
            <div class="modal-body">\
              <div class="row">\
                <div class="col-md-6">\
                  <div class="form-group">\
                    <label for="inicio">Início da aula</label>\
                    <input type="text" name="inicio" value="%s" id="inicio" readonly="readonly" class="form-control"/>\
                  </div>\
                </div>\
                <div class="col-md-6">\
                  <div class="formp-group">\
                    <label for="fim">Fim</label>\
                    <input type="text" name="fim" value="%s" id="fim" readonly="readonly" class="form-control"/>\
                  </div>\
                </div>\
              </div>\
              <div class="row">\
                <div class="col-md-6">\
                  <div class="form-group">\
                    <label for="presentes">Presentes</label>\
                    <input type="text" readonly="readonly" name="presentes" value="%s" class="presentes"/>\
                  </div>\
                </div>\
                <div class="col-md-6">\
                  <div class="formp-group">\
                    <label for="aprovados">Aprovados</label>\
                    <input type="text" readonly="readonly" name="aprovados" value="%s" class="aprovados"/>\
                  </div>\
                </div>\
              </div>\
              <div class="row">\
                <label for="comentarios">Comentários</label>\
                <input type="text" name="comentarios" value="%s" readonly="readonly" id="comentarios" class="form-control"/>\
              </div>\
            </div>\
            <div class="modal-footer justify-content-between">\
              <button type="button" id="editar" class="btn btn-default">Editar</button>\
              <button type="submit" class="btn btn-success">Enviar</button>\
            </div>\
                </form>\
          </div>\
          <!-- /.modal-content -->\
        </div>\
        <!-- /.modal-dialog -->\
      </div>\
      <!-- /.modal -->'%(script['Id'], cargo, script['Title'], inicio, fim, presentes, aprovados, comentarios)
            return render_template("script.html", scripts=script,
                                   agora=datetime.now().strftime("%d/%m/%Y %H:%M:%S"), teste=html, teste2=request.form)
        else:
            insereAula(tipo, cargo, inicio, presentes, aprovados, fim, comentarios, session['nick'])
            return redirect('/scripts')
    else:
        redirect('/')

@app.route("/relatorios/instrutor")
def relatorioInstrutor():
    if not 'logado' in session:
        return redirect('/login')
    if session['membro'] == False:
        return redirect('/')
    return render_template("relatorios/instrutor.html", relatorios=lista_relatorios_instrutor())

@app.route("/parciais/instrutor")
def parciaisInstrutor():
    if not 'logado' in session:
        return redirect('/login')
    if session['membro'] == False:
        return redirect('/')
    return render_template("parciais/instrutor.html", parciais=buscaParciais())

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