import logging
from pathlib import Path
from onto.OntologyBuilder import OntologyBuilder
from onto.OntologyService import OntologyService
from onto.OntologyQuery import OntologyQuery
from onto.OntologyVisualizer import OntologyVisualizer
from KaggleData.ProcessData import ProcessData

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

path = Path(__file__).parent

def interactive_menu(onto):
	"""Main interactive menu"""
	if onto is None:
		logger.error("[MAIN] ontology not loaded ?")
	if not hasattr(onto, 'Book'):
		logger.info("\n❌ Ontology loaded but missing 'Book' class.")
		logger.info(f"   Available classes: {[c for c in dir(onto) if not c.startswith('_') and c[0].isupper()]}")
	viz = OntologyVisualizer(onto)
	query_tool = OntologyQuery(onto)
	service = OntologyService(onto, query_tool)
	while True:
		print("\n" + "="*60)
		print("ONTOLOGY INTERACTIVE SHELL")
		print("="*60)
		print("\n1. View ontology graph")
		print("2. Natural Language Query")
		print("0. Exit")
		
		choice = input("\n Enter your choice (0-2): ").strip()
		
		if choice == '0':
			print("\nGoodbye!")
			break
		elif choice == '1':
			""" Visualize the model"""
			viz.create_basic_graph(max_nodes=50)
			viz.visualize()
		elif choice == '2':
			""" Query-tool for llm models """
			""" Service layer to pull and use data from onto """
			nl = input("\n Enter: ").strip()
			service.query_with_natural_language(nl)
		else:
			print("❌ Invalid choice. Please try again.")


""" Lets create a book recomendation system using ontology, and process request via natural language """
def main():
	try:
		""" Parse all the data in kaggle folder"""
		data = ProcessData()
		books = data.load_books_data()
		
		""" If ontology exist start the interactive window. """
		onto_builder = OntologyBuilder(path="books.owl")
		
		""" Create data into ontology, sample size of 200 just for performance """
		is_created = onto_builder.create_ontology_from_book_data(books.head(1000))
		if not is_created:
			logger.info(f"[MAIN]create_ontology_from_book_data")
		
		ratings = data.load_ratings_data()
		is_ratings_added = onto_builder.load_ratings_data(ratings.head(1000))
		if not is_ratings_added:
			logger.info(f"[MAIN] Unable to process ratings.csv")

		users = data.load_users_data()
		is_user_added = onto_builder.load_user_data(users.head(1000))
		if not is_user_added:
			logger.info(f"[MAIN] Unable to process users.csv")

		interactive_menu(onto_builder.onto)
	
	except Exception as e:
		logger.error(f"Exepction thrown for reason :{e}")


if __name__ == "__main__":
	main()