react";
// 索克生活环境配置管理器   支持多环境配置、配置验证和动态配置更新"
export interface EnvironmentConfig {";}  // 环境名称  name: string;"/;"/g"/;
  // 环境类型  type: "development" | "testing" | "staging" | "production/;"/g"/;
  // 服务配置  services: ServiceConfig;
  // 数据库配置  database: DatabaseConfig;
  // 缓存配置  cache: CacheConfig;
  // 监控配置  monitoring: MonitoringConfig;
  // 日志配置  logging: LoggingConfig;
  // 安全配置  security: SecurityConfig;
}
}
  // 性能配置  performance: PerformanceConfig;}
}
export interface ServiceConfig {;
// API网关配置  apiGateway: { host: string,/port: number,,/g,/;
  timeout: number,
}
  const rateLimit = number}
}
  // 智能体服务配置  agents: {/xiaoai: ServiceEndpoint,,/g,/;
  xiaoke: ServiceEndpoint,
}
    laoke: ServiceEndpoint,}
    const soer = ServiceEndpoint}
  // 诊断服务配置  diagnosis: {/look: ServiceEndpoint,,/g,/;
  listen: ServiceEndpoint,
inquiry: ServiceEndpoint,
}
    palpation: ServiceEndpoint,}
    const calculation = ServiceEndpoint}
  // 数据服务配置  data: {/healthData: ServiceEndpoint,/g/;
}
    userData: ServiceEndpoint,}
    const blockchain = ServiceEndpoint}
}
export interface ServiceEndpoint {";
host: string,"port: number,","
protocol: "http" | "https" | "grpc,";
timeout: number,
retries: number,
}
  const healthCheck = string}
}","
export interface DatabaseConfig {";}  // 主数据库  primary: {type: "postgresql" | "mysql" | "mongodb,""/host: string,,"/g,"/;
  port: number,
database: string,
username: string,
password: string,
ssl: boolean,
}
}
  const poolSize = number}
}
  // 读副本  replicas: Array<{/host: string,/g/;
}
    port: number,}
    const weight = number;}>
  // 分片配置  sharding: {/enabled: boolean,","/g,"/;
  strategy: "hash" | "range" | "directory,";
shards: Array<{id: string,
}
      host: string,}
      port: number,database: string;}>;
  };
}
export interface CacheConfig {;}  // Redis配置  redis: {host: string,port: number;/password?: string,/g,/;
  db: number,
const cluster = boolean;
}
}
    nodes?: Array<{ host: string; port: number}
}>;
  };
  // 本地缓存配置  local: { maxSize: number,}
const ttl = number;}
  // 分布式缓存配置  distributed: { enabled: boolean,"}""
const consistency = "eventual" | "strong";}";
}
export interface MonitoringConfig {;
// Prometheus配置  prometheus: { enabled: boolean,/host: string,,/g,/;
  port: number,
}
  const scrapeInterval = number}
}
  // Grafana配置  grafana: {/enabled: boolean,,/g,/;
  host: string,
}
    port: number,}
    adminUser: string,adminPassword: string;
  // 告警配置  alerting: {/enabled: boolean,/g/;
webhookUrl?: string;
emailConfig?:  {smtp: string}port: number,
}
      username: string,}
      const password = string;};
  };
  // 链路追踪配置  tracing: {/enabled: boolean;/g/;
}
    jaegerEndpoint?: string}
    const samplingRate = number;};
}","
export interface LoggingConfig {";}  // 日志级别  level: "debug" | "info" | "warn" | "error" | "fatal/;"/g"/;
  // 日志格式  format: "json" | "text/;"/g"/;
  // 日志输出  outputs: Array<{type: "console" | "file" | "elasticsearch" | "loki,""/;}}"/g"/;
}
  config: Record<string, any>}
}>;
  // 日志轮转  rotation: {/enabled: boolean,,/g,/;
  maxSize: string,
}
    maxFiles: number,}
    const maxAge = string}
  // 结构化日志  structured: {/enabled: boolean,/g/;
}
    includeStack: boolean,}
    const includeContext = boolean}
}
export interface SecurityConfig {;
// JWT配置  jwt: { secret: string,/expiresIn: string,/g/;
}
  const algorithm = string}
}
  // CORS配置  cors: {/origins: string[],/g/;
}
    methods: string[],headers: string[]}
    };
  // 加密配置  encryption: {/algorithm: string,/g/;
}
    keySize: number,}
    const saltRounds = number}
  // 区块链配置  blockchain: {/network: string,/g/;
}
    privateKey: string,}
    const contractAddress = string}
}
export interface PerformanceConfig {;
// 连接池配置  connectionPool: { maxConnections: number,/minConnections: number,,/g,/;
  acquireTimeout: number,
}
  const idleTimeout = number}
}
  // 缓存配置  cache: {/defaultTtl: number,/g/;
}
    maxMemory: string,}
    const evictionPolicy = string}
  // 并发配置  concurrency: {/maxConcurrent: number,/g/;
}
    queueSize: number,}
    const timeout = number}
}
export class EnvironmentManager {private static instance: EnvironmentManagerprivate currentConfig: EnvironmentConfig;
private configWatchers: Array<(config: EnvironmentConfig) => void> = [];
private constructor() {this.currentConfig = this.loadConfiguration()this.validateConfiguration();
}
}
    this.setupConfigWatcher()}
  }
  static getInstance(): EnvironmentManager {if (!EnvironmentManager.instance) {}
      EnvironmentManager.instance = new EnvironmentManager()}
    }
    return EnvironmentManager.instance;
  }
  // 加载配置  private loadConfiguration(): EnvironmentConfig {/;}","/g"/;
const env = process.env.NODE_ENV || "development;"";
const baseConfig = this.getBaseConfig;
const envConfig = this.getEnvironmentSpecificConfig(env;);
}
    return this.mergeConfigs(baseConfig, envConfig;)}
  }
  ///        return {/services: {,"apiGateway: {,"host: process.env.API_GATEWAY_HOST || "0.0.0.0,"","/g,"/;
  port: parseInt(process.env.API_GATEWAY_PORT || "8080");",
}
          timeout: parseInt(process.env.API_GATEWAY_TIMEOUT || "30000");","}","
rateLimit: parseInt(process.env.API_GATEWAY_RATE_LIMIT || "1000");},","
agents: {,"xiaoai: {,"host: process.env.XIAOAI_HOST || "localhost,
port: parseInt(process.env.XIAOAI_PORT || "8081");",
protocol: "http,
timeout: 30000,";
}
            retries: 3,"}
healthCheck: "/health",/              ;},"/,"/g,"/;
  xiaoke: {,"host: process.env.XIAOKE_HOST || "localhost,
port: parseInt(process.env.XIAOKE_PORT || "8082");",
protocol: "http,
timeout: 30000,";
}
            retries: 3,"}
healthCheck: "/health",/              ;},"/,"/g,"/;
  laoke: {,"host: process.env.LAOKE_HOST || "localhost,
port: parseInt(process.env.LAOKE_PORT || "8083");",
protocol: "http,
timeout: 30000,";
}
            retries: 3,"}
healthCheck: "/health",/              ;},"/,"/g,"/;
  soer: {,"host: process.env.SOER_HOST || "localhost,
port: parseInt(process.env.SOER_PORT || "8084");",
protocol: "http,
timeout: 30000,";
}
            retries: 3,"}
healthCheck: "/health",/              ;}"/;"/g"/;
        }
diagnosis: {,"look: {,"host: process.env.LOOK_SERVICE_HOST || "localhost,
port: parseInt(process.env.LOOK_SERVICE_PORT || "8085");",
protocol: "http,
timeout: 30000,";
}
            retries: 3,"}
healthCheck: "/health",/              ;},"/,"/g,"/;
  listen: {,"host: process.env.LISTEN_SERVICE_HOST || "localhost,
port: parseInt(process.env.LISTEN_SERVICE_PORT || "8086");",
protocol: "http,
timeout: 30000,";
}
            retries: 3,"}
healthCheck: "/health",/              ;},"/,"/g,"/;
  inquiry: {,"host: process.env.INQUIRY_SERVICE_HOST || "localhost,
port: parseInt(process.env.INQUIRY_SERVICE_PORT || "8087");",
protocol: "http,
timeout: 30000,";
}
            retries: 3,"}
healthCheck: "/health",/              ;},"/,"/g,"/;
  palpation: {,"host: process.env.PALPATION_SERVICE_HOST || "localhost,
port: parseInt(process.env.PALPATION_SERVICE_PORT || "8088");",
protocol: "http,
timeout: 30000,";
}
            retries: 3,"}
healthCheck: "/health",/              ;},"/,"/g,"/;
  calculation: {,"host: process.env.CALCULATION_SERVICE_HOST || "localhost,
port: parseInt(process.env.CALCULATION_SERVICE_PORT || "8089");",
protocol: "http,
timeout: 30000,";
}
            retries: 3,"}
healthCheck: "/health",/              ;}"/;"/g"/;
        }
data: {,"healthData: {,"host: process.env.HEALTH_DATA_SERVICE_HOST || "localhost,
port: parseInt(process.env.HEALTH_DATA_SERVICE_PORT || "8090");",
protocol: "http,
timeout: 30000,";
}
            retries: 3,"}
healthCheck: "/health",/              ;},"/,"/g,"/;
  userData: {,"host: process.env.USER_DATA_SERVICE_HOST || "localhost,
port: parseInt(process.env.USER_DATA_SERVICE_PORT || "8091");",
protocol: "http,
timeout: 30000,";
}
            retries: 3,"}
healthCheck: "/health",/              ;},"/,"/g,"/;
  blockchain: {,"host: process.env.BLOCKCHAIN_SERVICE_HOST || "localhost,
port: parseInt(process.env.BLOCKCHAIN_SERVICE_PORT || "8092");",
protocol: "http,
timeout: 30000,";
}
            retries: 3,"}
healthCheck: "/health",/              ;}"/;"/g"/;
        }
      }
database: {,"primary: {,"type: "postgresql,
host: process.env.DB_HOST || "localhost,
port: parseInt(process.env.DB_PORT || "5432");",
database: process.env.DB_NAME || "suoke_life,
username: process.env.DB_USER || "postgres,
password: process.env.DB_PASSWORD || ,";
}
          ssl: process.env.DB_SSL === "true,"}","
poolSize: parseInt(process.env.DB_POOL_SIZE || "10");},
replicas: [],"
sharding: {,"enabled: false,","
strategy: "hash,
}
          const shards = []}
        }
      }
cache: {,"redis: {,"host: process.env.REDIS_HOST || "localhost,
port: parseInt(process.env.REDIS_PORT || "6379");",
password: process.env.REDIS_PASSWORD,","
db: parseInt(process.env.REDIS_DB || "0");",
cluster: process.env.REDIS_CLUSTER === "true,
}
          const nodes = []"};
        ;},local: {maxSize: parseInt(process.env.LOCAL_CACHE_MAX_SIZE || "100"),ttl: parseInt(process.env.LOCAL_CACHE_TTL || "300");},distributed: {enabled: process.env.DISTRIBUTED_CACHE === 'true',consistency: "eventual;
      },monitoring: {prometheus: {enabled: process.env.PROMETHEUS_ENABLED === 'true',host: process.env.PROMETHEUS_HOST || "localhost",port: parseInt(process.env.PROMETHEUS_PORT || "9090"),scrapeInterval: parseInt(,process.env.PROMETHEUS_SCRAPE_INTERVAL || "15";)";}}"";
          )}
        },","
grafana: {,"enabled: process.env.GRAFANA_ENABLED === "true,
host: process.env.GRAFANA_HOST || "localhost,
port: parseInt(process.env.GRAFANA_PORT || "3000");",
}
          adminUser: process.env.GRAFANA_ADMIN_USER || "admin,"}","
adminPassword: process.env.GRAFANA_ADMIN_PASSWORD || "admin";},","
alerting: {,";}}
  enabled: process.env.ALERTING_ENABLED === "true,"}
webhookUrl: process.env.ALERT_WEBHOOK_URL;},","
tracing: {,"enabled: process.env.TRACING_ENABLED === "true,
}
          jaegerEndpoint: process.env.JAEGER_ENDPOINT,"}
const samplingRate = parseFloat(process.env.TRACING_SAMPLING_RATE || "0.1");}
      },","
logging: {,"level: (process.env.LOG_LEVEL as any) || "info,
format: (process.env.LOG_FORMAT as any) || "json",outputs: ;[;]{,";}}
  type: "console,"}";
const config = {}
          }
];
        ],","
rotation: {,"enabled: process.env.LOG_ROTATION === "true,
maxSize: process.env.LOG_MAX_SIZE || "100MB,
}
          maxFiles: parseInt(process.env.LOG_MAX_FILES || "10");","}","
maxAge: process.env.LOG_MAX_AGE || "30d";},","
structured: {,"enabled: process.env.STRUCTURED_LOGGING === "true,
}
          includeStack: process.env.LOG_INCLUDE_STACK === "true,"}","
includeContext: process.env.LOG_INCLUDE_CONTEXT === "true";}";
      }
security: {,"jwt: {,"secret: process.env.JWT_SECRET || "your-secret-key,
}
          expiresIn: process.env.JWT_EXPIRES_IN || "24h,"}","
algorithm: process.env.JWT_ALGORITHM || "HS256";},","
cors: {,"origins: (process.env.CORS_ORIGINS || "*").split(",),
methods: (process.env.CORS_METHODS || "GET,POST,PUT,DELETE").split(),"
          ),","
headers: (,)","
process.env.CORS_HEADERS || "Content-Type,Authorization;
}
          ).split(",);"};
        },","
encryption: {,"algorithm: process.env.ENCRYPTION_ALGORITHM || "aes-256-gcm,
}
          keySize: parseInt(process.env.ENCRYPTION_KEY_SIZE || "32");","}","
saltRounds: parseInt(process.env.SALT_ROUNDS || "12");},","
blockchain: {,"network: process.env.BLOCKCHAIN_NETWORK || "testnet,
privateKey: process.env.BLOCKCHAIN_PRIVATE_KEY || ,","
contractAddress: process.env.BLOCKCHAIN_CONTRACT_ADDRESS || "0x742d35Cc6634C0532925a3b8D4C9db96c4b4d8b1,
serviceUrl: process.env.BLOCKCHAIN_SERVICE_URL || "http://localhost:8007,""/,"/g,"/;
  gasLimit: parseInt(process.env.BLOCKCHAIN_GAS_LIMIT || "500000");",
gasPrice: process.env.BLOCKCHAIN_GAS_PRICE || "20000000000,
ipfsGateway: process.env.IPFS_GATEWAY_URL || "https://ipfs.io/ipfs/,""/,"/g,"/;
  zkpCircuitPath: process.env.ZKP_CIRCUIT_PATH || "/circuits/,""/,"/g,"/;
  enableZKP: process.env.ENABLE_ZKP === "true,
}
          enableEncryption: process.env.ENABLE_ENCRYPTION !== "false"
        }
      }
performance: {,"connectionPool: {,"maxConnections: parseInt(process.env.MAX_CONNECTIONS || "100");",
minConnections: parseInt(process.env.MIN_CONNECTIONS || "10");",
}
          acquireTimeout: parseInt(process.env.ACQUIRE_TIMEOUT || "30000");","}","
idleTimeout: parseInt(process.env.IDLE_TIMEOUT || "300000");},","
cache: {,"defaultTtl: parseInt(process.env.CACHE_DEFAULT_TTL || "3600");",
}
          maxMemory: process.env.CACHE_MAX_MEMORY || "1GB,"}","
evictionPolicy: process.env.CACHE_EVICTION_POLICY || "lru";},","
concurrency: {,"maxConcurrent: parseInt(process.env.MAX_CONCURRENT || "100");",
}
          queueSize: parseInt(process.env.QUEUE_SIZE || "1000");","}","
const timeout = parseInt(process.env.CONCURRENCY_TIMEOUT || "30000");}";
      }
    };
  }
  // 获取环境特定配置  private getEnvironmentSpecificConfig(env: string): unknown  {/;}","/g,"/;
  const: configs: Record<string, any> = {development: {,"name: "Development,
}
        type: "development,"}","
logging: { level: "debug"  ;},
monitoring: { prometheus: { enabled: false   }
grafana: { enabled: false   }
alerting: { enabled: false   }
const tracing = { enabled: false   }
        }
      },","
testing: {,"name: "Testing,
type: "testing,
}
        database: { primary: {,"}
const database = "suoke_life_test";}";
        }
const cache = { redis: { db: 1   ;}
        },","
const logging = { level: "warn"  ;}
      },","
staging: {,"name: "Staging,
}
        type: "staging,}";
monitoring: { prometheus: { enabled: true   }
grafana: { enabled: true   }
alerting: { enabled: true   }
const tracing = { enabled: true   }
        },","
logging: {,"level: "info,
outputs: [;]{,";}}
  type: "console,"}
config: {;} },
            {";}}
      type: "file,"}","
const config = { filename: "app.log"   ;} }";
];
          ];
        }
      },","
production: {,"name: "Production,
type: "production,";
database: {primary: {,}
  ssl: true,}
            poolSize: 20}
const sharding = { enabled: true  }
        }
cache: { redis: {,}
  cluster: true}
distributed: {,";}}
  enabled: true,"}
const consistency = "strong";}";
        }
monitoring: { prometheus: { enabled: true   }
grafana: { enabled: true   }
alerting: { enabled: true   }
tracing: { enabled: true, samplingRate: 0.01}
        },","
logging: {,"level: "warn,
outputs: [;]{,";}}
  type: "console,"}
config: {;} },
            {";}}
      type: "file,"}","
config: { filename: "app.log"   ;} },
            {";}}
      type: "elasticsearch,"}","
const config = { index: "suoke-logs"   ;} }";
];
          ];
        }
performance: {connectionPool: {,}
  maxConnections: 200,}
            minConnections: 20}
concurrency: {,}
  maxConcurrent: 500,}
            const queueSize = 5000}
        }
      }
    };
return configs[env] || configs.developme;n;t;
  }
  // 合并配置  private mergeConfigs(base: unknown, env: unknown): EnvironmentConfig  {/;}}/g/;
    return this.deepMerge(base, en;v;); as EnvironmentConfig}
  }
  // 深度合并对象  private deepMerge(target: unknown, source: unknown): unknown  {}
const result = { ...targe;t ;};
for (const key in source) {if ()"source[key] &&","
const typeof = source[key] === "object" &&";
        !Array.isArray(source[key]);
}
      ) {}
        result[key] = this.deepMerge(result[key] || {}, source[key]);
      } else {}
        result[key] = source[key]}
      }
    }
    return result;
  }
  // 验证配置  private validateConfiguration(): void {/const errors: string[] = [],/g/;
if (!this.currentConfig.database?.primary?.host) {}
}
    }
    if (!this.currentConfig.cache?.redis?.host) {}
}
    }
    if ()
      !this.currentConfig.security?.jwt?.secret ||","
this.currentConfig.security.jwt.secret === "your-secret-key;
    ) {}
}
    }","
if (this.currentConfig.type === "production") {"if (!this.currentConfig.database.primary.ssl) {}}"";
}
      }
      if (!this.currentConfig.monitoring.prometheus.enabled) {}
}
      }
    }
    if (errors.length > 0) {}
}
    }
  }
  // 设置配置监听器  private setupConfigWatcher(): void {/;}","/g"/;
if (process.env.NODE_ENV !== "production") {"setInterval() => {";}  // 性能监控"/,"/g,"/;
  const: performanceMonitor = usePerformanceMonitor(EnvironmentManager", {")"trackRender: true,"";
}
    trackMemory: false,}
    warnThreshold: 100, // ms ;};);
try {const newConfig = this.loadConfigurationif ();
JSON.stringify(newConfig); !== JSON.stringify(this.currentConfig);
          ) {this.currentConfig = newConfigthis.validateConfiguration();
}
            this.notifyConfigWatchers()}
          }
        } catch (error) {}
          }
      }, 30000);  }
  }
  // 通知配置监听器  private notifyConfigWatchers(): void {}
this.configWatchers.forEach(watcher); => {}
      try {}
        watcher(this.currentConfig)}
      } catch (error) {}
        }
    });
  }
  // 获取当前配置  getConfig(): EnvironmentConfig {/;}}/g/;
    return this.currentConf;i;g}
  }
  // 获取服务配置  getServiceConfig(serviceName: string): ServiceEndpoint | undefined  {/const services = this.currentConfig.servic;e;s,/g/;
if (services.agents[serviceName as keyof typeof services.agents]) {}
      return services.agents[serviceName as keyof typeof services.agents;]}
    }
    if (services.diagnosis[serviceName as keyof typeof services.diagnosis]) {}
      return services.diagnosis[serviceName as keyof typeof services.diagnosis;]}
    }
    if (services.data[serviceName as keyof typeof services.data]) {}
      return services.data[serviceName as keyof typeof services.data;]}
    }
    return undefin;e;d;
  }
  // 添加配置监听器  addConfigWatcher(watcher: (config: EnvironmentConfig) => void): void {/;}}/g/;
    this.configWatchers.push(watcher)}
  }
  // 移除配置监听器  removeConfigWatcher(watcher: (config: EnvironmentConfig) => void): void {/const index = this.configWatchers.indexOf(watche;r;),/g/;
if (index !== -1) {}
      this.configWatchers.splice(index, 1)}
    }
  }
  ///        this.currentConfig = this.deepMerge(this.currentConfig, updates);
this.validateConfiguration();
this.notifyConfigWatchers();
  }
  // 重载配置  reloadConfig(): void {/this.currentConfig = this.loadConfiguration(),/g/;
this.validateConfiguration();
}
    this.notifyConfigWatchers()}
  }
  // 获取配置摘要  getConfigSummary(): {/environment: string,,/g,/;
  services: number,
monitoring: boolean,
}
    caching: boolean,}
    const security = boolean;} {const services = this.currentConfig.servic;e;sconst  serviceCount =;
Object.keys(services.agents).length +;
Object.keys(services.diagnosis).length +;";
}
      Object.keys(services.data).length ;+"};
      ;1  return {environment: this.currentConfig.name,services: serviceCount,monitoring: this.currentConfig.monitoring.prometheus.enabled,caching: this.currentConfig.cache.redis.host !== 'localhost',security: this.currentConfig.security.jwt.secret !== "your-secret-key;
  };
};","
export default EnvironmentManager;""
