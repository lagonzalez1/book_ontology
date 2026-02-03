from owlready2 import *
from Models.Books import ontology_classification
from onto.OntologyBuilder import OntologyBuilder
from onto.WorldManager import WorldManager
import pandas as pd
from typing import Optional
from pathlib import Path
import logging

pt = Path(__file__).parent.parent

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



class OntologyQuery:
    """ Ontology query tool for llm """
    def __init__(self, onto: Optional[any]):
        self.onto = onto
        self.world = WorldManager.get_world()
    
    def _get_class_comment(self, cls) -> str:
        """Safely get class comment"""
        try:
            if hasattr(cls, 'comment'):
                comments = cls.comment
                if isinstance(comments, list) and len(comments) > 0:
                    return comments[0]
                elif isinstance(comments, str):
                    return comments
        except:
            pass
        return ""
    
    def _build_sparql_from_intent(self, query_intent: dict) -> str:
        """Convert structured query intent to SPARQL"""
        
        query_type = query_intent.get("query_type", "search_books")
        
        if query_type == "search_books":
            return self._build_book_search_sparql(query_intent)
        ## will create more query_types
        

    def _build_book_search_sparql(self, query_intent: dict) -> str:
        """Build SPARQL query extracting values from Enum objects"""
        
        patterns = {
            "type": "?book a onto:Book .",
            "title": "?book onto:book_title ?title .",
            "author": "?book onto:has_author ?author . ?author onto:author_name ?author_name ."
        }
        
        filters = []
        select_vars = ["?book", "?title", "?author_name"]
        
        # 1. Helper to extract string from Enum or keep as is
        get_val = lambda x: x.value if hasattr(x, 'value') else x

        # 2. Process Filters
        for filter_obj in query_intent.get("filters", []):
            f_type = get_val(filter_obj.get("type"))
            value = filter_obj.get("value")
            operator = get_val(filter_obj.get("operator", "="))
            
            if f_type == "publication_year":
                patterns["year"] = "?book onto:publication_year ?year ."
                filters.append(f"FILTER(?year {operator} {value})")
                
            elif f_type == "author":
                filters.append(f'FILTER(CONTAINS(LCASE(?author_name), LCASE("{value}")))')
                
            elif f_type == "page_count":
                patterns["pages"] = "?book onto:page_count ?pages ."
                filters.append(f"FILTER(?pages {operator} {value})")

            elif f_type == "genre":
                patterns["genre"] = "?book onto:has_genre ?genre . ?genre onto:genre_name ?g_name ."
                filters.append(f'FILTER(LCASE(?g_name) = LCASE("{value}"))')

        # 3. Handle Sorting
        sort_by = get_val(query_intent.get("sort_by", "none"))
        sort_order = get_val(query_intent.get("sort_order", "asc")).upper() # ASC or DESC
        order_by = ""
        
        if sort_by != "none":
            # Map sort_by Enum values to SPARQL variables
            sort_map = {
                "publication_year": "?year",
                "page_count": "?pages",
                "title": "?title",
                "author_name": "?author_name"
            }
            if sort_by in sort_map:
                target_var = sort_map[sort_by]
                order_by = f"ORDER BY {sort_order}({target_var})"
                # Ensure the variable is in SELECT if we're sorting by it
                if target_var not in select_vars:
                    select_vars.append(target_var)

        # 4. Construct Final Query
        where_clause = "\n        ".join(patterns.values())
        if filters:
            where_clause += "\n        " + "\n        ".join(filters)
        
        sparql = f"""
        PREFIX onto: <{self.onto.base_iri}>
        SELECT DISTINCT {" ".join(select_vars)} WHERE {{
            {where_clause}
        }}
        {order_by}
        LIMIT {query_intent.get("limit", 20)}
        """
        return sparql
    
    def _get_property_domain(self, prop) -> str:
        """Safely get property domain name"""
        try:
            if hasattr(prop, 'domain') and prop.domain:
                if isinstance(prop.domain, list):
                    for domain_item in prop.domain:
                        if hasattr(domain_item, 'name'):
                            return domain_item.name
                elif hasattr(prop.domain, 'name'):
                    return prop.domain.name
        except:
            pass
        return "Thing"
    
    def _get_property_range(self, prop) -> str:
        """Safely get property range"""
        try:
            if hasattr(prop, 'range') and prop.range:
                if isinstance(prop.range, list):
                    for range_item in prop.range:
                        if hasattr(range_item, 'name'):
                            return range_item.name
                        elif isinstance(range_item, type):
                            return range_item.__name__
                elif hasattr(prop.range, 'name'):
                    return prop.range.name
                elif isinstance(prop.range, type):
                    return prop.range.__name__
        except:
            pass
        return "Thing" if prop in self.onto.object_properties() else "string"
    
    def _execute_sparql(self, sparql_query: str) -> list:
        """Execute SPARQL query against the ontology"""
        try:
            ## from owlready2 import default_world
            
            # Execute the query
            results = list(self.world.sparql(sparql_query, error_on_undefined_entities=False))
            
            # Convert to list of dictionaries for easier handling
            formatted_results = []
            for row in results:
                result_dict = {}
                for i, var in enumerate(sparql_query.split("SELECT")[1].split("WHERE")[0].strip().split()):
                    if var.startswith("?"):
                        var_name = var[1:]
                        if i < len(row):
                            result_dict[var_name] = str(row[i])
                formatted_results.append(result_dict)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"[_execute_sparql] error: {e}") 
            logger.debug(f"Query was: {sparql_query}")
            return []

    def get_ontology_schema_for_llm(self) -> str:
        """Get a clean, safe schema description for LLM prompts"""
        try:
            if not self.onto:
                return "No ontology loaded."
            
            schema_info = []
            
            # 1. Classes
            schema_info.append("CLASSES:")
            classes_added = set()
            for cls in self.onto.classes():
                if (not cls.name.startswith('owl.') and 
                    cls.name != 'Thing' and 
                    cls.name not in classes_added):
                    comment = self._get_class_comment(cls)
                    schema_info.append(f"  - {cls.name}: {comment}")
                    classes_added.add(cls.name)
            
            # 2. Object Properties (relationships)
            schema_info.append("\nRELATIONSHIPS (Object Properties):")
            for prop in self.onto.object_properties():
                if not prop.name.startswith('owl.'):
                    domain = self._get_property_domain(prop)
                    range_cls = self._get_property_range(prop)
                    comment = self._get_class_comment(prop)
                    schema_info.append(f"  - {prop.name}: ({domain} → {range_cls}) {comment}")
            
            # 3. Data Properties (attributes)
            schema_info.append("\nATTRIBUTES (Data Properties):")
            for prop in self.onto.data_properties():
                if not prop.name.startswith('owl.'):
                    domain = self._get_property_domain(prop)
                    range_type = self._get_property_range(prop)
                    schema_info.append(f"  - {prop.name}: ({domain} → {range_type})")
            
            # 4. Genre hierarchy if exists
            if hasattr(self.onto, "Genre"):
                schema_info.append("\nGENRE HIERARCHY:")
                try:
                    # Get top-level genres first
                    top_genres = [g for g in self.onto.Genre.subclasses() 
                                 if not g.name.startswith('owl.')]
                    
                    def add_genre_with_indent(genre, indent=2):
                        schema_info.append(f"{' ' * indent}- {genre.name}")
                        # Get direct subclasses
                        for sub in genre.subclasses():
                            if not sub.name.startswith('owl.'):
                                add_genre_with_indent(sub, indent + 2)
                    
                    for genre in top_genres:
                        add_genre_with_indent(genre)
                        
                except Exception as e:
                    logger.debug(f"Could not build genre hierarchy: {e}")
                    schema_info.append("  (Available genres will be discovered during query)")
            
            return "\n".join(schema_info)
            
        except Exception as e:
            logger.error(f"[get_ontology_schema_for_llm] error: {e}")
            return f"Error: {str(e)}"