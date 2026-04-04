const qtdLinhasInput = document.getElementById("qtdLinhas");
const qtdColunasInput = document.getElementById("qtdColunas");
const totalColunasExibidas = document.getElementById("totalColunasExibidas");

const matrizGrid = document.getElementById("matrizGrid");
const textoMatriz = document.getElementById("textoMatriz");
const arquivoMatriz = document.getElementById("arquivoMatriz");
const fileName = document.getElementById("fileName");

const summaryDimensao = document.getElementById("summaryDimensao");
const summaryColunas = document.getElementById("summaryColunas");
const summaryArquivo = document.getElementById("summaryArquivo");

const resultadoClassificacao = document.getElementById("resultadoClassificacao");
const resultadoSolucao = document.getElementById("resultadoSolucao");
const resultadoLogs = document.getElementById("resultadoLogs");

const btnGerar = document.getElementById("btnGerar");
const btnPreencherExemplo = document.getElementById("btnPreencherExemplo");
const btnLimparTudo = document.getElementById("btnLimparTudo");
const btnResolver = document.getElementById("btnResolver");
const btnExportarTexto = document.getElementById("btnExportarTexto");

function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === `${name}=`) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

function showToast(title, text, type = "success") {
    const root = document.getElementById("toastRoot");
    const toast = document.createElement("div");
    toast.className = `toast toast--${type}`;

    toast.innerHTML = `
        <div class="toast-content">
            <div class="toast-title">${escapeHtml(title)}</div>
            <div class="toast-text">${escapeHtml(text)}</div>
        </div>
        <button class="toast-close" type="button" aria-label="Fechar">×</button>
    `;

    const closeBtn = toast.querySelector(".toast-close");
    closeBtn.addEventListener("click", () => {
        toast.remove();
    });

    root.appendChild(toast);

    requestAnimationFrame(() => {
        toast.classList.add("toast--visible");
    });

    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 3200);
}

function normalizarQuantidade(valor, padrao = 3) {
    const numero = parseInt(valor, 10);

    if (Number.isNaN(numero)) return padrao;
    if (numero < 1) return 1;
    if (numero > 10) return 10;

    return numero;
}

function obterDimensoes() {
    const linhas = normalizarQuantidade(qtdLinhasInput.value, 3);
    const colunas = normalizarQuantidade(qtdColunasInput.value, 2);

    qtdLinhasInput.value = linhas;
    qtdColunasInput.value = colunas;

    return {
        linhas,
        colunas,
        colunasTotais: colunas + 1,
    };
}

function atualizarResumo(linhas, colunas) {
    const colunasTotais = colunas + 1;

    if (summaryDimensao) {
        summaryDimensao.textContent = `${linhas} x ${colunas}`;
    }

    if (summaryColunas) {
        summaryColunas.textContent = String(colunasTotais);
    }

    if (totalColunasExibidas) {
        totalColunasExibidas.value = String(colunasTotais);
    }
}

function gerarMatriz() {
    const { linhas, colunas, colunasTotais } = obterDimensoes();

    matrizGrid.innerHTML = "";
    matrizGrid.style.gridTemplateColumns = `repeat(${colunasTotais}, 68px)`;

    for (let i = 0; i < linhas; i++) {
        for (let j = 0; j < colunasTotais; j++) {
            const input = document.createElement("input");
            input.type = "number";
            input.step = "any";
            input.placeholder = "0";
            input.className = "matrix-cell";
            input.dataset.row = i;
            input.dataset.col = j;

            if (j === colunas) {
                input.classList.add("col-b");
            }

            matrizGrid.appendChild(input);
        }
    }

    atualizarResumo(linhas, colunas);
}

function preencherMatrizPorTexto(texto) {
    const linhasTexto = texto
        .trim()
        .split(/\n+/)
        .map((linha) => linha.trim())
        .filter(Boolean);

    if (!linhasTexto.length) {
        showToast("Entrada vazia", "Não foi encontrado conteúdo para preencher.", "error");
        return;
    }

    const matriz = linhasTexto.map((linha) =>
        linha.replace(/;/g, " ").split(/\s+/).filter(Boolean)
    );

    const quantidadeLinhas = matriz.length;
    const quantidadeColunasTotais = matriz[0].length;

    const formatoValido = matriz.every(
        (linha) => linha.length === quantidadeColunasTotais
    );

    if (!formatoValido || quantidadeColunasTotais < 2) {
        showToast(
            "Formato inválido",
            "Todas as linhas precisam ter a mesma quantidade de valores.",
            "error"
        );
        return;
    }

    const quantidadeIncognitas = quantidadeColunasTotais - 1;

    qtdLinhasInput.value = quantidadeLinhas;
    qtdColunasInput.value = quantidadeIncognitas;

    gerarMatriz();

    const inputs = matrizGrid.querySelectorAll(".matrix-cell");

    matriz.forEach((linha, i) => {
        linha.forEach((valor, j) => {
            const index = i * quantidadeColunasTotais + j;
            if (inputs[index]) {
                inputs[index].value = valor;
            }
        });
    });

    atualizarResumo(quantidadeLinhas, quantidadeIncognitas);
    showToast("Matriz carregada", "Os campos foram preenchidos com sucesso.", "success");
}

function carregarArquivo(file) {
    if (!file) return;

    fileName.textContent = file.name;
    if (summaryArquivo) {
        summaryArquivo.textContent = file.name;
    }

    const reader = new FileReader();

    reader.onload = function (event) {
        const conteudo = String(event.target.result || "");
        textoMatriz.value = conteudo.trim();
        preencherMatrizPorTexto(conteudo);
    };

    reader.onerror = function () {
        showToast("Erro ao ler arquivo", "Não foi possível ler o arquivo enviado.", "error");
    };

    reader.readAsText(file);
}

function limparTudo() {
    qtdLinhasInput.value = 3;
    qtdColunasInput.value = 2;
    textoMatriz.value = "";
    arquivoMatriz.value = "";
    fileName.textContent = "Nenhum arquivo selecionado";

    if (summaryArquivo) {
        summaryArquivo.textContent = "Nenhum";
    }

    resultadoClassificacao.textContent = "Aguardando execução.";
    resultadoSolucao.textContent = "Nenhuma solução calculada ainda.";
    resultadoLogs.textContent = "Nenhum passo calculado ainda.";

    gerarMatriz();

    const inputs = matrizGrid.querySelectorAll(".matrix-cell");
    inputs.forEach((input) => {
        input.value = "";
    });

    showToast("Tela limpa", "Os campos foram redefinidos.", "success");
}

function coletarMatrizComoTexto() {
    const { linhas, colunasTotais } = obterDimensoes();
    const inputs = [...matrizGrid.querySelectorAll(".matrix-cell")];
    const linhasTexto = [];

    for (let i = 0; i < linhas; i++) {
        const linha = [];

        for (let j = 0; j < colunasTotais; j++) {
            const index = i * colunasTotais + j;
            const valor = inputs[index]?.value?.trim() || "0";
            linha.push(valor);
        }

        linhasTexto.push(linha.join(" "));
    }

    return linhasTexto.join("\n");
}

function renderizarResultado(dados) {
    resultadoClassificacao.textContent = `${dados.classificacao_extenso} (${dados.classificacao})`;
    resultadoSolucao.textContent = dados.solucao?.texto || "Sem conteúdo.";

    const logs = dados.logs || [];

    if (!logs.length) {
        resultadoLogs.textContent = "Nenhum passo calculado.";
        return;
    }

    resultadoLogs.innerHTML = logs
        .map((item) => {
            return `
                <div class="log-item">
                    <strong>${escapeHtml(item.titulo)}</strong>
                    <pre>${escapeHtml(item.matriz)}</pre>
                </div>
            `;
        })
        .join("");
}

arquivoMatriz.addEventListener("change", function () {
    const file = this.files && this.files[0] ? this.files[0] : null;

    if (!file) {
        fileName.textContent = "Nenhum arquivo selecionado";
        if (summaryArquivo) {
            summaryArquivo.textContent = "Nenhum";
        }
        return;
    }

    carregarArquivo(file);
});

btnGerar.addEventListener("click", () => {
    gerarMatriz();
    showToast("Matriz gerada", "Os campos foram montados conforme as dimensões informadas.", "success");
});

btnPreencherExemplo.addEventListener("click", () => {
    const exemplo = `1 1 2
2 -1 1
3 1 5`;

    textoMatriz.value = exemplo;
    preencherMatrizPorTexto(exemplo);
});

btnLimparTudo.addEventListener("click", limparTudo);

btnResolver.addEventListener("click", async () => {
    const texto = coletarMatrizComoTexto();
    const csrftoken = getCookie("csrftoken");

    try {
        const response = await fetch(window.SOLVER_CONFIG.resolverUrl, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrftoken,
            },
            body: JSON.stringify({
                matriz: texto,
            }),
        });

        const dados = await response.json();

        if (!response.ok || !dados.ok) {
            throw new Error(dados.erro || "Erro ao resolver o sistema.");
        }

        renderizarResultado(dados);
        showToast("Sucesso", "Sistema resolvido com sucesso.", "success");
    } catch (error) {
        resultadoClassificacao.textContent = "Erro";
        resultadoSolucao.textContent = error.message;
        resultadoLogs.textContent = "Não foi possível gerar os passos.";
        showToast("Erro", error.message, "error");
    }
});

btnExportarTexto.addEventListener("click", async () => {
    const texto = coletarMatrizComoTexto();

    try {
        await navigator.clipboard.writeText(texto);
        showToast("Copiado", "A matriz foi copiada para a área de transferência.", "success");
    } catch (error) {
        console.log(texto);
        showToast("Texto gerado", "Abra o console para ver a matriz exportada.", "success");
    }
});

gerarMatriz();