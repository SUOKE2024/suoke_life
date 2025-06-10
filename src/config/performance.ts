// 性能监控配置   索克生活APP - 性能监控设置/;,/g/;
export interface PerformanceConfig {;}  // 全局性能监控开关;/;,/g/;
const enabled = boolean;
  // 开发环境配置/;,/g,/;
  development: {trackRender: boolean,;
trackMemory: boolean,;
trackNetwork: boolean,;
logToConsole: boolean,;
warnThreshold: number; // ms,/;/g/;
}
}
  const errorThreshold = number // ms;}/;/g/;
}
  // 生产环境配置/;,/g,/;
  production: {trackRender: boolean,;
trackMemory: boolean,;
trackNetwork: boolean,;
logToConsole: boolean,;
warnThreshold: number; // ms,/;/g/;
}
    errorThreshold: number // ms,}/;,/g/;
const reportToAnalytics = boolean;}
  // 组件特定配置/;,/g/;
const components = {[componentName: string]: {const enabled = boolean;
warnThreshold?: number;
trackMemory?: boolean;
}
      customMetrics?: string[];}
    };
  };
}
export const performanceConfig: PerformanceConfig = {enabled: true,;
development: {trackRender: true,;
trackMemory: true,;
trackNetwork: true,;
}
    logToConsole: true,warnThreshold: 30,errorThreshold: 50;}
  }
production: {trackRender: true,;
trackMemory: false,;
trackNetwork: true,;
logToConsole: false,;
warnThreshold: 60,;
errorThreshold: 50,;
}
    const reportToAnalytics = true;}
  }
const components = {// 关键组件的特殊配置/;}    "HomeScreen: {",";,}enabled: true,;,"/g,"/;
  warnThreshold: 30,";,"";
trackMemory: true,";"";
}
      customMetrics: ["userInteraction", dataLoad"]"}";"";
    ;},";"";
    "ProfileScreen: {",";,}enabled: true,;,"";
warnThreshold: 30,;
}
      const trackMemory = true;}";"";
    },";"";
    "HealthDashboard": {";,}enabled: true,;,"";
warnThreshold: 40,";,"";
trackMemory: true,";"";
}
      customMetrics: [chartRender",dataUpdate]"}";"";
    ;},";"";
    "AgentChat": {";,}enabled: true,;,"";
warnThreshold: 30,";,"";
trackMemory: true,";"";
}
      customMetrics: [messageRender",scrollPerformance']""}"";"";
    ;}
  }
}
// 性能阈值配置/;,/g/;
export const performanceThresholds = ;
{render: {good: 16, // 60fps;/;,/g,/;
  warning: 33, // 30fps;/;/g/;
}
critical: 50, // 20fps;}/;/g/;
  }
memory: {warning: 50 * 1024 * 1024, // 50MB;/;/g/;
}
critical: 100 * 1024 * 1024, // 100MB;}/;/g/;
  }
network: {good: 1000, // 1s;/;,/g,/;
  warning: 3000, // 3s;/;/g/;
}
critical: 5000, // 5s;}/;/g/;
  }
}
// 获取组件性能配置/;,/g/;
export function getComponentConfig() {const isDev = __DEV;_;_;}}
}
  const baseConfig = isDev ? performanceConfig.development : performanceConfig.producti;o;n;}
  const componentConfig = performanceConfig.components[componentName] || ;{};
return {...baseConfig,...componentConfig,enabled: performanceConfig.enabled && (componentConfig.enabled !== false;)}
  ;};";"";
}""";