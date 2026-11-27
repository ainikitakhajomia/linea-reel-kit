# Creative Review Studio

De reviewstudio verzamelt het bestaande werk. Er worden voor deze review geen nieuwe effecten of films gegenereerd.

- Openbare omgeving: https://ainikitakhajomia.github.io/linea-reel-kit/
- Eigen lokale checkout: `PORT=65153 node src/server.mjs`.
- Inventaris: `public/review-manifest.json`.
- Blijvende bestanden: `public/review-media/`, met inhoudshash in iedere bestandsnaam.
- Vergelijking: publieke Justyn MP4s worden rechtstreeks van hun oorspronkelijke URL geladen. Geen referentiebeelden gekopieerd of opnieuw gepubliceerd.
- Iedere effectkaart gebruikt een bestaand MP4-bestand; parameters worden afzonderlijk met de bestaande canvasrenderer bekeken.
- Films tonen de teruggevonden bron, versies en bestaande effecttijdlijn. Deze tijdlijn vormt het getoonde storyboard; er is geen oorspronkelijke, uitgebreidere storyboarddocumentatie verzonnen.
- Er is geen echte talking-headopname beschikbaar. De presentator, spraak en conceptinterfaces zijn synthetisch; lipsync en premiumkwaliteit zijn niet geaccepteerd. Dieptedemo: 2.5D.
- Reviewopslag: localStorage op het huidige apparaat en de huidige oorsprong. Export/import draagt favorieten, feedback en besluiten over. Er is geen gedeelde backend en geen automatische communicatie met derden.
- De eerste 540p-filmversie was eerder visueel afgekeurd en wordt juist ter vergelijking behouden.
- Geen achtergrondmuziek toegevoegd. De oorspronkelijke soundtrack van ieder bestaand bestand blijft intact; sommige exports zijn stil.

Browseracceptatie: `node src/validate-studio.mjs [url]`, uitsluitend op de geïsoleerde Linux-runner. Controleert daadwerkelijke videodecodering en voortgang van 67 effectpreviews, referenties en alle opgenomen filmexports/bronnen; fullscreen, parameters, navigatie, reviewpersistentie, mobiel, console en mislukte requests. Audio wordt op een bestaand spraakbestand gedecodeerd en op niet-stil signaal gecontroleerd. Dit bewijst geen menselijke luisteracceptatie of creatieve kwaliteit.

Publicatie: `node scripts/build-static.mjs out/site /linea-reel-kit`; de build kopieert uitsluitend de expliciet opgenomen broncode en gehashte reviewmedia. De bestaande gh-pages-omgeving wordt gebruikt, zonder main te mergen of Studio Linea-productie te wijzigen.
