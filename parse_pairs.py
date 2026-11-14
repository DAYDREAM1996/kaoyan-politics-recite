import re

with open('extracted_text.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Look for patterns like:
# (1) 物质的共同特性（唯一特性、本质规定性）：客观实在性。
# (2) 物质的存在方式和根本属性（固有属性）：运动。
# 标志着...
# 核心问题是...
# 第一动力是...
pattern = re.compile(r'([^\n，。；]{2,30}(?:本质|根本|核心|基础|前提|标志|第一动力|生命线|首要|重要来源|基石|灵魂)[^\n，。；]{0,15}[：:—＝=]\s*[^\n，。；]{2,30})')
matches = pattern.findall(text)

print(f"Total paired concepts found: {len(matches)}")
cleaned = []
for m in matches[:35]:
    m_clean = re.sub(r'^[＠@\s\d\.\(\)CDAB\-\*①②③④⑤]+', '', m).strip()
    m_clean = re.sub(r'(?<=[一-龥])\s+(?=[一-龥])', '', m_clean)
    if any(k in m_clean for k in ['根本', '本质', '核心', '基础', '标志', '动力', '生命线', '首要', '基石']):
        cleaned.append(m_clean)

for c in cleaned[:20]:
    print("•", c)
