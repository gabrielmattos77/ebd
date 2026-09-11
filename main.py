from banco import (
    criar_banco,
    cadastrar_classes,
    listar_classes,
    cadastrar_aluno,
    listar_alunos_por_classe,
    atualizar_professor,
    criar_domingo,
    registrar_frequencia,
    listar_domingos,
    gerar_domingos_do_mes,
    obter_frequencia_mes,
    obter_status_aluno,
    cadastrar_visitante,
    listar_visitantes
)


def mostrar_cabecalho(titulo):
    print()
    print("=" * 50)
    print(f"{titulo:^50}")
    print("=" * 50)


def cadastrar_aluno_menu():
    mostrar_cabecalho("CADASTRO DE ALUNO")

    nome = input("Nome do aluno: ").strip()

    if not nome:
        print("\nO nome não pode ficar vazio.")
        input("\nPressione ENTER para voltar.....")
        return

    print()
    print("Escolha a classe:")
    print()

    classes = listar_classes()

    for id_classe, nome_classe in classes:
        print(f"{id_classe}. {nome_classe}")

    print()

    while True:
        opcao = input("Classe: ").strip()


        if not opcao.isdigit():
            print("Digite o número correspondente à classe.")
            continue

        classe_id = int(opcao)

        if any(id_classe == classe_id for id_classe, _ in classes):
            break

        print("Classe inválida. Escolha uma das opções acima.")

    data_inicio = date.today().isoformat()

    cadastrar_aluno(
        nome,
        classe_id,
        data_inicio
    )

    print()
    print("Aluno cadastrado com sucesso!")
    print(f"Nome: {nome}")

    for id_classe, nome_classe in classes:
        if id_classe == classe_id:
            print(f"Classe: {nome_classe}")
            break

    print(f"Data da matrícula: {data_inicio}")

    input("\nPressione ENTER para voltar.....")

def listar_alunos_menu():
    mostrar_cabecalho("LISTA DE ALUNOS")

    classes = listar_classes()

    print("Escolha a classe:")
    print()

    for id_classe, nome_classe in classes:
        print(f"{id_classe}. {nome_classe}")

    print()

    while True:
        opcao = input("Classe: ").strip()

        if not opcao.isdigit():
            print("Digite o número correspondente à classe.")
            continue

        classe_id = int(opcao)

        classe_selecionada = None

        for id_classe, nome_classe in classes:
            if id_classe == classe_id:
                classe_selecionada = nome_classe
                break

        if classe_selecionada:
            break

        print("Classe inválida. Escolha uma das opções acima.")

    alunos = listar_alunos_por_classe(classe_id)

    mostrar_cabecalho(classe_selecionada)

    if not alunos:
        print("Nenhum aluno cadastrado nesta classe.")
    else:
        print(f"Total de alunos: {len(alunos)}")
        print()

        for numero, aluno in enumerate(alunos, start=1):
            aluno_id, nome, ativo, data_inicio = aluno

            status = obter_status_aluno(aluno_id)

            if status["status"] == "matriculado":
                cor = "\033[92m"
                texto_status = "MATRICULADO"

            elif status["status"] == "visitante":
                cor = "\033[93m"
                texto_status = "VISITANTE"

            else:
                cor = "\033[91m"
                texto_status = "NÃO MATRICULADO"

            resetar_cor = "\033[0m"

            print(
                f"{cor}{numero:02d}. {nome} "
                f"— {texto_status}{resetar_cor}"
            )

    print()
    input("Pressione ENTER para voltar...")

def cadastrar_professor_menu():
    mostrar_cabecalho("CADASTRO DE PROFESSOR")

    classes = listar_classes()

    print("Escolha a classe:")
    print()

    for id_classe, nome_classe in classes:
        print(f"{id_classe}. {nome_classe}")

    print()

    while True:
        opcao = input("Classe: ").strip()

        if not opcao.isdigit():
            print("Digite o número correspondente à classe.")
            continue

        classe_id = int(opcao)

        classe_selecionada = None

        for id_classe, nome_classe in classes:
            if id_classe == classe_id:
                classe_selecionada = nome_classe
                break

        if classe_selecionada:
            break

        print("Classe inválida. Escolha uma das opções acima.")

    print()
    professor = input("Nome do professor: ").strip()

    if not professor:
        print("\nO nome do professor não pode ficar vazio.")
        input("Pressione ENTER para voltar...")
        return

    atualizar_professor(classe_id, professor)

    print()
    print("Professor cadastrado com sucesso!")
    print(f"Classe: {classe_selecionada}")
    print(f"Professor: {professor}")

    input("\nPressione ENTER para voltar.....")

def registrar_domingo_menu():
    mostrar_cabecalho("REGISTRAR DOMINGO")

    print("Digite a data do domingo.")
    print("Formato: DD/MM/AAAA")
    print()

    data_digitada = input("Data: ").strip()

    try:
        dia, mes, ano = data_digitada.split("/")

        if len(dia) != 2 or len(mes) != 2 or len(ano) != 4:
            raise ValueError

        data = f"{ano}-{mes}-{dia}"

    except ValueError:
        print()
        print("Data inválida.")
        print("Use o formato DD/MM/AAAA.")
        input("\nPressione ENTER para voltar.....")
        return

    criar_domingo(data)

    print()
    print("Domingo registrado com sucesso!")
    print(f"Data: {data_digitada}")

    input("\nPressione ENTER para voltar...")

def realizar_chamada_menu():
    mostrar_cabecalho("CHAMADA")

    domingos = listar_domingos()

    if not domingos:
        print("Nenhum domingo foi registrado.")
        print("Primeiro registre um domingo.")
        input("\nPressione ENTER para voltar.....")
        return

    print("Escolha o domingo:")
    print()

    for id_domingo, data in domingos:
        ano, mes, dia = data.split("-")
        print(f"{id_domingo}. {dia}/{mes}/{ano}")

    print()

    while True:
        opcao = input("Domingo: ").strip()

        domingo_selecionado = None
        domingo_id = None

        # Escolha pelo número
        if opcao.isdigit():
            numero = int(opcao)

            for id_domingo, data in domingos:
                if id_domingo == numero:
                    domingo_id = id_domingo
                    domingo_selecionado = data
                    break

        # Escolha pela data
        else:
            partes = opcao.split("/")

            if len(partes) == 3:
                dia, mes, ano = partes
                data_digitada = f"{ano}-{mes}-{dia}"

                for id_domingo, data in domingos:
                    if data == data_digitada:
                        domingo_id = id_domingo
                        domingo_selecionado = data
                        break

        if domingo_selecionado:
            break

        print("Domingo inválido.")
        print("Digite o número ou a data no formato DD/MM/AAAA.")

    classes = listar_classes()

    print()
    print("Escolha a classe:")
    print()

    for id_classe, nome_classe in classes:
        print(f"{id_classe}. {nome_classe}")

    print()

    while True:
        opcao = input("Classe: ").strip()

        if not opcao.isdigit():
            print("Digite o número correspondente à classe.")
            continue

        classe_id = int(opcao)

        classe_selecionada = None

        for id_classe, nome_classe in classes:
            if id_classe == classe_id:
                classe_selecionada = nome_classe
                break

        if classe_selecionada:
            break

        print("Classe inválida.")

    alunos = listar_alunos_por_classe(classe_id)

    ano, mes, dia = domingo_selecionado.split("-")

    mostrar_cabecalho(
        f"{classe_selecionada} — {dia}/{mes}/{ano}"
    )

    if not alunos:
        print("Nenhum aluno cadastrado nesta classe.")
        input("\nPressione ENTER para voltar.....")
        return

    print("Digite P para presente ou A para ausente.")
    print()

    while True:
        print()
        print("Digite P = Presente")
        print("Digite A = Ausente")
        print("Digite C = Corrigir chamada")
        print("Digite F = Finalizar")
        print("Digite V = Adicionar visitante")
        print()

        for numero, aluno in enumerate(alunos, start=1):
            aluno_id, nome, ativo, data_inicio = aluno

        status = obter_status_aluno(aluno_id)

        if status["status"] == "matriculado":
            simbolo = "🟢"
            texto_status = "MATRICULADO"
        elif status["status"] == "visitante":
            simbolo = "🟠"
            texto_status = "VISITANTE"
        else:
            simbolo = "🔴"
            texto_status = "NÃO MATRICULADO"

        resposta = input(
            f"{simbolo} {numero:02d}. {nome} "
            f"[{texto_status}] (P/A/C/F): "
        ).strip().upper()

        if resposta == "F":
            break

        if resposta == "V":
            print()
            print("CADASTRO DE VISITANTE")
            print()

            nome_visitante = input(
                "Nome do visitante: "
            ).strip()

            if not nome_visitante:
                print("O nome não pode ficar vazio.")
                continue

            identificacao = input(
                "Identificação/observação (opcional): "
            ).strip()

            cadastrar_visitante(
                domingo_id,
                nome_visitante,
                identificacao,
                classe_id
            )

            print()
            print("Visitante cadastrado com sucesso!")

            if identificacao:
                print(
                    f"🟠 {nome_visitante} "
                    f"({identificacao})"
                )
            else:
                print(f"🟠 {nome_visitante}")

            continue

        if resposta == "C":
            print()
            print("CORREÇÃO DE CHAMADA")
            print()

            for numero_correcao, aluno_correcao in enumerate(
                alunos, start=1
            ):
                aluno_id_correcao = aluno_correcao[0]
                nome_correcao = aluno_correcao[1]

                frequencias = obter_frequencia_mes(
                    aluno_id_correcao,
                    int(domingo_selecionado.split("-")[0]),
                    int(domingo_selecionado.split("-")[1])
                  )

                frequencia_atual = None

                for data, presente in frequencias:
                    if data == domingo_selecionado:
                        frequencia_atual = presente
                        break

                if frequencia_atual is None:
                    marcador = "-"
                elif frequencia_atual == 1:
                    marcador = "P"
                else:
                    marcador = "A"

                print(
                    f"{numero_correcao:02d}. "
                    f"{nome_correcao:<25} [{marcador}]"
                )

            print()
            print("Digite o número do aluno que deseja corrigir.")
            print("0 = Cancelar")
            print()

            escolha = input("Aluno: ").strip()

            if not escolha.isdigit():
                print("Digite um número válido.")
                continue

            numero_aluno = int(escolha)

            if numero_aluno == 0:
                continue

            if numero_aluno < 1 or numero_aluno > len(alunos):
                print("Aluno inválido.")
                continue

            aluno_correcao = alunos[numero_aluno - 1]
            aluno_id_correcao = aluno_correcao[0]
            nome_correcao = aluno_correcao[1]

            print()
            print(f"Aluno: {nome_correcao}")
            print("P = Presente")
            print("A = Ausente")
            print("0 = Cancelar")
            print()

            nova_frequencia = input(
                "Nova frequência: "
            ).strip().upper()

            if nova_frequencia == "0":
                continue

            if nova_frequencia not in ("P", "A"):
                print("Digite somente P ou A.")
                continue

            presente = 1 if nova_frequencia == "P" else 0

            registrar_frequencia(
                domingo_id,
                aluno_id_correcao,
                presente
            )

            print()
            print("Frequência corrigida com sucesso!")

            continue

        if resposta in ("P", "A"):
            presente = 1 if resposta == "P" else 0

            registrar_frequencia(
                domingo_id,
                aluno_id,
                presente
            )

        else:
            print("Digite P, A, C ou F.")

    print()
    print("Chamada finalizada.")
    input("Pressione ENTER para voltar...")

def cadastrar_visitante_menu():
    mostrar_cabecalho("CADASTRO DE VISITANTE")

    domingos = listar_domingos()

    if not domingos:
        print("Nenhum domingo foi registrado.")
        print("Primeiro registre um domingo.")
        input("\nPressione ENTER para voltar...")
        return

    print("Escolha o domingo:")
    print()

    for id_domingo, data in domingos:
        ano, mes, dia = data.split("-")
        print(f"{id_domingo}. {dia}/{mes}/{ano}")

    print()

    while True:
        opcao = input("Domingo: ").strip()

        if not opcao.isdigit():
            print("Digite o número correspondente ao domingo.")
            continue

        domingo_id = int(opcao)

        if any(id_domingo == domingo_id for id_domingo, _ in domingos):
            break

        print("Domingo inválido.")

    print()

    nome = input("Nome do visitante: ").strip()

    if not nome:
        print("O nome não pode ficar vazio.")
        input("\nPressione ENTER para voltar...")
        return

    identificacao = input(
        "Identificação/observação (opcional): "
    ).strip()

    print()
    print("Escolha a classe:")
    print()

    classes = listar_classes()

    for id_classe, nome_classe in classes:
        print(f"{id_classe}. {nome_classe}")

    print()

    while True:
        opcao = input("Classe: ").strip()

        if not opcao.isdigit():
            print("Digite o número correspondente à classe.")
            continue

        classe_id = int(opcao)

        if any(id_classe == classe_id for id_classe, _ in classes):
            break

        print("Classe inválida.")

    cadastrar_visitante(
        domingo_id,
        nome,
        identificacao,
        classe_id
    )

    print()
    print("Visitante cadastrado com sucesso!")
    print(f"Nome: {nome}")

    if identificacao:
        print(f"Identificação: {identificacao}")

    for id_classe, nome_classe in classes:
        if id_classe == classe_id:
            print(f"Classe: {nome_classe}")
            break

    input("\nPressione ENTER para voltar...")

def gerar_domingos_menu():
    mostrar_cabecalho("GERAR DOMINGOS DO MÊS")

    while True:
        ano_texto = input("Ano: ").strip()

        if not ano_texto.isdigit():
            print("Digite um ano válido.")
            continue

        ano = int(ano_texto)

        if ano < 2000 or ano > 2100:
            print("Digite um ano entre 2000 e 2100.")
            continue

        break

    while True:
        mes_texto = input("Mês (1-12): ").strip()

        if not mes_texto.isdigit():
            print("Digite um número de 1 a 12.")
            continue

        mes = int(mes_texto)

        if 1 <= mes <= 12:
            break

        print("Mês inválido.")

    domingos = gerar_domingos_do_mes(ano, mes)

    print()

    if not domingos:
        print("Nenhum domingo encontrado.")
    else:
        print("Domingos registrados:")

        for data in domingos:
            ano_d, mes_d, dia_d = data.split("-")
            print(f"• {dia_d}/{mes_d}/{ano_d}")

    print()
    print("Domingos do mês gerados com sucesso!")

    input("\nPressione ENTER para voltar...")

def chamada_mensal_menu():
    mostrar_cabecalho("CHAMADA MENSAL")

    while True:
        ano_texto = input("Ano: ").strip()

        if not ano_texto.isdigit():
            print("Digite um ano válido.")
            continue

        ano = int(ano_texto)

        if 2000 <= ano <= 2100:
            break

        print("Digite um ano entre 2000 e 2100.")

    while True:
        mes_texto = input("Mês (1-12): ").strip()

        if not mes_texto.isdigit():
            print("Digite um número de 1 a 12.")
            continue

        mes = int(mes_texto)

        if 1 <= mes <= 12:
            break

        print("Mês inválido.")

    gerar_domingos_do_mes(ano, mes)

    domingos = [
        (id_domingo, data)
        for id_domingo, data in listar_domingos()
        if data.startswith(f"{ano:04d}-{mes:02d}-")
    ]

    if not domingos:
        print("Nenhum domingo encontrado.")
        input("\nPressione ENTER para voltar...")
        return

    classes = listar_classes()

    print()
    print("Escolha a classe:")
    print()

    for id_classe, nome_classe in classes:
        print(f"{id_classe}. {nome_classe}")

    print()

    while True:
        opcao = input("Classe: ").strip()

        if not opcao.isdigit():
            print("Digite o número correspondente à classe.")
            continue

        classe_id = int(opcao)

        classe_selecionada = None

        for id_classe, nome_classe in classes:
            if id_classe == classe_id:
                classe_selecionada = nome_classe
                break

        if classe_selecionada:
            break

        print("Classe inválida.")

    while True:
        mostrar_cabecalho(
            f"CHAMADA — {classe_selecionada} — "
            f"{mes:02d}/{ano}"
        )

        alunos = listar_alunos_por_classe(classe_id)

        print(f"{'Aluno':<25}", end="")

        for _, data in domingos:
            dia = data.split("-")[2]
            print(f"{dia:>8}", end="")

        print()
        print("-" * (25 + len(domingos) * 8))

        for aluno in alunos:
            aluno_id, nome, ativo, data_inicio = aluno

            status = obter_status_aluno(aluno_id)

            if status["status"] == "matriculado":
                simbolo = "🟢"
                texto_status = "MATRICULADO"
            elif status["status"] == "visitante":
                simbolo = "🟠"
                texto_status = "VISITANTE"
            else:
                simbolo = "🔴"
                texto_status = "NÃO MATRICULADO"

            frequencias = obter_frequencia_mes(
                aluno_id,
                ano,
                mes
            )

            frequencias_por_data = {
                data: presente
                for data, presente in frequencias
            }

            print(
                f"{simbolo} {nome:<21}",
                end=""
            )

            for _, data in domingos:
                presente = frequencias_por_data.get(data)

                if presente is None:
                    marcador = "-"
                elif presente == 1:
                    marcador = "P"
                else:
                    marcador = "A"

                print(f"{marcador:>8}", end="")

            print()

        print()
        print("1. Registrar/alterar frequência")
        print("0. Voltar")
        print()

        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            break

        if opcao != "1":
            print("Opção inválida.")
            input("Pressione ENTER...")
            continue

        print()
        print("Escolha o domingo:")

        for numero, (_, data) in enumerate(domingos, start=1):
            ano_d, mes_d, dia_d = data.split("-")
            print(f"{numero}. {dia_d}/{mes_d}/{ano_d}")

        print("0. Cancelar")
        print()

        opcao_domingo = input("Domingo: ").strip()

        if not opcao_domingo.isdigit():
            print("Digite um número válido.")
            input("Pressione ENTER...")
            continue

        numero_domingo = int(opcao_domingo)

        if numero_domingo == 0:
            continue

        if numero_domingo < 1 or numero_domingo > len(domingos):
            print("Domingo inválido.")
            input("Pressione ENTER...")
            continue

        domingo_id, data_domingo = domingos[numero_domingo - 1]

        print()
        print(
            f"CHAMADA DO DIA "
            f"{data_domingo.split('-')[2]}/"
            f"{data_domingo.split('-')[1]}/"
            f"{data_domingo.split('-')[0]}"
        )
        print()

        for numero, aluno in enumerate(alunos, start=1):
            aluno_id, nome, ativo, data_inicio = aluno

            status = obter_status_aluno(aluno_id)

            if status["status"] == "matriculado":
                simbolo = "🟢"
                texto_status = "MATRICULADO"
            elif status["status"] == "visitante":
                simbolo = "🟠"
                texto_status = "VISITANTE"
            else:
                simbolo = "🔴"
                texto_status = "NÃO MATRICULADO"

            while True:
                resposta = input(
                    f"{simbolo} {numero:02d}. {nome} "
                    f"[{texto_status}] "
                    f"(P/A): "
                ).strip().upper()

                if resposta in ("P", "A"):
                    presente = 1 if resposta == "P" else 0

                    registrar_frequencia(
                        domingo_id,
                        aluno_id,
                        presente
                    )

                    break

                print("Digite somente P ou A.")

        print()
        print("Chamada registrada com sucesso!")
        input("Pressione ENTER para atualizar a tabela...")

def menu_principal():
    while True:
        mostrar_cabecalho("CONTROLE DA EBD")

        print("1. Registrar domingo")
        print("2. Gerar domingos do mês")
        print("3. Cadastrar aluno")
        print("4. Cadastrar professor")
        print("5. Listar alunos")
        print("6. Fazer chamada")
        print("7. Chamada mensal")
        print("8. Histórico")
        print("9. Cadastrar visitante")
        print("10. Relatórios")
        print("0. Sair")

        print()
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "1":
            registrar_domingo_menu()

        elif opcao == "2":
            gerar_domingos_menu()

        elif opcao == "3":
            cadastrar_aluno_menu()

        elif opcao == "4":
            cadastrar_professor_menu()

        elif opcao == "5":
            listar_alunos_menu()

        elif opcao == "6":
            realizar_chamada_menu()

        elif opcao == "7":
            chamada_mensal_menu()

        elif opcao == "8":
            print("\n[Histórico]")
            input("Pressione ENTER para voltar...")

        elif opcao == "9":
           cadastrar_visitante_menu()

        elif opcao == "10":
           relatorios_menu()

        elif opcao == "0":
            print("\nEncerrando o sistema...")
            break

        else:
            print("\nOpção inválida.")
            input("Pressione ENTER para tentar novamente...")

def main():
    criar_banco()
    cadastrar_classes()

    menu_principal()


if __name__ == "__main__":
    main()

