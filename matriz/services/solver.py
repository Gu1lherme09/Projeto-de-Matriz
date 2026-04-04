EPSILON = 1e-9
VARIAVEIS = ["x", "y", "z", "w", "k", "m"]


def get_nome_variavel(indice):
    if indice < len(VARIAVEIS):
        return VARIAVEIS[indice]
    return f"x{indice + 1}"


def copiar_matriz(matriz):
    return [linha[:] for linha in matriz]


def formatar_numero(valor, casas=6):
    if abs(valor) < 1e-10:
        valor = 0.0

    if float(valor).is_integer():
        return str(int(valor))

    texto = f"{valor:.{casas}f}".rstrip("0").rstrip(".")
    return texto if texto else "0"


def matriz_para_texto(matriz):
    linhas = []
    for linha in matriz:
        esquerda = "  ".join(f"{formatar_numero(v):>8}" for v in linha[:-1])
        direita = f"{formatar_numero(linha[-1]):>8}"
        linhas.append(f"{esquerda}  |  {direita}")
    return "\n".join(linhas)


def interpretar_matriz_texto(texto):
    linhas = [linha.strip() for linha in texto.strip().splitlines() if linha.strip()]

    if not linhas:
        raise ValueError("Nenhuma linha foi informada.")

    matriz = []
    for linha in linhas:
        partes = linha.replace(";", " ").split()

        try:
            numeros = [float(x.replace(",", ".")) for x in partes]
        except ValueError:
            raise ValueError("A matriz possui valores inválidos.")

        matriz.append(numeros)

    quantidade_colunas = len(matriz[0])

    for linha in matriz:
        if len(linha) != quantidade_colunas:
            raise ValueError("Todas as linhas da matriz devem ter a mesma quantidade de colunas.")

    if quantidade_colunas != len(matriz) + 1:
        raise ValueError("A matriz ampliada deve ter n linhas e n+1 colunas.")

    return matriz


def classificar_sistema(matriz_rref, eps=EPSILON):
    quantidade_linhas = len(matriz_rref)
    quantidade_colunas = len(matriz_rref[0])
    quantidade_variaveis = quantidade_colunas - 1

    colunas_pivo = []
    linhas_pivo = {}

    for i in range(quantidade_linhas):
        encontrou_pivo = False

        for j in range(quantidade_variaveis):
            if abs(matriz_rref[i][j]) > eps:
                colunas_pivo.append(j)
                linhas_pivo[j] = i
                encontrou_pivo = True
                break

        if not encontrou_pivo and abs(matriz_rref[i][-1]) > eps:
            return "SI", colunas_pivo, linhas_pivo

    posto = len(colunas_pivo)

    if posto == quantidade_variaveis:
        return "SPD", colunas_pivo, linhas_pivo

    return "SPI", colunas_pivo, linhas_pivo


def classificacao_extenso(sigla):
    mapa = {
        "SPD": "Sistema Possível e Determinado",
        "SPI": "Sistema Possível e Indeterminado",
        "SI": "Sistema Impossível",
    }
    return mapa.get(sigla, sigla)


def resolver_solucao(rref_matriz, classificacao, colunas_pivo, linhas_pivo, eps=EPSILON):
    n = len(rref_matriz[0]) - 1

    if classificacao == "SI":
        return {
            "tipo": "sem_solucao",
            "texto": "Sistema Impossível (SI)\nNão possui solução.",
        }

    livres = [j for j in range(n) if j not in linhas_pivo]

    if classificacao == "SPD":
        partes = []
        valores = {}

        for col in range(n):
            linha = linhas_pivo[col]
            valor = rref_matriz[linha][-1]
            nome = get_nome_variavel(col)
            valores[nome] = valor
            partes.append(f"{nome} = {formatar_numero(valor)}")

        return {
            "tipo": "unica",
            "valores": valores,
            "texto": "Sistema Possível e Determinado (SPD)\n" + ", ".join(partes),
        }

    parametros = {}
    for idx, col in enumerate(livres, start=1):
        parametros[col] = f"t{idx}"

    expressoes = {}

    for col in livres:
        nome = get_nome_variavel(col)
        expressoes[nome] = parametros[col]

    for col_pivo in colunas_pivo:
        linha = linhas_pivo[col_pivo]
        nome_var = get_nome_variavel(col_pivo)
        constante = rref_matriz[linha][-1]

        partes = []
        if abs(constante) > eps:
            partes.append(formatar_numero(constante))

        for col_livre in livres:
            coef = -rref_matriz[linha][col_livre]
            if abs(coef) <= eps:
                continue

            param = parametros[col_livre]

            if abs(coef - 1) <= eps:
                partes.append(param)
            elif abs(coef + 1) <= eps:
                partes.append(f"-{param}")
            else:
                partes.append(f"{formatar_numero(coef)}*{param}")

        if partes:
            expressoes[nome_var] = " + ".join(partes).replace("+ -", "- ")
        else:
            expressoes[nome_var] = "0"

    texto_final = []
    for i in range(n):
        nome = get_nome_variavel(i)
        texto_final.append(f"{nome} = {expressoes[nome]}")

    return {
        "tipo": "infinita",
        "parametros": list(parametros.values()),
        "expressoes": expressoes,
        "texto": "Sistema Possível e Indeterminado (SPI)\n" + ", ".join(texto_final),
    }


def gauss_jordan_com_pivotamento(matriz_original, eps=EPSILON):
    matriz = copiar_matriz(matriz_original)
    linhas = len(matriz)
    colunas = len(matriz[0])

    logs = []
    linha_pivo = 0
    etapa = 1

    logs.append(
        {
            "titulo": "Matriz inicial [A|b]",
            "matriz": matriz_para_texto(matriz),
        }
    )

    for coluna_pivo in range(colunas - 1):
        if linha_pivo >= linhas:
            break

        melhor_linha = max(
            range(linha_pivo, linhas),
            key=lambda i: abs(matriz[i][coluna_pivo]),
        )

        if abs(matriz[melhor_linha][coluna_pivo]) < eps:
            logs.append(
                {
                    "titulo": f"Etapa {etapa}: coluna {coluna_pivo + 1} ignorada (pivô nulo ou próximo de zero)",
                    "matriz": matriz_para_texto(matriz),
                }
            )
            etapa += 1
            continue

        if melhor_linha != linha_pivo:
            matriz[linha_pivo], matriz[melhor_linha] = matriz[melhor_linha], matriz[linha_pivo]
            logs.append(
                {
                    "titulo": f"Etapa {etapa}: troca L{linha_pivo + 1} ↔ L{melhor_linha + 1}",
                    "matriz": matriz_para_texto(matriz),
                }
            )
            etapa += 1

        pivo = matriz[linha_pivo][coluna_pivo]

        if abs(pivo - 1.0) >= eps:
            for j in range(colunas):
                matriz[linha_pivo][j] /= pivo

            logs.append(
                {
                    "titulo": f"Etapa {etapa}: L{linha_pivo + 1} = L{linha_pivo + 1} / {formatar_numero(pivo)}",
                    "matriz": matriz_para_texto(matriz),
                }
            )
            etapa += 1

        for i in range(linhas):
            if i == linha_pivo:
                continue

            fator = matriz[i][coluna_pivo]
            if abs(fator) < eps:
                continue

            for j in range(colunas):
                matriz[i][j] -= fator * matriz[linha_pivo][j]

            logs.append(
                {
                    "titulo": f"Etapa {etapa}: L{i + 1} = L{i + 1} - ({formatar_numero(fator)}) * L{linha_pivo + 1}",
                    "matriz": matriz_para_texto(matriz),
                }
            )
            etapa += 1

        linha_pivo += 1

    for i in range(linhas):
        for j in range(colunas):
            if abs(matriz[i][j]) < eps:
                matriz[i][j] = 0.0

    classificacao, colunas_pivo, linhas_pivo = classificar_sistema(matriz, eps=eps)
    solucao = resolver_solucao(matriz, classificacao, colunas_pivo, linhas_pivo, eps=eps)

    logs.append(
        {
            "titulo": "Forma escalonada reduzida final (RREF)",
            "matriz": matriz_para_texto(matriz),
        }
    )

    return {
        "matriz_final": matriz,
        "classificacao": classificacao,
        "classificacao_extenso": classificacao_extenso(classificacao),
        "solucao": solucao,
        "logs": logs,
    }