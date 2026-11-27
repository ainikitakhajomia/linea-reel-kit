# Publieke repositories en hergebruik

Gecontroleerd 27 november 2026. Bronnen zijn GitHub REST-metadata, recursieve trees, werkelijk opgehaalde LICENSE/README/bronbestanden, `git ls-remote` en publieke zoekresultaten. **Bestaan, inspectie, syntactische validatie en end-to-end uitvoering zijn verschillende controles.** Geen van onderstaande complete upstream-pakketten is blind geïnstalleerd of als geheel getest. Uitgevoerde kleine hergebruikmodules staan onderaan. Exacte snapshots staan in `repositories/`; rate-limitfouten staan daar ook.

| Repository | Toegang en code | Werkelijke licentie | Functionele waarde en besluit |
|---|---|---|---|
| [justynberk/reel-kit](https://github.com/justynberk/reel-kit) | GitHub API 404; oorspronkelijke bron niet toegankelijk | Niet vast te stellen | Geen broncode of assets overgenomen. Geen conclusie dat gelijknamige repos een fork zijn. Publieke zoekindex bevestigt historische vindbaarheid, niet huidige beschikbaarheid of hergebruikrechten. |
| [AskEditor/ai-video-editing-skills](https://github.com/AskEditor/ai-video-editing-skills) | Bestaat; 335 tree-items, echte Python core/effects/tests; HEAD `e20000b262fb5f2b7e0e87f9354d44bc00e545ca` | MIT code; fonts/modellen afzonderlijk, zie NOTICE | Sterkste effectencatalogus: 41 workflows, segmentation, captions, clean cut, behind-person, B-roll, geluid, review. Dependency-free Timeline daadwerkelijk hergebruikt. Volledige pack is English/single speaker, doorgaans één overlay per pass. Zware strak gepinde dependencylijst niet blind installeren. |
| [prathameshp107/video-editing](https://github.com/prathameshp107/video-editing) | Bestaat; 110 tree-items, 16 skills, helpers/tests; HEAD `b344da99bfaeb496c048703b82bf1a034d732f2a` | **Geen LICENSE gevonden** in recursieve tree; README zegt wel open-source | Alleen onderzoek. Niet vendoren op basis van alleen marketingtekst. Interessante storyboard/shot-log/EDL aanpak kan onafhankelijk gerealiseerd worden. |
| [pycodebr/heditor](https://github.com/pycodebr/heditor) | Bestaat; 184 tree-items; HEAD/tag v2.22.0 `4f19f560a5a26f3b32a3ea4114fa8b42b84c51f8` | LICENSE is MIT, ondanks API `NOASSERTION`; derden afzonderlijk | Veel named styles, HyperFrames/GSAP compositie, brand en voice-first QA. Breder dan alleen talking heads. Niet geïnstalleerd; stijl/workflowbron, geen audio/assets bundelen zonder afzonderlijke controle. |
| [tecnomanu/motion-video-styles](https://github.com/tecnomanu/motion-video-styles) | Bestaat; 46 tree-items; HEAD `57d76f6a18a4e3a1d1a1657e3bfc80934b0b9e05` | MIT code; GSAP/TTS/muziek afzonderlijke voorwaarden | README heeft 7 styles (metadata verouderd: 6), concrete HTML/GSAP/Playwright/FFmpeg engine. Word cues, deterministic randomness, cubic counter easing, typewriter en caption chunking dependency-free geadapteerd. |
| [robinsadeghpour/reel-kit](https://github.com/robinsadeghpour/reel-kit) | Bestaat; 60 tree-items; HEAD `be37c3f1cd87d2a628bdc77b0f2577a3b6fe10c1`; metadata `fork=false` | MIT | Concrete `analyze→plan→tighten→proof→cut→verify` pipeline, take ledger, overlays en audio QA. Eigen project; geen aangetoonde genealogie met Justyn. Research-subcommands gebruiken betaalde Apify/Gemini en vallen buiten toegestane gratis workflow. |
| [kurbaitaev/ghost-editor](https://github.com/kurbaitaev/ghost-editor) | Bestaat; 443 tree-items; HEAD `d71bdb62d8e8280f05d6271bb72610ca83d38d8a`; tags v0.1.0/v0.2.0/v0.3.0 geverifieerd | MIT code; demo-opnames expliciet niet hergebruiken; media en third-party packs eigen licenties | 19 named styles, cutout, face tracking, clean OS, whiteboard, SaaS/productpage, takes en mix. Uitgebreide werkende code zichtbaar; volledige uitvoering niet gecontroleerd. Gemini/ElevenLabs optioneel en niet activeren. |
| [remotion-dev/remotion](https://github.com/remotion-dev/remotion) | Bestaat; grote actieve TS/React monorepo, HEAD bij inspectie `2f843fdad11662be81cc2e0de6114fdde6c59502` | **Eigen Remotion License**, geen algemene permissieve OSS-licentie | Free License omvat individuen, for-profit met ≤3 werknemers, nonprofit en niet-commerciële evaluatie; anders Company License nodig. Geen aankoop/toestemming veronderstellen. Daarom primary renderer Playwright+FFmpeg; Remotion optionele integratie binnen bestaande rechten. |

Alle licentiebevindingen verwijzen naar de werkelijk opgehaalde `LICENSE`/`LICENSE.md` op genoemde HEAD; alleen een SPDX-indicator was onvoldoende. MIT notices moeten bij substantiële kopieën behouden blijven. Modelweights, muziek, fonts en demo-video's erven niet automatisch de codelicentie.

## Oorspronkelijke repo en publieke forks

De oorspronkelijke repo geeft 404. Dit maakt geen onderscheid tussen private, verwijderd of hernoemd. Er is geen legitieme broncode-ophaalroute gevonden. [Een publieke historische index](https://anclum.com/en/s/justynberk-reel-kit/) beschrijft een toenmalige storyboard-first skill en 17 effecten; dit is **secundaire historische evidence**, geen bewijs van de actuele 67-effectenbundel of van een licentie. Ook [NicheDB](https://nichedb.dev/c/workflows?tag=reels) vermeldt de repo historisch. Geen private caches, betaalde toegang of beperkingen omzeild.

De opgevraagde `forks` endpoints werden grotendeels door GitHub unauthenticated rate limiting geweigerd. Dit is geen bewijs dat er geen forks bestaan. De gelijknamige Robin-repo is volgens eigen metadata geen fork; de inhoud is een andere implementatie. Publieke zoekopdrachten leverden geen aantoonbare, toegankelijke kopie met bewezen Justyn-herkomst én verifieerbare licentie op. Daarom geen voormalige Justyn-code ingevoerd.

## Releases en praktische uitvoerbaarheid

`git ls-remote --tags` bevestigt Ghost v0.1.0–v0.3.0 en heditor v1.0.0–v2.22.0. Ghost [release notes](https://github.com/kurbaitaev/ghost-editor/releases) documenteren stijl- en QA-uitbreidingen. Motion-video-styles en Robin gaven een lege releases-array. Andere releases-API requests raakten de rate limit; dat is geen negatieve releasebevinding. Inspectie toont echte implementaties, maar README-claims worden niet als lokale geslaagde tests aangemerkt.

Een concreet reviewpunt in motion-video-styles `render.mjs`: Chromium wordt met `--disable-web-security` gestart en de FFmpeg close-code wordt niet gevalideerd. Deze runner niet blind overnemen. De kleine timingmodule is onafhankelijk van de runner geëxtraheerd. AskEditor code heeft een brede Python stack (OpenCV/MediaPipe/Whisper); scheiding van pure timing en zware inference voorkomt installatieconflicten.

## Aanvullende primaire bronnen

| Project | Verificatie | Gebruik |
|---|---|---|
| [SYSTRAN/faster-whisper](https://github.com/SYSTRAN/faster-whisper) | README en MIT LICENSE werkelijk opgehaald | Lokale Nederlandse/Engelse transcriptie met woordtijden; geschikt als enige ASR-backend. Modellicenties blijven afzonderlijk. |
| [WyattBlue/auto-editor](https://github.com/WyattBlue/auto-editor) | README en Unlicense werkelijk opgehaald | Silence/motion based cuts; optionele adapter, vermijd tweede concurrerende timeline als primary. |
| [MakeMyClip/editor](https://github.com/MakeMyClip/editor) | Metadata/README/package.json en MIT LICENSE opgehaald; tree-API rate limited | CLI + MCP + browser timeline + NLE-export. Sterke toekomstige integratie; niet uitgevoerd, Node/bundled FFmpeg-voorwaarden controleren. |
| [kajisho5/ffmpeg-skill](https://github.com/kajisho5/ffmpeg-skill) | README/package.json v4.20.3/MIT LICENSE opgehaald | 42 tooling commands, declarative renderer, contract-derived MCP. Niet uitgevoerd; alternatief voor veel eigen FFmpeg wrappers, uitgebreidere dependency/licentiecontrole nodig vóór bundelen. |
| [timkulbaev/ai-video-editor](https://github.com/timkulbaev/ai-video-editor) | README/pyproject.toml/MIT LICENSE opgehaald | Silero VAD/faster-whisper/FFmpeg pipeline met MCP. Niet uitgevoerd; overlapt met primary pipeline. |

Deze kandidaten zijn aangetoonde publieke bronnen, geen claim dat vijf integraties al geïnstalleerd zijn. De toolkit integreert geselecteerde onderdelen achter één skill/CLI in plaats van meerdere agent-editors automatisch te installeren.

## Daadwerkelijk geselecteerd, gecombineerd en uitgevoerd

1. `vendor/askeditor/timeline.py`: ongewijzigde MIT Python Timeline, stdlib-only. Ondersteunt kept segments, bron↔output timestamps, freezes en eindholds. Uitgevoerde assertions: cut removal, source/output mapping, excluded timestamps en freeze synchronization geslaagd.
2. `vendor/motion-video-styles/timing.mjs`: MIT adaptatie uit `engine/common.js`; geen DOM/GSAP, geen assets. Exports `cueWord`, `seededRandom`, `easeOutCubic`, `typeText`, `countValue`, `captionGroups`. Uitgevoerde Node assertions voor Nederlandse diacritische cue, typewriter timing, cubic count halfway (87.5%), clamping, captions en determinisme geslaagd.
3. Gedownloade AskEditor run/words/models/timeline en Robin kit/tighten/cut door Python `compile()` gecontroleerd. Dit is syntactische validatie, **geen** functionele end-to-end upstream test.

Vendored mappen bevatten LICENSE en provenance.json met bron-URL, pinned SHA en SHA-256. Geen beeld, muziek, fonts, beschermde demo-assets of Justyn-broncode meegekopieerd.
