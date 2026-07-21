"""Portes etanches : plusieurs jeux d'entrees, et parcours libre.

Le defaut mesure le 20 juillet : les 14 etapes de be_c s'ouvraient devant un
programme qui se contentait de reimprimer la sortie attendue en dur. Il suffisait
de lancer le corrige une fois et de recopier sa sortie dans des printf. Ces tests
verrouillent le mecanisme cense l'empecher -- et le premier d'entre eux echouerait
si on retirait la boucle multi-cas.
"""
import json
import tempfile
import unittest
from pathlib import Path

import executeur
import modele_etape
import progression

# Lit un entier et affiche son double. Choisi parce que la reponse depend de
# l'entree : c'est exactement ce qu'un printf en dur ne peut pas suivre.
VRAI_CALCUL = """#include <stdio.h>
int main(void)
{
    int n = 0;
    if (scanf("%d", &n) != 1) return 1;
    printf("resultat : %d\\n", n * 2);
    return 0;
}
"""

# La triche du paresseux : la bonne reponse du premier cas, ecrite en dur.
TRICHE = """#include <stdio.h>
int main(void)
{
    printf("resultat : 6\\n");
    return 0;
}
"""

META_MULTI = {
    "id": "cas_double", "titre": "Double du nombre lu", "type": "perso",
    "mode": "programme", "fichier_edite": "programme.c",
    "cas": [
        {"entree": "3\n", "sortie_attendue": ["resultat : 6"]},
        {"entree": "10\n", "sortie_attendue": ["resultat : 20"]},
    ],
}

META_UNIQUE = {
    "id": "cas_double", "titre": "Double du nombre lu", "type": "perso",
    "mode": "programme", "fichier_edite": "programme.c",
    "entree": "3\n", "sortie_attendue": ["resultat : 6"],
}


def _etape(meta: dict, dossier: Path):
    (dossier / "meta.json").write_text(json.dumps(meta, ensure_ascii=False),
                                       encoding="utf-8")
    return modele_etape.charger_etape(dossier)


class TestPorteMultiCas(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.dossier = Path(self.d.name)

    def tearDown(self):
        self.d.cleanup()

    def test_la_triche_passe_quand_il_n_y_a_qu_un_seul_cas(self):
        # Non pas un comportement souhaitable, mais le constat qui justifie tout le
        # reste : avec une seule execution, reciter la reponse suffit. Ce test doit
        # rester vert, sinon la porte multi-cas ne corrige plus rien de reel.
        e = _etape(META_UNIQUE, self.dossier)
        self.assertTrue(executeur.porte_programme(e, TRICHE).ok)

    def test_la_triche_tombe_des_qu_il_y_a_deux_cas(self):
        e = _etape(META_MULTI, self.dossier)
        r = executeur.porte_programme(e, TRICHE)
        self.assertFalse(r.ok)
        self.assertEqual(r.categorie, "sortie_incomplete")
        self.assertIn("Cas 2", r.sortie)          # le premier cas est passe, pas le second

    def test_le_vrai_calcul_passe_tous_les_cas(self):
        e = _etape(META_MULTI, self.dossier)
        r = executeur.porte_programme(e, VRAI_CALCUL)
        self.assertTrue(r.ok, r.sortie)
        self.assertIn("2 jeux d'entrées passés", r.sortie)

    def test_sans_champ_cas_le_comportement_est_inchange(self):
        e = _etape(META_UNIQUE, self.dossier)
        r = executeur.porte_programme(e, VRAI_CALCUL)
        self.assertTrue(r.ok, r.sortie)
        self.assertNotIn("Cas 1", r.sortie)       # pas de prefixe quand il n'y a qu'un cas

    def test_un_cas_herite_des_motifs_mais_pas_des_litteraux(self):
        # Les motifs decrivent un format, vrai quelle que soit l'entree : un cas qui
        # n'en parle pas garde ceux de l'etape. Les litteraux decrivent une valeur,
        # liee a une entree : les heriter ferait attendre du cas « 10 » la reponse du
        # cas « 3 ». C'est un test de conception, pas de plomberie -- la premiere
        # version heritait des deux et se contredisait des le deuxieme cas.
        meta = dict(META_UNIQUE)
        meta["sortie_motifs"] = [{"motif": r"resultat\s*:\s*\d+", "attendu": "une ligne resultat"}]
        meta["cas"] = [{"entree": "3\n", "sortie_attendue": ["resultat : 6"]},
                       {"entree": "10\n"}]        # ce cas ne garde que le motif
        e = _etape(meta, self.dossier)
        self.assertTrue(executeur.porte_programme(e, VRAI_CALCUL).ok)

    def test_le_litteral_de_l_etape_ne_contamine_pas_les_cas(self):
        # META_UNIQUE attend « resultat : 6 ». Avec deux cas, ce littéral ne doit pas
        # etre impose au cas « 10 », sinon aucun programme correct ne passerait.
        meta = dict(META_UNIQUE)
        meta["cas"] = [{"entree": "10\n", "sortie_attendue": ["resultat : 20"]}]
        e = _etape(meta, self.dossier)
        self.assertTrue(executeur.porte_programme(e, VRAI_CALCUL).ok)


class TestFragmentNumerique(unittest.TestCase):
    """Un resultat faux d'un facteur dix ne doit pas passer pour le bon.

    Mesure sur ex12_produit_somme, qui attend « La somme de a+b = 5 » : un programme
    affichant 50 franchissait la porte, le fragment attendu etant une sous-chaine du
    resultat faux."""

    def test_un_nombre_plus_long_ne_satisfait_pas_le_fragment(self):
        self.assertFalse(executeur.fragment_present("a+b = 5", "a+b = 50\n"))
        self.assertFalse(executeur.fragment_present("case [4] = 20", "case [4] = 200\n"))

    def test_le_bon_nombre_passe(self):
        self.assertTrue(executeur.fragment_present("a+b = 5", "a+b = 5\n"))
        self.assertTrue(executeur.fragment_present("a+b = 5", "La somme de a+b = 5 ok"))

    def test_une_occurrence_correcte_plus_loin_suffit(self):
        # La premiere occurrence est un prefixe de nombre, la seconde est la bonne :
        # on ne doit pas s'arreter a la premiere.
        self.assertTrue(executeur.fragment_present("x = 1", "x = 12\nx = 1\n"))

    def test_les_zeros_de_queue_d_un_decimal_sont_tolerés(self):
        # Cas casse par ma premiere version, rattrape par la suite tp_c : l'etape
        # attend « 9.9 » et printf %f ecrit « 9.900000 ». Des zeros apres une
        # decimale ne changent pas la valeur, contrairement au chiffre qui allonge
        # un entier.
        self.assertTrue(executeur.fragment_present("a = 9.9", "a = 9.900000\n"))
        self.assertTrue(executeur.fragment_present("x1 = 3.0", "x1 = 3.000000,"))

    def test_un_chiffre_significatif_apres_la_decimale_refuse(self):
        # 9.99 n'est pas 9.9 : la tolerance ne porte que sur les zeros.
        self.assertFalse(executeur.fragment_present("a = 9.9", "a = 9.99\n"))

    def test_un_fragment_ne_finissant_pas_par_un_chiffre_reste_un_prefixe_valide(self):
        # Plusieurs etapes en dependent : ex05 attend un bloc de tirets, ex09 des
        # debuts de phrase. Exiger une frontiere partout les casserait.
        self.assertTrue(executeur.fragment_present("Nombre de lignes ?",
                                                   "Nombre de lignes ? 6\n"))
        self.assertTrue(executeur.fragment_present("----", "--------\n"))


class TestParcoursLibre(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.contenu = Path(self.d.name)

    def tearDown(self):
        self.d.cleanup()

    def _parcours(self, libre):
        ordre = []
        for i in (1, 2, 3):
            dossier = self.contenu / f"e{i}"
            dossier.mkdir()
            (dossier / "meta.json").write_text(json.dumps(
                {"id": f"e{i}", "titre": f"Etape {i}", "type": "perso",
                 "mode": "programme", "fichier_edite": "programme.c"}), encoding="utf-8")
            ordre.append(f"e{i}")
        donnees = {"ordre": ordre, "mode": "isole"}
        if libre:
            donnees["libre"] = True
        (self.contenu / "parcours.json").write_text(json.dumps(donnees), encoding="utf-8")
        return modele_etape.charger_parcours_complet(self.contenu)

    def test_parcours_verrouille_par_defaut(self):
        p = self._parcours(libre=False)
        self.assertFalse(p.libre)
        vide = progression.Progression([], 0)
        self.assertTrue(progression.etape_deverrouillee(p.etapes[0], p.etapes, vide, p.libre))
        self.assertFalse(progression.etape_deverrouillee(p.etapes[2], p.etapes, vide, p.libre))

    def test_parcours_libre_ouvre_tout(self):
        p = self._parcours(libre=True)
        self.assertTrue(p.libre)
        vide = progression.Progression([], 0)
        for e in p.etapes:
            self.assertTrue(progression.etape_deverrouillee(e, p.etapes, vide, p.libre))

    def test_libre_absent_vaut_faux(self):
        # Les 6 parcours livres n'ont pas ce champ : leur comportement ne doit pas bouger.
        self.assertFalse(self._parcours(libre=False).libre)


if __name__ == "__main__":
    unittest.main()
