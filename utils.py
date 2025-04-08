from datetime import datetime
import uuid

def generate_uuid(base_id: str) -> str:
    '''
    Input string (base_id), use uuid5 to return a UUID
    
        UUID is reproducable if you input the same string

        Choose DNS namespace for generating UUIDs

    Return UUID string
    '''
    return uuid.uuid5(uuid.NAMESPACE_DNS, base_id).hex

def parse_timestamp(timestamp: float) -> str:
    '''
    Input timestamp from steam data and 
    
    Return a date string in "YYYY-MM-DD format"
    '''
    return str(datetime.fromtimestamp(timestamp).date())
    
def to_timestamp(date: str) -> float:
        '''
    Input date string in "YYYY-MM-DD" format
    
    Return a date timestamp for filtering dates
    '''
        return datetime.timestamp(datetime.strptime(date,'%Y-%m-%d'))

