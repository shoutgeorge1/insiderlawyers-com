/**
 * Convert PNG images to WebP for performance.
 * Run: npm install && node scripts/convert-to-webp.js
 * Then update HTML references from .png to .webp
 */
const fs = require('fs');
const path = require('path');

async function convert() {
  let sharp;
  try {
    sharp = require('sharp');
  } catch (e) {
    console.error('Run: npm install sharp');
    process.exit(1);
  }

  const root = path.join(__dirname, '..');
  const images = [
    { src: 'images/hero/google-logo.png', out: 'images/hero/google-logo.webp', maxWidth: 120 },
    { src: 'images/hero/yelp-logo.png', out: 'images/hero/yelp-logo.webp' },
    { src: 'images/hero/yelp-logo-mobile.png', out: 'images/hero/yelp-logo-mobile.webp' },
    { src: 'images/team-attorneys.png', out: 'images/team-attorneys.webp', maxWidth: 900 },
    { src: 'images/highlights/trial-strategy.png', out: 'images/highlights/trial-strategy.webp', maxWidth: 256 },
    { src: 'images/highlights/medical-network.png', out: 'images/highlights/medical-network.webp', maxWidth: 256 },
    { src: 'images/highlights/insurance-defense.png', out: 'images/highlights/insurance-defense.webp', maxWidth: 256 },
    { src: 'images/highlights/property-damage.png', out: 'images/highlights/property-damage.webp', maxWidth: 256 },
    { src: 'images/highlights/lost-income.png', out: 'images/highlights/lost-income.webp', maxWidth: 256 },
    { src: 'images/highlights/local-attorney.png', out: 'images/highlights/local-attorney.webp', maxWidth: 256 },
    { src: 'images/highlights/no-fee.png', out: 'images/highlights/no-fee.webp', maxWidth: 256 },
    { src: 'images/highlights/clock-247.png', out: 'images/highlights/clock-247.webp', maxWidth: 256 },
    { src: 'images/injuries/neck.png', out: 'images/injuries/neck.webp', maxWidth: 280 },
    { src: 'images/injuries/broken-bone.png', out: 'images/injuries/broken-bone.webp', maxWidth: 280 },
    { src: 'images/injuries/catastrophic.png', out: 'images/injuries/catastrophic.webp', maxWidth: 280 },
    { src: 'images/injuries/spine.png', out: 'images/injuries/spine.webp', maxWidth: 280 },
    { src: 'images/injuries/brain.png', out: 'images/injuries/brain.webp', maxWidth: 280 },
    { src: 'images/hero/ktown-bg.jpg', out: 'images/hero/ktown-bg.webp' },
  ];

  for (const img of images) {
    const srcPath = path.join(root, img.src);
    const outPath = path.join(root, img.out);
    if (!fs.existsSync(srcPath)) {
      console.warn('Skip (not found):', img.src);
      continue;
    }
    let pipeline = sharp(srcPath);
    if (img.maxWidth) {
      pipeline = pipeline.resize(img.maxWidth, null, { withoutEnlargement: true });
    }
    const isJpg = img.src.toLowerCase().endsWith('.jpg') || img.src.toLowerCase().endsWith('.jpeg');
    await pipeline.webp({ quality: isJpg ? 80 : 85 }).toFile(outPath);
    console.log('Created:', img.out);
  }
  console.log('Done. Update HTML references from .png to .webp for these images.');
}

convert().catch(e => {
  console.error(e);
  process.exit(1);
});
