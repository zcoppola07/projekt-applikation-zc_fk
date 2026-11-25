
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

#Running-History Start
historie = False
_draw, _key_pressed = draw, key_pressed
BTN = (340, 10, 150, 28)  # x, y, Breite, Höhe


def historie_zeichnen():
    py5.fill(0)
    py5.text("Running-History", 20, 35)
    werte = zeiten[:1] + zeiten[2:]  # Start + alle Läufe
    if len(zeiten) < 2:
        py5.text("Noch keine Daten.", 20, 80)
        return
    ziel = zeiten[1]
    lo, hi = min(werte + [ziel]) - 10, max(werte) + 10
    x0, x1, y0, y1 = 60, 470, 70, 250
    px = lambda i: x0 + (x1 - x0) * i / max(1, len(werte) - 1)
    pyy = lambda t: py5.remap(t, lo, hi, y0, y1)

    py5.stroke(0)
    py5.line(x0, y0, x0, y1)
    py5.line(x0, y1, x1, y1)
    py5.stroke(80, 180, 60)  # Ziellinie
    py5.line(x0, pyy(ziel), x1, pyy(ziel))

    py5.stroke(30, 90, 160)
    py5.stroke_weight(2)
    py5.no_fill()
    py5.begin_shape()
    for i, t in enumerate(werte):
        py5.vertex(px(i), pyy(t))
    py5.end_shape()

    py5.stroke_weight(1)
    py5.stroke(0)
    py5.text_size(12)
    for i, t in enumerate(werte):
        py5.fill(30, 90, 160)
        py5.circle(px(i), pyy(t), 8)
        py5.fill(0)
        py5.text(txt(t), px(i) - 12, pyy(t) - 10)
        py5.text("S" if i == 0 else str(i), px(i) - 3, y1 + 16)
    py5.fill(80, 180, 60)
    py5.text(f"Ziel {txt(ziel)}", x0 + 5, pyy(ziel) - 5)
    py5.text_size(18)


def draw():
    if historie:
        py5.background(245)
        historie_zeichnen()
    else:
        _draw()
    py5.fill(30, 90, 160)
    py5.rect(*BTN)
    py5.fill(255)
    py5.text_size(14)
    py5.text("Zurück" if historie else "Running-History", BTN[0] + 12, BTN[1] + 20)
    py5.text_size(18)


def mouse_pressed():
    global historie
    x, y, w, h = BTN
    if x <= py5.mouse_x <= x + w and y <= py5.mouse_y <= y + h:
        historie = not historie


def key_pressed():
    if not historie:  # in der Historie keine Eingabe
        _key_pressed()
#Ende Running-History


#Neustart-Bestätigung
bestaetigung = False
_draw2, _key2, _mouse2 = draw, key_pressed, mouse_pressed
JA, NEIN = (120, 170, 100, 35), (280, 170, 100, 35)


def im_feld(r):
    x, y, w, h = r
    return x <= py5.mouse_x <= x + w and y <= py5.mouse_y <= y + h


def draw():
    _draw2()
    if bestaetigung:
        py5.fill(0, 150)
        py5.rect(0, 0, 500, 320)  # Hintergrund abdunkeln
        py5.fill(255)
        py5.rect(100, 100, 300, 130)
        py5.fill(0)
        py5.text("Bist du dir sicher?", 150, 140)
        py5.fill(80, 180, 60)
        py5.rect(*JA)
        py5.fill(200, 60, 60)
        py5.rect(*NEIN)
        py5.fill(255)
        py5.text_size(14)
        py5.text("Ja", JA[0] + 38, JA[1] + 23)
        py5.text("Nein", NEIN[0] + 32, NEIN[1] + 23)
        py5.text_size(18)


def key_pressed():
    global bestaetigung
    k = py5.key
    if bestaetigung:
        if k in ("j", "J", "\n", "\r"):
            neustart()
            bestaetigung = False
        elif k in ("n", "N"):
            bestaetigung = False
    elif k in ("n", "N") and not historie:
        bestaetigung = True  # statt direktem Neustart erst fragen
    else:
        _key2()


def mouse_pressed():
    global bestaetigung
    if bestaetigung:
        if im_feld(JA):
            neustart()
            bestaetigung = False
        elif im_feld(NEIN):
            bestaetigung = False
    else:
        _mouse2()
#Ende Neustart-Bestätigung


py5.run_sketch()
