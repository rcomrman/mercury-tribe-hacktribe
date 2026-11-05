# R22 — autorité des trois slots de `C006EA10`

Le constructeur `C006E6EC` alloue et construit trois objets distincts : slot
`+0x34`, 76 octets, `C0084B3C`; slot `+0x38`, 88 octets, `C0084254`; slot
`+0x3c`, 76 octets, `C008C8B4`. `C006EA10` les lit sans test nul et appelle
leur vtable `+8`. Ils appartiennent au gestionnaire, pas à la page courante.

Les expériences R7 les construisent nativement mais doivent fournir leurs
services/observateurs. R8 montre qu'une réentrée de `C006F178` remet trop tôt à
zéro le marqueur actif d'une page : ce marqueur n'est pas un verrou. Les pages
dynamiques résident plutôt à `+0x10/+0x14` et leurs transitions détruisent les
anciens objets. Remplacer un des trois widgets annexes exigerait donc une preuve
de propriété, de désinscription, de destruction et d'absence d'emprunt que les
deux images ne fournissent pas.

Verdict : **NO GO pour l'insertion Mercury dans ces slots**. Un pointeur statique
fonctionne dans une fixture, mais aucune autorité native ne permet d'écraser le
pointeur possédé par le gestionnaire ou d'abandonner son objet initial.
