# run.py (O Lançador)

import subprocess
import os
import sys
import webbrowser
import time

def get_path(filename):
    """ Obtém o caminho correto, seja rodando como script ou como .exe compilado """
    if hasattr(sys, "_MEIPASS"):
        # Estamos rodando como .exe (compilado)
        return os.path.join(sys._MEIPASS, filename)
    else:
        # Estamos rodando como script .py
        return os.path.abspath(filename)

def main():
    app_path = get_path("app.py")

    cmd = [
        "streamlit.cmd", "run", app_path,
        "--server.headless", "true",
        "--server.port", "8501"
    ]

    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    # Removido SW_HIDE para depuração inicial, se necessário volte a adicionar
    # si.wShowWindow = subprocess.SW_HIDE 

    print("Iniciando servidor Streamlit em segundo plano...")
    try:
         # Usando criação de flags para esconder a janela no Windows
         # Use 0x08000000 para CREATE_NO_WINDOW
         server_process = subprocess.Popen(cmd, startupinfo=si, creationflags=0x08000000)
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")
        input("Pressione Enter para sair...")
        return


    print("Aguardando o servidor iniciar...")
    time.sleep(7) # Aumentei um pouco o tempo

    print("Abrindo a aplicação no navegador...")
    webbrowser.open_new_tab("http://localhost:8501")

    try:
        print("Servidor rodando. Pressione Ctrl+C no terminal para parar.")
        server_process.wait()
    except KeyboardInterrupt:
        print("Fechando servidor...")
        server_process.terminate()
    except Exception as e:
         print(f"Erro durante a execução do servidor: {e}")
    finally:
         # Garante que o processo filho seja encerrado ao sair
         if server_process.poll() is None:
              server_process.terminate()
              server_process.wait()
         print("Servidor finalizado.")


if __name__ == "__main__":
    main()