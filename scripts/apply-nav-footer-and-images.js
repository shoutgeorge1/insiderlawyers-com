/**
 * 1. Copy nav and footer from insurance-company-playbook to all other index.html (except root index).
 * 2. Remove asset-preview-block / infographic sections; replace with one content image.
 * 3. Standardize CTA buttons to "Free Case Review" and "Call 844-467-4335".
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');
const TEMPLATE = path.join(ROOT, 'insurance-company-playbook', 'index.html');
const CONTENT_IMG = '<figure class="content-hero-img" style="margin:24px 0 32px;border-radius:12px;overflow:hidden;box-shadow:0 8px 24px rgba(1,54,108,.12);"><img src="https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1200&amp;q=80" alt="Legal and injury claim guidance" style="width:100%;height:auto;display:block;"></figure>';

function getAllIndexFiles() {
  const list = [];
  function walk(dir) {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const e of entries) {
      const full = path.join(dir, e.name);
      if (e.isDirectory() && !['scripts', 'docs', 'styles', 'images', 'node_modules'].includes(e.name)) {
        walk(full);
      } else if (e.isFile() && e.name === 'index.html') {
        const rel = path.relative(ROOT, full);
        if (rel !== 'index.html') list.push(full);
      }
    }
  }
  walk(ROOT);
  return list;
}

function extractBlock(html, startMark, endMark) {
  const start = html.indexOf(startMark);
  if (start === -1) return null;
  const end = html.indexOf(endMark, start);
  if (end === -1) return null;
  return html.slice(start, end + endMark.length);
}

function main() {
  const templateHtml = fs.readFileSync(TEMPLATE, 'utf8');
  const navStart = '<nav class="header-nav-row" id="primary-nav" aria-label="Primary">';
  const navEnd = '</nav>';
  const footerStart = '<footer class="site-footer"';
  const footerEnd = '</footer>';

  const newNav = extractBlock(templateHtml, navStart, navEnd);
  const newFooter = extractBlock(templateHtml, footerStart, footerEnd);
  if (!newNav || !newFooter) {
    console.error('Could not extract nav or footer from template');
    process.exit(1);
  }

  const files = getAllIndexFiles();
  let navReplaced = 0, footerReplaced = 0, infographicRemoved = 0, imageAdded = 0, buttonFixed = 0;

  for (const file of files) {
    if (file === TEMPLATE) continue;
    let html = fs.readFileSync(file, 'utf8');
    let changed = false;

    const oldNav = extractBlock(html, navStart, navEnd);
    if (oldNav && oldNav !== newNav) {
      html = html.replace(oldNav, newNav);
      changed = true;
      navReplaced++;
    }

    const oldFooter = extractBlock(html, footerStart, footerEnd);
    if (oldFooter && oldFooter !== newFooter) {
      html = html.replace(oldFooter, newFooter);
      changed = true;
      footerReplaced++;
    }

    // Remove infographic: section and div asset-preview-block
    const sectionRegex = /<section class="asset-preview-block"[^>]*>[\s\S]*?<\/section>\s*/g;
    const divRegex = /<div class="asset-preview-block"[^>]*>[\s\S]*?<\/div>\s*/g;
    if (sectionRegex.test(html)) {
      html = html.replace(sectionRegex, '');
      infographicRemoved++;
      changed = true;
    }
    if (html.indexOf('asset-preview-block') !== -1) {
      const before = html;
      html = html.replace(divRegex, '');
      if (html !== before) {
        infographicRemoved++;
        changed = true;
      }
    }

    // Add one content image after first paragraph in content-body if none yet
    if (html.indexOf('content-hero-img') === -1 && html.indexOf('<main>') !== -1 && html.indexOf('<div class="content-body">') !== -1) {
      const bodyStart = html.indexOf('<div class="content-body">');
      const firstPClose = html.indexOf('</p>', bodyStart);
      if (firstPClose !== -1) {
        const insertPoint = firstPClose + 4;
        html = html.slice(0, insertPoint) + '\n                ' + CONTENT_IMG + '\n                ' + html.slice(insertPoint);
        imageAdded++;
        changed = true;
      }
    }

    // Standardize primary CTA button text
    if (html.indexOf('Get My Free Case Review') !== -1) {
      html = html.replace(/Get My Free Case Review/g, 'Free Case Review');
      buttonFixed++;
      changed = true;
    }

    if (changed) fs.writeFileSync(file, html, 'utf8');
  }

  console.log('Nav replaced:', navReplaced);
  console.log('Footer replaced:', footerReplaced);
  console.log('Infographic blocks removed:', infographicRemoved);
  console.log('Content image added:', imageAdded);
  console.log('Buttons fixed:', buttonFixed);
  console.log('Total files processed:', files.length);
}

main();
