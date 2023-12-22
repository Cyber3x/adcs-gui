from stores.GlobalStore import State


def extract_floats_from_line(line: str):
    return map(
        float,
        line.replace("(", "")
        .replace(")", "")
        .replace(",", "")
        .split(" ")[1:]
    )


def parse_input_line(raw_line: bytearray, state: State):
    try:
        line = raw_line.decode().strip()
    except UnicodeDecodeError:
        print("UnicodeDecodeError", end=" ")
        print(raw_line)
        return None

    if line.startswith("acc"):
        accelerations = extract_floats_from_line(line)
        state.add_IMU_acceleration_datapoint(
            *map(
                lambda x: x * 9.81,
                accelerations
            )
        )

    elif line.startswith("angle"):
        # input line format:
        # angle (x, y, z)
        angles = extract_floats_from_line(line)
        state.add_IMU_angle_datapoint(*angles)

    elif line.startswith("gyro"):
        angular_velocities = extract_floats_from_line(line)
        state.add_IMU_gyroscope_datapoint(*angular_velocities)

    elif line.startswith("temp"):
        temp = float(line.split(" ")[1])
        state.add_IMU_temperature_datapoint(temp)
    else:
        print(f"Unknown data: {line}")

    return line
