from owlready2 import *
from Models.Books import ontology_classification
import pandas as pd
from onto.WorldManager import WorldManager
from typing import Optional
from pathlib import Path
import random
import string

import logging



logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


"""
	Custom class to handle building the ontology
	Params: Requires a path to write to.
"""
class OntologyBuilder:
	def __init__(self, path: Optional[str] = None ):
		self.path = path
		self.world = WorldManager.reset_world()
		self.onto = None

	""" Will be used conditionally to either create or use the current onto on file"""
	def does_onto_exist(self)->bool:
		return bool(self.onto)

	""" Generate a random string for id usage"""
	def generate_random_string (self,length)->str:
		chars = string.ascii_letters + string.digits
		return ''.join(random.choice(chars) for i in range(length))
	
	def create_book_id(self, isbn: str) -> str:
		"""
		Create a consistent, XML-safe ID from ISBN.
		The ID is deterministic (same ISBN = same ID)
		and can be used across all data sources.
		"""
		if pd.isna(isbn):
			return None
		
		isbn_str = str(isbn).strip()
		
		# Option 1: Base64 encoding (most compact)
		import base64
		encoded = base64.b64encode(isbn_str.encode()).decode()
		# Replace base64 chars that might cause issues
		encoded = encoded.replace('+', '-').replace('/', '_').replace('=', '')
		return f"book_{encoded}"
	
	""" Load initially the data from books csv"""		
	def create_ontology_from_book_data(self, books: Optional[pd.DataFrame] = None)->bool:
		try:
			""" Create ontology from books.csv """
			if not self.onto:
				self.onto = ontology_classification(self.path)
				logger.error("unable to get ontology model")

			author_cache = {}
			publisher_cache = {}

			with self.onto:
				logger.info("Ontology model found")
				if books.empty:
					return False
				
				for idx, row in books.iterrows():
					try:
						isbn = row.get("ISBN")
						if not pd.notna(isbn):
							continue
						book_id = self.create_book_id(isbn)
						book = self.onto.Book(book_id)
						book.isbn = [str(isbn)]
						if pd.notna(row.get("Book-Title")):
							book.book_title = [str(row.get("Book-Title"))]
						year_raw = row.get("Year-Of-Publication")
						if pd.notna(year_raw):
							book.publication_year = [int(float(year_raw))]
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
			logger.info(f"[ONTO BUILDER] completed create_ontology_from_book_data()")
			return True
		except Exception as e:
			logger.error(f"[create_ontology_from_book_data] error found: {e}")
			raise
	

	""" Load all data into Book, Review, User onto and create the linkages"""
	def load_ratings_data(self, ratings: Optional[pd.DataFrame] = None)->bool:
		try:
			""" Create ontology from books.csv """
			if not self.onto:
				self.onto = ontology_classification(self.path)
				logger.error("unable to get ontology model")
			with self.onto:
				logger.info("Ontology model found")
				if ratings.empty:
					return False
				for idx, row in ratings.iterrows():
					try:
						isbn = row.get("ISBN")
						review_user_id = row.get("User-ID")
						rating = row.get("Book-Rating")
						if pd.notna(isbn) and pd.notna(review_user_id) and pd.notna(rating):
							book_id = self.create_book_id(isbn)
							random_str_id = self.generate_random_string(6)
							review_id = f'review_{random_str_id}-{review_user_id}'
							book = self.onto.Book(str(book_id)) 
							user = self.onto.User(f'user_{review_user_id}')
							review = self.onto.Review(review_id)
							review.rating = [int(rating)]
							review.review_user_id = [str(review_user_id)]
							review.reviewed_by = [user]
							# Since there is a posiblity of habing variouse user reviewing the same book
							# Need to check if there are any review present to append and set equal to.
							if book.has_review and len(book.has_review) > 0:
								current_list = list(book.has_review)
								current_list.append(review)
								book.has_review = current_list
							else:
								book.has_review = [review]
					except Exception as e:
						logger.info(f"[ERROR] unable to add review {idx}: {e}")
			self.save_ontology()
			logger.info(f"[ONTO BUILDER] completed load_ratings_data()")
			return True
		except Exception as e:
			logger.info(f"[load_ratings_data] Error from load_ratings_data: {e}")
			return False

	""" Load users.csv data into User, Review"""
	def load_user_data(self, users: Optional[pd.DataFrame] =None) -> bool:
		try:
			if not self.onto:
				self.onto = ontology_classification(self.path)
				logger.error("unable to get ontology model")

			with self.onto:
				for idx, row in users.iterrows():
					try:
						user_id = row.get("User-ID")
						if pd.notna(user_id):
							if hasattr(self.onto, f'user_{user_id}'):
								user = self.onto.User(str(f'user_{user_id}'))
								if not getattr(user, 'user_age') or not user.user_age:
									age = row.get("Age")
									if pd.notna(age):
										user.user_age = [int(age)]
								if not getattr(user, 'user_location') or not user.user_location:
									location = row.get("Location")
									if pd.notna(location):
										user.user_location = [str(location)]

					except Exception as e:
						logger.info(f"[load_user_data] unable to add user data on {idx}: {e}")
			self.save_ontology()
			logger.info(f"[ONTO BUILDER] completed load_user_data()")
			return True
		except Exception as e:
			logger.error(f"[ERROR] unable to load_user_data: {e}")
			return False
		
	def load_ontology_from_dir(self) -> bool:
		"""Get existing ontology or create a new one"""
		try:
			# Try to load existing ontology
			if hasattr(self, 'onto') and self.onto is not None:
				logger.info("[ONTO BUILDER] Using already loaded ontology")
				return True
			
			pt = Path(__file__).parent.parent
			# Try to load from file
			ontology_path = pt / "books.owl"
			logger.info(f"[ONTO BUILDER] current path {ontology_path} and type {type(ontology_path)}")
			
			if ontology_path.exists():
				# Load the ontology
				file_uri = ontology_path.as_uri() 
				self.onto = get_ontology(file_uri).load()
				
				logger.info(f"[ONTO BUILDER] WORLD WHEN LOADING FROM DIR {id(self.onto.world)}")
				logger.info(f"[ONTO BUILDER] Ontology base IRI: {self.onto.base_iri}")
				logger.info(f"[ONTO BUILDER] Ontology name: {self.onto.name}")
				
				if self.onto is None:
					logger.error("[ONTO BUILDER] onto did not load")
					return False
				
				# List all classes to see what we have
				all_classes = list(self.onto.classes())
				logger.info(f"[ONTO BUILDER] Found {len(all_classes)} classes")
				
				# Find the Book class - it might be in a different namespace
				book_class = None
				for cls in all_classes:
					if cls.name == "Book":
						book_class = cls
						break
				
				if book_class:
					logger.info(f"[ONTO BUILDER] Found Book class: {book_class}")
					try:
						book_count = len(list(book_class.instances()))
						logger.info(f"[ONTO BUILDER] Found {book_count} books")
					except Exception as e:
						logger.warning(f"[ONTO BUILDER] Could not access Book instances: {e}")
						return False
				else:
					logger.warning("[ONTO BUILDER] No 'Book' class found in ontology")
					# List available classes for debugging
					logger.info(f"[ONTO BUILDER] Available classes: {[c.name for c in all_classes]}")
					return False
				
				return True
			else:
				logger.warning(f"[ONTO BUILDER] Ontology file does not exist at {ontology_path}")
				return False
				
		except Exception as e:
			logger.error(f"[load_ontology_from_dir] Failed to load ontology: {e}")
			import traceback
			logger.error(traceback.format_exc())
			return False


	def ontology_stats(self) ->dict:
		try:
			stats = { 'books': 0, 'authors': 0, 'publishers': 0, 'reviews': 0}
			if self.onto is None:
				return None
			
			# Find classes by name instead of assuming they're direct attributes
			for cls in self.onto.classes():
				if cls.name == 'Book':
					stats["books"] = len(list(cls.instances()))
				elif cls.name == 'Author':
					stats["authors"] = len(list(cls.instances()))
				elif cls.name == 'Publisher':
					stats["publishers"] = len(list(cls.instances()))
				elif cls.name == 'Review':
					stats["reviews"] = len(list(cls.instances()))
			
			return stats
		except Exception as e:
			logger.error(f"[ontology_stats] Error raised: {e}")
			return None

	def save_ontology(self):
		"""Save ontology to file"""
		if self.onto:
			self.onto.save(file=str(self.path), format="rdfxml")
			logger.info(f"Ontology saved to: {self.path}")





