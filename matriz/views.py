import json

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from .services.solver import interpretar_matriz_texto, gauss_jordan_com_pivotamento


@require_GET
def home(request):
    return render(request, "home.html")


@require_POST
def resolver_sistema(request):
    try:
        dados = json.loads(request.body.decode("utf-8"))
        texto_matriz = str(dados.get("matriz", "")).strip()

        if not texto_matriz:
            return JsonResponse(
                {
                    "ok": False,
                    "erro": "A matriz não foi informada.",
                },
                status=400,
            )

        matriz = interpretar_matriz_texto(texto_matriz)
        resultado = gauss_jordan_com_pivotamento(matriz)

        return JsonResponse(
            {
                "ok": True,
                "classificacao": resultado["classificacao"],
                "classificacao_extenso": resultado["classificacao_extenso"],
                "solucao": resultado["solucao"],
                "logs": resultado["logs"],
            }
        )

    except json.JSONDecodeError:
        return JsonResponse(
            {
                "ok": False,
                "erro": "JSON inválido.",
            },
            status=400,
        )

    except ValueError as e:
        return JsonResponse(
            {
                "ok": False,
                "erro": str(e),
            },
            status=400,
        )

    except Exception as e:
        return JsonResponse(
            {
                "ok": False,
                "erro": f"Erro interno: {str(e)}",
            },
            status=500,
        )