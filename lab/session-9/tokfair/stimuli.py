"""stimuli.py — the stimulus bank for the Chinese tokenization-fairness study.

Design rationale
----------------
v1 of the explorer compared three hand-written variants (TW / CN / HK) and
reported the extra tokens as a single "dialect tax".  That number is not
interpretable, because the three variants differ on **two** factors at once:

    Factor A  SCRIPT   字形   {traditional, simplified}
    Factor B  LEXICON  詞彙   {tw, cn, hk}

`軟體 / 软件 / 軟件` differs in *both*.  Any "tax" estimated from that
comparison silently pools an orthographic effect (which token vocabularies
encode directly, one Unicode codepoint at a time) with a lexical effect (which
depends on whether a multi-character chunk made it into the merge table).
These have completely different causes and completely different remedies, so
they must be estimated separately.

We therefore write only the LEXICON factor by hand, and *generate* the SCRIPT
factor mechanically with OpenCC character-level conversion (`t2s` / `s2t`,
never `s2twp`, which would also convert vocabulary and re-introduce the
confound).  Every item yields a fully crossed 2 x 3 = 6-cell set:

    trad-tw  trad-cn  trad-hk
    simp-tw  simp-cn  simp-hk

Four of the six cells are orthographically well-formed but sociolinguistically
unattested (nobody writes Taiwanese vocabulary in simplified characters in a
Taiwanese newspaper).  That is fine and in fact necessary: they are *control*
conditions, in the same sense that a psycholinguist uses pseudowords.  They
isolate what the tokenizer responds to, not what a reader would produce.

Provenance note (a datasheet obligation, cf. Jurafsky & Martin ch.2 §Corpora):
the HK column is the weakest link.  It was written to represent *Hong Kong
written Chinese* (traditional script + HK lexical choices such as 的士 / 薯仔),
deliberately excluding written Cantonese (我哋 / 冇 / 畀), so that the contrast
stays lexical rather than becoming a different grammar.  Items marked
`hk_confidence="low"` need validation by a Hong Kong informant before any
result based on them is reported.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from typing import Literal

import opencc

_T2S = opencc.OpenCC("t2s")
_S2T = opencc.OpenCC("s2t")

Script = Literal["trad", "simp"]
Lexicon = Literal["tw", "cn", "hk"]


@dataclass
class Item:
    id: str
    category: str
    tw: str
    cn: str
    hk: str
    gloss: str
    #: what the item is designed to probe; used for per-category hypotheses
    probe: str = ""
    #: "high" if the HK wording is well established, "low" if it needs checking
    hk_confidence: str = "medium"
    #: free-text notes for the datasheet
    note: str = ""

    def cells(self) -> dict[tuple[Script, Lexicon], str]:
        """Expand one item into the fully crossed 2x3 design."""
        out: dict[tuple[Script, Lexicon], str] = {}
        for lex in ("tw", "cn", "hk"):
            surface = getattr(self, lex)
            trad = surface if lex in ("tw", "hk") else _S2T.convert(surface)
            simp = _T2S.convert(surface) if lex in ("tw", "hk") else surface
            out[("trad", lex)] = trad
            out[("simp", lex)] = simp
        return out


# --------------------------------------------------------------------------
# Categories.  Each carries an explicit hypothesis so that a null result is
# still informative.
# --------------------------------------------------------------------------
CATEGORY_HYPOTHESES = {
    "tech": "科技詞為晚近借入，三地各自造詞，且訓練語料以簡體技術文件為主：預測詞彙效果最大。",
    "daily": "日常具體名詞分歧久遠且無統一標準，HK 詞彙獨特性最高。",
    "news": "對照組。正式語體三地用詞高度重疊，殘餘差異應幾乎全部來自字形。",
    "loan": "音譯 vs 意譯的分歧（雷射／激光）：檢驗 BPE 是否偏好某一種造詞策略。",
    "cxg": "構式探針。檢驗 tokenizer 是否把半基模構式、離合詞、重疊式當作單位。",
    "name": "專名。字形受控下最純粹的詞彙效果（川普／特朗普）。",
}

ITEMS: list[Item] = [
    # ---- tech ------------------------------------------------------------
    Item("tech01", "tech", "這個軟體最近更新了介面設計。", "这个软件最近更新了界面设计。",
         "這個軟件最近更新了介面設計。", "This software recently updated its interface design.",
         probe="軟體/软件/軟件", hk_confidence="high"),
    Item("tech02", "tech", "請上傳一段三十秒的影片。", "请上传一段三十秒的视频。",
         "請上載一段三十秒的影片。", "Please upload a 30-second video.",
         probe="上傳/上传/上載", hk_confidence="high"),
    Item("tech03", "tech", "我需要把這份報告列印出來。", "我需要把这份报告打印出来。",
         "我需要把這份報告打印出來。", "I need to print out this report.",
         probe="列印/打印", hk_confidence="medium"),
    Item("tech04", "tech", "滑鼠右鍵點一下就會出現選單。", "鼠标右键点一下就会出现菜单。",
         "滑鼠右鍵撳一下就會出現選單。", "Right-click the mouse and a menu will appear.",
         probe="滑鼠/鼠标；選單/菜单", hk_confidence="low",
         note="撳 is colloquial Cantonese; consider 按 for written HK Chinese."),
    Item("tech05", "tech", "這個程式有一個小錯誤。", "这个程序有一个小错误。",
         "這個程式有一個小錯誤。", "This program has a small bug.",
         probe="程式/程序", hk_confidence="medium"),
    Item("tech06", "tech", "資料庫連線失敗，請檢查網路設定。", "数据库连接失败，请检查网络设置。",
         "資料庫連線失敗，請檢查網絡設定。", "Database connection failed; check the network settings.",
         probe="資料庫/数据库；網路/网络/網絡", hk_confidence="high"),
    Item("tech07", "tech", "把檔案存到隨身碟裡。", "把文件存到U盘里。",
         "把檔案存到手指裡。", "Save the file onto the USB drive.",
         probe="隨身碟/U盘/手指", hk_confidence="low",
         note="HK 手指 is very colloquial; 記憶棒 / USB 手指 may be safer."),

    # ---- daily -----------------------------------------------------------
    Item("daily01", "daily", "我要叫一輛計程車去機場。", "我要叫一辆出租车去机场。",
         "我要叫一輛的士去機場。", "I'm going to take a taxi to the airport.",
         probe="計程車/出租车/的士", hk_confidence="high"),
    Item("daily02", "daily", "夏天最喜歡吃鳳梨。", "夏天最喜欢吃菠萝。",
         "夏天最喜歡吃菠蘿。", "My favourite summer fruit is pineapple.",
         probe="鳳梨/菠萝", hk_confidence="high"),
    Item("daily03", "daily", "晚餐想煮馬鈴薯燉肉。", "晚餐想煮土豆炖肉。",
         "晚餐想煮薯仔燉肉。", "For dinner I want to make potato stew.",
         probe="馬鈴薯/土豆/薯仔", hk_confidence="high"),
    Item("daily04", "daily", "搭捷運大約二十分鐘可以到。", "坐地铁大约二十分钟可以到。",
         "搭港鐵大約二十分鐘可以到。", "It takes about 20 minutes by metro.",
         probe="捷運/地铁/港鐵", hk_confidence="high"),
    Item("daily05", "daily", "轉角的便利商店有賣。", "拐角的便利店有卖。",
         "轉角的便利店有賣。", "The convenience store on the corner sells it.",
         probe="便利商店/便利店", hk_confidence="high"),
    Item("daily06", "daily", "他騎機車去上班。", "他骑摩托车去上班。",
         "他踩電單車去上班。", "He rides a motorbike to work.",
         probe="機車/摩托车/電單車", hk_confidence="medium",
         note="HK 踩 is colloquial; 揸電單車 also possible."),
    Item("daily07", "daily", "冰箱裡還有一罐優格。", "冰箱里还有一罐酸奶。",
         "雪櫃裡還有一罐乳酪。", "There's still a yoghurt in the fridge.",
         probe="優格/酸奶/乳酪；冰箱/雪櫃", hk_confidence="medium"),

    # ---- news (control) --------------------------------------------------
    Item("news01", "news", "政府今日宣布新的環保政策。", "政府今日宣布新的环保政策。",
         "政府今日宣布新的環保政策。", "The government today announced new environmental policies.",
         probe="control: identical lexicon", hk_confidence="high"),
    Item("news02", "news", "教育部公布最新的入學率統計。", "教育部公布最新的入学率统计。",
         "教育局公布最新的入學率統計。", "The education authority released enrolment statistics.",
         probe="教育部/教育局", hk_confidence="high"),
    Item("news03", "news", "總統在記者會上發表重要談話。", "主席在记者会上发表重要谈话。",
         "特首在記者會上發表重要講話。", "The head of state spoke at the press conference.",
         probe="總統/主席/特首", hk_confidence="high"),
    Item("news04", "news", "疫情期間口罩供應穩定。", "疫情期间口罩供应稳定。",
         "疫情期間口罩供應穩定。", "Mask supply was stable during the pandemic.",
         probe="control", hk_confidence="high"),
    Item("news05", "news", "人工智慧的發展引發各界討論。", "人工智能的发展引发各界讨论。",
         "人工智能的發展引發各界討論。", "AI development has sparked wide discussion.",
         probe="人工智慧/人工智能", hk_confidence="high"),
    Item("news06", "news", "法院駁回上訴並維持原判決。", "法院驳回上诉并维持原判决。",
         "法院駁回上訴並維持原判決。", "The court dismissed the appeal and upheld the ruling.",
         probe="control: legal register", hk_confidence="high"),

    # ---- loanwords -------------------------------------------------------
    Item("loan01", "loan", "實驗室新買了一台雷射切割機。", "实验室新买了一台激光切割机。",
         "實驗室新買了一台激光切割機。", "The lab bought a laser cutter.",
         probe="雷射(音譯)/激光(意譯)", hk_confidence="high"),
    Item("loan02", "loan", "她每天都在部落格上寫作。", "她每天都在博客上写作。",
         "她每天都在網誌上寫作。", "She writes on her blog every day.",
         probe="部落格/博客/網誌 — 三種造詞策略", hk_confidence="high"),
    Item("loan03", "loan", "網際網路改變了資訊傳播。", "互联网改变了信息传播。",
         "互聯網改變了資訊傳播。", "The internet changed information flow.",
         probe="網際網路/互联网；資訊/信息", hk_confidence="high"),
    Item("loan04", "loan", "他點了一杯拿鐵和一份三明治。", "他点了一杯拿铁和一份三明治。",
         "他叫咗一杯拿鐵同一份三文治。", "He ordered a latte and a sandwich.",
         probe="三明治/三文治 — 同源音譯的地域分化", hk_confidence="low",
         note="叫咗/同 are written Cantonese; replace with 點了/和 if the HK column must stay in standard written Chinese."),
    Item("loan05", "loan", "這款巧克力用了新的乳化劑。", "这款巧克力用了新的乳化剂。",
         "這款朱古力用了新的乳化劑。", "This chocolate uses a new emulsifier.",
         probe="巧克力/朱古力", hk_confidence="high"),
    Item("loan06", "loan", "維他命和礦物質都要補充。", "维生素和矿物质都要补充。",
         "維他命和礦物質都要補充。", "Take both vitamins and minerals.",
         probe="維他命(音譯)/维生素(意譯)", hk_confidence="high"),

    # ---- constructions ---------------------------------------------------
    Item("cxg01", "cxg", "他越說越生氣，最後乾脆不講了。", "他越说越生气，最后干脆不讲了。",
         "他越講越嬲，最後索性唔講。", "The more he talked the angrier he got.",
         probe="越X越Y 半基模構式", hk_confidence="low",
         note="HK cell here is written Cantonese by design; treat as a separate register condition."),
    Item("cxg02", "cxg", "這本書我一看就懂。", "这本书我一看就懂。",
         "這本書我一睇就明。", "I understood this book at first glance.",
         probe="一X就Y 半基模構式", hk_confidence="low"),
    Item("cxg03", "cxg", "他昨天洗了個澡就睡了。", "他昨天洗了个澡就睡了。",
         "他琴日沖咗個涼就瞓。", "He took a shower yesterday and went to bed.",
         probe="離合詞 洗澡 → 洗了個澡（不連續）", hk_confidence="low"),
    Item("cxg04", "cxg", "我們研究研究再決定。", "我们研究研究再决定。",
         "我哋研究研究先決定。", "Let's think it over before deciding.",
         probe="動詞重疊 VV", hk_confidence="low"),
    Item("cxg05", "cxg", "這件事說起來一言難盡。", "这件事说起来一言难尽。",
         "呢件事講起上嚟一言難盡。", "It's a long story.",
         probe="成語（全實體構式）＋動補", hk_confidence="low"),
    Item("cxg06", "cxg", "他把那份文件放在桌上了。", "他把那份文件放在桌上了。",
         "佢將份文件擺喺枱面。", "He put the document on the desk.",
         probe="把字句", hk_confidence="low"),

    # ---- proper names ----------------------------------------------------
    Item("name01", "name", "川普與拜登再次交鋒。", "特朗普与拜登再次交锋。",
         "特朗普與拜登再次交鋒。", "Trump and Biden clashed again.",
         probe="川普/特朗普", hk_confidence="high"),
    Item("name02", "name", "他下週要飛往雪梨開會。", "他下周要飞往悉尼开会。",
         "他下星期要飛往悉尼開會。", "He flies to Sydney next week for a meeting.",
         probe="雪梨/悉尼", hk_confidence="high"),
    Item("name03", "name", "紐西蘭的乳製品出口成長。", "新西兰的乳制品出口增长。",
         "紐西蘭的乳製品出口增長。", "New Zealand dairy exports grew.",
         probe="紐西蘭/新西兰", hk_confidence="medium"),
    Item("name04", "name", "他最愛的作家是海明威。", "他最爱的作家是海明威。",
         "他最愛的作家是海明威。", "His favourite writer is Hemingway.",
         probe="control: identical transliteration", hk_confidence="high"),
    Item("name05", "name", "梵谷的畫作在奧塞美術館展出。", "梵高的画作在奥赛博物馆展出。",
         "梵高的畫作在奧賽博物館展出。", "Van Gogh's paintings are shown at the Musée d'Orsay.",
         probe="梵谷/梵高", hk_confidence="medium"),
]


def expand(items: list[Item] | None = None) -> list[dict]:
    """Flatten the item bank into one row per (item, script, lexicon) cell."""
    rows = []
    for it in (items or ITEMS):
        for (script, lex), text in it.cells().items():
            rows.append(
                dict(item_id=it.id, category=it.category, script=script,
                     lexicon=lex, text=text, gloss=it.gloss, probe=it.probe,
                     hk_confidence=it.hk_confidence, attested=(
                         (script == "trad" and lex in ("tw", "hk"))
                         or (script == "simp" and lex == "cn")))
            )
    return rows


# --------------------------------------------------------------------------
# Construction probes: minimal pairs, not sentences.  Each pair contrasts a
# canonical (contiguous) realisation with an interrupted / filled realisation
# of the *same* construction.
# --------------------------------------------------------------------------
CONSTRUCTION_PROBES = [
    dict(cx="成語（全實體）", schema="[X Y Z W]", canonical="一石二鳥", variant="一石二鳥",
         note="fully substantive, no slot"),
    dict(cx="成語（全實體）", schema="[X Y Z W]", canonical="畫蛇添足", variant="畫蛇添足"),
    dict(cx="成語（全實體）", schema="[X Y Z W]", canonical="雪中送炭", variant="雪中送炭"),
    dict(cx="越X越Y", schema="越 __ 越 __", canonical="越走越快", variant="越走越快"),
    dict(cx="越X越Y", schema="越 __ 越 __", canonical="越說越氣", variant="越想越不對勁"),
    dict(cx="一X就Y", schema="一 __ 就 __", canonical="一看就懂", variant="一聽到消息就走"),
    dict(cx="離合詞", schema="V __ O", canonical="洗澡", variant="洗了個澡"),
    dict(cx="離合詞", schema="V __ O", canonical="幫忙", variant="幫了他一個忙"),
    dict(cx="離合詞", schema="V __ O", canonical="見面", variant="見過一次面"),
    dict(cx="離合詞", schema="V __ O", canonical="生氣", variant="生他的氣"),
    dict(cx="動詞重疊", schema="V V", canonical="看看", variant="看一看"),
    dict(cx="動詞重疊", schema="V V", canonical="研究研究", variant="研究研究"),
    dict(cx="狀態形容詞 ABB", schema="A B B", canonical="紅通通", variant="紅通通"),
    dict(cx="AABB", schema="A A B B", canonical="高高興興", variant="高高興興"),
    dict(cx="動補 V-R", schema="V R", canonical="看完", variant="看得懂"),
    dict(cx="動補 V-R", schema="V R", canonical="想起來", variant="想不起來"),
    dict(cx="把字句", schema="把 NP V", canonical="把書放好", variant="把那本書放好"),
    dict(cx="連…都…", schema="連 NP 都 V", canonical="連我都知道", variant="連他自己都不知道"),
]
