
import os
import re
import py5

DATEI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lauf_daten.txt")
FRAGEN = ["Aktuelle 2km-Zeit (mm:ss):", "Zielzeit (mm:ss):", "Neuer Lauf (mm:ss):"]
# Buttons und Dialog: (x, y, Breite, Höhe)
BTN_HISTORIE = (250, 10, 130, 28)
BTN_NEUSTART = (395, 10, 95, 28)
DLG_JA = (120, 170, 100, 35)
DLG_NEIN = (280, 170, 100, 35)

zeiten = []    # [Start, Ziel, Lauf 1, Lauf 2, ...] in Sekunden
eingabe = ""
meldung = ""
ansicht = "eingabe"      # "eingabe" oder "historie"
bestaetigung = False     # True = Dialog ist offen

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
    global eingabe, meldung, ansicht, bestaetigung
    zeiten.clear()
    eingabe, meldung, ansicht, bestaetigung = "", "", "eingabe", False
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


def im_feld(feld):
    x, y, w, h = feld
    return x <= py5.mouse_x <= x + w and y <= py5.mouse_y <= y + h


def button(feld, beschriftung, farbe):
    py5.fill(*farbe)
    py5.rect(*feld)
    py5.fill(255)
    py5.text_size(14)
    py5.text(beschriftung, feld[0] + 12, feld[1] + feld[3] - 9)
    py5.text_size(18)


def zeichne_eingabe():
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


def zeichne_historie():
    py5.fill(0)
    py5.text("Running-History", 20, 35)
    if len(zeiten) < 2:
        py5.text("Noch keine Daten.", 20, 80)
        return

    werte = zeiten[:1] + zeiten[2:]  # Start + alle Läufe
    ziel = zeiten[1]
    tief, hoch = min(werte + [ziel]) - 10, max(werte) + 10
    x0, x1, y0, y1 = 60, 470, 70, 250

    def x_pos(i):
        return x0 + (x1 - x0) * i / max(1, len(werte) - 1)

    def y_pos(t):  # schnellere Zeit = weiter oben
        return py5.remap(t, tief, hoch, y0, y1)

    py5.stroke(0)
    py5.line(x0, y0, x0, y1)
    py5.line(x0, y1, x1, y1)
    py5.stroke(80, 180, 60)  # Ziellinie
    py5.line(x0, y_pos(ziel), x1, y_pos(ziel))

    py5.stroke(30, 90, 160)  # Verlauf
    py5.stroke_weight(2)
    py5.no_fill()
    py5.begin_shape()
    for i, t in enumerate(werte):
        py5.vertex(x_pos(i), y_pos(t))
    py5.end_shape()

    py5.stroke_weight(1)
    py5.stroke(0)
    py5.text_size(12)
    for i, t in enumerate(werte):
        py5.fill(30, 90, 160)
        py5.circle(x_pos(i), y_pos(t), 8)
        py5.fill(0)
        py5.text(txt(t), x_pos(i) - 12, y_pos(t) - 10)
        py5.text("S" if i == 0 else str(i), x_pos(i) - 3, y1 + 16)
    py5.fill(80, 180, 60)
    py5.text(f"Ziel {txt(ziel)}", x0 + 5, y_pos(ziel) - 5)
    py5.text_size(18)


def zeichne_dialog():
    py5.fill(0, 150)
    py5.rect(0, 0, 500, 320)  # Hintergrund abdunkeln
    py5.fill(255)
    py5.rect(100, 100, 300, 130)
    py5.fill(0)
    py5.text("Wirklich alles löschen?", 130, 140)
    button(DLG_JA, "Ja", (200, 60, 60))
    button(DLG_NEIN, "Nein", (80, 180, 60))


# ---------- Hauptfunktionen von py5 ----------
def setup():
    py5.size(500, 320)
    py5.text_size(18)
    laden()


def draw():
    py5.background(245)
    if ansicht == "eingabe":
        zeichne_eingabe()
    else:
        zeichne_historie()
    button(BTN_HISTORIE, "Zurück" if ansicht == "historie" else "Running-History", (30, 90, 160))
    button(BTN_NEUSTART, "Neustart", (200, 60, 60))
    if bestaetigung:
        zeichne_dialog()


def key_pressed():
    global eingabe, bestaetigung
    k = py5.key
    if bestaetigung:  # Dialog offen: nur J / N
        if k in ("j", "J"):
            neustart()
        elif k in ("n", "N"):
            bestaetigung = False
    elif k in ("n", "N"):
        bestaetigung = True
    elif ansicht == "eingabe":
        if k in ("\n", "\r"):
            bestaetigen()
        elif k in ("\b", chr(127)):
            eingabe = eingabe[:-1]
        elif len(k) == 1 and k in "0123456789:" and len(eingabe) < 5:
            eingabe += k


def mouse_pressed():
    global ansicht, bestaetigung
    if bestaetigung:  # Dialog offen: nur Ja / Nein
        if im_feld(DLG_JA):
            neustart()
        elif im_feld(DLG_NEIN):
            bestaetigung = False
    elif im_feld(BTN_NEUSTART):
        bestaetigung = True
    elif im_feld(BTN_HISTORIE):
        ansicht = "historie" if ansicht == "eingabe" else "eingabe"


py5.run_sketch()
