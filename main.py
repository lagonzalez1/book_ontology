import logging
from pydantic import BaseModel
from onto.OntologyBuilder import OntologyBuilder
from onto.OntologyService import OntologyService
from onto.OntologyQuery import OntologyQuery
from KaggleData.ProcessData import ProcessData
from llm.GeminiModel import GeminiModel

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


"""
	Lets create a book recomendation system using ontology
	
"""



def main():
	try:
		""" Parse all the data in kaggle folder"""
		data = ProcessData()
		books = data.load_books_data()
		""" Build the ontology Books owl file """
		onto_builder = OntologyBuilder(path="books.owl")
		""" Create data into ontology, sample size of 200 just for performance """
		created = onto_builder.create_ontology_from_book_data(books.head(50))
		if not created:
			logger.info(f"create_ontology_from_book_data")
		""" Query-tool for llm models """
		query_tool = OntologyQuery(onto_builder.onto)
		""" Service layer to pull and use data from onto """

		service = OntologyService(onto_builder.onto, query_tool)
		logger.info(f"OntologyBuilder world: {id(onto_builder.onto.world)}")
		logger.info(f"OntologyQuery world: {id(query_tool.world.world)}")
		logger.info(f"OntoogyQueryService world: {id(service.world)}")
		logger.info(f"OntologyQuery uri: {(onto_builder.onto.base_iri)}")
		## logger.info(f"TEST {service.get_all_books()}")
		
		service.query_with_natural_language()
	
	except Exception as e:
		logger.error(f"Exepction thrown for reason :{e}")


if __name__ == "__main__":
	main()