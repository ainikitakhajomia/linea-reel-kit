# Vergelijking met het publieke aanbod

Deze vergelijking maakt onderscheid tussen een verkoopclaim, een zichtbaar voorbeeld, gevonden broncode, een draaiende integratie en een visueel gelijkwaardige implementatie. De huidige toolkit is een onafhankelijke lokale editor met een effectenproeftuin. **67 lokale Canvas recipes betekenen geen bewezen gelijkwaardigheid aan de 67 publieke Justyn-demonstraties.**

Bronnen: [publieke verkooppagina](https://justyn.ai/masterclass), [aanbodaudit](../research/offer-audit.md), [67 referenties](../research/public-effects-inventory.json), [repository- en licentieaudit](../research/repository-audit.md). De oorspronkelijke `justynberk/reel-kit` gaf 404; geen broncode uit dat product is overgenomen.

## Functionele vergelijking

| Onderdeel | Publiek aanbod Justyn | Hier gerealiseerd of voorbereid | Resterende grens |
|---|---|---|---|
| Lokale talking-head montage | Opname naar afgewerkte reel | FFprobe-ingest, FFmpeg-cuts, portrait framing, audio-normalisatie, JSON-job voor compositie | Geen benchmark op representatieve echte talking heads; renderer- en eindtests bepalen de uitvoerstatus |
| Stiltes weghalen | Dode tijd verwijderen | Akoestische stilteherkenning; woordintervallen beschermen tegen automatisch knippen | Detectie van stilte begrijpt geen betekenis; microfoonruis en zachte spraak beïnvloeden grenzen |
| Goede takes | Laatste goede versie van elke regel | Voorstellen voor exact herhaalde genormaliseerde zinnen; optioneel eerdere versies knippen; agent kan bron-EDL schrijven | Geen automatische beoordeling van delivery, overtuiging, fout uitgesproken woorden of tegenstrijdige formuleringen |
| J-cuts en lip-synccontrole | J-cut op joins; controle voor/na render | Bron/output-tijdlijn en caption-remap maken inspectie mogelijk | Geen automatische J-cutbouw of inhoudelijke lip-syncscore; metadata/duurcontrole is geen lip-syncvalidatie |
| Nederlands en Engels | Meertalige voorbeelden; geen Nederlandse benchmark aangetroffen | Lokale faster-whisper-backend met woordtijden en expliciete `nl`/`en` keuze; transcript-JSON import | Adapterbeschikbaarheid is geen bewezen taalnauwkeurigheid; noteer daadwerkelijk geteste modellen en opnames in validatie |
| Dynamische captions | Woordnauwkeurig in huisstijl | Actief woord, groepen, tijdgestuurde weergave en output-tijdremap | Vast basislayout; geen automatische line-breakoptimalisatie of gegarandeerde ASR-alignment |
| Tekst achter persoon | Bewegende matte op elk frame | Compositor kan een aangeleverde foregroundlaag boven effecten plaatsen | Een echte consistente alpha-video/segmentation-backend en tests nodig; synthetisch portret telt niet als automatische cutout |
| Motion graphics | 67 publieke effecten | 67 onafhankelijk geschreven, parameteriseerbare Canvas recipes en enkele aliases | Veel recipes zijn vereenvoudigde prototypes; zie visuele acceptatie |
| Automatische B-roll | Visuele voorbeelden met schermen, kaarten en video | Aangeleverde lokale B-roll in job; agent kan timing en selectie wijzigen | Geen automatische legale assetzoekmachine, semantische matching of geverifieerde stocklicenties |
| Softwarewalkthrough | Videokaart of achtergrond achter persoon | Lokale walkthrough als compositielaag; job beschrijft bron | Geen automatische cursor-/hoofdstukherkenning of inhoudelijke synchronisatie |
| Referentievideo analyseren | Tempo/stijl leren en effect nabouwen | Scenewisselheuristiek, encoding-keyframes, stilteanalyse en representatieve frames | Geen model dat zelfstandig typografie, masking, easing of audioverhaal begrijpt; agent moet frames en opname inspecteren |
| Storyboard en feedback | Beats met frames en opmerkingen | Job/EDL zijn leesbaar en door agents wijzigbaar; preview kan review ondersteunen | Geen bewezen volledige equivalent van annotatieboard met authoring-state, comments en automatische feedbackverwerking |
| Brand styles | Guide, designbestand, site of voorbeelden | Parameterobject/preset voor kleuren en expliciete vormgeving | Geen automatische merkextractie of fontlicentiecontrole; gecontroleerde preset nodig |
| Drie varianten | Creatieve alternatieven en trial-posts | Minimal/dynamic/playful jobs met verschillende beginbehandeling | Niet drie inhoudelijk herbedachte edits; geen Instagram-publicatie of trials/statistieken |
| Carousels | Vanaf reel of idee; eigen stijl | Architectuur kan stills en layouts aansturen; actuele exportstatus staat in README/validatie | Niet afleiden uit een slideshow dat een volledig carouselboard of PDF/PNG-export al bestaat |
| Geanimeerde slideshow | Niet als afzonderlijke productbelofte vastgesteld | Tijdgestuurde recipes zonder bronvideo bruikbaar voor motion scenes | Contentstructuur, beeldkeuze en storytelling blijven agentwerk |
| Humor/social | Expressieve effecten en snelle wissels | Burst, UI, physics-achtige en caption recipes beschikbaar | Humor, juiste sound cue en timing zijn inhoudelijke keuzes, geen automatische kwaliteitsscore |
| SaaS motion graphics | UI/effectdemonstraties | Originele inputbalken, kaarten, tijdlijnen en cursorvormen | Productgetrouwe UI, echte schermopnames en merkconsistentie moeten per opdracht worden beoordeeld |
| Audio | SFX op bewegingen en streaming loudness | FFmpeg-normalisatie van bestaande audio; bron-audio behouden | Geen complete voice/SFX/music-ducking-engine of stemisolatie afgeleid uit alleen normalisatie |
| AI Content OS | Bonus met contentstrategie | Geen equivalent van privélessen of getrainde cursusassistent | Agent kan onafhankelijk ideeën/kalender maken; geen gereproduceerd private kennisproduct |
| Course, Edits, community | Lessen, telefoonworkflow, assistent, seat | Bewust technologiegerichte repository | Geen toegang tot privélessen, community, privéprompts of support inbegrepen |
| Manychat/Trial posting | Aanvullende platformautomatisering | Geen betalende services of externe publicatie aangezet | Vereist afzonderlijke platform-/toegangscontrole en expliciete opdracht |

De vijf bovengenoemde beeldoperaties zijn inhoudelijk verbeterd na de eerste recipe-audit. Syntaxvalidatie is geslaagd; browser-/renderacceptatie moet op de geïsoleerde runner worden uitgevoerd en is daarmee nog geen bewezen visuele parity.

Deze tabel beschrijft de code en de controleerbare grenzen. Een daadwerkelijke render bewijst dat één fixture de pipeline doorloopt; pas na tests met echte NL/EN opnames is er bewijs voor kwaliteit op die gevallen.

## Gratis gevonden versus werkelijk hergebruikt

- **AskEditor**: MIT Timeline geselecteerd en met bronvermelding opgenomen. De complete repository bevat nuttige segmentation, captions en behind-person workflows. Dat de bron bestaat, betekent niet dat de volledige zware stack hier is geïnstalleerd of uitgevoerd.
- **motion-video-styles**: MIT timinghulpmiddelen afzonderlijk geadapteerd en gevalideerd, met pinned herkomst. De oorspronkelijke runner is niet blind overgenomen. De Canvas-runtime importeert de timinghulpmiddelen; de editpipeline gebruikt de Timeline. Zelfstandige modulechecks en de geïntegreerde uitvoertests blijven afzonderlijke bewijsstukken.
- **FFmpeg / FFprobe**: de daadwerkelijke media-ingest, stilteanalyse, cuts, schaling, audioverwerking en referentiemetingen gebruiken bestaande tools.
- **faster-whisper**: optionele lokale ASR-adapter. Eerste modeldownload vereist internet en beschikbare schijfruimte; inferentie kan daarna lokaal. Geen betaalde transcriptie-API.
- **Playwright / Chromium / Canvas**: open tooling voor review en compositie. Browserinstallatie is een aparte dependency-download. FFmpeg verzorgt encoding; geen nieuwe codec ontwikkeld.
- **Ghost Editor, heditor, Robin Reel Kit**: echte MIT-kandidaten onderzocht. Niet presenteren als geïnstalleerde of bewezen werkende onderdelen als ze alleen zijn geïnspecteerd.
- **prathameshp107/video-editing**: geen passende LICENSE aangetroffen, daarom geen code gekopieerd.
- **Remotion**: concrete bestaande technologie, maar eigen licentievoorwaarden; geen nieuwe commerciële rechten of betaling verondersteld. De primaire pipeline heeft geen Remotion-runtime nodig.

Exacte upstream commits, notices, testgrenzen en aanvullende MCP/skill-kandidaten staan in de [repositoryaudit](../research/repository-audit.md). Een beschikbare MCP-server wordt niet als geïntegreerd aangemerkt zonder installatie en een geslaagde concrete toolcall.

## Wat onafhankelijk gebouwd is

De uniforme CLI/job-aanpak, reviewomgeving, agentinstructies en Canvas recipes zijn bedoeld om één werkstroom te vormen. De recipes gebruiken zelfgetekende vormen en tekst; geen beschermde reference-assets. Een bestaande licentie op vergelijkbare algemene technieken is niet nodig om onafhankelijk een inputbalk, tekstanimatie of kaartovergang te bouwen.

De nieuwe recipes dekken namen uit de publieke inventaris, maar meerdere implementaties wijken wezenlijk af van hun referentie:

| Recipe | Huidige vereenvoudiging | Vereiste voor functionele/visuele equivalentie |
|---|---|---|
| `icon-strike` | Drie zelfgetekende iconen met strike en staggered exits | Strike-/exitmomenten koppelen aan werkelijke woordtijden; multi-opname visuele acceptatie |
| `orbit-ring` | Draaiende glyphs in twee depthpasses; demoportret zonder bron | Echte foreground-alpha aanleveren en testen; headtracking ontbreekt; geen volwaardige 3D typografiescene |
| `knockout-captions` | Echte tekstuitsparing op offscreen plate met `destination-out` | Leesbaarheid/woordtiming op werkelijk bewegende footage beoordelen; camera dive niet inbegrepen |
| `paper-tear` | Twee rafelige papieren panelen met peel/shadow; optionele vorige image | Shottransition vraagt afzonderlijke vorige bronlaag; geen fysische paper curl of displacement shader |
| `finger-draw` | Vooraf getekend pad | Pad afkomstig van werkelijke fingertiptracking of expliciete motion-keyframes |
| `rack-focus` | Achtergrondblur met scherp foreground indien aangeleverd; anders synthetische demo | Geen automatisch subject-mask; eigen matte en rand-/bewegingsacceptatie nodig |
| `blow-away` | Tekstletters waaien uiteen | Pixels/deeltjes uit subject-matte, coherente verplaatsing en schone achtergrond |
| `double-exposure` | Overlappende synthetische portretten | Tweede video gemaskeerd in echte subject-silhouette |
| `dolly-zoom` | Globale punch-in bij video | Onafhankelijke foreground/backgroundtransformatie met stabiele subjectgrootte |
| `code-body` | Getypte codekaart | Glyphveld binnen bewegend subject-mask met gecontroleerde scanovergang |

De actuele bron kan verbeteren na deze audit; zet een rij pas op “geaccepteerd” nadat de rubric op de uiteindelijke render is toegepast. Zie [visual-acceptance.md](visual-acceptance.md).

## Waar deze aanpak controleerbaar sterk is

Dit zijn eigenschappen van onze repository, geen onbewezen superioriteitsclaims over Justyns private product:

1. **Inspecteerbare herkomst**: bron-URL, commit en notices voor opgenomen derdepartijcode; publieke referenties blijven afzonderlijk van lokale implementaties.
2. **Reviewbare beslissingen**: cuts en source→output-tijden staan als JSON in plaats van alleen in een afgewerkte MP4; bronnen worden behouden.
3. **Providerkeuze**: de kern heeft geen betaalde API nodig; captions kunnen worden geïmporteerd en modellen zijn optioneel lokaal.
4. **Reproduceerbare techniek**: projectbestanden en tijdgestuurde compositie zijn versieerbaar. Identieke outputs vereisen ook dezelfde browser, fonts, modellen en encoderinstellingen; geen onterechte bit-identieke garantie.
5. **Eerlijke uitvoerstatus**: functionele tests, media-probes en menselijke visuele beoordeling hebben verschillende rollen. Een geslaagde syntaxcheck wordt niet als een geslaagde edit gepresenteerd.

Voor “beter dan Justyn” op cutkwaliteit, teksttracking, visuele afwerking, snelheid of stabiliteit bestaat nog geen gecontroleerde A/B-meting met hetzelfde bronmateriaal. Die conclusie wordt daarom niet getrokken.
