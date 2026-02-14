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
	viz = OntologyVisualizer(onto)
	query_tool = OntologyQuery(onto)
	service = OntologyService(onto, query_tool)
	while True:
		print("\n" + "="*60)
		print("ONTOLOGY INTERACTIVE SHELL")
		print("="*60)
		print("\n1. View ontology graph, will be downloaded to path.")
		print("2. Natural Language Query")
		print("0. Exit")
		
		choice = input("\n Enter your choice (0-2): ").strip()
		
		if choice == '0':
			print("\nGoodbye!")
			break
		elif choice == '1':
			""" Visualize the model"""
			max_nodes = input("\n Max number of nodes? ").strip()
			viz.interactive_visualize(max_nodes=int(max_nodes))
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

		if onto_builder.load_ontology_from_dir():
			logger.info(f"Ontology stats: {onto_builder.ontology_stats()}")
			logger.info(f"[MAIN] Ontology WORLD: {id(onto_builder.onto.world)}")
			interactive_menu(onto_builder.onto)
			return
		else:
			return
		""" Create data into ontology, sample size of 200 just for performance """
		is_created = onto_builder.create_ontology_from_book_data(books)
		if not is_created:
			logger.info(f"[MAIN]create_ontology_from_book_data")
		
		ratings = data.load_ratings_data()
		is_ratings_added = onto_builder.load_ratings_data(ratings)
		if not is_ratings_added:
			logger.info(f"[MAIN] Unable to process ratings.csv")

		users = data.load_users_data()
		is_user_added = onto_builder.load_user_data(users)
		if not is_user_added:
			logger.info(f"[MAIN] Unable to process users.csv")

		logger.info(f"Ontology stats: {onto_builder.ontology_stats()}")
		logger.info(f"[MAIN] Ontology WORLD: {id(onto_builder.onto.world)}")
		interactive_menu(onto_builder.onto)
	
	except Exception as e:
		logger.error(f"Exepction thrown for reason :{e}")


if __name__ == "__main__":
	main()