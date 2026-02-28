# Reorder nav: Practice Areas, After Accident, Insurance & Claims, Referrals, LA by Accident Type; remove PPC.
# Only for files where first dropdown after Home is "After Accident" (or "For Victims — After an Accident").
import re
import os

BASE = os.path.dirname(os.path.abspath(__file__))
EXCLUDE = {'index.html', 'settlements', 'legal', '_old-site-extract'}

def extract_nav_blocks(html):
    """Extract nav content between <nav ...> and </nav>."""
    match = re.search(r'<nav\s[^>]*id="primary-nav"[^>]*>(.*?)</nav>', html, re.DOTALL)
    if not match:
        return None, None, None
    nav_content = match.group(1)
    start = match.start(1)
    end = match.end(1)
    return nav_content, start, end

def get_dropdown_order(nav_content):
    """Find order of dropdown labels (span.nav-link--dropdown)."""
    labels = re.findall(r'<span\s+class="nav-link\s+nav-link--dropdown">([^<]+)</span>', nav_content)
    return labels

def extract_blocks(nav_content):
    """Split nav into: before first dropdown (Case Review + Home), then each <div class="nav-item">...</div>."""
    # Everything before first <div class="nav-item"> that contains a dropdown
    parts = []
    rest = nav_content
    # Pattern: <div class="nav-item"> ... </div> (nested div for dropdown)
    block_pat = re.compile(
        r'(\s*<div\s+class="nav-item">\s*<span\s+class="nav-link\s+nav-link--dropdown">.*?</span>\s*<div\s+class="nav-dropdown">.*?</div>\s*</div>)',
        re.DOTALL
    )
    # Get leading part (Case Review link + Home link)
    first_block = block_pat.search(rest)
    if not first_block:
        return None, []
    leading = rest[:first_block.start()].rstrip()
    blocks = []
    pos = 0
    while True:
        m = block_pat.search(rest, pos)
        if not m:
            break
        blocks.append(m.group(1))
        pos = m.end()
    return leading, blocks

def get_block_label(block):
    m = re.search(r'<span\s+class="nav-link\s+nav-link--dropdown">([^<]+)</span>', block)
    return m.group(1).strip() if m else None

def is_after_accident(label):
    return label and ('After Accident' in label or 'After an Accident' in label)

def is_insurance(label):
    return label and ('Insurance' in label and 'Claims' in label)

def is_practice_areas(label):
    return label and 'Practice Areas' in label

def is_referrals(label):
    return label and 'Referrals' in label

def is_la_type(label):
    return label and ('LA by Accident Type' in label or 'LA Lawyer by Accident Type' in label)

def is_ppc(label):
    return label and label.strip() == 'PPC'

ORDER = ['Practice Areas', 'After Accident', 'Insurance & Claims', 'Referrals', 'LA by Accident Type']

def main():
    changed = []
    for root, dirs, files in os.walk(BASE):
        if '_old-site-extract' in root:
            continue
        rel = os.path.relpath(root, BASE)
        if rel == '.':
            rel_parts = []
        else:
            rel_parts = rel.split(os.sep)
        if 'legal' in rel_parts or (rel == '.' and 'index.html' in files):
            # Skip root index (already correct) and legal (handled separately)
            if rel == '.' and 'index.html' in files:
                # Check root - skip if already Practice Areas first
                p = os.path.join(root, 'index.html')
                with open(p, 'r', encoding='utf-8') as f:
                    h = f.read()
                nc, _, _ = extract_nav_blocks(h)
                if nc:
                    labels = get_dropdown_order(nc)
                    if labels and is_practice_areas(labels[0]):
                        pass  # skip root
                    else:
                        pass  # root has different structure, skip
            continue
        if 'settlements' in rel_parts:
            continue
        if 'index.html' not in files:
            continue
        path = os.path.join(root, 'index.html')
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
        nav_content, start, end = extract_nav_blocks(html)
        if not nav_content:
            continue
        labels = get_dropdown_order(nav_content)
        if not labels:
            continue
        first_label = labels[0]
        if not is_after_accident(first_label):
            continue
        leading, blocks = extract_blocks(nav_content)
        if not blocks:
            continue
        by_label = {}
        for b in blocks:
            lbl = get_block_label(b)
            if lbl:
                by_label[lbl] = b
        # Build new order: keep first label that matches each key
        practice_block = None
        after_block = None
        insurance_block = None
        referrals_block = None
        la_block = None
        for lbl, b in by_label.items():
            if is_practice_areas(lbl):
                practice_block = b
            elif is_after_accident(lbl):
                after_block = b
            elif is_insurance(lbl):
                insurance_block = b
            elif is_referrals(lbl):
                referrals_block = b
            elif is_la_type(lbl):
                la_block = b
        new_blocks = []
        for key in ORDER:
            if key == 'Practice Areas' and practice_block:
                new_blocks.append(practice_block)
            elif key == 'After Accident' and after_block:
                new_blocks.append(after_block)
            elif key == 'Insurance & Claims' and insurance_block:
                new_blocks.append(insurance_block)
            elif key == 'Referrals' and referrals_block:
                new_blocks.append(referrals_block)
            elif key == 'LA by Accident Type' and la_block:
                new_blocks.append(la_block)
        # Normalize labels in output: use "After Accident", "Insurance & Claims", "Referrals", "LA by Accident Type"
        def normalize_block(blk, want_label):
            if not blk:
                return blk
            # Replace the span text with canonical label
            if want_label == 'After Accident':
                blk = re.sub(r'(<span\s+class="nav-link\s+nav-link--dropdown">)[^<]+(</span>)', r'\1After Accident\2', blk, count=1)
            elif want_label == 'Insurance & Claims':
                blk = re.sub(r'(<span\s+class="nav-link\s+nav-link--dropdown">)[^<]+(</span>)', r'\1Insurance &amp; Claims\2', blk, count=1)
            elif want_label == 'Referrals':
                blk = re.sub(r'(<span\s+class="nav-link\s+nav-link--dropdown">)[^<]+(</span>)', r'\1Referrals\2', blk, count=1)
            elif want_label == 'LA by Accident Type':
                blk = re.sub(r'(<span\s+class="nav-link\s+nav-link--dropdown">)[^<]+(</span>)', r'\1LA by Accident Type\2', blk, count=1)
            return blk
        new_blocks = [
            normalize_block(new_blocks[0], 'Practice Areas') if len(new_blocks) > 0 else None,
            normalize_block(new_blocks[1], 'After Accident') if len(new_blocks) > 1 else None,
            normalize_block(new_blocks[2], 'Insurance & Claims') if len(new_blocks) > 2 else None,
            normalize_block(new_blocks[3], 'Referrals') if len(new_blocks) > 3 else None,
            normalize_block(new_blocks[4], 'LA by Accident Type') if len(new_blocks) > 4 else None,
        ]
        new_blocks = [b for b in new_blocks if b]
        new_nav = leading + '\n' + '\n'.join(new_blocks) + '\n            '
        new_html = html[:start] + new_nav + html[end:]
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_html)
        changed.append(path)
    print('Nav reordered (and PPC removed) in:', len(changed), 'files')
    for p in changed[:5]:
        print(' ', p)
    if len(changed) > 5:
        print(' ... and', len(changed) - 5, 'more')

if __name__ == '__main__':
    main()
