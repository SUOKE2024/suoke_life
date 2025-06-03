import { ServiceItem, CategoryConfig, ServiceCategory } from "../types/////    suoke";
//////
// 分类配置 * export const SERVICE_CATEGORIES: CategoryConfig[] = [{ key: "all", label: "全部", icon: "view-grid", color: "#007AFF"}, ////
  { key: "diagnosis", label: "五诊", icon: "stethoscope", color: "#34C759"},
  { key: "eco", label: "生态服务", icon: "leaf", color: "#32D74B"},
  { key: "product", label: "产品", icon: "package-variant", color: "#8E44AD"},
  { key: "service", label: "服务", icon: "medical-bag", color: "#E74C3C"},
  {
    key: "subscription",
    label: "订阅",
    icon: "calendar-check",
    color: "#3498DB"
  },
  {
    key: "appointment",
    label: "预约",
    icon: "calendar-clock",
    color: "#F39C12"
  },
  { key: "market", label: "市集", icon: "store", color: "#27AE60"},
  { key: "custom", label: "定制", icon: "cog", color: "#9B59B6"},
  { key: "supplier", label: "供应商", icon: "truck", color: "#34495E"}
];
;
// 五诊服务配置（从四诊升级为五诊） * export const DIAGNOSIS_SERVICES: ServiceItem[] = [////   ;
{
    id: "look_diagnosis",
    title: "望诊服务",
    subtitle: "面色舌象智能分析",
    icon: "eye",
    color: "#007AFF",
    category: "diagnosis",
    description: "通过AI视觉技术分析面色、舌象、体态等外在表现",
    features: ["面色分析", "舌象检测", "体态评估", "精神状态评估"],
    price: "¥99",
    available: true,
    rating: 4.8,
    reviewCount: 1234,
    estimatedTime: "15分钟",
    tags: ["AI分析", "无创检测", "即时结果"]
  },
  {
    id: "listen_diagnosis",
    title: "闻诊服务",
    subtitle: "声音气味智能识别",
    icon: "ear-hearing",
    color: "#34C759",
    category: "diagnosis",
    description: "通过声纹分析和气味识别技术进行健康评估",
    features: ["语音分析", "呼吸音检测", "咳嗽分析", "气味识别"],
    price: "¥79",
    available: true,
    rating: 4.6,
    reviewCount: 987,
    estimatedTime: "10分钟",
    tags: ["声纹识别", "呼吸分析", "智能诊断"]
  },
  {
    id: "inquiry_diagnosis",
    title: "问诊服务",
    subtitle: "智能问诊对话",
    icon: "comment-question",
    color: "#FF9500",
    category: "diagnosis",
    description: "基于中医理论的智能问诊系统，全面了解症状和病史",
    features: ["症状询问", "病史采集", "生活习惯评估", "家族史分析"],
    price: "¥59",
    available: true,
    rating: 4.9,
    reviewCount: 2156,
    estimatedTime: "20分钟",
    tags: ["智能对话", "全面评估", "个性化问诊"]
  },
  {
    id: "palpation_diagnosis",
    title: "切诊服务",
    subtitle: "脉象触诊检测",
    icon: "hand-back-right",
    color: "#FF2D92",
    category: "diagnosis",
    description: "结合传感器技术的现代化脉诊和触诊服务",
    features: ["脉象分析", "腹部触诊", "穴位检查", "皮肤触感"],
    price: "¥129",
    available: true,
    rating: 4.7,
    reviewCount: 856,
    estimatedTime: "25分钟",
    tags: ["传感器检测", "脉象分析", "专业触诊"]
  },
  {
    id: "calculation_diagnosis",
    title: "算诊服务",
    subtitle: "时间医学智能推演",
    icon: "calculator",
    color: "#8E44AD",
    category: "diagnosis",
    description:
      "基于传统中医算诊理论，结合五运六气、八字八卦等进行个性化健康分析",
    features: ["五运六气分析",
      "八字体质推算",
      "八卦体质分析",
      "子午流注时间医学"
    ],
    price: "¥149",
    available: true,
    rating: 4.9,
    reviewCount: 567,
    estimatedTime: "30分钟",
    tags: ["传统算诊", "时间医学", "个性化分析", "五运六气"]
  }
];
// 生态服务配置 * export const ECO_SERVICES: ServiceItem[] = [////   ;
{
    id: "mountain_wellness",
    title: "山水养生",
    subtitle: "自然环境康养体验",
    icon: "mountain",
    color: "#32D74B",
    category: "eco",
    description: "在优美的自然环境中进行康养活动",
    features: ["森林浴", "温泉疗养", "登山健身", "冥想静心"],
    price: "¥299/天",/////        available: true,
    rating: 4.9,
    reviewCount: 543,
    estimatedTime: "1-3天",
    tags: ["自然疗法", "环境康养", "身心放松"]
  },
  {
    id: "organic_farming",
    title: "有机农场",
    subtitle: "食农结合健康体验",
    icon: "sprout",
    color: "#4CAF50",
    category: "eco",
    description: "参与有机农业，体验从种植到餐桌的健康生活",
    features: ["有机种植", "农场体验", "健康饮食", "生态教育"],
    price: "¥199/天",/////        available: true,
    rating: 4.8,
    reviewCount: 432,
    estimatedTime: "半天-1天",
    tags: ["有机农业", "健康饮食", "生态体验"]
  },
  {
    id: "herbal_garden",
    title: "本草园",
    subtitle: "中药材种植与学习",
    icon: "flower",
    color: "#8BC34A",
    category: "eco",
    description: "学习中药材知识，参与种植和采摘",
    features: ["药材识别", "种植体验", "采摘加工", "药膳制作"],
    price: "¥159/次",/////        available: true,
    rating: 4.7,
    reviewCount: 321,
    estimatedTime: "3-4小时",
    tags: ["中药材", "传统文化", "实践学习"]
  }
];
// 其他服务配置 * export const OTHER_SERVICES: ServiceItem[] = [////   ;
{
    id: "health_products",
    title: "健康产品",
    subtitle: "精选健康商品",
    icon: "package-variant",
    color: "#8E44AD",
    category: "product",
    description: "经过专业筛选的健康产品和保健用品",
    features: ["中药材", "保健品", "健康器械", "养生用品"],
    available: true,
    rating: 4.6,
    reviewCount: 1876,
    tags: ["品质保证", "专业筛选", "健康生活"]
  },
  {
    id: "medical_services",
    title: "医疗服务",
    subtitle: "专业医疗咨询",
    icon: "medical-bag",
    color: "#E74C3C",
    category: "service",
    description: "提供专业的医疗咨询和健康管理服务",
    features: ["专家咨询", "健康评估", "治疗方案", "康复指导"],
    available: true,
    rating: 4.8,
    reviewCount: 2341,
    estimatedTime: "30-60分钟",
    tags: ["专业医疗", "个性化服务", "全程跟踪"]
  },
  {
    id: "health_subscription",
    title: "健康订阅",
    subtitle: "个性化健康计划",
    icon: "calendar-check",
    color: "#3498DB",
    category: "subscription",
    description: "定制化的健康管理订阅服务",
    features: ["月度体检", "营养配餐", "运动计划", "健康报告"],
    price: "¥299/月",/////        available: true,
    rating: 4.7,
    reviewCount: 987,
    tags: ["个性化", "持续服务", "全面管理"]
  },
  {
    id: "appointment_booking",
    title: "预约服务",
    subtitle: "便捷预约挂号",
    icon: "calendar-clock",
    color: "#F39C12",
    category: "appointment",
    description: "快速预约医生和健康服务",
    features: ["在线挂号", "专家预约", "体检预约", "上门服务"],
    available: true,
    rating: 4.5,
    reviewCount: 1543,
    tags: ["便捷预约", "多种选择", "灵活时间"]
  },
  {
    id: "health_market",
    title: "健康市集",
    subtitle: "健康生活商城",
    icon: "store",
    color: "#27AE60",
    category: "market",
    description: "一站式健康生活用品购物平台",
    features: ["有机食品", "运动器材", "美容护肤", "家居健康"],
    available: true,
    rating: 4.6,
    reviewCount: 2876,
    tags: ["一站式购物", "品质保证", "健康生活"]
  },
  {
    id: "custom_service",
    title: "定制服务",
    subtitle: "个性化健康方案",
    icon: "cog",
    color: "#9B59B6",
    category: "custom",
    description: "根据个人需求定制专属健康解决方案",
    features: ["体质分析", "方案定制", "跟踪服务", "效果评估"],
    price: "¥999起",
    available: true,
    rating: 4.9,
    reviewCount: 234,
    estimatedTime: "1-2周",
    tags: ["个性定制", "专业分析", "效果保证"]
  },
  {
    id: "supplier_network",
    title: "供应商网络",
    subtitle: "优质供应商合作",
    icon: "truck",
    color: "#34495E",
    category: "supplier",
    description: "与优质健康产品供应商建立合作关系",
    features: ["供应商认证", "质量保证", "物流配送", "售后服务"],
    available: true,
    rating: 4.4,
    reviewCount: 567,
    tags: ["质量保证", "可靠供应", "专业服务"]
  }
];
// 所有服务 * export const ALL_SERVICES: ServiceItem[] = [////  ;
...DIAGNOSIS_SERVICES, /////    ;
  ...ECO_SERVICES,;
  ...OTHER_SERVICES;
];
// 推荐服务（基于用户行为和评分） * export const RECOMMENDED_SERVICES = ALL_SERVICES.filte////   ;
r;(; /////
  (service); => service.rating && service.rating >= 4.7;
)
  .sort((a, b); => (b.rating || 0) - (a.rating || 0))
  .slice(0, 6);
// 热门服务（基于使用量） * export const POPULAR_SERVICES = ALL_SERVICES.filte////   ;
r;(; /////
  (service); => service.reviewCount && service.reviewCount >= 1000;
)
  .sort((a, b); => (b.reviewCount || 0) - (a.reviewCount || 0))
  .slice(0, 8);