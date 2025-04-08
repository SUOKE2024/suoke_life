/// 中医九种体质类型定义
/// 基于《中医体质分类与判定》（中华人民共和国中医药行业标准 ZYYXH/T 157-2009）
enum ConstitutionType {
  /// 平和质：阴阳气血调和，脏腑功能平稳
  balanced,
  
  /// 气虚质：气虚是主要特征，表现为气不足或气的功能减退
  qiDeficiency,
  
  /// 阳虚质：阳气不足，以畏寒怕冷，手足不温为特征
  yangDeficiency,
  
  /// 阴虚质：阴液亏少，以口燥咽干，手足心热为特征
  yinDeficiency,
  
  /// 痰湿质：体内痰湿停聚，以形体肥胖，腹部肥满为特征
  phlegmDampness,
  
  /// 湿热质：湿热内蕴，以面垢油光，口苦为特征
  dampnessHeat,
  
  /// 血瘀质：血行不畅，血流不顺，以肤色晦暗，舌质紫暗为特征
  bloodStasis,
  
  /// 气郁质：气机郁滞，以神情抑郁，忧虑脆弱为特征
  qiStagnation,
  
  /// 特禀质：先天禀赋不足，以过敏体质为特征
  specialConstitution,
}

/// 体质特性类
class ConstitutionTraits {
  /// 体质类型
  final ConstitutionType type;
  
  /// 体质名称（中文）
  final String name;
  
  /// 体质描述
  final String description;
  
  /// 主要特征
  final List<String> mainFeatures;
  
  /// 调理原则
  final String regulationPrinciple;
  
  /// 饮食调理建议
  final List<String> dietarySuggestions;
  
  /// 生活起居建议
  final List<String> lifestyleSuggestions;
  
  /// 心理调适建议
  final List<String> psychologicalSuggestions;
  
  /// 运动调养建议
  final List<String> exerciseSuggestions;
  
  /// 适宜食物
  final List<String> suitableFoods;
  
  /// 不宜食物
  final List<String> unsuitableFoods;
  
  /// 相关风险疾病
  final List<String> relatedDiseaseRisks;
  
  /// 诊断辨别要点
  final List<String> diagnosticPoints;

  const ConstitutionTraits({
    required this.type,
    required this.name,
    required this.description,
    required this.mainFeatures,
    required this.regulationPrinciple,
    required this.dietarySuggestions,
    required this.lifestyleSuggestions,
    required this.psychologicalSuggestions,
    required this.exerciseSuggestions,
    required this.suitableFoods,
    required this.unsuitableFoods,
    required this.relatedDiseaseRisks,
    required this.diagnosticPoints,
  });
  
  /// 获取所有体质特性列表
  static List<ConstitutionTraits> getAllTraits() {
    return [
      getBalancedTraits(),
      getQiDeficiencyTraits(),
      getYangDeficiencyTraits(),
      getYinDeficiencyTraits(),
      getPhlegmDampnessTraits(),
      getDampnessHeatTraits(),
      getBloodStasisTraits(),
      getQiStagnationTraits(),
      getSpecialConstitutionTraits(),
    ];
  }
  
  /// 获取平和质特性
  static ConstitutionTraits getBalancedTraits() {
    return const ConstitutionTraits(
      type: ConstitutionType.balanced,
      name: "平和质",
      description: "平和质是指体质阴阳调和，气血充盈的一种健康体质状态。形体匀称健壮，面色红润，精力充沛，睡眠良好，不易疲劳，对外界环境适应能力强。",
      mainFeatures: [
        "面色润泽，红白分明",
        "体形匀称，肌肉结实有弹性",
        "精力充沛，耐受力强",
        "睡眠良好，胃纳佳，二便正常",
        "性格随和开朗",
      ],
      regulationPrinciple: "调养平和体质的原则是'正常体质正常养护'，保持良好的生活习惯和精神状态。",
      dietarySuggestions: [
        "饮食有节，不偏不倚",
        "维持营养均衡，荤素搭配",
        "规律饮食，不暴饮暴食",
      ],
      lifestyleSuggestions: [
        "作息规律，早睡早起",
        "起居有常，避免过度疲劳",
        "注意保暖，随气候变化及时增减衣物",
      ],
      psychologicalSuggestions: [
        "保持心情舒畅，乐观豁达",
        "适当参加社交活动，保持良好人际关系",
        "培养积极健康的兴趣爱好",
      ],
      exerciseSuggestions: [
        "坚持适量运动，如太极拳、八段锦等",
        "根据个人情况选择适合的运动方式",
        "注意运动安全，避免过度运动",
      ],
      suitableFoods: [
        "五谷杂粮", "新鲜蔬果", "适量鱼肉蛋奶", "时令食物",
      ],
      unsuitableFoods: [
        "过于油腻", "过于辛辣", "烟熏烧烤食品", "过量酒类",
      ],
      relatedDiseaseRisks: [
        "平和体质一般不易发生疾病",
        "但如果生活不规律或受到外邪侵袭，仍可能发生疾病",
      ],
      diagnosticPoints: [
        "面色红润，语声洪亮",
        "体形适中，肌肉有力",
        "精力充沛，耐寒耐热",
        "胃纳良好，大小便正常",
        "舌色淡红，苔薄白",
        "脉象和缓有力",
      ],
    );
  }
  
  /// 获取气虚质特性
  static ConstitutionTraits getQiDeficiencyTraits() {
    return const ConstitutionTraits(
      type: ConstitutionType.qiDeficiency,
      name: "气虚质",
      description: "气虚质是指以元气不足为主要特征的体质状态。表现为气短乏力、易疲劳、说话声音低弱，舌淡胖，脉虚弱等。",
      mainFeatures: [
        "经常感到疲乏无力，精神不振",
        "声音低弱，气短懒言",
        "易出汗，活动后汗多",
        "舌淡胖有齿痕，脉弱",
        "易患感冒，恢复较慢",
      ],
      regulationPrinciple: "以补气为主，适当配合养血，注重饮食调养和适度运动。",
      dietarySuggestions: [
        "选择易消化、富含优质蛋白的食物",
        "多食补气食物，如山药、扁豆、黄芪煲汤",
        "少食生冷、油腻食物",
      ],
      lifestyleSuggestions: [
        "保证充足睡眠，避免熬夜",
        "生活规律，不要过度劳累",
        "注意保暖，避免受凉",
      ],
      psychologicalSuggestions: [
        "保持心情舒畅，避免过度忧虑",
        "培养积极的生活态度",
        "适当减少精神压力",
      ],
      exerciseSuggestions: [
        "选择缓和的运动，如散步、太极拳、八段锦",
        "运动时间不宜过长，注意量力而行",
        "避免剧烈运动和大量出汗",
      ],
      suitableFoods: [
        "山药", "莲子", "红枣", "黄芪", "人参", "鸡肉", "牛肉", "粳米",
      ],
      unsuitableFoods: [
        "生冷食物", "辛辣食物", "油腻食物", "过咸食物",
      ],
      relatedDiseaseRisks: [
        "易患感冒、气管炎等呼吸系统疾病",
        "容易出现消化不良、脾胃虚弱症状",
        "长期气虚可导致气血两虚",
      ],
      diagnosticPoints: [
        "面色苍白或萎黄",
        "说话无力，气短懒言",
        "动则汗出，稍劳即疲",
        "舌质淡，苔薄白",
        "脉象虚弱",
      ],
    );
  }
  
  /// 获取阳虚质特性
  static ConstitutionTraits getYangDeficiencyTraits() {
    return const ConstitutionTraits(
      type: ConstitutionType.yangDeficiency,
      name: "阳虚质",
      description: "阳虚质是指体内阳气不足，以畏寒怕冷，手足不温为主要特征的体质状态。",
      mainFeatures: [
        "怕冷，手脚发凉",
        "面色苍白或晦暗",
        "喜热饮，不喜冷食",
        "大便溏薄，小便清长",
        "舌淡胖，脉沉细",
      ],
      regulationPrinciple: "温阳补虚，注重四肢保暖，适当进食温热食物。",
      dietarySuggestions: [
        "多食温热性食物，如羊肉、狗肉、韭菜等",
        "避免生冷食物和冷饮",
        "可适当食用肉桂、干姜等温热调味品",
      ],
      lifestyleSuggestions: [
        "注意保暖，特别是腰腹部和足部",
        "避免长时间处于潮湿环境",
        "适当增加阳光照射时间",
      ],
      psychologicalSuggestions: [
        "保持积极乐观的心态",
        "避免悲观消极情绪",
        "适当参加户外活动增加阳气",
      ],
      exerciseSuggestions: [
        "选择能促进阳气升发的运动，如慢跑、八段锦",
        "运动后注意保暖，防止着凉",
        "保持适度运动强度，不宜过度出汗",
      ],
      suitableFoods: [
        "羊肉", "鹿肉", "狗肉", "韭菜", "生姜", "肉桂", "花椒", "胡椒",
      ],
      unsuitableFoods: [
        "冷饮", "瓜果", "西瓜", "冰淇淋", "柿子", "绿茶", "苦瓜",
      ],
      relatedDiseaseRisks: [
        "易患风寒感冒",
        "消化系统功能减弱",
        "可能出现水肿、腹泻等症状",
        "长期阳虚可能导致肾阳虚",
      ],
      diagnosticPoints: [
        "面色苍白，唇色淡白",
        "畏寒肢冷，喜温怕冷",
        "腹部怕冷，喜温热食物",
        "舌淡胖嫩，苔白滑",
        "脉沉迟或沉细",
      ],
    );
  }
  
  /// 获取阴虚质特性
  static ConstitutionTraits getYinDeficiencyTraits() {
    return const ConstitutionTraits(
      type: ConstitutionType.yinDeficiency,
      name: "阴虚质",
      description: "阴虚质是指体内阴液亏损，以口燥咽干，手足心热为主要特征的体质状态。",
      mainFeatures: [
        "手足心热，颧红",
        "口干咽燥，特别是夜间",
        "鼻干不适，眼干",
        "大便干结，小便短黄",
        "舌红少苔，脉细数",
      ],
      regulationPrinciple: "滋阴润燥，清热养血，注重情志调养。",
      dietarySuggestions: [
        "多食滋阴润燥食物，如银耳、百合、梨等",
        "少吃辛辣、煎炸、温热食物",
        "保持充分水分摄入",
      ],
      lifestyleSuggestions: [
        "保持充足睡眠，早睡晚起",
        "避免过度劳累和熬夜",
        "保持室内湿度，避免干燥环境",
      ],
      psychologicalSuggestions: [
        "保持心情平和，避免急躁情绪",
        "培养安静的爱好，如读书、绘画等",
        "学习放松技巧，减轻压力",
      ],
      exerciseSuggestions: [
        "选择柔和缓慢的运动，如太极、瑜伽",
        "避免大量出汗和剧烈运动",
        "晨练或傍晚运动，避开中午高温时段",
      ],
      suitableFoods: [
        "银耳", "百合", "梨", "芝麻", "豆腐", "蜂蜜", "糯米", "鸭肉",
      ],
      unsuitableFoods: [
        "辛辣食物", "油炸食物", "浓茶", "咖啡", "酒", "羊肉", "韭菜",
      ],
      relatedDiseaseRisks: [
        "易患口腔溃疡、咽喉炎",
        "可能出现失眠、盗汗等症状",
        "长期阴虚可导致阴阳两虚",
        "女性可能出现月经不调",
      ],
      diagnosticPoints: [
        "面色潮红或颧部红赤",
        "口干咽燥，喜饮冷水",
        "手足心热，不耐热",
        "舌红少苔或无苔，舌体瘦",
        "脉细数",
      ],
    );
  }
  
  /// 获取痰湿质特性
  static ConstitutionTraits getPhlegmDampnessTraits() {
    return const ConstitutionTraits(
      type: ConstitutionType.phlegmDampness,
      name: "痰湿质",
      description: "痰湿质是指体内痰湿停聚，以形体肥胖，腹部肥满为主要特征的体质状态。",
      mainFeatures: [
        "体形肥胖，腹部松软",
        "多痰，咳吐痰多",
        "胸闷，容易气喘",
        "口黏腻或甜，苔腻",
        "脉滑",
      ],
      regulationPrinciple: "健脾化湿，祛痰降浊，控制体重，注重运动。",
      dietarySuggestions: [
        "饮食清淡，少食多餐",
        "避免甜食、油腻、精细加工食品",
        "多食具有利水渗湿作用的食物，如薏米、赤小豆等",
      ],
      lifestyleSuggestions: [
        "保持规律作息，避免久坐不动",
        "避免潮湿环境，保持居室干燥通风",
        "减少夜间进食，睡前3小时不进食",
      ],
      psychologicalSuggestions: [
        "保持情绪稳定，避免忧思郁结",
        "培养活跃的生活方式",
        "制定健康减重计划，逐步实现",
      ],
      exerciseSuggestions: [
        "坚持有氧运动，如快走、慢跑、游泳",
        "适当增加运动强度和时间",
        "配合力量训练，增加肌肉量",
      ],
      suitableFoods: [
        "薏米", "赤小豆", "冬瓜", "荷叶", "山楂", "萝卜", "苦瓜", "绿茶",
      ],
      unsuitableFoods: [
        "油炸食品", "甜食", "精细米面", "肥肉", "奶油", "酒", "冷饮",
      ],
      relatedDiseaseRisks: [
        "易患肥胖症、代谢综合征",
        "容易出现高血压、高血脂",
        "可能发生糖尿病",
        "呼吸系统疾病风险增加",
      ],
      diagnosticPoints: [
        "体形肥胖，腹部松软肥满",
        "面色淡黄或晦暗",
        "痰多，胸闷，气短",
        "舌体胖大，苔厚腻",
        "脉滑",
      ],
    );
  }
  
  /// 获取湿热质特性
  static ConstitutionTraits getDampnessHeatTraits() {
    return const ConstitutionTraits(
      type: ConstitutionType.dampnessHeat,
      name: "湿热质",
      description: "湿热质是指体内湿热内蕴，以面垢油光，口苦为主要特征的体质状态。",
      mainFeatures: [
        "面色偏黄或油光发亮",
        "口苦或口臭，口干但不想喝水",
        "大便粘滞不爽，小便黄",
        "容易长痤疮、疖肿",
        "舌红，苔黄腻，脉滑数",
      ],
      regulationPrinciple: "清热利湿，调理脾胃，注重饮食清淡。",
      dietarySuggestions: [
        "饮食清淡，避免油腻、辛辣、甜腻食物",
        "多食具有清热利湿作用的食物，如绿豆、苦瓜等",
        "避免饮酒和咖啡等刺激性饮品",
      ],
      lifestyleSuggestions: [
        "保持作息规律，避免熬夜",
        "保持居室通风干燥",
        "注意个人卫生，勤换衣物",
      ],
      psychologicalSuggestions: [
        "保持情绪平和，避免暴躁易怒",
        "学习压力管理技巧",
        "保持心情愉悦",
      ],
      exerciseSuggestions: [
        "进行适量有氧运动，如慢跑、游泳",
        "避免在高温环境下剧烈运动",
        "运动后及时补充水分",
      ],
      suitableFoods: [
        "绿豆", "苦瓜", "冬瓜", "赤小豆", "薏米", "蚕豆", "芹菜", "西瓜",
      ],
      unsuitableFoods: [
        "油炸食品", "辛辣食物", "肥肉", "甜食", "酒", "咖啡", "浓茶",
      ],
      relatedDiseaseRisks: [
        "易患痤疮、脂溢性皮炎等皮肤病",
        "容易出现消化不良、胃肠不适",
        "可能发生尿路感染",
        "女性可能出现妇科炎症",
      ],
      diagnosticPoints: [
        "面色偏黄或油光发亮",
        "口苦口臭，口干不欲饮",
        "大便黏滞不爽，小便短黄",
        "舌质红，苔黄腻",
        "脉滑数",
      ],
    );
  }
  
  /// 获取血瘀质特性
  static ConstitutionTraits getBloodStasisTraits() {
    return const ConstitutionTraits(
      type: ConstitutionType.bloodStasis,
      name: "血瘀质",
      description: "血瘀质是指体内血行不畅，血流不顺，以肤色晦暗，舌质紫暗为主要特征的体质状态。",
      mainFeatures: [
        "面色晦暗或有瘀斑",
        "唇色偏暗，舌下静脉曲张",
        "肌肤甲错，皮肤干燥",
        "容易有固定疼痛",
        "舌紫暗或有瘀点，脉涩",
      ],
      regulationPrinciple: "活血化瘀，行气通络，注重情志调养和适度运动。",
      dietarySuggestions: [
        "多食具有活血化瘀作用的食物，如桃仁、红花、山楂等",
        "避免过于油腻、寒凉食物",
        "少食动物内脏、油炸食品",
      ],
      lifestyleSuggestions: [
        "保持规律作息，避免过度劳累",
        "保持心情舒畅，避免情绪郁结",
        "注意保暖，避免受凉",
      ],
      psychologicalSuggestions: [
        "培养豁达开朗的性格",
        "避免抑郁、焦虑等负面情绪",
        "学习情绪管理技巧",
      ],
      exerciseSuggestions: [
        "选择有利于气血流通的运动，如太极拳、八段锦",
        "适当增加有氧运动，如快走、慢跑",
        "保持运动习惯，避免久坐不动",
      ],
      suitableFoods: [
        "桃仁", "红花", "山楂", "红枣", "黑木耳", "胡萝卜", "荠菜", "玫瑰花",
      ],
      unsuitableFoods: [
        "动物内脏", "油炸食品", "过冷食物", "浓茶", "咖啡", "酒",
      ],
      relatedDiseaseRisks: [
        "易患心脑血管疾病",
        "女性可能出现痛经、闭经等症状",
        "可能出现静脉曲张",
        "皮肤易出现紫癜、瘀斑",
      ],
      diagnosticPoints: [
        "面色晦暗或紫暗",
        "唇色偏暗，舌下静脉曲张",
        "皮肤干燥，肌肤甲错",
        "舌质紫暗或有瘀点、瘀斑",
        "脉沉细或涩",
      ],
    );
  }
  
  /// 获取气郁质特性
  static ConstitutionTraits getQiStagnationTraits() {
    return const ConstitutionTraits(
      type: ConstitutionType.qiStagnation,
      name: "气郁质",
      description: "气郁质是指气机郁滞，以神情抑郁，忧虑脆弱为主要特征的体质状态。",
      mainFeatures: [
        "情绪低落，容易忧虑",
        "胸胁胀闷，叹气多",
        "焦虑不安，易激动",
        "失眠多梦，精神紧张",
        "舌淡红，苔薄白，脉弦",
      ],
      regulationPrinciple: "疏肝解郁，调畅气机，加强情志调养。",
      dietarySuggestions: [
        "多食具有疏肝解郁作用的食物，如柴胡、佛手、玫瑰花等",
        "少食辛辣、刺激性食物",
        "均衡饮食，定时定量",
      ],
      lifestyleSuggestions: [
        "保持作息规律，避免过度劳累",
        "保持心情舒畅，培养兴趣爱好",
        "加强人际交往，避免孤独",
      ],
      psychologicalSuggestions: [
        "学习情绪管理和压力缓解技巧",
        "进行心理咨询或认知行为疗法",
        "培养积极乐观的生活态度",
      ],
      exerciseSuggestions: [
        "选择轻松愉悦的运动，如散步、太极、瑜伽",
        "在自然环境中进行运动",
        "与朋友一起参加团体运动",
      ],
      suitableFoods: [
        "佛手", "柴胡", "玫瑰花", "薄荷", "柑橘", "白萝卜", "山楂", "茉莉花茶",
      ],
      unsuitableFoods: [
        "油腻食物", "辛辣刺激食物", "咖啡", "浓茶", "酒", "烟",
      ],
      relatedDiseaseRisks: [
        "易患抑郁症、焦虑障碍等心理疾病",
        "可能出现消化系统功能紊乱",
        "女性可能出现月经不调",
        "容易出现失眠多梦",
      ],
      diagnosticPoints: [
        "情绪抑郁，性格内向",
        "胸胁胀闷，喜欢叹气",
        "消化功能不佳，食欲减退",
        "舌质淡红，苔薄白",
        "脉弦",
      ],
    );
  }
  
  /// 获取特禀质特性
  static ConstitutionTraits getSpecialConstitutionTraits() {
    return const ConstitutionTraits(
      type: ConstitutionType.specialConstitution,
      name: "特禀质",
      description: "特禀质是指先天禀赋不足，以过敏体质为主要特征的体质状态。",
      mainFeatures: [
        "容易过敏，对某些物质特别敏感",
        "皮肤容易出现荨麻疹、湿疹等",
        "对气候变化反应敏感",
        "有家族过敏史",
        "舌淡红，苔薄白，脉细",
      ],
      regulationPrinciple: "调和体质，增强正气，避免接触过敏原。",
      dietarySuggestions: [
        "避免食用已知过敏食物",
        "多食温和、易消化的食物",
        "避免刺激性食物和饮料",
      ],
      lifestyleSuggestions: [
        "保持居室清洁，减少过敏原",
        "注意保暖，避免受凉",
        "避免接触有害化学物质",
      ],
      psychologicalSuggestions: [
        "保持心情平和，减少精神压力",
        "学习应对过敏发作的心理调适方法",
        "建立健康的生活方式",
      ],
      exerciseSuggestions: [
        "选择温和的运动方式，如散步、太极",
        "避免在过敏高发季节进行户外运动",
        "逐渐增加运动量，增强体质",
      ],
      suitableFoods: [
        "淡水鱼", "瘦肉", "新鲜蔬菜", "米粥", "菊花", "蜂蜜", "山药", "莲子",
      ],
      unsuitableFoods: [
        "已知过敏食物", "海鲜", "辛辣刺激食物", "酒", "咖啡", "浓茶",
      ],
      relatedDiseaseRisks: [
        "易患过敏性鼻炎、哮喘",
        "容易出现皮肤过敏、湿疹",
        "可能对药物过敏",
        "食物过敏风险增加",
      ],
      diagnosticPoints: [
        "有过敏史或家族过敏史",
        "对特定物质或环境特别敏感",
        "反复出现过敏症状",
        "舌质淡红，苔薄白",
        "脉细",
      ],
    );
  }
}

/// 体质评估项目类
class ConstitutionAssessmentItem {
  /// 问题ID
  final String id;
  
  /// 问题内容
  final String question;
  
  /// 相关体质类型
  final ConstitutionType relatedType;
  
  /// 问题权重
  final double weight;
  
  /// 评分规则说明
  final String scoringRule;
  
  const ConstitutionAssessmentItem({
    required this.id,
    required this.question,
    required this.relatedType,
    this.weight = 1.0,
    this.scoringRule = "从不:0分; 很少:1分; 有时:2分; 经常:3分; 总是:4分",
  });
}

/// 体质评估结果类
class ConstitutionAssessmentResult {
  /// 评估ID
  final String id;
  
  /// 用户ID
  final String userId;
  
  /// 评估时间
  final DateTime assessmentTime;
  
  /// 各体质类型得分
  final Map<ConstitutionType, double> scores;
  
  /// 主要体质类型
  final List<ConstitutionType> primaryTypes;
  
  /// 次要体质类型
  final List<ConstitutionType> secondaryTypes;
  
  /// 评估结论
  final String conclusion;
  
  /// 调理建议
  final String recommendations;
  
  ConstitutionAssessmentResult({
    required this.id,
    required this.userId,
    required this.assessmentTime,
    required this.scores,
    required this.primaryTypes,
    this.secondaryTypes = const [],
    required this.conclusion,
    required this.recommendations,
  });
  
  /// 是否为平和体质
  bool isBalanced() {
    return primaryTypes.contains(ConstitutionType.balanced) && 
           primaryTypes.length == 1 && 
           secondaryTypes.isEmpty;
  }
  
  /// 转换为JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'userId': userId,
      'assessmentTime': assessmentTime.toIso8601String(),
      'scores': scores.map((key, value) => MapEntry(key.toString().split('.').last, value)),
      'primaryTypes': primaryTypes.map((type) => type.toString().split('.').last).toList(),
      'secondaryTypes': secondaryTypes.map((type) => type.toString().split('.').last).toList(),
      'conclusion': conclusion,
      'recommendations': recommendations,
    };
  }
  
  /// 从JSON创建
  factory ConstitutionAssessmentResult.fromJson(Map<String, dynamic> json) {
    return ConstitutionAssessmentResult(
      id: json['id'],
      userId: json['userId'],
      assessmentTime: DateTime.parse(json['assessmentTime']),
      scores: (json['scores'] as Map<String, dynamic>).map(
        (key, value) => MapEntry(
          ConstitutionType.values.firstWhere(
            (e) => e.toString().split('.').last == key
          ), 
          value.toDouble()
        )
      ),
      primaryTypes: (json['primaryTypes'] as List).map(
        (type) => ConstitutionType.values.firstWhere(
          (e) => e.toString().split('.').last == type
        )
      ).toList(),
      secondaryTypes: (json['secondaryTypes'] as List).map(
        (type) => ConstitutionType.values.firstWhere(
          (e) => e.toString().split('.').last == type
        )
      ).toList(),
      conclusion: json['conclusion'],
      recommendations: json['recommendations'],
    );
  }
}
