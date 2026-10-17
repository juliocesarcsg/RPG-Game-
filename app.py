"""Arena de Combate em janela própria (pywebview).

    python app.py               abre a janela do jogo (F11 liga e desliga a tela cheia)
    python app.py --navegador   abre a mesma interface no navegador, em http://localhost:8765/?navegador
                                (útil para testar a interface sem a janela)

Para gerar o executável (ArenaDeCombate.exe), rode gerar_exe.bat.
O jogo no terminal continua disponível: python main.py
"""

import json
import os
import sys
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from partida import Partida

PORTA_NAVEGADOR = 8765


def recurso(*partes):
    """Caminho de um arquivo do jogo, tanto rodando o .py quanto dentro do .exe do PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *partes)


PASTA_INTERFACE = recurso("interface")


class Api:
    """O que a interface (interface/jogo.js) pode chamar. Atributos com _ não são expostos ao JavaScript."""

    def __init__(self):
        self._partida = Partida()
        self._janela = None
        self._trava = threading.Lock()  # um clique de cada vez
        self._tela_cheia = False

    def estado(self):
        with self._trava:
            return self._partida.estado()

    def agir(self, acao, dados=None):
        with self._trava:
            return self._partida.agir(acao, dados)

    def tela_cheia(self, ligar=None):
        """Liga/desliga a tela cheia da janela. Devolve se ficou em tela cheia."""
        if self._janela is not None and (ligar is None or bool(ligar) != self._tela_cheia):
            self._janela.toggle_fullscreen()
            self._tela_cheia = not self._tela_cheia
        return self._tela_cheia

    def sair(self):
        if self._janela is not None:
            self._janela.destroy()


def modo_navegador(porta=PORTA_NAVEGADOR):
    """Serve a interface e a Api por HTTP local (só para desenvolvimento e testes)."""
    api = Api()

    class Pedido(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=PASTA_INTERFACE, **kwargs)

        def do_POST(self):
            metodo = self.path.strip("/").split("/")[-1]
            if metodo not in ("estado", "agir"):
                self.send_error(404)
                return
            tamanho = int(self.headers.get("Content-Length", 0))
            argumentos = json.loads(self.rfile.read(tamanho) or b"[]")
            corpo = json.dumps(getattr(api, metodo)(*argumentos)).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.end_headers()
            self.wfile.write(corpo)

        def end_headers(self):
            self.send_header("Cache-Control", "no-store")
            super().end_headers()

        def log_message(self, *args):
            pass

    servidor = ThreadingHTTPServer(("127.0.0.1", porta), Pedido)
    print(f"Arena de Combate no navegador: http://localhost:{porta}/?navegador  (Ctrl+C para sair)")
    servidor.serve_forever()


def abrir_janela():
    import webview

    api = Api()
    janela = webview.create_window(
        "Arena de Combate",
        url=os.path.join(PASTA_INTERFACE, "index.html"),
        js_api=api,
        width=1366,
        height=860,
        min_size=(900, 620),
        maximized=True,
        background_color="#6b4a00",
        text_select=False,
    )
    api._janela = janela
    webview.start(http_server=True)


if __name__ == "__main__":
    if "--navegador" in sys.argv:
        modo_navegador()
    else:
        abrir_janela()
