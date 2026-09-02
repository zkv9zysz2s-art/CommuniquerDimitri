#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prepare le dossier de l'application « Je communique ».

A lancer sur le Mac, depuis le dossier qui contient index.html :

    python3 preparer.py

Le script :
  1. lit vocabulaire.js
  2. telecharge les pictogrammes ARASAAC dans pictos/
  3. fabrique les fichiers son dans sons/ avec la voix francaise de macOS
  4. affiche un rapport de ce qui a marche ou pas

Il ne remplace jamais un fichier deja present : si un pictogramme ne te plait
pas, tu supprimes le PNG et tu relances ; si tu veux ta propre voix, tu poses
ton enregistrement dans sons/<id>.wav et le script n'y touchera pas.

Options :
    --lister-voix      affiche les voix francaises installees, et s'arrete
    --voix NOM         impose une voix (refait tous les sons)
    --vitesse N        debit en mots/minute, 140 par defaut (refait tous les sons)
    --force            refait tout, meme ce qui existe deja
    --sans-son         seulement les pictogrammes
    --sans-picto       seulement les sons
    --debug            affiche le detail des erreurs reseau
"""

import json
import os
import re
import shutil
import ssl
import subprocess
import sys
import urllib.parse
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
DOSSIER_PICTOS = os.path.join(ICI, "pictos")
DOSSIER_SONS = os.path.join(ICI, "sons")
RESOLUTION = 300
VITESSE_DEFAUT = 140

UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15"}
DEBUG = False

# Une voix « Premium » ou « Amelioree » sonne infiniment moins robotique que la
# voix compacte installee par defaut. On les prefere systematiquement.
QUALITE = ["premium", "enhanced", "amelior", "amélior"]
NOMS_PREFERES = ["thomas", "aurelie", "aurélie", "audrey", "marie",
                 "amelie", "amélie", "nicolas", "daniel", "jacques"]


def log(*a):
    if DEBUG:
        print("      [debug]", *a)


# ---------------------------------------------------------------- vocabulaire

def lire_vocabulaire():
    chemin = os.path.join(ICI, "vocabulaire.js")
    if not os.path.exists(chemin):
        sys.exit("Fichier vocabulaire.js introuvable a cote de ce script.")
    with open(chemin, "r", encoding="utf-8") as f:
        brut = f.read()
    debut = brut.find("{", brut.find("var VOCABULAIRE"))
    fin = brut.rfind("}")
    if debut < 0 or fin < 0:
        sys.exit("vocabulaire.js : impossible de retrouver l'objet VOCABULAIRE.")
    texte = re.sub(r"/\*.*?\*/", "", brut[debut:fin + 1], flags=re.S)
    try:
        return json.loads(texte)
    except ValueError as e:
        sys.exit("vocabulaire.js n'est pas du JSON valide : %s" % e)


def tous_les_mots(voc):
    """Les mots uniques par identifiant.

    Un meme mot peut figurer dans plusieurs categories (par exemple « oui »
    dans Essentiel et dans Je dis) : il partage alors le meme pictogramme et
    le meme son, on ne le prepare qu'une fois.
    """
    mots, vus = [], {}
    for cat in voc.get("categories", []):
        for mot in cat.get("mots", []):
            mid = mot["id"]
            if mid in vus:
                if vus[mid].get("dit") != mot.get("dit"):
                    print("Attention : « %s » n'a pas le meme texte parle selon "
                          "les categories, c'est « %s » qui est retenu."
                          % (mid, vus[mid].get("dit")))
                continue
            vus[mid] = mot
            mots.append(mot)
    return mots


# ---------------------------------------------------------------------- reseau
#
# Python installe depuis python.org n'a pas toujours de certificats valides
# (il faut avoir lance « Install Certificates.command »). Plutot que d'imposer
# ca, on bascule automatiquement sur curl, qui est toujours present sur macOS
# et qui utilise le trousseau du systeme.

CURL = shutil.which("curl")
_transport = None          # "urllib" ou "curl", decide au premier appel


def _ctx():
    try:
        import certifi
        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return ssl.create_default_context()


def _http_urllib(url, timeout):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=timeout, context=_ctx()).read()


def _http_curl(url, timeout):
    r = subprocess.run(
        [CURL, "-sSL", "--max-time", str(timeout), "-A", UA["User-Agent"], url],
        capture_output=True)
    if r.returncode != 0:
        raise IOError((r.stderr or b"").decode("utf-8", "replace").strip())
    return r.stdout


def http(url, timeout=25):
    global _transport
    if _transport == "curl":
        return _http_curl(url, timeout)
    try:
        return _http_urllib(url, timeout)
    except Exception as e:
        if _transport is None and CURL:
            log("urllib a echoue (%s) -> bascule sur curl" % e)
            _transport = "curl"
            return _http_curl(url, timeout)
        raise


def tester_connexion():
    """Verifie qu'on sait joindre ARASAAC, et le dit clairement si non."""
    url = "https://api.arasaac.org/v1/pictograms/fr/search/eau"
    try:
        data = http(url, timeout=20)
        json.loads(data.decode("utf-8"))
        print("Connexion a ARASAAC : ok (%s)" % (_transport or "urllib"))
        return True
    except Exception as e:
        print("Connexion a ARASAAC : ECHEC")
        print("   %s" % e)
        print("   Verifie que le Mac est bien connecte a internet, puis relance.")
        print("   Si le probleme persiste : python3 preparer.py --debug")
        return False


# ---------------------------------------------------------------- pictogrammes

def chercher_id(terme):
    """Renvoie l'identifiant ARASAAC du premier pictogramme trouve, ou None."""
    q = urllib.parse.quote(terme)
    urls = [
        "https://api.arasaac.org/v1/pictograms/fr/bestsearch/%s" % q,
        "https://api.arasaac.org/v1/pictograms/fr/search/%s" % q,
        "https://api.arasaac.org/api/pictograms/fr/search/%s" % q,
    ]
    for url in urls:
        try:
            data = json.loads(http(url).decode("utf-8"))
        except Exception as e:
            log("recherche KO", url, "->", e)
            continue
        if isinstance(data, list) and data:
            for cle in ("_id", "id", "idPictogram"):
                if cle in data[0]:
                    return data[0][cle]
        log("recherche sans resultat", url)
    return None


def telecharger_picto(pid, destination):
    urls = [
        "https://static.arasaac.org/pictograms/%s/%s_%d.png" % (pid, pid, RESOLUTION),
        "https://api.arasaac.org/v1/pictograms/%s?resolution=%d&download=false" % (pid, RESOLUTION),
        "https://api.arasaac.org/api/pictograms/%s?resolution=%d&download=false" % (pid, RESOLUTION),
    ]
    for url in urls:
        try:
            contenu = http(url)
        except Exception as e:
            log("image KO", url, "->", e)
            continue
        if contenu[:8] == b"\x89PNG\r\n\x1a\n":
            with open(destination, "wb") as f:
                f.write(contenu)
            return True
        log("image pas au format PNG", url, contenu[:20])
    return False


# ---------------------------------------------------------------------- voix

def voix_francaises():
    """[(nom, langue, qualite_estimee)] pour toutes les voix fr installees."""
    try:
        sortie = subprocess.run(["say", "-v", "?"], capture_output=True,
                                text=True).stdout
    except FileNotFoundError:
        return []
    voix = []
    for ligne in sortie.splitlines():
        m = re.match(r"^(.+?)\s{2,}([a-z]{2}[-_][A-Z]{2})", ligne)
        if not m:
            continue
        nom, langue = m.group(1).strip(), m.group(2)
        if not langue.lower().startswith("fr"):
            continue
        bas = nom.lower()
        note = 0
        for i, mot in enumerate(QUALITE):
            if mot in bas:
                note = 10 - i
        voix.append((nom, langue, note))
    return voix


def afficher_voix():
    voix = voix_francaises()
    if not voix:
        print("Aucune voix francaise installee sur ce Mac.")
    else:
        print("Voix francaises installees :\n")
        for nom, langue, note in voix:
            print("   %-34s %s%s" % (nom, langue, "   <- haute qualite" if note else ""))
    print("""
Les voix sans mention sont les voix « compactes » : c'est celles qui sonnent
robotiques. Pour installer les bonnes :

   Reglages Systeme > Accessibilite > Contenu enonce > Voix systeme
   > Gerer les voix... > Francais
   > coche Thomas (Premium), Aurelie (Premium), Marie (Premium)...

Le telechargement fait quelques centaines de Mo mais la difference est enorme.
Ensuite :  python3 preparer.py --voix "Thomas (Premium)"
""")


def choisir_voix(impose):
    voix = voix_francaises()
    if impose:
        # on retrouve le nom exact, sans se soucier des majuscules
        for nom, _l, _n in voix:
            if nom.lower() == impose.lower():
                return nom
        for nom, _l, _n in voix:
            if impose.lower() in nom.lower() or nom.lower() in impose.lower():
                print("Voix « %s » -> j'utilise « %s »" % (impose, nom))
                return nom
        print("Voix « %s » introuvable sur ce Mac." % impose)
        if voix:
            print("Voix francaises installees :")
            for nom, _l, _n in voix:
                print("   %s" % nom)
        print("Pour en installer d'autres : python3 preparer.py --lister-voix")
        return None
    if not voix:
        return None
    def cle(v):
        nom = v[0].lower()
        rang = 99
        for i, n in enumerate(NOMS_PREFERES):
            if nom.startswith(n):
                rang = i
                break
        return (-v[2], rang)
    voix.sort(key=cle)
    return voix[0][0]


def fabriquer_son(texte, voix, vitesse, destination):
    base = ["say"] + (["-v", voix] if voix else []) + ["-r", str(vitesse)]
    try:
        r = subprocess.run(base + ["--data-format=LEI16@22050", "-o", destination, texte],
                           capture_output=True, text=True)
    except FileNotFoundError:
        return False, "la commande « say » est introuvable (ce script veut un Mac)"
    if r.returncode == 0 and os.path.exists(destination):
        return True, ""
    aiff = destination[:-4] + ".aiff"
    r = subprocess.run(base + ["-o", aiff, texte], capture_output=True, text=True)
    if r.returncode != 0:
        return False, (r.stderr or "").strip()
    c = subprocess.run(["afconvert", "-f", "WAVE", "-d", "LEI16@22050", aiff, destination],
                       capture_output=True, text=True)
    try:
        os.remove(aiff)
    except OSError:
        pass
    if c.returncode != 0:
        return False, (c.stderr or "").strip()
    return True, ""


# ------------------------------------------------------------- publication
#
# Ces trois fichiers rendent l'application installable depuis une adresse web
# (GitHub Pages par exemple) et utilisable ensuite sans aucune connexion.
# Ils sont regeneres a chaque modification, il n'y a pas d'etape a penser.

SW = """/* Genere automatiquement. Ne pas modifier a la main. */
var VERSION = "%(version)s";
var CACHE = "communiquer-" + VERSION;
var FICHIERS = %(fichiers)s;

self.addEventListener("install", function (e) {
  self.skipWaiting();
  e.waitUntil(caches.open(CACHE).then(function (c) {
    return Promise.all(FICHIERS.map(function (f) {
      return c.add(new Request(f, { cache: "reload" }))["catch"](function () {});
    }));
  }));
});

self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (l) {
    return Promise.all(l.map(function (k) {
      return k === CACHE ? null : caches.delete(k);
    }));
  }).then(function () { return self.clients.claim(); }));
});

/* Les fichiers son sont demandes par tranches d'octets (en-tete Range).
   Safari, sur iPad, refuse une reponse complete a une demande de tranche :
   sans ce traitement, les pictogrammes s'affichent hors connexion mais
   aucun son ne sort. On decoupe donc nous-memes la tranche demandee. */
function tranche(requete, entete) {
  return caches.match(requete, { ignoreSearch: true, ignoreVary: true })
    .then(function (rep) {
      if (!rep) { return fetch(requete); }
      return rep.arrayBuffer().then(function (buf) {
        var total = buf.byteLength;
        var m = /bytes=(\\d*)-(\\d*)/.exec(entete) || [];
        var debut = m[1] ? parseInt(m[1], 10) : 0;
        var fin = m[2] ? parseInt(m[2], 10) : total - 1;
        if (isNaN(debut) || debut < 0) { debut = 0; }
        if (isNaN(fin) || fin >= total) { fin = total - 1; }
        if (debut > fin) { debut = 0; }
        var part = buf.slice(debut, fin + 1);
        return new Response(part, {
          status: 206,
          statusText: "Partial Content",
          headers: {
            "Content-Type": rep.headers.get("Content-Type") || "audio/wav",
            "Content-Length": String(part.byteLength),
            "Content-Range": "bytes " + debut + "-" + fin + "/" + total,
            "Accept-Ranges": "bytes"
          }
        });
      });
    });
}

self.addEventListener("fetch", function (e) {
  if (e.request.method !== "GET") { return; }
  if (e.request.url.indexOf("version.json") >= 0) { return; }

  var entete = e.request.headers.get("range");
  if (entete) { e.respondWith(tranche(e.request, entete)); return; }

  e.respondWith(
    caches.match(e.request, { ignoreSearch: true, ignoreVary: true }).then(function (r) {
      if (r) { return r; }
      return fetch(e.request).then(function (rep) {
        if (rep && rep.status === 200 && rep.type === "basic") {
          var copie = rep.clone();
          caches.open(CACHE).then(function (c) { c.put(e.request, copie); });
        }
        return rep;
      })["catch"](function () {
        return e.request.mode === "navigate" ? caches.match("index.html") : undefined;
      });
    })
  );
});
"""


def publier(voc=None, bavard=False):
    import time
    if voc is None:
        voc = lire_vocabulaire()
    version = time.strftime("%Y%m%d-%H%M%S")
    titre = voc.get("titre") or "Je communique"

    fichiers = ["./", "index.html", "vocabulaire.js", "version.js",
                "manifest.json", "icone-180.png", "icone-192.png", "icone-512.png"]
    for dossier, prefixe in ((DOSSIER_PICTOS, "pictos/"), (DOSSIER_SONS, "sons/")):
        if os.path.isdir(dossier):
            for n in sorted(os.listdir(dossier)):
                if not n.startswith("."):
                    fichiers.append(prefixe + n)

    def ecrire(nom, contenu):
        with open(os.path.join(ICI, nom), "w", encoding="utf-8") as f:
            f.write(contenu)

    ecrire("version.js", 'var VERSION = "%s";\n' % version)
    ecrire("version.json", json.dumps({"v": version}) + "\n")
    ecrire("manifest.json", json.dumps({
        "name": titre,
        "short_name": titre if len(titre) <= 12 else "Communiquer",
        "start_url": "./",
        "scope": "./",
        "display": "standalone",
        "orientation": "landscape",
        "background_color": "#FBF8F3",
        "theme_color": "#232B3E",
        "icons": [
            {"src": "icone-192.png", "sizes": "192x192", "type": "image/png",
             "purpose": "any"},
            {"src": "icone-512.png", "sizes": "512x512", "type": "image/png",
             "purpose": "any maskable"}]},
        ensure_ascii=False, indent=2) + "\n")
    ecrire("sw.js", SW % {"version": version,
                          "fichiers": json.dumps(fichiers, ensure_ascii=False)})
    ecrire(".nojekyll", "")
    ecrire("robots.txt", "User-agent: *\nDisallow: /\n")

    if bavard:
        print("Publication preparee : version %s, %d fichiers hors ligne."
              % (version, len(fichiers)))
    return version


# --------------------------------------------------------------------- main

def option(nom, defaut=None):
    if nom in sys.argv:
        i = sys.argv.index(nom)
        if i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return defaut


def main():
    global DEBUG
    DEBUG = "--debug" in sys.argv

    if "--lister-voix" in sys.argv:
        afficher_voix()
        return

    if "--publier" in sys.argv:
        publier(bavard=True)
        print("Depose maintenant le dossier sur GitHub Desktop et publie.")
        return

    force = "--force" in sys.argv
    sans_son = "--sans-son" in sys.argv
    sans_picto = "--sans-picto" in sys.argv
    voix_imposee = option("--voix")
    vitesse = int(option("--vitesse", VITESSE_DEFAUT))
    # changer de voix ou de debit n'a de sens que si on refait les sons
    force_son = force or voix_imposee is not None or "--vitesse" in sys.argv

    voc = lire_vocabulaire()
    mots = tous_les_mots(voc)
    os.makedirs(DOSSIER_PICTOS, exist_ok=True)
    os.makedirs(DOSSIER_SONS, exist_ok=True)

    if not sans_picto:
        if not tester_connexion():
            if sans_son:
                return
            print("   -> on continue quand meme avec les sons.\n")
            sans_picto = True

    voix = None
    if not sans_son:
        voix = choisir_voix(voix_imposee)
        if voix is None:
            if voix_imposee:
                sys.exit("\nRelance avec un des noms ci-dessus, entre guillemets.")
            print("Aucune voix francaise trouvee. Lance : python3 preparer.py --lister-voix")
            sans_son = True
        else:
            haute = any(q in voix.lower() for q in QUALITE)
            print("Voix utilisee : %s  (%d mots/minute)%s"
                  % (voix, vitesse, "" if haute else "   <- voix compacte, sonne robotique"))
            if not haute:
                print("   pour une vraie voix : python3 preparer.py --lister-voix")

    print("\n%d mots a preparer.\n" % len(mots))

    pictos_ok, pictos_ko, pictos_deja = 0, [], 0
    sons_ok, sons_ko, sons_deja = 0, [], 0

    for n, mot in enumerate(mots, 1):
        mid = mot["id"]
        etat = []

        if not sans_picto:
            dest = os.path.join(DOSSIER_PICTOS, mid + ".png")
            if os.path.exists(dest) and not force:
                pictos_deja += 1
                etat.append("picto deja la")
            else:
                terme = str(mot.get("picto") or mot.get("mot"))
                pid = terme if terme.isdigit() else chercher_id(terme)
                if pid and telecharger_picto(pid, dest):
                    pictos_ok += 1
                    etat.append("picto %s" % pid)
                else:
                    pictos_ko.append(mid)
                    etat.append("PICTO ECHOUE")

        if not sans_son:
            dest = os.path.join(DOSSIER_SONS, mid + ".wav")
            if os.path.exists(dest) and not force_son:
                sons_deja += 1
                etat.append("son deja la")
            else:
                ok, err = fabriquer_son(mot.get("dit") or mot.get("mot"), voix, vitesse, dest)
                if ok:
                    sons_ok += 1
                    etat.append("son ok")
                else:
                    sons_ko.append(mid)
                    etat.append("SON ECHOUE %s" % err)

        print("  %2d/%d  %-14s %s" % (n, len(mots), mid, " | ".join(etat)))

    print("\n----- resultat -----")
    if not sans_picto:
        print("Pictogrammes : %d telecharges, %d deja presents, %d en echec"
              % (pictos_ok, pictos_deja, len(pictos_ko)))
        if pictos_ko:
            print("  a regler : %s" % ", ".join(pictos_ko))
            print("  -> change le mot-cle \"picto\" dans vocabulaire.js, ou mets")
            print("     directement le numero du pictogramme trouve sur arasaac.org,")
            print("     ou depose toi-meme un PNG dans pictos/")
    if not sans_son:
        print("Sons : %d fabriques, %d deja presents, %d en echec"
              % (sons_ok, sons_deja, len(sons_ko)))
        if sons_ko:
            print("  a regler : %s" % ", ".join(sons_ko))

    v = publier(voc)
    print("Publication : version %s prete (fichiers manifest.json, sw.js, version.js)." % v)

    print("\nOuvre index.html dans un navigateur pour verifier avant de copier")
    print("le dossier sur la tablette.")


if __name__ == "__main__":
    main()
