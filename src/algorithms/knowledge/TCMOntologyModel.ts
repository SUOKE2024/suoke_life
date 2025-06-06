import { ConstitutionType } from "../../types/////    collaboration;";

/**
 * * 中医本体模型
 * 实现中医辨证论治的数字化知识表示
export class TCMOntologyModel {private syndromePatterns: Map<string, SyndromePattern> = new Map();
  private constitutionProfiles: Map<ConstitutionType, ConstitutionProfile> = new Map();
  private herbDatabase: Map<string, HerbProfile> = new Map();
  private formulaDatabase: Map<string, FormulaProfile> = new Map();
  private meridianSystem: Map<string, MeridianProfile> = new Map();
  private organSystem: Map<string, OrganProfile> = new Map();
  constructor() {
    this.initializeOntology();
  }
  /**
 * * 初始化中医本体知识库
  private initializeOntology(): void {
    this.initializeConstitutionProfiles();
    this.initializeSyndromePatterns();
    this.initializeHerbDatabase();
    this.initializeFormulaDatabase();
    this.initializeMeridianSystem()
    this.initializeOrganSystem()
  }
  /**
 * * 初始化体质档案
  private initializeConstitutionProfiles(): void {
    // 平和质
this.constitutionProfiles.set(ConstitutionType.BALANCED, {
      name: ";平和质",
      characteristics: [
        体形匀称健壮",面色润泽,精力充沛",
        睡眠良好",食欲正常"
      ],
      physicalTraits: {
        complexion: "红润有光泽",
        bodyType: 匀称","
        energy: "充沛,",
        sleep: "良好",
        appetite: 正常""
      },
      psychologicalTraits: {
        personality: "性格随和开朗,",
        emotion: "情绪稳定",
        stress: 适应能力强""
      },
      susceptibleDiseases: ["感冒, "外感"],"
      adaptationCapacity: {
        climate: 适应性强","
        season: "四季皆宜,",
        environment: "环境适应性好"
      },
      healthMaintenance: {
        diet: 饮食有节","
        exercise: "适度运动,",
        lifestyle: "起居有常",
        emotion: 调畅情志""
      }
    });
    // 气虚质
this.constitutionProfiles.set(ConstitutionType.QI_DEFICIENCY, {
      name: "气虚质,",
      characteristics: [
        "元气不足",
        疲乏无力",气短懒言,容易出汗",
        舌淡苔白""
      ],
      physicalTraits: {
        complexion: "面色偏黄或淡白,",
        bodyType: "肌肉松软",
        energy: 精神不振","
        sleep: "容易疲劳,",
        appetite: "食欲不振"
      },
      psychologicalTraits: {
        personality: 性格内向","
        emotion: "情绪不稳,",
        stress: "不耐受风、寒、暑、湿邪"
      },
      susceptibleDiseases: [感冒", "内脏下垂, "虚劳"],
      adaptationCapacity: {
        climate: 不耐受风寒","
        season: "春夏较好,",
        environment: "易感外邪"
      },
      healthMaintenance: {
        diet: 益气健脾","
        exercise: "柔和运动,",
        lifestyle: "避风寒",
        emotion: 调养心神""
      }
    });
    // 阳虚质
this.constitutionProfiles.set(ConstitutionType.YANG_DEFICIENCY, {
      name: "阳虚质,",
      characteristics: [
        "阳气不足",
        畏寒怕冷",手足不温,精神不振",
        舌淡胖嫩""
      ],
      physicalTraits: {
        complexion: "面色淡白,",
        bodyType: "形体白胖",
        energy: 精神不振","
        sleep: "睡眠偏多,",
        appetite: "食量较少"
      },
      psychologicalTraits: {
        personality: 性格多沉静","
        emotion: "情绪低沉,",
        stress: "不耐受寒邪"
      },
      susceptibleDiseases: [水肿", "腹泻, "阳痿"],
      adaptationCapacity: {
        climate: 不耐受寒湿","
        season: "夏季较好,",
        environment: "喜暖怕凉"
      },
      healthMaintenance: {
        diet: 温阳散寒","
        exercise: "动则生阳,",
        lifestyle: "春夏养阳",
        emotion: 振奋阳气""
      }
    });
    // 继续添加其他体质类型...
    this.addRemainingConstitutions();
  }
  /**
 * * 添加其余体质类型
  private addRemainingConstitutions(): void {
    // 阴虚质
this.constitutionProfiles.set(ConstitutionType.YIN_DEFICIENCY, {
      name: "阴虚质,",
      characteristics: ["阴液不足", 虚热内扰", "口燥咽干, "手足心热", 舌红少苔"],"
      physicalTraits: {
        complexion: "面色潮红,",
        bodyType: "体形偏瘦",
        energy: 容易疲劳","
        sleep: "失眠多梦,",
        appetite: "口干喜冷饮"
      },
      psychologicalTraits: {
        personality: 性情急躁","
        emotion: "情绪易激动,",
        stress: "不耐受暑热燥邪"
      },
      susceptibleDiseases: [虚劳", "失眠, "糖尿病"],
      adaptationCapacity: {
        climate: 不耐受燥热","
        season: "秋冬较好,",
        environment: "喜润恶燥"
      },
      healthMaintenance: {
        diet: 滋阴润燥","
        exercise: "中小强度,",
        lifestyle: "秋冬养阴",
        emotion: 静神少虑""
      }
    });
    // 痰湿质
this.constitutionProfiles.set(ConstitutionType.PHLEGM_DAMPNESS, {
      name: "痰湿质,",
      characteristics: ["痰湿凝聚", 形体肥胖", "腹部肥满, "胸闷痰多", 舌体胖大"],"
      physicalTraits: {
        complexion: "面色淡黄而暗,",
        bodyType: "形体肥胖",
        energy: 容易困倦","
        sleep: "睡眠偏多,",
        appetite: "食量较大"
      },
      psychologicalTraits: {
        personality: 性格偏温和","
        emotion: "情绪稳定,",
        stress: "不耐受湿邪"
      },
      susceptibleDiseases: [消渴", "中风, "胸痹"],
      adaptationCapacity: {
        climate: 不耐受湿邪","
        season: "秋冬较好,",
        environment: "湿重环境不适"
      },
      healthMaintenance: {
        diet: 化痰祛湿","
        exercise: "加强运动,",
        lifestyle: "避湿邪",
        emotion: 开朗乐观""
      }
    });
    // 湿热质
this.constitutionProfiles.set(ConstitutionType.DAMP_HEAT, {
      name: "湿热质,",
      characteristics: ["湿热内蕴", 面垢油腻", "口苦口干, "身重困倦", 舌质偏红"],"
      physicalTraits: {
        complexion: "面垢油腻,",
        bodyType: "形体中等或偏瘦",
        energy: 容易疲倦","
        sleep: "睡眠一般,",
        appetite: "口苦口干"
      },
      psychologicalTraits: {
        personality: 性情急躁","
        emotion: "容易烦躁,",
        stress: "不耐受湿热邪气"
      },
      susceptibleDiseases: [疮疖", "黄疸, "火热病"],
      adaptationCapacity: {
        climate: 不耐受湿热","
        season: "秋冬较好,",
        environment: "湿热环境不适"
      },
      healthMaintenance: {
        diet: 清热利湿","
        exercise: "适度运动,",
        lifestyle: "避湿热",
        emotion: 心平气和""
      }
    });
    // 血瘀质
this.constitutionProfiles.set(ConstitutionType.BLOOD_STASIS, {
      name: "血瘀质,",
      characteristics: ["血行不畅", 肤色晦暗", "色素沉着, "口唇暗淡", 舌质紫暗"],"
      physicalTraits: {
        complexion: "面色晦暗,",
        bodyType: "形体正常",
        energy: 精神一般","
        sleep: "健忘,",
        appetite: "正常"
      },
      psychologicalTraits: {
        personality: 性格内郁","
        emotion: "情绪不稳,",
        stress: "不耐受寒邪"
      },
      susceptibleDiseases: [症瘕", "中风, "冠心病"],
      adaptationCapacity: {
        climate: 不耐受寒邪","
        season: "夏季较好,",
        environment: "血脉易瘀滞"
      },
      healthMaintenance: {
        diet: 活血化瘀","
        exercise: "促进血循环,",
        lifestyle: "避寒就温",
        emotion: 调畅气血""
      }
    });
    // 气郁质
this.constitutionProfiles.set(ConstitutionType.QI_STAGNATION, {
      name: "气郁质,",
      characteristics: ["气机郁滞", 神情抑郁", "情感脆弱, "烦闷不乐", 舌淡红"],"
      physicalTraits: {
        complexion: "面色萎黄,",
        bodyType: "形体偏瘦",
        energy: 精神抑郁","
        sleep: "失眠,",
        appetite: "食欲不振"
      },
      psychologicalTraits: {
        personality: 性格内向不稳定","
        emotion: "情感脆弱,",
        stress: "对精神刺激适应能力较差"
      },
      susceptibleDiseases: [郁证", "脏躁, "梅核气"],
      adaptationCapacity: {
        climate: 对阴雨天气适应能力差","
        season: "春季较好,",
        environment: "不喜阴雨天气"
      },
      healthMaintenance: {
        diet: 疏肝理气","
        exercise: "户外活动,",
        lifestyle: "调畅情志",
        emotion: 心情愉快""
      }
    });
    // 特禀质
this.constitutionProfiles.set(ConstitutionType.SPECIAL_CONSTITUTION, {
      name: "特禀质,",
      characteristics: ["先天失常", 过敏反应", "遗传缺陷, "胎传异常"],
      physicalTraits: {
        complexion: 无特殊","
        bodyType: "无特殊,",
        energy: "无特殊",
        sleep: 无特殊","
        appetite: "无特殊"
      },
      psychologicalTraits: {
        personality: "无特殊",
        emotion: 无特殊","
        stress: "对致敏物质敏感"
      },
      susceptibleDiseases: ["哮喘", 荨麻疹", "过敏性鼻炎],
      adaptationCapacity: {
        climate: "适应能力差",
        season: 季节交替时不适","
        environment: "对过敏原敏感"
      },
      healthMaintenance: {
        diet: "饮食清淡",
        exercise: 避免剧烈运动","
        lifestyle: "避免致敏原,",
        emotion: "保持平和"
      }
    });
  }
  /**
 * * 初始化证候模式
  private initializeSyndromePatterns(): void {
    // 风寒感冒证
this.syndromePatterns.set(wind_cold_common_cold", {"
      name: "风寒感冒,",
      category: "外感病证",
      pathogenesis: 风寒外袭，肺气失宣","
      mainSymptoms: [
        { name: "恶寒重, weight: 0.9, required: true },"
        { name: "发热轻", weight: 0.8, required: true },
        { name: 无汗", weight: 0.7, required: false },"
        { name: "头痛, weight: 0.6, required: false },"
        { name: "鼻塞流清涕", weight: 0.8, required: true },
        { name: 咳嗽痰稀白", weight: 0.7, required: false }"
      ],
      tongueManifestations: {
        tongueBody: "舌质淡红,",
        tongueCoating: "苔薄白"
      },
      pulseManifestations: [浮", "紧],
      treatmentPrinciple: "辛温解表，宣肺散寒",
      recommendedFormulas: [荆防败毒散", "麻黄汤],
      contraindications: ["辛凉解表药", 寒凉药物"],"
      prognosis: "及时治疗预后良好,",
      differentialDiagnosis: ["风热感冒", 暑湿感冒"]"
    });
    // 脾胃虚弱证
this.syndromePatterns.set("spleen_stomach_deficiency, {"
      name: "脾胃虚弱",
      category: 脏腑病证","
      pathogenesis: "脾胃气虚，运化失司,",
      mainSymptoms: [
        { name: "食少纳呆", weight: 0.9, required: true },
        { name: 腹胀", weight: 0.8, required: true },"
        { name: "便溏, weight: 0.8, required: true },"
        { name: "神疲乏力", weight: 0.7, required: false },
        { name: 面色萎黄", weight: 0.6, required: false },"
        { name: "肢体倦怠, weight: 0.7, required: false }"
      ],
      tongueManifestations: {
        tongueBody: "舌质淡",
        tongueCoating: 苔白""
      },
      pulseManifestations: ["缓, "弱"],"
      treatmentPrinciple: 健脾益气，和胃助运","
      recommendedFormulas: ["四君子汤, "参苓白术散"],"
      contraindications: [寒凉药物", "滋腻药物],
      prognosis: "调理得当可逐渐恢复",
      differentialDiagnosis: [胃阴不足", "肝胃不和]
    });
    // 继续添加更多证候模式...
    this.addMoreSyndromePatterns();
  }
  /**
 * * 添加更多证候模式
  private addMoreSyndromePatterns(): void {
    // 肝郁气滞证
this.syndromePatterns.set("liver_qi_stagnation", {
      name: 肝郁气滞","
      category: "脏腑病证,",
      pathogenesis: "情志不遂，肝气郁结",
      mainSymptoms: [
        { name: 胸胁胀痛", weight: 0.9, required: true },"
        { name: "情志抑郁, weight: 0.8, required: true },"
        { name: "善太息", weight: 0.7, required: false },
        { name: 急躁易怒", weight: 0.8, required: false },"
        { name: "咽中如有物阻, weight: 0.6, required: false }"
      ],
      tongueManifestations: {
        tongueBody: "舌质淡红",
        tongueCoating: 苔薄白""
      },
      pulseManifestations: ["弦],"
      treatmentPrinciple: "疏肝理气，调畅气机",
      recommendedFormulas: [逍遥散", "柴胡疏肝散],
      contraindications: ["辛燥药物"],
      prognosis: 调理情志，预后良好","
      differentialDiagnosis: ["肝火上炎, "心神不安"]"
    });
    // 肾阳虚证
this.syndromePatterns.set(kidney_yang_deficiency", {"
      name: "肾阳虚,",
      category: "脏腑病证",
      pathogenesis: 肾阳不足，温煦失职","
      mainSymptoms: [
        { name: "腰膝酸冷, weight: 0.9, required: true },"
        { name: "畏寒肢冷", weight: 0.8, required: true },
        { name: 阳痿早泄", weight: 0.8, required: false },"
        { name: "小便清长, weight: 0.7, required: false },"
        { name: "夜尿频多", weight: 0.7, required: false },
        { name: 面色㿠白", weight: 0.6, required: false }"
      ],
      tongueManifestations: {
        tongueBody: "舌质淡胖,",
        tongueCoating: "苔白滑"
      },
      pulseManifestations: [沉", "迟, "弱"],
      treatmentPrinciple: 温补肾阳","
      recommendedFormulas: ["肾气丸, "右归丸"],"
      contraindications: [寒凉药物", "苦寒药物],
      prognosis: "温补得当可改善",
      differentialDiagnosis: [肾阴虚", "脾肾阳虚]
    });
  }
  /**
 * * 初始化中药数据库
  private initializeHerbDatabase(): void {
    // 人参
this.herbDatabase.set("ginseng", {
      name: 人参","
      latinName: "Panax ginseng,",
      category: "补虚药",
      subCategory: 补气药","
      nature: "微温,",
      flavor: ["甘", 微苦"],"
      meridians: ["脾, "肺", 心", "肾],"
      functions: [
        "大补元气",
        复脉固脱",补脾益肺,生津养血",
        安神益智""
      ],
      indications: [
        "气虚欲脱,脾肺气虚",
        热病气阴两伤",心神不安,失眠多梦"
      ],
      dosage: 3-9g","
      contraindications: ["实热证, "湿热证"],"
      incompatibilities: [藜芦"],"
      processing: ["生用, "红参", 白参"],
      modernPharmacology: {
        activeComponents: ["人参皂苷, "人参多糖"],"
        pharmacologicalEffects: [增强免疫", "抗疲劳, "调节血糖"],
        clinicalApplications: [免疫功能低下", "慢性疲劳综合征]
      }
    });
    // 黄芪
this.herbDatabase.set("astragalus", {
      name: 黄芪","
      latinName: "Astragalus membranaceus,",
      category: "补虚药",
      subCategory: 补气药","
      nature: "微温,",
      flavor: ["甘"],
      meridians: [脾", "肺],
      functions: [
        "补气升阳",
        固表止汗",利水消肿,生津养血",
        行滞通痹""
      ],
      indications: [
        "气虚乏力,中气下陷",
        表虚自汗",水肿,血虚萎黄"
      ],
      dosage: 9-30g","
      contraindications: ["表实邪盛, "气滞湿阻"],"
      incompatibilities: [],
      processing: [生用", "蜜炙],
      modernPharmacology: {
        activeComponents: ["黄芪皂苷", 黄芪多糖"],"
        pharmacologicalEffects: ["免疫调节, "抗氧化", 保肝"],
        clinicalApplications: ["慢性肾炎, "糖尿病", 慢性肝炎"]
      }
    });
    // 继续添加更多中药...
    this.addMoreHerbs();
  }
  /**
 * * 添加更多中药
  private addMoreHerbs(): void {
    // 当归
this.herbDatabase.set("angelica, {"
      name: "当归",
      latinName: Angelica sinensis","
      category: "补虚药,",
      subCategory: "补血药",
      nature: 温","
      flavor: ["甘, "辛"],"
      meridians: [肝", "心, "脾"],
      functions: [补血活血", "调经止痛, "润肠通便"],
      indications: [血虚萎黄", "月经不调, "经闭痛经", 虚寒腹痛", "肠燥便秘],
      dosage: "6-12g",
      contraindications: [湿盛中满", "大便溏泄],
      incompatibilities: [],
      processing: ["生用", 酒制", "土炒],
      modernPharmacology: {
        activeComponents: ["阿魏酸", 当归多糖"],"
        pharmacologicalEffects: ["补血, "调节免疫", 抗血栓"],
        clinicalApplications: ["贫血, "月经不调", 血栓性疾病"]
      }
    });
    // 甘草
this.herbDatabase.set("licorice, {"
      name: "甘草",
      latinName: Glycyrrhiza uralensis","
      category: "补虚药,",
      subCategory: "补气药",
      nature: 平","
      flavor: ["甘],"
      meridians: ["心", 肺", "脾, "胃"],
      functions: [补脾益气", "清热解毒, "祛痰止咳", 缓急止痛", "调和诸药],
      indications: ["脾胃虚弱", 倦怠乏力", "心悸气短, "咳嗽痰多", 脘腹疼痛"],"
      dosage: "2-10g,",
      contraindications: ["湿盛胀满", 浮肿"],"
      incompatibilities: ["大戟, "芫花", 甘遂", "海藻],"
      processing: ["生用", 蜜炙"],"
      modernPharmacology: {
        activeComponents: ["甘草酸, "甘草次酸"],"
        pharmacologicalEffects: [抗炎", "免疫调节, "保肝"],
        clinicalApplications: [慢性肝炎", "胃溃疡, "支气管炎"]
      }
    });
  }
  /**
 * * 初始化方剂数据库
  private initializeFormulaDatabase(): void {
    // 四君子汤
this.formulaDatabase.set(sijunzi_decoction", {"
      name: "四君子汤,",
      category: "补益剂",
      subCategory: 补气剂","
      composition: [
        { herb: "人参, dosage: "9g", role: 君药" },
        { herb: "白术, dosage: "9g", role: 臣药" },
        { herb: "茯苓, dosage: "9g", role: 佐药" },
        { herb: "甘草, dosage: "6g", role: 使药" }
      ],
      functions: ["益气健脾, "和胃"],"
      indications: [
        脾胃气虚证",面色萎白,语声低微",
        气短乏力",食少便溏"
      ],
      contraindications: ["邪实证"],
      modifications: [
        {
          condition: 兼有痰湿","
          addition: ["陈皮, "半夏"],"
          removal: []
        },
        {
          condition: 兼有食积","
          addition: ["山楂, "神曲"],"
          removal: []
        }
      ],
      preparation: 水煎服","
      dosage: "每日1剂，分2次服,",
      modernApplications: [
        "慢性胃炎",
        胃及十二指肠溃疡",慢性肠炎,功能性消化不良"
      ]
    });
    // 逍遥散
this.formulaDatabase.set(xiaoyao_powder", {"
      name: "逍遥散,",
      category: "调和剂",
      subCategory: 调和肝脾","
      composition: [
        { herb: "柴胡, dosage: "9g", role: 君药" },
        { herb: "当归, dosage: "9g", role: 臣药" },
        { herb: "白芍, dosage: "9g", role: 臣药" },
        { herb: "白术, dosage: "9g", role: 佐药" },
        { herb: "茯苓, dosage: "9g", role: 佐药" },
        { herb: "甘草, dosage: "6g", role: 使药" },
        { herb: "薄荷, dosage: "3g", role: 佐药" },
        { herb: "生姜, dosage: "3g", role: 佐药" }
      ],
      functions: ["疏肝解郁, "健脾和血"],"
      indications: [
        肝郁脾虚证",胸胁胀痛,头痛目眩",
        口燥咽干",神疲食少"
      ],
      contraindications: ["肝阳上亢", 肝火炽盛"],"
      modifications: [
        {
          condition: "兼有热象,",
          addition: ["丹皮", 栀子"],"
          removal: []
        }
      ],
      preparation: "散剂或汤剂,",
      dosage: "每日1剂，分2次服",
      modernApplications: [
        慢性肝炎",胆囊炎,胃及十二指肠溃疡",
        功能性子宫出血",乳腺增生"
      ]
    });
  }
  /**
 * * 初始化经络系统
  private initializeMeridianSystem(): void {
    // 肺经
this.meridianSystem.set("lung_meridian", {
      name: 手太阴肺经","
      abbreviation: "LU,",
      type: "手三阴经",
      pairedOrgan: 大肠","
      flowDirection: "从胸走手,",
      peakTime: "3-5时",
      mainFunctions: [
        主气司呼吸",主宣发肃降,通调水道",
        朝百脉主治节""
      ],
      pathology: [
        "咳嗽,气喘",
        胸闷",咽喉肿痛,感冒"
      ],
      keyPoints: [
        { name: 中府", location: "胸外侧部, functions: ["宣肺理气", 止咳平喘"] },"
        { name: "尺泽, location: "肘横纹上", functions: [清肺热", "降逆气] },"
        { name: "列缺", location: 前臂桡侧", functions: ["宣肺解表, "通调水道"] },
        { name: 太渊", location: "腕横纹上, functions: ["补肺气", 通血脉"] }"
      ]
    });
    // 继续添加其他经络...
  }
  /**
 * * 初始化脏腑系统
  private initializeOrganSystem(): void {
    // 心
this.organSystem.set("heart, {"
      name: "心",
      category: 五脏","
      element: "火,",
      season: "夏",
      emotion: 喜","
      tissue: "血脉,",
      sensoryOrgan: "舌",
      fluid: 汗","
      mainFunctions: [
        "主血脉,主神明",
        开窍于舌",其华在面"
      ],
      physiologicalCharacteristics: [
        "心为君主之官",
        心主血脉",心藏神,心开窍于舌"
      ],
      pathologicalManifestations: [
        心悸怔忡",失眠多梦,神志异常",
        面色不华",舌质异常"
      ],
      commonSyndromes: [
        "心气虚",
        心阳虚",心血虚,心阴虚",
        心火亢盛""
      ]
    });
    // 继续添加其他脏腑...
  }
  /**
 * * 辨证分析
   * @param symptoms 症状列表
   * @param constitution 体质类型
   * @returns 辨证结果
  analyzePattern(symptoms: SymptomInput[], constitution?: ConstitutionType): PatternAnalysisResult {
    const candidatePatterns: PatternMatch[] = [];
    // 遍历所有证候模式
for (const [patternId, pattern] of this.syndromePatterns) {
      const match = this.calculatePatternMatch(symptoms, pattern);
      if (match.score > 0.3) { // 阈值可调整
candidatePatterns.push({
          patternId,
          pattern,
          score: match.score,
          matchedSymptoms: match.matchedSymptoms,
          confidence: match.confidence;
        });
      }
    }
    // 按匹配度排序
candidatePatterns.sort((a, b) => b.score - a.score);
    // 考虑体质因素调整结果
if (constitution) {
      this.adjustForConstitution(candidatePatterns, constitution);
    }
    return {primaryPattern: candidatePatterns[0] || null,alternativePatterns: candidatePatterns.slice(1, 3),confidence: candidatePatterns[0]?.confidence || 0,recommendations: this.generateRecommendations(candidatePatterns[0]),timestamp: new Date();
    };
  }
  /**
 * * 计算证候匹配度
  private calculatePatternMatch(symptoms: SymptomInput[], pattern: SyndromePattern): PatternMatchResult {
    let totalScore = 0;
    let maxPossibleScore = 0;
    const matchedSymptoms: MatchedSymptom[] = [];
    for (const patternSymptom of pattern.mainSymptoms) {
      maxPossibleScore += patternSymptom.weight;
      const userSymptom = symptoms.find(s =>;
        this.isSymptomMatch(s.name, patternSymptom.name);
      );
      if (userSymptom) {
        const severityFactor = userSymptom.severity / 10; // 归一化到0-1;
const score = patternSymptom.weight * severityFactor;
        totalScore += score;
        matchedSymptoms.push({
          symptomName: patternSymptom.name,
          userSeverity: userSymptom.severity,
          patternWeight: patternSymptom.weight,
          score;
        });
      } else if (patternSymptom.required) {
        // 必需症状缺失，大幅降低匹配度
totalScore -= patternSymptom.weight * 0.5;
      }
    }
    const normalizedScore = Math.max(0, totalScore /////     maxPossibleScore);
    const confidence = this.calculateConfidence(matchedSymptoms, pattern);
    return {score: normalizedScore,matchedSymptoms,confidence;
    };
  }
  /**
 * * 症状匹配判断
  private isSymptomMatch(userSymptom: string, patternSymptom: string): boolean {
    // 简化的症状匹配逻辑，实际应用中需要更复杂的NLP处理
return userSymptom.includes(patternSymptom) || patternSymptom.includes(userSymptom);
  }
  /**
 * * 计算置信度
  private calculateConfidence(matchedSymptoms: MatchedSymptom[], pattern: SyndromePattern): number {
    const requiredSymptoms = pattern.mainSymptoms.filter(s => s.required);
    const matchedRequired = matchedSymptoms.filter(ms =>;
      requiredSymptoms.some(rs => rs.name === ms.symptomName);
    );
    const requiredRatio = requiredSymptoms.length > 0 ? ;
      matchedRequired.length /////     requiredSymptoms.length : 1;
    const totalSymptomRatio = matchedSymptoms.length /////     pattern.mainSymptoms.length;
    return (requiredRatio * 0.7 + totalSymptomRatio * 0.3);
  }
  /**
 * * 根据体质调整辨证结果
  private adjustForConstitution(patterns: PatternMatch[], constitution: ConstitutionType): void {
    const constitutionProfile = this.constitutionProfiles.get(constitution);
    if (!constitutionProfile) return;
    // 根据体质特点调整证候匹配度
patterns.forEach(pattern => {}
      if (this.isPatternCompatibleWithConstitution(pattern.pattern, constitutionProfile)) {
        pattern.score *= 1.2; // 提高兼容证候的权重
      } else {
        pattern.score *= 0.8 // 降低不兼容证候的权重
      }
    });
    // 重新排序
patterns.sort((a, b) => b.score - a.score);
  }
  /**
 * * 判断证候与体质的兼容性
  private isPatternCompatibleWithConstitution(
    pattern: SyndromePattern,
    constitution: ConstitutionProfile;
  ): boolean {
    // 简化的兼容性判断逻辑
    // 实际应用中需要更复杂的规则引擎
return true; // 暂时返回true;
  }
  /**
 * * 生成治疗建议
  private generateRecommendations(patternMatch: PatternMatch | null): TreatmentRecommendation[] {
    if (!patternMatch) return [];
    const recommendations: TreatmentRecommendation[] = [];
    const pattern = patternMatch.pattern;
    // 方药建议
if (pattern.recommendedFormulas.length > 0) {
      recommendations.push({
        type: "formula,",
        title: "推荐方剂",
        content: pattern.recommendedFormulas.join(、"),"
        priority: "high"
      });
    }
    // 治疗原则
recommendations.push({
      type: "principle",
      title: 治疗原则","
      content: pattern.treatmentPrinciple,
      priority: "high"
    });
    // 禁忌事项
if (pattern.contraindications.length > 0) {
      recommendations.push({
        type: "contraindication",
        title: 注意事项","
        content: `避免使用：${pattern.contraindications.join("、)}`,"
        priority: "medium"
      });
    }
    return recommendations;
  }
  /**
 * * 获取体质档案
  getConstitutionProfile(constitution: ConstitutionType): ConstitutionProfile | null {
    return this.constitutionProfiles.get(constitution) || null;
  }
  /**
 * * 获取证候模式
  getSyndromePattern(patternId: string): SyndromePattern | null {
    return this.syndromePatterns.get(patternId) || null;
  }
  /**
 * * 获取中药信息
  getHerbProfile(herbName: string): HerbProfile | null {
    return this.herbDatabase.get(herbName) || null;
  }
  /**
 * * 获取方剂信息
  getFormulaProfile(formulaName: string): FormulaProfile | null {
    return this.formulaDatabase.get(formulaName) || null;
  }
}
// 接口定义
export interface SyndromePattern {name: string;
  category: string;
  pathogenesis: string;
  mainSymptoms: PatternSymptom[];
  tongueManifestations: TongueManifestations;
  pulseManifestations: string[];
  treatmentPrinciple: string;
  recommendedFormulas: string[];
  contraindications: string[];
  prognosis: string;
  differentialDiagnosis: string[];
}
export interface PatternSymptom {name: string;
  weight: number;
  required: boolean;
}
export interface TongueManifestations {tongueBody: string;
  tongueCoating: string;
}
export interface ConstitutionProfile {name: string;
  characteristics: string[];
  physicalTraits: PhysicalTraits;
  psychologicalTraits: PsychologicalTraits;
  susceptibleDiseases: string[];
  adaptationCapacity: AdaptationCapacity;
  healthMaintenance: HealthMaintenance;
}
export interface PhysicalTraits {complexion: string;
  bodyType: string;
  energy: string;
  sleep: string;
  appetite: string;
}
export interface PsychologicalTraits {personality: string;
  emotion: string;
  stress: string;
}
export interface AdaptationCapacity {climate: string;
  season: string;
  environment: string;
}
export interface HealthMaintenance {diet: string;
  exercise: string;
  lifestyle: string;
  emotion: string;
}
export interface HerbProfile {name: string;
  latinName: string;
  category: string;
  subCategory: string;
  nature: string;
  flavor: string[];
  meridians: string[];
  functions: string[];
  indications: string[];
  dosage: string;
  contraindications: string[];
  incompatibilities: string[];
  processing: string[];
  modernPharmacology: ModernPharmacology;
}
export interface ModernPharmacology {activeComponents: string[];
  pharmacologicalEffects: string[];
  clinicalApplications: string[];
}
export interface FormulaProfile {name: string;
  category: string;
  subCategory: string;
  composition: FormulaComponent[];
  functions: string[];
  indications: string[];
  contraindications: string[];
  modifications: FormulaModification[];
  preparation: string;
  dosage: string;
  modernApplications: string[];
}
export interface FormulaComponent {herb: string;
  dosage: string;
  role: string;
}
export interface FormulaModification {condition: string;
  addition: string[];
  removal: string[];
}
export interface MeridianProfile {name: string;
  abbreviation: string;
  type: string;
  pairedOrgan: string;
  flowDirection: string;
  peakTime: string;
  mainFunctions: string[];
  pathology: string[];
  keyPoints: AcupointProfile[];
}
export interface AcupointProfile {name: string;
  location: string;
  functions: string[];
}
export interface OrganProfile {name: string;
  category: string;
  element: string;
  season: string;
  emotion: string;
  tissue: string;
  sensoryOrgan: string;
  fluid: string;
  mainFunctions: string[];
  physiologicalCharacteristics: string[];
  pathologicalManifestations: string[];
  commonSyndromes: string[];
}
export interface SymptomInput {name: string;
  severity: number;
  duration?: string;
  frequency?: string;
}
export interface PatternAnalysisResult {primaryPattern: PatternMatch | null;
  alternativePatterns: PatternMatch[];
  confidence: number;
  recommendations: TreatmentRecommendation[];
  timestamp: Date;
}
export interface PatternMatch {patternId: string;
  pattern: SyndromePattern;
  score: number;
  matchedSymptoms: MatchedSymptom[];
  confidence: number;
}
export interface PatternMatchResult {score: number;
  matchedSymptoms: MatchedSymptom[];
  confidence: number;
}
export interface MatchedSymptom {symptomName: string;
  userSeverity: number;
  patternWeight: number;
  score: number;
}
export interface TreatmentRecommendation {type: formula" | "principle | "contraindication" | lifestyle
  title: string;
  content: string;
  priority: "high | "medium" | low";
}
export default TCMOntologyModel;
  */////
