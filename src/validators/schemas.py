percentage_number_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "adcs-gui/percentage-number.schema.json",
    "type": "number",
    "minimum": 0,
    "maximum": 100
}

stepper_values_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "adcs-gui/stepper-values.schema.json",
    "type": "object",
    "properties": {
        "stepper_values": {
            "type": "object",
            "properties": {
                "X": percentage_number_schema,
                "Y": percentage_number_schema,
                "Z": percentage_number_schema
            },
            "required": ["X", "Y", "Z"],
            "additionalProperties": False
        }
    },
    "required": ["stepper_values"],
    "additionalProperties": False
}

PID_values_schema = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "adcs-gui/PID-values.schema.json",
    "type": "object",
    "properties": {
        "PID_values": {
            "type": "object",
            "properties": {
                "P": {"type": "number"},
                "I": {"type": "number"},
                "D": {"type": "number"}
            },
            "required": ["P", "I", "D"],
            "additionalProperties": False
        }
    },
    "required": ["PID_values"],
    "additionalProperties": False
}
