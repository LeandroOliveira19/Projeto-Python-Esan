import csv
import os

class GestorFicheiros:
    def __init__(self, pasta="dados"):
        # 1. Descobre onde este ficheiro (gerifich.py) está: .../projeto/codigo
        diretorio_atual = os.path.dirname(os.path.abspath(__file__))
        
        # 2. Anda um nível para trás para chegar à raiz do projeto: .../projeto
        diretorio_projeto = os.path.dirname(diretorio_atual)
        
        # 3. Define o caminho para a pasta dados: .../projeto/dados
        self.pasta = os.path.join(diretorio_projeto, pasta)

        # Tenta criar a pasta se não existir (apenas por segurança)
        try:
            os.makedirs(self.pasta, exist_ok=True)
        except:
            pass

    def ler_csv(self, nome_ficheiro):
        caminho = os.path.join(self.pasta, nome_ficheiro)
        dados = []
        
        # Verificação de Debug: Se o ficheiro não existir, avisa no ecrã
        if not os.path.exists(caminho):
            print(f"[AVISO] Ficheiro não encontrado: {caminho}")
            return []

        try:
            with open(caminho, mode='r', encoding='utf-8') as f:
                leitor = csv.DictReader(f)
                for linha in leitor:
                    dados.append(linha)
            # print(f"[DEBUG] {nome_ficheiro}: {len(dados)} registos carregados.") # Opcional
        except Exception as e:
            print(f"Erro ao ler {nome_ficheiro}: {e}")
            
        return dados

    def guardar_csv(self, nome_ficheiro, campos, dados):
        # Garante que a pasta existe antes de guardar
        if not os.path.exists(self.pasta):
            try:
                os.makedirs(self.pasta, exist_ok=True)
            except Exception as e:
                print(f"ERRO CRÍTICO: Não consigo criar a pasta '{self.pasta}'.")
                return 
        
        caminho = os.path.join(self.pasta, nome_ficheiro)
        
        try:
            with open(caminho, mode='w', newline='', encoding='utf-8') as f:
                escritor = csv.DictWriter(f, fieldnames=campos)
                escritor.writeheader()
                escritor.writerows(dados)
        except Exception as e:
            print(f"Erro ao guardar {nome_ficheiro}: {e}")