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

chap_pattern = re.compile(r'(第[一二三四五六七八九十百]+[章节][^\n<]{1,30}|导论|绪论[^\n<]{0,20})')

questions = []
q_id = 1
current_chap = "导论"
current_rule = "真题命题点与避坑核心"

for p_idx, page in enumerate(pages):
    sub = get_subject_by_page(p_idx)
    if sub == '前言目录':
        continue
    
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
                    'statement': clean_stmt,
                    'answer': verdict,
                    'trap_type': trap,
                    'explanation': current_rule if current_rule else '真题高频考查点与命题避坑要点。'
                })
                q_id += 1
        elif line.startswith('例如') or line.startswith('＠') or line.startswith('@') or line.startswith('CD') or line.startswith('①') or line.startswith('②'):
            stmt_buf = [line]
        elif stmt_buf:
            stmt_buf.append(line)
            
        i += 1

print(f"Total Questions Parsed: {len(questions)}")

# Now generate core terms / cloze flashcards
core_terms = [
    {
        "id": 1,
        "subject": "马原",
        "category": "辩证唯物论",
        "question": "物质的共同特性（唯一特性、本质规定性）是：",
        "answer": "客观实在性",
        "notes": "注意区分客观实在性（唯一特性）与运动（根本属性和存在方式）。"
    },
    {
        "id": 2,
        "subject": "马原",
        "category": "辩证唯物论",
        "question": "物质的存在方式和根本属性（固有属性）是：",
        "answer": "运动",
        "notes": "物质与运动不可分，设想脱离物质的运动是唯心主义，设想脱离运动的物质是形而上学。"
    },
    {
        "id": 3,
        "subject": "马原",
        "category": "辩证唯物论",
        "question": "运动的衡量尺度和特殊状态是：",
        "answer": "静止",
        "notes": "静止是运动的特殊形式，是相对的、有条件的。"
    },
    {
        "id": 4,
        "subject": "马原",
        "category": "辩证唯物论",
        "question": "马克思主义的基石、辩证唯物主义最核心的观点是：",
        "answer": "世界的物质统一性原理",
        "notes": "一切从实际出发是世界物质统一性原理在实际工作中的根本要求。"
    },
    {
        "id": 5,
        "subject": "马原",
        "category": "辩证唯物论",
        "question": "客观规律性与主观能动性统一的基础是：",
        "answer": "实践",
        "notes": "实践是客观规律性与主观能动性相统一的根本途径。"
    },
    {
        "id": 6,
        "subject": "马原",
        "category": "唯物辩证法",
        "question": "唯物辩证法的实质和核心是：",
        "answer": "对立统一规律",
        "notes": "对立统一规律揭示了事物普遍联系的根本内容和变化发展的内在动力。"
    },
    {
        "id": 7,
        "subject": "马原",
        "category": "唯物辩证法",
        "question": "人们认识世界和改造世界的根本方法是：",
        "answer": "矛盾分析方法",
        "notes": "一分为二看问题，坚持两点论与重点论相统一。"
    },
    {
        "id": 8,
        "subject": "马原",
        "category": "唯物辩证法",
        "question": "事物发展的根本原因在于：",
        "answer": "事物的内部矛盾（内因）",
        "notes": "外因是变化的条件，内因是变化的根据，外因通过内因而起作用。"
    },
    {
        "id": 9,
        "subject": "马原",
        "category": "认识论",
        "question": "马克思主义首要的和基本的观点是：",
        "answer": "实践观点",
        "notes": "实践观点是马克思主义哲学区别于一切旧哲学的根本特征。"
    },
    {
        "id": 10,
        "subject": "马原",
        "category": "认识论",
        "question": "认识的本质是：",
        "answer": "主体在实践基础上对客体的能动反映",
        "notes": "既坚持了反映论（唯物主义），又坚持了能动性（辩证法）。"
    },
    {
        "id": 11,
        "subject": "马原",
        "category": "认识论",
        "question": "检验真理的唯一标准是：",
        "answer": "实践",
        "notes": "实践之所以是唯一标准，因为实践具有把主观认识同客观实际联系起来的品格。"
    },
    {
        "id": 12,
        "subject": "马原",
        "category": "认识论",
        "question": "人类认识世界和改造世界的根本目标是：",
        "answer": "认识必然和争取自由",
        "notes": "自由是对必然的认识和对客观世界的改造。"
    },
    {
        "id": 13,
        "subject": "马原",
        "category": "唯物史观",
        "question": "社会历史发展的根本动力是：",
        "answer": "社会基本矛盾",
        "notes": "即生产力与生产关系、经济基础与上层建筑的矛盾。"
    },
    {
        "id": 14,
        "subject": "马原",
        "category": "唯物史观",
        "question": "社会发展的最终决定力量是：",
        "answer": "生产力",
        "notes": "生产力是人类社会生活和全部历史的基础。"
    },
    {
        "id": 15,
        "subject": "马原",
        "category": "唯物史观",
        "question": "历史的创造者和决定力量是：",
        "answer": "人民群众",
        "notes": "人民群众是历史的主体，杰出历史人物对历史起推动或加速作用，但不能决定历史走向。"
    },
    {
        "id": 16,
        "subject": "马原",
        "category": "劳动价值论",
        "question": "以私有制为基础的商品经济的基本矛盾是：",
        "answer": "私人劳动和社会劳动的矛盾",
        "notes": "它是商品经济其他一切矛盾的基础，决定了商品经济的发展过程。"
    },
    {
        "id": 17,
        "subject": "马原",
        "category": "剩余价值论",
        "question": "马克思经济学说的核心内容和基石是：",
        "answer": "剩余价值理论",
        "notes": "剩余价值理论阐明了资本主义剥削的实质。"
    },
    {
        "id": 18,
        "subject": "马原",
        "category": "剩余价值论",
        "question": "剩余价值的唯一源泉是雇佣工人的：",
        "answer": "剩余劳动（可变资本v购买的劳动力）",
        "notes": "不变资本c只能转移价值，不能带来价值增殖。"
    },
    {
        "id": 19,
        "subject": "马原",
        "category": "资本主义发展",
        "question": "资本主义经济危机的本质特征是：",
        "answer": "生产相对过剩",
        "notes": "不是绝对过剩，而是相对于劳动人民有支付能力的需求过剩。"
    },
    {
        "id": 20,
        "subject": "马原",
        "category": "资本主义发展",
        "question": "资本主义经济危机爆发的根本原因是：",
        "answer": "资本主义基本矛盾（生产社会化与生产资料私人占有）",
        "notes": "只要资本主义制度存在，经济危机就不可避免。"
    },
    {
        "id": 21,
        "subject": "毛中特",
        "category": "毛泽东思想",
        "question": "毛泽东思想活的灵魂是：",
        "answer": "实事求是、群众路线、独立自主",
        "notes": "十一届六中全会《决议》明确提出。"
    },
    {
        "id": 22,
        "subject": "毛中特",
        "category": "毛泽东思想",
        "question": "党的思想路线的核心，毛泽东思想的精髓是：",
        "answer": "实事求是",
        "notes": "实事求是是马克思主义中国化时代化的根本要求。"
    },
    {
        "id": 23,
        "subject": "毛中特",
        "category": "新民主主义革命",
        "question": "区别新旧两种不同范畴民主主义革命的根本标志是：",
        "answer": "革命的领导权归属（无产阶级领导还是资产阶级领导）",
        "notes": "无产阶级领导权是新民主主义革命的核心问题。"
    },
    {
        "id": 24,
        "subject": "毛中特",
        "category": "新民主主义革命",
        "question": "中国革命的首要问题是：",
        "answer": "分清敌友",
        "notes": "毛泽东《中国社会各阶级的分析》提出：谁是我们的敌人？谁是我们的朋友？"
    },
    {
        "id": 25,
        "subject": "毛中特",
        "category": "新民主主义革命",
        "question": "中国革命的基本问题，新民主主义革命的主力军是：",
        "answer": "农民问题 / 农民阶级",
        "notes": "中国民主革命实质上就是党领导下的农民革命。"
    },
    {
        "id": 26,
        "subject": "毛中特",
        "category": "新民主主义革命",
        "question": "中国共产党战胜敌人的三大法宝是：",
        "answer": "统一战线、武装斗争、党的建设",
        "notes": "统一战线和武装斗争是两个基本武器，党的组织是掌握这两个武器的英勇战士。"
    },
    {
        "id": 27,
        "subject": "毛中特",
        "category": "邓小平理论",
        "question": "党在社会主义初级阶段的基本路线，是国家的生命线、人民的：",
        "answer": "幸福线",
        "notes": "一个中心，两个基本点（以经济建设为中心，坚持四项基本原则，坚持改革开放）。"
    },
    {
        "id": 28,
        "subject": "习思想",
        "category": "坚持党的全面领导",
        "question": "中国特色社会主义最本质的特征和最大优势是：",
        "answer": "中国共产党的领导",
        "notes": "党是最高政治领导力量，党政军民学，东西南北中，党是领导一切的。"
    },
    {
        "id": 29,
        "subject": "习思想",
        "category": "高质量发展",
        "question": "全面建设社会主义现代化国家的首要任务是：",
        "answer": "高质量发展",
        "notes": "高质量发展是新时代的硬道理。"
    },
    {
        "id": 30,
        "subject": "习思想",
        "category": "高质量发展",
        "question": "引领发展的第一动力是：",
        "answer": "创新",
        "notes": "坚持创新在我国现代化建设全局中的核心地位。"
    },
    {
        "id": 31,
        "subject": "习思想",
        "category": "中国式现代化",
        "question": "全面建设社会主义现代化国家的基础性、战略性支撑是：",
        "answer": "教育、科技、人才",
        "notes": "教育是基础，科技是关键，人才是第一资源。"
    },
    {
        "id": 32,
        "subject": "习思想",
        "category": "以人民为中心",
        "question": "党的一切工作的出发点和落脚点，中国式现代化的本质要求是：",
        "answer": "以人民为中心 / 增进民生福祉",
        "notes": "江山就是人民，人民就是江山。"
    },
    {
        "id": 33,
        "subject": "习思想",
        "category": "法治建设",
        "question": "治国理政的基本方式是：",
        "answer": "法治",
        "notes": "全面依法治国是国家治理的一场深刻革命。"
    },
    {
        "id": 34,
        "subject": "史纲",
        "category": "早期探索",
        "question": "中国近代史上第一个比较系统发展资本主义的方案是：",
        "answer": "《资政新篇》",
        "notes": "洪仁玕提出，但由于缺乏社会基础和战争环境未付诸实行。"
    },
    {
        "id": 35,
        "subject": "史纲",
        "category": "中国共产党成立",
        "question": "开辟中国历史新纪元，标志着中国新民主主义革命开端的事件是：",
        "answer": "五四运动",
        "notes": "五四运动促进了马克思主义同中国工人运动的结合。"
    },
    {
        "id": 36,
        "subject": "史纲",
        "category": "抗日战争",
        "question": "中国人民抗日战争胜利的决定性因素是：",
        "answer": "以爱国主义为核心的伟大民族精神",
        "notes": "中国共产党的中流砥柱作用是抗战胜利的关键。"
    },
    {
        "id": 37,
        "subject": "思修",
        "category": "理想信念",
        "question": "当代中国青年的历史使命和最大政治是：",
        "answer": "以中国式现代化全面推进中华民族伟大复兴",
        "notes": "立大志、明大德、成大才、担大任。"
    },
    {
        "id": 38,
        "subject": "思修",
        "category": "社会主义核心价值观",
        "question": "社会主义核心价值观中，国家层面的价值要求是：",
        "answer": "富强、民主、文明、和谐",
        "notes": "社会层面：自由、平等、公正、法治；公民个人层面：爱国、敬业、诚信、友善。"
    }
]

# Now prepare Subjective (Essay) Templates
essay_templates = [
    {
        "id": "mayuan-1",
        "title": "矛盾的对立统一与转化（万能帽子）",
        "subject": "马原分析题",
        "applicable": "材料中出现‘双刃剑’、‘利与弊’、‘危中有机’、‘转化’、‘兼顾’、‘克服困难取得成功’等",
        "principle": "矛盾是反映事物内部和事物之间对立统一关系的哲学范畴。同一性和斗争性是矛盾的两种基本属性。同一性是指矛盾双方相互依存、互为前提，并在一定条件下相互贯通、相互转化；斗争性是指矛盾双方相互排斥、相互分离。矛盾双方既对立又统一，由此推动事物的运动、变化和发展。",
        "methodology": "在实践中要坚持一分为二看问题，坚持两点论。既要看到矛盾双方的对立，又要看到矛盾双方的统一；善于在对立中把握统一，在统一中把握对立；积极创造有利条件，促使事物向有利于实践成功的方向转化，变不利为有利，化危机为先机。",
        "formula": "【第一步·亮帽子】：材料体现了唯物辩证法关于对立统一规律（或矛盾同一性与斗争性辩证关系）的原理。\n【第二步·展理论】：阐述原理+方法论（见上方）。\n【第三步·扣材料】：材料中指出[摘抄材料关键句]，说明在面对[具体事物/困境]时，既看到了[A面]，又看到了[B面]，通过[采取的行动]，成功实现了从[不利状态]向[有利状态]的转化。"
    },
    {
        "id": "mayuan-2",
        "title": "矛盾普遍性与特殊性（共性与个性）",
        "subject": "马原分析题",
        "applicable": "材料中出现‘因地制宜’、‘具体问题具体分析’、‘试点推广’、‘中国特色’、‘借鉴经验但不盲从’",
        "principle": "矛盾的普遍性是指矛盾存在于一切事物中，存在于一切事物发展过程的始终，即事事有矛盾、时时有矛盾。矛盾的特殊性是指具体事物在其运动中的矛盾及每一矛盾的各个方面都有其特点。矛盾的普遍性和特殊性是辩证统一的，共性寓于个性之中，并通过个性表现出来；个性包含共性，二者在一定条件下相互转化。",
        "methodology": "坚持矛盾普遍性和特殊性相统一，坚持具体问题具体分析。把马克思主义普遍真理与中国具体实际相结合；在实际工作中坚持‘一般号召与个别指导相结合’、‘解剖麻雀’、‘从群众中来到群众中去’，先试点再推广。",
        "formula": "【第一步·亮帽子】：材料体现了唯物辩证法关于矛盾普遍性与特殊性辩证关系的原理（共性与个性）。\n【第二步·展理论】：阐述原理+方法论。\n【第三步·扣材料】：材料中[主体]没有生搬硬套已有经验，而是结合了[本地/当前具体实际]，具体问题具体分析，从而找到了符合自身实际的[成功方案/特色道路]。"
    },
    {
        "id": "mayuan-3",
        "title": "主要矛盾与次要矛盾 / 两点论与重点论",
        "subject": "马原分析题",
        "applicable": "材料中出现‘抓住关键’、‘牵住牛鼻子’、‘突破口’、‘突出重点兼顾全面’、‘首要任务’",
        "principle": "在复杂事物的发展过程中，存在着多种矛盾，其中主要矛盾处于支配地位，对事物的发展起决定作用；次要矛盾处于从属地位。矛盾的主次方面中，主要方面决定事物的性质。两点论与重点论是统一的，辩证法的两点论是有重点的两点论，重点论是看到两点中的重点。",
        "methodology": "想问题、办事情既要全面，又要善于抓重点、抓中心、抓关键。在工作中要牵住‘牛鼻子’，集中力量解决主要矛盾，同时统筹兼顾次要矛盾，反对不分主次的一点论和均衡论。",
        "formula": "【第一步·亮帽子】：材料体现了唯物辩证法关于主要矛盾和次要矛盾（或两点论与重点论相统一）的原理。\n【第二步·展理论】：阐述原理+方法论。\n【第三步·扣材料】：材料中在推进[某项事业/工作]时，准确把握住了[核心问题/关键瓶颈]，将其作为[突破口/首要任务]，同时协同推进[其他工作]，做到了重点突破与全面兼顾。"
    },
    {
        "id": "mayuan-4",
        "title": "实践与认识的辩证关系 / 认识的反复性无限性",
        "subject": "马原分析题",
        "applicable": "材料中出现‘探索过程’、‘总结经验’、‘反复试验’、‘真理在实践中检验’、‘认识深化’",
        "principle": "实践是认识的基础，实践是认识的来源、发展的动力、检验真理的唯一标准和最终目的。认识对实践具有能动的反作用，正确的认识指导实践促进事物发展，错误的认识阻碍事物发展。由于受客观事物复杂性与主体认知水平的限制，认识具有反复性和无限性，追求真理是一个永无止境的循环往复、波浪式前进过程。",
        "methodology": "坚持一切从实际出发，实事求是；坚持实践第一的观点，把理论与实践紧密结合；在实践中检验和发展真理；与时俱进，开拓创新，不断深化认识、丰富认识。",
        "formula": "【第一步·亮帽子】：材料体现了辩证唯物主义认识论关于实践与认识的辩证关系原理（及认识发展的反复性与无限性）。\n【第二步·展理论】：阐述原理+方法论。\n【第三步·扣材料】：材料中[科研人员/实践主体]经过[多次实验/探索挫折]，在实践中不断发现问题、总结经验，推动认识从[感性到理性/从初步到深入]，最终用正确的理论成功指导了[具体实践结果]。"
    },
    {
        "id": "mayuan-5",
        "title": "真理尺度与价值尺度的统一",
        "subject": "马原分析题",
        "applicable": "材料中出现‘科技向善’、‘既按规律办事又造福人民’、‘绿色发展’、‘人工智能伦理’",
        "principle": "人类的实践活动受真理尺度和价值尺度的双重制约。真理尺度是指在实践中必须遵循客观规律（合规律性）；价值尺度是指在实践中必须满足人的需要（合目的性）。任何成功的实践都是合规律性与合目的性的统一，是真理尺度与价值尺度的辩证统一。",
        "methodology": "在实践中既要坚持科学态度，按客观规律办事；又要坚持人道主义和人民立场，把人民利益作为最高价值追求。推动科技创新必须兼顾伦理底线与社会效益，实现‘真’与‘善’的统一。",
        "formula": "【第一步·亮帽子】：材料体现了认识论关于真理尺度与价值尺度辩证统一的原理。\n【第二步·展理论】：阐述原理+方法论。\n【第三步·扣材料】：材料中在推进[科技发展/工程建设]时，既严格遵循了[客观科学规律]，又充分考虑了[人民群众福祉/生态环境保护]，实现了合规律性与合目的性的有机结合。"
    },
    {
        "id": "mayuan-6",
        "title": "尊重客观规律与发挥主观能动性",
        "subject": "马原分析题",
        "applicable": "材料中出现‘发挥人的干劲’、‘科学精神与实干奋斗’、‘克服自然条件限制’",
        "principle": "规律是客观的，不以人的意志为转移。尊重客观规律是正确发挥主观能动性的前提和基础；主观能动性是人们认识和利用客观规律的必要条件。实践是尊重规律和发挥能动性相统一的根本途径。",
        "methodology": "想问题、办事情必须把革命热情同科学态度结合起来，既要反对片面强调规律客观性而无所作为的宿命论，又要反对盲目蛮干、夸大主观意志的唯意志论。",
        "formula": "【第一步·亮帽子】：材料体现了尊重客观规律与发挥主观能动性相统一的原理。\n【第二步·展理论】：阐述原理+方法论。\n【第三步·扣材料】：材料中[主体]没有盲目蛮干，而是在深刻把握[自然/经济客观规律]的基础上，充分发挥了艰苦奋斗、开拓创新的主观能动性，创造性地实现了[工作成果]。"
    }
]

# Study Guide
study_guide = {
    "hours_breakdown": [
        {
            "time": "08:00 - 09:30 (1.5h)",
            "phase": "攻坚阶段：马原分析题万能原理帽子",
            "task": "背熟马原6大核心原理（矛盾对立统一、普遍特殊性、主次矛盾、实践认识、真理价值、客观规律与能动性）。",
            "goal": "能在纸上默写出原理名字和2-3句核心表述，确保马原大题不空场、帽子戴准（稳拿8分底分）。"
        },
        {
            "time": "09:30 - 12:30 (3.0h)",
            "phase": "刷题阶段：马原 & 毛中特 真题避坑判断题",
            "task": "打开刷题机，集中刷马原（177题）和毛中特（35题）避坑判断题。",
            "goal": "只看一眼凭直觉判断，错题立即看解析并点击收藏，建立对陷阱词的生理性反应。"
        },
        {
            "time": "12:30 - 13:30 (1.0h)",
            "phase": "休整阶段：午餐 + 放空大脑",
            "task": "吃饱饭，闭目养神30分钟，不要看手机信息，让大脑记忆固化。",
            "goal": "恢复脑力，为下午的死记硬背充电。"
        },
        {
            "time": "13:30 - 16:30 (3.0h)",
            "phase": "冲刺阶段：习思想 & 史纲 & 思修 避坑题",
            "task": "刷习思想（72题）、史纲（88题）、思修（46题）判断题，累计完成全套418题。",
            "goal": "扫除选择题所有盲点，熟悉史纲会议考点和习思想时政新提法。"
        },
        {
            "time": "16:30 - 18:00 (1.5h)",
            "phase": "秒杀阶段：命题定性词挖空速背卡",
            "task": "打开【定性词挖空卡】，逐条过一遍‘谁是根本/核心/前提/第一动力/生命线’。",
            "goal": "40个高频考点形成条件反射，选择题遇到‘根本保证’、‘首要任务’直接秒选。"
        },
        {
            "time": "18:00 - 19:00 (1.0h)",
            "phase": "休整阶段：晚餐散步 + 核心词口头默念",
            "task": "散步，脑中过一遍刚才背诵的帽子和核心大词。",
            "goal": "缓解眼部疲劳，巩固短时记忆。"
        },
        {
            "time": "19:00 - 21:30 (2.5h)",
            "phase": "大题套路：分析题采分公式与抄材料技术",
            "task": "学习主观题踩分技巧：掌握三段式答题框架（戴帽子 + 阐理论 + 结合材料分点抄写）。",
            "goal": "掌握即使不会背也能从材料中提取有效答案并拿到30+分的技巧。"
        },
        {
            "time": "21:30 - 23:00 (1.5h)",
            "phase": "收官复盘：重刷错题本 + 心理定心丸",
            "task": "点击刷题机中的【只刷错题】，把今天做错的所有题目再过一遍，全部清零。",
            "goal": "消除盲区，带着自信上考场。"
        },
        {
            "time": "23:00 准时就寝",
            "phase": "考前养精蓄锐",
            "task": "考研政治极其考验审题清晰度和文字书写，保证7小时高质量睡眠比熬夜多看两页书有用10倍！",
            "goal": "头脑清醒，卷面工整。"
        }
    ],
    "discard_list": [
        "❌ 坚决不看：政经第6章中复杂的超额剩余价值算术公式和资本周转速度计算（最多考1分单选题，性价比极低）。",
        "❌ 坚决不背：整篇长达数百字的完整大题参考答案范文（考场上根本默写不出来，踩点即可）。",
        "❌ 坚决不抠：细枝末节的党史历史人物生平、不知名战役细节、生僻会议名称。",
        "❌ 坚决不碰：试图完整通读这本324页PDF的每一个段落。"
    ],
    "golden_rules": [
        "✅ 阅卷核心：分析题是【采点给分】！只要写出了核心大词、原理帽子，并且标明①②③分段清晰，就能得分。",
        "✅ 抄材料原则：材料绝不是摆设！80%的答案其实就藏在材料里，要学会‘提取材料主旨 + 换成学术规范语言’写上去。",
        "✅ 卷面即分数：主观题一定要字迹清晰、分段明了，每段开头空两格，标上序号，字数写满答题卡80%以上。"
    ]
}

final_output = {
    "meta": {
        "title": "考研政治核心背诵笔记 · 24小时极速抢分系统",
        "source": "徐涛主编《2027核心背诵笔记》",
        "total_questions": len(questions),
        "total_terms": len(core_terms),
        "total_templates": len(essay_templates)
    },
    "questions": questions,
    "core_terms": core_terms,
    "essay_templates": essay_templates,
    "study_guide": study_guide
}

with open('politics_data.json', 'w', encoding='utf-8') as f:
    json.dump(final_output, f, ensure_ascii=False, indent=2)

print("Saved complete dataset to politics_data.json!")
