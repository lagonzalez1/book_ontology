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
        # Add Review as linkaes to Books

    def visualize(self, figsize=(15, 10)):
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