## Commandes

### Générales

Enregistrer : `s`
Définir options par défaut pour le calcul de dégâts : `def <param> <value>`
Paramètres : `pa`, `pomin`, `pomax`, `t`
Help : `h`
Fermer : `q`

### Stats

Créer nouvelle page de stats : `st new`
Modifier page de stats : `st mod <short_name>`
Supprimer page de stats : `st rm <short_name>`

### Sorts

Créer nouveau sort : `sp new`
Modifier sort : `sp mod <short_name>`
Supprimer sort : `sp rm <short_name>`

### Ensembles de sorts

Créer nouvel ensemble : `ss new`
Supprimer ensemble : `ss rm <short_name>`
Ajouter un sort à un ensemble : `ss add <spell_short_name>`
Retirer un sort d'un ensemble : `ss del <spell_short_name>`

### Dégâts

Calculer meilleurs dégâts pour un ensemble (options : nombre de PA, PO min et max, monocible/multicible/versatile) : `dmg <spell_set_short_name> [<param> <value>]+`
Paramètres :
 - Nombre de PA : `pa <value>`
 - PO : `po [min <value>] [max <value>]`
 - Type : `t <mono/multi/versa>`