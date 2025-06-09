// 根导航参数类型
export type RootStackParamList = {
  Auth: undefined;,
  Main: undefined;
  ChatDetail: {,
  chatId: string;
    chatType: string;,
  chatName: string;
  };
  AgentChat: {,
  agentId: string;
    agentName: string;
  };
  DiagnosisService: {,
  serviceType: string;
  };
  AgentDemo: undefined;
};
// 认证导航参数类型
export type AuthStackParamList = {
  Welcome: undefined;,
  Login: undefined;
  Register: undefined;,
  ForgotPassword: undefined;
};
// 主导航参数类型
export type MainStackParamList = {
  MainTabs: undefined;,
  Settings: undefined;
  ServiceStatus: undefined;,
  ServiceManagement: undefined;
  DeveloperPanel: undefined;,
  ApiIntegrationDemo: undefined;
  Benchmark: undefined;
};
// 主标签页参数类型
export type MainTabParamList = {
  Home: undefined;,
  Suoke: undefined;
  Explore: undefined;,
  Life: undefined;
  Maze: undefined;,
  Benchmark: undefined;
  Profile: undefined;
};
// 健康导航参数类型
export type HealthStackParamList = {
  LifeOverview: undefined;,
  MedicalResources: undefined;
  AppointmentManagement: undefined;,
  MedicalKnowledge: undefined;
  HealthDetail: {,
  type: string;
    id?: string;
  };
};
// 迷宫导航参数类型
export type MazeStackParamList = {
  MazeHome: undefined;,
  MazeGame: {
    level?: number;
    difficulty?: string;
  };
  MazeResults: {,
  score: number;
    time: number;
  };
};
// 智能体导航参数类型
export type AgentStackParamList = {
  AgentList: undefined;,
  AgentChat: {
    agentId: string;,
  agentName: string;
  };
  AgentProfile: {,
  agentId: string;
  };
};
// 诊断导航参数类型
export type DiagnosisStackParamList = {
  DiagnosisHome: undefined;,
  DiagnosisService: {
    serviceType: string;
  };
  DiagnosisHistory: undefined;,
  DiagnosisResult: {
    resultId: string;
  };
};
