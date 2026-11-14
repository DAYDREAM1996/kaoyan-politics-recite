import re
import json

with open('extracted_text.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

pages = text.split('\x0c')

def get_subject_by_page(p_idx):
    if p_idx < 8:
        return '前言目录'
    elif p_idx <= 95:
        return '马原'
    elif p_idx <= 137:
        return '毛中特'
    elif p_idx <= 201:
        return '习思想'
    elif p_idx <= 271:
        return '史纲'
    else:
        return '思修'

# Let's verify chapters inside each page
chap_pattern = re.compile(r'(第[一二三四五六七八九十百]+[章节][^\n<]{1,30}|导论|绪论[^\n<]{0,20})')

questions = []
q_id = 1
current_chap = "导论"
current_rule = "真题命题点与避坑核心"

for p_idx, page in enumerate(pages):
    sub = get_subject_by_page(p_idx)
    if sub == '前言目录':
        continue
    
    # Check chapter change
    m = chap_pattern.search(page)
    if m:
        c_title = m.group(1).replace('>', '').replace('<', '').replace('cc', '').replace('”', '').replace('“', '').strip()
        c_title = c_title.replace('弟', '第').replace('噩', '章').replace('唯圳论', '唯物论').replace('垂', '章').replace('窒', '章')
        current_chap = c_title
    
    lines = [l.strip() for l in page.split('\n') if l.strip()]
    cleaned_lines = []
    for l in lines:
        if re.search(r'继续前进|冲冲冲|考研政治核心背诵|中国政法大学|黄皮书系列|开 怕前进|堪坎|绢续|呻仙进|已冲剌', l) and len(l) < 30:
            continue
        if re.match(r'^\d+$', l):
            continue
        if re.match(r'^[Q©C0O3目~_—•§\s]+$', l):
            continue
        cleaned_lines.append(l)
    
    # Process lines
    i = 0
    stmt_buf = []
    while i < len(cleaned_lines):
        line = cleaned_lines[i]
        
        if '注意' in line or '命题思路' in line or '避坑要点' in line:
            rule_parts = [line]
            j = i + 1
            while j < len(cleaned_lines) and not cleaned_lines[j].startswith('例如') and not ('（对）' in cleaned_lines[j] or '（错）' in cleaned_lines[j]):
                if cleaned_lines[j].startswith('(') or cleaned_lines[j].startswith('（'):
                    break
                rule_parts.append(cleaned_lines[j])
                j += 1
            current_rule = ' '.join(rule_parts)
            # clean OCR spaces
            current_rule = re.sub(r'(?<=[一-龥])\s+(?=[一-龥])', '', current_rule)
            i = j
            continue
            
        if '（对）' in line or '（错）' in line or '(对)' in line or '(错)' in line:
            if stmt_buf:
                full_stmt = ' '.join(stmt_buf) + ' ' + line
                stmt_buf = []
            else:
                full_stmt = line
            
            verdict = True if ('（对）' in full_stmt or '(对)' in full_stmt) else False
            clean_stmt = full_stmt
            clean_stmt = re.sub(r'^[＠@\s\d\.\(\)CDAB\-\*①②③④⑤例如：:]+', '', clean_stmt)
            clean_stmt = re.sub(r'[（\(][对错][）\)].*$', '', clean_stmt).strip()
            clean_stmt = re.sub(r'(?<=[一-龥])\s+(?=[一-龥])', '', clean_stmt)
            
            if len(clean_stmt) >= 4 and not any(k in clean_stmt for k in ['冲冲冲', '继续前进', '已冲剌', '黄皮书系列']):
                trap = "高频正确考点" if verdict else "干扰项/常见命题陷阱"
                if not verdict:
                    if any(k in clean_stmt for k in ['根本原因', '直接原因', '决定', '反作用', '基础']):
                        trap = "因果/地位颠倒"
                    elif any(k in clean_stmt for k in ['绝对', '彻底', '完全', '消除', '终极', '唯一']):
                        trap = "绝对化表述"
                    elif any(k in clean_stmt for k in ['主观唯心', '客观唯心', '唯物主义', '形而上学']):
                        trap = "哲学派别混淆"
                    elif any(k in clean_stmt for k in ['等同于', '包含', '取代', '是一回事']):
                        trap = "概念混淆"
                    else:
                        trap = "偷换概念/违背真理"
                
                questions.append({
                    'id': q_id,
                    'subject': sub,
                    'chapter': current_chap,
                    'page': p_idx,
                    'statement': clean_stmt,
                    'answer': verdict,
                    'trap_type': trap,
                    'explanation': current_rule if current_rule else '真题高频避坑考点解析。'
                })
                q_id += 1
        elif line.startswith('例如') or line.startswith('＠') or line.startswith('@') or line.startswith('CD') or line.startswith('①') or line.startswith('②'):
            stmt_buf = [line]
        elif stmt_buf:
            stmt_buf.append(line)
            
        i += 1

print(f"Total extracted questions: {len(questions)}")
counts = {}
for q in questions:
    counts[q['subject']] = counts.get(q['subject'], 0) + 1
print("Counts by subject:", counts)
