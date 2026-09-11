from flask import Flask, render_template, request, redirect, url_for

from banco import (
    criar_banco,
    cadastrar_classes,
    cadastrar_aluno,
    listar_classes,
    listar_alunos_por_classe,
    listar_alunos_historico_classe,
    mudar_aluno_de_classe,
    atualizar_aluno,
    listar_domingos,
    definir_domingo_sem_aula,
    resetar_chamada,
    registrar_frequencia,
    obter_status_aluno,
    obter_frequencia,
    obter_frequencia_mes,
    cadastrar_visitante,
    listar_visitantes,
    excluir_visitante,
    excluir_aluno_da_classe,
    obter_registro_classe,
    registrar_registro_classe,
    obter_ofertas_mes,
    obter_resumo_mes_por_classe,
    obter_estatisticas_mes_por_classe,
    obter_estatisticas_trimestre_por_classe
    )

app = Flask(__name__)


@app.route("/")
def inicio():
    classes = listar_classes()
    domingos = listar_domingos()

    tri = int(request.args.get("tri", "1"))

    ano = int(request.args.get("ano", 2026))

    estatisticas_classes = obter_estatisticas_trimestre_por_classe(
        ano,
        tri
    )

    domingos_por_mes = {}

    for id_domingo, data, nao_teve_aula in domingos:
        ano = data[0:4]
        mes = data[5:7]

        chave_mes = f"{ano}-{mes}"

        if chave_mes not in domingos_por_mes:
            domingos_por_mes[chave_mes] = []

        domingos_por_mes[chave_mes].append(
            (id_domingo, data)
        )


    return render_template(
        "index.html",
        classes=classes,
        domingos=domingos,
        tri=tri,
        estatisticas_classes=estatisticas_classes
    )

@app.route("/chamada/resetar", methods=["POST"])
def resetar_chamada_rota():

    domingo_id = request.form.get("domingo_id")
    classe_id = request.form.get("classe_id")

    if domingo_id and classe_id:

        resetar_chamada(
            int(domingo_id),
            int(classe_id)
        )

    return redirect(
        url_for(
            "chamada",
            domingo_id=domingo_id,
            classe_id=classe_id
        )
    )

@app.route("/domingo/sem-aula", methods=["POST"])
def domingo_sem_aula():

    domingo_id = request.form.get("domingo_id")
    sem_aula = request.form.get("sem_aula")

    if domingo_id:
        definir_domingo_sem_aula(
            int(domingo_id),
            int(sem_aula)
        )

    return redirect(
        url_for(
            "chamada",
            domingo_id=domingo_id,
            classe_id=request.form.get("classe_id")
        )
    )

@app.route("/chamada", methods=["GET", "POST"])
def chamada():

    classes = listar_classes()
    domingos = listar_domingos()

    domingos_por_mes = {}

    for id_domingo, data, nao_teve_aula in domingos:
        ano = data[0:4]
        mes = data[5:7]

        chave_mes = f"{ano}-{mes}"

        if chave_mes not in domingos_por_mes:
            domingos_por_mes[chave_mes] = []

        domingos_por_mes[chave_mes].append(
            (id_domingo, data, nao_teve_aula)
        )

    if request.method == "POST":

        classe_id = request.form.get("classe_id")
        domingo_id = request.form.get("domingo_id")

        if classe_id and domingo_id:

            alunos = listar_alunos_por_classe(
                int(classe_id)
            )

            for aluno in alunos:

                aluno_id = aluno[0]

                resposta = request.form.get(
                    f"aluno_{aluno_id}_{domingo_id}"
                )

                if resposta in ("P", "A"):

                    presente = 1 if resposta == "P" else 0

                    registrar_frequencia(
                        int(domingo_id),
                        aluno_id,
                        presente
                    )

            biblias = request.form.get("biblias", "0")
            revistas = request.form.get("revistas", "0")
            oferta = request.form.get("oferta", "0")

            try:
                biblias = int(biblias)
            except ValueError:
                biblias = 0

            try:
                revistas = int(revistas)
            except ValueError:
                revistas = 0

            try:
                oferta = float(
                    oferta.replace(",", ".")
                )
            except ValueError:
                oferta = 0

            registrar_registro_classe(
                int(domingo_id),
                int(classe_id),
                biblias,
                revistas,
                oferta
            )

            return redirect(
                url_for(
                    "chamada",
                    domingo_id=domingo_id,
                    classe_id=classe_id,
                    salvo="1"
                )
            )

    domingo_id = request.args.get("domingo_id")
    classe_id = request.args.get("classe_id")

    alunos = []
    frequencias = {}
    visitantes_chamada = []

    domingo_selecionado = None
    classe_selecionada = None

    if classe_id:

        alunos = listar_alunos_por_classe(
            int(classe_id)
        )

        for aluno in alunos:

            aluno_id = aluno[0]
            frequencias[aluno_id] = {}

            for chave_mes, domingos_mes in domingos_por_mes.items():

                ano = int(chave_mes[0:4])
                mes = int(chave_mes[5:7])

                dados_mes = obter_frequencia_mes(
                    aluno_id,
                    ano,
                    mes
                )

                for data, presente in dados_mes:

                    frequencias[aluno_id][data] = presente

    if domingo_id and classe_id:

        visitantes_chamada = listar_visitantes(
            int(domingo_id),
            int(classe_id)
        )

    if domingo_id:

        for id_domingo, data, nao_teve_aula in domingos:

            if id_domingo == int(domingo_id):

                domingo_selecionado = data
                break

    if classe_id:

        for id_classe, nome in classes:

            if id_classe == int(classe_id):

                classe_selecionada = nome
                break

    salvo = request.args.get("salvo")

    resumo_chamada = {
        "matriculados": 0,
        "presentes": 0,
        "ausentes": 0,
        "visitantes": 0,
        "assistencias": 0,
        "biblias": 0,
        "revistas": 0,
        "oferta": 0
    }

    if domingo_id and classe_id:

        domingo_id_int = int(domingo_id)
        classe_id_int = int(classe_id)

        # -----------------------------------------
        # MATRICULADOS E PRESENTES
        # -----------------------------------------

        for aluno in alunos:

            aluno_id = aluno[0]

            status = obter_status_aluno(aluno_id)

            if status["status"] == "matriculado":

                resumo_chamada["matriculados"] += 1

                presenca = frequencias.get(
                    aluno_id,
                    {}
                ).get(domingo_selecionado)

                if presenca == 1:
                    resumo_chamada["presentes"] += 1

        # -----------------------------------------
        # AUSENTES
        # Matriculados - Presentes
        # -----------------------------------------

        resumo_chamada["ausentes"] = (
            resumo_chamada["matriculados"]
            - resumo_chamada["presentes"]
        )

        # -----------------------------------------
        # VISITANTES
        # -----------------------------------------

        visitantes = listar_visitantes(
            domingo_id_int,
            classe_id_int
        )

        resumo_chamada["visitantes"] = len(visitantes)

        # -----------------------------------------
        # ASSISTÊNCIAS
        # Presentes + Visitantes
        # -----------------------------------------

        resumo_chamada["assistencias"] = (
            resumo_chamada["presentes"]
            + resumo_chamada["visitantes"]
        )

        resumo_chamada["assistencias"] = (
            resumo_chamada["presentes"]
            + resumo_chamada["visitantes"]
        )

    registro_classe = {
        "biblias": 0,
        "revistas": 0,
        "oferta": 0
    }

    if domingo_id and classe_id:
        registro_classe = obter_registro_classe(
            int(domingo_id),
            int(classe_id)
        )

    resumo_chamada["biblias"] = registro_classe["biblias"]
    resumo_chamada["revistas"] = registro_classe["revistas"]
    resumo_chamada["oferta"] = registro_classe["oferta"]

    return render_template(
        "chamada.html",
        classes=classes,
        domingos=domingos,
        domingos_por_mes=domingos_por_mes,
        alunos=alunos,
        visitantes_chamada=visitantes_chamada,
        domingo_selecionado=domingo_selecionado,
        classe_selecionada=classe_selecionada,
        domingo_id=domingo_id,
        classe_id=classe_id,
        salvo=salvo,
        frequencias=frequencias,
        registro_classe=registro_classe,
        resumo_chamada=resumo_chamada,
        obter_status_aluno=obter_status_aluno,
    )

@app.route("/alunos", methods=["GET", "POST"])
def alunos():

    classes = listar_classes()

    if request.method == "POST":

        nome = request.form.get("nome", "").strip()

        identificacao = request.form.get(
            "identificacao", ""
        ).strip()

        classe_id = request.form.get("classe_id")

        if nome and classe_id:

            from datetime import date

            cadastrar_aluno(
                nome,
                identificacao,
                int(classe_id),
                date.today().isoformat()
            )

        return redirect(
            url_for(
                "alunos",
                classe_id=classe_id
            )
        )

    classe_id = request.args.get("classe_id")

    lista_alunos = []
    alunos_historico = []

    if classe_id:

        classe_id_int = int(classe_id)

        lista_alunos = listar_alunos_por_classe(
            classe_id_int
        )

        alunos_historico = listar_alunos_historico_classe(
            classe_id_int
        )

    return render_template(
        "alunos.html",
        classes=classes,
        alunos=lista_alunos,
        alunos_historico=alunos_historico,
        classe_id=classe_id
    )

@app.route("/alunos/mudar-classe", methods=["POST"])
def mudar_classe_aluno():

    aluno_id = request.form.get("aluno_id")
    nova_classe_id = request.form.get("nova_classe_id")
    motivo = request.form.get("motivo", "").strip()
    classe_atual_id = request.form.get("classe_atual_id")

    if aluno_id and nova_classe_id and motivo:

        from datetime import date

        mudar_aluno_de_classe(
            int(aluno_id),
            int(nova_classe_id),
            date.today().isoformat(),
            motivo
        )

    return redirect(
        url_for(
            "alunos",
            classe_id=classe_atual_id
        )
    )

@app.route("/alunos/excluir-classe", methods=["POST"])
def excluir_aluno_classe():

    aluno_id = request.form.get("aluno_id")
    classe_id = request.form.get("classe_id")

    if aluno_id:

        from datetime import date

        excluir_aluno_da_classe(
            int(aluno_id),
            date.today().isoformat()
        )

    return redirect(
        url_for(
            "alunos",
            classe_id=classe_id
        )
    )

@app.route("/alunos/editar", methods=["POST"])
def editar_aluno():

    aluno_id = request.form.get("aluno_id")
    nome = request.form.get("nome", "").strip()
    identificacao = request.form.get(
        "identificacao", ""
    ).strip()
    classe_id = request.form.get("classe_id")

    if aluno_id and nome:

        atualizar_aluno(
            int(aluno_id),
            nome,
            identificacao
        )

    return redirect(
        url_for(
            "alunos",
            classe_id=classe_id
        )
    )

@app.route("/visitantes/excluir", methods=["POST"])
def excluir_visitante_rota():

    visitante_id = request.form.get("visitante_id")
    domingo_id = request.form.get("domingo_id")
    classe_id = request.form.get("classe_id")

    if visitante_id:
        excluir_visitante(int(visitante_id))

    return redirect(
        url_for(
            "visitantes",
            domingo_id=domingo_id,
            classe_id=classe_id
        )
    )

@app.route("/visitantes", methods=["GET", "POST"])
def visitantes():

    classes = listar_classes()
    domingos = listar_domingos()

    domingo_id = request.args.get("domingo_id")
    classe_id = request.args.get("classe_id")

    if request.method == "POST":

        domingo_id = request.form.get("domingo_id")
        classe_id = request.form.get("classe_id")
        nome = request.form.get("nome", "").strip()
        identificacao = request.form.get(
            "identificacao", ""
        ).strip()

        if domingo_id and classe_id and nome:

            cadastrar_visitante(
                int(domingo_id),
                nome,
                identificacao,
                int(classe_id)
            )

        return redirect(
            url_for(
                "visitantes",
                domingo_id=domingo_id,
                classe_id=classe_id
            )
        )

    lista_visitantes = []

    if domingo_id and classe_id:

        lista_visitantes = listar_visitantes(
            int(domingo_id),
            int(classe_id)
        )

    return render_template(
        "visitantes.html",
        classes=classes,
        domingos=domingos,
        visitantes=lista_visitantes,
        domingo_id=domingo_id,
        classe_id=classe_id
    )

@app.route("/livro_chamada")
def livro_chamada():

    return render_template(
        "livro_chamada_inicio.html"
    )

@app.route("/relatorio_mes")
def relatorio_mes():

    ano = int(request.args.get("ano", 2026))
    mes = int(request.args.get("mes", 9))

    ofertas = obter_ofertas_mes(
        ano,
        mes
    )

    resumo_classes = obter_resumo_mes_por_classe(
        ano,
        mes
    )

    estatisticas_classes = obter_estatisticas_mes_por_classe(
        ano,
        mes
    )

    domingos = listar_domingos()

    domingos_do_mes = 0

    for id_domingo, data, nao_teve_aula in domingos:

        if data.startswith(f"{ano}-{mes:02d}"):

            domingos_do_mes += 1

    classes = listar_classes()
    total_classes = len(classes)

    total_ofertas = 0
    total_biblias = 0
    total_revistas = 0

    for linha in resumo_classes:

        total_ofertas += linha[1] or 0
        total_biblias += linha[2] or 0
        total_revistas += linha[3] or 0

    return render_template(
        "relatorio_mes.html",
        ano=ano,
        mes=mes,
        ofertas=ofertas,
        resumo_classes=resumo_classes,
        total_ofertas=total_ofertas,
        total_biblias=total_biblias,
        total_revistas=total_revistas,
        total_classes=total_classes,
        estatisticas_classes=estatisticas_classes,
        domingos_do_mes=domingos_do_mes
    )

@app.route("/relatorio_diario")
def relatorio_diario():

    domingo_id = request.args.get("domingo_id")

    domingos = listar_domingos()
    classes = listar_classes()

    if not domingo_id:
        return render_template(
            "relatorio_diario.html",
            domingos=domingos,
            domingo_selecionado=None,
            relatorio_classes=[],
            total_geral=None,
            total_anterior=None
        )

    domingo_id = int(domingo_id)

    # -------------------------------------------------
    # ENCONTRA O DOMINGO SELECIONADO
    # -------------------------------------------------

    domingo_atual = None
    indice_atual = None

    for indice, domingo in enumerate(domingos):

        if domingo[0] == domingo_id:
            domingo_atual = domingo
            indice_atual = indice
            break

    if domingo_atual is None:
        return redirect(url_for("relatorio_diario"))

    data_atual = domingo_atual[1]

    # -------------------------------------------------
    # DOMINGO ANTERIOR
    # -------------------------------------------------

    domingo_anterior = None

    if indice_atual is not None and indice_atual > 0:
        domingo_anterior = domingos[indice_atual - 1]

    # -------------------------------------------------
    # FUNÇÃO PARA MONTAR OS DADOS DE UM DOMINGO
    # -------------------------------------------------

    def montar_relatorio(id_domingo):

        resultado = []

        total = {
            "matriculados": 0,
            "presentes": 0,
            "ausentes": 0,
            "visitantes": 0,
            "assistencias": 0,
            "biblias": 0,
            "revistas": 0,
            "oferta": 0
        }

        for classe_id, nome_classe in classes:

            alunos = listar_alunos_por_classe(classe_id)

            matriculados = 0
            presentes = 0

            # -----------------------------------------
            # ALUNOS MATRICULADOS / PRESENTES
            # -----------------------------------------

            for aluno in alunos:

                aluno_id = aluno[0]

                status = obter_status_aluno(aluno_id)

                if status["status"] == "matriculado":

                    matriculados += 1

                    presenca = obter_frequencia(
                        aluno_id,
                        id_domingo
                    )

                    if presenca == 1:
                        presentes += 1

            ausentes = matriculados - presentes

            # -----------------------------------------
            # VISITANTES
            # -----------------------------------------

            visitantes_lista = listar_visitantes(
                id_domingo,
                classe_id
            )

            visitantes = len(visitantes_lista)

            # -----------------------------------------
            # ASSISTÊNCIAS
            # -----------------------------------------

            assistencias = presentes + visitantes

            # -----------------------------------------
            # BÍBLIAS / REVISTAS / OFERTA
            # -----------------------------------------

            registro = obter_registro_classe(
                id_domingo,
                classe_id
            )

            biblias = registro["biblias"] or 0
            revistas = registro["revistas"] or 0
            oferta = registro["oferta"] or 0

            dados_classe = {
                "nome": nome_classe,
                "matriculados": matriculados,
                "presentes": presentes,
                "ausentes": ausentes,
                "visitantes": visitantes,
                "assistencias": assistencias,
                "biblias": biblias,
                "revistas": revistas,
                "oferta": oferta
            }

            resultado.append(dados_classe)

            # -----------------------------------------
            # TOTAL GERAL
            # -----------------------------------------

            total["matriculados"] += matriculados
            total["presentes"] += presentes
            total["ausentes"] += ausentes
            total["visitantes"] += visitantes
            total["assistencias"] += assistencias
            total["biblias"] += biblias
            total["revistas"] += revistas
            total["oferta"] += oferta

        return {
            "classes": resultado,
            "total": total
        }

    # -------------------------------------------------
    # RELATÓRIO ATUAL
    # -------------------------------------------------

    relatorio_atual = montar_relatorio(domingo_id)

    # -------------------------------------------------
    # RELATÓRIO DO DOMINGO ANTERIOR
    # -------------------------------------------------

    relatorio_anterior = None

    if domingo_anterior:

        relatorio_anterior = montar_relatorio(
            domingo_anterior[0]
        )

    return render_template(
        "relatorio_diario.html",

        domingos=domingos,

        domingo_selecionado=domingo_atual,

        relatorio_classes=relatorio_atual["classes"],

        total_geral=relatorio_atual["total"],

        domingo_anterior=domingo_anterior,

        total_anterior=(
            relatorio_anterior["total"]
            if relatorio_anterior
            else None
        )
    )

if __name__ == "__main__":
    criar_banco()
    cadastrar_classes()

    app.run(debug=True)

