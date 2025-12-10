import os
import time
from gerifich import GestorFicheiros
from classes import *
from grafo import GrafoZoo

class SistemaZoo:
    def __init__(self):
        self.gestor_db = GestorFicheiros()
        self.areas = []
        self.habitats = []
        self.animais = []
        self.tratadores = []
        self.exposicoes = []
        self.lojas = []
        self.grafo = GrafoZoo()
        self.receita_bilhetes = 0.0
        self.carregar_dados()

    # --- 1. PERSISTÊNCIA DE DADOS ---
    def carregar_dados(self):
        # Carregar Areas
        for l in self.gestor_db.ler_csv("areas.csv"):
            self.areas.append(Area(l["CodigoArea"], l["Nome"], l["Descricao"]))
        
        # Carregar Habitats
        for l in self.gestor_db.ler_csv("habitats.csv"):
            self.habitats.append(Habitat(l["CodigoHabitat"], l["Nome"], l["Tipo"], l["CodigoArea"]))
        
        # Carregar Tratadores
        for l in self.gestor_db.ler_csv("tratadores.csv"):
            self.tratadores.append(Tratador(l["CodigoTratador"], l["Nome"], l["Especialidade"]))

        # Carregar Animais
        for l in self.gestor_db.ler_csv("animais.csv"):
            a = Animal(l["CodigoAnimal"], l["NomeComum"], l.get("NomeCientifico", ""), l["Especie"], l["Idade"], l["CodigoHabitat"], l.get("CodigoTratador", ""))
            self.animais.append(a)

        # Carregar Exposições
        for l in self.gestor_db.ler_csv("exposicoes.csv"):
            self.exposicoes.append(Exposicao(l["CodigoExposicao"], l["Nome"], l["Tema"], l["Horario"], l["LocalID"]))
            
        # Carregar Lojas
        for l in self.gestor_db.ler_csv("lojas.csv"):
            self.lojas.append(Loja(l["CodigoLoja"], l["Nome"]))

        # Carregar Grafo
        for l in self.gestor_db.ler_csv("conexoes.csv"):
            self.grafo.adicionar_conexao(l["CodigoHabitatA"], l["CodigoHabitatB"], l["Distancia"])

    def guardar_tudo(self):
        print("\n>> A guardar dados no disco...")
        self.gestor_db.guardar_csv("areas.csv", ["CodigoArea", "Nome", "Descricao"], [x.to_dict() for x in self.areas])
        self.gestor_db.guardar_csv("habitats.csv", ["CodigoHabitat", "Nome", "Tipo", "CodigoArea"], [x.to_dict() for x in self.habitats])
        self.gestor_db.guardar_csv("tratadores.csv", ["CodigoTratador", "Nome", "Especialidade"], [x.to_dict() for x in self.tratadores])
        self.gestor_db.guardar_csv("animais.csv", ["CodigoAnimal", "NomeComum", "NomeCientifico", "Especie", "Idade", "CodigoHabitat", "CodigoTratador"], [x.to_dict() for x in self.animais])
        self.gestor_db.guardar_csv("exposicoes.csv", ["CodigoExposicao", "Nome", "Tema", "Horario", "LocalID"], [x.to_dict() for x in self.exposicoes])
        self.gestor_db.guardar_csv("lojas.csv", ["CodigoLoja", "Nome"], [x.to_dict() for x in self.lojas])
        print(">> Sucesso! Todos os ficheiros foram atualizados.\n")

    # --- 2. AUXILIARES E VALIDAÇÃO ---
    def ler_input(self, msg, tipo=str):
        while True:
            val = input(msg)
            if tipo == int:
                if val.isdigit(): return int(val)
                print("Erro: Insira um número inteiro.")
            elif tipo == float:
                try: return float(val)
                except: print("Erro: Insira um número decimal.")
            else:
                if val.strip(): return val
                print("Erro: O campo não pode estar vazio.")

    def encontrar_por_id(self, lista, id_procurado, atributo_id="cod"):
        for obj in lista:
            if getattr(obj, atributo_id) == id_procurado:
                return obj
        return None

    # --- 3. GESTÃO DE ÁREAS ---
    def menu_areas(self):
        print("\n--- GESTÃO DE ÁREAS ---")
        print("1. Adicionar | 2. Listar | 3. Remover | 0. Voltar")
        op = input("Opção: ")
        if op == "1":
            cod = self.ler_input("Código Área: ")
            if self.encontrar_por_id(self.areas, cod):
                print("Erro: Código já existe!")
                return
            nome = self.ler_input("Nome: ")
            desc = self.ler_input("Descrição: ")
            self.areas.append(Area(cod, nome, desc))
            print("Área criada!")
        elif op == "2":
            for a in self.areas: print(f"[{a.cod}] {a.nome} - {a.descricao}")
        elif op == "3":
            cod = input("Código a remover: ")
            obj = self.encontrar_por_id(self.areas, cod)
            if obj: 
                self.areas.remove(obj)
                print("Área removida.")
            else: print("Área não encontrada.")

    # --- 4. GESTÃO DE HABITATS ---
    def menu_habitats(self):
        print("\n--- GESTÃO DE HABITATS ---")
        print("1. Adicionar | 2. Listar | 3. Editar | 0. Voltar")
        op = input("Opção: ")
        
        if op == "1":
            cod = self.ler_input("Código Habitat: ")
            if self.encontrar_por_id(self.habitats, cod):
                print("Erro: Código de Habitat já existe.")
                return

            nome = self.ler_input("Nome: ")
            tipo = self.ler_input("Tipo (ex: Aquático): ")
            area = self.ler_input("Código da Área: ")
            
            # Validação
            if not self.encontrar_por_id(self.areas, area):
                print("ERRO: Essa área não existe! Crie a área primeiro.")
            else:
                self.habitats.append(Habitat(cod, nome, tipo, area))
                print("Habitat criado!")

        elif op == "2":
            for h in self.habitats: print(f"[{h.cod}] {h.nome} ({h.tipo}) -> Área: {h.area_id}")
            
        elif op == "3":
            cod = input("Código a editar: ")
            h = self.encontrar_por_id(self.habitats, cod)
            if h:
                print(f"A editar: {h.nome} (Pressione Enter para manter o atual)")
                
                novo_nome = input(f"Novo Nome ({h.nome}): ")
                if novo_nome.strip(): h.nome = novo_nome
                
                novo_tipo = input(f"Novo Tipo ({h.tipo}): ")
                if novo_tipo.strip(): h.tipo = novo_tipo

                nova_area = input(f"Nova Área ({h.area_id}): ")
                if nova_area.strip():
                    if self.encontrar_por_id(self.areas, nova_area):
                        h.area_id = nova_area
                        print("Área atualizada.")
                    else:
                        print("ERRO: A área indicada não existe! A área manteve-se inalterada.")

                print("Habitat editado com sucesso.")
            else:
                print("Habitat não encontrado.")

    # --- 5. GESTÃO DE ANIMAIS (COM VALIDAÇÃO FORTE) ---
    def menu_animais(self):
        print("\n--- GESTÃO DE ANIMAIS ---")
        print("1. Registar Animal")
        print("2. Listar Todos")
        print("3. Pesquisar (Nome/Espécie/Habitat)")
        print("4. Remover Animal")
        print("0. Voltar")
        op = input("Opção: ")

        if op == "1":
            cod = self.ler_input("Código Animal: ")
            if self.encontrar_por_id(self.animais, cod):
                print("Erro: Já existe um animal com este código.")
                return

            nome = self.ler_input("Nome Comum: ")
            cient = input("Nome Científico (opcional): ")
            esp = self.ler_input("Espécie: ")
            idade = self.ler_input("Idade: ", int)
            
            # --- VALIDAÇÃO FORTE DE HABITAT ---
            hid = self.ler_input("Código Habitat: ")
            if not self.encontrar_por_id(self.habitats, hid):
                print(f"ERRO CRÍTICO: O Habitat '{hid}' não existe!")
                print("Operação cancelada. Nada foi registado.")
                return 

            # --- VALIDAÇÃO FORTE DE TRATADOR ---
            tid = self.ler_input("Código Tratador: ")
            if not self.encontrar_por_id(self.tratadores, tid):
                print(f"ERRO CRÍTICO: O Tratador '{tid}' não existe!")
                print("Operação cancelada. Nada foi registado.")
                return 
            
            self.animais.append(Animal(cod, nome, cient, esp, idade, hid, tid))
            print("Sucesso: Animal registado corretamente.")

        elif op == "2":
            print(f"{'COD':<5} {'NOME':<15} {'ESPÉCIE':<15} {'HABITAT':<10} {'TRATADOR':<10}")
            for a in self.animais:
                print(f"{a.cod:<5} {a.nome:<15} {a.especie:<15} {a.habitat_id:<10} {a.tratador_id:<10}")

        elif op == "3":
            termo = input("Pesquisar por: ").lower()
            resultados = [a for a in self.animais if termo in a.nome.lower() or termo in a.especie.lower() or termo == a.habitat_id.lower()]
            print(f"Encontrados: {len(resultados)}")
            for a in resultados: print(f"- {a.nome} ({a.especie}) no {a.habitat_id}")

        elif op == "4":
            cod = input("Código animal a remover: ")
            a = self.encontrar_por_id(self.animais, cod)
            if a: 
                self.animais.remove(a)
                print("Animal removido.")
            else: print("Não encontrado.")

    # --- 6. GESTÃO DE TRATADORES E EVENTOS ---
    def menu_staff_eventos(self):
        print("\n--- STAFF E EVENTOS ---")
        print("1. Gerir Tratadores (Adicionar/Listar)")
        print("2. Gerir Exposições (Adicionar/Listar)")
        op = input("Opção: ")
        
        if op == "1":
            sub = input("1. Novo Tratador | 2. Listar: ")
            if sub == "1":
                c = self.ler_input("Código: ")
                if self.encontrar_por_id(self.tratadores, c):
                    print("Erro: Código já existe.")
                    return
                n = self.ler_input("Nome: ")
                e = self.ler_input("Especialidade: ")
                self.tratadores.append(Tratador(c, n, e))
                print("Tratador registado.")
            elif sub == "2":
                for t in self.tratadores: print(f"[{t.cod}] {t.nome} - {t.especialidade}")

        elif op == "2":
            sub = input("1. Nova Exposição | 2. Listar: ")
            if sub == "1":
                c = self.ler_input("Código Evento: ")
                n = self.ler_input("Nome Evento: ")
                t = self.ler_input("Tema: ")
                h = self.ler_input("Horário (ex: 14:30): ")
                l = self.ler_input("Local (ID Area/Habitat): ")
                self.exposicoes.append(Exposicao(c, n, t, h, l))
            elif sub == "2":
                for e in self.exposicoes: print(f"{e.horario} - {e.nome} ({e.local_id})")

    # --- 7. LOJAS E ESTATISTICAS ---
    def menu_lojas(self):
        print("\n--- LOJAS ---")
        print("1. Adicionar Loja")
        print("2. Listar Lojas")
        op = input("Opção: ")
        if op == "1":
            c = self.ler_input("Código Loja: ")
            n = self.ler_input("Nome Loja: ")
            self.lojas.append(Loja(c, n))
        elif op == "2":
            for l in self.lojas: print(f"[{l.cod}] {l.nome}")

    def mostrar_estatisticas(self):
        print("\n=== ESTATÍSTICAS DO ZOO ===")
        print(f"Total Animais: {len(self.animais)}")
        print(f"Total Habitats: {len(self.habitats)}")
        print(f"Total Visitantes (Simulado): {len(self.animais) * 5 + 20}")
        print(f"Receita de Bilhetes (Sessão): {self.receita_bilhetes}€")
        if self.habitats:
            print(f"Habitat mais popular: {self.habitats[0].nome}")

    # --- 8. APLICAÇÃO CLIENTE ---
    def menu_visitante(self):
        while True:
            print("\n=== ÁREA DO VISITANTE ===")
            print("1. Consultar Animais e Habitats")
            print("2. Agenda de Exposições")
            print("3. Comprar Bilhetes")
            print("4. Mapa Inteligente (Caminho mais curto)")
            print("0. Voltar")
            op = input("Opção: ")

            if op == "1":
                self.menu_animais() 
            elif op == "2":
                print("\n--- Agenda ---")
                for e in self.exposicoes: 
                    print(f"[Horário: {e.horario}] {e.nome} - Tema: {e.tema}")
            elif op == "3":
                print("\n--- Bilheteira ---")
                print("1. Bilhete Normal (15€)")
                print("2. Bilhete Criança (8€)")
                qtd = self.ler_input("Quantidade: ", int)
                tipo = input("Tipo (1 ou 2): ")
                custo = qtd * 15 if tipo == "1" else qtd * 8
                print(f"Total a pagar: {custo}€")
                confirmar = input("Confirmar compra? (s/n): ")
                if confirmar.lower() == 's':
                    self.receita_bilhetes += custo
                    print("Compra efetuada! Bem-vindo ao Zoo.")
            elif op == "4":
                self.planear_rota()
            elif op == "0":
                break

    def planear_rota(self):
        print("\n--- Rota Inteligente ---")
        if not self.habitats:
            print("Não há habitats suficientes para calcular rotas.")
            return
        print("Habitats:", [h.cod for h in self.habitats])
        origem = input("Onde está (Código Habitat)? ")
        destino = input("Onde quer ir? ")
        custo, caminho = self.grafo.dijkstra(origem, destino)
        if caminho:
            print(f"-> Rota: {' > '.join(caminho)}")
            print(f"-> Distância: {custo}m")
        else:
            print("Caminho não encontrado. Verifique as conexões.")

    # --- MENUS PRINCIPAIS ---
    def menu_admin(self):
        while True:
            print("\n=== ADMINISTRAÇÃO ===")
            print("1. Gerir Áreas")
            print("2. Gerir Habitats")
            print("3. Gerir Animais")
            print("4. Staff e Eventos")
            print("5. Lojas")
            print("6. Estatísticas")
            print("7. Guardar Alterações") # <--- NOVO: Opção 7
            print("0. Voltar")
            op = input("Opção: ")
            
            if op == "1": self.menu_areas()
            elif op == "2": self.menu_habitats()
            elif op == "3": self.menu_animais()
            elif op == "4": self.menu_staff_eventos()
            elif op == "5": self.menu_lojas()
            elif op == "6": self.mostrar_estatisticas()
            elif op == "7": self.guardar_tudo() # <--- NOVO: Chama a gravação
            elif op == "0": break

# --- ARRANQUE ---
def menu_principal():
    sistema = SistemaZoo()
    while True:
        print("\n##########################")
        print("#    ZOO SYSTEM 2025     #")
        print("##########################")
        print("1. Entrar como Administrador")
        print("2. Entrar como Visitante")
        print("0. Sair e Guardar")
        op = input("Opção: ")

        if op == "1": sistema.menu_admin()
        elif op == "2": sistema.menu_visitante()
        elif op == "0": 
            sistema.guardar_tudo()
            break
        else: print("Opção inválida.")

if __name__ == "__main__":
    try:
        menu_principal()
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        input("\nPressiona ENTER para sair...")