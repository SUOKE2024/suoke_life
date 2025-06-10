// 根导航参数类型
export type RootStackParamList = {
  Auth: undefined;
  Main: undefined;
  ChatDetail: {
    chatId: string;
    chatType: string;
    chatName: string;
  };
  AgentChat: {
    agentId: string;
    agentName: string;
  };
  DiagnosisService: {
    serviceType: string;
  };
  AgentDemo: undefined;
  AgentList: undefined;
  AgentManagement: undefined;
};

// 认证导航参数类型
export type AuthStackParamList = {
  Welcome: undefined;
  Login: undefined;
  Register: undefined;
  ForgotPassword: undefined;
};

// 主导航参数类型
export type MainStackParamList = {
  MainTabs: undefined;
  Settings: undefined;
  ServiceStatus: undefined;
  ServiceManagement: undefined;
  DeveloperPanel: undefined;
  ApiIntegrationDemo: undefined;
  Benchmark: undefined;
  AgentList: undefined;
  AgentManagement: undefined;
};

// 主标签页参数类型
export type MainTabParamList = {
  Home: undefined;
  Suoke: undefined;
  Explore: undefined;
  Life: undefined;
  Maze: undefined;
  Benchmark: undefined;
  Business: undefined;
  Profile: undefined;
  Agents: undefined;
};

// 健康导航参数类型
export type HealthStackParamList = {
  LifeOverview: undefined;
  MedicalResources: undefined;
  AppointmentManagement: undefined;
  MedicalKnowledge: undefined;
  HealthDetail: {
    type: string;
    id?: string;
  };
  LifeEnhanced: undefined;
};

// 迷宫导航参数类型
export type MazeStackParamList = {
  MazeHome: undefined;
  MazeMain: undefined;
  MazeGame: {
    level?: number;
    difficulty?: string;
  };
  MazeResults: {
    score: number;
    time: number;
  };
  CreateMaze: undefined;
  MazeStats: undefined;
  MazeCompletion: {
    score: number;
    time: number;
    level: number;
  };
};

// 智能体导航参数类型
export type AgentStackParamList = {
  AgentList: undefined;
  AgentManagement: undefined;
  AgentChat: {
    agentId: string;
    agentName: string;
  };
  AgentProfile: {
    agentId: string;
  };
  AgentConfig: {
    agentId: string;
  };
  AgentAnalytics: {
    agentId: string;
  };
};

// 诊断导航参数类型
export type DiagnosisStackParamList = {
  DiagnosisHome: undefined;
  DiagnosisService: {
    serviceType: string;
  };
  DiagnosisHistory: undefined;
  DiagnosisResult: {
    resultId: string;
  };
  FiveDiagnosis: undefined;
  EnhancedDiagnosis: undefined;
  DiagnosisDetail: {
    diagnosisId: string;
  };
};

// 商业化导航参数类型
export type BusinessStackParamList = {
  BusinessDashboard: undefined;
  SubscriptionPlans: undefined;
  BPartnerList: undefined;
  BPartnerDetail: {
    partnerId: string;
  };
  EcosystemProducts: undefined;
  ProductDetail: {
    productId: string;
  };
  RevenueAnalytics: undefined;
  PricingManagement: undefined;
  OrderHistory: undefined;
  PaymentMethods: undefined;
  PaymentLogistics: undefined;
};

// 生活管理导航参数类型
export type LifeStackParamList = {
  LifeOverview: undefined;
  LifeEnhanced: undefined;
  HealthDashboard: undefined;
  LifestyleManagement: undefined;
  ExerciseTracking: undefined;
  NutritionManagement: undefined;
  SleepAnalysis: undefined;
  WellnessGoals: undefined;
};

// 探索导航参数类型
export type ExploreStackParamList = {
  ExploreHome: undefined;
  DiscoveryFeed: undefined;
  KnowledgeBase: undefined;
  CommunityHub: undefined;
  TrendingTopics: undefined;
  ExpertInsights: undefined;
};

// 个人中心导航参数类型
export type ProfileStackParamList = {
  ProfileMain: undefined;
  Settings: undefined;
  HealthRecords: undefined;
  PrivacySettings: undefined;
  NotificationSettings: undefined;
  AccountManagement: undefined;
  DataExport: undefined;
  HelpSupport: undefined;
};
