# conges-payes

Calculer ses jours de congés payés et l'indemnité correspondante en France, y compris après un arrêt maladie (règles de la loi du 22 avril 2024). Pour les salariés, les gestionnaires de paie et les petits employeurs. Aucune dépendance.

## Installation

```bash
pip install git+https://github.com/TheoPSR01/conges-payes.git
```

Python 3.10 ou plus récent.

## En ligne de commande

Quatre mois d'arrêt maladie sur la période, 30 000 € bruts perçus, salaire actuel de 2 500 €, une semaine de congé (6 jours ouvrables) :

```bash
conges-payes --maladie 4 --remuneration 30000 --salaire 2500
```

```
Jours acquis : 28 jours ouvrables (23,33 jours ouvrés)
Indemnité pour 6 jours : 642,86 € (dixième)
  dixième : 642,86 €, maintien de salaire : 576,92 €
```

```bash
conges-payes                          # année complète : 30 jours
conges-payes --travail 7,5            # embauche en cours de période
conges-payes --at-mp 3                # arrêt pour accident du travail
```

## En Python

```python
from conges_payes import jours_acquis, indemnite, en_jours_ouvres

jours_acquis(mois_travail=8, mois_maladie=4)      # 28
en_jours_ouvres(28)                               # Decimal('23.33')
i = indemnite(30000, jours_pris=6, jours_acquis_total=30, salaire_mensuel=2500)
print(i.montant, i.methode)                       # 600.00 dixième
```

## Règles appliquées

Acquisition : 2,5 jours ouvrables par mois de travail effectif ou d'arrêt pour accident du travail ou maladie professionnelle ; 2 jours ouvrables par mois d'arrêt pour maladie ou accident non professionnel, dans la limite de 24 jours par période (article L3141-5-1). Le total est limité à 30 jours ouvrables, et un nombre décimal est arrondi au jour supérieur.

Indemnité : la plus favorable des deux méthodes. Le dixième correspond à 10 % de la rémunération brute de la période de référence, au prorata des jours pris. Le maintien de salaire correspond au salaire que le salarié aurait touché en travaillant ; l'outil l'estime en divisant le salaire mensuel par 26 jours ouvrables.

## Limites

Le maintien de salaire est approché avec 26 jours ouvrables par mois ; la paie réelle utilise le nombre exact de jours du mois. Pour la règle du dixième, la rémunération des périodes de maladie non professionnelle ne compte qu'à 80 % : c'est à vous d'en tenir compte dans le montant saisi. Les jours supplémentaires (fractionnement, ancienneté, convention collective) et les congés des salariés à temps partiel annualisé ne sont pas traités.

## Contribuer

```bash
git clone https://github.com/TheoPSR01/conges-payes.git
cd conges-payes
pip install -e ".[dev]"
pytest
```

## Licence

MIT
