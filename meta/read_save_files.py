from pathlib import Path

# define main folder
main_file_path = Path(__file__).resolve().parent.parent


def get_file_path(folder_name, file_name):
    return main_file_path / folder_name / file_name