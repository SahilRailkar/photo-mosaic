from PIL import Image
import math
from os import listdir
import pathlib


def main():
    """Generates a photo mosaic of the given main Image using the given tile Images."""
    while True:
        main_image_loc = input("Enter the path of the main image in your computer: ")
        try:
            main_image = Image.open(main_image_loc)
        except FileNotFoundError:
            print("\nFileNotFoundError: No such file or directory '" + main_image_loc + "'")
        except OSError:
            print("\nOSError: Cannot identify image file '" + main_image_loc + "'")
        else:
            break

    tile_images_loc = input("Enter the path of the directory in which your tile images are located in your computer: ")
    p = pathlib.Path(tile_images_loc)

    while not(p.exists() and p.is_dir()):
        if p.exists() is False:
            print("\nFileNotFoundError: No such file or directory '" + tile_images_loc + "'")
        else:
            print("\nDirectoryNotFoundError: No such directory '" + tile_images_loc + "'")
        tile_images_loc = input("Enter the path of the directory in which your tile images are located in your "
                                "computer: ")
        p = pathlib.Path(tile_images_loc)

    num_of_tiles = 0
    while num_of_tiles == 0:
        try:
            num_of_tiles = int(input("Enter the number of tiles you would like your main image to be constructed "
                                     "with: "))
        except ValueError:
            print("\nValueError: Invalid literal for int with base 10")

    tile_size = int(max(main_image.width, main_image.height) / num_of_tiles)

    no_entry = True
    repeat = True
    while no_entry:
        repeat = input("Would you like images to be repeated in your photomosaic? If no, the number of tiles requested "
                       "must match the number of tile images given. ('Yes' or 'No'): ")
        if repeat.lower() == 'yes':
            repeat = True
            no_entry = False
        elif repeat.lower() == 'no':
            repeat = False
            no_entry = False
        else: 
            repeat = None
            no_entry = True
            print("\nPlease enter 'Yes' or 'No'!")

    main_image_grid = split_main_image(main_image, tile_size)
    main_image_rgb_grid = generate_rgb_grid(main_image_grid)
    resized_tile_images = resize_similar_images(tile_images_loc, tile_size)
    photomosaic_grid = find_similar_images(resized_tile_images, main_image_rgb_grid, repeat)
    photomosaic = create_photo_mosaic(main_image, photomosaic_grid, tile_size)
    photomosaic.show()


def split_main_image(image: Image, tile_size: int) -> list:
    """Splits the main Image into squares with side length tile_size.

    IMAGE is the main Image.
    TILE_SIZE is the calculated side length of each tile Image in the photo mosaic.
    """
    rgb_img = image.convert('RGB')
    img_grid = list()

    if rgb_img.width % tile_size == 0 and rgb_img.height % tile_size == 0:
        for row in range(int(rgb_img.height/tile_size)):
            img_grid.append(list())
            for col in range(int(rgb_img.width/tile_size)):
                cropped = image.crop((col * tile_size, row * tile_size, (col + 1) * tile_size, (row + 1) * tile_size))
                img_grid[row].append(cropped)
    elif rgb_img.width % tile_size != 0 and rgb_img.height % tile_size == 0:
        for row in range(rgb_img.height/tile_size):
            img_grid.append(list())
            for col in range(int(math.ceil(rgb_img.width/tile_size))):
                if col == range(int(math.ceil(rgb_img.width/tile_size)))[-1]:
                    cropped = image.crop((col * tile_size, row * tile_size, rgb_img.width, (row + 1) * tile_size))
                else:
                    cropped = image.crop((col * tile_size, row * tile_size, (col + 1) * tile_size, (row + 1) *
                                          tile_size))
                img_grid[row].append(cropped)
    elif rgb_img.width % tile_size == 0 and rgb_img.height % tile_size != 0:
        for row in range(int(math.ceil(rgb_img.height/tile_size))):
            img_grid.append(list())
            for col in range(int(rgb_img.width/tile_size)):
                if row == range(int(math.ceil(rgb_img.height/tile_size)))[-1]:
                    cropped = image.crop((col * tile_size, row * tile_size, (col + 1) * tile_size, rgb_img.height))
                else:
                    cropped = image.crop((col * tile_size, row * tile_size, (col + 1) * tile_size, (row + 1) *
                                          tile_size))
                img_grid[row].append(cropped)
    else:
        for row in range(int(math.ceil(rgb_img.height/tile_size))):
            img_grid.append(list())
            for col in range(int(math.ceil(rgb_img.width/tile_size))):
                if col == range(int(math.ceil(rgb_img.width/tile_size)))[-1] and row == \
                        range(int(math.ceil(rgb_img.height/tile_size)))[-1]:
                    cropped = image.crop((col * tile_size, row * tile_size, rgb_img.width, rgb_img.height))
                elif col == range(int(math.ceil(rgb_img.width/tile_size)))[-1]:
                    cropped = image.crop((col * tile_size, row * tile_size, rgb_img.width, (row + 1) * tile_size))
                elif row == range(int(math.ceil(rgb_img.height/tile_size)))[-1]:
                    cropped = image.crop((col * tile_size, row * tile_size, (col + 1) * tile_size, rgb_img.height))
                else:
                    cropped = image.crop((col * tile_size, row * tile_size, (col + 1) * tile_size, (row + 1) *
                                          tile_size))
                img_grid[row].append(cropped)

    return img_grid


def avg_rgb(image: Image) -> tuple:
    """Calculates the average RGB value of an Image.

    IMAGE is the given Image.
    """
    rgb_img = image.convert('RGB')

    total_rgb = [0, 0, 0]
    total_pixels = rgb_img.width * rgb_img.height

    for row in range(rgb_img.width):
        for col in range(rgb_img.height):
            r, g, b = rgb_img.getpixel((row, col))
            total_rgb[0] += r
            total_rgb[1] += g
            total_rgb[2] += b

    return total_rgb[0]/total_pixels, total_rgb[1]/total_pixels, total_rgb[2]/total_pixels


def generate_rgb_grid(grid: list) -> list:
    """Calculates all of the average RGB values of the Images in a grid.

    GRID is the two-dimensional Image list which contains the Image objects which this function calculates the average
    RGB values for.
    """
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            average_rgb = avg_rgb(grid[row][col])
            grid[row][col] = (grid[row][col], average_rgb)
    return grid


def resize_similar_images(tile_images_loc: str, tile_size: int) -> list:
    """Resizes all of the tile Images to have a side length of tile_size.

    TILE_IMAGES_LOC is the path to the directory which contains the tile Images.
    TILE_SIZE is the calculated side length of each tile Image in the photo mosaic.
    """
    image_list = listdir(tile_images_loc)
    resized_img_list = list()
    for image in image_list:
        try:
            resized_img = Image.open(tile_images_loc + "/" + image)
            resized_img = resized_img.resize((tile_size, tile_size))
            resized_img_list.append(resized_img)
        except OSError:
            continue
    return resized_img_list


def calculate_img_sim_dist(image1: tuple, image2: tuple) -> float:
    """Calculates the similarity of two given Images.

    IMAGE1 is the first given Image.
    IMAGE2 is the second given Image.
    """
    return math.sqrt((image1[1][0] - image2[1][0])**2 + (image1[1][1] - image2[1][1])**2 + (image1[1][2] -
                                                                                            image2[1][2])**2)


def find_similar_images(resized_img_list: list, rgb_grid: list, repeat: bool) -> list:
    """Finds tile Images similar to the Images in rgb_grid using the function calculate_img_sim_dist().

    RESIZED_IMG_LIST is a list of all the resized tile Images.
    RGB_GRID is a two-dimensional list which contains the tile-split main Image and each tiles' average RGB value.
    REPEAT is a Boolean value which tells if the user would like tile Images to be repeated.
    """
    for img in range(len(resized_img_list)):
        resized_img_list[img] = (resized_img_list[img], avg_rgb(resized_img_list[img]))

    photomosaic_grid = list()
    for row in rgb_grid:
        photomosaic_grid.append(list())

    if repeat is True:
        for row in range(len(rgb_grid)):
            for col in range(len(rgb_grid[row])):
                image1 = rgb_grid[row][col]
                best_image2 = resized_img_list[0]
                min_dist = calculate_img_sim_dist(image1, best_image2)
                for image2 in resized_img_list:
                    dist = calculate_img_sim_dist(image1, image2)
                    if min_dist > dist:
                        min_dist = dist
                        best_image2 = image2
                photomosaic_grid[row].append(best_image2)
    else:
        for row in range(len(rgb_grid)):
            for col in range(len(rgb_grid[row])):
                image1 = rgb_grid[row][col]
                best_image2 = resized_img_list[0]
                min_dist = calculate_img_sim_dist(image1, best_image2)
                for image2 in resized_img_list:
                    dist = calculate_img_sim_dist(image1, image2)
                    if min_dist > dist:
                        min_dist = dist
                        best_image2 = image2
                photomosaic_grid[row].append(best_image2)
                resized_img_list.remove(best_image2)

    return photomosaic_grid


def create_photo_mosaic(main_image: Image, photomosaic_grid: list, tile_size: int) -> Image:
    """Constructs the final photo mosaic.

    MAIN_IMAGE is the main image of the photo mosaic.
    PHOTOMOSAIC_GRID is the photo mosaic split into tiles of side length, tile_size.
    TILE_SIZE is the calculated side length of each tile image in the photomosaic.
    """
    photomosaic = Image.new('RGB', (main_image.width, main_image.height))

    for row in range(len(photomosaic_grid)):
        for col in range(len(photomosaic_grid[row])):
            img = photomosaic_grid[row][col][0]
            photomosaic.paste(img, (col * tile_size, row * tile_size))

    return photomosaic


if __name__ == "__main__":
    main()
