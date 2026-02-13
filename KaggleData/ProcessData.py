from owlready2 import *
import pandas as pd
from typing import Optional
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProcessData:
    def __init__(self):
        logger.info("Invoked ProcessData class, reading all data from file dir")
    
    def load_books_data(self) ->pd.DataFrame:
        """ Load data from kaggle_data path """
        path = Path(__file__).parent / str("./books.csv")
        logger.info("Checking path to open csv", path)
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            for encoding in encodings:
                try:
                    df = pd.read_csv(path, sep= ';', encoding=encoding, on_bad_lines='skip')
                    logger.info(f"Successfully loaded with {encoding} encoding")
                    return df
                except UnicodeDecodeError:
                    continue
                    
            # If all encodings fail, try without specifying encoding
            df = pd.read_csv(path, on_bad_lines='skip', engine='python')
            return df
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            return None

    def load_ratings_data(self) ->pd.DataFrame:
        """ Load data from kaggle_data path """
        try:
            path = Path(__file__).parent / str("./ratings.csv")
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            for encoding in encodings:
                try:
                    df = pd.read_csv(path, sep= ';', encoding=encoding, on_bad_lines='skip')
                    logger.info(f"Successfully loaded ratings with {encoding} encoding")
                    return df
                except UnicodeDecodeError:
                    continue
                    
            # If all encodings fail, try without specifying encoding
            df = pd.read_csv(path, on_bad_lines='skip', engine='python')
            return df 
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            return None

    def load_users_data(self) ->pd.DataFrame:
        """ Load data from kaggle_data path """
        path = Path(__file__).parent / str("./users.csv")
        logger.info("Checking path to open csv", path)
        try:
            # Try different encodings
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            for encoding in encodings:
                try:
                    df = pd.read_csv(path, sep= ';',encoding=encoding, on_bad_lines='skip')
                    logger.info(f"Successfully loaded with {encoding} encoding")
                    return df
                except UnicodeDecodeError:
                    continue
                    
            # If all encodings fail, try without specifying encoding
            df = pd.read_csv(path, on_bad_lines='skip', engine='python')
            return df
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            return None