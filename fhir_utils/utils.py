import json
import xmltodict

def json_to_dict(json_file_path):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            return data
    except FileNotFoundError:
        print(f"File '{json_file_path}' not found.")
    except json.JSONDecodeError:
        print(f"Unable to parse JSON file: '{json_file_path}'.")
    except Exception as e:
        print(f"An error occurred while importing JSON: {e}")


def xml_to_dict(xml_file_path):
    try:
        with open(xml_file_path, 'r') as file:
            xml_data = file.read()
            return xmltodict.parse(xml_data)
    except FileNotFoundError:
        print(f"Error: XML file not found at '{xml_file_path}'")
        return None
    except Exception as e:
        print(f"Error: Unable to parse XML file. Reason: {str(e)}")
        return None
 
    
def save_to_json(dict, json_path,):
    with open(json_path, "w") as file:
        json.dump(dict, file)