import heapq

class GrafoZoo:
    def __init__(self):
        # Estrutura: { 'Habitat1': {'Habitat2': 50, 'Habitat3': 10}, ... }
        self.adjacencias = {}

    def adicionar_conexao(self, origem, destino, distancia):
        if origem not in self.adjacencias:
            self.adjacencias[origem] = {}
        if destino not in self.adjacencias:
            self.adjacencias[destino] = {}
        
        # Grafo não direcionado (caminho vai e volta)
        self.adjacencias[origem][destino] = float(distancia)
        self.adjacencias[destino][origem] = float(distancia)

    def dijkstra(self, inicio, fim):
        # Fila de prioridade: (custo, nodo_atual, caminho)
        fila = [(0, inicio, [])]
        visitados = set()

        while fila:
            (custo, atual, caminho) = heapq.heappop(fila)
            
            # Reconstrói o caminho até agora
            caminho = caminho + [atual]

            if atual == fim:
                return (custo, caminho)

            if atual in visitados:
                continue
            visitados.add(atual)

            for vizinho, peso in self.adjacencias.get(atual, {}).items():
                if vizinho not in visitados:
                    heapq.heappush(fila, (custo + peso, vizinho, caminho))

        return (float('inf'), []) # Caminho não encontrado