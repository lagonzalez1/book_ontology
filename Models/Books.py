import logging
from owlready2 import *
from typing import List, Optional, Dict, Any
import random
from datetime import datetime


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ontology_classification(url: str):
	onto = get_ontology(url)

	with onto:
		""" Books model for owl ontology, define the init objects """
		class Book(Thing):
			""" Represents a book """
			pass

		class Author(Thing):
			""" Represent an book author"""
			pass

		class Publisher(Thing):
			""" Represent a publisher org """
			pass

		class Genre(Thing):
			"""Represents a book genre"""
			pass
		            
		class User(Thing):
			"""Represents a user of the system"""
			pass

		class Review(Thing):
			"""Represents a book review"""
			pass


		""" Define Object properties and characteristics"""
		class has_author(ObjectProperty):
			domain = [Book]
			range = [Author]
		
		class has_genre(ObjectProperty):
			domain = [Book]
			range = [Genre]

		class has_review(ObjectProperty):
			domain = [Book]
			range = [Review]

		class written_by(ObjectProperty):
			domain = [Author]
			range = [Book]
			inverse_property = has_author

		class reviewed_by(ObjectProperty):
			domain = [Review]
			range = [User]

		class has_publisher(ObjectProperty):
			domain = [Book]
			range = [Publisher]

		class similar_to(ObjectProperty):
			domain = [Book]
			range = [Book]
			simmetric = True

		class recommends(ObjectProperty):
			domain = [Book]
			range = [Book]


		""" Set the propery data values """
		class author_name(DataProperty):
			domain = [Author]
			range = [str]

		class book_title(DataProperty):
			domain = [Book]
			range = [str]

		class isbn(DataProperty):
			domain = [Book]
			range = [str]

		class publisher_name(DataProperty):
			domain = [Publisher]
			range = [str]

		class publication_year(DataProperty):
			domain = [Book]
			range = [int]

		class rating(DataProperty):
			domain = [Review]
			range = [int]

		class rating_user_id(DataProperty):
			domain = [Review]
			range = [int]

		class review_text(DataProperty):
			domain = [Review]
			range = [str]

		class review_user_id(DataProperty):
			domain = [Review]
			range = [int]

		class user_age(DataProperty):
			domain = [User]
			range = [int]

		class user_location(DataProperty):
			domain = [User]
			range = [str]

		class genre_name(DataProperty):
			domain = [Genre]
			range = [str]
        
		class user_name(DataProperty):
			domain = [User]
			range = [str]
        
		class preferred_genre(ObjectProperty):
			domain = [User]
			range = [Genre]

	return onto
