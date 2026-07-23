import re

with open('src/screens/Profile/Profile.jsx', 'r') as f:
    content = f.read()

def replacer(match):
    div_start = match.group(0)
    # inject role and tabIndex and onKeyDown
    return div_start.replace(" onClick", " role=\"button\" tabIndex={0} onKeyDown={(e) => { if(e.key==='Enter'||e.key===' ') { e.preventDefault(); if(!editing) setEditing(true); } }} onClick")

content = re.sub(r'<div className=\{`prf-card \$\{!editing \? \'clickable\' : \'\'\}`\} onClick=\{\(\) => !editing && setEditing\(true\)\}>', replacer, content)

# There is also one without template literal maybe?
# Check Onboarding.jsx, etc.
with open('src/screens/Profile/Profile.jsx', 'w') as f:
    f.write(content)
