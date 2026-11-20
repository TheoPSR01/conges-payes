from decimal import Decimal

import pytest

from conges_payes import en_jours_ouvres, indemnite, jours_acquis, main


@pytest.mark.parametrize("travail,maladie,at_mp,attendu", [
    (12, 0, 0, 30),
    (8, 4, 0, 28),        # exemple CCI Paris : 8 × 2,5 + 4 × 2
    (10, 2, 0, 29),       # 10 × 2,5 + 2 × 2
    (0, 12, 0, 24),       # arrêt maladie toute l'année : plafond de 24 jours
    (0, 0, 12, 30),       # accident du travail : 2,5 jours par mois
    ("7,5", 0, 0, 19),    # 18,75 arrondi au jour supérieur
    (1, 0, 0, 3),
])
def test_jours_acquis(travail, maladie, at_mp, attendu):
    assert jours_acquis(travail, maladie, at_mp) == attendu


def test_erreurs_jours():
    with pytest.raises(ValueError):
        jours_acquis(12, 1)
    with pytest.raises(ValueError):
        jours_acquis(-1)


def test_jours_ouvres():
    assert en_jours_ouvres(30) == Decimal("25.00")
    assert en_jours_ouvres(28) == Decimal("23.33")


def test_indemnite_dixieme_plus_favorable():
    i = indemnite(30000, 6, 30, 2500)
    assert i.dixieme == Decimal("600.00")
    assert i.maintien == Decimal("576.92")
    assert i.montant == Decimal("600.00") and i.methode == "dixième"


def test_indemnite_maintien_plus_favorable():
    # Augmentation récente : le maintien du nouveau salaire dépasse le dixième
    i = indemnite(24000, 6, 30, 2800)
    assert i.montant == i.maintien == Decimal("646.15")


def test_indemnite_erreurs():
    with pytest.raises(ValueError):
        indemnite(30000, 31, 30, 2500)


def test_cli(capsys):
    assert main(["--maladie", "4"]) == 0
    assert "28 jours ouvrables (23,33 jours ouvrés)" in capsys.readouterr().out
    assert main(["--remuneration", "30000", "--salaire", "2500"]) == 0
    assert "600,00 € (dixième)" in capsys.readouterr().out


def test_cli_aide():
    with pytest.raises(SystemExit) as exc:
        main(["--help"])
    assert exc.value.code == 0
