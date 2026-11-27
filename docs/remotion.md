# Optionele Remotion-adapter

De primaire pipeline is Playwright + Canvas + FFmpeg en heeft geen Remotion-account of commerciële Remotion-licentie nodig. Deze adapter hergebruikt dezelfde effectfuncties in React/Remotion. Niet uitgevoerd: de organisatie is niet verondersteld onder Remotions gratis licentie te vallen.

Controleer je bestaande rechten: https://www.remotion.dev/license. De toolkit koopt of activeert geen abonnement.

Als je bestaande rechten geschikt zijn:

```sh
cd remotion
npm install
npm run studio -- --public-dir ../public
npm run render -- ../out/remotion.mp4 --props ../public/jobs/demo/job.json --public-dir ../public
```

Volg de hostregels voor browserrendering; in de Studio Linea-werkruimte uitsluitend op de geïsoleerde runner.

Deze adapter heeft nog geen volledige pariteit voor B-roll, footage-camerabewegingen, front/back captions en foreground-aware effecten. Gebruik voor aflevering de geteste root-renderer. De adapter is een startpunt voor een bestaande Remotion-workflow.
