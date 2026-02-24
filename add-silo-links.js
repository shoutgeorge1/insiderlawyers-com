const fs = require('fs');
const path = require('path');

const root = __dirname;
const edits = [
  {
    name: 'Practice Areas nav',
    old: '<a href="/personal-injury">Personal Injury</a>\n                        <a href="/personal-injury/auto-accidents">Auto Accidents</a>',
    new: '<a href="/personal-injury">Personal Injury</a>\n                        <a href="/motor-vehicle">Motor Vehicle (LA)</a>\n                        <a href="/premises-liability">Premises Liability (LA)</a>\n                        <a href="/personal-injury/auto-accidents">Auto Accidents</a>',
  },
  {
    name: 'Practice Areas footer',
    old: /<li><a href="\/personal-injury">Personal Injury<\/a><\/li><li><a href="\/personal-injury\/auto-accidents">Auto Accidents<\/a><\/li>(<li><a href=")/,
    new: '<li><a href="/personal-injury">Personal Injury</a></li><li><a href="/motor-vehicle">Motor Vehicle (LA)</a></li><li><a href="/premises-liability">Premises Liability (LA)</a></li><li><a href="/personal-injury/auto-accidents">Auto Accidents</a></li>$1',
  },
  {
    name: 'LA Lawyer nav',
    old: '<span class="nav-link nav-link--dropdown">LA Lawyer by Accident Type</span>\n                    <div class="nav-dropdown">\n                        <a href="/los-angeles-car-accident-lawyer">LA Car Accident Lawyer</a>',
    new: '<span class="nav-link nav-link--dropdown">LA Lawyer by Accident Type</span>\n                    <div class="nav-dropdown">\n                        <a href="/motor-vehicle">Motor Vehicle</a>\n                        <a href="/premises-liability">Premises Liability</a>\n                        <a href="/los-angeles-car-accident-lawyer">LA Car Accident Lawyer</a>',
  },
  {
    name: 'LA Lawyer footer',
    old: '<h4>LA Lawyer by Accident Type</h4>\n          <ul>\n            <li><a href="/los-angeles-car-accident-lawyer">LA Car Accident Lawyer</a></li>',
    new: '<h4>LA Lawyer by Accident Type</h4>\n          <ul>\n            <li><a href="/motor-vehicle">Motor Vehicle</a></li><li><a href="/premises-liability">Premises Liability</a></li><li><a href="/los-angeles-car-accident-lawyer">LA Car Accident Lawyer</a></li>',
  },
];

function walkDir(dir, fileList = []) {
  const files = fs.readdirSync(dir);
  for (const f of files) {
    const p = path.join(dir, f);
    if (fs.statSync(p).isDirectory()) {
      if (f !== 'motor-vehicle' && f !== 'premises-liability') walkDir(p, fileList);
    } else if (f === 'index.html') fileList.push(p);
  }
  return fileList;
}

const files = walkDir(root);
let navCount = 0, footerCount = 0, laNavCount = 0, laFooterCount = 0;
for (const file of files) {
  let content = fs.readFileSync(file, 'utf8');
  if (content.includes('motor-vehicle">Motor Vehicle (LA)</a>')) continue; // already done
  let changed = false;
  if (content.includes(edits[0].old)) {
    content = content.split(edits[0].old).join(edits[0].new);
    navCount++;
    changed = true;
  }
  if (edits[1].old.test(content)) {
    content = content.replace(edits[1].old, edits[1].new);
    footerCount++;
    changed = true;
  }
  if (content.includes('LA Lawyer by Accident Type') && content.includes(edits[2].old)) {
    content = content.split(edits[2].old).join(edits[2].new);
    laNavCount++;
    changed = true;
  }
  if (content.includes('LA Lawyer by Accident Type') && content.includes(edits[3].old)) {
    content = content.split(edits[3].old).join(edits[3].new);
    laFooterCount++;
    changed = true;
  }
  if (changed) fs.writeFileSync(file, content, 'utf8');
}
console.log('Practice Areas nav:', navCount, '| footer:', footerCount, '| LA Lawyer nav:', laNavCount, '| LA Lawyer footer:', laFooterCount);
