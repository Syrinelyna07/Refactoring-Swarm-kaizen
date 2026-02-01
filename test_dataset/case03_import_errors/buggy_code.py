# filepath: data_processor.py
import pandas
from numpy import array
from non_existent_module import something  # Module inexistant

def process_dataframe(df):
    # pandas utilisé sans alias
    result = pd.DataFrame(df)  # NameError: pd n'est pas défini
    return result

def create_array(data):
    return array(data)
