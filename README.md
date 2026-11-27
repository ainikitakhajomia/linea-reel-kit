# Linea Reel Kit

Eén lokale toolkit voor agentgestuurde video-editing, motion graphics en carousels. Werkt vanuit Claude Code en Codex, zonder betaalde API's. Studio Linea is de eerste brand preset; bronvideo's en huisstijlen blijven onder je eigen controle.

**Status: werkende v0.1, geen volledige vervanging met bewezen visuele gelijkwaardigheid.** De bibliotheek bevat 67 onafhankelijke bewegende basisrecepten, op naam gekoppeld aan alle 67 publieke referenties. De recepten variëren in volwassenheid. Dat is iets anders dan Justyns product, assets of kwaliteitsniveau kopiëren. Zie [vergelijking](docs/comparison.md) en [visuele acceptatie](docs/visual-acceptance.md).

## Installeren

Node 22+, Python 3.10+ en FFmpeg (`ffmpeg` + `ffprobe`) zijn nodig. Linux/macOS; Windows via WSL2. Python 3.11 is aanbevolen voor optionele ML-pakketten.

```sh
git clone https://github.com/ainikitakhajomia/linea-reel-kit.git
cd linea-reel-kit
npm ci
python3 scripts/reel.py doctor
npm run review
```

Open http://127.0.0.1:4173. Alle effecten bewegen direct in de reviewomgeving; klik voor parameters, herkomst, licentie, referentielink en agentinstructie. Geen browserdownload nodig voor deze reviewserver.

Installeer de exportbrowser in een omgeving waar browserrendering is toegestaan:

```sh
npx playwright install chromium
# Linux met ontbrekende libraries: npx playwright install --with-deps chromium
```

In Studio Linea draaien browserrenders volgens AGENTS.md op de geïsoleerde runner, niet op de Mac. De meegeleverde [GitHub Actions-workflow](.github/workflows/validate.yml) voert exports en browseracceptatie uit op Ubuntu. Hij gebruikt alleen synthetische media. Draai deze workflow niet met vertrouwelijke klantvideo's in een publieke repo.

## Eerste echte edit

```sh
# Zelfgemaakte synthetische spraak + beeld + getimede voorbeeldtekst
python3 scripts/reel.py demo --out public/demo
python3 scripts/reel.py edit public/demo/source.mp4 \
  --transcript public/demo/transcript.json --out public/jobs/demo
npm run render -- public/jobs/demo/job.json out/demo.mp4
```

Dit maakt een H.264/AAC-video met aangepaste knippen, woordcaptions en motion graphics. `edited.mp4` is het schone knipresultaat; `out/demo.mp4` is de uiteindelijke compositie. Het brondocument met EDL, woordtijden en bronhash blijft beschikbaar. Voor jouw eigen video vervang je het inputpad.

Voor lokale Nederlandse/Engelse spraakherkenning:

```sh
python3.11 -m venv .venv-asr
.venv-asr/bin/pip install -r requirements-transcription.txt
.venv-asr/bin/python scripts/reel.py transcribe mijn-video.mp4 \
  --language nl --model small --out out/transcript.json
python3 scripts/reel.py edit mijn-video.mp4 \
  --transcript out/transcript.json --out public/jobs/mijn-edit
npm run render -- public/jobs/mijn-edit/job.json out/mijn-edit.mp4
```

Het eerste gebruik downloadt gratis modelgewichten. Daarna werkt inference lokaal. Tiny is werkelijk getest voor NL en EN; NL bevat herkenningsfouten. Kies small/medium voor praktisch werk en controleer namen, bedragen en vaktaal.

## Claude Code en Codex

```sh
python3 scripts/install-skills.py --codex --claude
```

De installer koppelt de skill aan deze checkout en overschrijft geen bestaande skill zonder `--force`. Na verplaatsen opnieuw installeren. De agent orkestreert de lokale scripts; er draait geen betaalde autonome API op de achtergrond.

Voorbeelden:

- “Edit deze talking head met premium motion graphics, Nederlands, Studio Linea.”
- “Analyseer deze referentievideo en stel dezelfde editingprincipes voor.”
- “Plaats grote geanimeerde tekst achter mij; maak eerst een foreground matte.”
- “Verwijder slechte takes. Laat zien welke takes je kiest en render daarna.”
- “Combineer mijn talking head met deze softwarewalkthrough.”
- “Maak drie creatieve varianten en render ze naast elkaar.”
- “Maak van dit script een geanimeerde slideshow én LinkedIn-carousel.”

De agent gebruikt visuele inspectie en taalbegrip om een storyboard/EDL te verfijnen. De CLI zelf claimt geen semantische kwaliteitsbeoordeling: automatische stilteknippen, herhaalde tekst en referentiestatistieken zijn heuristieken. Lees [pipeline](docs/pipeline.md).

## Slideshows, carousels en contentplanning

```sh
python3 scripts/story.py storyboard examples/script-nl.txt --out public/jobs/slideshow
npm run render -- public/jobs/slideshow/job.json out/slideshow.mp4
python3 scripts/story.py feedback public/jobs/slideshow/job.json --out out/feedback
python3 scripts/story.py carousel examples/script-nl.txt --out public/carousels/demo
node src/render-carousel.mjs public/carousels/demo out/carousel
```

Slideshowtiming is een scriptgebaseerde schatting, zonder automatisch gegenereerde voice-over. Carousels leveren eigen SVG's en 1080×1440 PNG's; geen fotobank of private templates. Zie [Content OS-basis](docs/content-os.md) voor de lokale planner.

## Tekst achter de spreker

[Segmentation](docs/segmentation.md) levert lokale foreground-PNG's via chromakey of optionele MediaPipe portrait segmentation. Zet `job.foregroundFrames` op de sequentie uit metadata; de compositor tekent de spreker tussen effecten en captions. Chromakey is op alpha-pixels getest; portrait ML vraagt afzonderlijke visuele acceptatie op je eigen video. Geen perfecte haren/handen/occlusies beloofd.

## Huisstijlen en formaten

Kopieer `brands/studio-linea.json` en geef `--brand brands/jouw-merk.json` mee aan `edit` of `storyboard`. Geobserveerde Linea-kleuren komen van https://studio.use-linea.com/: warm wit, navy en inktzwart. Geen logo's, fonts of foto's overgenomen. De canvasrenderer gebruikt voorlopig Arial/system fallback; `preferredFont` is metadata.

Defaultvideo: 720×1280, 30fps. Pas `width`/`height` in job.json aan voor 1080×1920 Reels, vierkante LinkedIn-video of 16:9. De huidige recipes gebruiken een genormaliseerde 9:16-layout en schalen mee; per-formaat artdirection en safe areas vereisen review. Carousels: 3:4. Softwarewalkthroughs gebruiken aangeleverde screenrecordings; geen browserautomatisering met klantaccounts.

## Architectuur en hergebruik

- FFmpeg: nauwkeurige cuts, concat, audionormalisatie en H.264/AAC-export.
- Faster-whisper: optionele lokale NL/EN-transcriptie.
- AskEditor: MIT Timeline-engine, daadwerkelijk gebruikt voor timing.
- Motion-video-styles: MIT easing, typewriter en counters in de renderer.
- Playwright/Chromium: deterministische framecapture, dezelfde Canvas-code als de review.
- MediaPipe: optionele CPU-persoonssegmentatie; chromakey werkt zonder ML.
- [Remotion-adapter](docs/remotion.md): optioneel, niet standaard geïnstalleerd of getest; eigen licentievoorwaarden.

Geen zeven losse apps: één checkout, één skill en een gedeeld job.json-contract. De natuurlijke-taalagent kiest de benodigde commando's. Voor alle herkomst en beperkingen: [repository-audit](research/repository-audit.md), [aanbodaudit](research/offer-audit.md) en `vendor/*/provenance.json`.

## Testen en renderbewijs

```sh
npm test
# Browserchecks op geïsoleerde Linux-runner:
node src/validate-browser.mjs
node src/render-library.mjs public/renders
```

De workflow publiceert MP4's, screenshots, alle 67 previews en een renderlog als Actions-artifact. Een groen pixel-/bewegingstestresultaat bewijst werking en determinisme, geen esthetische gelijkwaardigheid. Bronvideo's en eigen lokale exports staan in .gitignore. Licentie eigen code: MIT. Referentiemedia worden uitsluitend gelinkt, niet meegeleverd.
