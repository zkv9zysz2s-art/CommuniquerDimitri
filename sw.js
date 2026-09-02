/* Genere automatiquement. Ne pas modifier a la main. */
var VERSION = "20260902-204152";
var CACHE = "communiquer-" + VERSION;
var FICHIERS = ["./", "index.html", "vocabulaire.js", "version.js", "manifest.json", "icone-180.png", "icone-192.png", "icone-512.png", "pictos/aesh.png", "pictos/aide.png", "pictos/attends.png", "pictos/aurevoir.png", "pictos/boire.png", "pictos/bonjour.png", "pictos/bruit.png", "pictos/calme.png", "pictos/cantine.png", "pictos/chaud.png", "pictos/classe.png", "pictos/colere.png", "pictos/content.png", "pictos/copain.png", "pictos/dessiner.png", "pictos/dormir.png", "pictos/doudou.png", "pictos/encore.png", "pictos/faim.png", "pictos/fatigue.png", "pictos/fini.png", "pictos/froid.png", "pictos/jouer.png", "pictos/lapin.png", "pictos/livre.png", "pictos/maison.png", "pictos/maitre.png", "pictos/mal.png", "pictos/maman.png", "pictos/manger.png", "pictos/merci.png", "pictos/mouchoir.png", "pictos/musique.png", "pictos/non.png", "pictos/ordinateur.png", "pictos/oui.png", "pictos/papa.png", "pictos/pause.png", "pictos/peur.png", "pictos/ranger.png", "pictos/recreation.png", "pictos/saispas.png", "pictos/soif.png", "pictos/sortir.png", "pictos/sport.png", "pictos/stop.png", "pictos/stp.png", "pictos/toilettes.png", "pictos/travailler.png", "pictos/triste.png", "sons/aesh.wav", "sons/aide.wav", "sons/attends.wav", "sons/aurevoir.wav", "sons/boire.wav", "sons/bonjour.wav", "sons/bruit.wav", "sons/calme.wav", "sons/cantine.wav", "sons/chaud.wav", "sons/classe.wav", "sons/colere.wav", "sons/content.wav", "sons/copain.wav", "sons/dessiner.wav", "sons/dormir.wav", "sons/doudou.wav", "sons/encore.wav", "sons/faim.wav", "sons/fatigue.wav", "sons/fini.wav", "sons/froid.wav", "sons/jouer.wav", "sons/lapin.wav", "sons/livre.wav", "sons/maison.wav", "sons/maitre.wav", "sons/mal.wav", "sons/maman.wav", "sons/manger.wav", "sons/merci.wav", "sons/mouchoir.wav", "sons/musique.wav", "sons/non.wav", "sons/ordinateur.wav", "sons/oui.wav", "sons/papa.wav", "sons/pause.wav", "sons/peur.wav", "sons/ranger.wav", "sons/recreation.wav", "sons/saispas.wav", "sons/soif.wav", "sons/sortir.wav", "sons/sport.wav", "sons/stop.wav", "sons/stp.wav", "sons/toilettes.wav", "sons/travailler.wav", "sons/triste.wav"];

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
        var m = /bytes=(\d*)-(\d*)/.exec(entete) || [];
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
