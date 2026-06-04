import os
import sys
import matplotlib.pyplot as plt


def create_charts(dataset, root_name):
    if not dataset:
        print("Erreur : Aucune donnée à afficher.")
        return

    labels = list(dataset.keys())
    values = list(dataset.values())
    cmap = plt.get_cmap("tab20")
    colors = [cmap(i / len(labels)) for i in range(len(labels))]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    fig.suptitle(f"Analyse du dataset : {root_name}", fontsize=16)

    # 2. Bar Chart
    ax1.bar(labels, values, color=colors, edgecolor='black', alpha=0.8)
    ax1.set_title("Nombre d'images par catégorie")
    ax1.set_xlabel("Dossier")
    ax1.set_ylabel("Quantité")
    ax1.tick_params(axis='x', rotation=45)

    # 3. Pie Chart
    ax2.pie(
        values,
        labels=labels,
        autopct='%1.1f%%',
        colors=colors
    )
    ax2.set_title("Répartition en pourcentage")

    plt.tight_layout()
    plt.show()


def main():
    if len(sys.argv) != 2:
        print("Usage: un run python Distribution.py <directory_path>")
        return

    path_argument = sys.argv[1]
    dataset = {}

    for root, dirs, files in os.walk(path_argument):
        file_ends = ".jpg", ".jpeg", ".png", ".JPG", ".JPEG", ".PNG"
        liste_images = [f for f in files if f.lower().endswith((file_ends))]
        if len(liste_images) > 0:
            dataset[os.path.basename(root)] = len(liste_images)

    create_charts(dataset, path_argument)


if __name__ == "__main__":
    main()
