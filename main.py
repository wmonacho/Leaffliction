#!/usr/bin/env python3
"""Menu graphique de Leaffliction : lance les programmes du projet.

Pour ajouter un programme, il suffit d'ajouter une entrée dans PROGRAMS.
Tant que son script n'existe pas dans code/, sa carte affiche
« Bientôt disponible ».
"""
import os
import queue
import shlex
import subprocess
import sys
import threading
import tkinter as tk
from tkinter import filedialog

from PIL import Image, ImageDraw, ImageOps, ImageTk

ROOT = os.path.dirname(os.path.abspath(__file__))
CODE_DIR = os.path.join(ROOT, "code")
DATASET = os.path.join(ROOT, "leaves", "images")

# script : fichier dans code/
# input  : argument attendu : "dir" (dossier), "file" (image),
#          "any" (image ou dossier) ou None (aucun)
# image  : classe du dataset dont une photo sert d'illustration
PROGRAMS = [
    {"name": "Distribution", "script": "Distribution.py", "input": "dir",
     "image": "Apple_healthy",
     "text": "Compte les images de chaque classe\n"
             "et affiche un camembert et un histogramme."},
    {"name": "Augmentation", "script": "Augmentation.py", "input": "any",
     "image": "Apple_rust",
     "text": "Crée 6 variantes de chaque image\n"
             "(rotation, flou, contraste, zoom...)."},
    {"name": "Transformation", "script": "Transformation.py", "input": "any",
     "image": "Grape_Esca",
     "text": "Applique les transformations PlantCV\n"
             "(masque, contours, histogramme de couleurs...)."},
    {"name": "Train", "script": "train.py", "input": "dir",
     "image": "Apple_scab",
     "text": "Entraîne le modèle sur le dataset\n"
             "et produit leaffliction.zip."},
    {"name": "Predict", "script": "predict.py", "input": "file",
     "image": "Grape_spot",
     "text": "Prédit la maladie d'une feuille\n"
             "à partir d'une photo."},
]

# Couleurs et police
BG = "#0f1f17"
CARD = "#1b3326"
HOVER = "#27503a"
ACCENT = "#6fcf7f"
TEXT = "#e8f5e9"
MUTED = "#7f9c88"
FONT = "Helvetica"


def leaf_photo(class_name, size, gray=False):
    """Charge une photo d'une classe du dataset, aux coins arrondis.

    Si le dataset est absent, renvoie un simple rectangle vert.
    """
    folder = os.path.join(DATASET, class_name)
    try:
        first = sorted(os.listdir(folder))[0]
        img = ImageOps.fit(Image.open(os.path.join(folder, first)), size)
    except (OSError, IndexError):
        img = Image.new("RGB", size, HOVER)
    if gray:
        img = ImageOps.grayscale(img)
    img = img.convert("RGBA")
    # Masque transparent pour arrondir les coins
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *size), radius=14, fill=255)
    img.putalpha(mask)
    return ImageTk.PhotoImage(img)


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Leaffliction")
        self.geometry("900x640")
        self.minsize(820, 600)
        self.configure(bg=BG)
        self.images = []  # Tk efface une image si on n'en garde pas la référence
        self.screen = None
        self.animating = False
        self.fade_in()
        self.show(self.splash_screen())

    # ------------------------------------------------------------------
    # Transitions
    # ------------------------------------------------------------------
    def fade_in(self, alpha=0.0):
        """Fait apparaître la fenêtre en fondu au démarrage."""
        try:
            self.attributes("-alpha", alpha)
        except tk.TclError:
            return  # transparence non gérée par le système : on ignore
        if alpha < 1:
            self.after(20, self.fade_in, min(alpha + 0.05, 1))

    def show(self, new, direction=1):
        """Remplace l'écran actuel par `new` en le faisant glisser.

        direction = 1 : arrive par la droite, -1 : arrive par la gauche.
        """
        old, self.screen = self.screen, new
        if old is None:
            new.place(relx=0, rely=0, relwidth=1, relheight=1)
            return
        self.animating = True
        steps = 18

        def step(i):
            t = 1 - (1 - i / steps) ** 3  # ease-out : rapide puis ralentit
            new.place(relx=direction * (1 - t), rely=0,
                      relwidth=1, relheight=1)
            old.place(relx=-direction * t, rely=0, relwidth=1, relheight=1)
            if i < steps:
                self.after(15, step, i + 1)
            else:
                old.destroy()
                self.animating = False

        step(0)

    def go(self, make_screen, direction=1):
        """Change d'écran, sauf si une transition est déjà en cours."""
        if not self.animating:
            self.show(make_screen(), direction)

    # ------------------------------------------------------------------
    # Petits widgets réutilisables
    # ------------------------------------------------------------------
    def photo(self, class_name, size, gray=False):
        img = leaf_photo(class_name, size, gray)
        self.images.append(img)
        return img

    def button(self, parent, text, command, color=ACCENT):
        """Bouton plat qui s'éclaircit au survol."""
        b = tk.Label(parent, text=text, font=(FONT, 12, "bold"), bg=color,
                     fg=BG, padx=18, pady=8, cursor="hand2")
        b.bind("<Button-1>", lambda e: command())
        b.bind("<Enter>", lambda e: b.config(bg=TEXT))
        b.bind("<Leave>", lambda e: b.config(bg=color))
        return b

    # ------------------------------------------------------------------
    # Écran 1 : accueil
    # ------------------------------------------------------------------
    def splash_screen(self):
        frame = tk.Frame(self, bg=BG)
        row = tk.Frame(frame, bg=BG)
        row.pack(pady=(80, 30))
        for cls in ("Apple_healthy", "Apple_rust", "Grape_Esca", "Grape_spot"):
            tk.Label(row, image=self.photo(cls, (150, 150)),
                     bg=BG).pack(side="left", padx=8)
        tk.Label(frame, text="Leaffliction", font=(FONT, 42, "bold"),
                 fg=ACCENT, bg=BG).pack()
        tk.Label(frame, text="Détection des maladies des feuilles",
                 font=(FONT, 14), fg=MUTED, bg=BG).pack(pady=(4, 30))
        self.button(frame, "Commencer  →",
                    lambda: self.go(self.menu_screen)).pack()
        return frame

    # ------------------------------------------------------------------
    # Écran 2 : menu des programmes
    # ------------------------------------------------------------------
    def menu_screen(self):
        frame = tk.Frame(self, bg=BG)
        tk.Label(frame, text="Que veux-tu lancer ?", font=(FONT, 24, "bold"),
                 fg=TEXT, bg=BG).pack(pady=(35, 20))
        grid = tk.Frame(frame, bg=BG)
        grid.pack()
        for i, prog in enumerate(PROGRAMS):
            self.card(grid, prog).grid(row=i // 3, column=i % 3,
                                       padx=12, pady=12)
        return frame

    def card(self, parent, prog):
        """Carte cliquable d'un programme (grisée s'il n'existe pas encore)."""
        ready = os.path.isfile(os.path.join(CODE_DIR, prog["script"]))
        card = tk.Frame(parent, bg=CARD, padx=12, pady=12)
        widgets = [
            card,
            tk.Label(card, image=self.photo(prog["image"], (220, 120),
                                            gray=not ready), bg=CARD),
            tk.Label(card, text=prog["name"], font=(FONT, 15, "bold"),
                     fg=TEXT if ready else MUTED, bg=CARD),
            tk.Label(card, text="Lancer  →" if ready else "Bientôt disponible",
                     font=(FONT, 10), fg=ACCENT if ready else MUTED, bg=CARD),
        ]
        for w in widgets[1:]:
            w.pack(pady=(0, 4))
        if not ready:
            return card

        def hover(on):
            for w in widgets:
                w.config(bg=HOVER if on else CARD)

        for w in widgets:
            w.config(cursor="hand2")
            w.bind("<Enter>", lambda e: hover(True))
            w.bind("<Leave>", lambda e: hover(False))
            w.bind("<Button-1>",
                   lambda e: self.go(lambda: self.program_screen(prog)))
        return card

    # ------------------------------------------------------------------
    # Écran 3 : un programme
    # ------------------------------------------------------------------
    def program_screen(self, prog):
        frame = tk.Frame(self, bg=BG)

        back = tk.Label(frame, text="←  Menu", font=(FONT, 12, "bold"),
                        fg=ACCENT, bg=BG, cursor="hand2")
        back.pack(anchor="w", padx=25, pady=15)
        back.bind("<Button-1>",
                  lambda e: self.go(self.menu_screen, direction=-1))

        # En-tête : image + nom + description
        head = tk.Frame(frame, bg=BG)
        head.pack(fill="x", padx=30)
        tk.Label(head, image=self.photo(prog["image"], (130, 130)),
                 bg=BG).pack(side="left")
        info = tk.Frame(head, bg=BG)
        info.pack(side="left", padx=20)
        tk.Label(info, text=prog["name"], font=(FONT, 26, "bold"),
                 fg=TEXT, bg=BG).pack(anchor="w")
        tk.Label(info, text=prog["text"], font=(FONT, 12), justify="left",
                 fg=MUTED, bg=BG).pack(anchor="w", pady=(6, 0))

        # Formulaire : cible + options
        form = tk.Frame(frame, bg=BG)
        form.pack(fill="x", padx=30, pady=15)
        target = tk.StringVar(value=DATASET if prog["input"] == "dir" else "")
        options = tk.StringVar()
        if prog["input"]:
            self.field(form, 0, "Cible", target)
            browse = tk.Frame(form, bg=BG)
            browse.grid(row=0, column=2, padx=(8, 0))
            if prog["input"] in ("file", "any"):
                self.button(browse, "Image...", lambda: target.set(
                    filedialog.askopenfilename(initialdir=DATASET) or
                    target.get()), color=MUTED).pack(side="left", padx=2)
            if prog["input"] in ("dir", "any"):
                self.button(browse, "Dossier...", lambda: target.set(
                    filedialog.askdirectory(initialdir=DATASET) or
                    target.get()), color=MUTED).pack(side="left", padx=2)
        self.field(form, 1, "Options", options)
        form.columnconfigure(1, weight=1)

        console = tk.Text(frame, bg="#08130d", fg=TEXT, font=("Monospace", 10),
                          relief="flat", padx=10, pady=8, height=8)
        self.button(frame, "▶  Lancer", lambda: self.run(
            prog, target.get(), options.get(), console)).pack(pady=(0, 12))
        console.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        return frame

    def field(self, parent, row, label, var):
        """Ligne « libellé + champ texte » du formulaire."""
        tk.Label(parent, text=label, font=(FONT, 12), fg=TEXT,
                 bg=BG).grid(row=row, column=0, sticky="w", padx=(0, 10))
        tk.Entry(parent, textvariable=var, font=(FONT, 11), bg=CARD, fg=TEXT,
                 insertbackground=TEXT, relief="flat").grid(
            row=row, column=1, sticky="ew", ipady=5, pady=4)

    # ------------------------------------------------------------------
    # Lancement d'un programme
    # ------------------------------------------------------------------
    def run(self, prog, target, options, console):
        """Lance le script dans un sous-processus et affiche sa sortie.

        Le script tourne dans un thread pour que la fenêtre ne se fige pas ;
        ses lignes passent par une file que Tk relit toutes les 50 ms.
        """
        cmd = [sys.executable, "-u", os.path.join(CODE_DIR, prog["script"])]
        if target:
            cmd.append(target)
        cmd += shlex.split(options)
        console.delete("1.0", "end")
        shown = [os.path.relpath(cmd[2], ROOT)] + cmd[3:]
        console.insert("end", "$ python " + " ".join(shown) + "\n\n")
        lines = queue.Queue()

        def worker():
            proc = subprocess.Popen(cmd, cwd=ROOT, text=True,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            for line in proc.stdout:
                lines.put(line)
            lines.put(f"\n[terminé, code de sortie {proc.wait()}]\n")
            lines.put(None)

        def poll():
            if not console.winfo_exists():
                return  # l'utilisateur a quitté l'écran
            while not lines.empty():
                line = lines.get()
                if line is None:
                    return
                console.insert("end", line)
                console.see("end")
            self.after(50, poll)

        threading.Thread(target=worker, daemon=True).start()
        poll()


def main():
    App().mainloop()


if __name__ == "__main__":
    main()
