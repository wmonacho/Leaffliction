import sys
import os
import matplotlib.pyplot as plt
from PIL import ImageOps


def mirror(image):
    return ImageOps.mirror(image)


def flip(image):
    return ImageOps.flip(image)


def posterize(image):
    rgb_image = image.convert("RGB")
    return ImageOps.posterize(rgb_image, 2)


def contrast(image):
    return ImageOps.autocontrast(image, cutoff=2)


def rotation(image):
    return image.rotate(45, expand=True)


def projective(image):
    width, height = image.size
    # Mettre un 'b' à 0.3 incline l'image sans la couper si on ajoute une marge
    coeffs = [1, 0.4, -width * 0.2, 0, 1, 0]
    return image.transform(
        (width, height),
        ImageOps.Image.AFFINE,
        coeffs,
        ImageOps.Image.BICUBIC)


def process(output_dir, image_path):
    os.makedirs(output_dir, exist_ok=True)
    original = ImageOps.Image.open(image_path)
    transformations = {
        "original": original,
        "mirror": mirror(original),
        "flip": flip(original),
        "posterize": posterize(original),
        "contrast": contrast(original),
        "rotation": rotation(original),
        "projective": projective(original)
    }
    return transformations


def display(transformations_list):
    n_rows = len(transformations_list)
    n_cols = len(transformations_list[0])

    fig, axes = plt.subplots(n_rows, n_cols, figsize=(n_cols * 3, n_rows * 3))

    for row, transformations in enumerate(transformations_list):
        for col, (title, img) in enumerate(transformations.items()):
            ax = axes[row][col] if n_rows > 1 else axes[col]
            ax.imshow(img)
            if row == 0:
                ax.set_title(title, fontsize=10)
            ax.axis('off')

    plt.tight_layout()
    plt.show()


def save_transformations(transformations, name_without_ext, ext, output_dir):
    for suffix, transformed_img in transformations.items():
        new_filename = f"{name_without_ext}_{suffix}{ext}"
        transformed_img.save(os.path.join(output_dir, new_filename))


def process_single_image(image):
    print(image)
    name = os.path.basename(image)
    name_without_ext, ext = os.path.splitext(name)
    output_dir = "leaves/augmented_directory"
    try:
        transformations = process(output_dir, image)
        save_transformations(
            transformations,
            name_without_ext,
            ext,
            output_dir)
        display([transformations])

    except Exception as e:
        print(f"❌ Erreur lors du traitement de {image} : {e}")


def process_directory(dir):
    output_base = "leaves/augmented_directory"
    image_extensions = {".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"}
    preview_list = []

    for root, _, files in os.walk(dir):
        for filename in files:
            name_without_ext, ext = os.path.splitext(filename)
            if ext not in image_extensions:
                continue

            image_path = os.path.join(root, filename)
            rel_path = os.path.relpath(root, dir)
            output_dir = os.path.join(output_base, rel_path)

            try:
                transformations = process(output_dir, image_path)
                save_transformations(
                    transformations,
                    name_without_ext,
                    ext,
                    output_dir)
                if len(preview_list) < 5:
                    preview_list.append(transformations)

            except Exception as e:
                print(f"❌ Erreur pour {image_path} : {e}")

    if preview_list:
        display(preview_list)


def main():
    if len(sys.argv) != 2:
        print("Usage: un run python Augmentation.py <image>")
        return

    target = sys.argv[1]

    if os.path.isfile(target):
        process_single_image(target)
    elif os.path.isdir(target):
        process_directory(target)
    else:
        print(f"Erreur : '{target}' n'est ni un fichier ni un dossier valide.")


if __name__ == "__main__":
    main()
