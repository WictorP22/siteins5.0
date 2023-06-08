import gspread, json, requests
from datetime import datetime, date, timedelta, timezone

gc = gspread.service_account(filename='service_acoount.json')
planilha_central = gc.open_by_key('1NeWXNJnloZ4n_4DoOy3v2XPx3Q2EIFQOO_8mtU6FabA')
def busca_lista(nick):
    aba_lista_de_membros = planilha_central.worksheet("[x] Lista de Membros")
    lista = aba_lista_de_membros.get('AE2:Aq')
    for membro in lista:
        if membro[1] == nick:
            data = datetime.strptime(membro[2], '%d/%m/%Y')
            return {
                "Cargo": membro[0],
                "Nick": membro[1],
                "Entrada": data,
                "Promoção": membro[3],
                "CAP": membro[4],
                "PromoBloq": membro[5],
                "InicioLicença": membro[6],
                "FimLicença": membro[7],
                "Ministério": membro[8],
                "AV": membro[9],
                "TAGs": membro[10],
                "Situação": membro[11],
                "TAG": membro[12]
            }
    return {
        "Cargo": "-"
    }


def busca_historico_metas(nick):
    aba_historico_metas = planilha_central.worksheet('[x] Junta Tudo')
    metas = aba_historico_metas.get('L:U')
    retorno = []
    for meta in metas:
        if(meta[2] == nick):
            inicio = datetime.strptime(meta[0], '%d/%m/%Y')
            fim = datetime.strptime(meta[1], '%d/%m/%Y')
            retorno.append({
                "Inicio": inicio,
                "Fim": fim,
                "Professor": meta[2],
                "Meta1": meta[3],
                "Meta2": meta[4],
                "Meta3": meta[5],
                "Meta4": meta[6],
                "Meta5": meta[7],
                "Situação": meta[8],
                "Tipo": meta[9]
            })
    return retorno

def busca_avaliacoes(nick):
    aba_avaliacoes = planilha_central.worksheet('[x] Avaliações')
    avaliacoes = aba_avaliacoes.get('A:M')
    retorno = []
    for avaliacao in avaliacoes:
        if avaliacao[3].strip() == nick:
            inicio = datetime.strptime(avaliacao[0], '%d/%m/%Y %H:%M:%S')
            fim = datetime.strptime(avaliacao[4], '%d/%m/%Y %H:%M:%S')
            retorno.append({
                "Inicio": inicio,
                "Fim": fim,
                "Avaliador": avaliacao[1],
                "Fake": avaliacao[2],
                "Instrutor": avaliacao[3],
                "Corredor": avaliacao[5],
                "Aula": avaliacao[6],
                "Teste": avaliacao[7],
                "Comandos": avaliacao[8],
                "Finalização": avaliacao[9],
                "Comentários": avaliacao[10],
                "Qualidade": avaliacao[11],
                "Anexos": avaliacao[12]
            })
    return retorno

def busca_infracoes(nick):
    aba_infracoes = planilha_central.worksheet('[x] Infrações')
    infracoes = aba_infracoes.get('J2:Q')
    retorno = []
    for infracao in infracoes:
        if infracao[2] == nick:
            data = datetime.strptime(infracao[4], '%d/%m/%Y')
            retorno.append({
                "data": data,
                "Fiscalizador": infracao[1],
                "Infrator": infracao[2],
                "Infração": infracao[3],
                "Anexo": infracao[5],
                "ID": infracao[0],
                "Gravidade": infracao[7]
            })
    return retorno

def busca_projetos(nick):
    aba_projetos = planilha_central.worksheet('[x] Projetos')
    projetos = aba_projetos.get('W2:AC')
    retorno = []
    for projeto in projetos:
        if projeto[1] == nick:
            data = datetime.strptime(projeto[0], '%d/%m/%Y %H:%M:%S')
            retorno.append({
                "data": data,
                "Autor": projeto[1],
                "Modalidade": projeto[3],
                "Tema": projeto[4],
                "Veredito": projeto[5],
                "Ordem": projeto[2]
            })
    return retorno

def busca_historia(nick):
    aba_historia = planilha_central.worksheet('[x] História dos Instrutores')
    historias = aba_historia.get('B2:I')
    for historia in historias:
        if historia[0] == nick:
            return {
                "Cargo": historia[1],
                "história": historia[2],
                "Contribuições": historia[3],
                "Novatos": historia[4],
                "SubGrupos": historia[5],
                "Conquistas": historia[6],
                "Anos": historia[7]
            }

def busca_parcial(nick, cargo):
    aba_metas = planilha_central.worksheet('[x] Metas')
    if ((cargo == 'Instrutor') or (cargo == 'Aprendiz')):
        metas = aba_metas.get('A2:H')
        for meta in metas:
            if meta[0] == nick:
                return {
                    "Tipo": "Instrutor",
                    "Meta1": meta[1],
                    "Meta2": meta[2],
                    "Meta3": meta[3],
                    "Meta4": meta[4],
                    "Pontos": meta[5],
                    "Situação": meta[7]
                }
    elif cargo == 'Graduador':
        metas = aba_metas.get('R2:W')
        for meta in metas:
            if meta[0] == nick:
                return {
                    "Tipo": "Graduador",
                    "Meta1": meta[1],
                    "Meta2": meta[2],
                    "Meta3": "-",
                    "Meta4": "-",
                    "Pontos": meta[3],
                    "Situação": meta[5]
                }
    elif cargo == 'Avaliador':
        metas = aba_metas.get('AF2:AK')
        for meta in metas:
            if meta[0] == nick:
                return {
                    "Tipo": "Avaliador",
                    "Meta1": meta[1],
                    "Meta2": "-",
                    "Meta3": "-",
                    "Meta4": "-",
                    "Pontos": meta[2],
                    "Situação": meta[4]
                }
    elif cargo == 'Capacitador':
        metas = aba_metas.get('AS2:AW')
        for meta in metas:
            if meta[0] == nick:
                return {
                    "Tipo": "Capacitador",
                    "Meta1": meta[1],
                    "Meta2": "-",
                    "Meta3": "-",
                    "Meta4": "-",
                    "Pontos": meta[1],
                    "Situação": meta[3]
                }
    else:
        return {
            "Tipo": 'false'
        }

def busca_apostilas():
    aba_apostilas = planilha_central.worksheet('[x] Apostilas e Dicas')
    apostilas = aba_apostilas.get('A2:D')
    retorno = []
    for apostila in apostilas:
        data = datetime.strptime(apostila[0], '%d/%m/%Y')
        retorno.append({
            "Titulo": apostila[3],
            "Link": apostila[2],
            "Autor": apostila[1],
            "Data": data
        })
    return retorno

def busca_podio():
    aba_podio = planilha_central.worksheet('[x] Pódio')
    podio = aba_podio.get('A2:H24')
    retorno = []
    for pod in podio:
        retorno.append({
            "Nick": pod[0],
            "CFSd": pod[1],
            "CFC1": pod[2],
            "CFC2": pod[3],
            "CAP": pod[4],
            "Pontos": pod[5],
            "Situação": pod[7]
        })
    return retorno

def lista_projetos():
    aba_projetos = planilha_central.worksheet('[x] Projetos')
    projetos = aba_projetos.get('W2:AC')
    retorno = []
    for projeto in projetos:
        data = datetime.strptime(projeto[0], '%d/%m/%Y %H:%M:%S')
        retorno.append({
            "data": data,
            "Autor": projeto[1],
            "Modalidade": projeto[3],
            "Tema": projeto[4],
            "Veredito": projeto[5],
            "Ordem": projeto[2],
            "Comentário": projeto[6]
        })
    return retorno

def lista_relatorios_instrutor():
    aba_aulas = planilha_central.worksheet('[x] Relatórios')
    aulas = aba_aulas.get('A2:G')
    retorno = []
    for aula in aulas:
        retorno.append({
            "Instrutor": aula[0],
            "Início": aula[1],
            "CursoExtenso": aula[2],
            "Presentes": aula[3],
            "Aprovados": aula[4],
            "Comentários": aula[5],
            "AulaAbreviada": aula[6]
        })
    return retorno

def lista_membro():
    aba_lista_de_membros = planilha_central.worksheet("[X] Lista de Membros 2")
    lista = aba_lista_de_membros.get('S2:Z')
    cargos = aba_lista_de_membros.get("AD2:AD")
    retorno = {};
    for cargo in cargos:
        retorno[cargo[0]] = {}
        i = 0
        for membro in lista:
            if membro[0] == cargo[0]:
                entrada = datetime.strptime(membro[2], '%d/%m/%Y')
                nentrada = entrada + timedelta(days=1)
                if not membro[3]:
                    promo = "-";
                else:
                    promo = datetime.strptime(membro[3], '%d/%m/%Y') + timedelta(days=1)
                retorno[cargo[0]][i] = {
                    "Cargo": membro[0],
                    "Nick": membro[1],
                    "Entrada": nentrada,
                    "Promo": promo,
                    "CAP": membro[4],
                    "AV": membro[5],
                    "SubGrupos": membro[6],
                    "Situação": membro[7]
                }
                i = i+1
    return retorno;