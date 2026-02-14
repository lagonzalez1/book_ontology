from owlready2 import *
import pandas as pd
from typing import Optional
from pathlib import Path
import logging
from Prompts.Builder import PromptBuilder, PromptConfig
from llm.GeminiModel import GeminiModel
from llm.validation import QueryIntent
from onto.WorldManager import WorldManager

pt = Path(__file__).parent.parent

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OntologyService:
    """ Call ontology service to query, retrive, ... books. """
    def __init__(self, onto=None, ontology_query_tool: Optional[any] = None):
        self.onto = onto
        self.ontology_query_tool = ontology_query_tool
        self.prompt_builder = PromptBuilder()
        self.validator_class = QueryIntent
        self.world = WorldManager.get_world()
    
    def query_with_natural_language(self, user_quesion: Optional[str] = "Find books with a publication years between 2000 and 2015"):
        try:
            if not self.ontology_query_tool:
                raise Exception("Query tool not loaded, required for nlp.")
        
            ## logger.info(f"NLP prompt: {self.ontology_query_tool.get_ontology_schema_for_llm()}")
            query_prompt = self.ontology_query_tool.get_ontology_schema_for_llm()

            prompt_config = PromptConfig(
                template_name="BooksTemplate",
                model="gemini-2.5-flash",
                system_prompt=query_prompt,
                variables={
                    "ontology_schema": query_prompt,
                    "user_question": user_quesion,
                },
                max_tokens=10000,
                temperature=0.2,
            )
            prompt_data = self.prompt_builder.build(prompt_config)

            model = GeminiModel(self.validator_class, prompt_data)
            llm_response = model._invoke_model()

            logger.info(f"Model invoked results: {llm_response}")

            query = self.ontology_query_tool._build_sparql_from_intent(llm_response)

            logger.info(f"_build_sparql_from_intent results: {query}")

            
            result = self.ontology_query_tool._execute_sparql(query)

            logger.info(f"Result:  {result}")

        except Exception as e:
            logger.error(f"[query_with_natural_language] error: {e}") 
            raise 
        

    def _extract_book_info(self, book) -> Optional[dict]:
        """Extract information from a book instance"""
        info = {
            'id': book.name,
            'title': None,
            'author': None,
            'publisher': None,
            'year': None,
            'isbn': None
        }
        
        # Get title
        if hasattr(book, 'book_title') and book.book_title:
            info['title'] = book.book_title[0]
        elif hasattr(book, 'title') and book.title:
            info['title'] = book.title[0]
        
        # Get author
        if hasattr(book, 'has_author') and book.has_author:
            author = book.has_author[0]
            if hasattr(author, 'author_name') and author.author_name:
                info['author'] = author.author_name[0]
        
        # Get publisher
        if hasattr(book, 'has_publisher') and book.has_publisher:
            publisher = book.has_publisher[0]
            if hasattr(publisher, 'publisher_name') and publisher.publisher_name:
                info['publisher'] = publisher.publisher_name[0]
        
        # Get publication year
        if hasattr(book, 'publication_year') and book.publication_year:
            info['year'] = book.publication_year[0]
        
        # Get ISBN
        if hasattr(book, 'isbn') and book.isbn:
            info['isbn'] = book.isbn[0]
        
        return info

    def get_all_books(self, limit: int = 10) ->list[dict]:
        if not self.onto or not hasattr(self.onto, "Book"):
            logger.info("Ontology has not been loaded")
            return []
        books = []
        for i, book in enumerate(list(self.onto.Book.instances())[:limit]):
            book_info = self._extract_book_info(book)
            books.append(book_info)
            
            # Print first few
            if i < 5:
                print(f"{i+1}. {book_info['title']}")
                if book_info['author']:
                    print(f"   Author: {book_info['author']}")
                if book_info['publisher']:
                    print(f"   Publisher: {book_info['publisher']}")
                if book_info['year']:
                    print(f"   Year: {book_info['year']}")
                print()
        
        return books


