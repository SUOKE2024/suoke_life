
  LifeSuggestion,
  HealthMetric,
  LifePlan,
  LifeHabit,
  LifeGoal,
  { LifeStats } from "../types/life";//  *  索儿的生活建议 *// export const SOER_SUGGESTIONS: LifeSuggestion[] = [{,
    id: "morning_routine",
    title: "建立晨间仪式",
    description: "每天早上花15分钟做伸展运动，喝一杯温水，为新的一天做好准备",
    category: "exercise",
    priority: "high",
    icon: "weather-sunny",
    color: "#FF9500",
    completed: false,
    timeEstimate: "15分钟",
    benefits: ["提升精力", "改善心情", "增强体质"],
    steps: ["起床后喝一杯温水", "做5分钟伸展运动", "深呼吸3次"]
  },
  {
    id: "healthy_lunch",
    title: "营养午餐搭配",
    description: "今日推荐：蒸蛋羹配时令蔬菜，营养均衡又美味",
    category: "diet",
    priority: "high",
    icon: "food",
    color: "#34C759",
    completed: false,
    timeEstimate: "30分钟",
    benefits: ["补充营养", "维持血糖稳定", "提供持续能量"],
    steps: ["准备新鲜蔬菜", "制作蒸蛋羹", "合理搭配主食"]
  },
  {
    id: "afternoon_break",
    title: "下午茶时光",
    description: "工作间隙来一杯花茶，配点坚果，既解乏又健康",
    category: "mental",
    priority: "medium",
    icon: "tea",
    color: "#5856D6",
    completed: true,
    timeEstimate: "10分钟",
    benefits: ["缓解疲劳", "补充营养", "放松心情"],
    steps: ["选择合适的花茶", "准备少量坚果", "享受安静时光"]
  },
  {
    id: "evening_walk",
    title: "晚间散步",
    description: "饭后一小时，到附近公园走走，有助消化和放松心情",
    category: "exercise",
    priority: "medium",
    icon: "walk",
    color: "#007AFF",
    completed: false,
    timeEstimate: "30分钟",
    benefits: ["促进消化", "改善睡眠", "减轻压力"],
    steps: ["选择安全的路线", "穿舒适的鞋子", "保持适中的步速"]
  },
  {
    id: "digital_detox",
    title: "数字排毒",
    description: "睡前一小时关闭电子设备，读书或听音乐，提高睡眠质量",
    category: "sleep",
    priority: "high",
    icon: "cellphone-off",
    color: "#FF2D92",
    completed: false,
    timeEstimate: "60分钟",
    benefits: ["改善睡眠质量", "减少蓝光伤害", "放松大脑"],
    steps: ["设置设备关闭时间", "准备睡前读物", "创造安静环境"]
  },
  {
    id: "social_connection",
    title: "社交联系",
    description: "给家人朋友打个电话，分享今天的美好时光",
    category: "social",
    priority: "low",
    icon: "phone",
    color: "#8E44AD",
    completed: false,
    timeEstimate: "20分钟",
    benefits: ["增进感情", "分享快乐", "获得支持"],
    steps: ["选择合适的时间", "准备聊天话题", "真诚表达关心"]
  }
];
// 健康指标数据 * export const HEALTH_METRICS: HealthMetric[] = [;{, */
    id: "mood",
    name: "心情指数",
    value: 85,
    unit: "分",
    target: 80,
    icon: "emoticon-happy",
    color: "#FF9500",
    trend: "up",
    suggestion: "保持积极心态，今天心情不错！",
    history: [{, date: "2024-01-01", value: 75},
      { date: "2024-01-02", value: 80},
      { date: "2024-01-03", value: 85}
    ]
  },
  {
    id: "energy",
    name: "精力水平",
    value: 72,
    unit: "分",
    target: 80,
    icon: "lightning-bolt",
    color: "#34C759",
    trend: "stable",
    suggestion: "适当休息，补充能量",
    history: [{, date: "2024-01-01", value: 70},
      { date: "2024-01-02", value: 72},
      { date: "2024-01-03", value: 72}
    ]
  },
  {
    id: "stress",
    name: "压力水平",
    value: 35,
    unit: "分",
    target: 30,
    icon: "head-cog",
    color: "#FF2D92",
    trend: "down",
    suggestion: "压力稍高，建议放松一下",
    history: [{, date: "2024-01-01", value: 40},
      { date: "2024-01-02", value: 38},
      { date: "2024-01-03", value: 35}
    ]
  },
  {
    id: "balance",
    name: "生活平衡",
    value: 78,
    unit: "分",
    target: 85,
    icon: "scale-balance",
    color: "#5856D6",
    trend: "up",
    suggestion: "工作生活平衡良好",
    history: [{, date: "2024-01-01", value: 70},
      { date: "2024-01-02", value: 75},
      { date: "2024-01-03", value: 78}
    ]
  }
];
// 生活计划数据 * export const LIFE_PLANS: LifePlan[] = [;{, */
    id: "healthy_lifestyle",
    title: "健康生活方式养成",
    description: "建立规律作息，培养健康饮食和运动习惯",
    progress: 68,
    duration: "21天",
    category: "生活习惯",
    icon: "heart-pulse",
    color: "#FF2D92",
    nextAction: "完成今日晨练",
    startDate: "2024-01-01",
    endDate: "2024-01-21",
    milestones: [{,
        id: "week1",
        title: "第一周目标",
        description: "建立基础作息规律",
        targetDate: "2024-01-07",
        completed: true,
        completedDate: "2024-01-07"
      },
      {
        id: "week2",
        title: "第二周目标",
        description: "加入运动习惯",
        targetDate: "2024-01-14",
        completed: true,
        completedDate: "2024-01-14"
      },
      {
        id: "week3",
        title: "第三周目标",
        description: "完善饮食结构",
        targetDate: "2024-01-21",
        completed: false
      }
    ],
    rewards: ["健康徽章", "专属称号", "健康积分"]
  },
  {
    id: "work_life_balance",
    title: "工作生活平衡",
    description: "合理安排工作时间，留出充足的休息和娱乐时间",
    progress: 45,
    duration: "30天",
    category: "时间管理",
    icon: "scale-balance",
    color: "#5856D6",
    nextAction: "设置工作边界",
    startDate: "2024-01-01",
    endDate: "2024-01-30",
    milestones: [{,
        id: "boundaries",
        title: "设定工作边界",
        description: "明确工作时间和休息时间",
        targetDate: "2024-01-10",
        completed: true,
        completedDate: "2024-01-08"
      },
      {
        id: "hobbies",
        title: "培养兴趣爱好",
        description: "每周至少2小时兴趣活动",
        targetDate: "2024-01-20",
        completed: false
      }
    ],
    rewards: ["时间管理大师", "生活平衡者", "效率提升奖"]
  },
  {
    id: "mindfulness_practice",
    title: "正念冥想练习",
    description: "每日10分钟冥想，提升专注力和内心平静",
    progress: 82,
    duration: "14天",
    category: "心理健康",
    icon: "meditation",
    color: "#34C759",
    nextAction: "今日冥想练习",
    startDate: "2024-01-01",
    endDate: "2024-01-14",
    milestones: [{,
        id: "basic",
        title: "基础冥想",
        description: "掌握基本冥想技巧",
        targetDate: "2024-01-05",
        completed: true,
        completedDate: "2024-01-04"
      },
      {
        id: "advanced",
        title: "进阶练习",
        description: "尝试不同冥想方法",
        targetDate: "2024-01-14",
        completed: false
      }
    ],
    rewards: ["正念大师", "内心平静奖", "专注力提升"]
  }
];
// 生活习惯数据 * export const LIFE_HABITS: LifeHabit[] = [;{, */
    id: "morning_exercise",
    name: "晨间运动",
    description: "每天早上进行15分钟运动",
    category: "health",
    frequency: "daily",
    streak: 7,
    bestStreak: 15,
    icon: "run",
    color: "#FF9500",
    reminder: {
      enabled: true,
      time: "07:00",
      days: [1, 2, 3, 4, 5, 6, 0],
      message: "开始今天的晨间运动吧！"
    }
  },
  {
    id: "reading",
    name: "每日阅读",
    description: "每天阅读至少30分钟",
    category: "productivity",
    frequency: "daily",
    streak: 12,
    bestStreak: 25,
    icon: "book-open",
    color: "#34C759",
    reminder: {
      enabled: true,
      time: "21:00",
      days: [1, 2, 3, 4, 5, 6, 0],
      message: "今天的阅读时间到了！"
    }
  },
  {
    id: "meditation",
    name: "冥想练习",
    description: "每天进行10分钟冥想",
    category: "wellness",
    frequency: "daily",
    streak: 5,
    bestStreak: 20,
    icon: "meditation",
    color: "#5856D6",
    reminder: {
      enabled: true,
      time: "19:00",
      days: [1, 2, 3, 4, 5, 6, 0],
      message: "放松心情，开始冥想吧！"
    }
  }
];
// 生活目标数据 * export const LIFE_GOALS: LifeGoal[] = [;{, */
    id: "fitness_goal",
    title: "提升身体素质",
    description: "通过规律运动和健康饮食，提升整体身体素质",
    category: "health",
    priority: "high",
    progress: 65,
    targetDate: "2024-06-01",
    status: "active",
    subGoals: [{, id: "weight", title: "减重5公斤", completed: false},
      {
        id: "endurance",
        title: "提升心肺功能",
        completed: true,
        completedDate: "2024-01-15"
      },
      { id: "strength", title: "增强肌肉力量", completed: false}
    ]
  },
  {
    id: "career_goal",
    title: "职业技能提升",
    description: "学习新技能，提升职业竞争力",
    category: "career",
    priority: "high",
    progress: 40,
    targetDate: "2024-12-31",
    status: "active",
    subGoals: [{, id: "certification", title: "获得专业认证", completed: false},
      {
        id: "networking",
        title: "扩展职业网络",
        completed: true,
        completedDate: "2024-01-10"
      },
      { id: "leadership", title: "提升领导能力", completed: false}
    ]
  }
];
// 生活统计数据 * export const LIFE_STATS: LifeStats = {, */;
  totalSuggestions: 156,
  completedSuggestions: 89,
  activePlans: 3,
  completedPlans: 8,
  currentStreak: 15,
  longestStreak: 32,
  averageScore: 78.5,
  improvementRate: 12.3
};