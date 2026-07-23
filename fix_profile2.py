import re

with open('src/screens/Profile/Profile.jsx', 'r') as f:
    content = f.read()

# I want to replace the hardcoded role="button" tabIndex={0}
content = content.replace(
    'role="button" tabIndex={0} onKeyDown={(e) => { if(e.key===\'Enter\'||e.key===\' \') { e.preventDefault(); if(!editing) setEditing(true); } }}',
    'role={!editing ? "button" : undefined} tabIndex={!editing ? 0 : undefined} onKeyDown={(e) => { if(!editing && (e.key===\'Enter\'||e.key===\' \')) { e.preventDefault(); setEditing(true); } }}'
)

with open('src/screens/Profile/Profile.jsx', 'w') as f:
    f.write(content)
