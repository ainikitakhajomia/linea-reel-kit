# Tekst achter een echte spreker

Gebruik de **gemonteerde** `edited.mp4` als bron. Daardoor lopen de transparante voorgrond en de hoofdvideo gelijk, ook na takes verwijderen. De compositor tekent hoofdvideo → tekst → voorgrond-PNG. Een PNG bevat echte alpha; dit is geen nagebouwde persoon of vlakke vorm.

Voor een green-screenopname, zonder Python-packages:

```sh
python3 scripts/segment.py public/jobs/demo/edited.mp4 --out public/jobs/demo/foreground --mode chromakey --color 0x00ff00 --fps 30
```

Neem uit de geprinte metadata het veld `foregroundFrames` over in het job-JSON:

```json
{"foregroundFrames":"jobs/demo/foreground/%06d.png"}
```

De nummering start op `000000.png`. Job-fps en segmentation-fps moeten gelijk zijn. Gebruik dezelfde inputuitsnede; crop en positionering moeten overeenkomen met de hoofdvideo. Voorgrondframes gebruiken extra opslag: test eerst een kort fragment. Bestaande niet-lege uitvoermappen worden geweigerd om oude frames na een kortere nieuwe edit te voorkomen. Bronbestanden worden niet gewijzigd.

Voor een normale talking head bestaat een optionele lokale CPU-adapter:

```sh
python3.12 -m venv .venv-segmentation
.venv-segmentation/bin/pip install -r requirements-segmentation.txt
.venv-segmentation/bin/python scripts/segment.py public/jobs/demo/edited.mp4 --out public/jobs/demo/foreground --mode portrait --fps 30
```

MediaPipe 0.10.21 bevat het legacy selfie-segmentationmodel. De adapter downloadt of uploadt geen video of model tijdens verwerking. Code/licentie: [MediaPipe Apache-2.0](https://github.com/google-ai-edge/mediapipe/blob/v0.10.21/LICENSE); het package en transitive dependencies behouden hun eigen notices. Geen betaalde API. Deze optionele adapter is geïmplementeerd maar niet lokaal met de zware ML-stack getest; de chromakey-route is met echte FFmpeg alpha-pixels getest. Gebruik Python 3.10–3.12; dit package ondersteunt de huidige Python 3.14-installatie niet.

Parameters: `--similarity 0.15 --blend 0.05` voor chromakey; `--threshold 0.5 --feather 0.1` voor portrait. Een hogere threshold snijdt strakker, feather geeft een zachtere confidence-rand. Haar, bewegingsonscherpte en vergelijkbare achtergrondkleuren blijven aandachtspunten: bekijk frames en speel een proefrender af. MediaPipe is een persoonmasker, geen objectsegmentatie of trackinggarantie.

Verificatie: `python3 -m unittest discover -s tests -p test_segment.py`. De test genereert een groene achtergrond met rood onderwerp, extraheert RGBA-frames, controleert transparante achtergrond en ondoorzichtige voorgrond en bevestigt dat het bronbestand identiek blijft.
