EPSILON = 1e-9

# ============================================================
# VARIÁVEIS SIMBÓLICAS
# ============================================================
# Estas variáveis são usadas para montar a solução final.
# Exemplo:
#   x = 2
#   y = -1
#   z = 5
#
# Se o sistema tiver mais variáveis do que as listadas aqui,
# o código continua funcionando e usa nomes como x7, x8, ...
# ============================================================
VARIAVEIS = ["x", "y", "z", "w", "k", "m"]


def get_nome_variavel(indice):
    """
    Retorna o nome simbólico da variável na posição 'indice'.

    Exemplo:
        indice = 0 -> x
        indice = 1 -> y
        indice = 2 -> z
    """
    if indice < len(VARIAVEIS):
        return VARIAVEIS[indice]
    return f"x{indice + 1}"


def copiar_matriz(matriz):
    """
    Retorna uma cópia profunda da matriz.

    Isso evita alterar a matriz original enviada para o algoritmo.
    """
    return [linha[:] for linha in matriz]


def formatar_numero(valor, casas=6):
    """
    Formata números para exibição.

    Regras:
    - valores muito pequenos viram 0
    - inteiros aparecem sem casas decimais
    - decimais aparecem com até 'casas' casas
    """
    if abs(valor) < 1e-10:
        valor = 0.0

    if float(valor).is_integer():
        return str(int(valor))

    texto = f"{valor:.{casas}f}".rstrip("0").rstrip(".")
    return texto if texto else "0"


def matriz_para_texto(matriz):
    """
    Converte a matriz ampliada [A|b] para texto formatado.

    Exemplo visual:
        1   2   3 | 4
        0   1  -1 | 2
    """
    linhas = []
    for linha in matriz:
        esquerda = "  ".join(f"{formatar_numero(v):>8}" for v in linha[:-1])
        direita = f"{formatar_numero(linha[-1]):>8}"
        linhas.append(f"{esquerda}  |  {direita}")
    return "\n".join(linhas)


def interpretar_matriz_texto(texto):
    """
    Interpreta a matriz ampliada [A|b] a partir de um texto.

    ============================================================
    INTERPRETAÇÃO MATEMÁTICA
    ============================================================
    Cada linha representa uma equação linear.

    Exemplo:
        1  2  3  10
        0  1 -1   4

    significa:
        1x + 2y + 3z = 10
        0x + 1y - 1z = 4

    Ou seja:
        [A|b] = matriz dos coeficientes + coluna dos termos independentes
    ============================================================

    Regras:
    - cada linha deve ter a mesma quantidade de colunas
    - deve existir pelo menos 1 coeficiente e a coluna b
    - aceita ponto ou vírgula decimal
    """
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

    if quantidade_colunas < 2:
        raise ValueError("A matriz ampliada deve ter ao menos uma coluna de coeficientes e a coluna b.")

    for linha in matriz:
        if len(linha) != quantidade_colunas:
            raise ValueError("Todas as linhas da matriz devem ter a mesma quantidade de colunas.")

    return matriz


def classificar_sistema(matriz_rref, eps=EPSILON):
    """
    Classifica o sistema após obter a forma escalonada reduzida (RREF).

    ============================================================
    CLASSIFICAÇÃO MATEMÁTICA
    ============================================================

    Seja:
        m = número de equações
        n = número de variáveis

    Após o escalonamento:

    1) SI = Sistema Impossível
       Acontece quando aparece uma linha do tipo:
           0x + 0y + 0z = c, com c != 0
       Exemplo:
           0  0  0 | 5

       Isso é uma contradição: 0 = 5

    2) SPD = Sistema Possível e Determinado
       Ocorre quando o número de pivôs = número de variáveis.
       Nesse caso, existe solução única.

    3) SPI = Sistema Possível e Indeterminado
       Ocorre quando o número de pivôs < número de variáveis.
       Nesse caso, existem variáveis livres e infinitas soluções.
    ============================================================
    """
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

        # Linha inconsistente:
        # 0 0 0 ... | b, com b != 0
        if not encontrou_pivo and abs(matriz_rref[i][-1]) > eps:
            return "SI", colunas_pivo, linhas_pivo

    posto = len(colunas_pivo)

    if posto == quantidade_variaveis:
        return "SPD", colunas_pivo, linhas_pivo

    return "SPI", colunas_pivo, linhas_pivo


def classificacao_extenso(sigla):
    """
    Traduz a sigla da classificação para texto completo.
    """
    mapa = {
        "SPD": "Sistema Possível e Determinado",
        "SPI": "Sistema Possível e Indeterminado",
        "SI": "Sistema Impossível",
    }
    return mapa.get(sigla, sigla)


def resolver_solucao(rref_matriz, classificacao, colunas_pivo, linhas_pivo, eps=EPSILON):
    """
    Monta a solução final do sistema.

    ============================================================
    CASOS MATEMÁTICOS
    ============================================================

    1) SPD:
       Cada variável pivô fica determinada por um valor único.
       Exemplo:
           x = 2
           y = -1
           z = 5

    2) SPI:
       Existem variáveis livres.
       As variáveis pivô são escritas em função dos parâmetros livres:
           x = 2 - t1
           y = t1
           z = 3 + 2*t1

    3) SI:
       Não existe solução.
    ============================================================
    """
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
            "texto": "Sistema Possível e Determinado (SPD)\n" + "\n".join(partes),
        }

    # SPI: criar parâmetros livres t1, t2, ...
    parametros = {}
    for idx, col in enumerate(livres, start=1):
        parametros[col] = f"t{idx}"

    expressoes = {}

    # Variáveis livres
    for col in livres:
        nome = get_nome_variavel(col)
        expressoes[nome] = parametros[col]

    # Variáveis pivô escritas em função das livres
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
        "texto": (
            "Sistema Possível e Indeterminado (SPI)\n"
            + "\n".join(texto_final)
            + f"\n\nOnde {', '.join(parametros.values())} são parâmetros livres."
        ),
    }


def adicionar_log(logs, titulo, matriz):
    """
    Adiciona uma etapa ao log do processo.
    """
    logs.append(
        {
            "titulo": titulo,
            "matriz": matriz_para_texto(matriz),
        }
    )


def gauss_jordan_com_pivotamento(matriz_original, eps=EPSILON):
    """
    Executa o método de Gauss-Jordan com pivoteamento parcial.

    ============================================================
    IDEIA MATEMÁTICA
    ============================================================

    Queremos transformar a matriz ampliada [A|b] em forma escalonada
    reduzida (RREF - Reduced Row Echelon Form).

    Exemplo de forma reduzida:
        1  0  0 | a
        0  1  0 | b
        0  0  1 | c

    Isso equivale a:
        x = a
        y = b
        z = c

    PASSOS DO ALGORITMO:
    1. Escolher pivô em uma coluna
    2. Se necessário, trocar linhas (pivoteamento parcial)
    3. Normalizar a linha do pivô para que o pivô vire 1
    4. Eliminar os demais elementos da coluna
    5. Repetir para as próximas colunas

    O pivoteamento parcial melhora a estabilidade numérica,
    escolhendo o maior valor absoluto da coluna como pivô.
    ============================================================
    """
    matriz = copiar_matriz(matriz_original)
    linhas = len(matriz)
    colunas = len(matriz[0])
    quantidade_variaveis = colunas - 1

    logs = []

    adicionar_log(
        logs,
        "=== INÍCIO DO ESCALONAMENTO GAUSS-JORDAN COM PIVOTEAMENTO PARCIAL ===\nMatriz inicial [A|b]",
        matriz,
    )

    linha_atual = 0
    coluna_pivo = 0

    while linha_atual < linhas and coluna_pivo < quantidade_variaveis:
        # ========================================================
        # 1) ESCOLHA DO PIVÔ
        # Procuramos, na coluna atual, a linha com maior valor
        # absoluto a partir da linha_atual.
        #
        # Isso implementa o pivoteamento parcial.
        # ========================================================
        melhor_linha = linha_atual
        valor_max = abs(matriz[linha_atual][coluna_pivo])

        for i in range(linha_atual + 1, linhas):
            if abs(matriz[i][coluna_pivo]) > valor_max:
                valor_max = abs(matriz[i][coluna_pivo])
                melhor_linha = i

        # Se a coluna inteira é nula abaixo da linha atual,
        # então não há pivô nessa coluna.
        if valor_max < eps:
            adicionar_log(
                logs,
                f"Coluna {coluna_pivo + 1}: pivô nulo ou próximo de zero.\nA coluna foi ignorada e seguimos para a próxima.",
                matriz,
            )
            coluna_pivo += 1
            continue

        # ========================================================
        # 2) TROCA DE LINHAS
        # Se a melhor linha não for a linha atual, trocamos.
        # ========================================================
        if melhor_linha != linha_atual:
            matriz[linha_atual], matriz[melhor_linha] = matriz[melhor_linha], matriz[linha_atual]
            adicionar_log(
                logs,
                (
                    f"Troca de linhas (pivoteamento parcial): "
                    f"L{linha_atual + 1} ↔ L{melhor_linha + 1}\n"
                    f"Escolhemos o maior pivô em módulo na coluna {coluna_pivo + 1}."
                ),
                matriz,
            )

        # ========================================================
        # 3) NORMALIZAÇÃO DO PIVÔ
        # Tornamos o pivô igual a 1 dividindo a linha inteira
        # pelo valor do pivô.
        # ========================================================
        pivo = matriz[linha_atual][coluna_pivo]

        if abs(pivo) < eps:
            coluna_pivo += 1
            continue

        for j in range(colunas):
            matriz[linha_atual][j] /= pivo

        adicionar_log(
            logs,
            (
                f"Normalização da linha pivô:\n"
                f"L{linha_atual + 1} = L{linha_atual + 1} / {formatar_numero(pivo)}\n"
                f"Agora o pivô da coluna {coluna_pivo + 1} vale 1."
            ),
            matriz,
        )

        # ========================================================
        # 4) ELIMINAÇÃO
        # Zeramos todos os outros elementos da coluna pivô.
        #
        # Se o pivô está na linha r, então para cada outra linha i:
        #   Li = Li - (fator) * Lr
        #
        # Isso produz uma coluna com:
        #   0
        #   0
        #   1
        #   0
        #   0
        # ========================================================
        houve_eliminacao = False

        for i in range(linhas):
            if i == linha_atual:
                continue

            fator = matriz[i][coluna_pivo]
            if abs(fator) < eps:
                continue

            for j in range(colunas):
                matriz[i][j] -= fator * matriz[linha_atual][j]

            houve_eliminacao = True
            adicionar_log(
                logs,
                (
                    f"Eliminação na coluna {coluna_pivo + 1}:\n"
                    f"L{i + 1} = L{i + 1} - ({formatar_numero(fator)}) * L{linha_atual + 1}"
                ),
                matriz,
            )

        if not houve_eliminacao:
            adicionar_log(
                logs,
                f"Nenhuma eliminação adicional foi necessária na coluna {coluna_pivo + 1}.",
                matriz,
            )

        linha_atual += 1
        coluna_pivo += 1

    # Limpeza de resíduos numéricos muito pequenos
    for i in range(linhas):
        for j in range(colunas):
            if abs(matriz[i][j]) < eps:
                matriz[i][j] = 0.0

    adicionar_log(
        logs,
        "=== ESCALONAMENTO CONCLUÍDO ===\nForma escalonada reduzida final (RREF)",
        matriz,
    )

    classificacao, colunas_pivo, linhas_pivo = classificar_sistema(matriz, eps=eps)
    solucao = resolver_solucao(matriz, classificacao, colunas_pivo, linhas_pivo, eps=eps)

    return {
        "matriz_final": matriz,
        "classificacao": classificacao,
        "classificacao_extenso": classificacao_extenso(classificacao),
        "solucao": solucao,
        "logs": logs,
    }