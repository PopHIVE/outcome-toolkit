import os
from pydantic import BaseModel


class DataDelivery(BaseModel):
    """ Generic File Data Delivery Model. """

    root_dir: str = os.environ['DATA_BUNDLE_DIR']
    relative_path: str
    data_release: str
    data_provider: str

    def get_full_path(self) -> str:
        """ Get Full Path to Data Delivery """
        return os.path.join(self.root_dir, self.relative_path)
    
    def get_filename(self) -> str:
        """ Get Filename """
        return os.path.basename(self.relative_path)
        
    
class ZippedDataDelivery(DataDelivery):
    """ Zipped File Data Delivery Model. """
    
    file_name: str

    def get_filename(self) -> str:
        """ Get Filename """
        return self.file_name
    

class ZippedBinDataDelivery(DataDelivery):
    """ Zipped File Data Delivery Model. """
    
    file_name: str
    metrics_file_name: str

    def get_filename(self) -> str:
        """ Get Filename """
        return self.file_name
    
class CensusDataDelivery(DataDelivery):
    """ Census Data Delivery Model. """

    geo_type: str

    def get_type(self) -> str:
        """ Get Geographic Type. """
        return self.geo_type
    

class CensusGeomsDataDelivery(DataDelivery):
    """ Census Data Delivery Model. """

    geo_type: str
    geoid_col: str
    affgeoid_col: str

    def get_type(self) -> str:
        """ Get Geographic Type. """
        return self.geo_type