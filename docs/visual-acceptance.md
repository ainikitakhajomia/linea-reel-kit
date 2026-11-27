# Visuele acceptatie en referentiemetingen

Een effect is pas gereed wanneer het op daadwerkelijk bewegend materiaal werkt en de bedoelde functie zichtbaar vervult. Een geldige effect-ID, animatie in een gallery of geslaagde render is daarvoor onvoldoende. Houd drie statussen uit elkaar:

- **Recipe/demo**: de code speelt een onafhankelijke vereenvoudiging af.
- **Functioneel**: de bedoelde beeldoperatie werkt op eigen testmateriaal, met opgegeven inputs en bekende beperkingen.
- **Visueel geaccepteerd**: een reviewer beoordeelt de uiteindelijke export met onderstaande rubric; bevindingen en settings zijn vastgelegd.

De publieke referenties zijn een maatstaf voor technieken, timing en afwerking. We reproduceren geen beschermde assets en publiceren geen kopieën van bronclips. Gebruik een eigen talking head, eigen softwareopnames en zelfgetekende UI voor vergelijkingen.

## Reviewopstelling

1. Gebruik een eigen 30-fps opname met scherpe randen, bewegende handen, bril/haar en minstens één snelle hoofdbeweging. Bewaar de onbewerkte bron.
2. Voeg een tweede opname toe met bewegende of drukke achtergrond. Voeg afzonderlijke Nederlandse en Engelse spraak toe voor captioncontrole.
3. Render op 720 × 1280 voor vergelijking met de publieke hero, en controleer daarna 1080 × 1920 als leverformaat. Schaal previews niet omhoog en noem dat extra detail.
4. Bekijk eerst in realtime met geluid, vervolgens zonder geluid, vervolgens framegewijs rond in-/uitgangen en cutranden. Controleer de uiteindelijke MP4, niet uitsluitend Canvas.
5. Leg input-hash, job/EDL, codecommit, browser/encoder, gebruikte modelweights en fonts vast. Noteer outputduur en probegegevens.
6. Gebruik de agent voor voorstellen en een menselijke reviewer voor visuele acceptatie. Een agent kan afwijkingen aanwijzen, maar een automatische “premium”-claim telt niet als meetresultaat.

## Rubric

Score per dimensie 0–3: 0 ontbreekt/fout; 1 demo werkt maar duidelijke afwijkingen; 2 functioneel bruikbaar met kleine zichtbare onvolkomenheden; 3 afgewerkt en consistent op beide testopnames. Functioneel vereist alle relevante dimensies ≥2. Visueel geaccepteerd vereist daarnaast geen blokkerende fouten en een expliciete reviewerbeslissing. De rubric is intern; niet wetenschappelijk gevalideerd.

| Dimensie | Waarop beoordelen | Blokkerende fout |
|---|---|---|
| Functie | Doet het werkelijk wat de effectnaam belooft? | Cirkel gebruikt als “finger tracking”; balk gebruikt als “knockout” |
| Compositie | Focus op persoon/product, marges en hiërarchie | Ogen/mond bedekt zonder bewuste reden; tekst buiten frame |
| Timing | Start op betekenisvol woord; duidelijke anticipatie/hold/exit | Afgebroken woord/gebaar, effect mist payoff |
| Motion | Samenhangende snelheid, versnelling en rust | Onbedoelde sprong, clip op tweenranden of jank |
| Easing | Past kracht/gewicht bij intentie | Elastisch UI-element waar zwaar papier bedoeld wordt |
| Masking | Correcte occlusie, nette randen en temporele samenhang | Witte halo, gaten, flikkerende matte, verkeerde laagvolgorde |
| Typografie | Leesbaarheid op telefoon, contrast en fontconsistentie | Onleesbare kernzin, ontbrekende glyphs of overvolle regel |
| Camera | Gemotiveerde verplaatsing; onderwerp houdt schaalpositie waar bedoeld | Dolly-zoom schaalt subject en achtergrond identiek |
| Overgang | Oud/nieuw shot worden coherent verbonden | Eén-frame flash, zwart frame of onbedoelde mismatch |
| Audio | Stem verstaanbaar, SFX ondersteunen beweging, geen clipping | Hoorbare digitale vervorming of weggevallen spraak |
| Export | Juiste aspectratio, fps, geluid en duur | Beschadigde MP4, verkeerde duur of ontbrekende stream |

Captions: controleer minimaal twintig duidelijke woorden per taal. Noteer per woord de eerste hoorbare klank en eerste zichtbare highlight, in outputframes. Richtwaarde: maximaal twee frames afwijking bij 30 fps voor de meeste duidelijke woorden; rapporteer alle grotere afwijkingen. Dit is een eigen acceptatiedoel, geen claim over de referentie of ASR-garantie. Vermijd nep-woordtijden uit gelijkmatig verdeelde scripts.

Cutcontrole: beluister ±0.3 seconden rond elke join. Geen afgekapte medeklinker, ademstoot of ontbrekend inhoudelijk woord accepteren. Het bestand kan technisch lipsync hebben terwijl een cut inhoudelijk slecht is; controleer beide afzonderlijk.

## Zes referentie-effecten en meetplan

De durations zijn gemeten met FFprobe op publiek aangeboden voorbeeldclips; 15-fps contact sheets zijn bekeken voor onderstaande selectie. Lengteverschillen van enkele milliseconden door container/audioafronding zijn geen effecttiming. Voor exacte onsets moet de video zelf op 30-fps frames worden bekeken. Originele easingcurves en source keyframes zijn niet beschikbaar.

| Referentie | Gemeten lengte / 30 fps | Zichtbare techniek | Wat onze test moet meten |
|---|---|---|---|
| [Kinetic hook](https://justyn.ai/reel-kit/media/fx/kinetic-hook.mp4) | 3.178 s; ongeveer 95 frames | Wisselende headlineopbouw; voorgrond boven type | Log per woord onset/settle/hold/exit; fout t.o.v. eigen woordtijden; matte blijft consistent |
| [Word stamp](https://justyn.ai/reel-kit/media/fx/serif-stamp.mp4) | 2.600 s; ongeveer 78 frames | Grote serif boven/achter hoofd | Letteronsets, impact-frame en leeshold; onderwerp occludeert tekst werkelijk |
| [Orbit ring](https://justyn.ai/reel-kit/media/fx/orbit-ring.mp4) | 3.712 s; ongeveer 111 frames | Projectie van draaiende letters voor/achter hoofd | Positie en schaal voor dezelfde glyph op kwartrotaties; correcte depthpass en gemotiveerde woordaccenten |
| [Paper tear](https://justyn.ai/reel-kit/media/fx/paper-tear.mp4) | 1.000 s; ongeveer 30 frames | Papier splitst met onregelmatige rand en onthult volgende shot | Eerste splitframe, 50% onthulling, volledig vrij frame; controleer edge continuity, shading en twee onafhankelijke helften |
| [Rack focus](https://justyn.ai/reel-kit/media/fx/rack-focus.mp4) | 2.304 s; ongeveer 69 frames | Selectieve achtergrondonscherpte met scherp subject | Zelfde haar-/oogregio blijft scherp; blurwaarden/overgangsduur loggen; randen en handen blijven geloofwaardig |
| [Finger draw](https://justyn.ai/reel-kit/media/fx/finger-draw.mp4) | 2.240 s; ongeveer 67 frames | Lijn volgt een werkelijk handgebaar | Overlay fingertip-coördinaten; meet mediane en maximale pad-tot-fingertipafstand; geen claim tracking bij authored cirkel |

Voor fingertiptracking: een voorlopig eigen doel is ≤12 px mediane afstand op 720-px breed beeld en geen sprongen van >40 px zonder overeenkomstige handbeweging. Rapporteer occlusies en confidence; deze grenzen zijn implementatiedoelen, geen uit de publieke clip bewezen prestaties.

Voor masking: inspecteer op 100% grootte rond haar, vingers en schouders; test zowel donkere als lichte achtergrond en typografie. Eén handmatig uitgeknipte still levert geen per-frame videobewijs. Een externe alpha-laag telt alleen als die werkelijk geladen en gesynchroniseerd wordt.

## Audio en ritme als aparte meting

De [publieke hero](https://justyn.ai/reel-kit/media/edit-v3.mp4) meet −14.25 LUFS integrated, −0.45 dBTP true peak en 3.20 LU LRA. Dat is een referentiemeting van één bestand, geen norm die onze toolkit blind moet kopiëren. De huidige editpipeline kiest een eigen loudnorm-doel; meet het gerenderde eindbestand opnieuw, inclusief toegevoegde muziek en SFX.

Voor elk betekenisvol visueel accent: noteer actieframe, geluidsonset en stemniveau in dezelfde passage. Laat stem verstaanbaar; overdaad aan cues verlaagt de score ook als ze precies synchroon zijn. Audio-metrics bewijzen geen inhoudelijke lipsync en geen goede sounddesignkeuze.

## Acceptatieregister

Gebruik per effect/variant een entry met: effect-ID, codecommit, input/output-hashes, recipe/functioneel/geaccepteerd-status, alle rubricscores, gemeten onsets, exportinstellingen, beperkingen, reviewer en datum. Voeg een eigen MP4-preview toe en een publieke bronlink. Een rij in de referentie-inventaris mag niet automatisch naar “geïmplementeerd” of “gelijkwaardig” promoveren.

Totdat dit register ingevuld is, zijn de 67 lokale recipes een uitvoerbare ontwikkelbibliotheek. De gebruiker kan de voortgang bekijken, maar krijgt geen onbewezen belofte van identieke kwaliteit.


## Uitgevoerde recipeverbetering en nog vereiste controle

De huidige Canvas-bron bevat echte strike-paths, een offscreen tekstuitsparing, letter-orbit met rear/front-passes, tweezijdig rafelig papier met schaduw en achtergrondblur met een scherp foreground-pad. `node --check src/effects.mjs` is geslaagd. Een lokale browsercheck kon niet starten doordat de pinned Chromium-binary ontbreekt; er is daardoor geen browser- of renderbewijs uit die poging. Volgens de workspace-instructies moeten browser-/rendercontroles op de geïsoleerde runner worden uitgevoerd.

De resterende kwaliteitsgrenzen zijn concreet:

- Icon strike: onsets zijn voorlopig secondegebaseerd, niet automatisch aan iconnaam/spraak gekoppeld.
- Knockout: de uitsparing gebruikt echte compositing, maar fontgrootte/regelverdeling moeten op eigen woorden worden beoordeeld.
- Orbit: de twee depthpasses werken alleen geloofwaardig met een passende foreground-alpha; een vaste ringpositie volgt het hoofd niet automatisch.
- Paper tear: independent paper panels met onregelmatige randen zijn geen fysische simulatie. Een vorige shot/image kan worden meegegeven; de renderer moet die laag ook werkelijk laden om een shottransition te bewijzen.
- Rack focus: een aangeleverde foregroundlaag wordt scherp over een vervaagde bron getekend. Geen zelfgemaakte matte aanwezig betekent synthetische demo, geen geslaagde automatische subject-separatie.
- Finger draw blijft authored graphics zonder fingertiptracking.
