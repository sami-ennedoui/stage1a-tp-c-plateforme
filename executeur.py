"""Compile et exécute du C, rend un résultat. Aucune UI ici.
Le code de sortie du programme fait foi, pas le texte affiché."""
from dataclasses import dataclass
from pathlib import Path
import os
import shutil
import subprocess
import tempfile


def _nom_binaire(base: str) -> str:
    """Sous Windows, gcc (MinGW) ajoute .exe à la sortie ; on nomme donc le binaire
    avec son extension pour que le chemin lancé ensuite corresponde au fichier produit."""
    return base + ".exe" if os.name == "nt" else base

import chemins
from modele_etape import Etape


@dataclass
class Resultat:
    ok: bool
    sortie: str


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
        comp = subprocess.run(cmd, capture_output=True, text=True)
        if comp.returncode != 0:
            return Resultat(False, "Erreur de compilation :\n" + comp.stderr)
        try:
            run = subprocess.run([str(binaire)], capture_output=True, text=True,
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
    comp = subprocess.run(cmd, capture_output=True, text=True)
    if comp.returncode != 0:
        shutil.rmtree(persistant, ignore_errors=True)
        return Resultat(False, "Erreur de compilation de l'aperçu :\n" + comp.stderr), None
    return Resultat(True, "Aperçu construit."), binaire


def lancer_jeu(etape: Etape, code_eleve: str) -> Resultat:
    """Construit l'aperçu puis ouvre la fenêtre. Les assets sont chargés en chemin
    relatif, donc on lance depuis la copie de build."""
    resultat, binaire = construire_apercu(etape, code_eleve)
    if not resultat.ok:
        return resultat
    subprocess.Popen([str(binaire)], cwd=str(chemins.BUILD_COPY),
                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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

    Si etape.sortie_attendue est vide, la porte s'ouvre dès que le programme compile et
    s'exécute sans erreur. C'est une séance d'exploration. Sinon, chaque fragment de
    etape.sortie_attendue doit apparaître dans la sortie standard pour ouvrir la porte."""
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "programme.c"
        src.write_text(code_eleve, encoding="utf-8")
        binaire = Path(d) / _nom_binaire("prog")
        cmd = ["gcc", "-Wall", "-Wno-unused-parameter", "-Wno-unused-variable",
               f"-I{etape.dossier}", str(src), "-lm", "-o", str(binaire)]
        comp = subprocess.run(cmd, capture_output=True, text=True)
        if comp.returncode != 0:
            return Resultat(False, "Erreur de compilation :\n" + comp.stderr)
        try:
            run = subprocess.run([str(binaire)], capture_output=True, text=True,
                                 timeout=15, input=etape.entree or "")
        except subprocess.TimeoutExpired:
            return Resultat(False, "Le programme a dépassé le délai. Attend-il une saisie au clavier ?")
        sortie = run.stdout + run.stderr
        if run.returncode != 0:
            return Resultat(False, "Le programme s'est terminé en erreur :\n" + sortie)
        attendus = etape.sortie_attendue or []
        manquants = [f for f in attendus if f not in run.stdout]
        if manquants:
            return Resultat(False,
                            "Il manque ceci dans ta sortie : " + ", ".join(repr(m) for m in manquants) +
                            "\n\nSortie obtenue :\n" + (run.stdout or "(rien)"))
        return Resultat(True, run.stdout if run.stdout.strip() else "Le programme compile et s'exécute.")


def compiler_et_executer(etape: Etape, code_eleve: str) -> Resultat:
    """Compile le code de l'étudiant et, en mode programme, l'exécute. Rend la sortie
    console brute, sans juger de porte ni valider l'étape. Sert au bouton Compiler.

    En mode programme, on lance le binaire et on renvoie sa sortie (plus les
    avertissements du compilateur). Dans les autres modes, où le code seul n'a pas
    forcément de main, on se contente de vérifier qu'il compile (compilation sans édition
    de liens)."""
    with tempfile.TemporaryDirectory() as d:
        src = Path(d) / "source.c"
        src.write_text(code_eleve, encoding="utf-8")
        base = ["gcc", "-Wall", "-Wno-unused-parameter", "-Wno-unused-variable",
                f"-I{etape.dossier}"]

        if etape.mode != "programme":
            comp = subprocess.run(base + ["-c", str(src), "-o", str(Path(d) / "o.o")],
                                  capture_output=True, text=True)
            if comp.returncode != 0:
                return Resultat(False, "Erreur de compilation :\n" + comp.stderr)
            avert = comp.stderr.strip()
            return Resultat(True, (avert + "\n\n" if avert else "") + "Compilation reussie.")

        binaire = Path(d) / _nom_binaire("prog")
        comp = subprocess.run(base + [str(src), "-lm", "-o", str(binaire)],
                              capture_output=True, text=True)
        if comp.returncode != 0:
            return Resultat(False, "Erreur de compilation :\n" + comp.stderr)
        try:
            run = subprocess.run([str(binaire)], capture_output=True, text=True,
                                 timeout=15, input=etape.entree or "")
        except subprocess.TimeoutExpired:
            return Resultat(False, "Le programme a depasse le delai. Attend-il une saisie au clavier ?")
        avert = comp.stderr.strip()
        entete = "Avertissements du compilateur :\n" + avert + "\n\n" if avert else ""
        corps = run.stdout + run.stderr
        return Resultat(run.returncode == 0,
                        entete + (corps if corps.strip() else "(aucune sortie)"))


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
        text=True,
        cwd=str(espace.build_sh.parent),
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
        )
        return Resultat(True, "Build réussi. Jeu lancé.")
    return Resultat(True, "Build réussi.")
