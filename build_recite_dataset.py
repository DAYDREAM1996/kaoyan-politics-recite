#!/usr/bin/env python3
"""
Build structured memorization dataset (【背诵部分】) from《2027核心背诵笔记》.
Uses pdftotext -layout output so multi-column tables remain intact.
"""
import json
import os
import re
import subprocess

PDF_PATH = "2027核心背诵笔记.pdf【新公众号：安心研】免费分享.pdf"
LAYOUT_TXT_PATH = "/tmp/extracted_layout.txt"

TOC = [
    ("马原", "导论", 2),
    ("马原", "第一章 辩证唯物论", 5),
    ("马原", "第二章 唯物辩证法", 17),
    ("马原", "第三章 认识论", 29),
    ("马原", "第四章 唯物史观", 42),
    ("马原", "第五章 劳动价值论（简单商品经济）", 53),
    ("马原", "第六章 剩余价值论（发达商品经济）", 61),
    ("马原", "第七章 资本主义的发展及其趋势", 75),
    ("马原", "第八章 科学社会主义", 82),
    ("毛中特", "导论 马克思主义中国化时代化的历史进程与理论成果", 88),
    ("毛中特", "第一章 毛泽东思想及其历史地位", 91),
    ("毛中特", "第二章 新民主主义革命理论", 94),
    ("毛中特", "第三章 社会主义改造理论", 106),
    ("毛中特", "第四章 社会主义建设道路初步探索的理论成果", 112),
    ("毛中特", "第五章 中国特色社会主义理论体系的形成发展", 117),
    ("毛中特", "第六章 邓小平理论", 119),
    ("毛中特", "第七～八章 “三个代表”重要思想和科学发展观", 127),
    ("习思想", "导论", 130),
    ("习思想", "第一章 新时代坚持和发展中国特色社会主义", 132),
    ("习思想", "第二章 以中国式现代化全面推进中华民族伟大复兴", 136),
    ("习思想", "第三章 坚持党的全面领导", 139),
    ("习思想", "第四章 坚持以人民为中心", 141),
    ("习思想", "第五章 全面深化改革开放", 143),
    ("习思想", "第六章 推动高质量发展", 149),
    ("习思想", "第七章 社会主义现代化建设的教育、科技、人才战略", 161),
    ("习思想", "第八～九章 中国特色社会主义民主与法治建设", 165),
    ("习思想", "第十章 建设社会主义文化强国", 171),
    ("习思想", "第十一章 以保障和改善民生为重点加强社会建设", 175),
    ("习思想", "第十二章 建设社会主义生态文明", 177),
    ("习思想", "第十三～十五章 国家安全、国防军队和“一国两制”", 179),
    ("习思想", "第十六章 中国特色大国外交和推动构建人类命运共同体", 184),
    ("习思想", "第十七章 全面从严治党", 189),
    ("史纲", "第一章 进入近代后中华民族的磨难与抗争", 194),
    ("史纲", "第二章 不同社会力量对国家出路的早期探索", 200),
    ("史纲", "第三章 辛亥革命与君主专制制度的终结", 207),
    ("史纲", "第四章 中国共产党成立和中国革命新局面", 214),
    ("史纲", "第五章 中国革命的新道路", 227),
    ("史纲", "第六章 中华民族的抗日战争", 233),
    ("史纲", "第七章 为建立新中国而奋斗", 245),
    ("史纲", "第八～十章 新中国时期", 253),
    ("思修", "第一章 领悟人生真谛把握人生方向", 265),
    ("思修", "第二章 追求远大理想坚定崇高信念", 269),
    ("思修", "第三章 继承优良传统弘扬中国精神", 272),
    ("思修", "第四章 明确价值要求践行价值准则", 277),
    ("思修", "第五章 遵守道德规范锤炼道德品格", 280),
    ("思修", "第六章 学习法治思想提升法治素养", 289),
]

REC_RE = re.compile(r"(?:[一—\s]*[、\.．]\s*)?背\s*诵\s*(?:部\s*分|内\s*容)")
COMP_RE = re.compile(r"(?:[一二＿12]\s*[、\.．]\s*)?理\s*解\s*(?:部\s*分|内\s*容)")


def ensure_layout_txt():
    if not os.path.exists(LAYOUT_TXT_PATH):
        subprocess.run(["pdftotext", "-layout", PDF_PATH, LAYOUT_TXT_PATH], check=True)


def is_noise_line(raw_l):
    s = raw_l.strip()
    if not s:
        return False  # Preserve blank lines as visual row/paragraph separators!
    compact = re.sub(r"\s+", "", s)
    if re.match(r"^\d{1,3}$", compact):
        return True
    if re.match(r"^[CQGO0-9()=\[\]@.\s,、·~—\-''\"“”<>«»|/\\三一]+$", compact) and len(compact) <= 12:
        return True
    if re.search(r"考研.{0,6}(核心|核[1叱]1?).{0,4}[背昔肯苗][诵涌]", compact) and len(compact) < 30:
        return True
    if re.search(r"继续|冲冲冲|堪坎|叩贞|饱续|堪续|煤续|蕴续|恺坎|呻nn|tit女|吐11|吐i|血前启", compact) and len(compact) < 28:
        return True
    if re.match(r"^(马克思主义基本原理|毛泽东思想|习近平新时代|中国近现代史纲要|思想[道逄][德待锯徇佬]).{0,32}[”\"«《》\s]*$", compact):
        return True
    if compact in ("续表", "三", "匀", "心", "目", "仑", "石", "Q", "G", "r", "l", "I", "、", "丿", "()", "()=@", "”，导论<<", "”导论”", "一·", "兮"):
        return True
    if re.match(r"^[”\"«>＜]+\s*(导论|第.+[章节童垂窒])\s*[”\"«<＞]*$", compact):
        return True
    return False


def strip_inline_margin_noise(raw_l):
    # Remove trailing page-footer margin noise like '    三 295' or '   l   181'
    s = re.sub(r"\(\)=@\s*\d*", "", raw_l)
    s = re.sub(r"\s+(?:三|l|Q|©)\s*\d{2,3}\s*$", "", s)
    return s.rstrip()


EXACT_REPLACEMENTS = [
    ("以＾旦为中心", "以人民为中心"),
    ("基木观点", "基本观点"),
    ("科学认识2", "科学认识。"),
    ("坠须坚持", "必须坚持"),
    ("覂堕民地", "半殖民地"),
    ("罗觅群众", "劳动群众"),
    ("近代中国的且会性质", "近代中国的社会性质"),
    ("我国社全的性质", "我国社会的性质"),
    ("历史性课阻", "历史性课题"),
    ("发挥作甩", "发挥作用"),
    ("伟大构想的运甩", "伟大构想的运用"),
    ("民生福扯", "民生福祉"),
    ("人民福扯", "人民福祉"),
    ("爰国主义", "爱国主义"),
    ("反映溢", "反映着"),
    ("体现溢", "体现着"),
    ("体现看", "体现着"),
    ("标志薯", "标志着"),
    ("百力更生", "自力更生"),
    ("细枝未节", "细枝末节"),
    ("府续绵延", "赓续绵延"),
    ("盺党指挥", "听党指挥"),
    ("首要位贯", "首要位置"),
    ("内活", "内涵"),
    ("保暗", "保障"),
    ("U民依照", "人民依照"),
    ("U民", "人民"),
    ("廿文化事业", "和文化事业"),
    ("社会保章权", "社会保障权"),
    ("等自扛", "等自由"),
    ("工作入员", "工作人员"),
    ("衣照法律", "按照法律"),
    ("惟进国家", "推进国家"),
    ("效幸等", "效率等"),
    ("轰经常", "最经常"),
    ("轰大", "最大"),
    ("轰高", "最高"),
    ("轰根本", "最根本"),
    ("轰基本", "最基本"),
    ("轰主要", "最主要"),
    ("轰重要", "最重要"),
    ("童要着力点", "重要着力点"),
    ("突出童点", "突出重点"),
    ("合作共羸", "合作共赢"),
    ("一脉柜承", "一脉相承"),
    ("几于年", "几千年"),
    ("建军—百年", "建军一百年"),
    ("和平统—", "和平统一"),
    ("展性", "属性"),
    ("制度屈性", "制度属性"),
    ("影晌因素", "影响因素"),
    ("支待下", "支持下"),
    ("E确认同", "文化认同"),
    ("韦大复兴", "伟大复兴"),
    ("战路", "战略"),
    ("—切", "一切"),
    ("—致", "一致"),
    ("统—", "统一"),
    ("。。", "。"),
    ("领导力昼", "领导力量"),
    ("范踌", "范畴"),
    ("绍释", "解释"),
    ("问胚", "问题"),
    ("离效", "高效"),
    ("监昝", "监督"),
    ("荣沓", "荣誉"),
    ("统—战线", "统一战线"),
    ("刲度保隍", "制度保障"),
    ("战路基点", "战略基点"),
    ("战路支撑", "战略支撑"),
    ("材产", "财产"),
    ("又利", "权利"),
    ("关键少数 3", "关键少数”"),
    ("．关键少数", "“关键少数"),
    ("会、·。`'", ""),
    ("4俨·", ""),
    ("一－", ""),
    ("4.\" 马恩列“", "4. “马恩列”"),
    ("4.\"马恩列“", "4. “马恩列”"),
    ("影晌", "影响"),
    ("坠1922年", "从1922年"),
    ("衣民", "农民"),
    ("愧偶政权", "傀儡政权"),
    ("中共央", "中共中央"),
    ("I民党", "国民党"),
    ("洽法地位", "合法地位"),
    ("广怀、武汉", "广州、武汉"),
    ("蒋汇集团", "蒋介石集团"),
    ("纯寄托", "单纯寄托"),
    ("希脾", "希望"),
    ("统治医", "统治区"),
    ("全面抗战略线", "全面抗战路线"),
    ("中流砾柱", "中流砥柱"),
    ("政栠", "政策"),
    ("于部", "干部"),
    ("其屯教条主义", "其中教条主义"),
    ("历史间题", "历史问题"),
    ("先进生特征", "先进性特征"),
    ("具体屏释", "具体解释"),
    ("道笢评价", "道德评价"),
    ("先人后已", "先人后己"),
    ("第次写上了", "第一次写上了"),
    ("年内战局面", "十年内战局面"),
    ("飞马克思主义", "“马克思主义"),
    ("！．国民参政会", "2. 国民参政会"),
    ("i. 社会主义道德", "2. 社会主义道德"),
    ("u ", "“"),
    ("“四个自信＇", "“四个自信”"),
    ("“两个结合＇", "“两个结合”"),
    ("“一国两制＇", "“一国两制”"),
    ("“三个代表＇", "“三个代表”"),
    ("“和平统—、一国两制”", "“和平统一、一国两制”"),
    ("”问题r", "”问题："),
    ("万灵魂•a胎记•a挠神基因", "“灵魂”“胎记”“精神基因”"),
    ("汤（人民性）", "立场（人民性）"),
    ("上的价值立", "人民至上的价值立场"),
]

QIAN_TO_YU_WORDS = [
    "关于", "属于", "处于", "源于", "取决于", "有利于", "基于", "位于", "趋于",
    "贯彻于", "存在于", "区别于", "不同于", "来源于", "根源于", "集中于", "致力于",
    "勇于", "善于", "敢于", "在于", "由于", "对于", "至于", "大于", "小于", "少于",
    "等于", "低于", "高于", "归于", "寓于", "限于", "富于", "乐于", "忠于", "出身于",
    "成立于", "产生于", "发源于", "形成于", "着眼于", "立足于", "服务于", "服从于",
    "寄希望于", "归功于", "归结于", "受制于", "见之于", "融会于", "贯穿于", "体现于",
    "反映于", "屈服于", "沉迷于", "独立于", "游离于", "止步于", "诞生于", "植根于",
    "脱胎于", "始于", "终于", "优于", "劣于", "近于", "晚于", "早于", "先于", "后于",
    "迫于", "鉴于", "勤于", "敏于", "精于", "长于", "苦于", "忙于", "急于", "甘于",
    "耻于", "疏于", "怠于", "流于", "沦于", "陷于", "匿于", "溶于", "合于", "便于",
    "难于", "易于", "适于", "宜于", "无异于", "莫过于", "莫大于", "从属于", "附属于",
    "诉诸于", "置身于", "投身于", "融于", "见诸于", "流露于", "寄寓于", "立足于",
]


def clean_chinese_text(text):
    if not text:
        return ""
    s = text.strip()
    s = re.sub(r"(?<=[一-鿿])\s+(?=[一-鿿])", "", s)
    s = re.sub(r"(?<=[一-鿿])\s+(?=[，。、；：？！）》」』”])", "", s)
    s = re.sub(r"(?<=[（《「『“，。、；：？！])\s+(?=[一-鿿])", "", s)
    s = re.sub(r"\s*([，。；：？！、])\s*", r"\1", s)
    s = re.sub(r"\(\)=@\s*\d*", "", s)

    for old, new in EXACT_REPLACEMENTS:
        s = s.replace(old, new)

    # Fix '4." 马恩列“' or '" 马恩列“' or '6. u马克思主义”' style OCR quotes
    s = re.sub(r"^(\d{1,2})\s*[\.．]\s*[\"”u]\s*", r"\1. “", s)
    s = re.sub(r"^[\"”]\s*([一-鿿]{2,15})\s*[\"“”]", r"“\1”", s)
    s = re.sub(r"(?<=[一-鿿])“(?=[一-鿿]{2,15}(?:经典|重要|命题|思想))", "”", s)

    for w in QIAN_TO_YU_WORDS:
        broken = w.replace("于", "千")
        if broken != w:
            s = s.replace(broken, w)
    s = re.sub(r"融([^，。；]{1,12})千一体", r"融\1于一体", s)
    s = re.sub(r"集([^，。；]{1,12})千一身", r"集\1于一身", s)

    for w in ["并且", "并存", "并重", "并列", "并行", "并非", "并不", "并将", "并举", "并进", "并蓄", "兼收并蓄", "合并", "吞并", "一并"]:
        s = s.replace(w.replace("并", "井"), w)

    for w in ["已经", "已成为", "已成", "已由", "已达", "已进入", "已基本", "已占", "已发生", "已解决", "已确立"]:
        s = s.replace(w.replace("已", "巳"), w)

    s = re.sub(r"\([Il]\)", "(1)", s)
    s = re.sub(r"^(\d+)\s*[、,，]\s*", r"\1. ", s)
    s = re.sub(r"(?<![a-zA-Z])u\s*([一-鿿]{2,12})\s*n(?![a-zA-Z])", r"“\1”", s)
    s = s.replace("＇", "”").replace("＂", "”")
    s = re.sub(r"(?<=[一-鿿])·(?=[一-鿿])", "：", s)
    s = re.sub(r"\s{2,}", " ", s).strip()

    circ = "①②③④⑤⑥⑦⑧⑨⑩"
    s = re.sub(r"(?<=[:：；。\s])CD(?=[一-鿿])", "＠", s)
    s = re.sub(r"^CD(?=[一-鿿])", "＠", s)
    s = re.sub(r"^O(?=[一-鿿]{2,})", "＠", s)
    # Strip any residual running-header OCR fragments that survived inside a merged line
    s = re.sub(r"[呤爷咕][号考研零粤平]{1,3}政治.{0,12}[背昔肯苗][诵涌][芼笔]记[，,]?", "", s)
    if any(ch in s for ch in ("＠", "©", "@")):
        idx = 0
        out_chars = []
        for ch in s:
            if ch in ("＠", "©", "@"):
                out_chars.append(circ[idx] if idx < len(circ) else "•")
                idx += 1
            else:
                out_chars.append(ch)
        s = "".join(out_chars)
    return s.strip()


def renumber_circled_bullets(text):
    """If OCR per-line cleaning turned multiple bullets into ① ① ①, number them ① ② ③..."""
    if text.count("①") <= 1:
        return text
    circ = "①②③④⑤⑥⑦⑧⑨⑩"
    idx = 0
    out = []
    for ch in text:
        if ch == "①":
            out.append(circ[idx] if idx < len(circ) else "•")
            idx += 1
        else:
            out.append(ch)
    return "".join(out)


def split_segments_with_pos(line):
    segs = []
    for m in re.finditer(r"(?:\S| (?=\S))+", line):
        txt = m.group(0).strip()
        if txt:
            segs.append((m.start(), m.end(), txt))
    return segs


def is_structural_marker(s):
    s_norm = re.sub(r"^[,\.．·]+(?=\s*[一-鿿])", "1. ", s.strip())
    s_norm = re.sub(r"^[Lt]\s+(?=[一-鿿]{3,})", "1. ", s_norm)
    s_norm = re.sub(r"^(?:！|i)\s*[\.．]\s*", "2. ", s_norm)
    s_norm = re.sub(r"^\(([Il])\)", "(1)", s_norm)
    if re.match(r"^\(\s*\d{1,2}\s*\)", s_norm):
        return True
    if re.match(r"^[（(][一二三四五六七八九十]+[）)]\s*.{1,35}$", s_norm):
        return True
    m_top = re.match(r"^(\d{1,2})\s*[\.．、]\s*([一-鿿“”\"《（u].{1,55})$", s_norm)
    if m_top and int(m_top.group(1)) <= 25 and not re.match(r"^\d+\s*[年个条项次名步种世纪年代月日]", s_norm):
        return True
    return False


def is_table_line(line):
    s = line.strip()
    if not s or is_structural_marker(s):
        return False
    segs = split_segments_with_pos(line)
    if len(segs) >= 2:
        return True
    # Single-segment line inside a table: indented >= 8, OR short wrapped cell label (<=10 chars, no ending punctuation)
    if segs and (segs[0][0] >= 8 or (len(segs[0][2]) <= 10 and not re.search(r"[。！？]$", segs[0][2]))):
        return True
    return False


def cluster_columns_by_interval(all_segs):
    """Cluster segments into column intervals [min_start, max_end] using horizontal overlap."""
    intervals = []
    for line_segs in all_segs:
        for st, ed, _ in line_segs:
            intervals.append((st, ed))
    if not intervals:
        return []
    # Sort by start position
    intervals.sort()
    # Merge intervals that overlap (with 1-char tolerance only if narrow, or direct overlap)
    cols = []
    for st, ed in intervals:
        placed = False
        # Find best overlapping column
        best_idx = -1
        best_overlap = -1
        for idx, (cst, ced) in enumerate(cols):
            overlap = min(ed, ced) - max(st, cst)
            if overlap > 0 and overlap > best_overlap:
                best_overlap = overlap
                best_idx = idx
        if best_idx != -1:
            cst, ced = cols[best_idx]
            cols[best_idx] = (min(cst, st), max(ced, ed))
        else:
            cols.append((st, ed))
        cols.sort()
    # Second pass: merge any columns that now overlap significantly
    merged = []
    for cst, ced in cols:
        if merged and min(ced, merged[-1][1]) - max(cst, merged[-1][0]) > 2:
            merged[-1] = (min(merged[-1][0], cst), max(merged[-1][1], ced))
        else:
            merged.append((cst, ced))
    return merged


def parse_table_block(table_raw_lines):
    """
    table_raw_lines may contain empty strings representing blank-line gaps between rows!
    Lines NOT separated by blank lines belong to the SAME row (multi-line wrapped cells).
    """
    # Split into contiguous non-blank line groups (= visual rows)
    groups = []
    cur_g = []
    for l in table_raw_lines:
        if not l.strip():
            if cur_g:
                groups.append(cur_g)
                cur_g = []
        else:
            cur_g.append(l)
    if cur_g:
        groups.append(cur_g)

    group_segs = []
    all_segs = []
    for g in groups:
        g_s = [split_segments_with_pos(l) for l in g if split_segments_with_pos(l)]
        if g_s:
            group_segs.append(g_s)
            all_segs.extend(g_s)

    if not all_segs:
        return None

    col_intervals = cluster_columns_by_interval(all_segs)
    if len(col_intervals) < 2:
        return None

    def map_col(st, ed):
        best_c = 0
        best_score = -10**9
        mid = (st + ed) / 2
        for c_idx, (cst, ced) in enumerate(col_intervals):
            overlap = min(ed, ced) - max(st, cst)
            if overlap > 0:
                score = overlap + 1000
            else:
                cmid = (cst + ced) / 2
                score = -abs(mid - cmid)
            if score > best_score:
                best_score = score
                best_c = c_idx
        return best_c

    # Combine each contiguous line group into 1 logical row
    rows = []
    for g_s in group_segs:
        sub_rows = []
        cur_row = [""] * len(col_intervals)
        for line_segs in g_s:
            line_cols = {}
            for st, ed, txt in line_segs:
                c = map_col(st, ed)
                line_cols[c] = (line_cols[c] + " " + txt) if c in line_cols else txt

            # Only split within a contiguous group if BOTH col 0 AND another column have new entries
            # AND col 0 already has a complete cell (or col >= 1 looks like a fresh sub-row)
            if any(cur_row) and 0 in line_cols and cur_row[0] and len(line_cols) >= 2 and any(cur_row[k] for k in range(1, len(col_intervals))) and re.search(r"[。！？\d年]$|战略|建设|原则|时期|阶段|政府|国家|立法|执法|司法|守法", cur_row[0]):
                sub_rows.append(cur_row)
                cur_row = [""] * len(col_intervals)
            elif any(cur_row) and len(line_cols) >= 2 and 0 not in line_cols and any(cur_row[k] for k in line_cols if k > 0):
                c_first = min(line_cols.keys())
                if c_first < len(col_intervals) - 1 and len(line_cols[c_first]) <= 10 and cur_row[c_first] and len(cur_row[c_first]) <= 10:
                    sub_rows.append(cur_row)
                    cur_row = [""] * len(col_intervals)

            for c, txt in line_cols.items():
                if cur_row[c]:
                    if txt.startswith(("①", "②", "③", "④", "⑤", "＠", "©", "第一", "第二", "第三")):
                        cur_row[c] += "\n" + txt
                    else:
                        cur_row[c] += (" " if txt[0].isascii() else "") + txt
                else:
                    cur_row[c] = txt

        if any(cur_row):
            sub_rows.append(cur_row)
        rows.extend(sub_rows)

    # Clean all cells and drop noise rows/cols
    cleaned_rows = []
    for r in rows:
        cr = []
        for cell in r:
            parts = [clean_chinese_text(p) for p in cell.split("\n")]
            parts = [p for p in parts if p and p not in ("|", "I", "l", "1", "''", "一·", "。", "~", "「") and not re.match(r"^\d{1,3}$", p)]
            joined = renumber_circled_bullets("\n".join(parts))
            cr.append(joined)
        if any(cr):
            cleaned_rows.append(cr)

    keep_cols = [c for c in range(len(col_intervals)) if any(r[c] for r in cleaned_rows)]
    cleaned_rows = [[r[c] for c in keep_cols] for r in cleaned_rows]
    if len(keep_cols) < 2 or not cleaned_rows:
        return None
    if len(cleaned_rows) == 1 and sum(len(x) for x in cleaned_rows[0]) < 12:
        return None
    # Reject 1-2 row citation/parenthetical wrap that isn't an actual table
    flat_txt = "".join(x for r in cleaned_rows for x in r)
    if flat_txt.startswith(("（出自", "(出自", "的《")):
        return None

    first = cleaned_rows[0]
    header_keywords = {
        "项目", "内容", "本质", "地位", "作用", "意义", "特点", "表现", "环节", "主体", "原则",
        "属性", "层级", "名称", "会议", "时期", "阶段", "阶级", "类型", "标准", "划分标准",
        "代表", "目标", "要求", "职能", "原因", "时间", "背景", "方针", "政策", "领域", "方面",
        "维度", "关系", "主要内容", "回答的问题", "地位和作用", "科学内涵", "战略安排",
        "不同历史阶段", "革命的主要对象", "阶级特点", "形成", "核心", "人大", "政府", "其他",
        "内容及意义", "基本内容", "主要表现", "特征", "做法", "评价", "局限性", "影响", "解释",
        "分类", "解释说明", "措施", "内容解释", "必然性（依据）", "必要性（依据）", "可能性", "关键词",
    }
    has_header = (
        len(cleaned_rows) >= 2
        and all(len(c) <= 16 for c in first if c)
        and any(c in header_keywords or any(hk in c for hk in ("标准", "项目", "内容", "阶段", "环节", "时期", "类型", "名称", "特点", "对象", "主体", "原则", "意义", "解释", "依据")) for c in first if c)
    )

    if has_header:
        headers = [h if h else f"栏位{idx+1}" for idx, h in enumerate(first)]
        data_rows = cleaned_rows[1:]
    else:
        headers = [f"栏位{i+1}" for i in range(len(keep_cols))]
        data_rows = cleaned_rows

    if not data_rows:
        return None
    return {"headers": headers, "rows": data_rows}


def extract_clozes_and_qa(text):
    body = re.sub(r"^\(\d+\)\s*", "", text).strip()
    prompt = ""
    answer = ""
    clozes = []

    depth = 0
    in_quote = False
    colon_idx = -1
    for i, ch in enumerate(body):
        if ch in "（(《【":
            depth += 1
        elif ch in "）)》】":
            depth = max(0, depth - 1)
        elif ch in "“「":
            in_quote = True
        elif ch in "”」":
            in_quote = False
        elif ch in ("：", ":") and depth == 0 and not in_quote:
            if 2 <= i <= 65 and len(body) - i - 1 >= 2:
                colon_idx = i
                break

    if colon_idx != -1:
        prompt = body[:colon_idx].strip()
        answer = body[colon_idx + 1:].strip().rstrip("。")
        if len(answer) <= 75:
            clozes.append(answer)
        else:
            parts = re.split(r"(?=[①②③④⑤⑥⑦⑧])|[；;]", answer)
            for pt in parts:
                pt = pt.strip().rstrip("。；")
                pt_clean = re.sub(r"^[①②③④⑤⑥⑦⑧]\s*", "", pt).strip()
                if len(pt_clean) >= 3:
                    clozes.append(pt_clean[:45] if len(pt_clean) > 45 else pt_clean)

    for m in re.finditer(r"[“《]([^”》]{2,20})[”》]", body):
        kw = m.group(0)
        if kw not in clozes and not any(kw in c for c in clozes):
            clozes.append(kw)

    for m in re.finditer(r"(?:18|19|20)\d{2}\s*年(?:\s*\d{1,2}\s*月(?:\s*\d{1,2}\s*日)?)?", body):
        dt = m.group(0)
        if dt not in clozes and not any(dt in c for c in clozes):
            clozes.append(dt)

    if not clozes:
        for pat in [
            r"(?:根本|核心|实质|精髓|灵魂|关键|基础|前提|唯一特性|根本保证|根本原因|主要矛盾|基本国情|根本任务|总目标|本质)(?:是|为|在于)([^，。；]{2,28})",
            r"(?:标志着|实现了|确立了|提出了|阐明了)([^，。；]{3,28})",
        ]:
            for m in re.finditer(pat, body):
                kw = m.group(1).strip()
                if len(kw) >= 2 and kw not in clozes:
                    clozes.append(kw)

    return prompt, answer, clozes[:8]


def parse_chapter_content(chap_obj):
    raw_lines = chap_obj["raw"].splitlines()
    topics = []
    cur_subsec = ""
    cur_topic = {"title": "核心背诵要点", "subsection": "", "items": []}
    cur_item = None

    def flush_item():
        nonlocal cur_item
        if cur_item is not None:
            full = renumber_circled_bullets(clean_chinese_text(cur_item["text"]))
            if full and len(full) >= 2:
                prompt, answer, clozes = extract_clozes_and_qa(full)
                cur_topic["items"].append({
                    "type": "text",
                    "label": cur_item["label"],
                    "text": full,
                    "prompt": prompt,
                    "answer": answer,
                    "clozes": clozes,
                })
            cur_item = None

    def flush_topic():
        flush_item()
        if cur_topic["items"]:
            topics.append(cur_topic)

    i = 0
    n = len(raw_lines)
    while i < n:
        line = raw_lines[i]
        s = line.strip()
        if not s:
            i += 1
            continue

        s_norm = re.sub(r"^[,\.．·]+(?=\s*[一-鿿])", "1. ", s)
        s_norm = re.sub(r"^[Lt]\s+(?=[一-鿿]{3,})", "1. ", s_norm)
        s_norm = re.sub(r"^(?:！|i)\s*[\.．]\s*", "2. ", s_norm)
        s_norm = re.sub(r"^\(([Il])\)", "(1)", s_norm)
        # Note: some OCR lines have '1 唯物辩证法...' (missing dot); only allow missing dot if single-segment short heading!
        segs_cur = split_segments_with_pos(line)

        m_sub = re.match(r"^[（(]([一二三四五六七八九十]+)[）)]\s*(.+)$", s_norm)
        if m_sub and len(s_norm) < 40 and not re.search(r"[。；：]$", s_norm):
            flush_topic()
            cur_subsec = f"（{m_sub.group(1)}）{clean_chinese_text(m_sub.group(2))}"
            cur_topic = {"title": cur_subsec, "subsection": cur_subsec, "items": []}
            i += 1
            continue

        # Topic heading: either "N. Title" (even if followed by ：内容。) or "N Title" (single-segment without 。；)
        m_top = re.match(r"^(\d{1,2})\s*[\.．、]\s*([一-鿿“”\"《（u].{1,65})$", s_norm)
        if not m_top and len(segs_cur) == 1 and not re.search(r"[。；]$", s_norm):
            m_top = re.match(r"^(\d{1,2})\s+([一-鿿“”\"《（].{1,45})$", s_norm)

        if m_top and len(segs_cur) == 1 and not s_norm.startswith("(") and int(m_top.group(1)) <= 25 and not re.match(r"^\d+\s*[年个条项次名步种世纪年代月日]", s_norm):
            flush_topic()
            cleaned_rest = clean_chinese_text(m_top.group(2))
            # Handle 1-line "2. 邓小平理论的精髓（活的灵魂）：解放思想、实事求是。"
            if "：" in cleaned_rest and re.search(r"[。；]$", cleaned_rest):
                t_head, t_ans = cleaned_rest.split("：", 1)
                t_title = f"{m_top.group(1)}. {t_head.strip()}"
                cur_topic = {"title": t_title, "subsection": cur_subsec, "items": []}
                cur_item = {"type": "text", "label": "", "text": cleaned_rest}
            else:
                t_title = f"{m_top.group(1)}. {cleaned_rest}"
                cur_topic = {"title": t_title, "subsection": cur_subsec, "items": []}
            i += 1
            continue

        m_item = re.match(r"^\(\s*(\d{1,2})\s*\)\s*(.*)$", s_norm)
        if m_item:
            flush_item()
            lbl = f"({m_item.group(1)})"
            rest = m_item.group(2).strip()
            cur_item = {"type": "text", "label": lbl, "text": f"{lbl} {rest}" if rest else lbl}
            i += 1
            continue

        segs = split_segments_with_pos(line)
        starts_indented_table = (
            len(segs) == 1
            and segs[0][0] >= 8
            and cur_item is not None
            and cur_item["type"] == "text"
            and re.search(r"[：。]$", cur_item["text"].strip())
            and i + 1 < n
        )
        if (len(segs) >= 2 or starts_indented_table) and not re.match(r"^[①②③④⑤⑥⑦⑧＠©]", s_norm):
            # Collect table lines INCLUDING blank lines so parse_table_block sees visual row boundaries!
            tbl_lines = [line]
            j = i + 1
            while j < n:
                k = j
                while k < n and not raw_lines[k].strip():
                    k += 1
                if k >= n:
                    break
                nxt = raw_lines[k]
                if is_table_line(nxt):
                    # Preserve blank-line indicator if k > j
                    if k > j:
                        tbl_lines.append("")
                    tbl_lines.append(nxt)
                    j = k + 1
                else:
                    break

            tbl = parse_table_block(tbl_lines)
            if tbl and len(tbl["rows"]) >= 1:
                if cur_item and cur_item["type"] == "text":
                    intro = clean_chinese_text(cur_item["text"])
                    cur_item = None
                    cur_topic["items"].append({
                        "type": "table",
                        "label": "",
                        "intro": intro,
                        "headers": tbl["headers"],
                        "rows": tbl["rows"],
                    })
                else:
                    flush_item()
                    cur_topic["items"].append({
                        "type": "table",
                        "label": "",
                        "intro": "",
                        "headers": tbl["headers"],
                        "rows": tbl["rows"],
                    })
                i = j
                continue

        if cur_item is not None and cur_item["type"] == "text":
            cur_item["text"] += s
        else:
            cur_item = {"type": "text", "label": "", "text": s}
        i += 1

    flush_topic()
    return topics


def main():
    ensure_layout_txt()
    with open(LAYOUT_TXT_PATH, "r", encoding="utf-8", errors="ignore") as f:
        pages = f.read().split("\x0c")

    cleaned_pages = []
    for p in pages:
        cleaned_pages.append("\n".join(strip_inline_margin_noise(l) for l in p.splitlines() if not is_noise_line(l)))

    recitation_chapters = []
    total_items = 0
    total_tables = 0
    total_flashcards = 0
    item_seq = 1

    for idx, (sub, title, bp) in enumerate(TOC):
        start_p = bp + 9
        end_p = (TOC[idx + 1][2] + 9) if idx + 1 < len(TOC) else 313
        chunk = "\n".join(cleaned_pages[start_p : min(end_p + 1, 313)])
        m_rec = REC_RE.search(chunk)
        if not m_rec:
            print(f"WARNING: No recite marker for {sub} {title}")
            continue
        after_rec = chunk[m_rec.end():]
        m_comp = COMP_RE.search(after_rec)
        raw = after_rec[:m_comp.start()] if m_comp else after_rec
        if not m_comp:
            m_next = re.search(r"(习近平新时代中国特色|第[一二三四五六七八九十]+章|1\.\s*[\"“]两个结合)", raw)
            if m_next:
                raw = raw[:m_next.start()]

        topics = parse_chapter_content({
            "id": idx + 1,
            "subject": sub,
            "chapter": title,
            "book_page": bp,
            "raw": raw,
        })

        chap_item_count = 0
        for t in topics:
            for it in t["items"]:
                it["id"] = f"r_{item_seq}"
                item_seq += 1
                chap_item_count += 1
                total_items += 1
                if it["type"] == "table":
                    total_tables += 1
                elif it.get("prompt") and it.get("answer"):
                    total_flashcards += 1

        recitation_chapters.append({
            "id": f"ch_{idx + 1}",
            "order": idx + 1,
            "subject": sub,
            "chapter": title,
            "book_page": bp,
            "item_count": chap_item_count,
            "topics": topics,
        })

    existing = {}
    if os.path.exists("politics_data.json"):
        with open("politics_data.json", "r", encoding="utf-8") as f:
            existing = json.load(f)

    out_data = {
        "meta": {
            "title": "考研政治 · 核心背诵神器",
            "source": "徐涛《2027考研政治核心背诵笔记》【背诵部分】全量精编",
            "total_chapters": len(recitation_chapters),
            "total_items": total_items,
            "total_tables": total_tables,
            "total_flashcards": total_flashcards,
            "total_questions": len(existing.get("questions", [])),
        },
        "recitation": recitation_chapters,
        "core_terms": existing.get("core_terms", []),
        "essay_templates": existing.get("essay_templates", []),
        "study_guide": existing.get("study_guide", {}),
        "questions": existing.get("questions", []),
    }

    with open("politics_data.json", "w", encoding="utf-8") as f:
        json.dump(out_data, f, ensure_ascii=False, indent=2)

    with open("data.js", "w", encoding="utf-8") as f:
        f.write("window.POLITICS_DATA = ")
        json.dump(out_data, f, ensure_ascii=False)
        f.write(";\n")

    print(f"Done! Chapters: {len(recitation_chapters)}, Items: {total_items}, Tables: {total_tables}, Flashcards(Q->A): {total_flashcards}")


if __name__ == "__main__":
    main()
