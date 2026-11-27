# Public offer and visual reference audit

Checked 2026-11-27. Primary reference: <https://justyn.ai/masterclass>. This is a public sales-page audit, not access to the purchased product. A demonstrated output does not establish that its source implementation, reliability, or automation claims are reproducible. Public media remain the creator's property; this repository links to them and does not redistribute them.

## Evidence collected

- The page's public effect catalogue enumerates **67 distinct entries**. All 67 linked MP4 references returned HTTP 200 during this audit. Their names, stable identifiers, poster URLs and video URLs are in [public-effects-inventory.json](public-effects-inventory.json).
- [public-media-index.json](public-media-index.json) records public page media links and 25 member-reel links; no testimonial images or member videos are redistributed.
- The main reel was downloaded temporarily for analysis: H.264, 720 × 1280, 30 fps, approximately 54.27 seconds. Three editing-mode demonstrations and the three alternative style demonstrations were decoded with FFprobe; see [reference-media-probes.json](reference-media-probes.json).
- All effect clips were downloaded to temporary storage, decoded and sampled at six times per clip. [all-effects-probes.json](all-effects-probes.json) records this technical coverage. Six particularly relevant effects were additionally inspected in temporal sequences at 15 samples/second. This is **not** a claim that every frame of every public video was manually examined.
- Direct profile fetches for Instagram, TikTok and YouTube were throttled or restricted by the web tool. No authentication, scraper bypass, paywall workaround or private source was used. Public site-hosted copies of the creator's social reels supply the visual evidence below. Live platform comments, unlinked uploads and platform-specific audio cannot be fully audited from this evidence.

## What the bundle publicly claims

The offer combines an editing kit, a carousel kit, a lesson library, a content-planning bonus and a phone-editing bonus. It advertises 11 modules / 35 lessons, four style examples, three editing modes, ongoing effects and an optional comment-DM automation add-on. The execution environment is a local agent on the user's computer; model subscriptions are separate. These are marketing claims unless a visible output is described below. Source: [sales page](https://justyn.ai/masterclass).

| Capability | Public evidence | What remains unverified |
|---|---|---|
| Talking-head cut | Raw/finished comparison | Algorithm and robustness |
| Take selection | Described as choosing the final good delivery of each line | Semantic accuracy across recordings |
| Dead-air removal and J-cuts | Explicit cut description | Boundaries, failure handling |
| Lip-sync check | Advertised before and after rendering | Measurement and tolerances |
| Word captions | Visible throughout demo reels | Alignment method, languages supported |
| Text behind speaker | Visible occlusion in demo | Model, temporal stability, hard edge cases |
| Per-frame subject matte | Layer example and effect demos | Throughput and model/license |
| Motion graphics | 67 public demonstration clips | Product source and customization API |
| Sound design | Advertised sound cues and voice mixing | Loudness target and audio QC method |
| Storyboard and feedback | Frame/beat board with comments | Whether UI is shipped, storage and edit mechanics |
| Reference editing | Video examples used to build style/effects | Accuracy and amount of manual intervention |
| Brand setup | Website, guide or design file; style-board approval | Font licensing and extraction accuracy |
| B-roll / real artifacts | Screen captures, videos, charts visibly composited | Automatic source discovery and licensing; a general stock-B-roll engine is not established |
| Walkthrough combination | Video card and background replacement demos | Arbitrary software recording synchronization |
| Style alternatives | Original, paper, depth, receipt examples | Generalization beyond the showcased take |
| Trial variations | Multiple trial posts and score comparison advertised | Instagram integration permissions and current API behavior |
| Carousels | Eight-slide example and reel-to-carousel workflow | Export formats and source implementation |
| Content planning | Separate seven-lesson bonus | A shipped autonomous Content OS is not established |
| Course assistant | Lesson-trained project advertised | Training method and access |
| Generative media | Optional external image/video/music tools discussed | Not an included free local generator |
| DM automation | Separate optional Manychat installation | Paid-service and platform requirements |

## Visual engineering observations

These observations describe visible behavior, not recovered implementation. The techniques proposed below are independent implementation directions. Exact easing functions, 3D scene geometry, source mattes and audio stems cannot be recovered from encoded video alone.

### Main reel

Reference: <https://justyn.ai/reel-kit/media/edit-v3.mp4>.

The subject stays visually dominant and the portrait layout reserves the upper area for large claims or UI props. The caption sits lower around the upper torso; this makes captions readable without covering the face. Large display text alternates between condensed-looking heavy sans and contrasting editorial serif. Green/cream/gold belong to the creator's brand and should not become Studio Linea's palette.

Observed beats:

| Approximate time | Observed composition | Independent implementation direction |
|---|---|---|
| 0–3 s | Kinetic hook, alternating typography, subject over a solid plate | Background plate + animated text + temporally coherent foreground alpha |
| 3–6 s | Application icons struck out | Licensed/self-drawn symbols, SVG path animation and bounded exits |
| 6–9 s | Prompt UI and color-change split | Typed UI plus dual graded video layers with a moving clipping boundary |
| 9–14 s | Editorial title and cascading media | Parameterized cover layout and staggered card transforms |
| 14–20 s | Drop-zone metaphor, bad-take stamps | Composited player UI and text/shape impact animation |
| 20–27 s | Recursive frame and moody treatment | Nested video planes; deterministic grade/grain/vignette |
| 27–36 s | Creator grid and storyboard/browser props | Tiled media, scroll viewport, scene-to-UI scale changes |
| 36–44 s | Large word above/behind head, oversized captions | Foreground matte sandwich, word-level timing, intentional safe areas |
| 44–54 s | Walkthrough prop, comment CTA and follow interaction | Screen-media insertion, typed local UI, end hold |

Many beat lengths are around 1–3 seconds; the end CTA is longer. The page's public storyboard metadata gives 22 beats for the approximately 54-second example. Use semantic changes to motivate effects, rather than choosing a different random overlay every second.

### Detailed effect samples

- **Kinetic hook**, <https://justyn.ai/reel-kit/media/fx/kinetic-hook.mp4>: 3.178-second clip at 30 fps. Temporal sample sequence shows a serif opening replaced by compact, heavy stacked text, then a more restrained serif payoff. The person remains over the typography. Independent recipe: word timestamps drive sequences; text enters with short vertical displacement or reveal; a consistent alpha foreground preserves occlusion. Do not equate a text overlay without masking with this effect.
- **Word stamp**, <https://justyn.ai/reel-kit/media/fx/serif-stamp.mp4>: 2.6 seconds. Large serif type occupies the space above/behind the head. Independent recipe: tracked headline bounds, per-letter reveal and optional strike path; subject alpha above title.
- **Orbit ring**, <https://justyn.ai/reel-kit/media/fx/orbit-ring.mp4>: 3.712 seconds. Letters form a turning horizontal ring; parts pass behind the head and parts in front. Independent recipe: project text glyphs around a 3D ellipse, split rear/front passes by depth and sandwich the alpha subject. A flat rotating circle will not match its spatial behavior.
- **Paper tear**, <https://justyn.ai/reel-kit/media/fx/paper-tear.mp4>: 1 second. A newsprint composition splits near the center; irregular edges peel apart and uncover the continuing talking head. Independent recipe: independently generated jagged masks, opposing translation/rotation, paper-edge shading, underneath footage. Clean rectangular wipes are materially simpler.
- **Rack focus**, <https://justyn.ai/reel-kit/media/fx/rack-focus.mp4>: 2.304 seconds. Subject separation is essential; blur only the background layer, retain crisp foreground detail and animate blur radius.
- **Finger draw**, <https://justyn.ai/reel-kit/media/fx/finger-draw.mp4>: 2.24 seconds. Matching the claimed behavior requires tracked fingertip positions or authored keyframes. A generic scribble path is not evidence of hand tracking.

### Modes and alternative styles

- [Hi-fi](https://justyn.ai/reel-kit/media/mode-hifi.mp4), 68.07 s: controlled talking head alternates with full-frame information graphics. Minimal chart drawing, cream/green fields, large numbers, labels, artifact cutouts and muted word captions. Implementation priority: readable data hierarchy and reliable scene timing.
- [Lo-fi](https://justyn.ai/reel-kit/media/mode-lofi.mp4), 61.33 s: handheld/selfie framing stays present; screenshot overlays and small labels appear around the speaker. Premium does not require covering every shot with a full-frame graphic.
- [Showcase](https://justyn.ai/reel-kit/media/mode-showcase.mp4), 56.67 s: effect-heavy reference for semantic per-line transformations; source clip is decoded and temporally sampled, not used as a template asset.
- [Paper](https://justyn.ai/reel-kit/media/edit-paper.mp4): physically framed covers, tape, paper surfaces, contact sheets; grain and rough edges communicate the medium.
- [Depth](https://justyn.ai/reel-kit/media/edit-depth.mp4): perspective cards, planes and recursive visual movement. Accurate occlusion and camera trajectory matter more than arbitrary CSS rotation.
- [Receipt](https://justyn.ai/reel-kit/media/edit-receipt.mp4): printable/UI forms with restrained frame props; maintains the same dialogue and core shot timing.

## Practical implications for our toolkit

1. Implement reliable media ingest → transcript → editable take plan → storyboard → composed render → probe/QC before adding decorative variants.
2. Preserve provenance: the 67 reference items are an inventory, not 67 completed local effects. Match each implementation explicitly to a technique and status.
3. An honest text-behind-person feature needs a real alpha mask or segmentation pipeline. A placeholder silhouette is only a synthetic demonstration.
4. Automatic good-take selection must distinguish last-take heuristics from semantic judgment. Retain a reviewable edit decision list and an override path.
5. Agent orchestration can assemble the plan from instructions, but deterministic rendering and schema validation should not depend on live paid APIs.
6. Do not claim superior visual quality without matched source footage, equivalent output size and a side-by-side review. Measurable differences such as local execution, reproducible manifests, provenance and provider-independent tooling can be demonstrated separately.

## Other public primary sources

- [Creator homepage](https://justyn.ai/) links the product and public profiles.
- [Newsletter archive](https://justyn.ai/newsletter) documents successive kit launches.
- [Issue 014](https://justyn.ai/newsletter/014) described an earlier 40-effect edition; this explains count differences in older references.
- [Issue 016](https://justyn.ai/newsletter/016) links member examples, including non-English examples. These testimonials are not a Dutch transcription benchmark.
- [Issue 018](https://justyn.ai/newsletter/018) describes the carousel workflow.
- Public profiles: [Instagram](https://instagram.com/justyn.ai), [TikTok](https://www.tiktok.com/@justyn.ai), [YouTube](https://www.youtube.com/@justynca). Direct playback unavailable through the audit's web fetch; site-hosted examples were inspected instead.

## Reproduction and limitations

An HTTP-successful media URL proves public availability at the check time, not permission to redistribute it or evidence that the product's underlying code is open source. Research downloads and contact sheets are temporary analysis materials outside the repository, under `/tmp/linea-reference-review`. No course purchase, checkout interaction, private repository access or access-control bypass was performed.

## Carousel sample inspection

All eight public sample slides were downloaded to temporary analysis storage and visually inspected. They are 720 × 960 JPEGs (3:4). Reference pattern: `https://justyn.ai/reel-kit/media/carousel/claude-editing-01.jpg` through `-08.jpg`. The sequence alternates footage-backed slides and nearly empty typographic plates, uses short script-derived statements, mixed serif/sans emphasis, dark green and one pale grid-texture slide, and ends with a follow CTA. This is a substantially more editorial layout than eight video screenshots with captions added. Independent implementation should support at least photo-led, text-led and contrasting divider layouts, with a brand-safe CTA; copying the sample slides is unnecessary.

## Audio measurement

The main public reel's decoded AAC track measures approximately **−14.25 LUFS integrated**, **−0.45 dBTP true peak**, and **3.20 LU loudness range** with FFmpeg's loudnorm input analysis. See [reference-audio-measurements.json](reference-audio-measurements.json). This establishes a concrete loudness reference for that file. It does not prove the kit's internal normalization target, isolate its sound-effect mix, or validate lipsync. A local output can be tested against an explicit loudness and peak policy instead of relying on the phrase “streaming loudness”.
