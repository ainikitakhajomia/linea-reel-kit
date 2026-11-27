# Status van alle 67 lokale recipes

Deze broninspectie beschrijft wat `src/effects.mjs` werkelijk tekent. Het is geen visuele acceptatie en geen product-parityclaim. Alle 67 publieke referenties zijn geïnventariseerd en bekeken; niet elke lokale recipe realiseert de gelijknamige functie volledig. De classificatie beschrijft inhoudelijke volwassenheid en is geen automatisch testresultaat.

- **Beeldoperatie**: de kenmerkende compositing-/bewegingsoperatie is aanwezig, met de genoemde input- en kwaliteitsgrenzen. Browseracceptatie en toepassing op echte footage blijven afzonderlijk nodig.
- **Basisanimatie**: zelfstandig geanimeerde interpretatie van het algemene idee, met meerdere ontbrekende reference-specifieke onderdelen.
- **Stand-in**: zichtbaar bewegende demonstrator, maar de kernfunctie van de gelijknamige referentie is wezenlijk eenvoudiger of ontbreekt.

Counts bij deze inspectie: 39 basisanimatie, 18 beeldoperatie, 10 stand-in. Geen enkele classificatie betekent automatisch “premium” of “visueel gelijkwaardig”. Voor groen-/normale achtergrondsegmentatie gelden apart [segmentation.md](segmentation.md); voor daadwerkelijke test- en renderstatus gelden README en het uiteindelijke Actions-runresultaat.

| # | ID | Classificatie | Concrete afwijking / vereiste |
|---|---|---|---|
| 1 | `kinetic-hook` | Basisanimatie | Getimede woordopbouw, optioneel via woordtijden of `syncWords`; geen reference-specifieke fonts/lettertiming of automatische matte. |
| 2 | `icon-strike` | Beeldoperatie | Meerdere eigen iconen met strike en exit; timing nog niet aan gesproken iconnamen gekoppeld. |
| 3 | `prompt-bar` | Beeldoperatie | Inputkaart en typewriter; geen echte promptuitvoering of resultaatroll-in. |
| 4 | `grade-slider` | Beeldoperatie | Eigen footage onder moving splitmask; rechterdeel krijgt Canvas-gradefilter. Geen automatische kleurmatch of exacte reference-grade. |
| 5 | `magazine-cover` | Basisanimatie | Eigen coverlayout met werkelijk geselecteerde videofoto; geen automatische coverlines/barcode of fontmatching. |
| 6 | `nle-timeline` | Basisanimatie | Geanimeerde tracks/playhead; geen reconstructie van de werkelijke EDL als NLE-timeline. |
| 7 | `file-drop` | Basisanimatie | Dalende documentkaarten met eigen video-thumbnail; geen werkelijk verworpen takefragment of automatische afkeur. |
| 8 | `odometer-recursion` | Beeldoperatie | Cubic counter en geneste eigen bewegende video; counter is configureerbaar getal, geen werkelijk bron/editduur-odometer. |
| 9 | `mood-curtain` | Beeldoperatie | Eigen footage krijgt bewegende grade-onthulling en vignet; geen grainmodel of automatic lookmatching. |
| 10 | `grid-collapse` | Basisanimatie | Eigen media in gridcellen; zonder mediaSources herhaalt dezelfde video; geen automatische andere creatorselectie. |
| 11 | `page-scroll` | Basisanimatie | Clipped scroll met echte media-previewrijen; geen interpretatie van echte pagina of gesproken rijhighlights. |
| 12 | `comment-thread` | Basisanimatie | Staggered commentkaarten; geen persistent storyboardcomment-/replymechanisme. |
| 13 | `word-stamp` | Basisanimatie | Grote gedraaide kaderstempel; geen per-letter serifheadline uit referentie. |
| 14 | `giant-captions` | Basisanimatie | Gestapelde grote woorden; geen volledige captionbox/payofftransformatie. |
| 15 | `video-card` | Basisanimatie | Kaart toont werkelijke walkthrough/video; geen automatische hoofdstukherkenning of videoplayer-controlsynchronisatie. |
| 16 | `comment-cta` | Basisanimatie | Lokale getekende commentkaart; geen daadwerkelijke post/reply/like of externe API. |
| 17 | `camera-transitions` | Beeldoperatie | Echte bron transformeert met settle; richting, spin/drop en attack instelbaar; optionele previous-bron onder cut. Geen optical-flow motionblur of automatische cutmotivatie. |
| 18 | `contact-sheet-hook` | Basisanimatie | Grid met eigen levende mediakaarten; geen verschillende echte bronmomenten zonder apart aangeleverde assets. |
| 19 | `receipt-printer` | Basisanimatie | Papier-reveal met getekende tekst; geen dynamische instructieregels, tear-off of toss. |
| 20 | `jiggle-delete` | Beeldoperatie | Jiggle en krimp/delete; geen appassets of automatische naam-/woordkoppeling. |
| 21 | `keycaps` | Stand-in | Keycap-rij met drukken; geen vallende tiles, collision pile of bezem. |
| 22 | `projected-film` | Basisanimatie | Eigen footage in filmframe met rails/kras/vignet; geen stemgedreven soundtrackstrip of fysieke filmtransport. |
| 23 | `film-look` | Stand-in | Canvas-tint/kras/vignet; geen specifieke teal-shadow/warm-highlight footagegrade. |
| 24 | `eyedropper-grade` | Stand-in | Eigen footage-preview met vaste swatches en cursor; geen echte pixelkleurselectie of gekoppelde grade. |
| 25 | `reel-cascade` | Basisanimatie | Eigen videokaarten vallen in stapel; mediaSources kan reeds geladen alternatieven kiezen; geen collisionphysics. |
| 26 | `playing-grid` | Basisanimatie | Grid toont echte mediaframes; zonder meerdere bronnen dezelfde clip; geen automatische portfolioselectie. |
| 27 | `reel-feed` | Basisanimatie | Eigen videokaarten in feedvorm; geen snelheidsprofiel/scrollbrake met full-frame motionblur. |
| 28 | `intertitle` | Basisanimatie | Gekleurde titelplaat; geen iris-close op echt gezicht. |
| 29 | `screenplay-page` | Basisanimatie | Getypte scriptregels op kaart; geen eigen transcript met woordgewijze scriptmarkering. |
| 30 | `knockout-captions` | Beeldoperatie | Echte offscreen tekstuitsparing; woordtiming/leesbaarheid op eigen footage nog beoordelen. |
| 31 | `lens-ring` | Basisanimatie | Draaiende schaal met label; geen gekoppelde focal-length/readout of optische cameraactie. |
| 32 | `grease-pencil-sheet` | Stand-in | Titel met getekende ellips/markeringen; geen echte takecontactsheet of afgekeurde framekeuze. |
| 33 | `title-card-dive` | Basisanimatie | Schaalbare titelplaat; geen footage-in-phone compositie met echte dive. |
| 34 | `picture-dive` | Basisanimatie | Vier geneste eigen mediapanelen en schaalbeweging; dezelfde actuele bronframe of expliciet gekozen media, geen 3D kamertracking. |
| 35 | `live-markup` | Basisanimatie | Groeiende ellips over titel; geen footage-desaturatie of tracking op hoofd. |
| 36 | `storyboard-deck` | Basisanimatie | Fanned kaarten met werkelijke media; geen automatisch geselecteerde diverse storyframes of persistent commentactie. |
| 37 | `gravity-drop` | Basisanimatie | Springbeweging van titelblok; geen individuele letters met gesimuleerde collisions. |
| 38 | `video-backdrop` | Beeldoperatie | Werkelijke walkthrough of geselecteerde video full-frame; voor echte persoon ervoor foregroundFrames nodig. |
| 39 | `comment-drop` | Stand-in | Staggered commentkaarten; geen vallende individuele keywordletters in input. |
| 40 | `shape-transitions` | Basisanimatie | Iris, blinds, doors en clock-clipping met echte optionele `next`-bron; geen automatisch gekozen cutpunt, geometrische 3D deuren of volledige transitionbibliotheek. |
| 41 | `press-front` | Basisanimatie | Eigen cover/krantplaat met monochroom eigen videovenster; geen echt live-halftone of volledige newspaperkolommen. |
| 42 | `paper-tear` | Beeldoperatie | Twee rafelige panelen met schaduw/peel; previous-medialaag moet worden aangeleverd; geen fysische curl. |
| 43 | `blade-slice` | Beeldoperatie | Echte bronvideo verdeeld in tegengesteld bewegende horizontale banden; geen mondtracking of automatische cut-on-word. |
| 44 | `day-dial` | Basisanimatie | Draaiende klokmarkeringen en tijdlabel; geen uur-per-woordtik achter gemaskeerd subject. |
| 45 | `predict-keys` | Stand-in | Keycap-rij; geen volledige keyboard/input/predictivebar-simulatie. |
| 46 | `impact-frame` | Basisanimatie | Eigen starburst en woord; geen live ink/posterization van bronshot en anime speed-lines. |
| 47 | `orbit-ring` | Beeldoperatie | Projectie van letters in rear/front-pass; vereist foreground-alpha en handmatige center; geen headtracking. |
| 48 | `dolly-zoom` | Beeldoperatie | Achtergrond en foreground-alpha hebben onafhankelijk tegengestelde schaal. Vereist schone `background` plus matte voor een bruikbare echte shot; zonder die inputs blijft dit een synthetische/ghostgevoelige demonstratie, geen gereconstrueerde 3D-perspectiefwissel. |
| 49 | `banknote` | Basisanimatie | Eigen foreground/video in monochroom medaillon en oplopend configureerbaar bedrag; geen engraving/displacement. |
| 50 | `voice-note` | Basisanimatie | Eigen waveformachtige balk; geen uit stemaudio afgeleide waveform of transcript/send-state. |
| 51 | `letter-dive` | Beeldoperatie | Echte footage via source-in door een sterk inzoomend woordmasker, met late crossfade naar volledig bronbeeld om een lege eindframe te voorkomen. Zonder media deterministisch kleurverloop; geen automatische keuze/tracking van een glyphopening of 3D camera. |
| 52 | `live-cursor` | Basisanimatie | Pointerpad en clickring op kaart; geen automatisch geselecteerde/mobiele subjectcutout. |
| 53 | `head-stack` | Stand-in | Eigen subject-alpha of cropped videoportretten; nog geen gelabelde tiles met stacking/topplephysics. |
| 54 | `rack-focus` | Beeldoperatie | Achtergrondblur en scherpe aangeleverde alpha; zonder matte synthetische demo; geen autofocus/segmentation intern. |
| 55 | `code-body` | Beeldoperatie | Codeglyphs echt geclipt in aangeleverde subject-alpha met verticale scan; zonder alpha codekaartdemo; geen automatische segmentation intern. |
| 56 | `post-wall` | Basisanimatie | Eigen bewegende media in enkele kaarten; geen één-tegel-per-dag-dataset of postcounter. |
| 57 | `clone-row` | Basisanimatie | Offset kopieën van echte foreground-alpha of cropped video; geen autonome body/face-tracking, voor echte cutouts alpha nodig. |
| 58 | `layer-explode` | Basisanimatie | Perspectiefplaten met echte video, monochrome kopie en foreground; captionlaag nog label, geen stemwaveform. |
| 59 | `sketch-words` | Basisanimatie | Titel en growing/dashed underline; geen penciltextuur of handgeschreven glyphtracing. |
| 60 | `blow-away` | Stand-in | Tekstletters waaien uiteen; geen pixels/deeltjes van subject en gereconstrueerde clean plate. |
| 61 | `incoming-call` | Basisanimatie | Eigen telefoon/call-vorm; geen compact buzz/decline-banner op gesproken cue. |
| 62 | `search-suggest` | Basisanimatie | Typewriter en vaste suggesties; geen dynamische online zoekresultaten of semantische suggesties. |
| 63 | `double-exposure` | Beeldoperatie | Secundaire geselecteerde media via source-in in echte subject-alpha; vereist foreground en andere bron voor rijk effect; geen automatische scenechoice. |
| 64 | `shockwave` | Stand-in | Expanderende lijnring; geen displacement/vervorming van kamer of bronvideo. |
| 65 | `room-doors` | Beeldoperatie | Bronvideopanelen schuiven/schalen open op werkelijke walkthrough/gekozen media; geen getrackte kamergeometrie of fysische schaduwen. |
| 66 | `finger-draw` | Stand-in | Vooraf getekende ellips; geen fingertiptracking of pad uit handbeweging. |
| 67 | `follow-chip` | Basisanimatie | Eigen pill/button-reveal; geen werkelijk following-state/klik of accountactie. |

## Volgende kwaliteitsslag

Verbeter eerst de stand-ins die de kernwensen raken: echte alpha-backed talking head, semantische takekeuze via agentreview, betrouwbaar getimede woordcaptions en eigen schermmedia. Werk daarna naar echte orbit-occlusie, keynote-/SaaS-kaarten, screen-in-card en leesbare editorialtitels op eigen bronmateriaal. Met eigen input gebruiken scene-kaarten inmiddels echte video/walkthrough en portraitvormen foreground-alpha of cropped video; de standaardgalerij blijft zonder bronmateriaal synthetisch. Dat levert geen verschillende takes of nieuwe B-roll op zonder daadwerkelijk verschillende aangeleverde media.

Het algemene videopad, B-roll, walkthrough, foregroundframes en woordcaptions kunnen functies leveren die een specifieke zelfstandige demo niet intern bevat. Registreer zulke combinaties als een concrete job met inputs, niet als een stilzwijgende upgrade van alle recipes.

Gebruik het [acceptatieplan](visual-acceptance.md) om gemeten resultaten naast eigen renderpreviews te bewaren. Publieke effectnamen en referentielinks staan in [de inventaris](../research/public-effects-inventory.json); upstream licenties staan in [de repositoryaudit](../research/repository-audit.md).


## Eigen media in recipes

De shared Canvashelpers gebruiken per effect de aangeboden eigen media, zonder globale bronstate. `scene()` kiest standaard `walkthrough`, daarna `video`; `portrait()` kiest `foreground`, daarna een cropped eigen video. Zonder media blijven zelfstandige galerievoorbeelden zichtbaar. Grid, covers, recursie, kaarten en feed blijven dus bruikbaar als losse demo én met werkelijke eigen opname.

Optioneel kan `params.mediaSources` een array keys van reeds geladen media bevatten. Bij meerdere kaarten wordt door die array geroteerd. Elke key moet verwijzen naar materiaal dat de gedeelde loader daadwerkelijk heeft geladen. Een helper die zo’n key kan tekenen is geen bewijs dat willekeurige nieuwe paden al door de loader worden ingeladen; controleer het actuele jobcontract. Dezelfde video negenmaal tekenen is ook geen selectie van negen verschillende takes.

`foregroundOnTop: false` op een effect onderdrukt de normale laatste foregroundpass wanneer dat voor een bewuste transform nodig is. Blade-slice, banknote, paper-tear, room-doors en code-body doen dat standaard, zodat de onbewerkte persoon niet onbedoeld boven zijn eigen getransformeerde beeld wordt teruggezet. Double-exposure onderdrukt deze pass wanneer een echte alpha wordt gebruikt.

Deze media-backed paden zijn toegevoegd na de eerste bibliotheekvalidatie. Syntaxcontrole is uitgevoerd; alleen een geïsoleerde Actions-run van de betreffende commit met echte eigen media kan de browserpaden bewijzen. Gebruik synthetische eigen fixturemedia op de publieke runner, geen klantopnames.

## Herstelronde: compositie en instelbare beweging

Deze bronwijzigingen zijn door syntax- en pure unitcontroles gecontroleerd. Visuele acceptatie moet op de geïsoleerde runner voor de exacte commit worden vastgelegd; de classificaties zijn geen renderresultaten.

- Captiongroepen gebruiken werkelijk gemeten woordbreedtes, maximaal twee regels, zinsgrenzen, gecentreerde veilige marges en een donkere contrastplaat. Actieve woorden hebben een korte begrensde schaalpuls; woordtijden blijven uit het transcript komen. Ze staan rond y=1090–1152 in een 720×1280-compositie.
- `zoom-punch` houdt zijn bereikte schaal vast. `camera-transitions` gebruikt een cut-in met cubic settle, `direction: "left"`, `mode: "spin"`/`"drop"` en `attack` in seconden. Dit levert geen optische motionblur op.
- `dolly-zoom` gebruikt `amount` voor achtergrondzoom en `subjectAmount` voor een onafhankelijke tegengestelde subjectzoom. Lever `job.background` met een rechtmatig verkregen schone achtergrond en `foregroundFrames` aan. Een bron waarin de persoon nog aanwezig is kan dubbelbeelden tonen; zonder clean plate is het geen geaccepteerd dollyshot.
- `shape-transitions` accepteert `variant: "iris" | "blinds" | "doors" | "clock"`, `attack` en `job.next`. `paper-tear` kan nu daadwerkelijk `job.previous` inladen. Deze bronnen mogen video of PNG/JPEG/WebP zijn binnen `public/`.
- `letter-dive` gebruikt een echte tekst-alpha met bronmedia via source-in. `double-exposure` behoudt zijn secundaire beeld nu onder een zachte accenttint; de eerdere opaque fill overschreef dat beeld.
- `kinetic-hook` en `giant-captions` accepteren `wordTimes: [{start: 0.1}, …]` in lokale seconden of `startMs` in lokale milliseconden. Met `syncWords: true` op het effect worden captionwoordtijden binnen het effectinterval gebruikt. De auteur moet de effecttekst en captionwoorden inhoudelijk laten overeenkomen; dit is geen automatische tekstalignment.
- De gedeelde media-loader wacht op geladen frames, meldt timeout/loadfouten, begrenst seeks en voorkomt dat scrubben naar exact het einde een niet-bestaand foregroundframe vraagt. Stage wacht op geladen lokale fonts voordat een job start.

Na inspectie van de galerierenders is de no-media double-exposure-stand-in vervangen door een contrastrijke, expliciet synthetisch gelabelde portretsilhouet met geanimeerd duotoonlandschap. De media-backed alphaoperatie blijft afzonderlijk. Letter-dive gebruikt een late crossfade naar volledig bronbeeld; dit voorkomt een lege eindframe, maar is geen automatische camera door een echte glyphopening. Deze wijzigingen vragen nieuwe isolated-runner beelden.
