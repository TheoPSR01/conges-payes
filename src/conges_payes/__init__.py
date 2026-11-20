"""conges_payes : congés payés en France (Code du travail).

- Travail effectif et arrêts pour accident du travail ou maladie
  professionnelle : 2,5 jours ouvrables par mois (articles L3141-3 et L3141-5).
- Arrêt pour maladie ou accident non professionnel : 2 jours ouvrables par
  mois, dans la limite de 24 jours par période de référence (article L3141-5-1,
  loi du 22 avril 2024).
- Total limité à 30 jours ouvrables ; un nombre de jours décimal est arrondi
  au nombre entier supérieur (article L3141-7).
- Indemnité : la plus favorable entre le dixième de la rémunération brute de
  la période de référence et le maintien du salaire (article L3141-24).
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from decimal import ROUND_CEILING, ROUND_HALF_UP, Decimal, InvalidOperation
from typing import Union

__version__ = "0.1.0"

Montant = Union[int, float, str, Decimal]
MAX_JOURS = 30
MAX_JOURS_MALADIE = 24


def _d(x: Montant) -> Decimal:
    return x if isinstance(x, Decimal) else Decimal(str(x).replace(",", ".").replace(" ", ""))


def jours_acquis(mois_travail: Montant, mois_maladie: Montant = 0, mois_at_mp: Montant = 0) -> int:
    """Jours ouvrables acquis sur la période de référence (en général du 1er juin au 31 mai).

    ``mois_travail`` : mois de travail effectif (ou périodes assimilées) ;
    ``mois_maladie`` : mois d'arrêt pour maladie ou accident non professionnel ;
    ``mois_at_mp`` : mois d'arrêt pour accident du travail ou maladie professionnelle.
    """
    t, m, a = _d(mois_travail), _d(mois_maladie), _d(mois_at_mp)
    if min(t, m, a) < 0:
        raise ValueError("les durées doivent être positives")
    if t + m + a > 12:
        raise ValueError("une période de référence compte au plus 12 mois")
    jours = (t + a) * Decimal("2.5") + min(m * 2, Decimal(MAX_JOURS_MALADIE))
    jours = jours.to_integral_value(rounding=ROUND_CEILING)
    return int(min(jours, Decimal(MAX_JOURS)))


def en_jours_ouvres(jours_ouvrables: Montant) -> Decimal:
    """Conversion pour une entreprise qui décompte en jours ouvrés (5 jours pour 6)."""
    return (_d(jours_ouvrables) * 5 / 6).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


@dataclass(frozen=True)
class Indemnite:
    dixieme: Decimal
    maintien: Decimal
    montant: Decimal
    methode: str


def indemnite(remuneration_reference: Montant, jours_pris: Montant, jours_acquis_total: Montant,
              salaire_mensuel: Montant, jours_ouvrables_du_mois: Montant = 26) -> Indemnite:
    """Indemnité pour ``jours_pris`` jours ouvrables de congé.

    Dixième : 10 % de la rémunération brute de la période de référence,
    au prorata des jours pris. Maintien : salaire mensuel au prorata des jours
    pris sur les jours ouvrables du mois (26 par défaut).
    """
    r, p, a = _d(remuneration_reference), _d(jours_pris), _d(jours_acquis_total)
    s, j = _d(salaire_mensuel), _d(jours_ouvrables_du_mois)
    if a <= 0 or j <= 0 or p < 0 or r < 0 or s < 0:
        raise ValueError("valeurs positives attendues (et au moins un jour acquis)")
    if p > a:
        raise ValueError("plus de jours pris que de jours acquis")
    cent = Decimal("0.01")
    dixieme = (r / 10 * p / a).quantize(cent, rounding=ROUND_HALF_UP)
    maintien = (s * p / j).quantize(cent, rounding=ROUND_HALF_UP)
    if dixieme >= maintien:
        return Indemnite(dixieme, maintien, dixieme, "dixième")
    return Indemnite(dixieme, maintien, maintien, "maintien de salaire")


def _fr(x: Decimal) -> str:
    return f"{x:,.2f}".replace(",", " ").replace(".", ",")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="conges-payes", description="Jours de congés payés acquis et indemnité.")
    p.add_argument("--version", action="version", version=f"conges-payes {__version__}")
    p.add_argument("--travail", default="12", help="mois de travail effectif sur la période (défaut : 12)")
    p.add_argument("--maladie", default="0", help="mois d'arrêt maladie non professionnel")
    p.add_argument("--at-mp", default="0", help="mois d'arrêt pour accident du travail ou maladie professionnelle")
    p.add_argument("--remuneration", help="rémunération brute de la période de référence (pour l'indemnité)")
    p.add_argument("--salaire", help="salaire mensuel brut actuel (pour le maintien de salaire)")
    p.add_argument("--pris", default="6", help="jours ouvrables de congé pris (défaut : 6, une semaine)")
    args = p.parse_args(argv)
    try:
        if _d(args.travail) + _d(args.maladie) + _d(args.at_mp) > 12 and args.travail == "12":
            args.travail = str(12 - _d(args.maladie) - _d(args.at_mp))
        jours = jours_acquis(args.travail, args.maladie, args.at_mp)
        print(f"Jours acquis : {jours} jours ouvrables ({str(en_jours_ouvres(jours).normalize()).replace('.', ',')} jours ouvrés)")
        if args.remuneration and args.salaire:
            i = indemnite(args.remuneration, args.pris, jours, args.salaire)
            print(f"Indemnité pour {args.pris} jours : {_fr(i.montant)} € ({i.methode})")
            print(f"  dixième : {_fr(i.dixieme)} €, maintien de salaire : {_fr(i.maintien)} €")
    except (ValueError, InvalidOperation) as exc:
        print(f"conges-payes : {exc}", file=sys.stderr)
        return 2
    return 0


__all__ = ["Indemnite", "MAX_JOURS", "MAX_JOURS_MALADIE", "en_jours_ouvres", "indemnite", "jours_acquis", "main"]
