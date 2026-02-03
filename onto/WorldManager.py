# world_manager.py
from owlready2 import World, get_ontology, default_world
import logging

logger = logging.getLogger(__name__)

class WorldManager:
    """Singleton manager for OWLReady2 World instance"""
    _instance = None
    _world = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    @classmethod
    def get_world(cls, reset: bool = False) -> World:
        """Get the shared world instance"""
        if reset or cls._world is None:
            cls.reset_world()
        return cls._world
    
    @classmethod
    def reset_world(cls):
        """Completely reset the world"""
        logger.info("Resetting OWLReady2 world")
        if cls._world is not None:
            try:
                cls._world.close()  # Clean up if possible
            except:
                pass
        
        # Create fresh world
        cls._world = default_world
        
        # Set as default globally
        cls._world.save()
        
        logger.info(f"New world created: {id(cls._world)}")
        return cls._world
    
    @classmethod
    def load_ontology(cls, filepath: str):
        """Load ontology into the shared world"""
        world = cls.get_world()
        onto = get_ontology(f"file://{filepath}")
        onto.load(world=world)
        return onto