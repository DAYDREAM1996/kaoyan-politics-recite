import re

with open('extracted_text.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

noise_patterns = [
    r'(\n\s*\d{1,3}\s*\n[^\n]*(?:前进|冲冲|仙进|制进|背诵|已冲剌)[^\n]*)',
    r'\n\s*(?:继续前进|冲冲冲|堪坎仙进|绢续仙进|堪续仙进|呻仙进|开 怕前进)[^\n]*\n',
    r'\n\s*\d{1,3}\s*\n',
    r'\n\s*(?:马克思主义基本原理|毛泽东思想和中国特色社会主义理论体系概论|毛泽东思想和中目特色|习近平新时代中国特色社会主义思想概论|习近平\s*新\s*时代|中国近现代史纲要|中\s*国近现代史纲要|思想道德与法治|思想道径与法治|思想逄佬\s*与\s*法治|爷考研政治核心背[涌诵][芼至]记|士虾睬核心距员茎记|爷考研政治\s*核心背涌芼记)[”«" \t]*\n',
    r'\x0c'
]

for pat in noise_patterns:
    text = re.sub(pat, '\n', text)

idx = text.find('鲜明的政')
if idx != -1:
    print("Found around '鲜明的政':")
    print(repr(text[idx-40:idx+40]))
