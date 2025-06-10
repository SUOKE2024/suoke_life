// 根导航参数类型/;,/g/;
export type RootStackParamList = {Auth: undefined}Main: undefined,;
ChatDetail: {chatId: string,;
chatType: string,;
}
    const chatName = string;}
  };
AgentChat: {agentId: string,;
}
    const agentName = string;}
  };
DiagnosisService: {,;}}
    const serviceType = string;}
  };
AgentDemo: undefined,;
AgentList: undefined,;
const AgentManagement = undefined;
};

// 认证导航参数类型/;,/g/;
export type AuthStackParamList = {Welcome: undefined}Login: undefined,;
Register: undefined,;
}
  const ForgotPassword = undefined;}
};

// 主导航参数类型/;,/g/;
export type MainStackParamList = {MainTabs: undefined}Settings: undefined,;
ServiceStatus: undefined,;
ServiceManagement: undefined,;
DeveloperPanel: undefined,;
ApiIntegrationDemo: undefined,;
Benchmark: undefined,;
AgentList: undefined,;
}
  const AgentManagement = undefined;}
};

// 主标签页参数类型/;,/g/;
export type MainTabParamList = {Home: undefined}Suoke: undefined,;
Explore: undefined,;
Life: undefined,;
Maze: undefined,;
Benchmark: undefined,;
Business: undefined,;
Profile: undefined,;
}
  const Agents = undefined;}
};

// 健康导航参数类型/;,/g/;
export type HealthStackParamList = {LifeOverview: undefined}MedicalResources: undefined,;
AppointmentManagement: undefined,;
MedicalKnowledge: undefined,;
HealthDetail: {const type = string;
}
    id?: string;}
  };
const LifeEnhanced = undefined;
};

// 迷宫导航参数类型/;,/g/;
export type MazeStackParamList = {MazeHome: undefined}MazeMain: undefined,;
const MazeGame = {;,}level?: number;
}
    difficulty?: string;}
  };
MazeResults: {score: number,;
}
    const time = number;}
  };
CreateMaze: undefined,;
MazeStats: undefined,;
MazeCompletion: {score: number,;
time: number,;
}
    const level = number;}
  };
};

// 智能体导航参数类型/;,/g/;
export type AgentStackParamList = {AgentList: undefined}AgentManagement: undefined,;
AgentChat: {agentId: string,;
}
    const agentName = string;}
  };
AgentProfile: {,;}}
    const agentId = string;}
  };
AgentConfig: {,;}}
    const agentId = string;}
  };
AgentAnalytics: {,;}}
    const agentId = string;}
  };
};

// 诊断导航参数类型/;,/g/;
export type DiagnosisStackParamList = {DiagnosisHome: undefined}DiagnosisService: {,;}}
    const serviceType = string;}
  };
DiagnosisHistory: undefined,;
DiagnosisResult: {,;}}
    const resultId = string;}
  };
FiveDiagnosis: undefined,;
EnhancedDiagnosis: undefined,;
DiagnosisDetail: {,;}}
    const diagnosisId = string;}
  };
};

// 商业化导航参数类型/;,/g/;
export type BusinessStackParamList = {BusinessDashboard: undefined}SubscriptionPlans: undefined,;
BPartnerList: undefined,;
BPartnerDetail: {,;}}
    const partnerId = string;}
  };
EcosystemProducts: undefined,;
ProductDetail: {,;}}
    const productId = string;}
  };
RevenueAnalytics: undefined,;
PricingManagement: undefined,;
OrderHistory: undefined,;
PaymentMethods: undefined,;
const PaymentLogistics = undefined;
};

// 生活管理导航参数类型/;,/g/;
export type LifeStackParamList = {LifeOverview: undefined}LifeEnhanced: undefined,;
HealthDashboard: undefined,;
LifestyleManagement: undefined,;
ExerciseTracking: undefined,;
NutritionManagement: undefined,;
SleepAnalysis: undefined,;
}
  const WellnessGoals = undefined;}
};

// 探索导航参数类型/;,/g/;
export type ExploreStackParamList = {ExploreHome: undefined}DiscoveryFeed: undefined,;
KnowledgeBase: undefined,;
CommunityHub: undefined,;
TrendingTopics: undefined,;
}
  const ExpertInsights = undefined;}
};

// 个人中心导航参数类型/;,/g/;
export type ProfileStackParamList = {ProfileMain: undefined}Settings: undefined,;
HealthRecords: undefined,;
PrivacySettings: undefined,;
NotificationSettings: undefined,;
AccountManagement: undefined,;
DataExport: undefined,;
}
  const HelpSupport = undefined;}
};
