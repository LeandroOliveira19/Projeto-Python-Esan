import networkx as nx
import matplotlib.pyplot as plt


def show_dynamic_map(grafo, habitats):
    if not grafo.adjacencias:  # Assuming you have a property/method to check this
        print("AVISO: GrafoZoo não tem conexões definidas. O mapa não pode ser gerado.")
        return

    # 1. Processar Habitats (Lista de objetos Habitat -> Dicionário Código:Nome)
    # Acessa os atributos 'cod' e 'nome' dos objetos Habitat
    habitat_labels = {h.cod: h.nome for h in habitats}

    # 2. Processar GrafoZoo (Lista de Adjacência -> Lista de Arestas NetworkX)
    # Evita adicionar arestas duplicadas (A->B e B->A)
    visited_pairs = set()
    edge_list = []
    for u, neighbors in grafo.adjacencias.items():
        for v, distance in neighbors.items():
            # Cria uma chave única para a aresta (o par ordenado)
            pair_key = tuple(sorted((u, v)))
            if pair_key not in visited_pairs:
                # Adiciona a aresta no formato (origem, destino, {'atributo': valor})
                edge_list.append((u, v, {'Distancia': distance}))
                visited_pairs.add(pair_key)

    G = nx.Graph()
    G.add_edges_from(edge_list)



    # 3. --- Configuração e Desenho do Grafo ---
    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(15, 8), num='ZOO SYSTEM 2025 Dynamic Map')
    plt.axis('off')
    plt.title('ZOO SYSTEM 2025™ Dynamic Map', fontsize=14)

    # Desenhar os Nós (Códigos)
    nx.draw_networkx_nodes(G, pos, node_size=1500, node_color='lightblue', edgecolors='black', linewidths=1.5)
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold', font_color='black')

    # Desenhar as Arestas (Distâncias)
    nx.draw_networkx_edges(G, pos, width=2, alpha=0.7, edge_color='gray')
    edge_labels = nx.get_edge_attributes(G, 'Distancia')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_color='black', font_size=10, label_pos=0.3)

    # 4. --- Criar e Desenhar a Legenda (Caption) ---
    caption_text = "Legenda de Habitats (Código : Nome):\n\n"
    for code, name in sorted(habitat_labels.items()):
        caption_text += f"{code}: {name}\n"

    plt.text(
        x=1.05,
        y=0.9,
        s=caption_text,
        transform=plt.gca().transAxes,
        fontsize=10,
        verticalalignment='top',
        bbox=dict(boxstyle="round,pad=0.5", fc="white", alpha=0.6)
    )

    # background
    image_path = "codigo/img/girafe.jpeg"

    # Get the current axes object
    ax = plt.gca()
    # --- ADD BACKGROUND IMAGE ---
    try:
        # 1. Load the image
        bg_image = plt.imread(image_path)

        # 2. Draw the NetworkX elements first to establish the plot limits

        # We need the limits *after* drawing the nodes/edges,
        # or we calculate them from pos values.


        # Get the current x and y limits *after* drawing the graph
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()

        # 3. Display the background image
        # Use ax.imshow to place the image at the determined extent,
        # and set zorder to -1 to push it behind the graph elements.
        ax.imshow(
            bg_image,
            extent=(xmin, xmax, ymin, ymax),
            aspect='auto',
            zorder=-1,
            alpha=0.7  # Optional: adjust transparency for better visibility of the graph
        )


    except FileNotFoundError:
        print(f"AVISO: Imagem de fundo não encontrada em: {image_path}. O mapa será gerado sem imagem de fundo.")

    plt.tight_layout()
    plt.show()