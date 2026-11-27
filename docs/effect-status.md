# Status van alle 67 lokale recipes

Deze broninspectie beschrijft wat `src/effects.mjs` werkelijk tekent. Het is geen visuele acceptatie en geen product-parityclaim. Alle 67 publieke referenties zijn geïnventariseerd en bekeken; niet elke lokale recipe realiseert de gelijknamige functie volledig. De classificatie beschrijft inhoudelijke volwassenheid en is geen automatisch testresultaat.

- **Beeldoperatie**: de kenmerkende compositing-/bewegingsoperatie is aanwezig, met de genoemde input- en kwaliteitsgrenzen. Browseracceptatie en toepassing op echte footage blijven afzonderlijk nodig.
- **Basisanimatie**: zelfstandig geanimeerde interpretatie van het algemene idee, met meerdere ontbrekende reference-specifieke onderdelen.
- **Stand-in**: zichtbaar bewegende demonstrator, maar de kernfunctie van de gelijknamige referentie is wezenlijk eenvoudiger of ontbreekt.

Counts bij deze inspectie: 34 basisanimatie, 7 beeldoperatie, 26 stand-in. Geen enkele classificatie betekent automatisch “premium” of “visueel gelijkwaardig”. Voor groen-/normale achtergrondsegmentatie gelden apart [segmentation.md](segmentation.md); voor daadwerkelijke test- en renderstatus gelden README en het uiteindelijke Actions-runresultaat.

| # | ID | Classificatie | Concrete afwijking / vereiste |
|---|---|---|---|
| 1 | `kinetic-hook` | Basisanimatie | Getimede woordopbouw; geen reference-specifieke fonts/lettertiming of automatische matte. |
| 2 | `icon-strike` | Beeldoperatie | Meerdere eigen iconen met strike en exit; timing nog niet aan gesproken iconnamen gekoppeld. |
| 3 | `prompt-bar` | Beeldoperatie | Inputkaart en typewriter; geen echte promptuitvoering of resultaatroll-in. |
| 4 | `grade-slider` | Stand-in | Slider over getekende scene; geen echte dual-grade footagebewerking. |
| 5 | `magazine-cover` | Basisanimatie | Eigen coverlayout; geen automatisch aangepaste coverlines, barcode of subject-mask. |
| 6 | `nle-timeline` | Basisanimatie | Geanimeerde tracks/playhead; geen reconstructie van de werkelijke EDL als NLE-timeline. |
| 7 | `file-drop` | Basisanimatie | Dalende documentkaarten; geen werkelijk raw-playerfragment of afgekeurde-takeselectie. |
| 8 | `odometer-recursion` | Stand-in | Cubic getalcounter; geen raw/edit-tijddigits of frame-recursie. |
| 9 | `mood-curtain` | Basisanimatie | Vallende kleurstroken; geen echte grade/grain/vignette van footage. |
| 10 | `grid-collapse` | Basisanimatie | Getekende gridcellen; geen echte creatorvideo's of volwaardige zoom terug. |
| 11 | `page-scroll` | Basisanimatie | Clipped scroll met getekende scene-rijen; geen echte pagina of gesproken rijhighlights. |
| 12 | `comment-thread` | Basisanimatie | Staggered commentkaarten; geen persistent storyboardcomment-/replymechanisme. |
| 13 | `word-stamp` | Basisanimatie | Grote gedraaide kaderstempel; geen per-letter serifheadline uit referentie. |
| 14 | `giant-captions` | Basisanimatie | Gestapelde grote woorden; geen volledige captionbox/payofftransformatie. |
| 15 | `video-card` | Stand-in | Eigen kaart met getekende scene; algemene walkthroughlaag bestaat apart, geen per-card chapters. |
| 16 | `comment-cta` | Basisanimatie | Lokale getekende commentkaart; geen daadwerkelijke post/reply/like of externe API. |
| 17 | `camera-transitions` | Stand-in | Bij video vooral punch-in; geen afzonderlijke whip/spin/drop-overgangen per cut. |
| 18 | `contact-sheet-hook` | Stand-in | Getekende gridcellen; geen contact sheet van echte geselecteerde bronframes. |
| 19 | `receipt-printer` | Basisanimatie | Papier-reveal met getekende tekst; geen dynamische instructieregels, tear-off of toss. |
| 20 | `jiggle-delete` | Beeldoperatie | Jiggle en krimp/delete; geen appassets of automatische naam-/woordkoppeling. |
| 21 | `keycaps` | Stand-in | Keycap-rij met drukken; geen vallende tiles, collision pile of bezem. |
| 22 | `projected-film` | Basisanimatie | Filmrails, kras/vignet en scene; geen stemgedreven soundtrackstrip of fysieke filmtransport. |
| 23 | `film-look` | Stand-in | Canvas-tint/kras/vignet; geen specifieke teal-shadow/warm-highlight footagegrade. |
| 24 | `eyedropper-grade` | Stand-in | Vaste swatches en cursor; geen uit footage gesamplede kleuren of gekoppelde grade. |
| 25 | `reel-cascade` | Stand-in | Schuin gestapelde getekende kaarten; geen eigen bewegende reelcontent. |
| 26 | `playing-grid` | Stand-in | Getekende gridcellen met actieve lijn; geen zes daadwerkelijk afspelende video's. |
| 27 | `reel-feed` | Stand-in | Gestapelde getekende kaarten; geen versnellende feed met echte content en motionblur. |
| 28 | `intertitle` | Basisanimatie | Gekleurde titelplaat; geen iris-close op echt gezicht. |
| 29 | `screenplay-page` | Basisanimatie | Getypte scriptregels op kaart; geen eigen transcript met woordgewijze scriptmarkering. |
| 30 | `knockout-captions` | Beeldoperatie | Echte offscreen tekstuitsparing; woordtiming/leesbaarheid op eigen footage nog beoordelen. |
| 31 | `lens-ring` | Basisanimatie | Draaiende schaal met label; geen gekoppelde focal-length/readout of optische cameraactie. |
| 32 | `grease-pencil-sheet` | Stand-in | Titel met getekende ellips/markeringen; geen echte takecontactsheet of afgekeurde framekeuze. |
| 33 | `title-card-dive` | Basisanimatie | Schaalbare titelplaat; geen footage-in-phone compositie met echte dive. |
| 34 | `picture-dive` | Stand-in | Getekende scene schaalt op; geen meerdere levende recursieve fotolagen. |
| 35 | `live-markup` | Basisanimatie | Groeiende ellips over titel; geen footage-desaturatie of tracking op hoofd. |
| 36 | `storyboard-deck` | Basisanimatie | Drie eigen fanned kaarten; geen werkelijke videostoryboardframes en commentactie. |
| 37 | `gravity-drop` | Basisanimatie | Springbeweging van titelblok; geen individuele letters met gesimuleerde collisions. |
| 38 | `video-backdrop` | Stand-in | Gestapelde getekende scenes; echte walkthrough-overlay bestaat apart, geen automatische backdropvervanging. |
| 39 | `comment-drop` | Stand-in | Staggered commentkaarten; geen vallende individuele keywordletters in input. |
| 40 | `shape-transitions` | Basisanimatie | Expanderende cirkel; geen set blinds/barn-door/clock-wipes tussen twee media. |
| 41 | `press-front` | Basisanimatie | Eigen coverachtige krantplaat; geen live halftone-portrait en dicht newspaperlayout. |
| 42 | `paper-tear` | Beeldoperatie | Twee rafelige panelen met schaduw/peel; previous-medialaag moet worden aangeleverd; geen fysische curl. |
| 43 | `blade-slice` | Stand-in | Verschoven tekstbanden; geen werkelijk door mond gesneden en nog sprekende footagehelften. |
| 44 | `day-dial` | Basisanimatie | Draaiende klokmarkeringen en tijdlabel; geen uur-per-woordtik achter gemaskeerd subject. |
| 45 | `predict-keys` | Stand-in | Keycap-rij; geen volledige keyboard/input/predictivebar-simulatie. |
| 46 | `impact-frame` | Basisanimatie | Eigen starburst en woord; geen live ink/posterization van bronshot en anime speed-lines. |
| 47 | `orbit-ring` | Beeldoperatie | Projectie van letters in rear/front-pass; vereist foreground-alpha en handmatige center; geen headtracking. |
| 48 | `dolly-zoom` | Stand-in | Bij bronvideo globale zoom; geen onafhankelijk tegengesteld background-/subjectperspectief. |
| 49 | `banknote` | Basisanimatie | Eigen bankbiljetkaart met vast bedrag; geen gegraveerd echt portrait of oplopende bedragdigits. |
| 50 | `voice-note` | Basisanimatie | Eigen waveformachtige balk; geen uit stemaudio afgeleide waveform of transcript/send-state. |
| 51 | `letter-dive` | Stand-in | Individuele letters schalen in; geen video door tekstmask en camera die in glyphopening duikt. |
| 52 | `live-cursor` | Basisanimatie | Pointerpad en clickring op kaart; geen automatisch geselecteerde/mobiele subjectcutout. |
| 53 | `head-stack` | Stand-in | Gestaffelde synthetische portretten; geen gelabelde tiles met stacking/topplephysics. |
| 54 | `rack-focus` | Beeldoperatie | Achtergrondblur en scherpe aangeleverde alpha; zonder matte synthetische demo; geen autofocus/segmentation intern. |
| 55 | `code-body` | Stand-in | Getypte codekaart; geen codeglyphs binnen werkelijk bewegende subject-silhouette. |
| 56 | `post-wall` | Stand-in | Enkele getekende kaarten; geen één-tegel-per-dag-dataset en synchroon oplopende postcounter. |
| 57 | `clone-row` | Basisanimatie | Synthetische portrettenrij; geen gekloonde bewegende alpha-subjects uit bronvideo. |
| 58 | `layer-explode` | Basisanimatie | Vier benoemde perspectiefplaten; geen eigen footage/captions/audio in echte renderlagen. |
| 59 | `sketch-words` | Basisanimatie | Titel en growing/dashed underline; geen penciltextuur of handgeschreven glyphtracing. |
| 60 | `blow-away` | Stand-in | Tekstletters waaien uiteen; geen pixels/deeltjes van subject en gereconstrueerde clean plate. |
| 61 | `incoming-call` | Basisanimatie | Eigen telefoon/call-vorm; geen compact buzz/decline-banner op gesproken cue. |
| 62 | `search-suggest` | Basisanimatie | Typewriter en vaste suggesties; geen dynamische online zoekresultaten of semantische suggesties. |
| 63 | `double-exposure` | Stand-in | Synthetische portretten via screenblend; geen secundaire footage in echte subject-silhouette. |
| 64 | `shockwave` | Stand-in | Expanderende lijnring; geen displacement/vervorming van kamer of bronvideo. |
| 65 | `room-doors` | Basisanimatie | Twee schalende vlakke panelen; geen getrackte wanden of fysische diepte/shadowscene. |
| 66 | `finger-draw` | Stand-in | Vooraf getekende ellips; geen fingertiptracking of pad uit handbeweging. |
| 67 | `follow-chip` | Basisanimatie | Eigen pill/button-reveal; geen werkelijk following-state/klik of accountactie. |

## Volgende kwaliteitsslag

Verbeter eerst de stand-ins die de kernwensen raken: echte alpha-backed talking head, semantische takekeuze via agentreview, betrouwbaar getimede woordcaptions en eigen schermmedia. Werk daarna naar echte orbit-occlusie, keynote-/SaaS-kaarten, screen-in-card en leesbare editorialtitels op eigen bronmateriaal. Een preview van getekende kaarten is geen bewijs dat automatische video-insertie al op dezelfde plaats werkt.

Het algemene videopad, B-roll, walkthrough, foregroundframes en woordcaptions kunnen functies leveren die een specifieke zelfstandige demo niet intern bevat. Registreer zulke combinaties als een concrete job met inputs, niet als een stilzwijgende upgrade van alle recipes.

Gebruik het [acceptatieplan](visual-acceptance.md) om gemeten resultaten naast eigen renderpreviews te bewaren. Publieke effectnamen en referentielinks staan in [de inventaris](../research/public-effects-inventory.json); upstream licenties staan in [de repositoryaudit](../research/repository-audit.md).
