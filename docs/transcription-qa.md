# Transcriptie-QA voor de tien demonstraties

Na echte lokale ASR op de geïsoleerde runner:

```sh
python3 scripts/demos.py --asr
python3 scripts/transcript-qa.py public/demos/manifest.json --out out/transcription-qa.json
```

De tweede opdracht leest het oorspronkelijke script en de taal uit ieder manifestitem, vergelijkt de daadwerkelijke jobcaptions met de opgeslagen ASR-transcriptie en gebruikt de manifestduur voor tijdcontroles. De bronbestanden worden niet aangepast. De QA draait uitsluitend op bestaande JSON; hij downloadt geen modellen en roept geen betaalde dienst aan.

Het rapport bevat per demonstratie:

- Word error rate (WER): Levenshtein-afstand op woorden, uitgesplitst in substituties, deleties en inserties. Unicode NFKC, kleine letters en leestekenverwijdering normaliseren vormverschillen; accenten en getallen blijven behouden. WER kan boven 1 uitkomen bij veel ingevoegde woorden.
- De fractie scriptwoorden die correct zijn herkend en de fractie met tevens geldige tijdintervallen. Dit vergelijkt woorden; het bewijst niet dat hun tijdstempels akoestisch correct zijn.
- Millisecondevalidatie: eindige getallen, niet-negatieve start, einde na start, monotone starttijden en einde binnen de manifestduur. Overlappende woordintervallen worden voor tijddekking samengevoegd zodat dekking niet boven de videoduur telt.
- Modelconfidence: gemiddelde, minimum, aantal onder 0,5 en ontbrekende waarden. Deze modelkans is geen gekalibreerde kans op correcte woorden.
- Genormaliseerde brontekst en hypothese plus de afzonderlijke woordfouten voor inhoudelijke beoordeling.

De taaloverzichten voor Nederlands en Engels bevatten een micro-WER: alle woordfouten gedeeld door alle scriptwoorden in die taal. `bothLanguagesTested` vereist werkelijk beide talen in de ingelezen manifestitems. Alleen het bestaan van een transcriptbestand geldt niet als geslaagde ASR-test.

De standaard lokale bruikbaarheidsgrens is WER ≤ 0,35 en minstens 65% correct herkende scriptwoorden met geldige tijden, zonder ongeldige intervallen en met een geregistreerd model. Dit is een expliciete projectdrempel voor een technische tiny-modeldemonstratie, geen publicatiekeurmerk. Iedere demonstratie en beide talen moeten voldoen voordat het totaalrapport `usable: true` krijgt. Hoge WER blijft zichtbaar als `usable: false`; controleer namen, getallen en commerciële claims altijd handmatig. Stel de grenzen desgewenst expliciet in met `--max-wer` en `--min-timed-coverage`.

Ongeldige tijden of confidencewaarden laten de opdracht na het schrijven van het rapport eindigen met code 2. Ontbrekende/corrupte bestanden, tegenstrijdige transcript/jobmetadata en paden buiten de publieke bronmap stoppen ook met code 2. Hoge WER, ontbrekende woorden of onvoldoende taaldekking staan standaard als negatieve kwaliteitsuitkomst in het rapport; met `--require-usable` geven die tevens exitcode 1. Daardoor kan CI technische timingproblemen blokkeren en tegelijk een eerlijk rapport van een zwak ASR-resultaat bewaren.

Dit experiment gebruikt door espeak-ng gegenereerde synthetische spraak. Het bewijst geen vergelijkbare nauwkeurigheid bij natuurlijke Nederlandse/Engelse sprekers, dialecten, muziek of rumoer. De scripttekst is woordelijke ground truth, geen geforceerd uitgelijnde ground truth voor woordtijden. De gemeten captiontijddekking bewijst daarom geen audiovisuele synchronisatie, fonetische lipsync of overeenstemming met mondbewegingen. Dat vereist luisteren, bekijken en aanvullende akoestische analyse. Het rapport krijgt pas waarde als bewijs van deze runneruitvoering wanneer de echte demonstratietranscripties zijn gegenereerd en het resultaat bij het Actions-artifact is bewaard.

Validatie van de QA zelf: `python3 -m unittest discover -s tests -p test_transcript_qa.py`. De tests controleren bekende edit-afstanden, Unicode-normalisatie, lege ASR, tijdgrenzen en volgorde, samengevoegde intervaldekking, confidence, beide talen, afgeschermde paden en de CLI-exitcodes. De fixtures zijn als tests opgesteld en worden niet als echte ASR-uitkomst gepresenteerd.
