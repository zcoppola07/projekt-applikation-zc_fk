import os
import re
import py5

DATEI = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lauf_daten.txt")
FRAGEN = ["Deine aktuelle 2-km-Zeit", "Deine Zielzeit", "Neuen Lauf eintragen"]
PAPIER, TINTE, GRAU = "#F5F4EF", "#182D34", "#50636A"
PETROL, MINT, WEISS = "#11695F", "#DCEDE6", "#FFFFFF"
# Klickflächen: x, y, Breite, Höhe
BTN_HISTORIE, BTN_NEUSTART = (337, 21, 97, 36), (444, 21, 108, 36)
BTN_SPEICHERN = (383, 141, 145, 40)
ZEITFELD = (48, 130, 310, 62)
DLG_JA, DLG_NEIN = (297, 218, 123, 38), (160, 218, 123, 38)

zeiten = []    # [Start, Ziel, Lauf 1, Lauf 2, ...] in Sekunden
eingabe = ""
feld_aktiv = False
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


def schrift(text, x, y, groesse, farbe=TINTE):
    py5.fill(farbe)
    py5.text_size(groesse)
    py5.text(text, x, y)


def flaeche(x, y, breite, hoehe, farbe, radius=12):
    py5.no_stroke()
    py5.fill(farbe)
    py5.rect(x, y, breite, hoehe, radius)


def button(feld, text, hintergrund, farbe):
    x, y, w, h = feld
    flaeche(x, y, w, h, hintergrund, 8)
    py5.text_align(py5.CENTER, py5.CENTER)
    schrift(text, x + w / 2, y + h / 2, 15, farbe)
    py5.text_align(py5.LEFT, py5.BASELINE)


def zeichne_eingabe():
    flaeche(28, 82, 524, 165, WEISS)
    schrift(FRAGEN[min(len(zeiten), 2)], 48, 116, 21)
    flaeche(*ZEITFELD, MINT if feld_aktiv else PAPIER, 8)
    schrift(eingabe or "mm:ss", 62, 172, 32, TINTE if eingabe else GRAU)
    if feld_aktiv and py5.millis() % 1000 < 550:
        x = 62 + py5.text_width(eingabe)
        flaeche(x, 145, 2, 34, PETROL, 0)
    button(BTN_SPEICHERN, "Speichern ↵", PETROL, WEISS)
    schrift(meldung, 48, 224, 16, PETROL)
    if len(zeiten) >= 2:
        anteil = fortschritt()
        schrift(f"Fortschritt zum Ziel   {anteil:.0%}", 32, 292, 21)
        flaeche(32, 310, 516, 12, MINT, 6)
        if anteil > 0:
            flaeche(32, 310, 516 * anteil, 12, PETROL, 6)
        schrift(f"Start {txt(zeiten[0])}     Ziel {txt(zeiten[1])}     Läufe {len(zeiten) - 2}", 32, 352, 15, GRAU)


def zeichne_historie():
    flaeche(28, 82, 524, 290, WEISS)
    schrift("Laufverlauf", 48, 120, 23)
    if len(zeiten) < 2:
        schrift("Trage zuerst Start- und Zielzeit ein.", 48, 175, 17, GRAU)
        return

    werte = zeiten[:1] + zeiten[2:]
    ziel = zeiten[1]
    schrift(f"Ziel   {txt(ziel)}", 420, 120, 16, PETROL)
    tief, hoch = min(werte + [ziel]) - 10, max(werte) + 10

    def y_pos(zeit):
        return py5.remap(zeit, tief, hoch, 174, 306)

    py5.stroke(PETROL)
    py5.line(66, y_pos(ziel), 506, y_pos(ziel))
    # Alle Läufe zeichnen, bei vielen Läufen nur einzelne Punkte beschriften.
    for i, zeit in enumerate(werte):
        x = 66 + 440 * i / max(1, len(werte) - 1)
        y = y_pos(zeit)
        if i > 0:
            py5.stroke(TINTE)
            py5.line(letztes_x, letztes_y, x, y)
        py5.no_stroke()
        py5.fill(TINTE)
        py5.circle(x, y, 8)
        if len(werte) <= 8 or i in (0, len(werte) - 1):
            schrift(txt(zeit), x - 14, y - 10, 13)
            schrift("Start" if i == 0 else str(i), x - 10, 345, 13, GRAU)
        letztes_x, letztes_y = x, y


def zeichne_dialog():
    py5.fill(15, 32, 38, 145)
    py5.rect(0, 0, py5.width, py5.height)
    flaeche(90, 110, 400, 170, WEISS)
    schrift("Laufdaten löschen?", 120, 154, 24)
    schrift("Alle gespeicherten Zeiten werden gelöscht.", 120, 186, 16, GRAU)
    button(DLG_NEIN, "Abbrechen", PAPIER, TINTE)
    button(DLG_JA, "Löschen", "#A43E36", WEISS)


def settings():
    py5.size(580, 400)


def setup():
    py5.text_font(py5.create_font("SansSerif", 20))
    laden()


def draw():
    py5.background(PAPIER)
    schrift("2 km / Lauftracker", 28, 48, 28)
    button(BTN_HISTORIE, "Zurück" if ansicht == "historie" else "Verlauf", PETROL, WEISS)
    button(BTN_NEUSTART, "Neustart", WEISS, TINTE)
    if ansicht == "eingabe":
        zeichne_eingabe()
    else:
        zeichne_historie()
    if bestaetigung:
        zeichne_dialog()


def key_typed():
    global eingabe
    if feld_aktiv and py5.key in "0123456789:" and len(eingabe) < 5:
        eingabe += py5.key


def key_pressed():
    global eingabe, bestaetigung, feld_aktiv
    if bestaetigung:
        if py5.key in ("j", "J"):
            neustart()
        elif py5.key in ("n", "N"):
            bestaetigung = False
    elif py5.key in ("n", "N"):
        bestaetigung = True
        feld_aktiv = False
    elif feld_aktiv:
        if py5.key in ("\n", "\r"):
            bestaetigen()
        elif py5.key in ("\b", chr(127)):
            eingabe = eingabe[:-1]


def mouse_pressed():
    global ansicht, bestaetigung, feld_aktiv
    feld_aktiv = False
    if bestaetigung:  # Dialog offen: nur Ja / Nein
        if im_feld(DLG_JA):
            neustart()
        elif im_feld(DLG_NEIN):
            bestaetigung = False
    elif im_feld(BTN_NEUSTART):
        bestaetigung = True
    elif im_feld(BTN_HISTORIE):
        ansicht = "historie" if ansicht == "eingabe" else "eingabe"
    elif ansicht == "eingabe":
        if im_feld(BTN_SPEICHERN):
            bestaetigen()
            feld_aktiv = True
        else:
            feld_aktiv = im_feld(ZEITFELD)


py5.run_sketch()
