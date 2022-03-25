import yaml
import datetime
import dateparser

from pathlib import Path

def get_date(input: str) -> datetime.datetime:
    """Get a datetime object from the date stored together with the kindle clippings.
    Parameter
    ---------
    input: str
        Has the following structure: "- {text} | {text}, 1 of January of 2019 23:13:08"
    """
    try:
        date_str = input.split(', ')[1]
        return dateparser.parse(date_str)
        
    except Exception:
        return None


def store_date(date: datetime.datetime, file_path: Path, info: dict):
    """Store the date established as the last highlight exported in the YAML file."""
    try:
        info["Paths"]["last_date"] = date

        with open(file_path, 'w') as f:
            yaml.dump(info, f)
            
    except Exception:
        print("Date was not stored in the YAML file")
        pass