import re
import json

with open('extracted_text.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

# Clean noise patterns
noise_patterns = [
    r'(\n\s*\d{1,3}\s*\n[^\n]*(?:前进|冲冲|仙进|制进|背诵|已冲剌)[^\n]*)',
    r'\n\s*(?:继续前进|冲冲冲|堪坎仙进|绢续仙进|堪续仙进|呻仙进|开 怕前进)[^\n]*\n',
    r'\n\s*\d{1,3}\s*\n',
    r'\n\s*(?:马克思主义基本原理|毛泽东思想和中国特色社会主义理论体系概论|毛泽东思想和中目特色|习近平新时代中国特色社会主义思想概论|习近平\s*新\s*时代|中国近现代史纲要|中\s*国近现代史纲要|思想道德与法治|思想道径与法治|思想逄佬\s*与\s*法治|爷考研政治核心背[涌诵][芼至]记|士虾睬核心距员茎记|爷考研政治\s*核心背涌芼记)[”«" \t]*\n',
    r'\x0c'
]

for pat in noise_patterns:
    text = re.sub(pat, '\n', text)

# Normalize spaces inside Chinese text
# Replace multiple blank lines with double newline
text = re.sub(r'\n{3,}', '\n\n', text)

# Subject positions
subject_positions = [
    (0, '马原'),
    (text.find('圣 毛泽东思想'), '毛中特'),
    (text.find('圣 习近平新时代'), '习思想'),
    (text.find('圣 中国近现代史纲要'), '史纲'),
    (text.find('思想道德与法治'), '思修')
]

def get_subject_at_pos(pos):
    current = '马原'
    for p, name in subject_positions:
        if p != -1 and pos >= p:
            current = name
    return current

# Let's extract chapters
# Find all chapter headers like '>> 第一章 ...' or '第X章 ...'
chapter_matches = list(re.finditer(r'(?:>>\s*)?(第[一二三四五六七八九十百]+[章节][^\n<]{2,30}|导论|绪论[^\n<]{0,20})', text))

def get_chapter_at_pos(pos):
    current_chap = '导论'
    for m in chapter_matches:
        if m.start() <= pos:
            title = m.group(1).replace('>', '').replace('<', '').replace('cc', '').replace('”', '').replace('“', '').strip()
            # Clean OCR weird characters in chapter titles
            title = title.replace('弟', '第').replace('噩', '章').replace('唯圳论', '唯物论').replace('垂', '章')
            current_chap = title
        else:
            break
    return current_chap

# Find all blocks of (1) 注意 ... 例如 ... （对/错）
# We can iterate through paragraphs
lines = text.split('\n')

questions = []
q_id = 1
current_rule = "考点辨析与真题避坑要点"
current_buf = []

for idx, line in enumerate(lines):
    l = line.strip()
    if not l:
        continue
    
    # Update rule if this line has "注意"
    if '注意' in l or '命题思路' in l or '避坑要点' in l:
        rule_lines = [l]
        lookahead = idx + 1
        while lookahead < len(lines) and lookahead < idx + 4:
            next_l = lines[lookahead].strip()
            if not next_l or next_l.startswith('例如') or '（对）' in next_l or '（错）' in next_l or next_l.startswith('(') or next_l.startswith('（'):
                break
            rule_lines.append(next_l)
            lookahead += 1
        current_rule = ''.join(rule_lines)
    
    # Check if this line ends with or contains （对） or （错）
    if '（对）' in l or '（错）' in l or '(对)' in l or '(错)' in l:
        current_buf.append(l)
        combined = ''.join(current_buf)
        current_buf = []
        
        # Check verdict
        verdict = True if ('（对）' in combined or '(对)' in combined) else False
        
        # Clean statement
        s = combined
        # remove prefix markers
        s = re.sub(r'^[＠@\s\d\.\(\)CDAB\-\*①②③④⑤例如：:]+', '', s)
        s = re.sub(r'[（\(][对错][）\)].*$', '', s).strip()
        # remove extra spaces between Chinese characters
        s = re.sub(r'(?<=[一-龥])\s+(?=[一-龥])', '', s)
        
        # Filter out bad OCR lines or too short lines
        if len(s) >= 4 and not any(k in s for k in ['冲冲冲', '继续前进', '已冲剌', '黄皮书系列']):
            # Infer trap type
            trap = "真题命题点"
            if not verdict:
                if any(k in s for k in ['根本原因', '直接原因', '决定', '反作用', '基础']):
                    trap = "因果/主次颠倒"
                elif any(k in s for k in ['绝对', '彻底', '完全', '消除', '终极', '唯一']):
                    trap = "绝对化表述"
                elif any(k in s for k in ['主观唯心', '客观唯心', '唯物主义', '形而上学']):
                    trap = "哲学派别张冠李戴"
                elif any(k in s for k in ['等同于', '包含', '取代', '是一回事']):
                    trap = "概念混淆"
                else:
                    trap = "偷换概念/违背真理"
            else:
                trap = "高频正确表述"
            
            # Position in text
            pos = sum(len(line) + 1 for line in lines[:idx])
            sub = get_subject_at_pos(pos)
            chap = get_chapter_at_pos(pos)
            
            # Clean explanation
            expl = current_rule
            expl = re.sub(r'^[＠@\s\d\.\(\)CDAB\-\*①②③④⑤例如：:]+', '', expl)
            expl = re.sub(r'(?<=[一-龥])\s+(?=[一-龥])', '', expl).strip()
            
            questions.append({
                'id': q_id,
                'subject': sub,
                'chapter': chap,
                'statement': s,
                'answer': verdict,
                'trap_type': trap,
                'explanation': expl
            })
            q_id += 1
    elif l.startswith('例如') or l.startswith('＠') or l.startswith('@') or l.startswith('CD') or l.startswith('①') or l.startswith('②') or l.startswith('③'):
        current_buf = [l]
    elif current_buf:
        # Continue accumulating statement
        current_buf.append(l)

print(f"Extracted {len(questions)} high-yield true/false questions!")
subject_counts = {}
for q in questions:
    subject_counts[q['subject']] = subject_counts.get(q['subject'], 0) + 1
print("By Subject:", subject_counts)
