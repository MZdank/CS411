from typing import Any, Optional
from wildlife_tracker.habitat_management.habitat import Habitat
from wildlife_tracker.migration_tracking.migration_path import MigrationPath

class Migration:
    def __init__ (self, 
                  migration_id : int,
                  start_date: str, 
                  current_date : str, 
                  current_location: str, 
                  destination: Habitat,  
                  start_location: Habitat,
                  migration_path: MigrationPath,
                  duration: Optional[int] = None, 
                  status:str = "Scheduled") -> None:
        self.migration_id = migration_id
        self.start_date = start_date
        self.current_date = current_date
        self.current_location = current_location
        self.destination = destination
        self.start_location = start_location
        self.migration_path = migration_path
        self.duration = duration
        self.status = status
        
    
    def get_migration_details(self) -> dict[str, Any]:
        pass

    def update_migration_details(self, **kwargs: Any) -> None:
        pass

    pass