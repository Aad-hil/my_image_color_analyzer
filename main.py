from PIL import Image
from collections import Counter
from webcolors import css3_hex_to_names, hex_to_rgb
from scipy.spatial import KDTree
from flask import Flask, render_template, request
from io import BytesIO

app = Flask(__name__)


def process_image(image_data):
    # Open image from bytes
    image = Image.open(BytesIO(image_data))

    # Convert image to RGB
    image = image.convert("RGB")

    # Flatten image
    pixels = list(image.getdata())

    # Count color frequencies
    color_freq = Counter(pixels)

    # Sort color frequencies
    most_common_colors = color_freq.most_common()

    def convert_rgb_to_names(rgb_tuple):
        # a dictionary of all the hex and their respective names in css3
        css3_db = css3_hex_to_names
        names = []
        rgb_values = []
        for color_hex, color_name in css3_db.items():
            names.append(color_name)
            rgb_values.append(hex_to_rgb(color_hex))

        kdt_db = KDTree(rgb_values)
        distance, index = kdt_db.query(rgb_tuple)
        return names[index]

    # Get the top 3 most common colors
    top_colors_with_names = []
    for color, freq in most_common_colors[:3]:  # Display top 3 common colors
        color_name = convert_rgb_to_names(color)
        top_colors_with_names.append({"name": color_name, "rgb": color, "freq": freq})

    return top_colors_with_names


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename != '':
                image_data = image_file.read()
                top_colors = process_image(image_data)
                return render_template('index.html', uploaded=True, top_colors=top_colors, image_data=image_data)
    return render_template('index.html', uploaded=False)


if __name__ == "__main__":
    app.run(debug=True)
