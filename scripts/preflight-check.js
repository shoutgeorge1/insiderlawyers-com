const fs = require("fs");
const path = require("path");

const ROOT_DIR = path.resolve(__dirname, "..");
const REQUIRED_CANONICAL_ROOT = "https://www.insiderlawyers.com/";
const CANONICAL_DOMAIN = "https://www.insiderlawyers.com/";
const REQUIRED_PHONE = "tel:844-467-4335";
const REQUIRED_FORM_ACTION = "https://formsubmit.co/ial.leads.2024@gmail.com";
const REQUIRED_GTM = "GTM-WS8XT5FC";
const REQUIRED_HOME_SNIPPETS = [
  'class="home-ppc"',
  'id="case-evaluation"',
  'id="case-evaluation-form"',
  'id="case-results"',
  'id="our-attorneys"',
  'id="footer-contact"',
  'class="tap-to-call-bar"',
  "Start My Free Case Review",
  "3435 Wilshire Blvd Suite 1620, Los Angeles, CA 90010"
];

const ignoredDirs = new Set([".git", "node_modules"]);
const htmlFiles = [];
const failures = [];

function walk(dirPath) {
  const entries = fs.readdirSync(dirPath, { withFileTypes: true });
  for (const entry of entries) {
    const absolutePath = path.join(dirPath, entry.name);
    if (entry.isDirectory()) {
      if (!ignoredDirs.has(entry.name)) {
        walk(absolutePath);
      }
      continue;
    }
    if (entry.isFile() && entry.name.toLowerCase().endsWith(".html")) {
      htmlFiles.push(absolutePath);
    }
  }
}

function assertCondition(condition, message) {
  if (!condition) failures.push(message);
}

function run() {
  walk(ROOT_DIR);
  assertCondition(htmlFiles.length > 0, "No HTML files found in project.");

  for (const filePath of htmlFiles) {
    const relPath = path.relative(ROOT_DIR, filePath).replace(/\\/g, "/");
    const content = fs.readFileSync(filePath, "utf8");

    const canonicalMatch = content.match(/<link\s+rel="canonical"\s+href="([^"]+)"/i);
    assertCondition(!!canonicalMatch, `[${relPath}] Missing canonical tag.`);

    if (canonicalMatch) {
      const canonical = canonicalMatch[1].trim();
      assertCondition(
        canonical.startsWith(CANONICAL_DOMAIN),
        `[${relPath}] Canonical must start with ${CANONICAL_DOMAIN}, found: ${canonical}`
      );
    }

    if (relPath === "index.html") {
      assertCondition(
        !!canonicalMatch && canonicalMatch[1].trim() === REQUIRED_CANONICAL_ROOT,
        `[index.html] Canonical must be exactly ${REQUIRED_CANONICAL_ROOT}`
      );
      assertCondition(
        content.includes(REQUIRED_PHONE),
        `[index.html] Missing required call link ${REQUIRED_PHONE}`
      );
      assertCondition(
        content.includes(REQUIRED_GTM),
        `[index.html] Missing required GTM container ${REQUIRED_GTM}`
      );
      for (const snippet of REQUIRED_HOME_SNIPPETS) {
        assertCondition(
          content.includes(snippet),
          `[index.html] Homepage lock check failed. Missing required snippet: ${snippet}`
        );
      }
      const phoneLinkCount = (content.match(/href="tel:844-467-4335"/g) || []).length;
      assertCondition(
        phoneLinkCount >= 4,
        `[index.html] Expected at least 4 primary phone links, found ${phoneLinkCount}`
      );
    }

    if (content.includes('id="case-evaluation-form"')) {
      const formActionMatch = content.match(/<form[^>]*action="([^"]+)"/i);
      assertCondition(
        !!formActionMatch && formActionMatch[1].trim() === REQUIRED_FORM_ACTION,
        `[${relPath}] Form action must be ${REQUIRED_FORM_ACTION}`
      );
      assertCondition(
        /name="_captcha"\s+value="false"/i.test(content),
        `[${relPath}] Form is missing hidden _captcha=false field.`
      );
      assertCondition(
        /id="form-next-url"/i.test(content),
        `[${relPath}] Form is missing hidden _next target (id=form-next-url).`
      );
    }
  }

  if (failures.length > 0) {
    console.error("\nPreflight checks failed:\n");
    for (const failure of failures) {
      console.error(`- ${failure}`);
    }
    process.exit(1);
  }

  console.log(`Preflight checks passed for ${htmlFiles.length} HTML files.`);
}

run();
