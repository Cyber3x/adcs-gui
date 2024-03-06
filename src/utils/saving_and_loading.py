import json
import os
from json.decoder import JSONDecodeError
from typing import TypeVar, Optional

from PyQt6.QtWidgets import QFileDialog, QMessageBox
from jsonschema import validate, ValidationError

from utils.utils import custom_JSON_encoder

CONFIG_DIR = "config"


def save_json_data(data, caption: str, directory: str):
    filters = "JavaScript Object Notation (*.json)"
    filename, selected_filter = QFileDialog.getSaveFileName(
        None,
        caption,
        os.path.join(CONFIG_DIR, directory),
        filter=filters,
        initialFilter=filters,
    )

    if not filename:
        return

    with open(filename, "w") as f:
        json.dump(data, f, default=custom_JSON_encoder, indent=4)


T = TypeVar("T")


def load_json_data(schema, caption: str, inital_dir: str = "") -> Optional[T]:
    """
    This opens a file dialog to load a json file and returns the data from the file
    @param schema: The schema to validate the json data
    @param caption: The caption of the file dialog
    @param inital_dir: The starting directory of the file dialog, empty string uses the current directory
    @return:
    """
    filters = "JavaScript Object Notation (*.json)"
    initial_filter = "All files (*.*)"

    init_directory = os.path.join(os.getcwd(), CONFIG_DIR, inital_dir)

    filename, selected_filter = QFileDialog.getOpenFileName(
        caption=caption,
        directory=init_directory,
        filter=filters,
        initialFilter=initial_filter,
    )

    if not filename or not os.path.isfile(filename):
        return

    with open(filename, "r") as f:
        try:
            data = json.load(f)
        except JSONDecodeError as e:
            print("json error")
            QMessageBox.critical(
                None,
                "Invalid JSON",
                f"The opened file is not a valid JSON file.\n\n"
                f"{e.msg}",
                buttons=QMessageBox.StandardButton.Ok,
                defaultButton=QMessageBox.StandardButton.Ok,
            )
            return

    try:
        validate(data, schema)
    except ValidationError as e:
        QMessageBox.critical(
            None,
            "Invalid Data Format",
            f"{e.message}\n\n"
            "The format of the JSON file is invalid. Thus, the file cannot be opened.\nYou can try to fix the "
            "file manually or create a new one.",
            buttons=QMessageBox.StandardButton.Ok,
            defaultButton=QMessageBox.StandardButton.Ok,
        )
        return

    return data
