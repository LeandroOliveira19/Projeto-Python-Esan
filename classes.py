class Area:
    def __init__(self, cod, nome, descricao):
        self.cod = cod
        self.nome = nome
        self.descricao = descricao
    def to_dict(self):
        return {"CodigoArea": self.cod, "Nome": self.nome, "Descricao": self.descricao}

class Habitat:
    def __init__(self, cod, nome, tipo, area_id):
        self.cod = cod
        self.nome = nome
        self.tipo = tipo
        self.area_id = area_id
    def to_dict(self):
        return {"CodigoHabitat": self.cod, "Nome": self.nome, "Tipo": self.tipo, "CodigoArea": self.area_id}

class Animal:
    def __init__(self, cod, nome, cientifico, especie, idade, habitat_id, tratador_id):
        self.cod = cod
        self.nome = nome
        self.cientifico = cientifico
        self.especie = especie
        self.idade = idade
        self.habitat_id = habitat_id
        self.tratador_id = tratador_id
    def to_dict(self):
        return {
            "CodigoAnimal": self.cod, "NomeComum": self.nome, "NomeCientifico": self.cientifico,
            "Especie": self.especie, "Idade": self.idade, 
            "CodigoHabitat": self.habitat_id, "CodigoTratador": self.tratador_id
        }

class Tratador:
    def __init__(self, cod, nome, especialidade):
        self.cod = cod
        self.nome = nome
        self.especialidade = especialidade
    def to_dict(self):
        return {"CodigoTratador": self.cod, "Nome": self.nome, "Especialidade": self.especialidade}

class Exposicao:
    def __init__(self, cod, nome, tema, horario, local_id):
        self.cod = cod
        self.nome = nome
        self.tema = tema
        self.horario = horario
        self.local_id = local_id 
    def to_dict(self):
        return {"CodigoExposicao": self.cod, "Nome": self.nome, "Tema": self.tema, "Horario": self.horario, "LocalID": self.local_id}

class Loja:
    def __init__(self, cod, nome):
        self.cod = cod
        self.nome = nome
    def to_dict(self):
        return {"CodigoLoja": self.cod, "Nome": self.nome}

class Produto:
    def __init__(self, cod, loja_id, nome, preco, quantidade, vendas=0):
        self.cod = cod
        self.loja_id = loja_id
        self.nome = nome
        self.preco = preco
        self.quantidade = quantidade
        self.vendas = vendas 
    def to_dict(self):
        return {
            "CodigoProduto": self.cod, "CodigoLoja": self.loja_id, 
            "Nome": self.nome, "Preco": self.preco, 
            "Quantidade": self.quantidade, "Vendas": self.vendas
        }