# add Motor Vehicle & Premises Liability to nav and footer
import os
import re

root = os.path.dirname(os.path.abspath(__file__))

def walk(dir, out=None):
    out = out or []
    for name in os.listdir(dir):
        path = os.path.join(dir, name)
        if os.path.isdir(path):
            if name not in ('motor-vehicle', 'premises-liability'):
                walk(path, out)
        elif name == 'index.html':
            out.append(path)
    return out

nav_practice_old = '<a href="/personal-injury">Personal Injury</a>\n                        <a href="/personal-injury/auto-accidents">Auto Accidents</a>'
nav_practice_new = '''<a href="/personal-injury">Personal Injury</a>
                        <a href="/motor-vehicle">Motor Vehicle (LA)</a>
                        <a href="/premises-liability">Premises Liability (LA)</a>
                        <a href="/personal-injury/auto-accidents">Auto Accidents</a>'''

footer_practice_old = '<li><a href="/personal-injury">Personal Injury</a></li><li><a href="/personal-injury/auto-accidents">Auto Accidents</a></li>'
footer_practice_new = '<li><a href="/personal-injury">Personal Injury</a></li><li><a href="/motor-vehicle">Motor Vehicle (LA)</a></li><li><a href="/premises-liability">Premises Liability (LA)</a></li><li><a href="/personal-injury/auto-accidents">Auto Accidents</a></li>'

la_nav_old = '''<span class="nav-link nav-link--dropdown">LA Lawyer by Accident Type</span>
                    <div class="nav-dropdown">
                        <a href="/los-angeles-car-accident-lawyer">LA Car Accident Lawyer</a>'''
la_nav_new = '''<span class="nav-link nav-link--dropdown">LA Lawyer by Accident Type</span>
                    <div class="nav-dropdown">
                        <a href="/motor-vehicle">Motor Vehicle</a>
                        <a href="/premises-liability">Premises Liability</a>
                        <a href="/los-angeles-car-accident-lawyer">LA Car Accident Lawyer</a>'''

la_footer_old = '''<h4>LA Lawyer by Accident Type</h4>
          <ul>
            <li><a href="/los-angeles-car-accident-lawyer">LA Car Accident Lawyer</a></li>'''
la_footer_new = '''<h4>LA Lawyer by Accident Type</h4>
          <ul>
            <li><a href="/motor-vehicle">Motor Vehicle</a></li><li><a href="/premises-liability">Premises Liability</a></li><li><a href="/los-angeles-car-accident-lawyer">LA Car Accident Lawyer</a></li>'''

files = walk(root)
n1 = n2 = n3 = n4 = 0
for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'motor-vehicle">Motor Vehicle (LA)</a>' in content:
        continue
    changed = False
    if nav_practice_old in content:
        content = content.replace(nav_practice_old, nav_practice_new)
        n1 += 1
        changed = True
    if footer_practice_old in content:
        content = content.replace(footer_practice_old, footer_practice_new)
        n2 += 1
        changed = True
    if 'LA Lawyer by Accident Type' in content and la_nav_old in content:
        content = content.replace(la_nav_old, la_nav_new)
        n3 += 1
        changed = True
    if 'LA Lawyer by Accident Type' in content and la_footer_old in content:
        content = content.replace(la_footer_old, la_footer_new)
        n4 += 1
        changed = True
    if changed:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
print('Practice nav:', n1, 'footer:', n2, 'LA nav:', n3, 'LA footer:', n4)
