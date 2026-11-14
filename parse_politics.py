import re
import json

with open('extracted_text.txt', 'r', encoding='utf-8', errors='ignore') as f:
    raw_text = f.read()

pages = raw_text.split('\x0c')

def get_subject_and_chapter(page_num, page_str):
    if page_num <= 86:
        sub = '马原'
        if page_num <= 4:
            chap = '导论'
        elif page_num <= 16:
            chap = '辩证唯物论'
        elif page_num <= 28:
            chap = '唯物辩证法'
        elif page_num <= 41:
            chap = '认识论'
        elif page_num <= 52:
            chap = '唯物史观'
        elif page_num <= 60:
            chap = '劳动价值论（简单商品经济）'
        elif page_num <= 74:
            chap = '剩余价值论（发达商品经济）'
        elif page_num <= 81:
            chap = '资本主义的发展及其趋势'
        else:
            chap = '科学社会主义'
    elif page_num <= 129:
        sub = '毛中特'
        if page_num <= 90:
            chap = '导论'
        elif page_num <= 93:
            chap = '毛泽东思想及其历史地位'
        elif page_num <= 105:
            chap = '新民主主义革命理论'
        elif page_num <= 111:
            chap = '社会主义改造理论'
        elif page_num <= 116:
            chap = '社会主义建设道路初步探索'
        elif page_num <= 118:
            chap = '中国特色社会主义理论体系'
        elif page_num <= 126:
            chap = '邓小平理论'
        else:
            chap = '“三个代表”与科学发展观'
    elif page_num <= 193:
        sub = '习思想'
        if page_num <= 131:
            chap = '导论'
        elif page_num <= 135:
            chap = '新时代坚持和发展中国特色社会主义'
        elif page_num <= 138:
            chap = '以中国式现代化全面推进中华民族伟大复兴'
        elif page_num <= 140:
            chap = '坚持党的全面领导'
        elif page_num <= 142:
            chap = '坚持以人民为中心'
        elif page_num <= 148:
            chap = '全面深化改革开放'
        elif page_num <= 160:
            chap = '推动高质量发展'
        elif page_num <= 164:
            chap = '教育、科技、人才战略'
        elif page_num <= 170:
            chap = '民主与法治建设'
        elif page_num <= 174:
            chap = '建设社会主义文化强国'
        elif page_num <= 176:
            chap = '改善民生与社会建设'
        elif page_num <= 178:
            chap = '建设社会主义生态文明'
        elif page_num <= 183:
            chap = '国家安全、国防军队与“一国两制”'
        elif page_num <= 188:
            chap = '大国外交与人类命运共同体'
        else:
            chap = '全面从严治党'
    elif page_num <= 263:
        sub = '史纲'
        if page_num <= 199:
            chap = '近代中国磨难与抗争'
        elif page_num <= 206:
            chap = '早期探索与洋务/维新运动'
        elif page_num <= 213:
            chap = '辛亥革命与君主专制终结'
        elif page_num <= 226:
            chap = '中国共产党成立和中国革命新局面'
        elif page_num <= 232:
            chap = '中国革命的新道路'
        elif page_num <= 244:
            chap = '中华民族的抗日战争'
        elif page_num <= 252:
            chap = '为建立新中国而奋斗'
        else:
            chap = '社会主义革命与建设时期'
    else:
        sub = '思修'
        if page_num <= 264:
            chap = '绪论 担当复兴大任'
        elif page_num <= 268:
            chap = '领悟人生真谛 把握人生方向'
        elif page_num <= 271:
            chap = '追求远大理想 坚定崇高信念'
        elif page_num <= 276:
            chap = '继承优良传统 弘扬中国精神'
        elif page_num <= 279:
            chap = '明确价值要求 践行价值准则'
        elif page_num <= 288:
            chap = '遵守道德规范 锤炼道德品格'
        else:
            chap = '学习法治思想 提升法治素养'
    return sub, chap

print("Subject and chapter map defined.")

questions = []
q_id = 1

for p_idx, page in enumerate(pages):
    if p_idx < 10 or p_idx > 305:
        continue
    
    sub, chap = get_subject_and_chapter(p_idx, page)
    
    # Filter noise lines
    raw_lines = page.split('\n')
    cleaned_lines = []
    for l in raw_lines:
        ls = l.strip()
        if not ls:
            continue
        if re.search(r'继续前进|冲冲冲|考研政治核心背诵|中国政法大学|黄皮书系列|开 怕前进|堪坎|绢续', ls) and len(ls) < 30:
            continue
        if re.match(r'^\d+$', ls):
            continue
        if re.match(r'^[Q©C0O3目~_—•§\s]+$', ls):
            continue
        cleaned_lines.append(ls)
    
    # Track current "注意..." explanation rule
    current_rule = ""
    stmt_buf = []
    
    i = 0
    while i < len(cleaned_lines):
        line = cleaned_lines[i]
        
        # Check if line introduces a rule: e.g. (1) 注意... or 注意...
        if '注意' in line or '命题思路' in line or '避坑要点' in line:
            # collect rule lines until '例如' or next item
            rule_parts = [line]
            j = i + 1
            while j < len(cleaned_lines) and not cleaned_lines[j].startswith('例如') and not ('（对）' in cleaned_lines[j] or '（错）' in cleaned_lines[j]):
                if cleaned_lines[j].startswith('(') or cleaned_lines[j].startswith('（'):
                    break
                rule_parts.append(cleaned_lines[j])
                j += 1
            current_rule = ' '.join(rule_parts)
            i = j
            continue
            
        # Check if line contains (对) or (错)
        if '（对）' in line or '（错）' in line or '(对)' in line or '(错)' in line:
            # Combine with buffer if buffer exists
            if stmt_buf:
                full_stmt = ' '.join(stmt_buf) + ' ' + line
                stmt_buf = []
            else:
                full_stmt = line
            
            # Determine verdict
            verdict = True if ('（对）' in full_stmt or '(对)' in full_stmt) else False
            
            # Clean statement
            clean_stmt = full_stmt
            clean_stmt = re.sub(r'^[＠@\s\d\.\(\)CDAB\-\*①②③④⑤例如：:]+', '', clean_stmt)
            clean_stmt = re.sub(r'[（\(][对错][）\)].*$', '', clean_stmt).strip()
            
            if len(clean_stmt) >= 4 and not clean_stmt.startswith('继续前进'):
                questions.append({
                    'id': q_id,
                    'subject': sub,
                    'chapter': chap,
                    'page': p_idx,
                    'statement': clean_stmt,
                    'answer': verdict,
                    'explanation': current_rule if current_rule else '考点辨析与真题避坑。'
                })
                q_id += 1
        elif line.startswith('例如') or line.startswith('＠') or line.startswith('@') or line.startswith('CD'):
            # This is likely the start of a statement that might wrap to next lines
            if stmt_buf:
                stmt_buf = []
            stmt_buf.append(line)
        elif stmt_buf:
            stmt_buf.append(line)
        
        i += 1

print(f"Total extracted questions: {len(questions)}")
print("Sample questions:")
for q in questions[:10]:
    print(f"[{q['id']}] [{q['subject']}-{q['chapter']}] ({'对' if q['answer'] else '错'}) {q['statement']}")
    if q['explanation']:
        print(f"   解析: {q['explanation'][:60]}...")
