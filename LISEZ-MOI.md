# Je communique — tablette de communication par pictogrammes

Une application unique : l'élève touche un pictogramme, la tablette prononce le mot.
Aucune connexion internet, aucun compte, aucune publicité, rien d'autre à l'écran.

```
communiquer/
  index.html        l'application (c'est elle qu'on met sur la tablette)
  vocabulaire.js    les catégories et les mots
  editeur.py        l'éditeur, à lancer sur le Mac
  preparer.py       le script de fabrication en masse
  pictos/           les images
  sons/             les fichiers audio
```

---

## L'éditeur — la façon normale de travailler

```bash
python3 editeur.py
```

Une page s'ouvre dans le navigateur du Mac. Tout ce que tu fais y est enregistré
immédiatement : il n'y a pas de bouton « sauvegarder », il n'y a rien à oublier.

- **Ajouter un mot** : tu tapes un terme dans le champ de recherche à droite —
  n'importe lequel, il y a des milliers de pictogrammes ARASAAC — tu cliques sur
  celui qui te convient, tu ajustes le texte écrit et le texte prononcé, et
  c'est fait : l'image est téléchargée et le son fabriqué dans la foulée.
- **Catégories** : créer, renommer, changer la couleur, monter, supprimer.
- **Mots** : réordonner avec les flèches, modifier, retirer, et le bouton ▶ pour
  écouter le son tel que l'élève l'entendra.
- **⧉ Copier vers une autre catégorie** : le mot copié garde le même
  pictogramme et le même son, rien n'est retéléchargé. Utile pour avoir *oui*
  et *non* à la fois dans l'Essentiel et dans leur catégorie d'origine.
- **Voix et débit** en haut : « Refaire tous les sons » régénère l'ensemble.

### Pictogrammes par page

Le menu déroulant à côté du nom de la catégorie fixe le nombre de cases par
page : 4 (grille 2 × 2), 6, 9, 12, 16 ou 20. C'est ce réglage — et non le nombre
de mots — qui détermine la taille des cases sur la tablette.

Au-delà, la catégorie se découpe en pages, et une bande de navigation apparaît en
bas de l'écran avec deux grosses flèches et le numéro de page. Une catégorie de
30 mots réglée à 6 par page donne donc cinq pages de très grosses cases, au lieu
d'une seule grille illisible. On revient toujours à la page 1 en changeant de
catégorie.

« Automatique » met tout sur une seule page et adapte la grille au nombre de
mots : c'est bien pour une petite catégorie comme l'Essentiel.

Quand tu as fini : Ctrl-C dans le Terminal pour arrêter le serveur.

---

## Le script de préparation

`preparer.py` reste utile pour les traitements en masse : après avoir modifié
`vocabulaire.js` à la main, ou pour tout régénérer.

```bash
python3 preparer.py                              # complète ce qui manque
python3 preparer.py --voix "Audrey (Premium)"    # change de voix
python3 preparer.py --vitesse 130                # change le débit
python3 preparer.py --lister-voix                # voix françaises installées
python3 preparer.py --force                      # tout refaire
```

Il ne remplace **jamais** un fichier déjà présent, sauf avec `--force`. Donc si tu
veux **ta voix** plutôt que celle de macOS — c'est souvent mieux accepté, et
l'élève t'identifie — enregistre-toi et dépose le fichier dans `sons/` sous le nom
`boire.wav`, `toilettes.wav`, etc. Le script le laissera tranquille. Tu peux
mélanger : ta voix sur les dix mots qui comptent, la synthèse sur le reste.

### Voix

Les voix installées par défaut sur macOS sont les voix « compactes », qui datent
d'il y a quinze ans. Pour les bonnes :

> Réglages Système → Accessibilité → Contenu énoncé → Voix système →
> Gérer les voix → Français → cocher les versions **Premium**

L'écart de qualité est sans commune mesure.

---

## Le mode maître, sur la tablette

**Appui long de 3 secondes sur le titre**, en haut à gauche. Un panneau s'ouvre :

- masquer ou réafficher une catégorie entière ;
- masquer ou réafficher un mot ;
- une section « Vérification » qui liste les pictogrammes et les sons manquants ;
- « Tout réafficher » pour revenir au tableau complet.

C'est fait pour ajuster en classe, sans câble : on masque une catégorie le temps
d'une activité, on réduit le tableau à trois mots un jour difficile.

`vocabulaire.js` reste la référence. Les masquages sont un simple filtre posé
par-dessus, mémorisé par le navigateur de la tablette. S'ils s'effacent, tout
réapparaît — l'application ne peut pas se retrouver cassée ni vide.

Ajouter un **nouveau** mot passe forcément par le Mac : il faut télécharger
l'image et fabriquer le son.

---

## Publier sur GitHub Pages, pour l'iPad

L'application sait s'installer sur un iPad et fonctionner ensuite **sans aucune
connexion**. Il faut la publier une fois à une adresse web ; la connexion ne
resservira que quand tu voudras envoyer tes modifications.

### ⚠️ À lire avant de publier

Un dépôt GitHub Pages gratuit est **public**. Tout ce qui est dans le dossier
sera lisible par n'importe qui connaissant l'adresse.

C'est sans conséquence pour un vocabulaire générique en voix de synthèse. Mais
n'y mets pas :

- le **prénom ou le nom de l'élève**, ni dans les mots, ni dans les noms de
  fichiers ;
- sa photo ou celle d'un camarade en guise de pictogramme ;
- des enregistrements où l'on nomme des personnes.

Si tu veux des pictogrammes personnalisés de ce type, garde-les pour la version
copiée par câble sur la tablette Android, et publie la version générique.
Le script écrit un `robots.txt` qui demande aux moteurs de recherche de ne pas
indexer la page, mais cela n'empêche pas l'accès direct.

### Publier

1. Vérifie que le dossier est à jour :

   ```bash
   python3 preparer.py --publier
   ```

   Cela écrit `manifest.json`, `sw.js`, `version.js` et `version.json` — les
   fichiers qui rendent l'application installable et utilisable hors connexion.
   L'éditeur les régénère aussi tout seul à chaque modification.

2. Dans **GitHub Desktop** : `File → Add local repository`, choisis le dossier.
   S'il propose de créer un dépôt, accepte. Écris un message de commit,
   **Commit to main**, puis **Publish repository** — en décochant « Keep this
   code private », sinon Pages ne marchera pas avec un compte gratuit.

3. Sur github.com, dans le dépôt : `Settings → Pages`. Source : **Deploy from a
   branch**, branche `main`, dossier `/ (root)`. Enregistre.

4. Une à deux minutes plus tard, l'adresse s'affiche sur cette même page. Elle
   ressemble à `https://tonpseudo.github.io/communiquer/`.

### Installer sur l'iPad

1. Connecte l'iPad au wifi, ouvre l'adresse **dans Safari** (pas Chrome : sur
   iOS, seul Safari sait installer une application).
2. Laisse la page ouverte une quinzaine de secondes : elle télécharge en fond
   tous les pictogrammes et tous les sons.
3. Bouton Partager → **Sur l'écran d'accueil**.
4. Ouvre l'application depuis l'icône, coupe le wifi, et vérifie qu'elle marche.
   L'appui long de 3 secondes sur le titre affiche le nombre de fichiers
   disponibles hors connexion — c'est la preuve que tout est bien descendu.

### Verrouiller l'iPad sur l'application

Réglages → Accessibilité → **Accès guidé** → activer, et définir un code.
Ensuite, application ouverte, **triple-clic sur le bouton latéral** pour
verrouiller, triple-clic et code pour sortir. On peut aussi y désactiver des
zones de l'écran au doigt.

Règle aussi : rotation bloquée en paysage, verrouillage automatique sur Jamais,
volume au maximum, et vérifie le petit interrupteur latéral si l'iPad en a un —
sur iOS il coupe le son des pages web.

### Mettre à jour l'iPad

Après avoir modifié tes tableaux dans l'éditeur : dans GitHub Desktop, Commit
puis Push. Puis, sur l'iPad connecté au wifi, ouvre l'application, appui long de
3 secondes sur le titre, **Chercher une mise à jour**. Elle te dit si une
nouvelle version existe, la télécharge et redémarre toute seule.

Tant que tu ne fais pas cette manipulation, l'iPad garde exactement la version
qu'il a — une mise à jour ne peut pas te surprendre en pleine séance.

---

## Installer sur la tablette

1. Branche la tablette au Mac en USB. Sur un Mac récent il faut
   [Android File Transfer](https://www.android.com/filetransfer/) pour voir le
   stockage de la tablette.
2. Copie le dossier `communiquer` complet dans le stockage interne, à la racine.
   Inutile d'y mettre `editeur.py` et `preparer.py`, ils ne servent que sur le Mac.
3. Sur la tablette, ouvre le navigateur et saisis :

   ```
   file:///sdcard/communiquer/index.html
   ```

   (le navigateur « Internet » de Samsung gère bien les fichiers locaux ; si Chrome
   refuse, utilise celui-là)
4. Menu du navigateur → **Ajouter à l'écran d'accueil**.

Quand tu modifies le tableau plus tard, seul `vocabulaire.js` et les nouveaux
fichiers de `pictos/` et `sons/` sont à recopier.

### Réglages de la tablette, à faire une bonne fois

- Volume **média** au maximum
- Mise en veille de l'écran : 10 minutes ou jamais
- Rotation automatique désactivée, tablette bloquée en **paysage**
- Mode avion activé : la tablette n'a besoin de rien, l'autonomie double
- Écran d'accueil vidé de tout sauf l'icône de l'application
- Aucun code de verrouillage

---

## Verrouiller sur cette seule application

C'est le point qui coince avec cette tablette : l'**épinglage d'écran d'Android
n'existe qu'à partir d'Android 5**, et la SM-T210 est bloquée en 4.4. Il faut donc
un lanceur de remplacement.

**Solution recommandée** : un lanceur de contrôle parental, par exemple « Kids
Place » sur le Play Store — le Play Store sert automatiquement aux vieux appareils
la dernière version compatible. Une fois installé :

- définis-le comme **écran d'accueil par défaut** (« Toujours »)
- n'autorise **que** l'application de communication
- protège la sortie par un code à 4 chiffres

Le bouton Accueil renvoie alors toujours à l'application.

**Si la tablette a un Mode Enfant Samsung** intégré, il fait la même chose et il
est déjà là : essaie-le en premier.

**Si rien ne fonctionne** — l'écosystème Android 4.4 est en fin de vie — une
tablette d'occasion en Android 5.1 ou plus (30–50 €) rend tout trivial :
épinglage natif et [Fully Kiosk Browser](https://www.fully-kiosk.com/) en dix
minutes. L'application, elle, ne change pas d'un octet.

---

## Notes techniques

- Si un fichier son manque, l'application essaie la synthèse vocale du système.
  Sur la tablette elle n'existe probablement pas : **les `.wav` sont indispensables**.
- Les sons sont en WAV non compressé exprès : décodage instantané, aucun délai
  entre le doigt et la voix, même sur un processeur de 2013.
- Un appui déclenche le son immédiatement, sans les 300 ms d'attente d'un clic web
  classique, et la carte se souligne en noir : l'élève voit et entend qu'il a été
  entendu.
- Un même mot peut figurer dans plusieurs catégories : il partage alors le même
  pictogramme et le même son.
- Pictogrammes **ARASAAC** — Gouvernement d'Aragon, auteur Sergio Palao,
  licence CC BY-NC-SA. Utilisation pédagogique libre.
