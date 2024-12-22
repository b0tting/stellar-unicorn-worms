# Description: Converts a PNG / JPG whatever file to a dictionary or array of arrays of RGB values
from argparse import ArgumentParser
from pathlib import Path

import sys
from PIL import Image


class PNGConverter:
    def __init__(self, file=None, verbose=False):
        self.file = self.get_file_stream(file)
        self.verbose = verbose
        self.log("File stream loaded")

    def log(self, message):
        if self.verbose:
            print(message)

    def resize_needed(self, image, resize_width: int, resize_height: int):
        if image.width != resize_width or image.height != resize_height:
            return True
        return False

    def convert_to_iterable(self, resize_width: int = 16, resize_height: int = 16, return_dict=True):
        image = PNGConverter.load_image(self.file)
        resize_height = int(resize_height) if resize_height else image.height
        resize_width = int(resize_width) if resize_width else image.width
        if self.resize_needed(image, resize_width, resize_height):
            self.log(f"Image currently {image.width}x{image.height}")
            self.log(f"Resizing image to {resize_width}x{resize_height}")
            image = self.resize_image(image, resize_width, resize_height)
        if return_dict:
            rgb_dict = self.convert_image_to_rgb_dict(image)
        else:
            rgb_dict = self.convert_image_to_rgb_arrays(image)
        return rgb_dict

    def load_image(file):
        img = Image.open(file)
        img = img.convert("RGB")
        img.load()
        return img

    def resize_image(self, image, width, height):
        return image.resize((width, height))

    def get_file_stream(self, file):
        file = Path(file)
        if not file:
            print("No file specified")
            sys.exit(1)
        if not file.exists():
            print(f"File {file} does not exist")
            sys.exit(1)
        return file

    def convert_image_to_rgb_dict(self, image : Image):
        rgb_dict = {}
        for x in range(image.width):
            for y in range(image.height):
                rgb = image.getpixel([x, y])
                rgb_dict[(x, y)] = rgb
        return rgb_dict

    def convert_image_to_rgb_arrays(self, image : Image):
        rgb_arrays = []
        indexes_x = list(range(image.width))
        indexes_x.reverse()
        for x in indexes_x:
            row = []
            indexes_y = list(range(image.height))
            indexes_y.reverse()
            for y in indexes_y:
                rgb = image.getpixel([x, y])
                row.append(list(rgb))
            rgb_arrays.append(row)
        return rgb_arrays


if __name__ == "__main__":
    argparse = ArgumentParser()
    argparse.add_argument("--file", type=str, help="The image file to convert to a dictionary")
    argparse.add_argument("--resize-width", type=int, default=0, help="The resized width of the image")
    argparse.add_argument("--resize-height", type=int, default=0, help="The resized height of the image")
    argparse.add_argument("--return-dict", action="store_true", default=False, help="Return a dictionary instead of an array of arrays")
    argparse.add_argument("--verbose", action="store_true", help="Print verbose output")


    args = argparse.parse_args()
    converter = PNGConverter(file=args.file, verbose=args.verbose)
    rgb_arrays = converter.convert_to_iterable(args.resize_width, args.resize_height, return_dict=args.return_dict)
    print(rgb_arrays)
