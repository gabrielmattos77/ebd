import sqlite3

BANCO = "ebd.db"


def conectar():
    return sqlite3.connect(BANCO)


def criar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS classes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            professor TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alunos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            ativo INTEGER NOT NULL DEFAULT 1
        )
    """)

    cursor.execute("""
        PRAGMA table_info(alunos)
    """)

    colunas_alunos = [
        coluna[1]
        for coluna in cursor.fetchall()
    ]

    if "identificacao" not in colunas_alunos:
        cursor.execute("""
            ALTER TABLE alunos
            ADD COLUMN identificacao TEXT
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS matriculas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            aluno_id INTEGER NOT NULL,
            classe_id INTEGER NOT NULL,
            data_inicio TEXT NOT NULL,
            data_fim TEXT,

            FOREIGN KEY (aluno_id) REFERENCES alunos(id),
            FOREIGN KEY (classe_id) REFERENCES classes(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS domingos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        PRAGMA table_info(domingos)
    """)

    colunas_domingos = [
        coluna[1]
        for coluna in cursor.fetchall()
    ]

    if "sem_aula" not in colunas_domingos:
        cursor.execute("""
            ALTER TABLE domingos
            ADD COLUMN sem_aula INTEGER NOT NULL DEFAULT 0
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chamadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domingo_id INTEGER NOT NULL,
            aluno_id INTEGER NOT NULL,
            presente INTEGER NOT NULL,

            FOREIGN KEY (domingo_id) REFERENCES domingos(id),
            FOREIGN KEY (aluno_id) REFERENCES alunos(id),

            UNIQUE (domingo_id, aluno_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visitantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domingo_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            identificacao TEXT,
            classe_id INTEGER NOT NULL,

            FOREIGN KEY (domingo_id) REFERENCES domingos(id),
            FOREIGN KEY (classe_id) REFERENCES classes(id)
        )
    """)

    cursor.execute("""
        PRAGMA table_info(visitantes)
    """)

    colunas_visitantes = [
        coluna[1]
        for coluna in cursor.fetchall()
    ]

    if "identificacao" not in colunas_visitantes:
        cursor.execute("""
            ALTER TABLE visitantes
            ADD COLUMN identificacao TEXT
        """)

    if "biblia" not in colunas_visitantes:
        cursor.execute("""
            ALTER TABLE visitantes
            ADD COLUMN biblia INTEGER NOT NULL DEFAULT 0
        """)

    if "revista" not in colunas_visitantes:
        cursor.execute("""
            ALTER TABLE visitantes
            ADD COLUMN revista INTEGER NOT NULL DEFAULT 0
        """)

    if "oferta" not in colunas_visitantes:
        cursor.execute("""
            ALTER TABLE visitantes
            ADD COLUMN oferta REAL NOT NULL DEFAULT 0
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros_classe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domingo_id INTEGER NOT NULL,
            classe_id INTEGER NOT NULL,
            biblias INTEGER NOT NULL DEFAULT 0,
            revistas INTEGER NOT NULL DEFAULT 0,
            oferta REAL NOT NULL DEFAULT 0,

            FOREIGN KEY (domingo_id) REFERENCES domingos(id),
            FOREIGN KEY (classe_id) REFERENCES classes(id),

            UNIQUE (domingo_id, classe_id)
        )
    """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS visitantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domingo_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            identificacao TEXT,
            classe_id INTEGER NOT NULL,

            FOREIGN KEY (domingo_id) REFERENCES domingos(id),
            FOREIGN KEY (classe_id) REFERENCES classes(id)
        )
    """)

    cursor.execute("""
        PRAGMA table_info(visitantes)
    """)

    colunas_visitantes = [
        coluna[1]
        for coluna in cursor.fetchall()
    ]

    if "identificacao" not in colunas_visitantes:
        cursor.execute("""
            ALTER TABLE visitantes
            ADD COLUMN identificacao TEXT
        """)


    cursor.execute("""
        CREATE TABLE IF NOT EXISTS registros_classe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domingo_id INTEGER NOT NULL,
            classe_id INTEGER NOT NULL,
            biblias INTEGER NOT NULL DEFAULT 0,
            revistas INTEGER NOT NULL DEFAULT 0,
            oferta REAL NOT NULL DEFAULT 0,

            FOREIGN KEY (domingo_id) REFERENCES domingos(id),
            FOREIGN KEY (classe_id) REFERENCES classes(id),

            UNIQUE (domingo_id, classe_id)
        )
    """)

    conexao.commit()
    conexao.close()

def cadastrar_classes():
    conexao = conectar()
    cursor = conexao.cursor()

    classes = [
        "Maternal",
        "Crescendo em Cristo",
        "Pré-Adolescentes",
        "Adolescentes",
        "Jovens e Adultos"
    ]

    for nome in classes:
        cursor.execute("""
            INSERT OR IGNORE INTO classes (nome, professor)
            VALUES (?, ?)
        """, (nome, "A definir"))

    conexao.commit()
    conexao.close()


def listar_classes():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome
        FROM classes
        ORDER BY id
    """)

    classes = cursor.fetchall()

    conexao.close()

    return classes

def cadastrar_aluno(nome, identificacao, classe_id, data_inicio):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO alunos (
            nome,
            identificacao
        )
        VALUES (?, ?)
    """, (nome, identificacao))

    aluno_id = cursor.lastrowid

    cursor.execute("""
        INSERT INTO matriculas (
            aluno_id,
            classe_id,
            data_inicio
        )
        VALUES (?, ?, ?)
    """, (aluno_id, classe_id, data_inicio))

    conexao.commit()
    conexao.close()

def listar_alunos_por_classe(classe_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            alunos.id,
            alunos.nome,
            alunos.ativo,
            alunos.identificacao,
            matriculas.data_inicio,

            (
                SELECT historico.motivo_fim
                FROM matriculas AS historico
                WHERE historico.aluno_id = alunos.id
                  AND historico.data_fim IS NOT NULL
                  AND historico.motivo_fim IS NOT NULL
                  AND TRIM(historico.motivo_fim) != ''
                ORDER BY historico.data_fim DESC
                LIMIT 1
            ) AS ultimo_motivo

        FROM alunos

        INNER JOIN matriculas
            ON alunos.id = matriculas.aluno_id

        WHERE matriculas.classe_id = ?
          AND matriculas.data_fim IS NULL
          AND alunos.ativo = 1

        ORDER BY alunos.nome
    """, (classe_id,))

    alunos = cursor.fetchall()

    conexao.close()

    return alunos

def listar_alunos_historico_classe(classe_id):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            alunos.id,
            alunos.nome,
            alunos.identificacao,
            matriculas.data_inicio,
            matriculas.data_fim,
            matriculas.motivo_fim,

            classe_anterior.nome,

            (
                SELECT classe_nova.nome
                FROM matriculas AS proxima
                INNER JOIN classes AS classe_nova
                    ON classe_nova.id = proxima.classe_id
                WHERE proxima.aluno_id = matriculas.aluno_id
                  AND proxima.data_inicio >= matriculas.data_fim
                  AND proxima.id > matriculas.id
                ORDER BY proxima.data_inicio ASC, proxima.id ASC
                LIMIT 1
            )

        FROM alunos

        INNER JOIN matriculas
            ON alunos.id = matriculas.aluno_id

        INNER JOIN classes AS classe_anterior
            ON classe_anterior.id = matriculas.classe_id

        WHERE matriculas.classe_id = ?
          AND matriculas.data_fim IS NOT NULL

          AND NOT EXISTS (
              SELECT 1
              FROM matriculas AS atual
              WHERE atual.aluno_id = alunos.id
                AND atual.classe_id = matriculas.classe_id
                AND atual.data_fim IS NULL
          )

        ORDER BY matriculas.data_fim DESC, alunos.nome
    """, (classe_id,))

    alunos = cursor.fetchall()

    conexao.close()

    return alunos

def mudar_aluno_de_classe(aluno_id, nova_classe_id, data_inicio, motivo):

    conexao = conectar()
    cursor = conexao.cursor()

    # Encerra a matrícula atual
    cursor.execute("""
        UPDATE matriculas
            SET data_fim = ?,
            motivo_fim = ?
            WHERE aluno_id = ?
            AND data_fim IS NULL
    """, (
        data_inicio,
        motivo,
        aluno_id
    ))

    # Cria a nova matrícula
    cursor.execute("""
        INSERT INTO matriculas (
            aluno_id,
            classe_id,
            data_inicio,
            data_fim
        )
        VALUES (?, ?, ?, NULL)
    """, (
        aluno_id,
        nova_classe_id,
        data_inicio
    ))

    conexao.commit()
    conexao.close()

def atualizar_aluno(aluno_id, nome, identificacao):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE alunos
        SET nome = ?,
            identificacao = ?
        WHERE id = ?
    """, (
        nome,
        identificacao,
        aluno_id
    ))

    conexao.commit()
    conexao.close()

def excluir_aluno_da_classe(aluno_id, data_fim):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE matriculas
        SET data_fim = ?
        WHERE aluno_id = ?
        AND data_fim IS NULL
    """, (
        data_fim,
        aluno_id
    ))

    conexao.commit()
    conexao.close()

def atualizar_professor(classe_id, professor):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE classes
        SET professor = ?
        WHERE id = ?
    """, (professor, classe_id))

    conexao.commit()
    conexao.close()


def criar_domingo(data):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO domingos (data)
        VALUES (?)
    """, (data,))

    conexao.commit()

    cursor.execute("""
        SELECT id
        FROM domingos
        WHERE data = ?
    """, (data,))

    resultado = cursor.fetchone()

    conexao.close()

    return resultado[0]


def registrar_frequencia(domingo_id, aluno_id, presente):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id
        FROM chamadas
        WHERE domingo_id = ?
          AND aluno_id = ?
    """, (domingo_id, aluno_id))

    existente = cursor.fetchone()

    if existente:
        cursor.execute("""
            UPDATE chamadas
            SET presente = ?
            WHERE domingo_id = ?
              AND aluno_id = ?
        """, (presente, domingo_id, aluno_id))
    else:
        cursor.execute("""
            INSERT INTO chamadas (
                domingo_id,
                aluno_id,
                presente
            )
            VALUES (?, ?, ?)
        """, (domingo_id, aluno_id, presente))

    conexao.commit()
    conexao.close()

def resetar_chamada(domingo_id, classe_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM chamadas
        WHERE domingo_id = ?
          AND aluno_id IN (
              SELECT matriculas.aluno_id
              FROM matriculas
              WHERE matriculas.classe_id = ?
          )
    """, (domingo_id, classe_id))

    cursor.execute("""
        DELETE FROM registros_classe
        WHERE domingo_id = ?
          AND classe_id = ?
    """, (domingo_id, classe_id))

    conexao.commit()
    conexao.close()

def obter_historico_aluno(aluno_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT domingos.data, chamadas.presente
        FROM chamadas
        INNER JOIN domingos
            ON chamadas.domingo_id = domingos.id
        WHERE chamadas.aluno_id = ?
        ORDER BY domingos.data
    """, (aluno_id,))

    historico = cursor.fetchall()

    conexao.close()

    return historico


def obter_status_aluno(aluno_id):
    historico = obter_historico_aluno(aluno_id)

    presencas_consecutivas = 0
    ausencias_consecutivas = 0

    status = "nao_matriculado"

    for data, presente in historico:

        if presente == 1:
            presencas_consecutivas += 1
            ausencias_consecutivas = 0

            if presencas_consecutivas >= 3:
                status = "matriculado"

        else:
            ausencias_consecutivas += 1
            presencas_consecutivas = 0

            if (
                status == "matriculado"
                and ausencias_consecutivas >= 4
            ):
                status = "visitante"

    return {
        "status": status,
        "presencas_consecutivas": presencas_consecutivas,
        "ausencias_consecutivas": ausencias_consecutivas
    }

def listar_domingos():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, data, sem_aula
        FROM domingos
        ORDER BY data
    """)

    domingos = cursor.fetchall()

    conexao.close()

    return domingos

def definir_domingo_sem_aula(domingo_id, sem_aula):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE domingos
        SET sem_aula = ?
        WHERE id = ?
    """, (sem_aula, domingo_id))

    conexao.commit()
    conexao.close()

def gerar_domingos_do_mes(ano, mes):
    from datetime import date, timedelta

    conexao = conectar()
    cursor = conexao.cursor()

    primeiro_dia = date(ano, mes, 1)

    # Descobre quantos dias tem o mês
    if mes == 12:
        proximo_mes = date(ano + 1, 1, 1)
    else:
        proximo_mes = date(ano, mes + 1, 1)

    ultimo_dia = proximo_mes - timedelta(days=1)

    # Procura o primeiro domingo
    dias_ate_domingo = (6 - primeiro_dia.weekday()) % 7

    domingo = primeiro_dia + timedelta(days=dias_ate_domingo)

    domingos_criados = []

    while domingo <= ultimo_dia:

        data = domingo.isoformat()

        cursor.execute("""
            INSERT OR IGNORE INTO domingos (data)
            VALUES (?)
        """, (data,))

        domingos_criados.append(data)

        domingo += timedelta(days=7)

    conexao.commit()
    conexao.close()

    return domingos_criados

def obter_frequencia_mes(aluno_id, ano, mes):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT domingos.data, chamadas.presente
        FROM domingos
        LEFT JOIN chamadas
            ON domingos.id = chamadas.domingo_id
            AND chamadas.aluno_id = ?
        WHERE strftime('%Y', domingos.data) = ?
          AND strftime('%m', domingos.data) = ?
        ORDER BY domingos.data
    """, (
        aluno_id,
        str(ano),
        f"{mes:02d}"
    ))

    frequencia = cursor.fetchall()

    conexao.close()

    return frequencia

def cadastrar_visitante(domingo_id, nome, identificacao, classe_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO visitantes (
            domingo_id,
            nome,
            identificacao,
            classe_id
        )
        VALUES (?, ?, ?, ?)
    """, (
        domingo_id,
        nome,
        identificacao,
        classe_id
    ))

    conexao.commit()
    conexao.close()


def listar_visitantes(domingo_id, classe_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            id,
            nome,
            identificacao,
            biblia,
            revista,
            oferta
        FROM visitantes
        WHERE domingo_id = ?
          AND classe_id = ?
        ORDER BY nome
    """, (domingo_id, classe_id))

    visitantes = cursor.fetchall()

    conexao.close()

    return visitantes

def excluir_visitante(visitante_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM visitantes
        WHERE id = ?
    """, (visitante_id,))

    conexao.commit()
    conexao.close()

def resetar_visitantes(domingo_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        DELETE FROM visitantes
        WHERE domingo_id = ?
    """, (domingo_id,))

    conexao.commit()
    conexao.close()

def obter_frequencia(aluno_id, domingo_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT presente
        FROM chamadas
        WHERE aluno_id = ?
          AND domingo_id = ?
    """, (aluno_id, domingo_id))

    resultado = cursor.fetchone()

    conexao.close()

    if resultado is None:
        return None

    return resultado[0]


def registrar_registro_classe(domingo_id, classe_id, biblias, revistas, oferta):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id
        FROM registros_classe
        WHERE domingo_id = ?
          AND classe_id = ?
    """, (domingo_id, classe_id))

    existente = cursor.fetchone()

    if existente:
        cursor.execute("""
            UPDATE registros_classe
            SET biblias = ?,
                revistas = ?,
                oferta = ?
            WHERE domingo_id = ?
              AND classe_id = ?
        """, (
            biblias,
            revistas,
            oferta,
            domingo_id,
            classe_id
        ))
    else:
        cursor.execute("""
            INSERT INTO registros_classe (
                domingo_id,
                classe_id,
                biblias,
                revistas,
                oferta
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            domingo_id,
            classe_id,
            biblias,
            revistas,
            oferta
        ))

    conexao.commit()
    conexao.close()


def obter_registro_classe(domingo_id, classe_id):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT biblias, revistas, oferta
        FROM registros_classe
        WHERE domingo_id = ?
          AND classe_id = ?
    """, (domingo_id, classe_id))

    resultado = cursor.fetchone()

    conexao.close()

    if resultado is None:
        return {
            "biblias": 0,
            "revistas": 0,
            "oferta": 0
        }

    return {
        "biblias": resultado[0],
        "revistas": resultado[1],
        "oferta": resultado[2]
    }

def obter_ofertas_mes(ano, mes):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            domingos.data,
            SUM(registros_classe.oferta)
        FROM registros_classe
        INNER JOIN domingos
            ON domingos.id = registros_classe.domingo_id
        WHERE strftime('%Y', domingos.data) = ?
          AND strftime('%m', domingos.data) = ?
        GROUP BY domingos.data
        ORDER BY domingos.data
    """, (
        str(ano),
        f"{mes:02d}"
    ))

    dados = cursor.fetchall()

    conexao.close()

    return dados

def obter_resumo_mes_por_classe(ano, mes):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            classes.nome,

            SUM(registros_classe.oferta) as ofertas,

            SUM(registros_classe.biblias) as biblias,

            SUM(registros_classe.revistas) as revistas

        FROM registros_classe

        INNER JOIN classes
            ON classes.id = registros_classe.classe_id

        INNER JOIN domingos
            ON domingos.id = registros_classe.domingo_id

        WHERE strftime('%Y', domingos.data)=?
          AND strftime('%m', domingos.data)=?

        GROUP BY classes.id
        ORDER BY ofertas DESC
    """, (
        str(ano),
        f"{mes:02d}"
    ))

    dados = cursor.fetchall()

    conexao.close()

    return dados

def obter_estatisticas_mes_por_classe(ano, mes):

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome
        FROM classes
        ORDER BY id
    """)

    classes = cursor.fetchall()

    resultado = []

    for classe_id, nome_classe in classes:

        # -------------------------------------------------
        # ALUNOS DA CLASSE
        # -------------------------------------------------

        cursor.execute("""
            SELECT alunos.id
            FROM alunos
            INNER JOIN matriculas
                ON alunos.id = matriculas.aluno_id
            WHERE matriculas.classe_id = ?
              AND matriculas.data_fim IS NULL
              AND alunos.ativo = 1
        """, (classe_id,))

        alunos = cursor.fetchall()

        matriculados = len(alunos)

        presentes = 0
        ausentes = 0

        # -------------------------------------------------
        # DOMINGOS DO MÊS
        # -------------------------------------------------

        cursor.execute("""
            SELECT id
            FROM domingos
            WHERE strftime('%Y', data) = ?
              AND strftime('%m', data) = ?
            ORDER BY data
        """, (
            str(ano),
            f"{mes:02d}"
        ))

        domingos = cursor.fetchall()

        # -------------------------------------------------
        # PRESENÇAS / AUSÊNCIAS
        # -------------------------------------------------

        for (aluno_id,) in alunos:

            for (domingo_id,) in domingos:

                cursor.execute("""
                    SELECT presente
                    FROM chamadas
                    WHERE domingo_id = ?
                      AND aluno_id = ?
                """, (
                    domingo_id,
                    aluno_id
                ))

                registro = cursor.fetchone()

                if registro:

                    if registro[0] == 1:
                        presentes += 1

                    elif registro[0] == 0:
                        ausentes += 1

        # -------------------------------------------------
        # VISITANTES
        # -------------------------------------------------

        cursor.execute("""
            SELECT COUNT(*)
            FROM visitantes
            INNER JOIN domingos
                ON domingos.id = visitantes.domingo_id
            WHERE visitantes.classe_id = ?
              AND strftime('%Y', domingos.data) = ?
              AND strftime('%m', domingos.data) = ?
        """, (
            classe_id,
            str(ano),
            f"{mes:02d}"
        ))

        visitantes = cursor.fetchone()[0] or 0

        # -------------------------------------------------
        # BÍBLIAS, REVISTAS E OFERTAS
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                SUM(registros_classe.biblias),
                SUM(registros_classe.revistas),
                SUM(registros_classe.oferta)
            FROM registros_classe
            INNER JOIN domingos
                ON domingos.id = registros_classe.domingo_id
            WHERE registros_classe.classe_id = ?
              AND strftime('%Y', domingos.data) = ?
              AND strftime('%m', domingos.data) = ?
        """, (
            classe_id,
            str(ano),
            f"{mes:02d}"
        ))

        dados = cursor.fetchone()

        biblias = dados[0] or 0
        revistas = dados[1] or 0
        ofertas = dados[2] or 0

        # -------------------------------------------------
        # ASSISTÊNCIAS
        # -------------------------------------------------

        assistencias = presentes + visitantes

        resultado.append({
            "classe": nome_classe,
            "matriculados": matriculados,
            "presentes": presentes,
            "ausentes": ausentes,
            "visitantes": visitantes,
            "assistencias": assistencias,
            "biblias": biblias,
            "revistas": revistas,
            "ofertas": ofertas
        })

    conexao.close()

    resultado.sort(
    key=lambda classe: (
        classe["presentes"],
        classe["assistencias"],
        classe["matriculados"]
    ),
    reverse=True
)
    return resultado

def obter_estatisticas_trimestre_por_classe(ano, tri):

    meses_por_tri = {
        1: [1, 2, 3],
        2: [4, 5, 6],
        3: [7, 8, 9],
        4: [10, 11, 12]
    }

    meses = meses_por_tri.get(tri, [1, 2, 3])

    resultado = []

    for mes in meses:

        dados_mes = obter_estatisticas_mes_por_classe(
            ano,
            mes
        )

        for classe in dados_mes:

            existente = None

            for item in resultado:

                if item["classe"] == classe["classe"]:
                    existente = item
                    break

            if existente is None:

                existente = {
                    "classe": classe["classe"],
                    "matriculados": classe["matriculados"],
                    "presentes": 0,
                    "ausentes": 0,
                    "visitantes": 0,
                    "assistencias": 0,
                    "biblias": 0,
                    "revistas": 0,
                    "ofertas": 0
                }

                resultado.append(existente)

            existente["presentes"] += classe["presentes"]
            existente["ausentes"] += classe["ausentes"]
            existente["visitantes"] += classe["visitantes"]
            existente["assistencias"] += classe["assistencias"]
            existente["biblias"] += classe["biblias"]
            existente["revistas"] += classe["revistas"]
            existente["ofertas"] += classe["ofertas"]

    resultado.sort(
        key=lambda classe: (
            classe["presentes"],
            classe["assistencias"],
            classe["matriculados"]
        ),
        reverse=True
    )

    return resultado


