import os
import time

#from pycparser.c_ast import While

from gerifich import GestorFicheiros
from classes import *
from grafo import GrafoZoo

class SistemaZoo:
    def __init__(self):
        self.gestor_db = GestorFicheiros()
        # Listas de Dados
        self.areas = []
        self.habitats = []
        self.animais = []
        self.tratadores = []
        self.exposicoes = []
        self.lojas = []
        self.produtos = [] # <--- NOVO: Lista de Produtos
        self.reservas = [] 
        
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

        # Carregar Produtos (NOVO)
        for l in self.gestor_db.ler_csv("produtos.csv"):
            self.produtos.append(Produto(l["CodigoProduto"], l["CodigoLoja"], l["Nome"], float(l["Preco"]), int(l["Quantidade"])))

        # Carregar Reservas
        for l in self.gestor_db.ler_csv("reservas.csv"):
            self.reservas.append(l)

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
        self.gestor_db.guardar_csv("produtos.csv", ["CodigoProduto", "CodigoLoja", "Nome", "Preco", "Quantidade"], [x.to_dict() for x in self.produtos])
        self.gestor_db.guardar_csv("reservas.csv", ["CodigoReserva", "CodigoVisitante", "CodigoExposicao"], self.reservas)
        
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
        print("1. Adicionar | 2. Listar | 3. Editar | 4. Remover | 0. Voltar")
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
        elif op == "3": # EDICAO NOVA
            cod = input("Código a editar: ")
            obj = self.encontrar_por_id(self.areas, cod)
            if obj:
                print(f"A editar '{obj.nome}' (Enter para manter)")
                novo_n = input(f"Nome ({obj.nome}): ")
                if novo_n.strip(): obj.nome = novo_n
                novo_d = input(f"Descrição ({obj.descricao}): ")
                if novo_d.strip(): obj.descricao = novo_d
                print("Área atualizada.")
            else: print("Não encontrada.")
        elif op == "4":
            cod = input("Código a remover: ")
            obj = self.encontrar_por_id(self.areas, cod)
            if obj: 
                # Opcional: Verificar se há habitats nesta área antes de remover
                self.areas.remove(obj)
                print("Área removida.")
            else: print("Área não encontrada.")

    # --- 4. GESTÃO DE HABITATS ---
    def menu_habitats(self):
        print("\n--- GESTÃO DE HABITATS ---")
        print("1. Adicionar | 2. Listar | 3. Editar | 4. Remover | 0. Voltar")
        op = input("Opção: ")
        
        if op == "1":
            cod = self.ler_input("Código Habitat: ")
            if self.encontrar_por_id(self.habitats, cod):
                print("Erro: Código de Habitat já existe.")
                return
            nome = self.ler_input("Nome: ")
            tipo = self.ler_input("Tipo (ex: Aquático): ")
            area = self.ler_input("Código da Área: ")
            
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

        elif op == "4":
            cod = input("Código a remover: ")
            h = self.encontrar_por_id(self.habitats, cod)
            if h:
                self.habitats.remove(h)
                print("Habitat removido.")
            else: print("Não encontrado.")

    # --- 5. GESTÃO DE ANIMAIS ---
    def menu_animais(self):
        print("\n--- GESTÃO DE ANIMAIS ---")
        print("1. Registar Animal")
        print("2. Listar Todos")
        print("3. Pesquisar")
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
            
            hid = self.ler_input("Código Habitat: ")
            if not self.encontrar_por_id(self.habitats, hid):
                print(f"ERRO CRÍTICO: O Habitat '{hid}' não existe!")
                return 

            tid = self.ler_input("Código Tratador: ")
            if not self.encontrar_por_id(self.tratadores, tid):
                print(f"ERRO CRÍTICO: O Tratador '{tid}' não existe!")
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

    # --- 6. GESTÃO DE STAFF E EVENTOS ---
    def menu_staff_eventos(self):
        print("\n--- STAFF E EVENTOS ---")
        print("1. Gerir Tratadores")
        print("2. Gerir Exposições")
        print("0. Voltar")
        op = input("Opção: ")
        
        if op == "1": self.submenu_tratadores()
        elif op == "2": self.submenu_exposicoes()

    def submenu_tratadores(self):
        print("\n-- TRATADORES --")
        print("1. Novo | 2. Listar | 3. Editar | 4. Remover")
        op = input("Opção: ")
        if op == "1":
            c = self.ler_input("Código: ")
            if self.encontrar_por_id(self.tratadores, c):
                print("Erro: Código já existe.")
                return
            n = self.ler_input("Nome: ")
            e = self.ler_input("Especialidade: ")
            self.tratadores.append(Tratador(c, n, e))
            print("Tratador registado.")
        elif op == "2":
            for t in self.tratadores: print(f"[{t.cod}] {t.nome} - {t.especialidade}")
        elif op == "3":
            c = input("Código a editar: ")
            t = self.encontrar_por_id(self.tratadores, c)
            if t:
                t.nome = self.ler_input(f"Novo Nome ({t.nome}): ")
                t.especialidade = self.ler_input(f"Nova Especialidade ({t.especialidade}): ")
                print("Editado.")
            else: print("Não encontrado.")
        elif op == "4":
            c = input("Código a remover: ")
            t = self.encontrar_por_id(self.tratadores, c)
            if t:
                self.tratadores.remove(t)
                print("Removido.")
            else: print("Não encontrado.")

    def submenu_exposicoes(self):
        print("\n-- EXPOSIÇÕES --")
        print("1. Nova | 2. Listar | 3. Editar | 4. Remover")
        op = input("Opção: ")
        if op == "1":
            c = self.ler_input("Código Evento: ")
            n = self.ler_input("Nome Evento: ")
            t = self.ler_input("Tema: ")
            h = self.ler_input("Horário (ex: 14:30): ")
            l = self.ler_input("Local (ID Area/Habitat): ")
            self.exposicoes.append(Exposicao(c, n, t, h, l))
            print("Evento criado.")
        elif op == "2":
            for e in self.exposicoes: print(f"[{e.cod}] {e.horario} - {e.nome} ({e.local_id})")
        elif op == "3":
            c = input("Código a editar: ")
            e = self.encontrar_por_id(self.exposicoes, c)
            if e:
                print("Enter para manter atual.")
                nn = input(f"Nome ({e.nome}): "); 
                if nn.strip(): e.nome = nn
                nt = input(f"Tema ({e.tema}): "); 
                if nt.strip(): e.tema = nt
                nh = input(f"Horário ({e.horario}): "); 
                if nh.strip(): e.horario = nh
                nl = input(f"Local ({e.local_id}): "); 
                if nl.strip(): e.local_id = nl
                print("Editado.")
            else: print("Não encontrado.")
        elif op == "4":
            c = input("Código a remover: ")
            e = self.encontrar_por_id(self.exposicoes, c)
            if e:
                self.exposicoes.remove(e)
                print("Removido.")

    # --- 7. LOJAS E PRODUTOS (FUNCIONALIDADE 12) ---
    def menu_lojas(self):
        print("\n--- LOJAS E PRODUTOS ---")
        print("1. Gerir Lojas")
        print("2. Gerir Produtos (Inventário)")
        print("0. Voltar")
        op = input("Opção: ")
        if op == "1": self.submenu_lojas()
        elif op == "2": self.submenu_produtos()

    def submenu_lojas(self):
        print("\n-- GERIR LOJAS --")
        print("1. Adicionar | 2. Listar | 3. Editar | 4. Remover")
        op = input("Opção: ")
        if op == "1":
            c = self.ler_input("Código Loja: ")
            if self.encontrar_por_id(self.lojas, c): 
                print("Já existe."); return
            n = self.ler_input("Nome Loja: ")
            self.lojas.append(Loja(c, n))
            print("Loja criada.")
        elif op == "2":
            for l in self.lojas: print(f"[{l.cod}] {l.nome}")
        elif op == "3":
            c = input("Código a editar: ")
            l = self.encontrar_por_id(self.lojas, c)
            if l:
                l.nome = self.ler_input(f"Novo Nome ({l.nome}): ")
                print("Editado.")
        elif op == "4":
            c = input("Código a remover: ")
            l = self.encontrar_por_id(self.lojas, c)
            if l:
                self.lojas.remove(l)
                print("Loja removida.")

    def submenu_produtos(self):
        print("\n-- GERIR PRODUTOS --")
        print("1. Adicionar Produto")
        print("2. Listar Produtos de uma Loja")
        print("3. Editar Produto")
        print("4. Remover Produto")
        op = input("Opção: ")

        if op == "1":
            lid = input("Código da Loja onde vai adicionar: ")
            if not self.encontrar_por_id(self.lojas, lid):
                print("Erro: Loja não existe.")
                return
            pid = self.ler_input("Código Produto: ")
            if self.encontrar_por_id(self.produtos, pid):
                print("Erro: Produto já existe.")
                return
            nome = self.ler_input("Nome Produto: ")
            preco = self.ler_input("Preço: ", float)
            qtd = self.ler_input("Quantidade: ", int)
            self.produtos.append(Produto(pid, lid, nome, preco, qtd))
            print("Produto adicionado.")

        elif op == "2":
            lid = input("Código da Loja (Enter para ver todos): ")
            print(f"{'COD':<5} {'NOME':<20} {'PREÇO':<10} {'QTD':<5} {'LOJA'}")
            for p in self.produtos:
                if not lid or p.loja_id == lid:
                    print(f"{p.cod:<5} {p.nome:<20} {p.preco:<10} {p.quantidade:<5} {p.loja_id}")

        elif op == "3":
            pid = input("Código do Produto a editar: ")
            p = self.encontrar_por_id(self.produtos, pid)
            if p:
                print(f"A editar {p.nome} (Loja {p.loja_id})")
                nn = input(f"Nome ({p.nome}): ")
                if nn.strip(): p.nome = nn
                npr = input(f"Preço ({p.preco}): ")
                if npr.strip(): p.preco = float(npr)
                nq = input(f"Quantidade ({p.quantidade}): ")
                if nq.strip(): p.quantidade = int(nq)
                print("Produto atualizado.")
            else: print("Produto não encontrado.")

        elif op == "4":
            pid = input("Código a remover: ")
            p = self.encontrar_por_id(self.produtos, pid)
            if p:
                self.produtos.remove(p)
                print("Produto removido.")

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
            print("2. Agenda de Exposições & Reservas")
            print("3. Bilheteira (Comprar Bilhetes)")
            print("4. Mapa Inteligente (Caminho mais curto)")
            print("0. Voltar")
            op = input("Opção: ")

            if op == "1":
                # self.menu_animais()
                self.menu_cliente_animais_habitats()
            elif op == "2":
                self.menu_reservas_exposicoes()
            elif op == "3":
                self.menu_bilheteira()
            elif op == "4":
                self.planear_rota()
            elif op == "0":
                break

    def menu_cliente_animais_habitats(self):#Revisar
        while True:
            print("\n--- Animais e Habitats ---")
            print("1. Listar Animais")
            print("2. Listar Habitats")
            print("3. Listar Animais por Habitat")
            print("0. Voltar")
            op = input("Opção: ")
            if op=="1":
                print(f"{'COD':<5} {'NOME':<15} {'ESPÉCIE':<15} {'HABITAT':<10} {'TRATADOR':<10}")
                for a in self.animais:
                    print(f"{a.cod:<5} {a.nome:<15} {a.especie:<15} {a.habitat_id:<10} {a.tratador_id:<10}")
            elif op=="2":
                print(f"{'COD':<5} {'NOME':<15}               {'ÁREA':<15}")
                for h in self.habitats: print(f"[{h.cod}] {h.nome} ({h.tipo}) -> Área: {h.area_id}")
            elif op=="3":
                # 1. Create a mapping from habitat ID to habitat name for easy lookup
                habitat_names = {h.cod: h.nome for h in self.habitats}

                # 2. Group animals by their habitat ID
                # This uses a dictionary where the keys are habitat IDs and the values are lists of animals
                animals_by_habitat = {}
                for animal in self.animais:
                    habitat_id = animal.habitat_id
                    if habitat_id not in animals_by_habitat:
                        animals_by_habitat[habitat_id] = []
                    animals_by_habitat[habitat_id].append(animal)

                # 3. Print the results, iterating through the grouped data
                print("\n--- Animais por Habitat ---")

                for habitat_id, animals in animals_by_habitat.items():
                    # Get the habitat name, or a default message if the ID is not found
                    habitat_name = habitat_names.get(habitat_id, f"[ID {habitat_id} - Nome Desconhecido]")

                    print(f"\n== Habitat: {habitat_name} (ID: {habitat_id}) ==")

                    # Check if there are animals in this habitat before printing the header
                    if not animals:
                        print("  (Nenhum animal neste habitat)")
                        continue

                    # Print the header for the animals in this specific habitat
                    print(f"{'COD':<5} {'NOME':<15} {'ESPÉCIE':<15} {'TRATADOR':<10}")
                    print("-----" + " " * 4 + "-" * 15 + " " * 4 + "-" * 15 + " " * 4 + "-" * 10)

                    # List all the animals in this group
                    for a in animals:
                        print(f"{a.cod:<5} {a.nome:<15} {a.especie:<15} {a.tratador_id:<10}")
            elif op=="0":
                break


    def menu_reservas_exposicoes(self):
        while True:
            print("\n--- AGENDA E RESERVAS ---")
            print("1. Ver Agenda de Exposições")
            print("2. Fazer Reserva em Exposição")
            print("0. Voltar")
            op = input("Opção: ")

            if op == "1":
                if not self.exposicoes:
                    print("Não há exposições agendadas.")
                for e in self.exposicoes:
                    print(f"[{e.cod}] {e.nome} às {e.horario} (Tema: {e.tema})")

            elif op == "2":
                flag=True
                while flag:
                    print("\n-- Nova Reserva --")
                    print("Digite o código da Exposição (0 para voltar)")
                    cod_exp = input("Código da Exposição: ")
                    if cod_exp!= "0":
                        evento = self.encontrar_por_id(self.exposicoes, cod_exp)
                        if not evento:
                            print("Erro: Exposição não encontrada.")
                            return
                        cod_vis = input("O seu Nome ou ID de Visitante (-1 para cancelar): ")
                        if cod_vis=="" or not cod_vis=="-1":
                            nova_reserva = {"CodigoReserva": f"R{len(self.reservas)+1}", "CodigoVisitante": cod_vis, "CodigoExposicao": cod_exp}
                            self.reservas.append(nova_reserva)
                            print(f"Reserva confirmada para '{evento.nome}'!")
                        else:
                            print("Reserva Cancelada!")
                            flag=False
                    else:
                        flag=False

            elif op=="0":
                break

    def menu_bilheteira(self):
        buying_mode=False#Will be set to true when buying to change text
        custo_total = 0.0

        def buying_process():
            buying_mode = True
            print("Digite a quantidade")
            qtd = int(input("Quantidade: "))
            return (buying_mode, qtd)

        while True:
            print("\n--- BILHETEIRA ---" if not buying_mode else "\n--- BILHETEIRA (A EFETUAR OPERAÇÃO)---")
            print("1. Bilhete Normal (15€)")
            print("2. Bilhete Criança (8€)")
            if buying_mode: print("3. Concluir Compra")
            print("0. Voltar" if not buying_mode else "0. Cancelar")#Ternary operator
            op=input("Opção: ")
            try:
                if op=="1":
                    (buying_mode,qtd)=buying_process()

                    if qtd <= 0:
                        print("Quantidade menor ou igual a zero, voltando a etapa anterior...")
                    else:
                        custo_total+=qtd * 15

                elif op=="2":
                    (buying_mode,qtd)=buying_process()

                    if qtd <= 0:
                        print("Quantidade menor ou igual a zero, voltando a etapa anterior...")
                    else:
                        custo_total += qtd * 8

                elif op=="3" and buying_mode:
                    print("Valor a pagar: ",custo_total,"€")
                    conf = input("Confirmar pagamento? (s/n): ")
                    if conf.lower() == 's':
                        self.receita_bilhetes += custo_total
                        print("Pagamento aceite. Bem-vindo ao Zoo!")
                        break
                    else:
                        print("Pagamento cancelado, voltando a etapa anterior...")

                elif op=="0" and not buying_mode:
                    break

                elif op=="0" and buying_mode:
                    print("Tem certeza que deseja cancelar a operação?")
                    print("1. Não")
                    print("0. Sim")
                    op2=input("Opção: ")
                    if op2== "0":
                        break

            except ValueError:
                print("Erro: Valor inválido, voltando a etapa anterior...")


            # try:
            #     qtd = int(input("Quantidade: "))
            #     tipo = input("Tipo (1 ou 2): ")
            #     custo = qtd * 15 if tipo == "1" else qtd * 8
            #     print(f"Total a pagar: {custo}€")
            #     conf = input("Confirmar pagamento? (s/n): ")
            #     if conf.lower() == 's':
            #         self.receita_bilhetes += custo
            #         print("Pagamento aceite. Bem-vindo ao Zoo!")
            # except ValueError:
            #     print("Erro: Valor inválido.")

    def planear_rota(self):
        print("\n--- ROTA INTELIGENTE (DIJKSTRA) ---")
        if not self.grafo.adjacencias:
            print("AVISO: Não existem conexões definidas no ficheiro 'conexoes.csv'.")
            return
        print("Habitats disponíveis:", [h.cod for h in self.habitats])
        origem = input("Código Habitat Início: ")
        destino = input("Código Habitat Fim: ")
        custo, caminho = self.grafo.dijkstra(origem, destino)
        if caminho:
            print(f"\n--> Melhor Rota: {' > '.join(caminho)}")
            print(f"--> Distância Total: {custo} metros")
        else:
            print("\nErro: Caminho não encontrado.")

    # --- MENUS PRINCIPAIS ---
    def menu_admin(self):
        while True:
            print("\n=== ADMINISTRAÇÃO ===")
            print("1. Gerir Áreas")
            print("2. Gerir Habitats")
            print("3. Gerir Animais")
            print("4. Staff e Eventos")
            print("5. Lojas e Produtos") # <--- Atualizado
            print("6. Estatísticas")
            print("7. Guardar Alterações")
            print("0. Voltar")
            op = input("Opção: ")
            
            if op == "1": self.menu_areas()
            elif op == "2": self.menu_habitats()
            elif op == "3": self.menu_animais()
            elif op == "4": self.menu_staff_eventos()
            elif op == "5": self.menu_lojas()
            elif op == "6": self.mostrar_estatisticas()
            elif op == "7": self.guardar_tudo()
            elif op == "0": break

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