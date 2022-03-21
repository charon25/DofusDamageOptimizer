## Commandes

### Générales

Enregistrer : `s`
Informations : `i`
Définir options par défaut pour le calcul de dégâts : `def <param> <value>`
Paramètres : `pa`, `pomin`, `pomax`, `t`
Help : `h`
Fermer : `q`

### Stats

Créer nouvelle page de stats : `st new <short_name>`
Lister les pages de stats : `st ls`
Afficher les détails d'une page de stats : `st show <short_name>`
Modifier page de stats : `st mod <short_name>`
Supprimer page de stats : `st rm <short_name>`

### Sorts

Créer nouveau sort : `sp new <short_name>`
Lister les sorts : `sp ls`
Afficher les détails d'un sort : `sp show <short_name>`
Modifier sort : `sp mod <short_name>`
Supprimer sort : `sp rm <short_name>`

### Ensembles de sorts

Créer nouvel ensemble : `ss new <short_name>`
Supprimer ensemble : `ss rm <short_name>`
Lister les ensembles de sorts : `ss ls`
Afficher les détails d'un ensemble : `ss show <short_name>`
Ajouter un sort à un ensemble : `ss add <spell_set_short_name> <spell_short_name>`
Retirer un sort d'un ensemble : `ss del <spell_set_short_name> <spell_short_name>`

### Dégâts

Calculer meilleurs dégâts pour un ensemble (options : nombre de PA, PO min et max, monocible/multicible/versatile) : `dmg <spell_set_short_name> <stats_short_name> [<param> <value>]+`
Paramètres :
 - Nombre de PA : `pa <value>`
 - PO : `po [min <value>] [max <value>]`
 - Type : `t <mono/multi/versa>`