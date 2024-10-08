from typing import Optional
from wildlife_tracker.habitat_management.habitat import Habitat

class MigrationPath:
    def __init__(self, 
                 path_id: int,
                 species: str, 
                 start_location: Habitat,
                 destination: Habitat) -> None:
        self.path_id = path_id
        self.species = species
        self.start_location = start_location
        self.destination = destination


    def get_migration_path_details(self) -> dict:
        pass

    def update_migration_path_details(self, **kwargs) -> None:
        pass

    pass