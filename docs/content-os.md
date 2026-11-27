# Lokale contentwerkplek

`scripts/content.py` is een lichte lokale tracker voor ideeën, scripts, reels, carousels, slideshows en LinkedIn-content. Hij doet geen API-calls, genereert geen platformanalytics en publiceert niets. Dit is een uitbreidbare basis voor een eigen Content OS, geen equivalent van Justyns gehoste product of cursus.

```sh
python3 scripts/content.py init
python3 scripts/content.py add --title 'Ons productverhaal' --kind idea
python3 scripts/content.py derive --title 'Nieuwe workflow' --script examples/script-nl.txt
python3 scripts/content.py list --kind reel
python3 scripts/content.py status RECORD_ID ready
```

`derive` maakt drie gekoppelde records: het bronidee met script, een reeldraft en een carouseldraft. De inhoud blijft het originele script; creatieve herschrijving is een taak voor Claude Code/Codex. Elk resultaat is JSON, zodat de agent de ids en scripts direct kan gebruiken. Geef `--workspace /pad/naar/content` vóór of na het subcommando op voor een andere werkplek; standaard `out/content`.

Dezelfde agent kan het reel-script gebruiken met de editingpipeline en de carousel met `scripts/story.py carousel`. Renderuitvoer en publicatiedatum worden nog niet automatisch in records bijgewerkt. Zet de status met het expliciete commando nadat de uitvoer is beoordeeld.

Statussen: `idea → draft → ready → rendered → published → archived`. Vanuit `ready` mag direct gepubliceerd worden (bijvoorbeeld tekstcontent). `ready`/`rendered` kunnen terug naar `draft`; gepubliceerde content moet eerst gearchiveerd worden voordat een nieuwe draft start. Elke wijziging schrijft een **nieuwe** revisionfile; eerdere JSON-records blijven behouden. `init` is idempotent voor een compatibele werkplek en weigert bestaande onbekende manifests. Een exclusieve `.write-lock` voorkomt gelijktijdige wijzigingen. Na een procescrash: controleer dat geen contentproces meer draait voordat je de achtergebleven lock handmatig verwijdert.

Opslag: `workspace.json` bevat schemaVersion 1; `records/<id>/000001.json` bevat id, revision, kind, title, status, script, parentId, createdAt en updatedAt. Houd de workspace privé wanneer scripts klantinformatie bevatten. De bestaande `.gitignore` sluit `out/` uit.

Voorbeeldinstructie: “Neem dit script op in onze contentwerkplek, maak een reel- en carouseldraft, render beide in Studio Linea-stijl en zet alleen de beoordeelde outputs op ready.”

Testen: `python3 -m unittest discover -s tests -p test_content.py`. De tests controleren gekoppelde derivaten, geldige statustransities, onveranderde eerdere revisies, incompatibele gebruikersdata, corrupte state en gelijktijdige schrijvers.
