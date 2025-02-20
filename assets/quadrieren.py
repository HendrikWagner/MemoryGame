from PIL import Image, ExifTags
import os

# Ordner mit den Originalbildern
input_folder = "C:/Users/drhen/Documents/Projekte/GIT/MemoryGame/assets"
output_folder = "C:/Users/drhen/Documents/Projekte/GIT/MemoryGame/assets/resized/"
target_size = 150  # Zielgröße in Pixeln (z. B. 100x100)

# Sicherstellen, dass der Ausgabeordner existiert
os.makedirs(output_folder, exist_ok=True)

def correct_orientation(image):
    """Korrigiert die Rotation basierend auf den EXIF-Daten"""
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == "Orientation":
                break
        
        exif = image._getexif()
        if exif is not None:
            orientation_value = exif.get(orientation, 1)

            if orientation_value == 3:
                image = image.rotate(180, expand=True)
            elif orientation_value == 6:
                image = image.rotate(270, expand=True)
            elif orientation_value == 8:
                image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        pass  # Falls kein EXIF vorhanden ist, einfach Originalbild verwenden

    return image

def make_square(image):
    """Schneidet ein Bild quadratisch zu (zentriert)"""
    width, height = image.size
    if width == height:
        return image  # Bereits quadratisch

    # Zuschneiden auf quadratisches Format (mittig)
    side_length = min(width, height)
    left = (width - side_length) // 2
    top = (height - side_length) // 2
    right = left + side_length
    bottom = top + side_length

    return image.crop((left, top, right, bottom))

# Alle Bilder im Ordner durchgehen
for filename in os.listdir(input_folder):
    if filename.lower().endswith((".jpg", ".jpeg", ".png")):  # Nur Bilddateien
        img_path = os.path.join(input_folder, filename)
        img = Image.open(img_path)

        # Bild korrekt ausrichten
        img = correct_orientation(img)

        # Quadrat erstellen und verkleinern
        img = make_square(img)
        img = img.resize((target_size, target_size), Image.LANCZOS)

        # Speichern
        output_path = os.path.join(output_folder, filename)
        img.save(output_path)
        print(f"✔ {filename} verarbeitet → {output_path}")

print("Alle Bilder wurden erfolgreich angepasst und richtig ausgerichtet!")
