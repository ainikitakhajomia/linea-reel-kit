# Linea Reel Kit — voortzetting 27 november 2026

## Project en behoud

Bestaand project, geen herstart. Oorspronkelijke repo: `/Users/nikitakhajomia/linea-dev/worktrees/moeder/task-20261127-173344-4f2dc9d203/linea-reel-kit`. Bij overname schoon, laatste commit `a586292`; geen ongecommitte werk daar. Volledige onafhankelijke gitkopie in `/Users/nikitakhajomia/linea-dev/worktrees/mattia/task-20261127-175400-eededbe663/linea-reel-kit`. Geen Studio Linea-productiewijzigingen. Circa 14 GiB beschikbaar bij start.

GitHub: https://github.com/ainikitakhajomia/linea-reel-kit
Werkbranch: `recovery/verified-review`.

## Hersteld en toegevoegd

- Lege preview: HTML aan root vroeg `/review.mjs` op in plaats van `/src/review.mjs`; catalogusfix uit vorige sessie alleen was onvoldoende. Absolute module-URL hersteld.
- Eerste Linux-run `46046012218`: browseracceptatie van 67 geanimeerde/deterministische recepten en UI geslaagd. Eerste volledige run `46046012093` kon alle 67 MP4s renderen; oorspronkelijke runs `46045013148`, `46045359598` faalden op ontbrekende kaarten.
- Reviewinterface opnieuw ingericht: responsive Studio Linea-werkbank, alle categorieën, zoeken, sorteren, lokaal bewaarde favorieten, tijdlijn/scrub/pauze, tekst/kleur/duur, JSON-parameters, downloadbare jobs en identieke preview/exportbeeldcode. Nieuwe uitgebreidere acceptatie moet op exacte commit groen zijn.
- Beeldfouten hersteld: secondary exposure, contrast/regels captions, woordaccenten, camera settle/punch, aparte dolly-background/subject, letter-alpha-dive, vier bronmedia-wipes; previous/next/background worden daadwerkelijk geladen en gevalideerd.
- Intelligente NL/EN briefplanner `scripts/agent-plan.py` en drie skillkopieën bijgewerkt; planner is een beslisdocument, geen onbewezen autonome segmentatie of hoogwaardige generator.
- Tien verschillende synthetische voorbeeldjobs en volledige MP4-exports via `scripts/demos.py --asr` + `node src/render-demos.mjs`. Duidelijke provenance. Echte lokale Whisper-woordtijden op synthetische NL/EN-spraak. Export op Linux, geen zware renders op Mac.
- Vercel: geen bevestigde deployment gevonden; zie `docs/deployment-status.md`. Geen project/dienst aangemaakt.

## Lopend / eerst volgende stap

1. Volgende commit pushen en beide Actions volgen. Bij failure: `gh run view <id> --repo ainikitakhajomia/linea-reel-kit --log-failed`.
2. `visual-preview-evidence` downloaden en screenshots zelf bekijken, inclusief alle-effecten-contactsheet en media-composition. `linea-reel-kit-rendered` bevat uiteindelijke exports/probes/QA en tien demo-contact sheets. Alleen groene checks + visuele inspectie leveren bewijs.
3. Tien exports en alle 67 exportframes visueel beoordelen; steminhoud/echte lipsync wordt niet bewezen door FFprobe. Eventuele ASR- of renderfouten oplossen.
4. Preview openbaar beschikbaar maken via geschikte gratis statische hosting als dat kan zonder betaalde service. Lokaal werkt `npm run review` op http://127.0.0.1:4173. De previewserver loopt in root toolsession zolang die behouden blijft; anders opnieuw starten.
5. Globale Codex/Claude skillpaden opnieuw binden aan deze behouden repo met installer na definitieve wijzigingen.

## Exact hervatten

```sh
cd /Users/nikitakhajomia/linea-dev/worktrees/mattia/task-20261127-175400-eededbe663/linea-reel-kit
git status --short
gh run list --repo ainikitakhajomia/linea-reel-kit --limit 8
npm ci
npm run review
# Alleen geïsoleerde Linux-runner: browser/render scripts.
```

Push gebruikt de actuele gh-auth; standaard macOS gitcredential heeft verouderde token zonder workflowscope. Geen tokens printen:

```sh
git -c credential.helper= -c 'credential.helper=!gh auth git-credential' push origin recovery/verified-review
```

## Eerlijke grenzen

67 recepten zijn geen 67 premium geaccepteerde reproducties. Zie `docs/effect-status.md` voor basisanimatie / beeldoperatie / stand-in. Geen representatieve eigen talking-headopnamen beschikbaar: illustratieve spreker, synthetische stem en concept-UI bewijzen geen portretkwaliteit. Tracken, echte fysieke 3D, subject-particles, semantic takes en hoogwaardige referentiematching blijven deels/open. Demo 9 is 2.5D; noem die geen echte 3D-engine. Alleen publiek toegankelijke referenties gelinkt; geen beschermde clips opnieuw gepubliceerd. Geen betaalde APIs, klantmedia of credentials toevoegen.

## Controlepunt na eerste volledige groene herstelrun

De volledige workflow `46046650541` op `d8cad22` is groen: alle 67 exports, compositing, tien complete 540×960 synthetische films met echte NL/EN-ASR, audio/media-QA en portrait-inference. Artifact `linea-reel-kit-rendered`, ca. 79 MB. Dit is technisch bewijs, geen menselijke portret- of premiumacceptatie.

De openbare statische preview is aangemaakt op GitHub Pages: https://ainikitakhajomia.github.io/linea-reel-kit/ . De Pages-build `46046889400` is groen. Hosting bevat uitsluitend allowlist-code; demo's worden na validatie toegevoegd. Vercel blijft onbevestigd. `scripts/build-static.mjs out/site /linea-reel-kit` is het publicatiepad. `src/validate-hosted.mjs` controleert daadwerkelijk scrollen/afspelen van alle 67 kaarten op Linux. Volgende commit voegt dit toe aan previewworkflow.

Globale skills opnieuw geïnstalleerd met `python3 scripts/install-skills.py --repo "$PWD" --codex --claude --force`; Codex-home is `/Users/nikitakhajomia/.codex-mattia`, Claude-home `/Users/nikitakhajomia/.claude`.

Nieuwe lokale, nog te pushen iteratie: 67 eerlijke cataloguslabels en inputvoorwaarden, uitwerkingsfilter, standaard double-exposurecontrast en letter-dive-eindbeeld, vier exportcontactbladen met FFprobe/framecounts/SHA per MP4, posters en native1080×1920 @24fps demo's. De eerste gedownloade interface/compositie/all67-screenshots zijn door root visueel bekeken; volledige nieuwe exportcontactbladen nog niet.

## Visuele en transcriptie-afkeur van eerste filmversie

Root heeft alle tien eerste filmcontactbladen (uit echte MP4s) bekeken. Versie d8cad22 is technisch groen maar visueel onvoldoende: overlays over ogen, dubbele walkthroughpanelen, vaste typographykop achter nieuwe tekst, dubbele portretlaag bij transitions. Niet als premium geaccepteerd of als definitieve films publiceren.

Eigen QA op de daadwerkelijk opgeslagen tiny-transcripts: Nederlandse micro-WER **61,4%** op acht synthetische scripts, alle acht `usable:false`; Engelse micro-WER **15,6%** op twee scripts. Geen ongeldige woordtijden. Rapport lokaal `out/first-evidence/out/transcription-qa.json`. Dit zijn synthetische spraaktests, geen uitspraak over natuurlijke sprekers. Eerst groter lokaal Whisper-model `small`, opnieuw meten; niet het script als initial_prompt gebruiken om het resultaat te verfraaien.

Lopende correctie: native1080-bronbeelden, schone graphicbackdrops, losse clean plate + foregroundalpha, presenter-PIP buiten walkthrough, overlayplaatsing via offsetX/offsetY/scale, echte verschillende slideshowafbeeldingen en speech-cues op gemeten ASR-woorden. Afsluiten met nieuwe daadwerkelijke exports en beeldinspectie.

De publieke preview is nu daadwerkelijk op Linux gecontroleerd: run `46047955418` speelde **alle 67 kaarten** af, nul consolefouten of mislukte assetrequests. Films waren op dat moment nog niet gepubliceerd (`demosPlayed:0`). Eén eerdere hostedtest faalde door URL-object i.p.v. string in de QA zelf; gerepareerd in `0a1ee10`.

## Creative Review Studio — visuele review heeft voorrang

Geen nieuwe effecten of engine ontwikkeld. Eigen behouden checkout onder Dave bevat de reviewstudio met echte MP4 previews, referenties rechtstreeks vanaf de publieke bron, feedback/favorieten/goedkeuring met localStorage en JSON export/import, versie- en bronvergelijking, bestaande effecttijdlijn als storyboard en dertien stijlencategorieën. Synthetische presentator en 2.5D blijven expliciet benoemd. Categorieën zonder film worden als ontbrekend aangeduid.

`public/review-manifest.json` is de mediainventaris; `public/review-media/` bevat uitsluitend bestaande synthetische outputs met SHA256-bestandsnamen. Media staan blijvend in Git, niet alleen in tijdelijke Actions-artifacts. `scripts/assemble-review.py` verzamelt bestaande downloads en behouden lokale resultaten zonder te renderen. `src/validate-studio.mjs` draait op de geïsoleerde GitHub Linux-runner. Bestaande zware renderworkflow wordt voor commits met `[review-only]` overgeslagen; de aparte browseracceptatie blijft draaien.
