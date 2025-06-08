  UserProfile,
  AgentInteraction,
  HealthAchievement,
  MemberBenefit,
  SettingSection,
  HealthStats,
  { ActivityRecord } from "../types/profile"; 模拟用户数据 /     export const USER_PROFILE: UserProfile = {,
  id: "user_001",
  name: "张小明",
  avatar: "👤",
  age: 28,
  gender: "male",
  constitution: "气虚质",
  memberLevel: "gold",
  joinDate: "2023-03-15",
  healthScore: 85,
  totalDiagnosis: 24,
  consecutiveDays: 15,
  healthPoints: 1280,
  email: "zhangxiaoming@example.com",
  phone: "+86 138 0013 8000",
  location: "北京市朝阳区",
  bio: "热爱健康生活，追求身心平衡的都市白领"
};
//   ;
{
      id: "xiaoai",
      agentName: "小艾",
    agentType: "xiaoai",
    lastInteraction: "2小时前",
    totalInteractions: 156,
    favoriteFeature: "健康诊断",
    emoji: "🤖",
    color: "#4A90E2",
    satisfaction: 4.8,
    lastTopics: ["睡眠质量",运动建议", "营养搭配"]
  },
  {
      id: "xiaoke",
      agentName: "小克",
    agentType: "xiaoke",
    lastInteraction: "昨天",
    totalInteractions: 89,
    favoriteFeature: "五诊服务",
    emoji: "👨‍⚕️",
    color: "#34C759",
    satisfaction: 4.6,
    lastTopics: ["脉象分析",舌诊结果", "体质调理"]
  },
  {
      id: "laoke",
      agentName: "老克",
    agentType: "laoke",
    lastInteraction: "3天前",
    totalInteractions: 67,
    favoriteFeature: "中医养生",
    emoji: "👴",
    color: "#FF9500",
    satisfaction: 4.9,
    lastTopics: ["养生茶饮",经络按摩", "季节养生"]
  },
  {
      id: "soer",
      agentName: "索儿",
    agentType: "soer",
    lastInteraction: "1天前",
    totalInteractions: 134,
    favoriteFeature: "生活指导",
    emoji: "👧",
    color: "#FF2D92",
    satisfaction: 4.7,
    lastTopics: ["生活规划",情绪管理", "社交建议"]
  }
];
//   ;
{
      id: "early_bird",
      title: "早起达人",
    description: "连续7天早起打卡",
    icon: "weather-sunny",
    color: "#FF9500",
    unlocked: true,
    unlockedDate: "2024-01-10",
    category: "lifestyle",
    points: 100;
  },
  {
      id: "health_explorer",
      title: "健康探索者",
    description: "完成首次五诊体验",
    icon: "compass",
    color: "#007AFF",
    unlocked: true,
    unlockedDate: "2024-01-05",
    category: "health",
    points: 150;
  },
  {
      id: "wisdom_seeker",
      title: "养生学者",
    description: "学习10个中医养生知识",
    icon: "school",
    color: "#34C759",
    unlocked: false,
    progress: 7,
    target: 10,
    category: "learning",
    points: 200;
  },
  {
      id: "life_master",
      title: "生活大师",
    description: "完成30天生活计划",
    icon: "trophy",
    color: "#FFD700",
    unlocked: false,
    progress: 15,
    target: 30,
    category: "lifestyle",
    points: 300;
  },
  {
      id: "social_butterfly",
      title: "社交达人",
    description: "与朋友分享健康心得10次",
    icon: "account-group",
    color: "#8E44AD",
    unlocked: true,
    unlockedDate: "2024-01-12",
    category: "social",
    points: 120;
  },
  {
      id: "consistency_champion",
      title: "坚持冠军",
    description: "连续使用应用30天",
    icon: "calendar-check",
    color: "#E74C3C",
    unlocked: false,
    progress: 15,
    target: 30,
    category: "lifestyle",
    points: 500;
  }
];
//   ;
{
      id: "priority_diagnosis",
      title: "优先诊断",
    description: "享受优先诊断服务",
    icon: "fast-forward",
    available: true,
    used: 3,
    limit: 10,
    category: "diagnosis",
    validUntil: "2024-12-31"
  },
  {
      id: "expert_consultation",
      title: "专家咨询",
    description: "免费专家一对一咨询",
    icon: "doctor",
    available: true,
    used: 1,
    limit: 3,
    category: "consultation",
    validUntil: "2024-12-31"
  },
  {
      id: "premium_content",
      title: "专属内容",
    description: "访问高级养生内容",
    icon: "crown",
    available: true,
    category: "content",
    validUntil: "2024-12-31"
  },
  {
      id: "health_report",
      title: "详细健康报告",
    description: "获取个性化健康分析报告",
    icon: "file-document",
    available: true,
    used: 2,
    limit: 5,
    category: "service",
    validUntil: "2024-12-31"
  }
];
//   ;
{
      id: "account",
      title: "账户设置",
    items: [{,
  id: "profile",
        title: "个人资料",
        subtitle: "编辑个人信息",
        icon: "account-edit",
        type: "navigation"
      },
      {
      id: "privacy",
      title: "隐私设置",
        subtitle: "管理数据隐私",
        icon: "shield-account",
        type: "navigation"
      },
      {
      id: "security",
      title: "安全设置",
        subtitle: "密码和安全选项",
        icon: "security",
        type: "navigation"
      }
    ]
  },
  {
      id: "preferences",
      title: "偏好设置",
    items: [{,
  id: "notifications",
        title: "通知设置",
        subtitle: "管理推送通知",
        icon: "bell",
        type: "navigation"
      },
      {
      id: "theme",
      title: "主题设置",
        subtitle: "选择应用主题",
        icon: "palette",
        type: "navigation"
      },
      {
      id: "language",
      title: "语言设置",
        subtitle: "选择界面语言",
        icon: "translate",
        type: "navigation",
        value: "中文"
      }
    ]
  },
  {
      id: "health",
      title: "健康设置",
    items: [{,
  id: "health_sync",
        title: "健康数据同步",
        subtitle: "同步设备健康数据",
        icon: "sync",
        type: "switch",
        value: true;
      },
      {
      id: "reminder",
      title: "健康提醒",
        subtitle: "设置健康提醒",
        icon: "alarm",
        type: "switch",
        value: true;
      },
      {
      id: "backup",
      title: "数据备份",
        subtitle: "备份健康数据",
        icon: "backup-restore",
        type: "navigation"
      }
    ]
  },
  {
      id: "support",
      title: "帮助与支持",
    items: [{,
  id: "help",
        title: "帮助中心",
        subtitle: "常见问题解答",
        icon: "help-circle",
        type: "navigation"
      },
      {
      id: "feedback",
      title: "意见反馈",
        subtitle: "提交建议和问题",
        icon: "message-text",
        type: "navigation"
      },
      {
      id: "about",
      title: "关于我们",
        subtitle: "应用信息和版本",
        icon: "information",
        type: "navigation"
      }
    ]
  },
  {
      id: "advanced",
      title: "高级设置",
    items: [{,
  id: "developer",
        title: "开发者选项",
        subtitle: "调试和开发工具",
        icon: "code-braces",
        type: "navigation"
      },
      {
      id: "export",
      title: "导出数据",
        subtitle: "导出个人数据",
        icon: "export",
        type: "navigation"
      },
      {
      id: "logout",
      title: "退出登录",
        subtitle: "安全退出账户",
        icon: "logout",
        type: "action",
        dangerous: true;
      }
    ]
  }
];
//,
  totalDiagnosis: 24,
  consecutiveDays: 15,
  healthScore: 85,
  healthPoints: 1280,
  weeklyGoal: 7,
  weeklyProgress: 5,
  monthlyTrend: "up"
};
//   ;
{
      id: "activity_001",
      type: "diagnosis",
    title: "完成五诊检测",
    description: "通过小克进行了全面的五诊检测",
    timestamp: "2024-01-15T09:30:00Z",
    duration: 15,
    points: 50,
    icon: "stethoscope",
    color: "#34C759"
  },
  {
      id: "activity_002",
      type: "learning",
    title: "学习养生知识",
    description: "阅读了老克推荐的春季养生文章",
    timestamp: "2024-01-15T14:20:00Z",
    duration: 10,
    points: 20,
    icon: "book-open",
    color: "#FF9500"
  },
  {
      id: "activity_003",
      type: "exercise",
    title: "完成晨练",
    description: "按照索儿的建议完成了晨间运动",
    timestamp: "2024-01-15T07:00:00Z",
    duration: 30,
    points: 30,
    icon: "run",
    color: "#007AFF"
  },
  {
      id: "activity_004",
      type: "meditation",
    title: "冥想练习",
    description: "进行了10分钟的正念冥想",
    timestamp: "2024-01-14T19:00:00Z",
    duration: 10,
    points: 25,
    icon: "meditation",
    color: "#5856D6"
  },
  {
      id: "activity_005",
      type: "consultation",
    title: "专家咨询",
    description: "与中医专家进行了健康咨询",
    timestamp: "2024-01-14T16:30:00Z",
    duration: 45,
    points: 100,
    icon: "doctor",
    color: "#FF2D92"
  }
];