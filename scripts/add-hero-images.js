/**
 * Add hero images to pages per image_mapping.json.
 * Reads mapping from the images project, copies images already done separately,
 * and injects <div class="page-hero-img"><img src="/images/..." alt="..."></div> after first </h1> in each page.
 * Skips: los-angeles-car-accident-lawyer (PPC page).
 */
const fs = require('fs');
const path = require('path');

const IMAGE_MAPPING_PATH = 'C:\\Users\\georgea\\.cursor\\projects\\c-Users-georgea-insiderlawyer-com-images\\image_mapping.json';
const LP_ROOT = path.join(__dirname, '..');
const SKIP_PATHS = new Set(['los-angeles-car-accident-lawyer']);

function getPathFromUrl(url) {
  const base = 'https://www.insiderlawyers.com';
  if (!url || url === base || url === base + '/') return '';
  if (url === base + '/index.html') return '';
  try {
    const u = new URL(url);
    let p = u.pathname.replace(/^\/|\/$/g, '');
    if (p === 'index.html') return '';
    return p;
  } catch (e) { return ''; }
}

function getIndexPath(pathFromUrl) {
  if (!pathFromUrl) return path.join(LP_ROOT, 'index.html');
  return path.join(LP_ROOT, pathFromUrl.replace(/\//g, path.sep), 'index.html');
}

const raw = fs.readFileSync(IMAGE_MAPPING_PATH, 'utf8');
const map = JSON.parse(raw);
const byPath = {};
for (const img of map.images) {
  const p = getPathFromUrl(img.url);
  if (SKIP_PATHS.has(p)) continue;
  byPath[p] = { filename: img.suggested_filename, alt: img.alt_text };
}

let updated = 0;
let skipped = 0;
for (const [pathKey, { filename, alt }] of Object.entries(byPath)) {
  const indexPath = getIndexPath(pathKey);
  if (!fs.existsSync(indexPath)) {
    skipped++;
    continue;
  }
  let html = fs.readFileSync(indexPath, 'utf8');
  const heroBlock = `<div class="page-hero-img"><img src="/images/${filename}" alt="${alt.replace(/"/g, '&quot;')}" width="800" height="450" loading="lazy"></div>`;
  // Insert after first </h1> - avoid replacing in nav/header by targeting content area
  const re = /(<\/h1>\s*)(\n\s*)(<p class="lead-text"|<\/nav>\s*\n\s*<h1>|<\/div>\s*\n\s*<h1>|<div class="silo-hero-img"|<p class="lead-text"|<\/h1>\s*\n\s*<div)/;
  const alreadyHas = html.includes('page-hero-img') || html.includes('silo-hero-img');
  if (alreadyHas && html.includes('/images/' + filename)) continue;
  if (alreadyHas && pathKey !== '' && !pathKey.startsWith('motor-vehicle') && !pathKey.startsWith('premises-liability')) {
    // Replace existing hero img src if we have a mapped image
    const imgRe = new RegExp(`(<div class="(?:page-hero-img|silo-hero-img)"[^>]*>\\s*<img[^>]+src=")[^"]+(")[^>]*>`, 'i');
    if (imgRe.test(html)) {
      html = html.replace(imgRe, `$1/images/${filename}$2 alt="${alt.replace(/"/g, '&quot;')}" width="800" height="450" loading="lazy">`);
      fs.writeFileSync(indexPath, html);
      updated++;
    }
    continue;
  }
  if (alreadyHas) { skipped++; continue; }
  const match = html.match(/(<\/h1>\s*)(\r?\n)(\s*)(<p |<div class="cta-row"|<div class="silo-|<ul |<h2 |<p>)/m);
  if (match) {
    const insert = match[1] + match[2] + match[3] + heroBlock + match[2] + match[3];
    html = html.replace(/(<\/h1>\s*)(\r?\n)(\s*)(<p |<div class="cta-row"|<div class="silo-|<ul |<h2 |<p>)/m, insert);
    fs.writeFileSync(indexPath, html);
    updated++;
  } else {
    const simple = html.replace(/(<\/h1>\s*)(\r?\n)/, '$1$2' + heroBlock + '$2');
    if (simple !== html) {
      fs.writeFileSync(indexPath, simple);
      updated++;
    } else skipped++;
  }
}
console.log('Updated', updated, 'pages. Skipped', skipped);
console.log('Ensure .page-hero-img { margin:1rem 0; border-radius:12px; overflow:hidden; max-height:320px; } .page-hero-img img { width:100%; height:auto; display:block; } is in main.css or per-page style.');
