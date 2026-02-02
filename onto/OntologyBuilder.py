from owlready2 import *
from Models.Books import ontology_classification
import pandas as pd
from typing import Optional
from pathlib import Path
import logging



pt = Path(__file__).parent.parent

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OntologyBuilder:
	def __init__(self, path: Optional[str] = None ):
		self.path = path
		self.onto = None
		self.world = World()
		
	def create_ontology_from_book_data(self, books: Optional[pd.DataFrame] = None)->bool:
		""" Create ontology from books.csv """
		self.onto = ontology_classification(self.path)

		if not self.onto:
			logger.error("unable to get ontology model")
			return False

		author_cache = {}
		publisher_cache = {}

		with self.onto:
			logger.info("Ontology model found")
			if books.empty:
				return False
			
			for idx, row in books.iterrows():
				try:
					book_id = f"book_{idx}"
					## Create the book 
					book = self.onto.Book(book_id)
					if pd.notna(row.get("Book-Title")):
						book.book_title = [row.get("Book-Title")]
					if pd.notna(row.get("ISBN")):
						book.isbn = [row.get("ISBN")]
					if pd.notna(row.get("Year-Of-Publication")):
						book.publication_year = [row.get("Year-Of-Publication")]
					if pd.notna(row.get("Publisher")):
						pub_name = str(row.get("Publisher")).strip()
						if pub_name:
							if pub_name not in publisher_cache:
								## Create a pub_id to 
								pub_id = f"publisher_{len(publisher_cache)}"
								publisher = self.onto.Publisher(pub_id)
								publisher.publisher_name = [pub_name]
								publisher_cache[pub_name] = publisher

							book.has_publisher = [publisher_cache[pub_name]]

					if pd.notna(row.get("Book-Author")):
						auth_name = str(row.get("Book-Author")).strip()
						if auth_name:
							if auth_name not in author_cache:
								auth_id = f"author_{len(author_cache)}"
								author = self.onto.Author(auth_id)
								author.author_name = [auth_name]
								author_cache[auth_name] = author
							
							book.has_author = [author_cache[auth_name]]
				except Exception as e:
					logger.warning(f"Error adding book {idx}: {e}")
					continue

		self.save_ontology()

		return True
	


	def load_ontology_from_dir(self):
		""" Get existing ontology or create a new one"""
		try:
			# Try to load existing ontology
			if hasattr(self, 'onto') and self.onto is not None:
				return self.onto
				
			# Try to load from file
			if hasattr(self, 'ontology_file'):
				return get_ontology(f"{pt}/books").load()
						
		except Exception as e:
			logger.error(f"Failed to get/create ontology: {e}")
			return None


	def save_ontology(self):
		"""Save ontology to file"""
		if self.onto:
			self.onto.save(file=str(self.path), format="rdfxml")
			logger.info(f"Ontology saved to: {self.path}")





