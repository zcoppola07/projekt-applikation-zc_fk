
import os
import re
import py5

DATEI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lauf_daten.txt")
FRAGEN = ["Aktuelle 2km-Zeit (mm:ss):", "Zielzeit (mm:ss):", "Neuer Lauf (mm:ss):"]

zeiten = []    # [Start, Ziel, Lauf 1, Lauf 2, ...] in Sekunden
eingabe = ""
meldung = ""


def sek(text):
    """'10:30' -> 630 (None bei falschem Format)."""
    m = re.fullmatch(r"(\d+):([0-5]\d)", text.strip())
    return int(m[1]) * 60 + int(m[2]) if m else None


def txt(s):
    return f"{s // 60}:{s % 60:02d}"


def fortschritt():
    start, ziel = zeiten[0], zeiten[1]
    beste = min(zeiten[:1] + zeiten[2:])
    return max(0, min(1, (start - beste) / (start - ziel)))


def speichern():
    """Eine Zeit pro Zeile: 1. Start, 2. Ziel, danach alle Läufe."""
    with open(DATEI, "w", encoding="utf-8") as f:
        f.write("\n".join(txt(t) for t in zeiten))


def laden():
    if not os.path.exists(DATEI):
        return
    with open(DATEI, encoding="utf-8") as f:
        werte = [sek(zeile) for zeile in f.read().splitlines()]
    if None in werte or (len(werte) > 1 and werte[1] >= werte[0]):
        return  # Datei kaputt: neu beginnen
    zeiten.extend(werte)


def neustart():
    global eingabe, meldung
    zeiten.clear()
    eingabe, meldung = "", ""
    if os.path.exists(DATEI):
        os.remove(DATEI)


def bestaetigen():
    global eingabe, meldung
    zeit = sek(eingabe)
    if zeit is None:
        meldung = "Format: mm:ss, z.B. 10:30"
        return
    if len(zeiten) == 1 and zeit >= zeiten[0]:
        meldung = "Ziel muss schneller als der Start sein."
        return

    zeiten.append(zeit)
    meldung = ""
    if len(zeiten) > 2:  # es war ein Lauf -> Feedback
        vorher = zeiten[-2] if len(zeiten) > 3 else zeiten[0]
        if zeit <= zeiten[1]:
            meldung = "Ziel erreicht! Super!"
        elif zeit < vorher:
            meldung = f"Schneller! {vorher - zeit} s besser."
        elif zeit == vorher:
            meldung = "Gleiche Zeit. Dranbleiben!"
        else:
            meldung = f"{zeit - vorher} s langsamer. Kopf hoch!"
    eingabe = ""
    speichern()


def setup():
    py5.size(500, 320)
    py5.text_size(18)
    laden()


def draw():
    py5.background(245)
    py5.fill(0)
    py5.text("2km Lauf-Tracker", 20, 35)
    py5.text(FRAGEN[min(len(zeiten), 2)], 20, 80)
    py5.text(eingabe + "|", 20, 112)
    py5.fill(30, 90, 160)
    py5.text(meldung, 20, 150)
    if len(zeiten) >= 2:
        py5.fill(220)
        py5.rect(20, 185, 460, 25)
        py5.fill(80, 180, 60)
        py5.rect(20, 185, 460 * fortschritt(), 25)
        py5.fill(0)
        py5.text(f"{txt(zeiten[0])} -> {txt(zeiten[1])}   Läufe: {len(zeiten) - 2}", 20, 240)
    py5.text_size(12)
    py5.text("Taste N = Neustart", 20, 305)
    py5.text_size(18)


def key_pressed():
    global eingabe
    k = py5.key
    if k in ("\n", "\r"):
        bestaetigen()
    elif k in ("\b", chr(127)):
        eingabe = eingabe[:-1]
    elif len(k) == 1 and k in "0123456789:" and len(eingabe) < 5:
        eingabe += k
    elif k in ("n", "N"):
        neustart()


py5.run_sketch()