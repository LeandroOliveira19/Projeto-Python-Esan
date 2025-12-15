import networkx as nx
import matplotlib.pyplot as plt
import os
import time
import tempfile  # <--- NOVO: Para usar a pasta temporária do Windows

def show_dynamic_map(grafo, habitats):
    # 1. Verificar conexões
    if not grafo.adjacencias:
        print("AVISO: GrafoZoo não tem conexões definidas. O mapa não pode ser gerado.")
        return

    # 2. Processar Dados
    habitat_labels = {h.cod: h.nome for h in habitats}

    visited_pairs = set()
    edge_list = []
    for u, neighbors in grafo.adjacencias.items():
        for v, distance in neighbors.items():
            pair_key = tuple(sorted((u, v)))
            if pair_key not in visited_pairs:
                edge_list.append((u, v, {'Distancia': distance}))
                visited_pairs.add(pair_key)

    G = nx.Graph()
    G.add_edges_from(edge_list)

    # 3. Desenhar
    plt.figure(figsize=(15, 10))
    plt.axis('off')
    plt.title('ZOO SYSTEM 2025 - Mapa de Habitats', fontsize=16, fontweight='bold', color='darkgreen')

    pos = nx.spring_layout(G, seed=42)

    nx.draw_networkx_nodes(G, pos, node_size=2500, node_color='#e6f2ff', edgecolors='#004d99', linewidths=2)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold', font_color='#003366')

    nx.draw_networkx_edges(G, pos, width=2.5, alpha=0.6, edge_color='#666666', style='dashed')
    edge_labels = nx.get_edge_attributes(G, 'Distancia')
    edge_labels_formatted = {k: f"{v}m" for k, v in edge_labels.items()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels_formatted, font_size=9, font_color='darkred', font_weight='bold')

    # 4. Legenda
    caption_text = "LEGENDA:\n"
    for code, name in sorted(habitat_labels.items()):
        caption_text += f"{code}: {name}\n"

    plt.text(0.02, 0.02, caption_text, transform=plt.gca().transAxes, fontsize=10,
             bbox=dict(boxstyle="round", fc="white", ec="gray", alpha=0.9), verticalalignment='bottom')

    if os.name=="windows":
        # 5. Imagem de Fundo
        base_dir = os.path.dirname(os.path.abspath(__file__))
        full_image_path = os.path.join(base_dir, "img", "girafe.jpeg")

        if os.path.exists(full_image_path):
            try:
                bg_image = plt.imread(full_image_path)
                ax = plt.gca()
                xmin, xmax = ax.get_xlim()
                ymin, ymax = ax.get_ylim()
                ax.imshow(bg_image, extent=(xmin, xmax, ymin, ymax), aspect='auto', zorder=-1, alpha=0.5)
            except:
                pass

        # 6. GUARDAR NA PASTA TEMPORÁRIA (Solução Definitiva)
        try:
            # Gera um nome único
            timestamp = int(time.time())
            nome_ficheiro = f"mapa_zoo_{timestamp}.png"

            # Obtém a pasta temporária do Windows (ex: C:\Users\...\AppData\Local\Temp)
            pasta_temp = tempfile.gettempdir()
            caminho_completo = os.path.join(pasta_temp, nome_ficheiro)

            # Guarda lá (onde temos sempre permissão)
            plt.savefig(caminho_completo, dpi=150, bbox_inches='tight')
            print(f"\n>> Sucesso! Mapa gerado em: {caminho_completo}")

            # Abre a imagem
            print(">> A abrir imagem...")
            os.startfile(caminho_completo)
        except Exception as e:
            print(f"\n[ERRO CRÍTICO] Não foi possível gerar o mapa: {e}")
        finally:
            plt.close()
    else:
        # background
        image_path = "codigo/img/girafe.jpeg"

        # Get the current axes object
        ax = plt.gca()
        # --- ADD BACKGROUND IMAGE ---
        try:
            # 1. Load the image
            bg_image = plt.imread(image_path)

            # Get the current x and y limits after drawing the graph
            xmin, xmax = ax.get_xlim()
            ymin, ymax = ax.get_ylim()

            # Display the background image
            ax.imshow(
                bg_image,
                extent=(xmin, xmax, ymin, ymax),
                aspect='auto',
                zorder=-1,
                alpha=0.7
            )


        except FileNotFoundError:
            print(f"AVISO: Imagem de fundo não encontrada em: {image_path}. O mapa será gerado sem imagem de fundo.")

        plt.tight_layout()
        plt.show()

