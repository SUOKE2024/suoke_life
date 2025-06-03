"""
中医知识服务模块
实现中医知识库管理和智能推荐功能
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from ..domain.models import ConstitutionType, ResourceType

logger = logging.getLogger(__name__)

class TCMCategory(Enum):
    """中医知识类别"""

    THEORY = "theory"  # 中医理论
    FORMULA = "formula"  # 方剂
    HERB = "herb"  # 中药
    ACUPOINT = "acupoint"  # 穴位
    SYNDROME = "syndrome"  # 证候
    TREATMENT = "treatment"  # 治法
    DIAGNOSIS = "diagnosis"  # 诊断
    CONSTITUTION = "constitution"  # 体质

class TCMProperty(Enum):
    """中药性味"""

    # 四气
    COLD = "寒"
    COOL = "凉"
    WARM = "温"
    HOT = "热"
    NEUTRAL = "平"

    # 五味
    SWEET = "甘"
    SOUR = "酸"
    BITTER = "苦"
    SPICY = "辛"
    SALTY = "咸"
    BLAND = "淡"

class MeridianType(Enum):
    """经络类型"""

    LUNG = "肺经"
    LARGE_INTESTINE = "大肠经"
    STOMACH = "胃经"
    SPLEEN = "脾经"
    HEART = "心经"
    SMALL_INTESTINE = "小肠经"
    BLADDER = "膀胱经"
    KIDNEY = "肾经"
    PERICARDIUM = "心包经"
    TRIPLE_HEATER = "三焦经"
    GALLBLADDER = "胆经"
    LIVER = "肝经"

@dataclass
class TCMKnowledge:
    """中医知识条目"""

    knowledge_id: str
    name: str
    category: TCMCategory
    description: str
    properties: Dict[str, Any]
    related_constitutions: List[ConstitutionType]
    indications: List[str]
    contraindications: List[str]
    references: List[str]
    created_at: datetime
    updated_at: datetime

@dataclass
class TCMFormula:
    """中医方剂"""

    formula_id: str
    name: str
    alias_names: List[str]
    source: str
    composition: List[Dict[str, Any]]  # 组成药物
    dosage: Dict[str, str]
    preparation: str
    functions: List[str]
    indications: List[str]
    contraindications: List[str]
    modifications: List[Dict[str, Any]]
    related_constitutions: List[ConstitutionType]
    clinical_applications: List[str]
    modern_research: List[str]
    created_at: datetime

@dataclass
class TCMHerb:
    """中药材"""

    herb_id: str
    name: str
    latin_name: str
    alias_names: List[str]
    source: str
    properties: List[TCMProperty]
    meridians: List[MeridianType]
    functions: List[str]
    indications: List[str]
    contraindications: List[str]
    dosage: str
    processing_methods: List[str]
    compatibility: Dict[str, List[str]]  # 配伍
    toxicity: Optional[str]
    modern_pharmacology: List[str]
    quality_standards: Dict[str, Any]
    created_at: datetime

@dataclass
class TCMAcupoint:
    """穴位"""

    acupoint_id: str
    name: str
    code: str
    meridian: MeridianType
    location: str
    anatomy: str
    functions: List[str]
    indications: List[str]
    contraindications: List[str]
    needling_methods: List[Dict[str, Any]]
    moxibustion_methods: List[Dict[str, Any]]
    point_combinations: List[str]
    clinical_applications: List[str]
    precautions: List[str]
    created_at: datetime

@dataclass
class TCMSyndrome:
    """中医证候"""

    syndrome_id: str
    name: str
    category: str
    pathogenesis: str
    clinical_manifestations: List[str]
    tongue_pulse: Dict[str, str]
    treatment_principles: List[str]
    representative_formulas: List[str]
    related_constitutions: List[ConstitutionType]
    differential_diagnosis: List[str]
    prognosis: str
    created_at: datetime

@dataclass
class TCMDiagnosis:
    """中医诊断"""

    diagnosis_id: str
    patient_id: str
    constitution_type: ConstitutionType
    main_syndrome: str
    secondary_syndromes: List[str]
    symptoms: List[str]
    tongue_diagnosis: Dict[str, str]
    pulse_diagnosis: Dict[str, str]
    treatment_principle: str
    recommended_formulas: List[str]
    lifestyle_advice: List[str]
    follow_up_plan: str
    created_at: datetime
    created_by: str

class TCMKnowledgeService:
    """
    中医知识服务

    提供中医知识库管理和智能推荐功能
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # 知识库
        self.formulas: Dict[str, TCMFormula] = {}
        self.herbs: Dict[str, TCMHerb] = {}
        self.acupoints: Dict[str, TCMAcupoint] = {}
        self.syndromes: Dict[str, TCMSyndrome] = {}

        # 索引
        self.constitution_formula_index: Dict[ConstitutionType, List[str]] = {}
        self.symptom_formula_index: Dict[str, List[str]] = {}
        self.herb_function_index: Dict[str, List[str]] = {}
        self.acupoint_indication_index: Dict[str, List[str]] = {}

        # 初始化知识库
        self._initialize_knowledge_base()
        self._build_indexes()

        logger.info("中医知识服务初始化完成")

    def _initialize_knowledge_base(self):
        """初始化知识库"""
        self._initialize_classic_formulas()
        self._initialize_common_herbs()
        self._initialize_important_acupoints()
        self._initialize_common_syndromes()

    def _initialize_classic_formulas(self):
        """初始化经典方剂"""
        # 四君子汤
        self.formulas["四君子汤"] = TCMFormula(
            formula_id="formula_001",
            name="四君子汤",
            alias_names=["四君汤"],
            source="《太平惠民和剂局方》",
            composition=[
                {"herb": "人参", "dosage": "9g", "role": "君药"},
                {"herb": "白术", "dosage": "9g", "role": "臣药"},
                {"herb": "茯苓", "dosage": "9g", "role": "佐药"},
                {"herb": "甘草", "dosage": "6g", "role": "使药"},
            ],
            dosage={"daily": "一日一剂", "method": "水煎服"},
            preparation="水煎服，温服",
            functions=["益气健脾", "补中益气"],
            indications=["脾胃气虚", "食少便溏", "气短乏力", "面色萎白"],
            contraindications=["阴虚内热", "实热证"],
            modifications=[
                {"condition": "食欲不振", "add": ["陈皮", "砂仁"], "remove": []},
                {"condition": "腹胀", "add": ["木香", "枳壳"], "remove": []},
                {"condition": "便溏", "add": ["山药", "扁豆"], "remove": []},
            ],
            related_constitutions=[ConstitutionType.QI_XU],
            clinical_applications=["慢性胃炎", "功能性消化不良", "慢性腹泻"],
            modern_research=["调节胃肠功能", "增强免疫力", "改善营养吸收"],
            created_at=datetime.now(),
        )

        # 六味地黄丸
        self.formulas["六味地黄丸"] = TCMFormula(
            formula_id="formula_002",
            name="六味地黄丸",
            alias_names=["地黄丸"],
            source="《小儿药证直诀》",
            composition=[
                {"herb": "熟地黄", "dosage": "24g", "role": "君药"},
                {"herb": "山茱萸", "dosage": "12g", "role": "臣药"},
                {"herb": "山药", "dosage": "12g", "role": "臣药"},
                {"herb": "泽泻", "dosage": "9g", "role": "佐药"},
                {"herb": "茯苓", "dosage": "9g", "role": "佐药"},
                {"herb": "牡丹皮", "dosage": "9g", "role": "佐药"},
            ],
            dosage={"daily": "一日两次", "method": "温开水送服"},
            preparation="蜜丸，每丸9g",
            functions=["滋阴补肾", "填精益髓"],
            indications=["肾阴虚", "腰膝酸软", "头晕耳鸣", "盗汗遗精"],
            contraindications=["脾胃虚弱", "痰湿内盛"],
            modifications=[
                {"condition": "阴虚火旺", "add": ["知母", "黄柏"], "remove": []},
                {"condition": "肾阳虚", "add": ["肉桂", "附子"], "remove": []},
                {"condition": "气虚", "add": ["人参", "黄芪"], "remove": []},
            ],
            related_constitutions=[ConstitutionType.YIN_XU],
            clinical_applications=["慢性肾炎", "糖尿病", "高血压", "更年期综合征"],
            modern_research=["调节内分泌", "抗衰老", "保护肾功能"],
            created_at=datetime.now(),
        )

        # 逍遥散
        self.formulas["逍遥散"] = TCMFormula(
            formula_id="formula_003",
            name="逍遥散",
            alias_names=["逍遥丸"],
            source="《太平惠民和剂局方》",
            composition=[
                {"herb": "柴胡", "dosage": "9g", "role": "君药"},
                {"herb": "当归", "dosage": "9g", "role": "臣药"},
                {"herb": "白芍", "dosage": "9g", "role": "臣药"},
                {"herb": "白术", "dosage": "9g", "role": "佐药"},
                {"herb": "茯苓", "dosage": "9g", "role": "佐药"},
                {"herb": "甘草", "dosage": "6g", "role": "使药"},
                {"herb": "薄荷", "dosage": "3g", "role": "佐药"},
                {"herb": "生姜", "dosage": "3g", "role": "佐药"},
            ],
            dosage={"daily": "一日一剂", "method": "水煎服"},
            preparation="水煎服，温服",
            functions=["疏肝解郁", "健脾和血"],
            indications=["肝郁脾虚", "胸胁胀痛", "头痛目眩", "月经不调"],
            contraindications=["肝阳上亢", "阴虚火旺"],
            modifications=[
                {"condition": "郁火", "add": ["栀子", "牡丹皮"], "remove": []},
                {"condition": "血虚", "add": ["熟地", "何首乌"], "remove": []},
                {"condition": "气滞", "add": ["香附", "青皮"], "remove": []},
            ],
            related_constitutions=[ConstitutionType.QI_YU],
            clinical_applications=["抑郁症", "月经不调", "慢性肝炎", "胃炎"],
            modern_research=["调节神经内分泌", "抗抑郁", "保肝"],
            created_at=datetime.now(),
        )

        # 二陈汤
        self.formulas["二陈汤"] = TCMFormula(
            formula_id="formula_004",
            name="二陈汤",
            alias_names=["二陈丸"],
            source="《太平惠民和剂局方》",
            composition=[
                {"herb": "半夏", "dosage": "15g", "role": "君药"},
                {"herb": "陈皮", "dosage": "15g", "role": "君药"},
                {"herb": "茯苓", "dosage": "9g", "role": "臣药"},
                {"herb": "甘草", "dosage": "4.5g", "role": "使药"},
            ],
            dosage={"daily": "一日一剂", "method": "水煎服"},
            preparation="水煎服，温服",
            functions=["燥湿化痰", "理气和中"],
            indications=["湿痰咳嗽", "痰多色白", "胸脘痞闷", "恶心呕吐"],
            contraindications=["阴虚燥咳", "热痰"],
            modifications=[
                {"condition": "寒痰", "add": ["干姜", "细辛"], "remove": []},
                {"condition": "热痰", "add": ["黄芩", "瓜蒌"], "remove": []},
                {"condition": "顽痰", "add": ["南星", "白附子"], "remove": []},
            ],
            related_constitutions=[ConstitutionType.TAN_SHI],
            clinical_applications=["慢性支气管炎", "慢性胃炎", "梅核气"],
            modern_research=["祛痰止咳", "调节胃肠功能", "抗炎"],
            created_at=datetime.now(),
        )

        # 龙胆泻肝汤
        self.formulas["龙胆泻肝汤"] = TCMFormula(
            formula_id="formula_005",
            name="龙胆泻肝汤",
            alias_names=["龙胆汤"],
            source="《医方集解》",
            composition=[
                {"herb": "龙胆草", "dosage": "6g", "role": "君药"},
                {"herb": "黄芩", "dosage": "9g", "role": "臣药"},
                {"herb": "栀子", "dosage": "9g", "role": "臣药"},
                {"herb": "泽泻", "dosage": "12g", "role": "佐药"},
                {"herb": "木通", "dosage": "6g", "role": "佐药"},
                {"herb": "车前子", "dosage": "9g", "role": "佐药"},
                {"herb": "当归", "dosage": "3g", "role": "佐药"},
                {"herb": "生地黄", "dosage": "9g", "role": "佐药"},
                {"herb": "柴胡", "dosage": "6g", "role": "使药"},
                {"herb": "甘草", "dosage": "6g", "role": "使药"},
            ],
            dosage={"daily": "一日一剂", "method": "水煎服"},
            preparation="水煎服，温服",
            functions=["清热泻火", "利湿退黄"],
            indications=["肝胆湿热", "胁痛口苦", "耳聋耳肿", "湿疹阴痒"],
            contraindications=["脾胃虚寒", "肾阳虚"],
            modifications=[
                {"condition": "湿重", "add": ["茵陈", "薏苡仁"], "remove": []},
                {"condition": "热重", "add": ["黄连", "黄柏"], "remove": []},
                {"condition": "阴虚", "add": ["麦冬", "玄参"], "remove": []},
            ],
            related_constitutions=[ConstitutionType.SHI_RE],
            clinical_applications=["急性肝炎", "胆囊炎", "泌尿系感染", "湿疹"],
            modern_research=["抗炎", "利胆", "抗菌", "保肝"],
            created_at=datetime.now(),
        )

    def _initialize_common_herbs(self):
        """初始化常用中药"""
        # 人参
        self.herbs["人参"] = TCMHerb(
            herb_id="herb_001",
            name="人参",
            latin_name="Panax ginseng C.A.Mey.",
            alias_names=["吉林参", "棒槌", "神草"],
            source="五加科植物人参的干燥根",
            properties=[TCMProperty.SWEET, TCMProperty.NEUTRAL],
            meridians=[MeridianType.SPLEEN, MeridianType.LUNG, MeridianType.HEART],
            functions=["大补元气", "复脉固脱", "补脾益肺", "生津安神"],
            indications=["气虚欲脱", "脾肺气虚", "热病伤津", "心神不安"],
            contraindications=["实热证", "湿热证", "正虚邪实证"],
            dosage="3-9g，另煎兑服",
            processing_methods=["生晒参", "红参", "糖参"],
            compatibility={
                "相须": ["黄芪", "白术", "茯苓"],
                "相使": ["附子", "干姜"],
                "相畏": ["莱菔子"],
                "相恶": ["五灵脂"],
                "相反": ["藜芦"],
            },
            toxicity="无明显毒性，过量可致人参滥用综合征",
            modern_pharmacology=["增强免疫", "抗疲劳", "调节血糖", "保护心脑血管"],
            quality_standards={"人参皂苷": "≥0.20%", "水分": "≤13.0%"},
            created_at=datetime.now(),
        )

        # 黄芪
        self.herbs["黄芪"] = TCMHerb(
            herb_id="herb_002",
            name="黄芪",
            latin_name="Astragalus membranaceus (Fisch.) Bunge",
            alias_names=["绵芪", "黄耆", "独椹"],
            source="豆科植物蒙古黄芪或膜荚黄芪的干燥根",
            properties=[TCMProperty.SWEET, TCMProperty.WARM],
            meridians=[MeridianType.SPLEEN, MeridianType.LUNG],
            functions=["补气升阳", "固表止汗", "利水消肿", "生肌"],
            indications=["气虚乏力", "中气下陷", "久泻脱肛", "表虚自汗"],
            contraindications=["表实邪盛", "气滞湿阻", "阴虚阳亢"],
            dosage="9-30g",
            processing_methods=["生黄芪", "蜜炙黄芪"],
            compatibility={
                "相须": ["人参", "白术", "当归"],
                "相使": ["升麻", "柴胡"],
                "相畏": [],
                "相恶": [],
                "相反": [],
            },
            toxicity="无明显毒性",
            modern_pharmacology=["增强免疫", "抗疲劳", "保护心脏", "抗衰老"],
            quality_standards={"黄芪甲苷": "≥0.040%", "水分": "≤15.0%"},
            created_at=datetime.now(),
        )

        # 当归
        self.herbs["当归"] = TCMHerb(
            herb_id="herb_003",
            name="当归",
            latin_name="Angelica sinensis (Oliv.) Diels",
            alias_names=["秦归", "云归", "西当归"],
            source="伞形科植物当归的干燥根",
            properties=[TCMProperty.SWEET, TCMProperty.SPICY, TCMProperty.WARM],
            meridians=[MeridianType.LIVER, MeridianType.HEART, MeridianType.SPLEEN],
            functions=["补血活血", "调经止痛", "润肠通便"],
            indications=["血虚萎黄", "月经不调", "经闭痛经", "肠燥便秘"],
            contraindications=["湿盛中满", "大便溏泄"],
            dosage="6-12g",
            processing_methods=["当归头", "当归身", "当归尾", "全当归"],
            compatibility={
                "相须": ["熟地", "白芍", "川芎"],
                "相使": ["黄芪", "人参"],
                "相畏": [],
                "相恶": ["湿面"],
                "相反": [],
            },
            toxicity="无明显毒性",
            modern_pharmacology=["补血", "调节免疫", "抗血栓", "保护肝脏"],
            quality_standards={"阿魏酸": "≥0.050%", "水分": "≤15.0%"},
            created_at=datetime.now(),
        )

        # 甘草
        self.herbs["甘草"] = TCMHerb(
            herb_id="herb_004",
            name="甘草",
            latin_name="Glycyrrhiza uralensis Fisch.",
            alias_names=["国老", "甜草", "蜜草"],
            source="豆科植物甘草、胀果甘草或光果甘草的干燥根和根茎",
            properties=[TCMProperty.SWEET, TCMProperty.NEUTRAL],
            meridians=[
                MeridianType.HEART,
                MeridianType.LUNG,
                MeridianType.SPLEEN,
                MeridianType.STOMACH,
            ],
            functions=["补脾益气", "清热解毒", "祛痰止咳", "缓急止痛", "调和诸药"],
            indications=["脾胃虚弱", "倦怠乏力", "心悸气短", "咳嗽痰多"],
            contraindications=["湿盛胀满", "浮肿"],
            dosage="2-10g",
            processing_methods=["生甘草", "蜜炙甘草"],
            compatibility={
                "相须": ["人参", "白术", "茯苓"],
                "相使": ["大部分中药"],
                "相畏": [],
                "相恶": ["大戟", "芫花", "甘遂", "海藻"],
                "相反": [],
            },
            toxicity="大剂量长期使用可致假性醛固酮增多症",
            modern_pharmacology=["抗炎", "抗病毒", "保护胃黏膜", "调节免疫"],
            quality_standards={"甘草酸": "≥2.0%", "水分": "≤15.0%"},
            created_at=datetime.now(),
        )

        # 柴胡
        self.herbs["柴胡"] = TCMHerb(
            herb_id="herb_005",
            name="柴胡",
            latin_name="Bupleurum chinense DC.",
            alias_names=["北柴胡", "南柴胡", "软柴胡"],
            source="伞形科植物柴胡或狭叶柴胡的干燥根",
            properties=[TCMProperty.BITTER, TCMProperty.SPICY, TCMProperty.COOL],
            meridians=[
                MeridianType.LIVER,
                MeridianType.GALLBLADDER,
                MeridianType.TRIPLE_HEATER,
            ],
            functions=["疏散退热", "疏肝解郁", "升举阳气"],
            indications=["感冒发热", "寒热往来", "胸胁胀痛", "月经不调"],
            contraindications=["肝阳上亢", "阴虚火旺"],
            dosage="3-12g",
            processing_methods=["生柴胡", "醋柴胡", "鳖血柴胡"],
            compatibility={
                "相须": ["黄芩", "半夏", "人参"],
                "相使": ["白芍", "当归"],
                "相畏": [],
                "相恶": [],
                "相反": [],
            },
            toxicity="无明显毒性",
            modern_pharmacology=["解热", "抗炎", "保肝", "抗抑郁"],
            quality_standards={"柴胡皂苷a": "≥0.30%", "水分": "≤13.0%"},
            created_at=datetime.now(),
        )

    def _initialize_important_acupoints(self):
        """初始化重要穴位"""
        # 足三里
        self.acupoints["足三里"] = TCMAcupoint(
            acupoint_id="acu_001",
            name="足三里",
            code="ST36",
            meridian=MeridianType.STOMACH,
            location="小腿前外侧，当犊鼻下3寸，距胫骨前缘一横指（中指）",
            anatomy="在胫骨前肌中；有胫前动、静脉；布有腓肠外侧皮神经，深层为腓深神经",
            functions=["调理脾胃", "补中益气", "通经活络", "扶正祛邪"],
            indications=["胃痛", "呕吐", "腹胀", "腹泻", "便秘", "下肢痿痹"],
            contraindications=["孕妇慎用"],
            needling_methods=[
                {"method": "直刺", "depth": "1-2寸", "sensation": "酸胀感向足背放散"},
                {"method": "斜刺", "depth": "1.5寸", "direction": "向下"},
            ],
            moxibustion_methods=[
                {"method": "艾炷灸", "quantity": "3-7壮"},
                {"method": "艾条灸", "duration": "10-20分钟"},
            ],
            point_combinations=["内关", "中脘", "天枢", "三阴交"],
            clinical_applications=["消化系统疾病", "免疫系统疾病", "神经系统疾病"],
            precautions=["针刺不宜过深", "避免刺伤血管"],
            created_at=datetime.now(),
        )

        # 内关
        self.acupoints["内关"] = TCMAcupoint(
            acupoint_id="acu_002",
            name="内关",
            code="PC6",
            meridian=MeridianType.PERICARDIUM,
            location="前臂掌侧，当曲泽与大陵的连线上，腕横纹上2寸，掌长肌腱与桡侧腕屈肌腱之间",
            anatomy="在掌长肌腱与桡侧腕屈肌腱之间，有指浅屈肌，深层为指深屈肌；有前臂正中动、静脉，深层为前臂掌侧骨间动、静脉；布有前臂内侧皮神经，下为正中神经掌皮支，最深层为前臂掌侧骨间神经",
            functions=["宁心安神", "理气止痛", "和胃降逆"],
            indications=["心痛", "心悸", "胸痛", "胃痛", "呕吐", "失眠"],
            contraindications=["无特殊禁忌"],
            needling_methods=[
                {"method": "直刺", "depth": "0.5-1寸", "sensation": "酸胀感向指端放散"},
                {"method": "向上斜刺", "depth": "1寸", "direction": "向肘部"},
            ],
            moxibustion_methods=[{"method": "艾条灸", "duration": "10-15分钟"}],
            point_combinations=["足三里", "神门", "三阴交", "太冲"],
            clinical_applications=["心血管疾病", "消化系统疾病", "神经系统疾病"],
            precautions=["针刺不宜过深", "避免刺伤正中神经"],
            created_at=datetime.now(),
        )

        # 百会
        self.acupoints["百会"] = TCMAcupoint(
            acupoint_id="acu_003",
            name="百会",
            code="GV20",
            meridian=MeridianType.GALLBLADDER,  # 督脉，这里用胆经代替
            location="头部，当前发际正中直上5寸，或两耳尖连线的中点处",
            anatomy="在帽状腱膜中；有左右颞浅动、静脉吻合网；布有枕大神经分支",
            functions=["升阳举陷", "益气固脱", "安神定志"],
            indications=["头痛", "眩晕", "中风", "癫痫", "失眠", "健忘"],
            contraindications=["婴幼儿囟门未闭者禁针"],
            needling_methods=[
                {"method": "平刺", "depth": "0.5-0.8寸", "direction": "向前或向后"},
                {"method": "点刺", "depth": "浅刺", "method": "三棱针"},
            ],
            moxibustion_methods=[
                {"method": "艾条灸", "duration": "10-20分钟"},
                {"method": "艾炷灸", "quantity": "3-5壮"},
            ],
            point_combinations=["神门", "三阴交", "太冲", "印堂"],
            clinical_applications=["神经系统疾病", "精神疾病", "内分泌疾病"],
            precautions=["针刺不宜过深", "避免刺伤脑组织"],
            created_at=datetime.now(),
        )

        # 三阴交
        self.acupoints["三阴交"] = TCMAcupoint(
            acupoint_id="acu_004",
            name="三阴交",
            code="SP6",
            meridian=MeridianType.SPLEEN,
            location="小腿内侧，当足内踝尖上3寸，胫骨内侧缘后方",
            anatomy="在胫骨后肌和趾长屈肌之间；有大隐静脉，胫后动、静脉；布有小腿内侧皮神经，深层后方为胫神经",
            functions=["健脾益血", "调肝补肾", "安神"],
            indications=["腹胀", "腹泻", "月经不调", "带下", "遗精", "失眠"],
            contraindications=["孕妇禁针"],
            needling_methods=[
                {"method": "直刺", "depth": "1-1.5寸", "sensation": "酸胀感"},
                {"method": "向上斜刺", "depth": "1寸", "direction": "沿胫骨后缘"},
            ],
            moxibustion_methods=[
                {"method": "艾条灸", "duration": "10-20分钟"},
                {"method": "艾炷灸", "quantity": "3-7壮"},
            ],
            point_combinations=["足三里", "内关", "关元", "血海"],
            clinical_applications=["妇科疾病", "消化系统疾病", "泌尿生殖系统疾病"],
            precautions=["孕妇禁用", "针刺不宜过深"],
            created_at=datetime.now(),
        )

        # 合谷
        self.acupoints["合谷"] = TCMAcupoint(
            acupoint_id="acu_005",
            name="合谷",
            code="LI4",
            meridian=MeridianType.LARGE_INTESTINE,
            location="手背，第1、2掌骨间，当第二掌骨桡侧的中点处",
            anatomy="在第一骨间背侧肌中，深层有拇收肌横头；有手背静脉网，近腕侧有桡动脉从手背穿向手掌；布有桡神经浅支的掌背侧神经，深层有正中神经的指掌侧固有神经",
            functions=["镇静止痛", "通经活络", "清热解表"],
            indications=["头痛", "齿痛", "咽喉肿痛", "感冒发热", "便秘"],
            contraindications=["孕妇慎用"],
            needling_methods=[
                {"method": "直刺", "depth": "0.5-1寸", "sensation": "酸胀感向食指放散"},
                {"method": "向小指方向斜刺", "depth": "0.8寸"},
            ],
            moxibustion_methods=[{"method": "艾条灸", "duration": "5-10分钟"}],
            point_combinations=["太冲", "列缺", "迎香", "曲池"],
            clinical_applications=["头面部疾病", "感冒", "消化系统疾病"],
            precautions=["孕妇慎用", "针刺不宜过深"],
            created_at=datetime.now(),
        )

    def _initialize_common_syndromes(self):
        """初始化常见证候"""
        # 脾胃虚弱证
        self.syndromes["脾胃虚弱证"] = TCMSyndrome(
            syndrome_id="syn_001",
            name="脾胃虚弱证",
            category="脏腑辨证",
            pathogenesis="脾胃虚弱，运化失司，清阳不升，浊阴不降",
            clinical_manifestations=[
                "食少纳呆",
                "腹胀",
                "便溏",
                "倦怠乏力",
                "面色萎黄",
                "形体消瘦",
                "四肢不温",
                "少气懒言",
            ],
            tongue_pulse={"舌象": "舌淡苔白", "脉象": "脉细弱"},
            treatment_principles=["健脾益气", "和胃化湿"],
            representative_formulas=["四君子汤", "参苓白术散", "补中益气汤"],
            related_constitutions=[ConstitutionType.QI_XU],
            differential_diagnosis=["胃阴虚证", "脾阳虚证", "胃气虚证"],
            prognosis="调理得当，预后良好",
            created_at=datetime.now(),
        )

        # 肝郁气滞证
        self.syndromes["肝郁气滞证"] = TCMSyndrome(
            syndrome_id="syn_002",
            name="肝郁气滞证",
            category="脏腑辨证",
            pathogenesis="情志不遂，肝失疏泄，气机郁滞",
            clinical_manifestations=[
                "胸胁胀痛",
                "善太息",
                "情志抑郁",
                "易怒",
                "咽中如有物阻",
                "或颈部瘿瘤",
                "妇女可见乳房胀痛",
                "月经不调",
            ],
            tongue_pulse={"舌象": "舌苔薄白", "脉象": "脉弦"},
            treatment_principles=["疏肝理气", "调畅气机"],
            representative_formulas=["逍遥散", "柴胡疏肝散", "甘麦大枣汤"],
            related_constitutions=[ConstitutionType.QI_YU],
            differential_diagnosis=["肝火上炎证", "肝阳上亢证", "肝血虚证"],
            prognosis="疏肝理气，预后较好",
            created_at=datetime.now(),
        )

        # 肾阴虚证
        self.syndromes["肾阴虚证"] = TCMSyndrome(
            syndrome_id="syn_003",
            name="肾阴虚证",
            category="脏腑辨证",
            pathogenesis="肾阴亏虚，虚火内扰，阴不制阳",
            clinical_manifestations=[
                "腰膝酸软",
                "头晕耳鸣",
                "失眠多梦",
                "五心烦热",
                "盗汗",
                "口干咽燥",
                "形体消瘦",
                "男子遗精",
                "女子经少",
            ],
            tongue_pulse={"舌象": "舌红少苔", "脉象": "脉细数"},
            treatment_principles=["滋阴补肾", "清虚热"],
            representative_formulas=["六味地黄丸", "知柏地黄丸", "左归丸"],
            related_constitutions=[ConstitutionType.YIN_XU],
            differential_diagnosis=["肾阳虚证", "肝肾阴虚证", "心肾不交证"],
            prognosis="滋阴补肾，预后良好",
            created_at=datetime.now(),
        )

        # 痰湿内阻证
        self.syndromes["痰湿内阻证"] = TCMSyndrome(
            syndrome_id="syn_004",
            name="痰湿内阻证",
            category="病理产物辨证",
            pathogenesis="脾失健运，水湿内停，聚湿成痰，痰湿内阻",
            clinical_manifestations=[
                "胸脘痞闷",
                "恶心呕吐",
                "食少多寐",
                "头重如裹",
                "身重困倦",
                "或见眩晕",
                "心悸",
                "咳嗽痰多",
            ],
            tongue_pulse={"舌象": "舌淡胖苔白腻", "脉象": "脉滑"},
            treatment_principles=["健脾化湿", "理气化痰"],
            representative_formulas=["二陈汤", "平胃散", "温胆汤"],
            related_constitutions=[ConstitutionType.TAN_SHI],
            differential_diagnosis=["寒湿困脾证", "湿热蕴脾证", "痰火扰心证"],
            prognosis="化痰除湿，预后良好",
            created_at=datetime.now(),
        )

        # 湿热蕴结证
        self.syndromes["湿热蕴结证"] = TCMSyndrome(
            syndrome_id="syn_005",
            name="湿热蕴结证",
            category="病理产物辨证",
            pathogenesis="湿热之邪蕴结体内，湿热互结，缠绵难愈",
            clinical_manifestations=[
                "身热不扬",
                "头身困重",
                "胸脘痞闷",
                "恶心厌食",
                "口苦口黏",
                "渴不多饮",
                "小便短赤",
                "大便不爽",
            ],
            tongue_pulse={"舌象": "舌红苔黄腻", "脉象": "脉滑数"},
            treatment_principles=["清热利湿", "分消走泄"],
            representative_formulas=["龙胆泻肝汤", "茵陈蒿汤", "三仁汤"],
            related_constitutions=[ConstitutionType.SHI_RE],
            differential_diagnosis=["湿温证", "暑湿证", "肝胆湿热证"],
            prognosis="清热利湿，预后较好",
            created_at=datetime.now(),
        )

    def _build_indexes(self):
        """构建索引"""
        # 构建体质-方剂索引
        for formula_name, formula in self.formulas.items():
            for constitution in formula.related_constitutions:
                if constitution not in self.constitution_formula_index:
                    self.constitution_formula_index[constitution] = []
                self.constitution_formula_index[constitution].append(formula_name)

        # 构建症状-方剂索引
        for formula_name, formula in self.formulas.items():
            for indication in formula.indications:
                if indication not in self.symptom_formula_index:
                    self.symptom_formula_index[indication] = []
                self.symptom_formula_index[indication].append(formula_name)

        # 构建功效-中药索引
        for herb_name, herb in self.herbs.items():
            for function in herb.functions:
                if function not in self.herb_function_index:
                    self.herb_function_index[function] = []
                self.herb_function_index[function].append(herb_name)

        # 构建主治-穴位索引
        for acupoint_name, acupoint in self.acupoints.items():
            for indication in acupoint.indications:
                if indication not in self.acupoint_indication_index:
                    self.acupoint_indication_index[indication] = []
                self.acupoint_indication_index[indication].append(acupoint_name)

    async def search_knowledge(
        self,
        query: str,
        category: Optional[TCMCategory] = None,
        constitution: Optional[ConstitutionType] = None,
    ) -> List[Dict[str, Any]]:
        """搜索中医知识"""
        try:
            results = []

            # 搜索方剂
            if not category or category == TCMCategory.FORMULA:
                for formula_name, formula in self.formulas.items():
                    if self._match_query(
                        query, formula.name, *formula.alias_names, *formula.indications
                    ):
                        if (
                            not constitution
                            or constitution in formula.related_constitutions
                        ):
                            results.append(
                                {
                                    "type": "formula",
                                    "id": formula.formula_id,
                                    "name": formula.name,
                                    "description": f"功效：{', '.join(formula.functions)}",
                                    "indications": formula.indications,
                                    "source": formula.source,
                                    "relevance_score": self._calculate_relevance_score(
                                        query, formula
                                    ),
                                }
                            )

            # 搜索中药
            if not category or category == TCMCategory.HERB:
                for herb_name, herb in self.herbs.items():
                    if self._match_query(
                        query, herb.name, *herb.alias_names, *herb.functions
                    ):
                        results.append(
                            {
                                "type": "herb",
                                "id": herb.herb_id,
                                "name": herb.name,
                                "description": f"性味：{', '.join([p.value for p in herb.properties])}",
                                "functions": herb.functions,
                                "indications": herb.indications,
                                "relevance_score": self._calculate_relevance_score(
                                    query, herb
                                ),
                            }
                        )

            # 搜索穴位
            if not category or category == TCMCategory.ACUPOINT:
                for acupoint_name, acupoint in self.acupoints.items():
                    if self._match_query(
                        query, acupoint.name, acupoint.code, *acupoint.indications
                    ):
                        results.append(
                            {
                                "type": "acupoint",
                                "id": acupoint.acupoint_id,
                                "name": acupoint.name,
                                "code": acupoint.code,
                                "description": f"归经：{acupoint.meridian.value}",
                                "functions": acupoint.functions,
                                "indications": acupoint.indications,
                                "relevance_score": self._calculate_relevance_score(
                                    query, acupoint
                                ),
                            }
                        )

            # 搜索证候
            if not category or category == TCMCategory.SYNDROME:
                for syndrome_name, syndrome in self.syndromes.items():
                    if self._match_query(
                        query, syndrome.name, *syndrome.clinical_manifestations
                    ):
                        if (
                            not constitution
                            or constitution in syndrome.related_constitutions
                        ):
                            results.append(
                                {
                                    "type": "syndrome",
                                    "id": syndrome.syndrome_id,
                                    "name": syndrome.name,
                                    "description": syndrome.pathogenesis,
                                    "manifestations": syndrome.clinical_manifestations,
                                    "treatment": syndrome.treatment_principles,
                                    "relevance_score": self._calculate_relevance_score(
                                        query, syndrome
                                    ),
                                }
                            )

            # 按相关性排序
            results.sort(key=lambda x: x["relevance_score"], reverse=True)

            return results[:20]  # 返回前20个结果

        except Exception as e:
            logger.error(f"搜索中医知识失败: {e}")
            return []

    def _match_query(self, query: str, *fields) -> bool:
        """匹配查询条件"""
        query_lower = query.lower()
        for field in fields:
            if field and query_lower in field.lower():
                return True
        return False

    def _calculate_relevance_score(self, query: str, item: Any) -> float:
        """计算相关性分数"""
        score = 0.0
        query_lower = query.lower()

        # 名称匹配
        if hasattr(item, "name") and query_lower in item.name.lower():
            score += 1.0

        # 别名匹配
        if hasattr(item, "alias_names"):
            for alias in item.alias_names:
                if query_lower in alias.lower():
                    score += 0.8
                    break

        # 功效/功能匹配
        if hasattr(item, "functions"):
            for function in item.functions:
                if query_lower in function.lower():
                    score += 0.6
                    break

        # 主治/适应症匹配
        if hasattr(item, "indications"):
            for indication in item.indications:
                if query_lower in indication.lower():
                    score += 0.5
                    break

        # 临床表现匹配（证候）
        if hasattr(item, "clinical_manifestations"):
            for manifestation in item.clinical_manifestations:
                if query_lower in manifestation.lower():
                    score += 0.4
                    break

        return score

    async def get_formula_details(self, formula_id: str) -> Optional[Dict[str, Any]]:
        """获取方剂详情"""
        for formula in self.formulas.values():
            if formula.formula_id == formula_id:
                return {
                    "formula_id": formula.formula_id,
                    "name": formula.name,
                    "alias_names": formula.alias_names,
                    "source": formula.source,
                    "composition": formula.composition,
                    "dosage": formula.dosage,
                    "preparation": formula.preparation,
                    "functions": formula.functions,
                    "indications": formula.indications,
                    "contraindications": formula.contraindications,
                    "modifications": formula.modifications,
                    "related_constitutions": [
                        c.value for c in formula.related_constitutions
                    ],
                    "clinical_applications": formula.clinical_applications,
                    "modern_research": formula.modern_research,
                }
        return None

    async def get_herb_details(self, herb_id: str) -> Optional[Dict[str, Any]]:
        """获取中药详情"""
        for herb in self.herbs.values():
            if herb.herb_id == herb_id:
                return {
                    "herb_id": herb.herb_id,
                    "name": herb.name,
                    "latin_name": herb.latin_name,
                    "alias_names": herb.alias_names,
                    "source": herb.source,
                    "properties": [p.value for p in herb.properties],
                    "meridians": [m.value for m in herb.meridians],
                    "functions": herb.functions,
                    "indications": herb.indications,
                    "contraindications": herb.contraindications,
                    "dosage": herb.dosage,
                    "processing_methods": herb.processing_methods,
                    "compatibility": herb.compatibility,
                    "toxicity": herb.toxicity,
                    "modern_pharmacology": herb.modern_pharmacology,
                    "quality_standards": herb.quality_standards,
                }
        return None

    async def get_acupoint_details(self, acupoint_id: str) -> Optional[Dict[str, Any]]:
        """获取穴位详情"""
        for acupoint in self.acupoints.values():
            if acupoint.acupoint_id == acupoint_id:
                return {
                    "acupoint_id": acupoint.acupoint_id,
                    "name": acupoint.name,
                    "code": acupoint.code,
                    "meridian": acupoint.meridian.value,
                    "location": acupoint.location,
                    "anatomy": acupoint.anatomy,
                    "functions": acupoint.functions,
                    "indications": acupoint.indications,
                    "contraindications": acupoint.contraindications,
                    "needling_methods": acupoint.needling_methods,
                    "moxibustion_methods": acupoint.moxibustion_methods,
                    "point_combinations": acupoint.point_combinations,
                    "clinical_applications": acupoint.clinical_applications,
                    "precautions": acupoint.precautions,
                }
        return None

    async def recommend_treatment(
        self,
        constitution_type: ConstitutionType,
        symptoms: List[str],
        syndrome: Optional[str] = None,
    ) -> Dict[str, Any]:
        """推荐治疗方案"""
        try:
            recommendations = {
                "constitution_type": constitution_type.value,
                "symptoms": symptoms,
                "syndrome": syndrome,
                "recommended_formulas": [],
                "recommended_herbs": [],
                "recommended_acupoints": [],
                "lifestyle_advice": [],
                "treatment_principles": [],
            }

            # 推荐方剂
            constitution_formulas = self.constitution_formula_index.get(
                constitution_type, []
            )
            for formula_name in constitution_formulas:
                formula = self.formulas[formula_name]
                match_score = self._calculate_symptom_match(
                    symptoms, formula.indications
                )
                if match_score > 0.3:
                    recommendations["recommended_formulas"].append(
                        {
                            "name": formula.name,
                            "functions": formula.functions,
                            "match_score": match_score,
                            "composition": formula.composition[:4],  # 只显示前4味药
                        }
                    )

            # 推荐中药
            for symptom in symptoms:
                if symptom in self.herb_function_index:
                    for herb_name in self.herb_function_index[symptom][:3]:
                        herb = self.herbs[herb_name]
                        recommendations["recommended_herbs"].append(
                            {
                                "name": herb.name,
                                "functions": herb.functions,
                                "properties": [p.value for p in herb.properties],
                            }
                        )

            # 推荐穴位
            for symptom in symptoms:
                if symptom in self.acupoint_indication_index:
                    for acupoint_name in self.acupoint_indication_index[symptom][:3]:
                        acupoint = self.acupoints[acupoint_name]
                        recommendations["recommended_acupoints"].append(
                            {
                                "name": acupoint.name,
                                "code": acupoint.code,
                                "functions": acupoint.functions,
                                "location": acupoint.location,
                            }
                        )

            # 生成生活建议
            recommendations["lifestyle_advice"] = self._generate_lifestyle_advice(
                constitution_type
            )

            # 生成治疗原则
            if syndrome and syndrome in self.syndromes:
                syndrome_obj = self.syndromes[syndrome]
                recommendations["treatment_principles"] = (
                    syndrome_obj.treatment_principles
                )

            # 去重和排序
            recommendations["recommended_formulas"] = sorted(
                recommendations["recommended_formulas"],
                key=lambda x: x["match_score"],
                reverse=True,
            )[:5]

            # 去重
            seen_herbs = set()
            unique_herbs = []
            for herb in recommendations["recommended_herbs"]:
                if herb["name"] not in seen_herbs:
                    seen_herbs.add(herb["name"])
                    unique_herbs.append(herb)
            recommendations["recommended_herbs"] = unique_herbs[:5]

            seen_acupoints = set()
            unique_acupoints = []
            for acupoint in recommendations["recommended_acupoints"]:
                if acupoint["name"] not in seen_acupoints:
                    seen_acupoints.add(acupoint["name"])
                    unique_acupoints.append(acupoint)
            recommendations["recommended_acupoints"] = unique_acupoints[:5]

            return recommendations

        except Exception as e:
            logger.error(f"推荐治疗方案失败: {e}")
            return {}

    def _calculate_symptom_match(
        self, symptoms: List[str], indications: List[str]
    ) -> float:
        """计算症状匹配度"""
        if not symptoms or not indications:
            return 0.0

        matches = 0
        for symptom in symptoms:
            for indication in indications:
                if symptom in indication or indication in symptom:
                    matches += 1
                    break

        return matches / len(symptoms)

    def _generate_lifestyle_advice(
        self, constitution_type: ConstitutionType
    ) -> List[str]:
        """生成生活建议"""
        advice_map = {
            ConstitutionType.QI_XU: [
                "适当运动，如散步、太极拳等",
                "保证充足睡眠，避免熬夜",
                "饮食宜温热，少食生冷",
                "保持心情愉快，避免过度劳累",
                "可常食用人参、黄芪等补气食材",
            ],
            ConstitutionType.YANG_XU: [
                "注意保暖，避免受寒",
                "适当进行温和运动",
                "饮食宜温热，多食温阳食物",
                "避免过度出汗",
                "可食用羊肉、韭菜、生姜等温阳食材",
            ],
            ConstitutionType.YIN_XU: [
                "避免熬夜，保证充足睡眠",
                "避免剧烈运动和过度出汗",
                "饮食宜清淡，多食滋阴食物",
                "保持心境平和，避免急躁",
                "可食用银耳、百合、枸杞等滋阴食材",
            ],
            ConstitutionType.TAN_SHI: [
                "适当运动，促进新陈代谢",
                "饮食清淡，少食肥甘厚腻",
                "保持环境干燥，避免潮湿",
                "规律作息，避免久坐",
                "可食用薏米、冬瓜、茯苓等化湿食材",
            ],
            ConstitutionType.SHI_RE: [
                "避免高温环境，注意防暑",
                "饮食清淡，忌辛辣油腻",
                "保持心境平和，避免急躁",
                "适当运动，但避免过度出汗",
                "可食用绿豆、苦瓜、菊花等清热食材",
            ],
            ConstitutionType.XUE_YU: [
                "适当运动，促进血液循环",
                "保持心情愉快，避免情志郁结",
                "饮食宜温通，可适当食用活血食物",
                "避免久坐久立",
                "可食用山楂、红花、当归等活血食材",
            ],
            ConstitutionType.QI_YU: [
                "保持心情愉快，避免情志抑郁",
                "适当运动，如散步、瑜伽等",
                "多与人交流，避免独处",
                "听音乐、看书等调节情绪",
                "可食用玫瑰花、佛手、柠檬等理气食材",
            ],
            ConstitutionType.TE_BING: [
                "避免接触过敏原",
                "增强体质，提高免疫力",
                "饮食宜清淡，避免易过敏食物",
                "保持环境清洁",
                "可食用灵芝、人参等增强免疫食材",
            ],
            ConstitutionType.PING_HE: [
                "保持规律作息",
                "适当运动，增强体质",
                "饮食均衡，营养全面",
                "保持心情愉快",
                "定期体检，预防疾病",
            ],
        }

        return advice_map.get(constitution_type, [])

    def get_service_statistics(self) -> Dict[str, Any]:
        """获取服务统计信息"""
        return {
            "total_formulas": len(self.formulas),
            "total_herbs": len(self.herbs),
            "total_acupoints": len(self.acupoints),
            "total_syndromes": len(self.syndromes),
            "constitution_formula_coverage": {
                constitution: len(formulas)
                for constitution, formulas in self.constitution_formula_index.items()
            },
            "herb_categories": list(
                set(
                    herb.source.split("科")[0] + "科" if "科" in herb.source else "其他"
                    for herb in self.herbs.values()
                )
            ),
            "meridian_coverage": list(
                set(
                    meridian.value
                    for acupoint in self.acupoints.values()
                    for meridian in [acupoint.meridian]
                )
            ),
            "syndrome_categories": list(
                set(syndrome.category for syndrome in self.syndromes.values())
            ),
        }
