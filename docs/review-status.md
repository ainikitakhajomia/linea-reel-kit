# Werkstatus en bewijs

Peildatum: 27 november 2026. Status gaat over bewezen gedrag, niet over overeenkomst met een effectnaam.

| Onderdeel | Huidige uitkomst | Beperking |
|---|---|---|
| Bibliotheek | 67 zichtbare recepten, canvasanimatie; zoeken, categorie, bewaren, tekst/kleur/duur, jobdownload getest op schone Linux-browser | 39 basisanimaties, 18 beeldoperaties, 10 stand-ins; geen 67 premium geaccepteerde technieken |
| Preview/export | Zelfde renderer en effect-job; inspector en exportstage pixelgelijk in Linux-regressie | Geen perceptuele identiteitsgarantie tussen Canvas en gecomprimeerde MP4 |
| Effectexport | Eerste herstelrun exporteerde alle 67 MP4s op Linux | Recepten met synthetische standaardmedia; echte portretacceptatie afzonderlijk nodig |
| Camera en masking | Gescheiden subject/achtergrondcamera, daadwerkelijke tekst- en alpha-maskers, dubbele belichting hersteld | Dolly vereist clean plate; subjectalpha moet aangeleverd of gegenereerd worden |
| Transitie | Wipes, letter-mask, paper, previous/next-bronpaden | Geen getrackte fysieke 3D-scène |
| Captions/audio | Twee regels, contrastplaat, woordaccenten, echte lokale ASR en FFmpeg audiomix | Containerstarts en woordtijden bewijzen geen inhoudelijke lipsync |
| Editing | Stilte-/takevoorstellen, EDL, timestampremapping, brand en intentplanner | Slechte take inhoudelijk kiezen vraagt nog agentreview van transcript én bron |
| Codex/Claude | Eén canonical skill plus geïnstalleerde kopieën; Nederlands/Engels en maximaal vijf varianten | Afhankelijk van aanwezige lokale tools, bronmedia en modelweights |
| Tien films | Afzonderlijke synthetische scripts, getekende presentator/concept-UI, lokale stem, alpha, captions en effecten | Illustratieve mond beweegt op energie; geen echte presentator; 3D-film gebruikt 2.5D |
| Vercel | Geen deployment bevestigd | Zie deployment-status.md; geen betaald product aangemaakt |

## Bewijsbestanden

GitHub Actions levert `visual-preview-evidence` met interfacebeelden, `browser-validation.json`, `composition-validation.json` en compositing-contactsheet. De uitgebreide renderworkflow levert `linea-reel-kit-rendered`: alle 67 MP4s, FFprobe/SHA-rapport, vier contact sheets uit daadwerkelijk gedecodeerde exports, tien complete MP4s met QA en contact sheets, en een draagbare reviewmap.

Referentievergelijking: alle 67 bestaande zes-samplecontactbladen zijn opnieuw bekeken, plus fijnere sequenties uit het eerdere onderzoek. Dat is een tijdsteekproef, geen continue vergelijkingsplayback of audiobeoordeling. Zie comparison.md en effect-status.md voor concrete verschillen. Er is geen ongefundeerde premium- of parityclaim.
