// Adapted from tecnomanu/motion-video-styles engine/common.js (MIT).
// Copyright (c) 2026 tecnomanu. See LICENSE and provenance.json beside this file.
// This dependency-free extraction keeps source timing/easing; no GSAP or DOM required.
const normalize = value => String(value).toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]/g, '');
export const clamp01 = value => Math.max(0, Math.min(1, value));
export const easeOutCubic = value => 1 - Math.pow(1 - clamp01(value), 3);
export function seededRandom(seed) {
  const x = Math.sin(seed * 12.9898 + 78.233) * 43758.5453;
  return x - Math.floor(x);
}
export function cueWord(segment, match, occurrence = 0) {
  let count = 0;
  for (const word of segment.words) {
    if (normalize(word.w).includes(normalize(match)) && count++ === occurrence) return word.t;
  }
  return segment.start;
}
export function typeText(text, time, start = 0, charactersPerSecond = 28) {
  return text.slice(0, Math.max(0, Math.min(text.length, Math.floor((time - start) * charactersPerSecond))));
}
export function countValue(target, time, start = 0, duration = 1) {
  return target * easeOutCubic(duration > 0 ? (time - start) / duration : Number(time >= start));
}
export function captionGroups(segments, maxWords = 4) {
  if (!Number.isInteger(maxWords) || maxWords < 1) throw new Error('maxWords must be a positive integer');
  const groups = [];
  for (const segment of segments) {
    let current = [];
    segment.words.forEach((word, i) => {
      current.push(word);
      if (/[.,:;?!]$/.test(word.w) || current.length >= maxWords || i === segment.words.length - 1) {
        groups.push({segment, words: current}); current = [];
      }
    });
  }
  return groups.map((group, i) => ({...group,
    start: group.words[0].t - .06,
    end: groups[i + 1]?.segment === group.segment ? groups[i + 1].words[0].t - .06 : group.segment.end + .25,
  }));
}
