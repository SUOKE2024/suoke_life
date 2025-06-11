import { LinkingOptions, getPathFromState as getPathFromStateRN, getStateFromPath as getStateFromPathRN } from "@react-navigation/native";
import { RootStackParamList } from "./types";

// 深度链接配置
export const deepLinkConfig: LinkingOptions<RootStackParamList>['config'] = {
  screens: {
    Auth: {
      screens: {
        Welcome: "welcome",
        Login: 'login',
        Register: 'register',
        ForgotPassword: 'forgot-password'
      }
    },
    Main: {
      screens: {
        MainTabs: {
          screens: {
            Home: "home",
            Suoke: 'suoke',
            Explore: 'explore',
            Life: 'life',
            Maze: 'maze',
            Benchmark: 'benchmark',
            Profile: 'profile'
          }
        },
        Settings: 'settings',
        ServiceStatus: 'service-status',
        ServiceManagement: 'service-management',
        DeveloperPanel: 'developer-panel',
        ApiIntegrationDemo: 'api-demo',
        Benchmark: 'benchmark-detail'
      }
    },
    ChatDetail: {
      path: 'chat/:chatId/:chatType',
      parse: {
        chatId: (chatId: string) => chatId,
        chatType: (chatType: string) => chatType
      }
    },
    AgentDemo: 'agent-demo'
  }
};

// 完整的链接配置
export const linkingConfig: LinkingOptions<RootStackParamList> = {
  prefixes: [
    "suokelife://",
    "https://suokelife.com",
    'https://app.suokelife.com'
  ],
  config: deepLinkConfig,
  
  // 自定义状态获取逻辑
  getStateFromPath: (path: string, options?: any) => {
    try {
      const state = getStateFromPathRN(path, options);
      
      // 添加自定义逻辑处理特殊路径
      if (path.includes('/agent/')) {
        const agentId = path.split('/agent/')[1];
        return {
          routes: [
            {
              name: "Main",
              state: {
                routes: [
                  {
                    name: "MainTabs",
                    state: {
                      routes: [{ name: 'Home' }],
                      index: 0
                    },
                    params: { agentId }
                  }
                ],
                index: 0
              }
            }
          ],
          index: 0
        };
      }
      
      return state;
    } catch (error) {
      console.warn('Failed to parse deep link:', error);
      return undefined;
    }
  },
  
  // 自定义路径生成逻辑
  getPathFromState: (state: any, options?: any) => {
    try {
      return getPathFromStateRN(state, options);
    } catch (error) {
      console.warn('Failed to generate path from state:', error);
      return '/';
    }
  }
};

// 导出便捷函数
export const getStateFromPath = linkingConfig.getStateFromPath!;
export const getPathFromState = linkingConfig.getPathFromState!;

// 深度链接处理器
export class DeepLinkHandler {
  private static instance: DeepLinkHandler;

  static getInstance(): DeepLinkHandler {
    if (!DeepLinkHandler.instance) {
      DeepLinkHandler.instance = new DeepLinkHandler();
    }
    return DeepLinkHandler.instance;
  }

  // 处理智能体深度链接
  handleAgentLink(agentId: string, action?: string): string {
    const baseUrl = 'suokelife://agent/';
    return action ? `${baseUrl}${agentId}/${action}` : `${baseUrl}${agentId}`;
  }

  // 处理聊天深度链接
  handleChatLink(chatId: string, chatType: string, chatName?: string): string {
    const baseUrl = 'suokelife://chat/';
    return `${baseUrl}${chatId}/${chatType}${chatName ? `?name=${encodeURIComponent(chatName)}` : ''}`;
  }

  // 处理健康数据深度链接
  handleHealthLink(dataType: string, dateRange?: string): string {
    const baseUrl = 'suokelife://health/';
    return dateRange ? `${baseUrl}${dataType}?range=${dateRange}` : `${baseUrl}${dataType}`;
  }

  // 处理诊断深度链接
  handleDiagnosisLink(diagnosisType: string, sessionId?: string): string {
    const baseUrl = 'suokelife://diagnosis/';
    return sessionId ? `${baseUrl}${diagnosisType}/${sessionId}` : `${baseUrl}${diagnosisType}`;
  }

  // 验证深度链接格式
  validateDeepLink(url: string): boolean {
    const validPrefixes = linkingConfig.prefixes || [];
    return validPrefixes.some(prefix => url.startsWith(prefix));
  }

  // 解析深度链接参数
  parseDeepLinkParams(url: string): Record<string, string> {
    try {
      const urlObj = new URL(url);
      const params: Record<string, string> = {};
      urlObj.searchParams.forEach((value, key) => {
        params[key] = value;
      });
      return params;
    } catch (error) {
      console.warn('Failed to parse deep link params:', error);
      return {};
    }
  }
}

// 导出单例实例
export const deepLinkHandler = DeepLinkHandler.getInstance();