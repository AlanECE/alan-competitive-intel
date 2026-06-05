# Angle Framework — Alan Competitive Intel

Classification des angles publicitaires e-commerce pour Meta Ads et TikTok. Adapté aux produits physiques DTC.

---

## Les 8 Angles E-commerce

Assigner un **angle principal** par ad. Baser la classification sur les 3 premières secondes (hook) ou la première image/headline visible.

### 1. Problème (Pain)
L'ad nomme un problème concret, une frustration quotidienne, ou un échec actuel.

Signaux :
- "Tu en as marre de..."
- "Si tu souffres de [problème]..."
- "Le problème avec [solution habituelle]..."
- Problème nommé avant toute solution
- Image du "avant" négatif

Efficacité : fort en froid, fonctionne sur audiences larges. Risque : saturation si trop générique.

### 2. Transformation (Désir)
L'ad montre directement le résultat, le futur état désirable, la transformation.

Signaux :
- Before/After explicite ou implicite
- Résultat chiffré mesurable
- "En [X jours/semaines]..."
- Image du "après" positif sans montrer le problème
- Transformation visuelle (peau, corps, maison, etc.)

Efficacité : très fort pour produits visuels e-com. Nécessite preuves ou disclaimer.

### 3. Preuve Sociale (Social Proof)
L'ad commence par ou est dominé par la preuve : avis client, UGC, testimonial, cas réel.

Signaux :
- "★★★★★ 4 732 avis"
- Vidéo client / UGC authentique
- Screenshot d'avis réel
- Nombre de clients ("Plus de 50 000 clients")
- Témoignage nominatif ou anonymisé

Efficacité : excellent en remarketing et audience tiède. Fort sur TikTok avec UGC natif.

### 4. Contre-intuitif (Pattern Interrupt)
L'ad brise une croyance commune ou attaque la solution habituelle.

Signaux :
- "Ce que tout le monde fait, mais qui ne marche pas..."
- "Le vrai problème n'est pas X, c'est Y"
- Verdict contre-intuitif dans les 3 premières secondes
- "Pourquoi [solution populaire] est une erreur"

Efficacité : fort pour stopper le scroll. Nécessite une preuve solide ensuite.

### 5. Urgence / Rareté
L'ad crée une raison d'agir maintenant.

Signaux :
- Compte à rebours visible
- "Stock limité / dernières pièces"
- Offre à durée déterminée
- "Seulement X disponibles"
- Fin de promotion imminente

Efficacité : fort en bas de funnel, fonctionne mal en cold. Souvent utilisé en retargeting.

### 6. Éducatif (How-It-Works)
L'ad explique pourquoi le produit fonctionne, le mécanisme, la science derrière.

Signaux :
- "Voici comment ça fonctionne..."
- Explication du mécanisme produit
- Comparaison de composants / ingrédients
- "La différence entre X et Y"
- Tone pédagogique sans pression de vente directe

Efficacité : excellent sur audience Problème-aware. Fort pour produits innovants incompris.

### 7. Autorité / Validation
L'ad s'appuie sur une expertise, une certification, une validation externe.

Signaux :
- Mention presse ("Vu sur...", "Featured in...")
- Expert ou professionnel qui recommande
- Certification ou label visible
- Fondateur avec crédibilité visible
- Nombre d'années d'expertise

Efficacité : fort pour produits santé/beauté nécessitant confiance. Nécessite validation réelle.

### 8. Entertainment / Natif Plateforme
L'ad est conçu comme contenu organique de la plateforme. Fait rire, surprend, divertit.

Signaux TikTok : trend audio, format challenge, storytelling rapide, humour
Signaux Meta : carousel storytelling, Reels natif, format "POV"
Pas de pression de vente directe dans les 5 premières secondes
Engagement fort (commentaires, partages)

Efficacité : très fort sur TikTok cold. Difficile à scaler sans algo favorable. Dépend du contenu.

---

## Winner Rules

Utiliser la durée d'activité comme proxy de profitabilité (pas une preuve absolue).

| Durée active | Label | Interprétation |
|---|---|---|
| 0-7 jours | `Test` | Trop tôt pour juger |
| 8-21 jours | `Validation` | Début de signal positif |
| 22-59 jours | `Winner` | Ad rentable avec scaling probable |
| 60-179 jours | `Hero` | Ad fort, annonceur en confiance |
| 180+ jours | `Evergreen` | Pilier de la stratégie — reproduire le pattern |

Règle : `winner=true` à partir de 22 jours actifs.
Si la date de début est masquée : laisser le champ vide et noter "date masquée".

---

## Règle d'activation des recommandations

Un angle est **Prouvé** si : ≥2 concurrents significatifs ont des ads Hero (60j+) avec cet angle.

Un hook est **recommandable** si :
1. L'angle est Prouvé
2. Le hook est extrait des patterns observés sur des ads Hero/Evergreen (pas inventé)
3. Il est accompagné de la preuve : "Observé chez [Concurrent] — actif depuis [Durée] — [URL si disponible]"

Un angle avec uniquement des ads Test ou Validation → **"Signal précoce — insuffisant pour recommander"**

Un angle avec 0 Winner → **"Non validé — exclure de la stratégie initiale"**

---

## Angles Saturés vs White Spaces

**Angle Saturé** : ≥5 concurrents utilisent cet angle avec des ads Winner+. Éviter ou trouver un twist différenciateur.

**White Space** : angle Prouvé (utilisé par ≥2 concurrents Hero+) mais sous-représenté dans la niche (<3 concurrents). Opportunité de différenciation.

**Zone morte** : aucun concurrent n'utilise cet angle + aucune donnée de performance. Ne pas recommander sans test.

---

## Matrice Meta vs TikTok

Certains angles performent différemment selon la plateforme :

| Angle | Meta Force | TikTok Force |
|---|---|---|
| Problème | ★★★★★ | ★★★★ |
| Transformation | ★★★★★ | ★★★★★ |
| Preuve Sociale | ★★★★ | ★★★★★ |
| Contre-intuitif | ★★★★ | ★★★ |
| Urgence | ★★★ | ★★ |
| Éducatif | ★★★ | ★★★★ |
| Autorité | ★★★★ | ★★★ |
| Entertainment | ★★★ | ★★★★★ |

---

## Format dominant par plateforme

**Meta** : Static 1:1 et 4:5 (dominant pour le spend), Video Reels 9:16, Carousel

**TikTok** : Video verticale 9:16 (obligatoire), durée optimale 15-30s pour cold, 45-60s pour warm

Règle : un concurrent avec beaucoup d'ads Static Hero sur Meta → il a trouvé un creative qui scale en static. Chercher le visual pattern.
