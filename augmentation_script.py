import json
import random
import os


def check_file_size(file_paths):
    report = []
    for file_path in file_paths:
        with open(file_path, "r") as f:
            content = f.read()
        num_chars = len(content)
        status = "Pass" if num_chars < 4000 else "Fail"
        report.append(
            {"file_name": file_path, "num_chars": num_chars, "status": status}
        )
    return report


def generate_color():
    """Generate a random color."""
    return [round(random.random(), 2) for _ in range(3)] + [1]  # RGBA


def modify_stroke_width(width):
    """Modify the stroke width by ±10%."""
    factor = round(random.uniform(0.9, 1.1), 2)
    return round(width * factor, 2)


def modify_duration(duration):
    """Modify the duration by ±5%."""
    factor = round(random.uniform(0.95, 1.05), 2)
    return round(duration * factor, 2)


def modify_opacity(opacity):
    """Modify the opacity between 70% to 100%."""
    return round(random.uniform(0.7, 1.0), 2)


def augment_lottie(file_path, output_dir):
    """
    Augments a Lottie JSON file by modifying color, stroke width, duration, and opacity.

    Args:
        file_path (str): The path to the Lottie JSON file.

    Returns:
        dict: A dictionary containing the original and augmented file names, as well as the modifications made.
    """
    # Initialize variables to None
    new_color = None
    new_width = None
    new_duration = None
    new_opacity = None

    # Create a deep copy of the original data
    with open(file_path, "r") as f:
        data = json.load(f)
    modified_data = json.loads(json.dumps(data))

    # Iterate through layers to find the correct shape/line for modification
    for layer in modified_data["layers"]:
        # Check if the layer has the "shapes" key
        if "shapes" in layer:
            for shape in layer["shapes"]:
                if shape["ty"] == "st":  # Targeting strokes for now
                    # Color Modification
                    if "c" in shape and "k" in shape["c"]:
                        original_color = shape["c"]["k"]
                        new_color = generate_color()
                        shape["c"]["k"] = new_color

                    # Stroke Width Modification
                    if "w" in shape:
                        original_width = shape["w"]["k"]
                        new_width = modify_stroke_width(original_width)
                        shape["w"]["k"] = new_width

    # Modify Duration
    if "op" in modified_data:
        original_duration = modified_data["op"]
        new_duration = modify_duration(original_duration)
        modified_data["op"] = new_duration

    # Modify Opacity (assuming first layer for simplicity)
    if (
        "ks" in modified_data["layers"][0]
        and "o" in modified_data["layers"][0]["ks"]
        and "k" in modified_data["layers"][0]["ks"]["o"]
    ):
        original_opacity = (
            modified_data["layers"][0]["ks"]["o"]["k"] / 100.0
        )  # Assuming opacity is given in percentage
        new_opacity = modify_opacity(original_opacity)
        modified_data["layers"][0]["ks"]["o"]["k"] = new_opacity * 100

        # Save the augmented Lottie JSON
    augmented_file_name = os.path.splitext(os.path.basename(file_path))[0] + "_"
    modifications = []
    if new_color is not None:
        modifications.append("color")
    if new_width is not None:
        modifications.append("stroke_width")
    if new_duration is not None:
        modifications.append("duration")
    if new_opacity is not None:
        modifications.append("opacity")
    augmented_file_name += "_" + "_".join(modifications) + ".json"
    augmented_file_path = os.path.join(output_dir, augmented_file_name)
    with open(augmented_file_path, "w") as f:
        json.dump(modified_data, f, separators=(",", ":"), ensure_ascii=False)

    # Record the modifications
    modifications_record = {
        "original_file_name": file_path,
        "augmented_file_name": augmented_file_path,
        "modifications": {
            "color": new_color,
            "stroke_width": new_width,
            "duration_factor": round(new_duration / original_duration, 2)
            if new_duration is not None
            else None,
            "opacity": new_opacity,
        },
    }

    return modifications_record


def main():
    original_dir = "original_files"
    output_dir = "augmented_files"
    os.makedirs(output_dir, exist_ok=True)

    file_names = [
        "Blue line shape on white background made of a star, a circle, and a rectangle, erasing itself counterclockwise.json",
        "Irregular blue dashed line on grey background drawing itself on from left to right.json",
        "Irregularly shaped white line on a black background erasing itself clockwise.json",
        "Purple bordered triangle with blue and green gradient fill on a white background  erasing itself from the top of the triangle.json",
        "Short white line on black background moving horizontally across the screen disappearing then appearing again on the other side to continue moving.json",
        "Three vertical black lines of different heights on a green background growing from zero to full height one at a time from left to right.json",
        "Three vertical black lines of different heights on a green background growing from zero to full height so they all finish at the same time.json",
        "White line on black background growing and shrinking horizontally.json",
        "White line square on a black background drawing itself on from it's top left corner.json",
        "White line with triangle arrow head on a black background drawing on in an irregular path from left to right.json",
    ]
    file_paths = [os.path.join(original_dir, file_name) for file_name in file_names]
    all_records = []

    for file_path in file_paths:
        record = augment_lottie(file_path, output_dir)
        all_records.append(record)

    # Save the records to a JSON
    with open("augmentation_records.json", "w") as f:
        json.dump(all_records, f)

        # Generate the report for the original files
    original_report = check_file_size(file_paths)
    with open("original_report.json", "w") as f:
        json.dump(original_report, f)

    # Generate the report for the augmented files
    augmented_file_paths = [record["augmented_file_name"] for record in all_records]
    augmented_report = check_file_size(augmented_file_paths)
    with open("augmented_report.json", "w") as f:
        json.dump(augmented_report, f)


if __name__ == "__main__":
    main()
