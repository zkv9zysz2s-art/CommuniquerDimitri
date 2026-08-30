/* ------------------------------------------------------------------
   VOCABULAIRE
   Fichier ecrit par editeur.py — on peut aussi le modifier a la main.

   Pour chaque mot :
     "id"      : nom des fichiers (pictos/<id>.png et sons/<id>.wav)
     "mot"     : ce qui est ecrit sous le pictogramme
     "dit"     : ce que la tablette prononce
     "picto"   : mot-cle ou numero du pictogramme ARASAAC
   ------------------------------------------------------------------ */

var VOCABULAIRE = {
  "titre": "Je communique",
  "categories": [
    {
      "id": "favoris",
      "nom": "★ Essentiel",
      "couleur": "#5B87BF",
      "mots": [
        {
          "id": "oui",
          "mot": "oui",
          "dit": "oui",
          "picto": "oui"
        },
        {
          "id": "non",
          "mot": "non",
          "dit": "non",
          "picto": "non"
        },
        {
          "id": "toilettes",
          "mot": "toilettes",
          "dit": "je veux aller aux toilettes",
          "picto": "toilettes"
        },
        {
          "id": "aide",
          "mot": "aide-moi",
          "dit": "aide-moi",
          "picto": "aider"
        }
      ]
    },
    {
      "id": "veux",
      "nom": "Je veux",
      "couleur": "#5E9E6E",
      "mots": [
        {
          "id": "boire",
          "mot": "boire",
          "dit": "je veux boire",
          "picto": "boire"
        },
        {
          "id": "manger",
          "mot": "manger",
          "dit": "je veux manger",
          "picto": "manger"
        },
        {
          "id": "toilettes",
          "mot": "toilettes",
          "dit": "je veux aller aux toilettes",
          "picto": "toilettes"
        },
        {
          "id": "dormir",
          "mot": "dormir",
          "dit": "je veux dormir",
          "picto": "dormir"
        },
        {
          "id": "sortir",
          "mot": "sortir",
          "dit": "je veux sortir",
          "picto": "sortir"
        },
        {
          "id": "pause",
          "mot": "pause",
          "dit": "Je veux faire une pause",
          "picto": "38213"
        },
        {
          "id": "jouer",
          "mot": "jouer",
          "dit": "je veux jouer",
          "picto": "jouer"
        },
        {
          "id": "musique",
          "mot": "musique",
          "dit": "je veux de la musique",
          "picto": "musique"
        },
        {
          "id": "ordinateur",
          "mot": "ordinateur",
          "dit": "je veux l'ordinateur",
          "picto": "ordinateur"
        },
        {
          "id": "mouchoir",
          "mot": "mouchoir",
          "dit": "je veux un mouchoir",
          "picto": "mouchoir"
        },
        {
          "id": "dessiner",
          "mot": "dessiner",
          "dit": "je veux dessiner",
          "picto": "dessiner"
        },
        {
          "id": "livre",
          "mot": "livre",
          "dit": "je veux un livre",
          "picto": "livre"
        },
        {
          "id": "doudou",
          "mot": "doudou",
          "dit": "je veux mon doudou",
          "picto": "peluche"
        }
      ],
      "parPage": 9
    },
    {
      "id": "dis",
      "nom": "Je dis",
      "couleur": "#D9A62E",
      "mots": [
        {
          "id": "oui",
          "mot": "oui",
          "dit": "oui",
          "picto": "oui"
        },
        {
          "id": "non",
          "mot": "non",
          "dit": "non",
          "picto": "non"
        },
        {
          "id": "bonjour",
          "mot": "bonjour",
          "dit": "bonjour",
          "picto": "bonjour"
        },
        {
          "id": "aurevoir",
          "mot": "au revoir",
          "dit": "au revoir",
          "picto": "au revoir"
        },
        {
          "id": "merci",
          "mot": "merci",
          "dit": "merci",
          "picto": "merci"
        },
        {
          "id": "stp",
          "mot": "s'il te plaît",
          "dit": "s'il te plaît",
          "picto": "s'il te plait"
        },
        {
          "id": "aide",
          "mot": "aide-moi",
          "dit": "aide-moi",
          "picto": "aider"
        },
        {
          "id": "encore",
          "mot": "encore",
          "dit": "encore",
          "picto": "encore"
        },
        {
          "id": "fini",
          "mot": "fini",
          "dit": "j'ai fini",
          "picto": "fini"
        },
        {
          "id": "stop",
          "mot": "stop",
          "dit": "stop",
          "picto": "stop"
        },
        {
          "id": "attends",
          "mot": "attends",
          "dit": "attends",
          "picto": "attendre"
        },
        {
          "id": "saispas",
          "mot": "je ne sais pas",
          "dit": "je ne sais pas",
          "picto": "ne pas savoir"
        }
      ]
    },
    {
      "id": "ressens",
      "nom": "Je ressens",
      "couleur": "#5B87BF",
      "mots": [
        {
          "id": "content",
          "mot": "content",
          "dit": "je suis content",
          "picto": "content"
        },
        {
          "id": "triste",
          "mot": "triste",
          "dit": "je suis triste",
          "picto": "triste"
        },
        {
          "id": "colere",
          "mot": "en colère",
          "dit": "je suis en colère",
          "picto": "colere"
        },
        {
          "id": "peur",
          "mot": "peur",
          "dit": "j'ai peur",
          "picto": "peur"
        },
        {
          "id": "calme",
          "mot": "calme",
          "dit": "je suis calme",
          "picto": "calme"
        },
        {
          "id": "fatigue",
          "mot": "fatigué",
          "dit": "je suis fatigué",
          "picto": "fatigue"
        },
        {
          "id": "mal",
          "mot": "j'ai mal",
          "dit": "j'ai mal",
          "picto": "douleur"
        },
        {
          "id": "faim",
          "mot": "faim",
          "dit": "j'ai faim",
          "picto": "faim"
        },
        {
          "id": "soif",
          "mot": "soif",
          "dit": "j'ai soif",
          "picto": "soif"
        },
        {
          "id": "chaud",
          "mot": "chaud",
          "dit": "j'ai chaud",
          "picto": "chaud"
        },
        {
          "id": "froid",
          "mot": "froid",
          "dit": "j'ai froid",
          "picto": "froid"
        },
        {
          "id": "bruit",
          "mot": "trop de bruit",
          "dit": "il y a trop de bruit",
          "picto": "bruit"
        }
      ]
    },
    {
      "id": "ecole",
      "nom": "L'école",
      "couleur": "#D97C4E",
      "mots": [
        {
          "id": "maison",
          "mot": "la maison",
          "dit": "la maison",
          "picto": "maison"
        },
        {
          "id": "maman",
          "mot": "maman",
          "dit": "maman",
          "picto": "mere"
        },
        {
          "id": "papa",
          "mot": "papa",
          "dit": "papa",
          "picto": "pere"
        },
        {
          "id": "recreation",
          "mot": "récréation",
          "dit": "la récréation",
          "picto": "recreation"
        },
        {
          "id": "travailler",
          "mot": "travailler",
          "dit": "travailler",
          "picto": "travailler"
        },
        {
          "id": "classe",
          "mot": "la classe",
          "dit": "la classe",
          "picto": "salle de classe"
        },
        {
          "id": "sport",
          "mot": "sport",
          "dit": "le sport",
          "picto": "sport"
        },
        {
          "id": "ranger",
          "mot": "ranger",
          "dit": "ranger",
          "picto": "ranger"
        },
        {
          "id": "maitre",
          "mot": "le maître",
          "dit": "le maître",
          "picto": "enseignant"
        },
        {
          "id": "copain",
          "mot": "un copain",
          "dit": "un copain",
          "picto": "ami"
        }
      ]
    }
  ]
};
