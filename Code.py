import py5

# ---------- Zustand ----------
zustand = "start"      # start -> ziel -> wochen -> lauf
eingabe = ""           # Text, der gerade getippt wird
meldung = ""           # Feedback oder Fehlermeldung
start_zeit = 0         # in Sekunden
ziel_zeit = 0          # in Sekunden
wochen = 0             # Zeitraum
laeufe = []            # alle eingetragenen Zeiten (Sekunden)

FRAGEN = {
    "start": "Deine aktuelle 2km-Zeit (mm:ss):",
    "ziel": "Deine Zielzeit (mm:ss):",
    "wochen": "Wie viele Wochen hast du Zeit?",
    "lauf": "Neuer Lauf - deine Zeit (mm:ss):",
}


# ---------- Hilfsfunktionen ----------
def zeit_zu_sek(text):
    """'10:30' -> 630. Gibt None zurück, wenn das Format nicht stimmt."""
    teile = text.split(":")
    if len(teile) != 2 or not teile[0].isdigit() or not teile[1].isdigit():
        return None
    if int(teile[1]) > 59:
        return None
    return int(teile[0]) * 60 + int(teile[1])


def sek_zu_text(sek):
    return f"{sek // 60}:{sek % 60:02d}"


def fortschritt():
    """Wert zwischen 0 und 1: wie weit ist die beste Zeit vom Start zum Ziel?"""
    beste = min(laeufe) if laeufe else start_zeit
    anteil = (start_zeit - beste) / (start_zeit - ziel_zeit)
    return max(0, min(1, anteil))


def feedback(neue_zeit):
    """Text nach einem Lauf (laeufe enthält die neue Zeit bereits)."""
    vorher = laeufe[-2] if len(laeufe) > 1 else start_zeit
    diff = vorher - neue_zeit
    if neue_zeit <= ziel_zeit:
        return "Ziel erreicht! Super gemacht!"
    if diff > 0:
        return f"Schneller! {diff} Sekunden besser als zuvor."
    if diff == 0:
        return "Gleiche Zeit wie zuvor. Bleib dran!"
    return f"{-diff} Sekunden langsamer. Kann mal passieren - weiter geht's!"


def bestaetigen():
    """Wird bei Enter aufgerufen und steuert die Zustände."""
    global zustand, eingabe, meldung, start_zeit, ziel_zeit, wochen
    meldung = ""

    if zustand == "wochen":
        if not eingabe.isdigit() or int(eingabe) < 1:
            meldung = "Bitte eine Zahl grösser als 0 eingeben."
            return
        wochen = int(eingabe)
        zustand = "lauf"
        eingabe = ""
        return

    zeit = zeit_zu_sek(eingabe)
    if zeit is None:
        meldung = "Bitte im Format mm:ss eingeben, z.B. 10:30"
        return

    if zustand == "start":
        start_zeit = zeit
        zustand = "ziel"
    elif zustand == "ziel":
        if zeit >= start_zeit:
            meldung = "Die Zielzeit muss schneller sein als deine Startzeit."
            return
        ziel_zeit = zeit
        zustand = "wochen"
    elif zustand == "lauf":
        laeufe.append(zeit)
        meldung = feedback(zeit)
    eingabe = ""


# ---------- Zeichnen ----------
def zeichne_eingabe():
    py5.fill(0)
    py5.text_size(20)
    py5.text(FRAGEN[zustand], 30, 140)
    py5.fill(255)
    py5.stroke(0)
    py5.rect(30, 155, 200, 40)
    py5.fill(0)
    cursor = "|" if py5.frame_count % 60 < 30 else ""
    py5.text(eingabe + cursor, 40, 183)
    py5.no_stroke()


def zeichne_balken():
    py5.fill(220)
    py5.rect(30, 260, 540, 30)
    py5.fill(80, 180, 60)
    py5.rect(30, 260, 540 * fortschritt(), 30)
    py5.fill(0)
    py5.text_size(16)
    py5.text(f"Start {sek_zu_text(start_zeit)}", 30, 315)
    py5.text(f"Ziel {sek_zu_text(ziel_zeit)}", 500, 315)
    py5.text(f"{int(fortschritt() * 100)} %", 270, 250)


def zeichne_laeufe():
    py5.fill(0)
    py5.text_size(16)
    py5.text(f"Zeitraum: {wochen} Wochen  |  Läufe: {len(laeufe)}", 30, 350)
    letzte = laeufe[-5:]
    for i, zeit in enumerate(letzte):
        nr = len(laeufe) - len(letzte) + i + 1
        py5.text(f"Lauf {nr}: {sek_zu_text(zeit)}", 30, 380 + i * 22)


def setup():
    py5.size(600, 500)


def draw():
    py5.background(245)
    py5.fill(0)
    py5.text_size(28)
    py5.text("2km Lauf-Tracker", 30, 50)

    zeichne_eingabe()

    py5.text_size(18)
    py5.fill(30, 90, 160)
    py5.text(meldung, 30, 225)

    if zustand == "lauf":
        zeichne_balken()
        zeichne_laeufe()


def key_pressed():
    global eingabe
    taste = py5.key
    if taste in ("\n", "\r"):
        bestaetigen()
    elif taste in ("\b", chr(127)):
        eingabe = eingabe[:-1]
    elif len(taste) == 1 and (taste.isdigit() or taste == ":") and len(eingabe) < 5:
        eingabe += taste


py5.run_sketch()
