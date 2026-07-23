import re

with open('src/screens/Onboarding/Onboarding.jsx', 'r') as f:
    content = f.read()

# Emojis -> Lucide
content = content.replace("import {\n  CheckCircle,\n} from 'lucide-react';", 
"import {\n  CheckCircle,\n  User,\n  Users,\n  Briefcase,\n  PiggyBank,\n  GraduationCap,\n  TrendingUp,\n  Gem,\n} from 'lucide-react';")

# Gender
content = content.replace("{ id: 'male',      icon: '🧑', label: 'Male' },", "{ id: 'male',      icon: <User size={20} />, label: 'Male' },")
content = content.replace("{ id: 'female',    icon: '👩', label: 'Female' },", "{ id: 'female',    icon: <User size={20} />, label: 'Female' },")
content = content.replace("{ id: 'nonbinary', icon: '🌈', label: 'Non-Binary / Prefer not to say' },", "{ id: 'nonbinary', icon: <Users size={20} />, label: 'Non-Binary / Prefer not to say' },")

# Budget
content = content.replace("icon: '💼'", "icon: <Briefcase size={20} />")
content = content.replace("icon: '🐷'", "icon: <PiggyBank size={20} />")
content = content.replace("icon: '🎓'", "icon: <GraduationCap size={20} />")
content = content.replace("icon: '📈'", "icon: <TrendingUp size={20} />")
content = content.replace("icon: '💎'", "icon: <Gem size={20} />")

with open('src/screens/Onboarding/Onboarding.jsx', 'w') as f:
    f.write(content)
