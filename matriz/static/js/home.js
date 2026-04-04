const ordemInput = document.getElementById("ordem");
const matrizGrid = document.getElementById("matrizGrid");
const textoMatriz = document.getElementById("textoMatriz");
const arquivoMatriz = document.getElementById("arquivoMatriz");
const fileName = document.getElementById("fileName");

const summaryOrdem = document.getElementById("summaryOrdem");
const summaryColunas = document.getElementById("summaryColunas");
const summaryArquivo = document.getElementById("summaryArquivo");

const previewOrdem = document.getElementById("previewOrdem");
const previewCampos = document.getElementById("previewCampos");
const previewArquivo = document.getElementById("previewArquivo");
const previewManual = document.getElementById("previewManual");

const resultadoClassificacao = document.getElementById("resultadoClassificacao");
const resultadoSolucao = document.getElementById("resultadoSolucao");
const resultadoLogs = document.getElementById("resultadoLogs");

const btnGerar = document.getElementById("btnGerar");
const btnGerarTopo = document.getElementById("btnGerarTopo");
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

function normalizarOrdem(valor) {
    const numero = parseInt(valor, 10);

    if (Number.isNaN(numero)) return 3;
    if (numero < 2) return 2;
    if (numero > 10) return 10;

    return numero;
}

function atualizarResumo(ordem) {
    summaryOrdem.textContent = `${ordem} x ${ordem}`;
    summaryColunas.textContent = `${ordem + 1}`;
    previewOrdem.textContent = `${ordem} x ${ordem}`;
    previewCampos.textContent = `${ordem * (ordem + 1)}`;
    previewManual.textContent = textoMatriz.value.trim() ? "Preenchida" : "Vazia";
}

function gerarMatriz() {
    const ordem = normalizarOrdem(ordemInput.value);
    ordemInput.value = ordem;
    matrizGrid.innerHTML = "";
    matrizGrid.style.gridTemplateColumns = `repeat(${ordem + 1}, 68px)`;

    for (let i = 0; i < ordem; i++) {
        for (let j = 0; j < ordem + 1; j++) {
            const input = document.createElement("input");
            input.type = "number";
            input.step = "any";
            input.placeholder = "0";
            input.className = "matrix-cell";
            input.dataset.row = i;
            input.dataset.col = j;

            if (j === ordem) {
                input.classList.add("col-b");
            }

            matrizGrid.appendChild(input);
        }
    }

    atualizarResumo(ordem);
}

function preencherMatrizPorTexto(texto) {
    const linhas = texto
        .trim()
        .split(/\n+/)
        .map((linha) => linha.trim())
        .filter(Boolean);

    if (!linhas.length) {
        showToast("Entrada vazia", "Não foi encontrado conteúdo para preencher.", "error");
        return;
    }

    const matriz = linhas.map((linha) =>
        linha.replace(/;/g, " ").split(/\s+/).filter(Boolean)
    );

    const tamanho = matriz.length;
    const colunasEsperadas = tamanho + 1;
    const formatoValido = matriz.every((linha) => linha.length === colunasEsperadas);

    if (!formatoValido) {
        showToast("Formato inválido", "O texto deve ter n linhas e n+1 colunas em cada linha.", "error");
        return;
    }

    ordemInput.value = tamanho;
    gerarMatriz();

    const inputs = matrizGrid.querySelectorAll(".matrix-cell");

    matriz.forEach((linha, i) => {
        linha.forEach((valor, j) => {
            const index = i * (tamanho + 1) + j;
            if (inputs[index]) {
                inputs[index].value = valor;
            }
        });
    });

    atualizarResumo(tamanho);
    showToast("Matriz carregada", "Os campos foram preenchidos com sucesso.", "success");
}

function carregarArquivo(file) {
    if (!file) return;

    fileName.textContent = file.name;
    summaryArquivo.textContent = file.name;
    previewArquivo.textContent = file.name;

    const reader = new FileReader();

    reader.onload = function (event) {
        const conteudo = String(event.target.result || "");
        textoMatriz.value = conteudo.trim();
        previewManual.textContent = textoMatriz.value.trim() ? "Preenchida" : "Vazia";
        preencherMatrizPorTexto(conteudo);
    };

    reader.onerror = function () {
        showToast("Erro ao ler arquivo", "Não foi possível ler o arquivo enviado.", "error");
    };

    reader.readAsText(file);
}

function limparTudo() {
    ordemInput.value = 3;
    textoMatriz.value = "";
    arquivoMatriz.value = "";
    fileName.textContent = "Nenhum arquivo selecionado";
    summaryArquivo.textContent = "Nenhum";
    previewArquivo.textContent = "Nenhum arquivo anexado";
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
    const ordem = normalizarOrdem(ordemInput.value);
    const inputs = [...matrizGrid.querySelectorAll(".matrix-cell")];
    const linhas = [];

    for (let i = 0; i < ordem; i++) {
        const linha = [];

        for (let j = 0; j < ordem + 1; j++) {
            const index = i * (ordem + 1) + j;
            const valor = inputs[index]?.value?.trim() || "0";
            linha.push(valor);
        }

        linhas.push(linha.join(" "));
    }

    return linhas.join("\n");
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
        summaryArquivo.textContent = "Nenhum";
        previewArquivo.textContent = "Nenhum arquivo anexado";
        return;
    }

    carregarArquivo(file);
});

textoMatriz.addEventListener("input", function () {
    previewManual.textContent = this.value.trim() ? "Preenchida" : "Vazia";
});

btnGerar.addEventListener("click", () => {
    if (textoMatriz.value.trim()) {
        preencherMatrizPorTexto(textoMatriz.value);
        return;
    }

    gerarMatriz();
    showToast("Matriz gerada", "Os campos foram montados pela ordem escolhida.", "success");
});

btnGerarTopo.addEventListener("click", () => {
    if (textoMatriz.value.trim()) {
        preencherMatrizPorTexto(textoMatriz.value);
        return;
    }

    gerarMatriz();
    showToast("Matriz gerada", "Os campos foram montados pela ordem escolhida.", "success");
});

btnPreencherExemplo.addEventListener("click", () => {
    const exemplo = `2 1 -1 8
-3 -1 2 -11
-2 1 2 -3`;

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