import logging
from pydantic import BaseModel
from onto.OntologyBuilder import OntologyBuilder
from onto.OntologyService import OntologyService
from KaggleData.ProcessData import ProcessData

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
		
		onto_service = OntologyService(onto_builder.onto)

		onto_service.get_all_books()


	except Exception as e:
		logger.error(f"Exepction thrown for reason :{e}")


if __name__ == "__main__":
	main()