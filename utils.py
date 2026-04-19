import json


def validate_json(json_data):
    try:
        json_object = json.loads(json_data)
    except ValueError as e:
        print(f"Invalid JSON: {e}")
        return False
    return True


def parse_quiz_file(file_path):
    """Parse a quiz file and return quiz data."""
    with open(file_path, 'r') as file:
        return json.load(file)


def write_to_file(file_path, data):
    """Write data to a file."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def read_from_file(file_path):
    """Read data from a file."""
    with open(file_path, 'r') as file:
        return json.load(file)


def helper_method_example():
    """Example of a helper method."""
    pass
