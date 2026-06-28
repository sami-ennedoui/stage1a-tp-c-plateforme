import unittest
import chemins
from modele_etape import charger_etape
from executeur import porte_perso, juger_test, porte_jalon


class TestPortePerso(unittest.TestCase):
    def setUp(self):
        self.etape = charger_etape(chemins.CONTENU / "perso_P1")
        self.corrige = (self.etape.dossier / "corrige.c").read_text(encoding="utf-8")
        self.starter = (self.etape.dossier / "starter.c").read_text(encoding="utf-8")

    def test_corrige_passe(self):
        r = porte_perso(self.etape, self.corrige)
        self.assertTrue(r.ok, r.sortie)

    def test_starter_echoue(self):
        r = porte_perso(self.etape, self.starter)
        self.assertFalse(r.ok, r.sortie)


class TestJalon(unittest.TestCase):
    def setUp(self):
        self.etape = charger_etape(chemins.CONTENU / "jalon1_parametrage")
        self.test_ref = (self.etape.dossier / "test_reference.c").read_text(encoding="utf-8")
        self.corrige = (self.etape.dossier / "corrige.c").read_text(encoding="utf-8")
        # un test mou : il vérifie seulement que l'état a changé, il rate le bug
        self.test_mou = (
            '#include <stdio.h>\n#include "harnais.h"\n'
            'int main(void){ int etat=12345; SDL_Event e; simuler_clic(0);'
            ' SP_Gestion_Evenements_MENU_PARAMETRAGE(e,&etat);'
            ' if(etat==12345){printf("FAIL\\n");return 1;} printf("ok\\n"); return 0; }\n'
        )

    def test_reference_est_solide(self):
        r = juger_test(self.etape, self.test_ref)
        self.assertTrue(r.passe_corrige, r.sortie)
        self.assertTrue(r.attrape_bug, r.sortie)
        self.assertTrue(r.test_solide, r.sortie)

    def test_mou_est_rejete(self):
        r = juger_test(self.etape, self.test_mou)
        self.assertTrue(r.passe_corrige, r.sortie)
        self.assertFalse(r.attrape_bug, r.sortie)
        self.assertFalse(r.test_solide, r.sortie)

    def test_porte_jalon_corrige_passe(self):
        r = porte_jalon(self.etape, self.corrige, self.test_ref)
        self.assertTrue(r.ok, r.sortie)


if __name__ == "__main__":
    unittest.main()
