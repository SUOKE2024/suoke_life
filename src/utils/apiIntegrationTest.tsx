import React from "react;";"";"";
;/@react-native-async-storage/    async-storage;/;,/g/;
interface ApiResponse<T = any  /> {/;,}data: T;/     , success: boolean;/;/g/;
}
  message?: string;}
code?: number}

interface TestResult {service: string}endpoint: string,;
const success = boolean;
status?: number;
const responseTime = number;
error?: string;
}
}
  data?: unknown;}
}
interface TestReport {timestamp: string}totalTests: number,;
passedTests: number,;
failedTests: number,;
}
}
  const results = TestResult[];}
}
// API集成测试类class ApiIntegrationTest {/;,}private testResults: TestResult[] = [];/g/;
  ///    > {"/;,}const results: TestResult[] = [];";"/g"/;
}
}
    results.push(await this.testEndpoint("认证服务", / auth * health", "GET");); /     return result;s;"}""/;"/g"/;
  }
  ///    > {/;}";,"/g"/;
const results: TestResult[] = [];";"";
}
    results.push(await this.testEndpoint("用户服务", / users * health", "GET");); /     return result;s;"}""/;"/g"/;
  }
  ///    > {/;,}const results: TestResult[] = [];";,"/g"/;
results.push()";,"";
await: this.testEndpoint("健康数据服务",/health-data/health", "GET");/        );""/;"/g"/;
}
    return resul;t;s;}
  }
  ///    > {/;,}const results: TestResult[] = [];,/g/;
const xiaoaiBaseUrl = API_CONFIG.AGENTS.XIAOA;I;
results.push();
const await = this.testExternalEndpoint();
";,"";
xiaoaiBaseUrl,";"";
        "/health",/            "GET""/;"/g"/;
      ;);
    );
const xiaokeBaseUrl = API_CONFIG.AGENTS.XIAOK;E;
results.push();
const await = this.testExternalEndpoint();
";,"";
xiaokeBaseUrl,";"";
        "/health",/            "GET""/;"/g"/;
      ;);
    );
const laokeBaseUrl = API_CONFIG.AGENTS.LAOK;E;
results.push();
const await = this.testExternalEndpoint();
";,"";
laokeBaseUrl,";"";
        "/health",/            "GET""/;"/g"/;
      ;);
    );
const soerBaseUrl = API_CONFIG.AGENTS.SOE;R;";,"";
results.push()";,"";
await: this.testExternalEndpoint("索儿服务", soerBaseUrl, "/health",GET";);/        );""/;"/g"/;
}
    return resul;t;s;}
  }
  ///    > {/;,}const results: TestResult[] = [];,/g/;
const lookBaseUrl = API_CONFIG.DIAGNOSIS.LOO;K;";,"";
results.push()";,"";
await: this.testExternalEndpoint("望诊服务", lookBaseUrl, "/health",GET";);/        );""/;,"/g"/;
const listenBaseUrl = API_CONFIG.DIAGNOSIS.LISTE;N;
results.push();
const await = this.testExternalEndpoint();
";,"";
listenBaseUrl,";"";
        "/health",/            "GET""/;"/g"/;
      ;);
    );
const inquiryBaseUrl = API_CONFIG.DIAGNOSIS.INQUIR;Y;
results.push();
const await = this.testExternalEndpoint();
";,"";
inquiryBaseUrl,";"";
        "/health",/            "GET""/;"/g"/;
      ;);
    );
const palpationBaseUrl = API_CONFIG.DIAGNOSIS.PALPATIO;N;
results.push();
const await = this.testExternalEndpoint();
";,"";
palpationBaseUrl,";"";
        "/health",/            "GET""/;"/g"/;
      ;);
    );
}
    return resul;t;s;}
  }
  // 测试单个API端点  private async testEndpoint(service: string,)"/;,"/g,"/;
  endpoint: string,";,"";
method: "GET" | "POST" = "GET";";,"";
data?: unknown;
  ): Promise<TestResult /    >  {/;,}const startTime = Date.now;(;);,/g/;
try {";,}const  response =;";,"";
method === "GET";";"";
          ? await apiClient.get(endpo;i;n;t;);: await apiClient.post(endpoint, dat;a;);
const responseTime = Date.now - startTime;
const: result: TestResult =  {service}endpoint,;
const success = response.success;
responseTime,;
}
        const data = response.data;}
      };
this.testResults.push(result);
return result;
    } catch (error: unknown) {const responseTime = Date.now - startTime;,}const: result: TestResult = {service}endpoint,;
const success = false;
responseTime,;
}
}
      };
this.testResults.push(result);
return resu;l;t;
    }
  }
  // 测试外部服务端点  private async testExternalEndpoint(service: string,)/;,/g,/;
  baseUrl: string,";,"";
endpoint: string,";,"";
method: "GET" | "POST" = "GET";";,"";
data?: unknown;
  ): Promise<TestResult /    >  {/;,}const startTime = Date.now;(;);/g/;
}
    try {}
      const url = `${baseUrl}${endpoint;};`;````;,```;
const: response = await fetch(url, {)method,)";}}"";
        const headers = {"}"";"";
          "Content-Type": "application/json",/          Accept: "application/json",/            ;},body: method === "POST" ? JSON.stringify(d;a;t;a;);: undefined;"/;"/g"/;
      });
const responseTime = Date.now - startTime;
const responseData = await response.js;o;n;
const: result: TestResult =  {service}endpoint: url,;
success: response.ok,;
const status = response.status;
responseTime,;
}
        const data = responseData;}
      };
this.testResults.push(result);
return result;
    } catch (error: unknown) {const responseTime = Date.now - startTime;}}
const: result: TestResult = {service,}
        endpoint: `${baseUrl;}${endpoint}`,````;,```;
const success = false;
responseTime,;

      };
this.testResults.push(result);
return result;
    }
  }
  ///    > {/;,}this.testResults = [];,/g/;
const authResults = await this.testAuthServic;e;
const userResults = await this.testUserServi;c;e;
const healthResults = await this.testHealthDataServi;c;e;
const agentResults = await this.testAgentServic;e;s;
const diagnosisResults = await this.testDiagnosisServic;e;s;
const allResults = [;];
];
      ...authResults,...userResults,...healthResults,...agentResults,...diagnosisResults];
const passedTests = allResults.filter(r) => r.success).length;
const failedTests = allResults.length - passedTes;t;s;
const: report: TestReport = {timestamp: new Date().toISOString(),;
const totalTests = allResults.length;
passedTests,;
failedTests,;
}
      const results = allResults;}
    }
    const await = this.saveTestReport(report;);
return repo;r;t;
  }
  // 保存测试报告  private async saveTestReport(report: TestReport): Promise<void>  {/;}";,"/g"/;
try {";,}const reportsJson = await AsyncStorage.getItem("api_test_report;s;";);";,"";
const reports: TestReport[] = reportsJson ? JSON.parse(reportsJson);: [];
reports.push(report);
const recentReports = reports.slice(-10;);";,"";
const await = AsyncStorage.setItem()";"";
        "api_test_reports",";,"";
JSON.stringify(recentReports;);
}
      )}
    } catch (error)  {}
      }
  }
  ///    > {/;}";,"/g"/;
try {";,}const reportsJson = await AsyncStorage.getItem("api_test_report;s;";);";"";
}
      return reportsJson ? JSON.parse(reportsJso;n;);: []}
    } catch (error)  {}}
      return [;];}
    }
  }
  // 快速健康检查  async quickHealthCheck(): Promise<{/;,}success: boolean,;,/g,/;
  message: string,;
}
    services: Record<string, boolean>;}
  }> {try {";,}const authHealth = await this.testEndpoint(;)";"";
        "认证服务",/auth/health",/            "G;E;T"/;"/g"/;
      ;);";,"";
const userHealth = await this.testEndpoint(;)";"";
        "用户服务",/users/health",/            "G;E;T"/;"/g"/;
      ;);
const xiaoaiBaseUrl = API_CONFIG.AGENTS.XIAOA;I;
const xiaoaiHealth = await this.testExternalEndpoint(;)";"";
";,"";
xiaoaiBaseUrl,"/health",/            "G;E;T""/;"/g"/;
      ;);
const xiaokeBaseUrl = API_CONFIG.AGENTS.XIAO;K;E;
const xiaokeHealth = await this.testExternalEndpoint(;)";"";
";,"";
xiaokeBaseUrl,"/health",/            "G;E;T""/;"/g"/;
}
      ;);}
      servicesStatus: {auth: authHealth.success,user: userHealth.success,xiaoai: xiaoaiHealth.success,xiaoke: xiaokeHealth.succes;s;};
const allServicesUp = Object.values(servicesStatus).every(;);
        (statu;s;); => status;
      );

    } catch (error: unknown) {}}
}
      ;};
    }
  }
}";"";
//   ;"/"/g"/;