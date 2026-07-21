"""Compile et exécute du C, rend un résultat. Aucune UI ici.
Le code de sortie du programme fait foi, pas le texte affiché."""
from dataclasses import dataclass
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading


def _nom_binaire(base: str) -> str:
    """Sous Windows, gcc (MinGW) ajoute .exe à la sortie ; on nomme donc le binaire
    avec son extension pour que le chemin lancé ensuite corresponde au fichier produit."""
    return base + ".exe" if os.name == "nt" else base


def _masquer_chemin_temp(texte: str, dossier: str) -> str:
    """Retire le chemin absolu du dossier temporaire des diagnostics du compilateur.

    Deux raisons : ce chemin (par ex. C:\\Users\\<compte>\\AppData\\Local\\Temp\\...) fait
    fuiter le nom de compte Windows de l'utilisateur dans chaque message d'erreur, et il
    est long et intimidant pour un débutant. On ne garde que le nom de fichier, donc gcc
    affiche « programme.c:6:10: error: ... » au lieu du chemin complet. On couvre les trois
    formes de séparateur car gcc (MinGW) peut renvoyer le chemin avec \\ ou /.

    On retire d'abord le dossier précis (laisse juste « programme.c »), puis, en repli, la
    racine temp du système : ainsi un fichier source écrit dans un autre dossier temp par
    l'appelant (test_eleve.c, soumission.c...) perd aussi le préfixe qui contient le nom de
    compte, même si son dossier exact n'est pas celui passé ici."""
    prefixes = [dossier + os.sep, dossier + "\\", dossier + "/"]
    racine_temp = tempfile.gettempdir()
    prefixes += [racine_temp + os.sep, racine_temp + "\\", racine_temp + "/"]
    for prefixe in prefixes:
        texte = texte.replace(prefixe, "")
    return texte


# Sous Windows, l'appli est packagée sans console (--windowed). Lancer un programme
# console (gcc, le binaire compilé) ferait alors clignoter une fenêtre cmd. Ce drapeau
# la supprime. Vaut 0 hors Windows, où il est sans objet.
_SANS_FENETRE = getattr(subprocess, "CREATE_NO_WINDOW", 0)

# Plafond de la sortie capturee d'un programme etudiant. Sans lui, un programme qui
# inonde stdout en boucle infinie ferait bufferiser toute sa sortie en RAM jusqu'au
# delai (des centaines de Mo). Au-dela, on jette : la memoire reste bornee.
_TAILLE_MAX_SORTIE = 10 * 1024 * 1024


def _executer_cape(cmd, entree="", timeout=15, cap=_TAILLE_MAX_SORTIE):
    """Lance cmd, envoie `entree` sur son entree standard, capture stdout+stderr fusionnes
    mais PLAFONNES a `cap` octets (au-dela on continue a lire et jeter, pour ne pas bloquer
    le programme sur un tube plein, mais sans grossir la memoire). Coupe au bout de
    `timeout` secondes. Renvoie (returncode, texte, delai, tronque)."""
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, creationflags=_SANS_FENETRE)
    tampon = bytearray()
    etat = {"tronque": False}

    def _lire():
        try:
            while True:
                bloc = proc.stdout.read(65536)
                if not bloc:
                    break
                reste = cap - len(tampon)
                if reste > 0:
                    tampon.extend(bloc[:reste])
                if len(tampon) >= cap:
                    etat["tronque"] = True
                # on continue a vider le tube meme apres le plafond, sinon le programme
                # se bloque sur un tube plein et on ne peut plus le tuer proprement.
        except (ValueError, OSError):
            # le tube a ete ferme sous nos pieds : cas du delai depasse, ou le fil
            # survit a la fermeture ci-dessous. Rien a sauver, on sort sans bruit.
            pass

    lecteur = threading.Thread(target=_lire, daemon=True)
    lecteur.start()
    try:
        if entree:
            proc.stdin.write(entree.encode("utf-8"))
    except (BrokenPipeError, OSError):
        pass
    try:
        proc.stdin.close()
    except OSError:
        pass
    delai = False
    try:
        proc.wait(timeout=timeout)
    except subprocess.TimeoutExpired:
        delai = True
        proc.kill()
        proc.wait()
    lecteur.join(timeout=2)
    # Fermeture explicite du tube. Sans elle l'objet fichier n'est libere qu'au passage
    # du ramasse-miettes : ca se voit d'abord comme un ResourceWarning dans les tests,
    # mais le vrai cout est ailleurs. L'atelier appelle cette fonction a chaque « Tester »,
    # et une session d'etudiant en enchaine des dizaines : autant de descripteurs retenus
    # sans raison dans un processus qui reste ouvert des heures.
    try:
        proc.stdout.close()
    except OSError:
        pass
    # decodage + fins de ligne universelles (comme le faisait subprocess.run en mode texte) :
    # sous Windows le programme C emet \r\n, mais les fragments attendus utilisent \n.
    texte = tampon.decode("utf-8", errors="replace").replace("\r\n", "\n").replace("\r", "\n")
    return proc.returncode, texte, delai, etat["tronque"]


def assurer_compilateur_sur_path() -> None:
    """Ajoute w64devkit\\bin au PATH s'il est trouvé à côté de l'application. Ainsi gcc
    est disponible même si l'atelier est lancé sans passer par lancer.bat (double-clic
    direct sur l'exe). Sans effet si gcc est déjà là ou si le dossier est absent."""
    if os.name != "nt" or shutil.which("gcc"):
        return
    # exe figé : à côté de l'exe ; bundle portable : à côté du dossier des sources
    base = Path(sys.executable).parent if getattr(sys, "frozen", False) \
        else Path(__file__).resolve().parent.parent
    wk = base / "w64devkit" / "bin"
    if wk.is_dir():
        os.environ["PATH"] = str(wk) + os.pathsep + os.environ.get("PATH", "")


def _resultat_sans_gcc() -> "Resultat":
    return Resultat(False,
                    "Le compilateur gcc est introuvable.\n"
                    "Lance l'atelier avec lancer.bat (il ajoute le compilateur au PATH), "
                    "ou vérifie que le dossier w64devkit est bien à côté.")

import chemins
from modele_etape import Etape


@dataclass
class Resultat:
    ok: bool
    sortie: str
    # categorie du resultat pour l'instrumentation (surtout porte_programme) :
    # "ok" | "erreur_compilation" | "delai" | "erreur_execution" | "sortie_incomplete" | ""
    categorie: str = ""
    # fragments/libelles manquants quand categorie == "sortie_incomplete", sinon vide
    manquants: tuple = ()


def _compiler_et_lancer(sources: list[Path], includes: list[Path],
                        cflags: list[str] = [], libs: list[str] = [],
                        timeout: int = 15) -> Resultat:
    with tempfile.TemporaryDirectory() as d:
        binaire = Path(d) / _nom_binaire("prog")
        cmd = ["gcc", "-Wall", "-Wno-unused-parameter", "-Wno-unused-variable"]
        cmd += [f"-I{i}" for i in includes]
        cmd += cflags
        cmd += [str(s) for s in sources]
        cmd += libs
        cmd += ["-lm", "-o", str(binaire)]
        try:
            comp = subprocess.run(cmd, capture_output=True, encoding="utf-8",
                                  errors="replace", creationflags=_SANS_FENETRE)
        except FileNotFoundError:
            return _resultat_sans_gcc()
        if comp.returncode != 0:
            return Resultat(False, "Erreur de compilation :\n" + _masquer_chemin_temp(comp.stderr, d))
        try:
            run = subprocess.run([str(binaire)], capture_output=True, encoding="utf-8",
                                 errors="replace", creationflags=_SANS_FENETRE,
                                 timeout=timeout)
        except subprocess.TimeoutExpired:
            return Resultat(False, "Le test a dépassé le délai, boucle infinie probable.")
        return Resultat(run.returncode == 0, run.stdout + run.stderr)


@dataclass
class ResultatTest:
    test_solide: bool
    passe_corrige: bool
    attrape_bug: bool
    sortie: str


def _includes_jalon() -> list[Path]:
    # les en-têtes projet viennent de la copie de build, la casse y est corrigée
    return [chemins.BUILD_COPY] + chemins.SDL_INCLUDES


def juger_test(etape: Etape, test_eleve: str) -> ResultatTest:
    """Juge le test de l'étudiant : il doit passer le corrigé et attraper le bug planté."""
    includes = [etape.dossier] + _includes_jalon()
    libs = chemins.libs_sdl(avec_ttf_image=False)
    with tempfile.TemporaryDirectory() as d:
        t = Path(d) / "test_eleve.c"
        t.write_text(test_eleve, encoding="utf-8")
        stubs = etape.dossier / "stubs.c"

        r_ok = _compiler_et_lancer([etape.dossier / "corrige.c", t, stubs], includes, libs=libs)
        r_bug = _compiler_et_lancer([etape.dossier / "corrige_buggue.c", t, stubs], includes, libs=libs)

        passe_corrige = r_ok.ok
        attrape_bug = (not r_bug.ok) and ("Erreur de compilation" not in r_bug.sortie)
        solide = passe_corrige and attrape_bug
        sortie = ("Contre le corrigé, ton test doit passer :\n" + r_ok.sortie +
                  "\nContre une version buggée, ton test doit échouer :\n" + r_bug.sortie)
        return ResultatTest(solide, passe_corrige, attrape_bug, sortie)


def porte_jalon(etape: Etape, code_eleve: str, test_eleve: str) -> Resultat:
    """Lance le test solide de l'étudiant contre son propre code. Code 0 = porte ouverte."""
    includes = [etape.dossier] + _includes_jalon()
    libs = chemins.libs_sdl(avec_ttf_image=False)
    with tempfile.TemporaryDirectory() as d:
        code = Path(d) / etape.fichier_edite
        code.write_text(code_eleve, encoding="utf-8")
        t = Path(d) / "test_eleve.c"
        t.write_text(test_eleve, encoding="utf-8")
        return _compiler_et_lancer([code, t, etape.dossier / "stubs.c"], includes, libs=libs)


# Sources de la bibliothèque du projet suffisantes pour un menu. Confirmées présentes
# dans la copie de build. On évite les fichiers de gameplay incomplets de l'archive.
_SOURCES_APERCU = [
    "Bibliotheque_source/Initialisation_SDL.c",
    "Bibliotheque_source/OutilsDessin.c",
    "Bibliotheque_source/OutilsBouton.c",
    "Bibliotheque_source/OutilsCouleur.c",
    "Bibliotheque_source/OutilsZoneTexte.c",
    "InitialisationTexture.c",
    "VariablesGlobales.c",
]


def construire_apercu(etape: Etape, code_eleve: str) -> tuple[Resultat, Path | None]:
    """Construit le binaire d'aperçu : le code de l'étudiant plus apercu.c plus la
    bibliothèque du projet. Rend (Resultat, chemin_binaire_ou_None).
    Le dossier temporaire est volontairement persistant, le binaire doit survivre à
    l'appel pour que lancer_jeu puisse l'ouvrir, il reste dans /tmp jusqu'au redémarrage."""
    persistant = Path(tempfile.mkdtemp(prefix="apercu_"))
    code = persistant / etape.fichier_edite
    code.write_text(code_eleve, encoding="utf-8")
    binaire = persistant / "apercu"

    sources = [code, etape.dossier / "apercu.c"]
    sources += [chemins.BUILD_COPY / s for s in _SOURCES_APERCU]
    includes = [etape.dossier, chemins.BUILD_COPY, chemins.BUILD_COPY / "Bibliotheque_header"]
    includes += chemins.SDL_INCLUDES

    cmd = ["gcc", "-Wall", "-Wno-unused-parameter", "-Wno-unused-variable"]
    cmd += [f"-I{i}" for i in includes]
    cmd += chemins.cflags_sdl(avec_ttf_image=True)
    cmd += [str(s) for s in sources]
    cmd += chemins.libs_sdl(avec_ttf_image=True)
    cmd += ["-lm", "-o", str(binaire)]
    comp = subprocess.run(cmd, capture_output=True, encoding="utf-8",
                          errors="replace", creationflags=_SANS_FENETRE)
    if comp.returncode != 0:
        message = _masquer_chemin_temp(comp.stderr, str(persistant))
        shutil.rmtree(persistant, ignore_errors=True)
        return Resultat(False, "Erreur de compilation de l'aperçu :\n" + message), None
    return Resultat(True, "Aperçu construit."), binaire


def lancer_jeu(etape: Etape, code_eleve: str) -> Resultat:
    """Construit l'aperçu puis ouvre la fenêtre. Les assets sont chargés en chemin
    relatif, donc on lance depuis la copie de build."""
    resultat, binaire = construire_apercu(etape, code_eleve)
    if not resultat.ok:
        return resultat
    subprocess.Popen([str(binaire)], cwd=str(chemins.BUILD_COPY),
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     creationflags=_SANS_FENETRE)
    return Resultat(True, "Fenêtre lancée. Échap pour fermer.")


def porte_perso(etape: Etape, code_eleve: str) -> Resultat:
    """Compile le code de l'étudiant avec tests.c de l'étape, exécute, code 0 = porte ouverte."""
    with tempfile.TemporaryDirectory() as d:
        soumission = Path(d) / "soumission.c"
        soumission.write_text(code_eleve, encoding="utf-8")
        sources = [soumission, etape.dossier / "tests.c"]
        includes = [etape.dossier]
        return _compiler_et_lancer(sources, includes)


def porte_programme(etape: Etape, code_eleve: str) -> Resultat:
    """Compile le programme complet de l'étudiant, qui contient son propre main, l'exécute
    avec l'entrée standard fixée par l'étape, et juge la sortie.

    Si etape.sortie_attendue et etape.sortie_motifs sont vides, la porte s'ouvre dès que
    le programme compile et s'exécute sans erreur. C'est une séance d'exploration. Sinon :
      - chaque fragment littéral de sortie_attendue doit apparaître tel quel ;
      - chaque motif de sortie_motifs (regex + libellé lisible) doit se retrouver dans la
        sortie. Les motifs servent quand l'énoncé n'impose pas de valeur précise : on
        vérifie le libellé et le format, pas la valeur (ex. ex01, les types)."""
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "programme.c"
        src.write_text(code_eleve, encoding="utf-8")
        binaire = Path(d) / _nom_binaire("prog")
        cmd = ["gcc", "-Wall", "-Wno-unused-parameter", "-Wno-unused-variable",
               f"-I{etape.dossier}", str(src), "-lm", "-o", str(binaire)]
        try:
            comp = subprocess.run(cmd, capture_output=True, encoding="utf-8",
                                  errors="replace", creationflags=_SANS_FENETRE)
        except FileNotFoundError:
            return _resultat_sans_gcc()
        if comp.returncode != 0:
            return Resultat(False, "Erreur de compilation :\n" + _masquer_chemin_temp(comp.stderr, d),
                            categorie="erreur_compilation")
        rc, sortie, delai, tronque = _executer_cape([str(binaire)], etape.entree or "", timeout=15)
        if delai:
            return Resultat(False, "Le programme a dépassé le délai. Attend-il une saisie au clavier ?",
                            categorie="delai")
        if rc != 0:
            return Resultat(False, "Le programme s'est terminé en erreur :\n" + sortie,
                            categorie="erreur_execution")
        attendus = etape.sortie_attendue or []
        manquants = [repr(f) for f in attendus if f not in sortie]
        motifs = etape.sortie_motifs or []
        manquants += [m.get("attendu", m["motif"]) for m in motifs
                      if not re.search(m["motif"], sortie)]
        if manquants:
            return Resultat(False,
                            "Il manque ceci dans ta sortie : " + ", ".join(manquants) +
                            "\n\nSortie obtenue :\n" + (sortie or "(rien)"),
                            categorie="sortie_incomplete", manquants=tuple(manquants))
        note = "" if not tronque else "\n(sortie très volumineuse, tronquée pour l'affichage)"
        return Resultat(True, (sortie if sortie.strip() else "Le programme compile et s'exécute.") + note,
                        categorie="ok")


def porte_logique(espace, fichier_edite: str, code_etudiant: str,
                  harnais: Path, sources: list[str]) -> Resultat:
    """Écrit le code de l'étudiant dans l'espace, compile le harnais logique avec les sources du
    projet et pkg-config sdl3, exécute sans fenêtre et renvoie un Resultat. Le code de sortie
    fait foi.

    Paramètres
    ----------
    espace : EspaceProjet
        La copie de travail déjà initialisée.
    fichier_edite : str
        Chemin du fichier que l'étudiant modifie, relatif à la racine du projet copié,
        par exemple 'SNAKE/GestionJeu.c'.
    code_etudiant : str
        Contenu source à poser dans le fichier édité.
    harnais : Path
        Chemin absolu du fichier de harnais à compiler, par exemple
        chemins.PROJET_CORRIGE / 'tests_logique' / 'test_deplacement.c'.
    sources : list[str]
        Chemins des fichiers .c nécessaires à la compilation, relatifs à la racine du projet copié,
        par exemple ['SNAKE/GestionJeu.c', 'SNAKE/VariablesGlobales.c', 'SNAKE/InitialisationJeu.c'].
    """
    espace.ecrire_fichier(fichier_edite, code_etudiant)
    srcs = [Path(harnais)] + [espace.chemin_racine / s for s in sources]
    includes = [espace.dossier_snake]
    cflags = chemins.cflags_sdl(avec_ttf_image=False)
    libs = chemins.libs_sdl(avec_ttf_image=False)
    return _compiler_et_lancer(srcs, includes, cflags, libs)


def construire_et_jouer_projet(espace, lancer: bool = True) -> Resultat:
    """Lance build.sh sur l'espace et, si le build réussit et que lancer est True, ouvre
    le binaire snake en sous-processus détaché sans bloquer. Renvoie l'erreur de compilation
    si le build échoue. Passer lancer=False dans les tests unitaires pour éviter d'ouvrir
    une fenêtre réelle."""
    build = subprocess.run(
        ["bash", str(espace.build_sh)],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(espace.build_sh.parent),
        creationflags=_SANS_FENETRE,
    )
    if build.returncode != 0:
        return Resultat(False, "Erreur de build :\n" + build.stderr + build.stdout)
    binaire = espace.dossier_snake / "snake"
    if not binaire.exists():
        return Resultat(False, "Le build s'est terminé sans erreur mais le binaire est introuvable.")
    if lancer:
        subprocess.Popen(
            [str(binaire)],
            cwd=str(espace.dossier_snake),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=_SANS_FENETRE,
        )
        return Resultat(True, "Build réussi. Jeu lancé.")
    return Resultat(True, "Build réussi.")
