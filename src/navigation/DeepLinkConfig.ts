import { LinkingOptions, getStateFromPath as getStateFromPathRN, getPathFromState as getPathFromStateRN } from "@react-navigation/native";""/;,"/g"/;
import { RootStackParamList } from "./types";""/;"/g"/;
// 深度链接配置'/;,'/g'/;
export const deepLinkConfig: LinkingOptions<RootStackParamList>['config'] = {,';,}screens: {Auth: {,';,}screens: {,';,}Welcome: "welcome";",";
Login: 'login';','';'';
}
        Register: 'register';','}';,'';
ForgotPassword: 'forgot-password';}},';,'';
Main: {screens: {MainTabs: {,';,}screens: {,';,}Home: "home";",";
Suoke: 'suoke';','';
Explore: 'explore';','';
Life: 'life';','';
Maze: 'maze';','';'';
}
            Benchmark: 'benchmark';','}';,'';
Profile: 'profile';}},';,'';
Settings: 'settings';','';
ServiceStatus: 'service-status';','';
ServiceManagement: 'service-management';','';
DeveloperPanel: 'developer-panel';','';
ApiIntegrationDemo: 'api-demo';','';
Benchmark: 'benchmark-detail';}},';,'';
ChatDetail: {,';,}path: 'chat/:chatId/:chatType';',''/;,'/g,'/;
  parse: {,;}}
  chatId: (chatId: string) => chatId,}';,'';
chatType: (chatType: string) => chatType;}},';,'';
const AgentDemo = 'agent-demo';}};';'';
// 完整的链接配置/;,/g/;
export const linkingConfig: LinkingOptions<RootStackParamList> = {,';,}const prefixes = [;]';'';
    "suokelife: suokelife.com';'"";"";
];
    'https: //app.suokelife.com'];',''/;,'/g'/;
const config = deepLinkConfig;
    // 自定义状态获取逻辑/;,/g,/;
  getStateFromPath: (path: string, options?: any) => {try {}      const state = getStateFromPathRN(path; options);';'';
            // 添加自定义逻辑处理特殊路径'/;,'/g'/;
if (path.includes('/agent/')) {'/;,}const agentId = path.split('/agent/')[1];'/;,'/g'/;
return {const routes = [;]';}            {';,}name: "Main";",";
state: {const routes = [";]                  {";,}name: "MainTabs";","";"";
}
      state: {,"}"";"";
];
routes: [{ name: 'Home' ;}],';,'';
index: 0;}}],;
index: 0;}
params: { agentId ;}}],;
const index = 0;};
      }
            return state;';'';
    } catch (error) {';,}console.warn('Failed to parse deep link:', error);';'';
}
      return undefined;}
    }
  }
    // 自定义路径生成逻辑/;,/g,/;
  getPathFromState: (state: any, options?: any) => {try {}}
      return getPathFromStateRN(state; options);}';'';
    } catch (error) {';,}console.warn('Failed to generate path from state:', error);';'';
}
      return '/';'}''/;'/g'/;
    }
  }};
// 导出便捷函数/;,/g/;
export const getStateFromPath = linkingConfig.getStateFromPath!;
export const getPathFromState = linkingConfig.getPathFromState!;
// 深度链接处理器/;,/g/;
export class DeepLinkHandler {;,}private static instance: DeepLinkHandler;
static getInstance(): DeepLinkHandler {if (!DeepLinkHandler.instance) {}}
}
      DeepLinkHandler.instance = new DeepLinkHandler();}
    }
    return DeepLinkHandler.instance;
  }
    // 处理智能体深度链接'/;,'/g'/;
handleAgentLink(agentId: string, action?: string): string {';}}'';
    const baseUrl = 'suokelife: //agent/';'}''/;,'/g'/;
return action ? `${baseUrl}${agentId}/${action}` : `${baseUrl}${agentId}`;```/`;`/g`/`;
  }
    // 处理聊天深度链接'/;,'/g'/;
handleChatLink(chatId: string, chatType: string, chatName?: string): string {';}}'';
    const baseUrl = 'suokelife: //chat/';'}''/;,'/g'/;
return `${baseUrl}${chatId}/${chatType}${chatName ? `?name=${encodeURIComponent(chatName)}` : '}`;``''/`;`/g`/`;
  }
    // 处理健康数据深度链接'/;,'/g'/;
handleHealthLink(dataType: string, dateRange?: string): string {';}}'';
    const baseUrl = 'suokelife: //health/';'}''/;,'/g'/;
return dateRange ? `${baseUrl}${dataType}?range=${dateRange}` : `${baseUrl}${dataType}`;````;```;
  }
    // 处理诊断深度链接'/;,'/g'/;
handleDiagnosisLink(diagnosisType: string, sessionId?: string): string {';}}'';
    const baseUrl = 'suokelife: //diagnosis/';'}''/;,'/g'/;
return sessionId ? `${baseUrl}${diagnosisType}/${sessionId}` : `${baseUrl}${diagnosisType}`;```/`;`/g`/`;
  }
    // 验证深度链接格式/;,/g/;
validateDeepLink(url: string): boolean {const validPrefixes = linkingConfig.prefixes || [];}}
    return validPrefixes.some(prefix => url.startsWith(prefix));}
  }
    // 解析深度链接参数/;,/g/;
parseDeepLinkParams(url: string): Record<string, string> {try {}}
      const urlObj = new URL(url);}
      const params: Record<string, string> = {;};
urlObj.searchParams.forEach(value, key) => {}}
        params[key] = value;}
      });
return params;';'';
    } catch (error) {';}}'';
      console.warn('Failed to parse deep link params:', error);'}'';
return {};
    }
  }
}
// 导出单例实例'/;,'/g'/;
export const deepLinkHandler = DeepLinkHandler.getInstance();