#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Editeur des tableaux de communication.

    python3 editeur.py

Ouvre une page dans le navigateur du Mac. On y cherche un mot dans tout
ARASAAC, on clique, et le pictogramme est telecharge et le son fabrique
dans la foulee. Les categories se creent, se renomment, se reordonnent
et se suppriment a la souris.

Tout est enregistre immediatement dans vocabulaire.js : il n'y a pas de
bouton « sauvegarder », il n'y a rien a oublier.

Arreter le serveur : Ctrl-C dans le Terminal.
"""

import json
import os
import re
import sys
import threading
import unicodedata
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ICI)
import preparer  # noqa: E402

PORT = 8765
COULEURS = ["#9B6BA8", "#5E9E6E", "#D9A62E", "#5B87BF", "#D97C4E",
            "#C4646B", "#4F9A94", "#8A7E6B"]

ENTETE = """/* ------------------------------------------------------------------
   VOCABULAIRE
   Fichier ecrit par editeur.py — on peut aussi le modifier a la main.

   Pour chaque mot :
     "id"      : nom des fichiers (pictos/<id>.png et sons/<id>.wav)
     "mot"     : ce qui est ecrit sous le pictogramme
     "dit"     : ce que la tablette prononce
     "picto"   : mot-cle ou numero du pictogramme ARASAAC
   ------------------------------------------------------------------ */

var VOCABULAIRE = """


# --------------------------------------------------------------- utilitaires

def slug(texte):
    t = unicodedata.normalize("NFKD", texte or "")
    t = "".join(c for c in t if not unicodedata.combining(c))
    t = re.sub(r"[^A-Za-z0-9]+", "", t).lower()
    return t or "mot"


def ids_existants(voc):
    r = set()
    for c in voc.get("categories", []):
        for m in c.get("mots", []):
            r.add(m["id"])
    return r


def id_libre(base, pris):
    if base not in pris:
        return base
    n = 2
    while "%s%d" % (base, n) in pris:
        n += 1
    return "%s%d" % (base, n)


def ecrire_vocabulaire(voc):
    corps = json.dumps(voc, ensure_ascii=False, indent=2)
    with open(os.path.join(ICI, "vocabulaire.js"), "w", encoding="utf-8") as f:
        f.write(ENTETE + corps + ";\n")
    # on regenere aussi les fichiers de publication : le dossier est toujours
    # pret a etre pousse sur GitHub, il n'y a pas d'etape a penser
    try:
        preparer.publier(voc)
    except Exception:
        pass


def son_existe(mid):
    return os.path.exists(os.path.join(preparer.DOSSIER_SONS, mid + ".wav"))


def picto_existe(mid):
    return os.path.exists(os.path.join(preparer.DOSSIER_PICTOS, mid + ".png"))


REGLAGES = {"voix": None, "vitesse": preparer.VITESSE_DEFAUT}


# ------------------------------------------------------------------- la page

PAGE = """<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<title>Editeur - Je communique</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700&family=Mulish:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root{--papier:#FBF8F3;--encre:#232B3E;--trait:#E2D9C9;--doux:#8A7E6B;}
*{box-sizing:border-box;}
body{margin:0;background:var(--papier);color:var(--encre);
  font-family:Mulish,"Helvetica Neue",Arial,sans-serif;font-size:15px;}
h1,h2,h3{font-family:"Baloo 2",Mulish,sans-serif;margin:0;}
#haut{display:flex;align-items:center;gap:16px;padding:12px 20px;
  background:#fff;border-bottom:2px solid var(--trait);position:sticky;top:0;z-index:9;}
#haut h1{font-size:21px;}
#etat{margin-left:auto;font-size:13px;color:var(--doux);}
#etat.vu{color:#4E7A48;font-weight:700;}
select,input[type=text],input[type=number]{font:inherit;padding:7px 10px;
  border:2px solid var(--trait);border-radius:9px;background:#fff;color:inherit;}
button{font:inherit;font-weight:700;padding:8px 14px;border:2px solid var(--encre);
  border-radius:9px;background:#fff;color:var(--encre);cursor:pointer;}
button:hover{background:var(--encre);color:#fff;}
button.discret{border-color:var(--trait);color:var(--doux);font-weight:600;}
button.discret:hover{background:var(--trait);color:var(--encre);}
#corps{display:grid;grid-template-columns:230px 1fr 330px;gap:20px;padding:20px;
  align-items:start;}
.bloc{background:#fff;border:2px solid var(--trait);border-radius:16px;padding:14px;}
.bloc h2{font-size:16px;margin-bottom:10px;}
.catl{display:flex;align-items:center;gap:8px;padding:9px 10px;border-radius:10px;
  border:2px solid transparent;cursor:pointer;margin-bottom:4px;}
.catl:hover{background:#F7F3EC;}
.catl.on{border-color:var(--encre);background:#F7F3EC;}
.pastille{width:12px;height:26px;border-radius:4px;flex:none;}
.catl .nb{margin-left:auto;font-size:12px;color:var(--doux);}
#grille{display:grid;grid-template-columns:repeat(auto-fill,minmax(152px,1fr));gap:12px;}
.carte{border:3px solid var(--trait);border-radius:14px;background:#fff;
  padding:8px;text-align:center;position:relative;}
.carte img{width:100%;height:86px;object-fit:contain;}
.carte .vide{height:86px;display:flex;align-items:center;justify-content:center;
  font-weight:700;color:var(--doux);font-size:13px;}
.carte .nom{font-weight:700;margin-top:6px;font-size:14px;}
.carte .dit{font-size:11px;color:var(--doux);margin-top:2px;min-height:14px;}
.carte .outils{display:flex;gap:3px;justify-content:center;margin-top:7px;flex-wrap:wrap;}
.carte .outils button{padding:2px 6px;font-size:12px;border-width:1px;line-height:1.3;}
.pb{color:#B4462F;font-size:11px;font-weight:700;}
#resultats{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-top:12px;}
#resultats figure{margin:0;border:2px solid var(--trait);border-radius:10px;padding:5px;
  cursor:pointer;background:#fff;}
#resultats figure:hover{border-color:var(--encre);}
#resultats img{width:100%;height:66px;object-fit:contain;}
.aide{color:var(--doux);font-size:13px;line-height:1.5;margin-top:10px;}
dialog{border:2px solid var(--encre);border-radius:16px;padding:20px;max-width:420px;
  background:var(--papier);}
dialog::backdrop{background:rgba(35,43,62,.4);}
dialog label{display:block;margin:12px 0 4px;font-weight:700;font-size:13px;}
dialog input{width:100%;}
.rangee{display:flex;gap:8px;margin-top:18px;justify-content:flex-end;}
</style></head><body>

<div id="haut">
  <h1>Je communique — editeur</h1>
  <label>Voix <select id="voix"></select></label>
  <label>Debit <input type="number" id="vitesse" min="90" max="220" step="5" style="width:74px"></label>
  <button class="discret" id="refaire">Refaire tous les sons</button>
  <span id="etat">pret</span>
</div>

<div id="corps">
  <div class="bloc">
    <h2>Categories</h2>
    <div id="cats"></div>
    <button style="margin-top:10px;width:100%" id="addcat">+ Categorie</button>
  </div>

  <div class="bloc">
    <h2 id="titrecat">-</h2>
    <div id="grille"></div>
    <p class="aide" id="conseil"></p>
  </div>

  <div class="bloc">
    <h2>Ajouter un mot</h2>
    <div style="display:flex;gap:6px">
      <input type="text" id="q" placeholder="boire, trampoline, Lucie..." style="flex:1">
      <button id="go">Chercher</button>
    </div>
    <div id="resultats"></div>
    <p class="aide" id="aiderech">Cherche dans les milliers de pictogrammes ARASAAC.
      Clique sur celui que tu veux : l'image est telechargee et le son fabrique
      tout de suite.</p>
  </div>
</div>

<dialog id="dlgcopie">
  <h2 id="dlgtitrecopie">Copier vers</h2>
  <div id="listecats" style="margin-top:12px"></div>
  <p class="aide">Le mot copie garde le meme pictogramme et le meme son : il
    n'y a rien a retelecharger.</p>
  <div class="rangee"><button class="discret" id="copienon">Fermer</button></div>
</dialog>

<dialog id="dlg">
  <h2 id="dlgtitre">Nouveau mot</h2>
  <img id="dlgimg" style="height:96px;display:block;margin:10px auto">
  <label>Ecrit sous le pictogramme</label>
  <input type="text" id="dlgmot">
  <label>Ce que la tablette prononce</label>
  <input type="text" id="dlgdit">
  <div class="rangee">
    <button class="discret" id="dlgnon">Annuler</button>
    <button id="dlgoui">Valider</button>
  </div>
</dialog>

<script>
let V = null, iCat = 0, dernierePicto = null, modeEdition = null;
const PP = [["", "Automatique (tout sur une page)"],
            ["4", "4 par page - 2 x 2"], ["6", "6 par page - 3 x 2"],
            ["9", "9 par page - 3 x 3"], ["12", "12 par page - 4 x 3"],
            ["16", "16 par page - 4 x 4"], ["20", "20 par page - 5 x 4"]];
const $ = s => document.querySelector(s);
const etat = (t, ok) => { const e = $("#etat"); e.textContent = t; e.className = ok ? "vu" : ""; };

async function api(chemin, corps) {
  const o = corps ? { method: "POST", headers: { "Content-Type": "application/json" },
                      body: JSON.stringify(corps) } : {};
  const r = await fetch(chemin, o);
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

async function charger() {
  const d = await api("/api/etat");
  V = d.vocabulaire;
  $("#voix").innerHTML = d.voix.map(v => `<option${v === d.voixActive ? " selected" : ""}>${v}</option>`).join("");
  $("#vitesse").value = d.vitesse;
  dessiner();
}

async function enregistrer() {
  etat("enregistrement...");
  await api("/api/enregistrer", V);
  etat("enregistre", true);
  setTimeout(() => etat("pret"), 1600);
}

function dessiner() {
  $("#cats").innerHTML = "";
  V.categories.forEach((c, i) => {
    const d = document.createElement("div");
    d.className = "catl" + (i === iCat ? " on" : "");
    d.innerHTML = `<span class="pastille" style="background:${c.couleur}"></span>
      <span>${c.nom}</span><span class="nb">${c.mots.length}</span>`;
    d.onclick = () => { iCat = i; dessiner(); };
    $("#cats").appendChild(d);
  });

  const c = V.categories[iCat];
  if (!c) { $("#grille").innerHTML = ""; return; }
  const cur = c.parPage ? String(c.parPage) : "";
  const opts = PP.map(o => `<option value="${o[0]}"${o[0] === cur ? " selected" : ""}>${o[1]}</option>`).join("");
  $("#titrecat").innerHTML = `${c.nom}
    <select id="pp" style="font-size:13px;padding:4px 8px;margin-left:6px">${opts}</select>
    <button class="discret" style="font-size:12px;padding:3px 8px" onclick="renommer()">renommer</button>
    <button class="discret" style="font-size:12px;padding:3px 8px" onclick="couleur()">couleur</button>
    <button class="discret" style="font-size:12px;padding:3px 8px" onclick="monterCat()">monter</button>
    <button class="discret" style="font-size:12px;padding:3px 8px" onclick="supprimerCat()">supprimer</button>`;
  $("#pp").onchange = e => {
    const v = e.target.value;
    if (v) c.parPage = +v; else delete c.parPage;
    dessiner(); enregistrer();
  };

  $("#grille").innerHTML = "";
  c.mots.forEach((m, j) => {
    const carte = document.createElement("div");
    carte.className = "carte";
    carte.style.borderColor = c.couleur;
    const img = m.aPicto ? `<img src="/pictos/${m.id}.png?v=${Date.now()}">`
                         : `<div class="vide">pas d'image</div>`;
    carte.innerHTML = `${img}<div class="nom">${m.mot}</div>
      <div class="dit">${m.dit || ""}</div>
      ${m.aSon ? "" : '<div class="pb">son manquant</div>'}
      <div class="outils">
        <button title="ecouter">&#9654;</button>
        <button title="modifier">&#9998;</button>
        <button title="copier dans une autre categorie">&#10697;</button>
        <button title="vers la gauche">&larr;</button>
        <button title="vers la droite">&rarr;</button>
        <button title="retirer">&times;</button>
      </div>`;
    const b = carte.querySelectorAll(".outils button");
    b[0].onclick = () => new Audio(`/sons/${m.id}.wav?v=${Date.now()}`).play();
    b[1].onclick = () => modifier(j);
    b[2].onclick = () => copier(j);
    b[3].onclick = () => deplacer(j, -1);
    b[4].onclick = () => deplacer(j, 1);
    b[5].onclick = () => retirer(j);
    $("#grille").appendChild(carte);
  });

  const n = c.mots.length;
  const pp = c.parPage || n || 1;
  const pages = Math.max(1, Math.ceil(n / pp));
  const g = pp <= 4 ? "2 x 2" : pp <= 6 ? "3 x 2" : pp <= 9 ? "3 x 3"
          : pp <= 12 ? "4 x 3" : pp <= 16 ? "4 x 4" : "5 x 4";
  $("#conseil").textContent = n === 0
    ? "Categorie vide : elle n'apparaitra pas sur la tablette."
    : `${n} mot(s), ${pp} par page — ${pages} page(s) sur la tablette, grille ${g}.` +
      (pages > 1 ? " Une bande de navigation apparait en bas de l'ecran." : "") +
      (pp > 20 ? " Au-dela de 20 cases par page, elles deviennent petites." : "");
}

/* ---- copier un mot dans une autre categorie ---- */
function copier(j) {
  const m = V.categories[iCat].mots[j];
  const l = $("#listecats");
  l.innerHTML = "";
  V.categories.forEach((c, i) => {
    if (i === iCat) return;
    const deja = c.mots.some(x => x.id === m.id);
    const b = document.createElement("button");
    b.className = deja ? "discret" : "";
    b.style.cssText = "display:block;width:100%;margin-bottom:6px;text-align:left";
    b.textContent = c.nom + (deja ? "   (deja present)" : "");
    b.disabled = deja;
    b.onclick = () => {
      c.mots.push({ id: m.id, mot: m.mot, dit: m.dit, picto: m.picto });
      $("#dlgcopie").close();
      dessiner(); enregistrer();
    };
    l.appendChild(b);
  });
  if (!l.children.length) {
    l.innerHTML = '<p class="aide">Il n\\'y a pas d\\'autre categorie.</p>';
  }
  $("#dlgtitrecopie").textContent = `Copier « ${m.mot} » vers`;
  $("#dlgcopie").showModal();
}
$("#copienon").onclick = () => $("#dlgcopie").close();

/* ---- categories ---- */
async function renommer() {
  const v = prompt("Nom de la categorie", V.categories[iCat].nom);
  if (v) { V.categories[iCat].nom = v; dessiner(); enregistrer(); }
}
async function couleur() {
  const c = V.categories[iCat];
  const l = ${couleurs_js};
  c.couleur = l[(l.indexOf(c.couleur) + 1) % l.length];
  dessiner(); enregistrer();
}
async function monterCat() {
  if (iCat === 0) return;
  const a = V.categories;
  [a[iCat - 1], a[iCat]] = [a[iCat], a[iCat - 1]];
  iCat--; dessiner(); enregistrer();
}
async function supprimerCat() {
  if (!confirm(`Supprimer la categorie « ${V.categories[iCat].nom} » ?
Les pictogrammes et les sons restent dans les dossiers.`)) return;
  V.categories.splice(iCat, 1);
  iCat = Math.max(0, iCat - 1); dessiner(); enregistrer();
}
$("#addcat").onclick = async () => {
  const nom = prompt("Nom de la nouvelle categorie");
  if (!nom) return;
  V.categories.push({ id: "c" + Date.now(), nom,
    couleur: ${couleurs_js}[V.categories.length % ${nb_couleurs}], mots: [] });
  iCat = V.categories.length - 1; dessiner(); enregistrer();
};

/* ---- mots ---- */
function deplacer(j, d) {
  const a = V.categories[iCat].mots, k = j + d;
  if (k < 0 || k >= a.length) return;
  [a[j], a[k]] = [a[k], a[j]];
  dessiner(); enregistrer();
}
function retirer(j) {
  V.categories[iCat].mots.splice(j, 1);
  dessiner(); enregistrer();
}
function modifier(j) {
  const m = V.categories[iCat].mots[j];
  modeEdition = j;
  $("#dlgtitre").textContent = "Modifier";
  $("#dlgimg").src = m.aPicto ? `/pictos/${m.id}.png` : "";
  $("#dlgimg").style.display = m.aPicto ? "block" : "none";
  $("#dlgmot").value = m.mot;
  $("#dlgdit").value = m.dit || "";
  $("#dlg").showModal();
}

/* ---- recherche ARASAAC ---- */
$("#go").onclick = chercher;
$("#q").onkeydown = e => { if (e.key === "Enter") chercher(); };

async function chercher() {
  const q = $("#q").value.trim();
  if (!q) return;
  $("#resultats").innerHTML = "";
  etat("recherche...");
  try {
    const r = await api("/api/recherche?q=" + encodeURIComponent(q));
    etat("pret");
    if (!r.length) { $("#aiderech").textContent = "Aucun pictogramme pour « " + q + " »."; return; }
    $("#aiderech").textContent = "Clique sur le pictogramme que tu veux ajouter.";
    r.forEach(p => {
      const f = document.createElement("figure");
      f.innerHTML = `<img src="${p.image}" loading="lazy">`;
      f.onclick = () => { dernierePicto = p; modeEdition = null;
        $("#dlgtitre").textContent = "Ajouter un mot";
        $("#dlgimg").src = p.image; $("#dlgimg").style.display = "block";
        $("#dlgmot").value = q; $("#dlgdit").value = q;
        $("#dlg").showModal(); };
      $("#resultats").appendChild(f);
    });
  } catch (e) { etat("erreur reseau"); $("#aiderech").textContent = String(e); }
}

/* ---- boite de dialogue ---- */
$("#dlgnon").onclick = () => $("#dlg").close();
$("#dlgoui").onclick = async () => {
  const mot = $("#dlgmot").value.trim(), dit = $("#dlgdit").value.trim();
  if (!mot) return;
  $("#dlg").close();
  etat("fabrication du son...");
  if (modeEdition !== null) {
    const m = V.categories[iCat].mots[modeEdition];
    const change = m.dit !== dit;
    m.mot = mot; m.dit = dit;
    await api("/api/enregistrer", V);
    if (change) { const r = await api("/api/son", { id: m.id, dit,
      voix: $("#voix").value, vitesse: +$("#vitesse").value }); m.aSon = r.ok; }
  } else {
    const r = await api("/api/ajouter", { mot, dit, pictoId: dernierePicto.id,
      categorie: iCat, voix: $("#voix").value, vitesse: +$("#vitesse").value });
    V = r.vocabulaire;
  }
  dessiner(); etat("enregistre", true); setTimeout(() => etat("pret"), 1600);
};

$("#refaire").onclick = async () => {
  if (!confirm("Refabriquer les " + V.categories.reduce((n, c) => n + c.mots.length, 0) +
    " sons avec cette voix et ce debit ?\\nLes enregistrements que tu as faits toi-meme seront remplaces.")) return;
  etat("fabrication...");
  const r = await api("/api/tousLesSons", { voix: $("#voix").value, vitesse: +$("#vitesse").value });
  V = r.vocabulaire; dessiner(); etat(r.faits + " sons refaits", true);
};

charger();
</script>
</body></html>
"""

PAGE = PAGE.replace("${couleurs_js}", json.dumps(COULEURS))
PAGE = PAGE.replace("${nb_couleurs}", str(len(COULEURS)))


# ---------------------------------------------------------------- le serveur

def enrichir(voc):
    """Ajoute a chaque mot l'info « son present » / « picto present »."""
    for c in voc.get("categories", []):
        for m in c.get("mots", []):
            m["aSon"] = son_existe(m["id"])
            m["aPicto"] = picto_existe(m["id"])
    return voc


def nettoyer(voc):
    """Enleve les champs de service avant d'ecrire le fichier."""
    propre = json.loads(json.dumps(voc))
    for c in propre.get("categories", []):
        for m in c.get("mots", []):
            m.pop("aSon", None)
            m.pop("aPicto", None)
    return propre


class Handler(BaseHTTPRequestHandler):

    def log_message(self, *a):
        pass

    # -------------------------------------------------- reponses

    def envoyer(self, contenu, type_mime="application/json", code=200):
        if isinstance(contenu, (dict, list)):
            contenu = json.dumps(contenu, ensure_ascii=False).encode("utf-8")
        elif isinstance(contenu, str):
            contenu = contenu.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", type_mime + ("; charset=utf-8"
                         if type_mime.startswith("text") or "json" in type_mime else ""))
        self.send_header("Content-Length", str(len(contenu)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(contenu)

    def fichier(self, chemin, type_mime):
        if not os.path.exists(chemin):
            self.envoyer({"erreur": "absent"}, code=404)
            return
        with open(chemin, "rb") as f:
            self.envoyer(f.read(), type_mime)

    def corps_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

    # -------------------------------------------------- GET

    def do_GET(self):
        u = urlparse(self.path)
        chemin, q = u.path, parse_qs(u.query)

        if chemin in ("/", "/index"):
            return self.envoyer(PAGE, "text/html")

        if chemin == "/api/etat":
            voix = [v[0] for v in preparer.voix_francaises()]
            if REGLAGES["voix"] is None:
                REGLAGES["voix"] = preparer.choisir_voix(None)
            return self.envoyer({
                "vocabulaire": enrichir(preparer.lire_vocabulaire()),
                "voix": voix,
                "voixActive": REGLAGES["voix"],
                "vitesse": REGLAGES["vitesse"]})

        if chemin == "/api/recherche":
            terme = (q.get("q") or [""])[0]
            return self.envoyer(self.rechercher(terme))

        if chemin.startswith("/pictos/"):
            nom = os.path.basename(unquote(chemin))
            return self.fichier(os.path.join(preparer.DOSSIER_PICTOS, nom), "image/png")

        if chemin.startswith("/sons/"):
            nom = os.path.basename(unquote(chemin))
            return self.fichier(os.path.join(preparer.DOSSIER_SONS, nom), "audio/wav")

        self.envoyer({"erreur": "inconnu"}, code=404)

    def rechercher(self, terme):
        if not terme:
            return []
        import urllib.parse as up
        qq = up.quote(terme)
        for url in ["https://api.arasaac.org/v1/pictograms/fr/search/%s" % qq,
                    "https://api.arasaac.org/api/pictograms/fr/search/%s" % qq]:
            try:
                data = json.loads(preparer.http(url).decode("utf-8"))
            except Exception:
                continue
            if isinstance(data, list) and data:
                out = []
                for p in data[:24]:
                    pid = p.get("_id") or p.get("id")
                    if pid is None:
                        continue
                    out.append({"id": pid,
                                "image": "https://static.arasaac.org/pictograms/%s/%s_300.png"
                                         % (pid, pid)})
                return out
        return []

    # -------------------------------------------------- POST

    def do_POST(self):
        chemin = urlparse(self.path).path
        try:
            d = self.corps_json()
        except Exception as e:
            return self.envoyer({"erreur": str(e)}, code=400)

        if chemin == "/api/enregistrer":
            ecrire_vocabulaire(nettoyer(d))
            return self.envoyer({"ok": True})

        if chemin == "/api/son":
            REGLAGES["voix"] = d.get("voix") or REGLAGES["voix"]
            REGLAGES["vitesse"] = int(d.get("vitesse") or REGLAGES["vitesse"])
            dest = os.path.join(preparer.DOSSIER_SONS, d["id"] + ".wav")
            ok, err = preparer.fabriquer_son(d.get("dit") or d["id"],
                                             REGLAGES["voix"], REGLAGES["vitesse"], dest)
            preparer.publier()
            return self.envoyer({"ok": ok, "erreur": err})

        if chemin == "/api/ajouter":
            return self.envoyer(self.ajouter(d))

        if chemin == "/api/tousLesSons":
            return self.envoyer(self.tous_les_sons(d))

        self.envoyer({"erreur": "inconnu"}, code=404)

    def ajouter(self, d):
        REGLAGES["voix"] = d.get("voix") or REGLAGES["voix"]
        REGLAGES["vitesse"] = int(d.get("vitesse") or REGLAGES["vitesse"])

        voc = preparer.lire_vocabulaire()
        pris = ids_existants(voc)
        mid = id_libre(slug(d["mot"]), pris)

        os.makedirs(preparer.DOSSIER_PICTOS, exist_ok=True)
        os.makedirs(preparer.DOSSIER_SONS, exist_ok=True)

        preparer.telecharger_picto(d["pictoId"],
                                   os.path.join(preparer.DOSSIER_PICTOS, mid + ".png"))
        preparer.fabriquer_son(d.get("dit") or d["mot"], REGLAGES["voix"],
                               REGLAGES["vitesse"],
                               os.path.join(preparer.DOSSIER_SONS, mid + ".wav"))

        i = int(d.get("categorie") or 0)
        if not voc["categories"]:
            voc["categories"].append({"id": "c1", "nom": "Nouvelle categorie",
                                      "couleur": COULEURS[0], "mots": []})
            i = 0
        i = min(i, len(voc["categories"]) - 1)
        voc["categories"][i]["mots"].append({
            "id": mid, "mot": d["mot"], "dit": d.get("dit") or d["mot"],
            "picto": str(d["pictoId"])})
        ecrire_vocabulaire(voc)
        return {"ok": True, "vocabulaire": enrichir(voc)}

    def tous_les_sons(self, d):
        REGLAGES["voix"] = d.get("voix") or REGLAGES["voix"]
        REGLAGES["vitesse"] = int(d.get("vitesse") or REGLAGES["vitesse"])
        voc = preparer.lire_vocabulaire()
        faits = 0
        for m in preparer.tous_les_mots(voc):
            dest = os.path.join(preparer.DOSSIER_SONS, m["id"] + ".wav")
            ok, _ = preparer.fabriquer_son(m.get("dit") or m["mot"], REGLAGES["voix"],
                                           REGLAGES["vitesse"], dest)
            faits += 1 if ok else 0
        preparer.publier(voc)
        return {"ok": True, "faits": faits, "vocabulaire": enrichir(voc)}


def main():
    if not os.path.exists(os.path.join(ICI, "vocabulaire.js")):
        sys.exit("vocabulaire.js introuvable a cote de editeur.py")
    os.makedirs(preparer.DOSSIER_PICTOS, exist_ok=True)
    os.makedirs(preparer.DOSSIER_SONS, exist_ok=True)

    serveur = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = "http://127.0.0.1:%d/" % PORT
    print("Editeur ouvert sur %s" % url)
    print("Tout est enregistre automatiquement dans vocabulaire.js.")
    print("Pour arreter : Ctrl-C\n")
    threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        serveur.serve_forever()
    except KeyboardInterrupt:
        print("\nArrete.")


if __name__ == "__main__":
    main()
