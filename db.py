from main import bcrypt
import mysql.connector, requests, json
from lista_membros import *
from flask_bcrypt import Bcrypt

def db2():
	return mysql.connector.connect(host='us-cdbr-east-06.cleardb.net', user='b5010672adeb65', password='b5d9fcae', database='heroku_40a73087811b6c2')

def registrar(nick, tag, email, senha, confirmasenha, missao):
	if checainfo('nick', nick) == 'true':
		return "<span class='text-danger'>Nick já em uso</span>"
	if checainfo('email', email) == 'true':
		return "<span class='text-danger'>Email já em uso</span>"
	if checainfo('tag', tag) == 'true':
		return "<span class='text-danger'>TAG já em uso</span>"
	if senha != confirmasenha:
		return "<span class='text-danger'>Senhas não coincidem</span>"
	usuario = requests.get(f"https://www.habbo.com.br/api/public/users?name={nick}")
	membro = json.loads(usuario.content)
	if membro['motto'] != missao:
		return "<span class='text-danger'>Insira o código abaixo na missão do seu avatar</span>"
	plan = busca_lista(nick)
	if plan['Cargo'] == "-":
		return "<span class='text-danger'>Usuário não ativo na lista de membros</span>"
	senhaEncript = bcrypt.generate_password_hash(senha)
	sql = "INSERT INTO usuarios (nick, email, tag, senha, situacao) VALUES(%(nick)s, %(email)s, %(tag)s, %(senha)s, 'A')"
	nzc = db2()
	cursor = nzc.cursor()
	cursor.execute(sql, {
		'nick': nick,
		'email': email,
		'tag': tag,
		'senha': senhaEncript
	})
	nzc.commit()
	cursor.reset()
	cursor.close()
	return"<span class='text-success'>Usuário cadastrado e ativo</span>"

def logar(nick, senha2):
	nzc = db2()
	cursor = nzc.cursor()
	sql = f"SELECT id, nick, senha FROM usuarios WHERE nick=%(nome)s"
	cursor.execute(sql, {'nome': nick})
	quantidade = 0
	for(id,nick, senha) in cursor:
		quantidade = cursor.rowcount
		novaSenha = senha
	cursor.reset()
	cursor.close()
	if quantidade == 1:
		senhaEncript = bcrypt.check_password_hash(novaSenha, senha2)
		if senhaEncript == True:
			return {
				'resultado': 'false',
				'msg': "<span class='text-success'>Conectado com sucesso</span>"
			}
		else:
			return {
				'resultado': 'true',
				'msg': "<span class='text-danger'>Senha incorreta</span>"
			}
	else:
		return {
			'resultado': 'true',
			'msg': "<span class='text-danger'>Usuário não cadastrado no sistema</span>"
		}

def recuperando(nick, missao, senha, novasenha):
	usuario = requests.get(f"https://www.habbo.com.br/api/public/users?name={nick}")
	membro = json.loads(usuario.content)
	if membro['motto'] != missao:
		return "<span class='text-danger'>Insira o código abaixo na missão do seu avatar</span>"
	plan = busca_lista(nick)
	if plan['Cargo'] == "-":
		return "<span class='text-danger'>Usuário não ativo na lista de membros</span>"
	nzc = db2()
	cursor = nzc.cursor()
	sql = f"SELECT id, nick, situacao FROM usuarios WHERE nick='{nick}'"
	cursor.execute(sql)
	quantidade = 0
	for (id, nick, situacao) in cursor:
		quantidade = cursor.rowcount
		iduser = id
	cursor.reset()
	if quantidade == 1:
		senhaEncript = bcrypt.generate_password_hash(senha)
		sql = "UPDATE usuarios SET senha=%(senha)s, situacao='A' WHERE id=%(nick)s"
		cursor.execute(sql, {'senha': senhaEncript, 'nick': iduser})
		nzc.commit()
		cursor.reset()
		cursor.close()
		return "<span class='text-success'>Trocou a senha</span>"
	else:
		return "<span class='text-danger'>Usuário não encontrado em nosso sistema</span>"


def checainfo(coluna, valor):
	nzc = db2()
	cursor = nzc.cursor()
	sql = f"SELECT id, nick, email, tag FROM usuarios WHERE {coluna}='{valor}'"
	cursor.execute(sql)
	quantidade = 0
	for (id, nick, email, tag) in cursor:
		quantidade = cursor.rowcount
	cursor.reset()
	cursor.close()
	if quantidade >= 1:
		return 'true'
	else:
		return 'false'