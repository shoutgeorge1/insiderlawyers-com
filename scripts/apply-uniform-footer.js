/**
 * Apply the same footer as los-angeles-car-accident-lawyer to all pages that don't have it.
 * Run from repo root: node scripts/apply-uniform-footer.js
 */
const fs = require('fs');
const path = require('path');

const ROOT = path.join(__dirname, '..');

const CANONICAL_FOOTER = `  <footer class="site-footer" id="footer-contact">
    <div class="container">
      <div class="footer-content">
        <div class="footer-section">
          <h3>Insider Accident Lawyers</h3>
          <p>Los Angeles personal injury attorneys. Real trial lawyers, real results.</p>
          <p><a href="tel:844-467-4335" class="footer__phone" data-callrail-phone="844-467-4335">844-467-4335</a></p>
          <p>Available 24/7 · Hablamos Espanol</p>
          <p>No Fee Unless We Win</p>
          <p>3435 Wilshire Blvd Suite 1620, Los Angeles, CA 90010</p>
        </div>
        <div class="footer-section">
          <h4>Firm</h4>
          <ul>
            <li><a href="/">Home</a></li><li><a href="/#case-evaluation">Free Case Review</a></li><li><a href="/#case-results">Case Results</a></li><li><a href="/#our-attorneys">Our Attorneys</a></li><li><a href="/settlements">Settlements</a></li>
          </ul>
        </div>
        <div class="footer-section">
          <h4>Core Practice Areas</h4>
          <ul>
            <li><a href="/personal-injury">Personal Injury</a></li><li><a href="/personal-injury/auto-accidents">Auto Accidents</a></li><li><a href="/personal-injury/truck-accidents">Truck Accidents</a></li><li><a href="/personal-injury/brain-injuries">Brain Injuries</a></li><li><a href="/personal-injury/wrongful-death">Wrongful Death</a></li>
          </ul>
        </div>
        <div class="footer-section">
          <h4>Additional Practice Areas</h4>
          <ul>
            <li><a href="/personal-injury/animal-attacks">Animal Attacks</a></li><li><a href="/personal-injury/bicycle-accidents">Bicycle Accidents</a></li><li><a href="/personal-injury/motorcycle-accidents">Motorcycle Accidents</a></li><li><a href="/personal-injury/pedestrian-accidents">Pedestrian Accidents</a></li><li><a href="/personal-injury/premises-liability">Premises Liability</a></li><li><a href="/personal-injury/product-liability">Product Liability</a></li><li><a href="/personal-injury/slip-and-fall">Slip and Fall</a></li><li><a href="/personal-injury/spine-injuries">Spine Injuries</a></li><li><a href="/personal-injury/catastrophic-injuries">Catastrophic Injuries</a></li><li><a href="/personal-injury/uber-and-lyft-accidents">Uber and Lyft Accidents</a></li>
          </ul>
        </div>
        <div class="footer-section">
          <h4>Claim Playbooks</h4>
          <ul>
            <li><a href="/insurance-company-playbook">Insurance Company Playbook</a></li><li><a href="/insurance-company-tactics-personal-injury">Insurance Company Tactics</a></li><li><a href="/adjuster-claim-valuation">Adjuster Claim Valuation</a></li><li><a href="/proving-claim-value">Proving Claim Value</a></li><li><a href="/demand-letter-negotiation">Demand Letter Negotiation</a></li><li><a href="/lowball-offer-response">Lowball Offer Response</a></li><li><a href="/major-car-accident">Major Car Accident Guide</a></li><li><a href="/california-car-accident-lawyer">California Car Accident Guide</a></li><li><a href="/brain-injury">Brain Injury Compensation Guide</a></li><li><a href="/personal-injury-court">Personal Injury Court</a></li><li><a href="/post-dog-bite">Post Dog Bite</a></li><li><a href="/pedestrian-right-of-way">Pedestrian Right of Way</a></li><li><a href="/uber-or-lyft-accident">Uber or Lyft Accident</a></li><li><a href="/injuries-truck-accidents">Injuries in Truck Accidents</a></li><li><a href="/motorcycle-accident-case">Motorcycle Accident Case</a></li>
          </ul>
        </div>
        <div class="footer-section">
          <h4>Injury &amp; Accident Types</h4>
          <ul>
            <li><a href="/los-angeles-car-accident-lawyer">Los Angeles Car Accident Lawyer</a></li><li><a href="/los-angeles-auto-accident-lawyer">Los Angeles Auto Accident Lawyer</a></li><li><a href="/los-angeles-car-crash-lawyer">Los Angeles Car Crash Lawyer</a></li><li><a href="/car-accident-lawyer-near-me-los-angeles">Car Accident Lawyer Near Me Los Angeles</a></li><li><a href="/los-angeles-truck-accident-lawyer">Los Angeles Truck Accident Lawyer</a></li><li><a href="/los-angeles-motorcycle-accident-lawyer">Los Angeles Motorcycle Accident Lawyer</a></li><li><a href="/los-angeles-pedestrian-accident-lawyer">Los Angeles Pedestrian Accident Lawyer</a></li><li><a href="/los-angeles-bicycle-accident-lawyer">Los Angeles Bicycle Accident Lawyer</a></li><li><a href="/los-angeles-wrongful-death-lawyer">Los Angeles Wrongful Death Lawyer</a></li><li><a href="/los-angeles-brain-injury-lawyer">Los Angeles Brain Injury Lawyer</a></li><li><a href="/los-angeles-spine-injury-lawyer">Los Angeles Spine Injury Lawyer</a></li><li><a href="/los-angeles-catastrophic-injury-lawyer">Los Angeles Catastrophic Injury Lawyer</a></li><li><a href="/los-angeles-premises-liability-lawyer">Los Angeles Premises Liability Lawyer</a></li><li><a href="/los-angeles-slip-and-fall-lawyer">Los Angeles Slip and Fall Lawyer</a></li><li><a href="/los-angeles-product-liability-lawyer">Los Angeles Product Liability Lawyer</a></li><li><a href="/los-angeles-uber-lyft-accident-lawyer">Los Angeles Uber Lyft Accident Lawyer</a></li><li><a href="/hit-and-run-accident-lawyer-los-angeles">Hit and Run Accident Lawyer Los Angeles</a></li><li><a href="/rear-end-accident-lawyer-los-angeles">Rear-End Accident Lawyer Los Angeles</a></li><li><a href="/t-bone-accident-lawyer-los-angeles">T-Bone Accident Lawyer Los Angeles</a></li><li><a href="/parking-lot-accident-lawyer-los-angeles">Parking Lot Accident Lawyer Los Angeles</a></li><li><a href="/pedestrian-accident-lawyer-los-angeles">Pedestrian Accident Lawyer Los Angeles</a></li><li><a href="/uber-accident-lawyer-los-angeles">Uber Accident Lawyer Los Angeles</a></li><li><a href="/uninsured-driver-accident-lawyer-los-angeles">Uninsured Driver Accident Lawyer Los Angeles</a></li>
          </ul>
        </div>
        <div class="footer-section">
          <h4>Trucking Guides</h4>
          <ul>
            <li><a href="/personal-injury/truck-accidents">Truck Accidents</a></li><li><a href="/truck-accident-legal-rights">Truck Accident Legal Rights</a></li><li><a href="/proving-truck-accident-case">Proving a Truck Accident Case</a></li><li><a href="/injuries-truck-accidents">Injuries in Truck Accidents</a></li><li><a href="/personal-injury/truck-accidents/fmcsa-hours-of-service">FMCSA Hours-of-Service</a></li><li><a href="/personal-injury/truck-accidents/truck-accident-evidence">Truck Evidence Preservation</a></li><li><a href="/personal-injury/truck-accidents/truck-accident-liability">Truck Liability Guide</a></li>
          </ul>
        </div>
        <div class="footer-section">
          <h4>California Guides</h4>
          <ul>
            <li><a href="/california-comparative-negligence-personal-injury">California Comparative Negligence</a></li><li><a href="/evidence-preservation-car-accident-california">Evidence Preservation California</a></li><li><a href="/herniated-disc-car-accident-settlement-california">Herniated Disc Settlement California</a></li><li><a href="/how-long-does-a-car-accident-settlement-take-california">How Long Settlement Takes</a></li><li><a href="/how-much-is-my-car-accident-worth-california">How Much Is My Accident Worth</a></li><li><a href="/personal-injury-claim-process-california">Personal Injury Claim Process California</a></li><li><a href="/should-i-accept-insurance-first-offer">Should I Accept First Offer</a></li><li><a href="/soft-tissue-injury-settlement-california">Soft Tissue Settlement California</a></li><li><a href="/spinal-fusion-surgery-car-accident-settlement-california">Spinal Fusion Settlement California</a></li><li><a href="/traumatic-brain-injury-car-accident-settlement-california">TBI Settlement California</a></li>
          </ul>
        </div>
        <div class="footer-section">
          <h4>Litigation Referrals</h4>
          <ul>
            <li><a href="/attorney-referrals">Attorney Referrals</a></li><li><a href="/lit-referral-core">Litigation Referral Core</a></li><li><a href="/lit-referral-process">Litigation Referral Process</a></li><li><a href="/lit-referral-criteria">Referral Criteria</a></li><li><a href="/lit-referral-economics">Referral Economics</a></li><li><a href="/lit-referral-trial-ready-cocounsel">Trial-Ready Co-Counsel</a></li><li><a href="/lit-referral-catastrophic-cases">Catastrophic Injury Referrals</a></li><li><a href="/lit-referral-truck-litigation">Truck Litigation Referrals</a></li><li><a href="/lit-referral-brain-injury">Brain Injury Referrals</a></li><li><a href="/lit-referral-wrongful-death">Wrongful Death Referrals</a></li><li><a href="/lit-referral-coverage-disputes">Coverage Dispute Referrals</a></li>
          </ul>
        </div>
        <div class="footer-section">
          <h4>Legal</h4>
          <ul>
            <li><a href="/legal/results-disclaimer">Results Disclaimer</a></li><li><a href="/legal/disclaimer">Legal Disclaimer</a></li><li><a href="/legal/terms">Terms of Use</a></li><li><a href="/legal/accessibility">Accessibility Statement</a></li><li><a href="https://www.insideraccidentlawyers.com/privacy-policy">Privacy Policy</a></li>
          </ul>
        </div>
      </div>
      <div class="footer__disclaimer">
        <p id="footer-verdicts-note"><strong>*</strong> Past verdicts and settlements obtained by attorneys at Insider Accident Lawyers and prior firms. Results vary; no guarantee of similar outcome. Each case is unique.</p>
        <p>Attorney advertising. Prior results do not guarantee a similar outcome. This site does not provide legal advice; viewing does not create an attorney-client relationship.</p>
        <p>Countrywide Trial Lawyers A Professional Law Corporation DBA Insider Accident Lawyers. California Entity #4851715. 3435 Wilshire Blvd Suite 1620, Los Angeles, CA 90010. <a href="https://www.insideraccidentlawyers.com/privacy-policy">Privacy Policy</a></p>
        <p class="footer__copyright">© 2026 Insider Accident Lawyers. All Rights Reserved.</p>
      </div>
    </div>
  </footer>`;

const FOOTER_CSS_LINK = '<link rel="stylesheet" href="/styles/footer.css">';

function walkDir(dir, fileList = []) {
  const files = fs.readdirSync(dir);
  for (const file of files) {
    const full = path.join(dir, file);
    if (fs.statSync(full).isDirectory()) {
      if (file !== 'styles' && file !== 'scripts' && file !== 'images' && file !== 'node_modules') {
        walkDir(full, fileList);
      }
    } else if (file === 'index.html') {
      fileList.push(full);
    }
  }
  return fileList;
}

function hasUniformFooter(html) {
  return html.includes('footer__disclaimer') && html.includes('Injury &amp; Accident Types</h4>') && html.includes('California Guides</h4>');
}

function hasMainCss(html) {
  return html.includes('main.css');
}

const footerRegex = /<footer[\s\S]*?<\/footer>/i;

let updated = 0;
let skipped = 0;
const indexFiles = walkDir(ROOT);

for (const filePath of indexFiles) {
  let html = fs.readFileSync(filePath, 'utf8');
  if (hasUniformFooter(html)) {
    skipped++;
    continue;
  }
  const match = html.match(footerRegex);
  if (!match) {
    console.warn('No footer found:', filePath);
    continue;
  }
  html = html.replace(footerRegex, CANONICAL_FOOTER);
  if (!hasMainCss(html)) {
    html = html.replace('</head>', FOOTER_CSS_LINK + '\n</head>');
  }
  fs.writeFileSync(filePath, html, 'utf8');
  updated++;
  console.log('Updated:', path.relative(ROOT, filePath));
}

console.log('\nDone. Updated', updated, 'files, skipped', skipped, '(already uniform).');
