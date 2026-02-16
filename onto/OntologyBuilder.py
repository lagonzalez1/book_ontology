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
	def __init__(self, uri: Optional[str] = None ):
		self.uri = uri
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
				self.onto = ontology_classification(self.uri)

			author_cache = {}
			publisher_cache = {}

			with self.onto:
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
				return False
			
			with self.onto:
				if ratings.empty:
					return False
				user_cache = {}
				for idx, row in ratings.iterrows():
					try:
						isbn = row.get("ISBN")
						review_user_id = row.get("User-ID")
						rating = row.get("Book-Rating")
						if pd.notna(isbn) and pd.notna(review_user_id) and pd.notna(rating):
							book_id = self.create_book_id(isbn)
							random_str_id = self.generate_random_string(6)
							review_id = f'review_{random_str_id}-{review_user_id}'
							user = self.onto.User(f'user_{review_user_id}')
							
							if review_user_id not in user_cache:
								user_cache[review_user_id] = user
							
							book = self.onto.Book(str(book_id)) 
							
							review = self.onto.Review(review_id)
							review.rating = [int(rating)]
							review.review_user_id = [str(review_user_id)]
							review.reviewed_by = [user_cache[review_user_id]]

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
				return False

			with self.onto:
				for idx, row in users.iterrows():
					try:
						user_id = row.get("User-ID")
						if pd.notna(user_id):
							user = self.onto.User(str(f'user_{user_id}'))
							age = row.get("Age")
							if pd.notna(age):
								user.user_age = [int(age)]
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
			
			path_to_owl = Path(__file__).parent.parent
			file = path_to_owl / "books.owl"

			try:
				uri = get_ontology(str(file)).load()
				self.onto = get_ontology(uri.base_iri)
				return True
			except Exception as e:
				logger.error(f"[ONTO BUILDER] error loading onto from {self.uri}")
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
			pt = Path(__file__).parent.parent
			save_path = pt / "books.owl"
			self.onto.save(file=str(save_path), format="rdfxml")
			logger.info(f"Ontology saved to: {self.uri}")




