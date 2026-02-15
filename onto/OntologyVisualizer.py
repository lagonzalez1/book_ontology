from owlready2 import *
from onto.WorldManager import WorldManager
from typing import Optional
from onto.WorldManager import WorldManager
from pathlib import Path
import networkx as nx
import matplotlib.pyplot as plt

import logging



pt = Path(__file__).parent.parent

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OntologyVisualizer:

    def __init__(self, onto: Optional[any]):
        self.onto = onto
        self.graph = nx.Graph()
        self.world = WorldManager.get_world()
        self.colormap = {
            'book': '#4C72B0',      # Blue
            'author': '#DD8452',     # Orange
            'publisher': '#55A868',   # Green
            'user': '#C44E52',        # Red
            'review': '#937860',      # Brown
            'other': '#8172B2'        # Purple
        }
    
    """ Visualize demo ontology"""
    def create_basic_graph(self, max_nodes: Optional[int] = 100) -> None:
        # Add books as nodes
        for book in list(self.onto.Book.instances())[:max_nodes//3]:
            
            # Book title
            book_title = book.book_title[0] if hasattr(book, 'book_title') and book.book_title else book.name
            self.graph.add_node(
                book.name, 
                label=book_title[:20], 
                tier=1,
                type='book', 
                color="skyblue"
            )

            if hasattr(book, 'has_author') and book.has_author:
                for author in book.has_author:
                    author_name = author.author_name[0] if hasattr(author, 'author_name') and author.author_name else author.name
                    self.graph.add_node(
                        author.name, 
                        label=author_name[:20], 
                        tier=2,
                        type="author", 
                        color="lightgreen"
                    )
                    self.graph.add_edge(
                        book.name, 
                        author.name, 
                        relation='written_by'
                    )
        
            if hasattr(book, 'has_publisher') and book.has_publisher:
                for pub in book.has_publisher:
                    pub_name = pub.publisher_name[0] if hasattr(pub, "publisher_name") and pub.publisher_name else pub.name
                    self.graph.add_node(
                        pub.name, 
                        label=pub_name[:20], 
                        tier=2,
                        type="publisher", 
                        color="lightcoral"
                    )
                    self.graph.add_edge(
                        book.name, 
                        pub.name, 
                        relation="published_by"
                    )
            if hasattr(book, 'has_review') and book.has_review:
                for review in book.has_review:
                    review_name = review.review_user_id[0] if hasattr(review, "review_user_id") and review.review_user_id else review.name
                    self.graph.add_node(
                        review.name,
                        label=review_name[:10],
                        tier=3,
                        type="user", 
                        color="orange",
                    )
                    self.graph.add_edge(book.name, review.name, relation="reviewed_by")
        
        return self.graph


    def visualize_spring(self, figsize=(15, 10), k=2, iterations=50, max_nodes: int = 50):
        if len(self.graph.nodes) == 0:
            self.create_basic_graph()
        
        plt.figure(figsize=figsize)
        
        # SPRING LAYOUT - Classic force-directed
        pos = nx.spring_layout(self.graph, k=k, iterations=iterations, seed=42)
        
        # Draw the graph
        self._draw_graph(pos, "Book Ontology - Spring Layout (Force-Directed)")
        
        plt.savefig('ontology_graph_spring.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return self.graph
    
    def visualize_kamada_kawai(self, figsize=(15, 10), max_nodes: int = 50):
        if len(self.graph.nodes) == 0:
            self.create_basic_graph(max_nodes)
        
        plt.figure(figsize=figsize)
        
        # KAMADA-KAWAI LAYOUT - Energy-based, often cleaner than spring
        pos = nx.kamada_kawai_layout(self.graph)
        
        # Draw the graph
        self._draw_graph(pos, "Book Ontology - Kamada-Kawai Layout")
        
        plt.savefig('ontology_graph_kamada.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return self.graph
    
    def visualize_shell(self, figsize=(14, 10), max_nodes: int = 50):
        if len(self.graph.nodes) == 0:
            self.create_basic_graph()
        
        plt.figure(figsize=figsize)
        
        # Group nodes by type for shells
        books = [n for n in self.graph.nodes if self.graph.nodes[n].get('type') == 'book']
        authors = [n for n in self.graph.nodes if self.graph.nodes[n].get('type') == 'author']
        publishers = [n for n in self.graph.nodes if self.graph.nodes[n].get('type') == 'publisher']
        others = [n for n in self.graph.nodes if n not in books + authors + publishers]
        
        # Create shells (books in center, then authors, then publishers/others)
        shells = []
        if books:
            shells.append(books)
        if authors:
            shells.append(authors)
        if publishers or others:
            shells.append(publishers + others)
        
        # SHELL LAYOUT - Concentric circles
        pos = nx.shell_layout(self.graph, nlist=shells if shells else None)
        
        # Draw the graph
        self._draw_graph(pos, "Book Ontology - Shell Layout (Hierarchical)")
        
        plt.savefig('ontology_graph_shell.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return self.graph
    
    def visualize_random(self, figsize=(14, 10), seed=42, max_nodes: int = 50):
        """
        Random layout - Nodes placed randomly.
        Best for: Quick preview, no structure implied
        """
        if len(self.graph.nodes) == 0:
            self.create_basic_graph()
        
        plt.figure(figsize=figsize)
        
        # RANDOM LAYOUT
        pos = nx.random_layout(self.graph, seed=seed)
        
        # Draw the graph
        self._draw_graph(pos, "Book Ontology - Random Layout")
        
        plt.savefig('ontology_graph_random.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return self.graph
    
    def _draw_graph(self, pos, title, max_nodes: int = 50):
        """Core drawing function used by all layouts"""
        
        # Draw edges
        nx.draw_networkx_edges(self.graph, pos,
                             edge_color='gray',
                             alpha=0.5,
                             width=1,
                             arrows=True,
                             arrowstyle='->',
                             arrowsize=10)
        
        # Draw nodes by type
        node_types = {}
        for node in self.graph.nodes:
            node_type = self.graph.nodes[node].get('type', 'other')
            if node_type not in node_types:
                node_types[node_type] = []
            node_types[node_type].append(node)
        
        # Draw each node type with its color
        for node_type, nodes in node_types.items():
            if nodes:
                color = self.colormap.get(node_type, self.colormap['other'])
                
                # Different sizes for different types
                if node_type == 'book':
                    size = 1500
                elif node_type == 'author':
                    size = 1000
                elif node_type == 'publisher':
                    size = 800
                elif node_type == 'user':
                    size = 600
                else:
                    size = 500
                
                nx.draw_networkx_nodes(self.graph, pos,
                                     nodelist=nodes,
                                     node_color=color,
                                     node_size=size,
                                     alpha=0.8,
                                     label=f'{node_type.capitalize()}s ({len(nodes)})')
        
        # Draw labels
        labels = {node: self.graph.nodes[node].get('label', node[:10]) 
                 for node in self.graph.nodes}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8)
        
        plt.title(title, fontsize=16, fontweight='bold')
        plt.legend(scatterpoints=1, fontsize=10, loc='upper left')
        plt.axis('off')
        plt.tight_layout()
    
    def visualize_all(self, save_prefix="ontology_graph"):
        """Generate all graph types for comparison"""
        
        layouts = [
            (self.visualize_spring, "spring", "Spring Layout"),
            (self.visualize_kamada_kawai, "kamada", "Kamada-Kawai Layout"),
            (self.visualize_shell, "shell", "Shell Layout"),
            (self.visualize_random, "random", "Random Layout")
        ]
        
        print("\n" + "="*60)
        print("📊 GENERATING ALL GRAPH TYPES")
        print("="*60)
        
        for viz_func, name, description in layouts:
            print(f"\n🔄 Generating {description}...")
            try:
                viz_func()
                print(f"   ✅ Saved as {save_prefix}_{name}.png")
            except Exception as e:
                print(f"   ❌ Failed: {e}")
    
    def interactive_visualize(self, figsize=(15,10), max_nodes=100):
        """Interactive menu to choose visualization type"""
        
        print("\n" + "="*60)
        print("ONTOLOGY GRAPH VISUALIZATION")
        print("="*60)
        print("\nChoose layout type:")
        print("1. Spring (Force-directed) - Shows clusters")
        print("2. Kamada-Kawai - Distance-based, cleaner")
        print("3. Shell - Hierarchical (books in center)")
        print("4. Random - No structure")
        print("5. All layouts")
        print("0. Cancel")
        
        choice = input("\nEnter choice (0-5): ").strip()
        
        if choice == '1':
            self.visualize_spring(max_nodes=max_nodes)
        elif choice == '2':
            self.visualize_kamada_kawai(max_nodes=max_nodes)
        elif choice == '3':
            self.visualize_shell(max_nodes=max_nodes)
        elif choice == '4':
            self.visualize_random(max_nodes=max_nodes)
        elif choice == '5':
            self.visualize_all()
        else:
            print("❌ Cancelled")

        if len(self.graph.nodes) == 0:
            self.create_basic_graph()
        
        plt.figure(figsize=figsize)
        
        # Create layout
        #pos = nx.spring_layout(self.graph, k=2, iterations=50)

        # Circular layout
        pos = nx.kamada_kawai_layout(self.graph)
        
        # Draw nodes by type
        node_colors = []
        node_sizes = []
        
        for node in self.graph.nodes:
            node_type = self.graph.nodes[node].get('type', 'other')
            if node_type == 'book':
                node_colors.append('skyblue')
                node_sizes.append(1500)
            elif node_type == 'author':
                node_colors.append('lightgreen')
                node_sizes.append(800)
            elif node_type == 'publisher':
                node_colors.append('lightcoral')
                node_sizes.append(600)
            elif node_type == 'user':
                node_colors.append('orange')
                node_sizes.append(200)
            else:
                continue
        
        # Draw the graph
        nx.draw_networkx_nodes(self.graph, pos, 
                            node_shape='o',
                             node_color=node_colors, 
                             node_size=node_sizes,
                             alpha=0.8)
        
        nx.draw_networkx_edges(self.graph, pos, 
                             edge_color='gray', 
                             arrowstyle='->',
                             arrows=True,
                             node_shape='o',
                             alpha=0.5,
                             width=1)
        
        labels = {node: self.graph.nodes[node].get('label', node[:10]) 
                 for node in self.graph.nodes}
        nx.draw_networkx_labels(self.graph, pos, labels, font_size=8)
        
        plt.title("Book Ontology Graph", fontsize=16, fontweight='bold')
        plt.axis('off')
        plt.tight_layout()
        
        # Save the graph
        plt.savefig('ontology_graph_basic.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        return self.graph