import os
import time
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
        self.produtos = [] 
        self.reservas = [] 
        self.conexoes = [] # <--- NOVO: Lista para gerir as conexões e gravar no CSV
        
        # --- NOVOS CONTADORES PARA ESTATÍSTICAS ---
        self.qtd_bilhetes_adulto = 0
        self.qtd_bilhetes_crianca = 0
        
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

        # Carregar Produtos (ATUALIZADO PARA LER VENDAS)
        for l in self.gestor_db.ler_csv("produtos.csv"):
            vendas = int(l.get("Vendas", 0)) # Lê as vendas guardadas, ou 0 se não existir
            self.produtos.append(Produto(l["CodigoProduto"], l["CodigoLoja"], l["Nome"], float(l["Preco"]), int(l["Quantidade"]), vendas))

        # Carregar Reservas
        for l in self.gestor_db.ler_csv("reservas.csv"):
            self.reservas.append(l)

        # Carregar Grafo e Conexões (ALTERADO)
        for l in self.gestor_db.ler_csv("conexoes.csv"):
            self.conexoes.append(l) # Guarda na lista para poder gravar depois
            self.grafo.adicionar_conexao(l["CodigoHabitatA"], l["CodigoHabitatB"], l["Distancia"])

        # Carregar Estatísticas Financeiras
        fin = self.gestor_db.ler_csv("financeiro.csv")
        if fin:
            self.qtd_bilhetes_adulto = int(fin[0].get("Adulto", 0))
            self.qtd_bilhetes_crianca = int(fin[0].get("Crianca", 0))
            # Recalcula a receita total baseada no histórico
            self.receita_bilhetes = (self.qtd_bilhetes_adulto * 15.0) + (self.qtd_bilhetes_crianca * 8.0)

    def guardar_tudo(self):
        print("\n>> A guardar dados no disco...")
        self.gestor_db.guardar_csv("areas.csv", ["CodigoArea", "Nome", "Descricao"], [x.to_dict() for x in self.areas])
        self.gestor_db.guardar_csv("habitats.csv", ["CodigoHabitat", "Nome", "Tipo", "CodigoArea"], [x.to_dict() for x in self.habitats])
        self.gestor_db.guardar_csv("tratadores.csv", ["CodigoTratador", "Nome", "Especialidade"], [x.to_dict() for x in self.tratadores])
        self.gestor_db.guardar_csv("animais.csv", ["CodigoAnimal", "NomeComum", "NomeCientifico", "Especie", "Idade", "CodigoHabitat", "CodigoTratador"], [x.to_dict() for x in self.animais])
        self.gestor_db.guardar_csv("exposicoes.csv", ["CodigoExposicao", "Nome", "Tema", "Horario", "LocalID"], [x.to_dict() for x in self.exposicoes])
        self.gestor_db.guardar_csv("lojas.csv", ["CodigoLoja", "Nome"], [x.to_dict() for x in self.lojas])
        self.gestor_db.guardar_csv("reservas.csv", ["CodigoReserva", "CodigoVisitante", "CodigoExposicao"], self.reservas)
        
        # Guardar Produtos (Incluindo Vendas)
        self.gestor_db.guardar_csv("produtos.csv", ["CodigoProduto", "CodigoLoja", "Nome", "Preco", "Quantidade", "Vendas"], [x.to_dict() for x in self.produtos])
        
        # Guardar Conexões (NOVO)
        self.gestor_db.guardar_csv("conexoes.csv", ["CodigoHabitatA", "CodigoHabitatB", "Distancia"], self.conexoes)
        
        # Guardar Financeiro
        dados_fin = [{"Adulto": self.qtd_bilhetes_adulto, "Crianca": self.qtd_bilhetes_crianca}]
        self.gestor_db.guardar_csv("financeiro.csv", ["Adulto", "Crianca"], dados_fin)
        
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

    # --- Comparação "Case Insensitive" ---
    def encontrar_por_id(self, lista, id_procurado, atributo_id="cod"):
        procura_normalizada = str(id_procurado).strip().upper()
        for obj in lista:
            valor_obj = str(getattr(obj, atributo_id)).strip().upper()
            if valor_obj == procura_normalizada:
                return obj
        return None

    # --- 3. GESTÃO DE ÁREAS ---
    def menu_areas(self):
        while True:
            print("\n--- GESTÃO DE ÁREAS ---")
            print("1. Adicionar | 2. Listar | 3. Editar | 4. Remover | 0. Voltar")
            op = input("Opção: ")
            if op == "1":
                print("Digite o código da área (-1 para cancelar)")
                cod = self.ler_input("Código Área: ").upper()
                if cod!="-1":
                    if self.encontrar_por_id(self.areas, cod):
                        print("Erro: Código já existe!")
                        return
                    nome = self.ler_input("Nome: ")
                    desc = self.ler_input("Descrição: ")
                    self.areas.append(Area(cod, nome, desc))
                    print("Área criada!")
                else: print("Cancelado!")
            elif op == "2":
                for a in self.areas: print(f"[{a.cod}] {a.nome} - {a.descricao}")
            elif op == "3": 
                print("Digite o código da área (-1 para cancelar)")
                cod = input("Código a editar: ")
                if cod!="-1":
                    obj = self.encontrar_por_id(self.areas, cod)
                    if obj:
                        print(f"A editar '{obj.nome}' (Enter para manter)")
                        novo_n = input(f"Nome ({obj.nome}): ")
                        if novo_n.strip(): obj.nome = novo_n
                        novo_d = input(f"Descrição ({obj.descricao}): ")
                        if novo_d.strip(): obj.descricao = novo_d
                        print("Área atualizada.")
                    else: print("Não encontrada.")
                else: print("Edição de área cancelada!")
            elif op == "4":
                print("Digite o código da área (-1 para cancelar)")
                cod = input("Código a remover: ")
                if cod!="-1":
                    obj = self.encontrar_por_id(self.areas, cod)
                    if obj:
                        self.areas.remove(obj)
                        print("Área removida.")
                    else: print("Área não encontrada.")
                else: print("Remoção de área cancelada!")
            elif op=="0":
                break

    # --- 4. GESTÃO DE HABITATS (COM GESTÃO DE CONEXÕES) ---
    def menu_habitats(self):
        while True:
            print("\n--- GESTÃO DE HABITATS ---")
            print("1. Adicionar | 2. Listar | 3. Editar | 4. Remover | 0. Voltar")
            op = input("Opção: ")

            if op == "1":
                print("Digite o código (-1 para cancelar)")
                cod = self.ler_input("Código Habitat: ").upper()
                if cod!="-1":
                    if self.encontrar_por_id(self.habitats, cod):
                        print("Erro: Já existe.")
                        return
                    nome = self.ler_input("Nome: ")
                    tipo = self.ler_input("Tipo: ")
                    area = self.ler_input("Código da Área: ")

                    if not self.encontrar_por_id(self.areas, area):
                        print("ERRO: Área não existe!")
                    else:
                        self.habitats.append(Habitat(cod, nome, tipo, area))
                        print("Habitat criado!")

                        # --- ADICIONAR CONEXÕES LOGO APÓS CRIAR ---
                        print("\n=== Configurar Distâncias ===")
                        print("Este habitat precisa de estar ligado a outros para aparecer no mapa.")
                        while True:
                            resp = input("Deseja conectar a outro habitat agora? (s/n): ").lower()
                            if resp != 's': break
                            
                            print("\nHabitats existentes:")
                            for h in self.habitats:
                                if h.cod != cod: print(f"- {h.cod} ({h.nome})")
                            
                            dest = input("Código do habitat vizinho: ").upper()
                            if dest == cod:
                                print("Não pode conectar a si mesmo.")
                                continue
                                
                            if self.encontrar_por_id(self.habitats, dest):
                                dist = self.ler_input(f"Distância entre {cod} e {dest} (metros): ", float)
                                
                                # Adiciona ao Grafo (para usar já)
                                self.grafo.adicionar_conexao(cod, dest, dist)
                                # Adiciona à Lista (para guardar no CSV)
                                self.conexoes.append({
                                    "CodigoHabitatA": cod,
                                    "CodigoHabitatB": dest,
                                    "Distancia": dist
                                })
                                print("Conexão adicionada!")
                            else:
                                print("Habitat vizinho não encontrado.")

                else: print("Cancelado!")

            elif op == "2":
                for h in self.habitats: print(f"[{h.cod}] {h.nome} ({h.tipo}) -> Área: {h.area_id}")

            elif op == "3":
                cod = input("Código a editar: ")
                if cod != "-1":
                    h = self.encontrar_por_id(self.habitats, cod)
                    if h:
                        print(f"A editar: {h.nome}")
                        novo_nome = input(f"Novo Nome ({h.nome}): ")
                        if novo_nome.strip(): h.nome = novo_nome
                        novo_tipo = input(f"Novo Tipo ({h.tipo}): ")
                        if novo_tipo.strip(): h.tipo = novo_tipo
                        nova_area = input(f"Nova Área ({h.area_id}): ")
                        if nova_area.strip():
                            if self.encontrar_por_id(self.areas, nova_area):
                                h.area_id = nova_area.upper()
                                print("Área atualizada.")
                            else:
                                print("ERRO: Área inexistente.")
                        print("Sucesso.")
                    else: print("Não encontrado.")

            elif op == "4":
                cod = input("Código a remover: ").upper()
                if cod != "-1":
                    h = self.encontrar_por_id(self.habitats, cod)
                    if h:
                        self.habitats.remove(h)
                        # Remover também as conexões deste habitat para não quebrar o grafo
                        self.conexoes = [c for c in self.conexoes if c["CodigoHabitatA"] != cod and c["CodigoHabitatB"] != cod]
                        # Reconstrói o grafo do zero para garantir integridade
                        self.grafo = GrafoZoo()
                        for c in self.conexoes:
                            self.grafo.adicionar_conexao(c["CodigoHabitatA"], c["CodigoHabitatB"], c["Distancia"])
                        
                        print("Habitat e respetivas conexões removidos.")
                    else: print("Não encontrado.")
            elif op=="0":
                break

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
            cod = self.ler_input("Código Animal: ").upper()
            if self.encontrar_por_id(self.animais, cod):
                print("Erro: Já existe.")
                return
            nome = self.ler_input("Nome Comum: ")
            cient = input("Nome Científico: ")
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
            print("Animal registado.")

        elif op == "2":
            print(f"{'COD':<5} {'NOME':<15} {'ESPÉCIE':<15} {'HABITAT':<10} {'TRATADOR':<10}")
            for a in self.animais:
                print(f"{a.cod:<5} {a.nome:<15} {a.especie:<15} {a.habitat_id:<10} {a.tratador_id:<10}")

        elif op == "3":
            termo = input("Pesquisar: ").lower()
            resultados = [a for a in self.animais if termo in a.nome.lower() or termo in a.especie.lower()]
            print(f"Encontrados: {len(resultados)}")
            for a in resultados: print(f"- {a.nome} ({a.especie}) no {a.habitat_id}")

        elif op == "4":
            cod = input("Código a remover: ")
            a = self.encontrar_por_id(self.animais, cod)
            if a: 
                self.animais.remove(a)
                print("Removido.")
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
            c = self.ler_input("Código: ").upper()
            if self.encontrar_por_id(self.tratadores, c):
                print("Erro: Já existe.")
                return
            n = self.ler_input("Nome: ")
            e = self.ler_input("Especialidade: ")
            self.tratadores.append(Tratador(c, n, e))
            print("Registado.")
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
            c = self.ler_input("Código Evento: ").upper()
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
            c = self.ler_input("Código Loja: ").upper()
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
            lid = input("Código da Loja: ")
            if not self.encontrar_por_id(self.lojas, lid):
                print("Erro: Loja não existe.")
                return
            pid = self.ler_input("Código Produto: ").upper()
            if self.encontrar_por_id(self.produtos, pid):
                print("Erro: Produto já existe.")
                return
            nome = self.ler_input("Nome Produto: ")
            preco = self.ler_input("Preço: ", float)
            qtd = self.ler_input("Quantidade: ", int)
            self.produtos.append(Produto(pid, lid, nome, preco, qtd))
            print("Produto adicionado.")

        elif op == "2":
            lid = input("Código da Loja (Enter=Todos): ")
            print(f"{'COD':<5} {'NOME':<20} {'PREÇO':<10} {'QTD':<5} {'LOJA'}")
            for p in self.produtos:
                if not lid or p.loja_id == lid.strip().upper():
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

    # --- 8. ESTATÍSTICAS AVANÇADAS ---
    def desenhar_barra(self, valor, maximo, tamanho=20):
        if maximo == 0: return ""
        perc = valor / maximo
        chars = int(perc * tamanho)
        return "█" * chars + "░" * (tamanho - chars)

    def mostrar_estatisticas(self):
        print("\n" + "="*40)
        print("   DASHBOARD ZOO SYSTEM 2025")
        print("="*40)
        
        # 1. VISÃO GERAL
        total_animais = len(self.animais)
        total_habitats = len(self.habitats)
        print(f"\n[GERAL]")
        print(f"Total Animais:   {total_animais}")
        print(f"Total Habitats:  {total_habitats}")
        print(f"Total Staff:     {len(self.tratadores)}")

        # 2. FINANCEIRO (Bilheteira)
        total_bilhetes = self.qtd_bilhetes_adulto + self.qtd_bilhetes_crianca
        receita_real = (self.qtd_bilhetes_adulto * 15) + (self.qtd_bilhetes_crianca * 8)

        print(f"\n[FINANCEIRO - BILHETEIRA]")
        print(f"Receita Total:   {receita_real:.2f}€")
        print(f"Bilhetes Vendidos: {total_bilhetes}")
        
        if total_bilhetes > 0:
            p_adulto = (self.qtd_bilhetes_adulto / total_bilhetes) * 100
            p_crianca = (self.qtd_bilhetes_crianca / total_bilhetes) * 100
            print(f"\nDistribuição de Visitantes:")
            print(f"Adultos  ({int(p_adulto)}%) |{self.desenhar_barra(self.qtd_bilhetes_adulto, total_bilhetes)}| ({self.qtd_bilhetes_adulto})")
            print(f"Crianças ({int(p_crianca)}%) |{self.desenhar_barra(self.qtd_bilhetes_crianca, total_bilhetes)}| ({self.qtd_bilhetes_crianca})")
        else:
            print("(Sem dados de bilhetes ainda)")

        # 3. VENDAS DE PRODUTOS
        print(f"\n[TOP PRODUTOS MAIS VENDIDOS]")
        # Ordena produtos por vendas (do maior para o menor)
        produtos_ordenados = sorted(self.produtos, key=lambda p: p.vendas, reverse=True)
        top_3 = produtos_ordenados[:3]
        
        if top_3 and top_3[0].vendas > 0:
            max_vendas = top_3[0].vendas
            for p in top_3:
                if p.vendas > 0:
                    barra = self.desenhar_barra(p.vendas, max_vendas, 15)
                    print(f"{p.nome:<15} |{barra}| {p.vendas} un.")
        else:
            print("(Ainda não foram vendidos produtos)")

        # 4. EXPOSIÇÕES MAIS POPULARES
        print(f"\n[POPULARIDADE DAS EXPOSIÇÕES]")
        if not self.exposicoes:
            print("(Sem exposições criadas)")
        else:
            contagem = {}
            for r in self.reservas:
                eid = r["CodigoExposicao"]
                contagem[eid] = contagem.get(eid, 0) + 1
            
            expos_ordenadas = sorted(self.exposicoes, key=lambda e: contagem.get(e.cod, 0), reverse=True)
            
            if contagem:
                max_res = max(contagem.values())
                for e in expos_ordenadas[:3]:
                    qtd = contagem.get(e.cod, 0)
                    barra = self.desenhar_barra(qtd, max_res, 15)
                    print(f"{e.nome:<15} |{barra}| {qtd} reservas")
            else:
                print("(Sem reservas registadas)")

        input("\nPressione Enter para voltar...")

    # --- 9. APLICAÇÃO CLIENTE ---
    def menu_visitante(self):
        import dynamic_map  # <--- IMPORT CORRIGIDO
        while True:
            print("\n=== ÁREA DO VISITANTE ===")
            print("1. Consultar Animais e Habitats")
            print("2. Agenda de Exposições & Reservas")
            print("3. Bilheteira (Comprar Bilhetes)")
            print("4. Loja de Souvenirs (Comprar)") 
            print("5. Planear Rota (Caminho mais curto)")
            print("6. Visualizar Mapa")
            print("0. Voltar")
            op = input("Opção: ")

            if op == "1": self.menu_cliente_animais_habitats()
            elif op == "2": self.menu_reservas_exposicoes()
            elif op == "3": self.menu_bilheteira()
            elif op == "4": self.menu_cliente_loja() 
            elif op == "5": self.planear_rota()
            elif op == "6": dynamic_map.show_dynamic_map(self.grafo, self.habitats) # <--- CHAMADA CORRIGIDA
            elif op == "0": break

    def menu_cliente_animais_habitats(self):
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
                habitat_names = {h.cod: h.nome for h in self.habitats}
                animals_by_habitat = {}
                for animal in self.animais:
                    habitat_id = animal.habitat_id
                    if habitat_id not in animals_by_habitat:
                        animals_by_habitat[habitat_id] = []
                    animals_by_habitat[habitat_id].append(animal)

                print("\n--- Animais por Habitat ---")

                for habitat_id, animals in animals_by_habitat.items():
                    habitat_name = habitat_names.get(habitat_id, f"[ID {habitat_id} - Nome Desconhecido]")
                    print(f"\n== Habitat: {habitat_name} (ID: {habitat_id}) ==")

                    if not animals:
                        print("  (Nenhum animal neste habitat)")
                        continue

                    print(f"{'COD':<5} {'NOME':<15} {'ESPÉCIE':<15} {'TRATADOR':<10}")
                    print("-----" + " " * 4 + "-" * 15 + " " * 4 + "-" * 15 + " " * 4 + "-" * 10)

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
        buying_mode=False
        custo_total = 0.0
        
        # Variáveis temporárias para contar nesta sessão de compra
        temp_adultos = 0
        temp_criancas = 0

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
            print("0. Voltar" if not buying_mode else "0. Cancelar")
            op=input("Opção: ")
            try:
                if op=="1":
                    (buying_mode,qtd)=buying_process()
                    if qtd <= 0:
                        print("Quantidade menor ou igual a zero.")
                    else:
                        custo_total+=qtd * 15
                        temp_adultos += qtd # Conta temporariamente

                elif op=="2":
                    (buying_mode,qtd)=buying_process()
                    if qtd <= 0:
                        print("Quantidade menor ou igual a zero.")
                    else:
                        custo_total += qtd * 8
                        temp_criancas += qtd # Conta temporariamente

                elif op=="3" and buying_mode:
                    print("Valor a pagar: ",custo_total,"€")
                    conf = input("Confirmar pagamento? (s/n): ")
                    if conf.lower() == 's':
                        self.receita_bilhetes += custo_total
                        
                        # --- ATUALIZA ESTATÍSTICAS ---
                        self.qtd_bilhetes_adulto += temp_adultos
                        self.qtd_bilhetes_crianca += temp_criancas
                        
                        print("Pagamento aceite. Bem-vindo ao Zoo!")
                        break
                    else:
                        print("Pagamento cancelado.")

                elif op=="0" and not buying_mode:
                    break

                elif op=="0" and buying_mode:
                    print("Tem certeza que deseja cancelar?")
                    if input("1. Não | 0. Sim: ") == "0":
                        break

            except ValueError:
                print("Erro: Valor inválido.")

    # --- NOVA FUNÇÃO: LOJA DO CLIENTE ---
    def menu_cliente_loja(self):
        print("\n--- LOJA DE SOUVENIRS ---")
        if not self.produtos:
            print("A loja está vazia hoje.")
            return

        print(f"{'COD':<5} {'NOME':<20} {'PREÇO':<10}")
        print("-" * 40)
        for p in self.produtos:
            if p.quantidade > 0:
                print(f"{p.cod:<5} {p.nome:<20} {p.preco}€")
        
        cod = input("\nDigite o código do produto para comprar (0 para sair): ")
        if cod != "0":
            prod = self.encontrar_por_id(self.produtos, cod)
            if prod and prod.quantidade > 0:
                print(f"Vai comprar: {prod.nome} ({prod.preco}€)")
                if input("Confirmar? (s/n): ") == 's':
                    prod.quantidade -= 1
                    prod.vendas += 1 # <--- ATUALIZA A ESTATÍSTICA DE VENDAS
                    print("Obrigado pela compra!")
            else:
                print("Produto não encontrado ou esgotado.")

    def planear_rota(self):
        print("\n--- ROTA INTELIGENTE (DIJKSTRA) ---")
        if not self.grafo.adjacencias:
            print("AVISO: Não existem conexões definidas no ficheiro 'conexoes.csv'.")
            return
        print("Habitats disponíveis:", [h.cod for h in self.habitats])
        origem = input("Código Habitat Início: ")
        destino = input("Código Habitat Fim: ")
        
        # Converte para maiúsculas antes de calcular
        custo, caminho = self.grafo.dijkstra(origem.strip().upper(), destino.strip().upper())
        
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
            print("5. Lojas e Produtos") 
            print("6. Estatísticas Avançadas") # <--- Atualizado
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