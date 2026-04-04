import sys
import os
from typing import List, Tuple

# =====================================================
# CONSTANTES
# =====================================================
EPSILON = 1e-10

# Variáveis simbólicas conforme pedido pelo professor
VARIAVEIS = ['x', 'y', 'z', 'w', 'k', 'm']


def get_nome_variavel(indice: int) -> str:
    if indice < len(VARIAVEIS):
        return VARIAVEIS[indice]
    else:
        return f"x{indice + 1}"


def format_int(val: float) -> str:
    """Formata o número como inteiro se for praticamente inteiro, senão com 4 casas."""
    if abs(val - round(val)) < 1e-8:
        return str(int(round(val)))
    else:
        return f"{val:.4f}"


# =====================================================
# FUNÇÕES DE ENTRADA
# =====================================================

def ler_matriz_arquivo(nome_arquivo: str) -> List[List[float]]:
    if not os.path.exists(nome_arquivo):
        raise FileNotFoundError(f"Arquivo '{nome_arquivo}' não encontrado.")
    
    matriz = []
    with open(nome_arquivo, 'r', encoding='utf-8') as f:
        for linha in f:
            linha = linha.strip()
            if not linha:
                continue
            try:
                valores = [float(x) for x in linha.split()]
                matriz.append(valores)
            except ValueError:
                raise ValueError(f"Erro na linha: '{linha}'. Todos os valores devem ser números.")
    
    if not matriz:
        raise ValueError("Arquivo vazio.")
    
    cols = len(matriz[0])
    for row in matriz:
        if len(row) != cols:
            raise ValueError("Todas as linhas devem ter o mesmo número de colunas.")
    
    return matriz


def ler_matriz_manual() -> List[List[float]]:
    print("\n=== ENTRADA MANUAL DA MATRIZ AMPLIADA [A|b] ===")
    try:
        n_vars = int(input("Número de variáveis (n): "))
        n_eqs = int(input("Número de equações (m): "))
        
        if n_vars < 1 or n_eqs < 1:
            raise ValueError("n e m devem ser maiores que zero.")
        
        matriz = []
        print(f"\nDigite os coeficientes para as {n_eqs} equações:")
        for i in range(n_eqs):
            print(f"Equação {i+1}:")
            linha = []
            for j in range(n_vars):
                coef = float(input(f"   a{i+1}{j+1} = "))
                linha.append(coef)
            b = float(input(f"   b{i+1}   = "))
            linha.append(b)
            matriz.append(linha)
        return matriz
    except ValueError as e:
        print(f"Erro de entrada: {e}")
        sys.exit(1)


# =====================================================
# VISUALIZAÇÃO
# =====================================================

def imprimir_matriz(matriz: List[List[float]], titulo: str = "Matriz Atual") -> None:
    print(f"\n{titulo}:")
    for row in matriz:
        linha_a = "  ".join(f"{val:8.2f}" for val in row[:-1])   # 2 casas na matriz para ficar mais limpo
        print(f"  {linha_a}  |  {row[-1]:8.2f}")
    print("-" * 85)


def copiar_matriz(matriz: List[List[float]]) -> List[List[float]]:
    return [row[:] for row in matriz]


# =====================================================
# ESCALONAMENTO GAUSS-JORDAN COM LOGS EM INTEIROS
# =====================================================

def escalonamento_gauss_jordan(matriz_original: List[List[float]]) -> Tuple[List[List[float]], List[str]]:
    matriz = copiar_matriz(matriz_original)
    m = len(matriz)
    n = len(matriz[0]) - 1
    
    logs: List[str] = ["=== INÍCIO DO ESCALONAMENTO GAUSS-JORDAN COM PIVOTEAMENTO PARCIAL ==="]
    imprimir_matriz(matriz, "MATRIZ INICIAL [A|b]")
    logs.append("Matriz inicial carregada.")
    
    linha_atual = 0
    coluna_pivot = 0
    
    while linha_atual < m and coluna_pivot < n:
        # Pivoteamento parcial
        linha_pivot = linha_atual
        valor_max = abs(matriz[linha_atual][coluna_pivot])
        
        for i in range(linha_atual + 1, m):
            if abs(matriz[i][coluna_pivot]) > valor_max:
                valor_max = abs(matriz[i][coluna_pivot])
                linha_pivot = i
        
        if valor_max < EPSILON:
            logs.append(f"Coluna {coluna_pivot + 1}: pivô ≈ 0 → coluna ignorada.")
            coluna_pivot += 1
            continue
        
        # Troca de linhas
        if linha_pivot != linha_atual:
            matriz[linha_atual], matriz[linha_pivot] = matriz[linha_pivot], matriz[linha_atual]
            logs.append(f"L{linha_atual + 1} ↔ L{linha_pivot + 1}   (pivoteamento parcial - maior pivô na coluna {coluna_pivot + 1})")
            imprimir_matriz(matriz, f"Após troca: L{linha_atual + 1} ↔ L{linha_pivot + 1}")
        
        # Normalização do pivô
        pivô = matriz[linha_atual][coluna_pivot]
        if abs(pivô) < EPSILON:
            coluna_pivot += 1
            continue
            
        for j in range(n + 1):
            matriz[linha_atual][j] /= pivô
        
        logs.append(f"L{linha_atual + 1} = L{linha_atual + 1} / {format_int(pivô)}   → pivô agora = 1")
        imprimir_matriz(matriz, f"Após normalização da L{linha_atual + 1}")
        
        # Eliminação nas outras linhas
        for i in range(m):
            if i == linha_atual:
                continue
            fator = matriz[i][coluna_pivot]
            if abs(fator) < EPSILON:
                continue
                
            for j in range(n + 1):
                matriz[i][j] -= fator * matriz[linha_atual][j]
            
            logs.append(f"L{i + 1} = L{i + 1} - L{linha_atual + 1} * {format_int(fator)}")
        
        imprimir_matriz(matriz, f"Após eliminação da coluna {coluna_pivot + 1}")
        
        linha_atual += 1
        coluna_pivot += 1
    
    logs.append("=== ESCALONAMENTO CONCLUÍDO → Matriz em Forma Escalonada Reduzida (RREF) ===")
    imprimir_matriz(matriz, "MATRIZ FINAL EM RREF")
    
    return matriz, logs


# =====================================================
# CLASSIFICAÇÃO E SOLUÇÃO
# =====================================================

def classificar_sistema(rref_matriz: List[List[float]]) -> Tuple[str, List[int], dict]:
    m = len(rref_matriz)
    n = len(rref_matriz[0]) - 1
    
    colunas_pivot: List[int] = []
    linhas_pivot: dict = {}
    
    for i in range(m):
        for j in range(n):
            if abs(rref_matriz[i][j]) > EPSILON:
                colunas_pivot.append(j)
                linhas_pivot[j] = i
                break
        else:
            if abs(rref_matriz[i][-1]) > EPSILON:
                return "SI", [], {}
    
    rank = len(colunas_pivot)
    if rank == n:
        return "SPD", colunas_pivot, linhas_pivot
    else:
        return "SPI", colunas_pivot, linhas_pivot


def resolver_sistema(rref_matriz: List[List[float]], classificacao: str,
                     colunas_pivot: List[int], linhas_pivot: dict) -> str:
    n = len(rref_matriz[0]) - 1
    
    if classificacao == "SI":
        return "Sistema Impossível (SI)\nNão possui solução."
    
    livres = [j for j in range(n) if j not in linhas_pivot]
    
    if classificacao == "SPD":
        solucao = []
        for col in range(n):
            linha = linhas_pivot[col]
            valor = rref_matriz[linha][-1]
            var_nome = get_nome_variavel(col)
            solucao.append(f"{var_nome} = {format_int(valor)}")
        return ("Sistema Possível e Determinado (SPD)\n"
                "Solução única:\n" + "\n".join(solucao))
    
    else:  # SPI
        num_livres = len(livres)
        parametros = [f"t{k+1}" for k in range(num_livres)]
        dict_livres = {livres[k]: parametros[k] for k in range(num_livres)}
        
        expressoes = []
        for var in range(n):
            var_nome = get_nome_variavel(var)
            if var in linhas_pivot:
                linha = linhas_pivot[var]
                expr = f"{format_int(rref_matriz[linha][-1])}"
                for livre_col in livres:
                    coef = rref_matriz[linha][livre_col]
                    if abs(coef) > EPSILON:
                        sinal = "-" if coef > 0 else "+"
                        expr += f" {sinal} {format_int(abs(coef))}*{dict_livres[livre_col]}"
                expressoes.append(f"{var_nome} = {expr}")
            else:
                idx = livres.index(var)
                expressoes.append(f"{var_nome} = {parametros[idx]}")
        
        return ("Sistema Possível e Indeterminado (SPI)\n"
                "Solução geral:\n" + "\n".join(expressoes) + 
                f"\n\nOnde {' , '.join(parametros)} são parâmetros livres.")

def main():
    print("=" * 95)
    print("MATRIZES - ESCALONAMENTO GAUSS-JORDAN")
    print("Variáveis: x, y, z, w, k, m")
    print("=" * 95)
    
    print("\nEscolha a forma de entrada:")
    print("1 - Ler de arquivo .txt")
    print("2 - Entrada manual pelo teclado")
    opcao = input("Opção (1 ou 2): ").strip()
    
    if opcao == "1":
        nome_arq = input("Nome do arquivo .txt: ").strip()
        try:
            matriz_inicial = ler_matriz_arquivo(nome_arq)
        except Exception as e:
            print(f"ERRO: {e}")
            return
    else:
        matriz_inicial = ler_matriz_manual()
    
    print("\n" + "=" * 95)
    print("INICIANDO PROCESSAMENTO ALGORÍTMICO...")
    print("=" * 95)
    
    rref_final, logs = escalonamento_gauss_jordan(matriz_inicial)
    
    print("\n" + "=" * 95)
    print("LOG DETALHADO DE OPERAÇÕES ELEMENTARES")
    print("=" * 95)
    for log in logs:
        print(f"• {log}")
    
    classificacao, colunas_pivot, linhas_pivot = classificar_sistema(rref_final)
    
    print("\n" + "=" * 95)
    print("CLASSIFICAÇÃO DO SISTEMA")
    print("=" * 95)
    print(f"→ {classificacao}")
    
    solucao_texto = resolver_sistema(rref_final, classificacao, colunas_pivot, linhas_pivot)
    
    print("\n" + "=" * 95)
    print("SOLUÇÃO FINAL")
    print("=" * 95)
    print(solucao_texto)
    
    print("\n" + "=" * 95)
    print("PROGRAMA CONCLUÍDO COM SUCESSO!")


if __name__ == "__main__":
    main()