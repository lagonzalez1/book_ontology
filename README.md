# Intro
A sophisticated book management system that combines OWL ontologies with Large Language Models (LLMs) to enable natural language queries over structured book data.
Short for book recommendation system using natural language.

# Features
Ontology-Based Data Model: Structured representation of books, authors, publishers, genres, and relationships

Natural Language Interface: Ask questions in plain English like "Find historical fiction books about Rome"

Intelligent Query Processing: LLM-powered translation of natural language to structured queries

SPARQL Integration: Efficient querying using semantic web standards

Data Integration: Import from CSV/Excel datasets with automatic entity resolution

Type Safety: Pydantic validation for all query intents and responses

# Prerequisites

1. Python 3.8+
2. Google Gemini API key

# Getting Started

1. git clone this repo
2. create venv (recomended)
3. pip install -r requirements.txt
4. TBD Make file on the way


# Architecture
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Natural       │    │      LLM        │    │   Query         │
│   Language      │────▶   (Gemini)      │────▶   Intent        │
│   Query         │    │                 │    │   Parser        │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                            │
                                                            ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Results       │    │     SPARQL      │    │   OWL           │
│   Formatter     │◀───│   Query         │◀───│   Ontology      │
│                 │    │   Generator     │    │   (OWLReady2)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘


# To do
1. Complete the ontology to include all csv file attributes.
2. Linking to the World (DBpedia/Wikidata)
    - Instead of just a name string
    - jk_rowling = self.onto.Author("author_jk_rowling")
    - jk_rowling.author_name = ["J.K. Rowling"]

    - Add a 'seeAlso' or 'sameAs' link to the global ID
    - jk_rowling.comment = ["https://dbpedia.org/resource/J._K._Rowling"]
    - ThenThe "Simple" Federated Query

3. Accept user input