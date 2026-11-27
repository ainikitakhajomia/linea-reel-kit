# Lokale audioafwerking

```sh
python3 scripts/audio.py mix out/video.mp4 --out out/video-mixed.mp4
python3 scripts/audio.py mix out/video.mp4 --out out/video-music.mp4 --music /pad/naar/eigen-muziek.wav
python3 scripts/audio.py mix out/video.mp4 --out out/video-complete.mp4 --music /pad/naar/eigen-muziek.wav --sfx-job public/jobs/demo/job.json
```

De input bevat video en narratie. Muziek blijft op laag niveau (0.12 gain), wordt geloopt tot de videolengte en via FFmpeg `sidechaincompress` verder gedempt onder de stem. De effectstarts uit `job.effects` of `effects` sturen subtiele korte geluiden aan: eigen deterministische noise/sine-sweeps met attack/decay-envelope. Geen externe samples, uploads, API-calls of betaalde diensten. Gebruik alleen muziek waarvoor je de rechten hebt.

De gemixte audio wordt eerst als tijdelijke PCM gemeten, daarna met een tweede loudnorm-pass afgewerkt richting **−16 LUFS**, **−1.5 dBTP** en LRA 11. De geprinte metadata bevat meetwaarden en `twoPass`. Bij onmeetbare stilte gebruikt de tool een enkele dynamische normalisatiepass (`twoPass:false`). Zeer korte clips, beperkte dynamiek en AAC-encoding kunnen van de targets afwijken; controleer de uiteindelijke uitvoer, targets zijn geen kwaliteitsgarantie.

Output is MP4 met AAC, 48 kHz, 192 kbps. Bestaande H.264-video wordt zonder herencoding gekopieerd; andere videocodecs worden naar H.264 omgezet. De videolengte blijft leidend. Elke mix vereist een nieuwe uitvoernaam: de tool weigert bronbestanden en bestaande outputs te overschrijven. Paden worden als subprocess-argumenten doorgegeven, nooit via shellinterpolatie. Tempbestanden blijven lokaal en verdwijnen na voltooiing.

Verificatie: `python3 -m unittest discover -s tests -p test_audio.py`. De integratietest maakt één seconde echte FFmpeg-video/narratie en een korte muziekloop, voert ducking/SFX/tweepass-normalisatie uit, controleert AAC, duur, niet-stille samples, finale loudness binnen 1 LU van −16 en finale true peak ≤−0.8 dBTP (AAC-tolerantie), en vergelijkt de gekopieerde H.264-pakkethash met het origineel. Ook deterministische synthese en de overschrijfbeveiliging worden getest. Dit meet technische correctheid; luister de mix en de snijpunten af voordat je publiceert.
