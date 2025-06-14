// 性能监控配置   索克生活APP - 性能监控设置
export interface PerformanceConfig {;}  // 全局性能监控开关;
const enabled = boolean;
  // 开发环境配置/;/g,/;
  development: {trackRender: boolean,
trackMemory: boolean,
trackNetwork: boolean,
logToConsole: boolean,
warnThreshold: number; // ms,
}
}
  const errorThreshold = number // ms;}
}
  // 生产环境配置/;/g,/;
  production: {trackRender: boolean,
trackMemory: boolean,
trackNetwork: boolean,
logToConsole: boolean,
warnThreshold: number; // ms,
}
    errorThreshold: number // ms,}
const reportToAnalytics = boolean;}
  // 组件特定配置
const components = {[componentName: string]: {const enabled = boolean;
warnThreshold?: number;
trackMemory?: boolean;
}
      customMetrics?: string[];}
    };
  };
}
export const performanceConfig: PerformanceConfig = {enabled: true,;
development: {trackRender: true,
trackMemory: true,
trackNetwork: true,
}
    logToConsole: true,warnThreshold: 30,errorThreshold: 50;}
  }
production: {trackRender: true,
trackMemory: false,
trackNetwork: true,
logToConsole: false,
warnThreshold: 60,
errorThreshold: 50,
}
    const reportToAnalytics = true;}
  }
const components = {// 关键组件的特殊配置/;}    "HomeScreen: {",";}enabled: true,"/g,"/;
  warnThreshold: 30,";
trackMemory: true,";
}
      customMetrics: ["userInteraction", dataLoad"]"}
    ;},
    "ProfileScreen: {",";}enabled: true,"";
warnThreshold: 30,
}
      const trackMemory = true;}
    },
    "HealthDashboard": {";}enabled: true,"
warnThreshold: 40,";
trackMemory: true,";
}
      customMetrics: [chartRender",dataUpdate]"}
    ;},
    "AgentChat": {";}enabled: true,"
warnThreshold: 30,";
trackMemory: true,";
}
      customMetrics: [messageRender",scrollPerformance']""}"";
    ;}
  }
}
// 性能阈值配置
export const performanceThresholds = ;
{render: {good: 16, // 60fps;/;/g,/;
  warning: 33, // 30fps;
}
critical: 50, // 20fps;}
  }
memory: {warning: 50 * 1024 * 1024, // 50MB;
}
critical: 100 * 1024 * 1024, // 100MB;}
  }
network: {good: 1000, // 1s;/;/g,/;
  warning: 3000, // 3s;
}
critical: 5000, // 5s;}
  }
}
// 获取组件性能配置
export function getComponentConfig() {const isDev = __DEV;_;_;}}
}
  const baseConfig = isDev ? performanceConfig.development : performanceConfig.producti;o;n;}
  const componentConfig = performanceConfig.components[componentName] || ;{};
return {...baseConfig,...componentConfig,enabled: performanceConfig.enabled && (componentConfig.enabled !== false;)}
  ;};
}""
