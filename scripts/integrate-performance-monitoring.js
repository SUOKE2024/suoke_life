#!/usr/bin/env node;
const fs = require("fs);
const path = require(")path");

// 递归获取所有React组件文件
function getAllComponentFiles(dir, files = []) {
  const items = fs.readdirSync(dir);
  
  for (const item of items) {
    const fullPath = path.join(dir, item);
    const stat = fs.statSync(fullPath);
    
    if (stat.isDirectory() && !item.startsWith(".) && item !== "node_modules") {
      getAllComponentFiles(fullPath, files);
    } else if (item.endsWith(.tsx") && !item.endsWith(".test.tsx)) {
      files.push(fullPath);
    }
  }
  
  return files;
}

// 分析组件是否需要性能监控
function analyzeComponent(filePath) {
  try {
    const content = fs.readFileSync(filePath, "utf8");
    const fileName = path.basename(filePath, .tsx");
    
    const analysis = {
      filePath,
      fileName,
      needsMonitoring: false,
      priority: "low,
      reasons: [],
      hasMonitoring: false,
      complexity: "low",
      renderCount: 0,
      stateCount: 0,;
      effectCount: 0};
    
    // 检查是否已经有性能监控
analysis.hasMonitoring = content.includes(usePerformanceMonitor");
    
    // 分析组件复杂度
const useStateCount = (content.match(/useState/g) || []).length;
    const useEffectCount = (content.match(/useEffect/g) || []).length;
    const useMemoCount = (content.match(/useMemo/g) || []).length;
    const useCallbackCount = (content.match(/useCallback/g) || []).length;
    const renderCount = (content.match(/return\s*\(/g) || []).length;
    const lineCount = content.split("\n).length;
    
    analysis.stateCount = useStateCount;
    analysis.effectCount = useEffectCount;
    analysis.renderCount = renderCount;
    
    // 判断是否需要性能监控
const complexityFactors = [];
    
    // 高状态管理复杂度
if (useStateCount > 3) {
      complexityFactors.push("多状态管理");
      analysis.needsMonitoring = true;
    }
    
    // 多副作用
if (useEffectCount > 2) {
      complexityFactors.push(多副作用");
      analysis.needsMonitoring = true;
    }
    
    // 大量优化Hook
if (useMemoCount + useCallbackCount > 3) {
      complexityFactors.push("大量优化Hook);
      analysis.needsMonitoring = true;
    }
    
    // 大文件
if (lineCount > 200) {
      complexityFactors.push("大文件");
      analysis.needsMonitoring = true;
    }
    
    // 关键组件（根据命名判断）
    const criticalPatterns = [
      /Screen$/,
      /Dashboard/,
      /List$/,
      /Table$/,
      /Chart/,
      /Modal/,
      /Navigation/,
      /App$/,
      /Main/,
      /Home/,
      /Profile/,
      /Settings/
    ];
    
    if (criticalPatterns.some(pattern => pattern.test(fileName))) {
      complexityFactors.push(关键组件");
      analysis.needsMonitoring = true;
      analysis.priority = "high;
    }
    
    // 包含复杂渲染逻辑
if (content.includes("FlatList") || content.includes(ScrollView") || content.includes("VirtualizedList)) {
      complexityFactors.push("列表渲染");
      analysis.needsMonitoring = true;
      analysis.priority = high";
    }
    
    // 包含动画
if (content.includes("Animated) || content.includes("useSharedValue") || content.includes(withTiming")) {
      complexityFactors.push("动画组件);
      analysis.needsMonitoring = true;
      analysis.priority = "high";
    }
    
    // 网络请求
if (content.includes(fetch") || content.includes("axios) || content.includes("useQuery")) {
      complexityFactors.push(网络请求");
      analysis.needsMonitoring = true;
    }
    
    analysis.reasons = complexityFactors;
    
    // 设置复杂度等级
if (complexityFactors.length >= 3) {
      analysis.complexity = "high;
      analysis.priority = "high";
    } else if (complexityFactors.length >= 2) {
      analysis.complexity = medium";
      analysis.priority = "medium;
    }
    
    return analysis;
  } catch (error) {
    return null;
  }
}

// 为组件添加性能监控
function addPerformanceMonitoring(filePath, analysis) {
  try {
    let content = fs.readFileSync(filePath, "utf8");
    const originalContent = content;
    
    // 如果已经有性能监控，跳过
if (analysis.hasMonitoring) {
      return false;
    }
    
    // 添加性能监控Hook导入
if (!content.includes(usePerformanceMonitor")) {
      // 查找现有的import语句
const importMatch = content.match(/import.*from\s+["]react["];?\s*\n/);
      if (importMatch) {
        const importStatement = "import { usePerformanceMonitor } from "../hooks/usePerformanceMonitor";\n";
        content = content.replace(importMatch[0], importMatch[0] + importStatement);
      } else {
        // 如果没有React import，在文件开头添加
const importStatement = "import React from react";\nimport { usePerformanceMonitor } from "../hooks/usePerformanceMonitor;\n\n";
        content = importStatement + content;
      }
    }
    
    // 在组件函数内添加性能监控Hook
const componentMatch = content.match(/((?:function|const)\s+\w+.*?(?:React\.FC|JSX\.Element|\(\s*\)\s*=>).*?\{)/s);
    if (componentMatch) {
      const componentStart = componentMatch[1];
      const monitoringCode =  `;
  // 性能监控
const performanceMonitor = usePerformanceMonitor("${analysis.fileName}", {
    trackRender: true,
    trackMemory: ${analysis.complexity === high"},
    warnThreshold: ${analysis.priority === "high ? 50 : 100}, // ms
  });
`;
      
      content = content.replace(componentStart, componentStart + monitoringCode);
    }
    
    // 在return语句前添加性能记录
const returnMatch = content.match(/(\s+)(return\s*\()/);
    if (returnMatch) {
      const indent = returnMatch[1];
      const performanceCode = `${indent}// 记录渲染性能
${indent}performanceMonitor.recordRender();
${indent}
${indent}`;
      
      content = content.replace(returnMatch[0], performanceCode + returnMatch[0]);
    }
    
    // 如果有useEffect，添加副作用监控
if (analysis.effectCount > 0) {
      content = content.replace(
        /useEffect\(\(\) => \{/g,
        `useEffect(() => {
    const effectStart = performance.now();`
      );
      
      content = content.replace(
        /\}, \[([^\]]*)\]\);/g,
        `    const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [$1]);`
      );
    }
    
    // 如果内容有变化，写回文件
if (content !== originalContent) {
      fs.writeFileSync(filePath, content);
      return true;
    }
    
    return false;
  } catch (error) {
    return false;
  }
}

// 创建性能监控配置文件
function createPerformanceConfig() {
  const configContent = `/**
 * 性能监控配置
 * 索克生活APP - 性能监控设置
 */

export interface PerformanceConfig {;
  // 全局性能监控开关
enabled: boolean;
  
  // 开发环境配置
development: {
    trackRender: boolean;
    trackMemory: boolean;
    trackNetwork: boolean;
    logToConsole: boolean;
    warnThreshold: number; // ms
errorThreshold: number; // ms
  }
  
  // 生产环境配置
production: {
    trackRender: boolean;
    trackMemory: boolean;
    trackNetwork: boolean;
    logToConsole: boolean;
    warnThreshold: number; // ms
errorThreshold: number; // ms
reportToAnalytics: boolean;
  };
  
  // 组件特定配置
components: {
    [componentName: string]: {
      enabled: boolean;
      warnThreshold?: number;
      trackMemory?: boolean;
      customMetrics?: string[];
    };
  };
}

export const performanceConfig: PerformanceConfig = {
  enabled: true,
  
  development: {
    trackRender: true,
    trackMemory: true,
    trackNetwork: true,
    logToConsole: true,
    warnThreshold: 50,
    errorThreshold: 100},
  
  production: {
    trackRender: true,
    trackMemory: false,
    trackNetwork: true,
    logToConsole: false,
    warnThreshold: 100,
    errorThreshold: 200,
    reportToAnalytics: true},
  
  components: {
    // 关键组件的特殊配置
    "HomeScreen": {
      enabled: true,
      warnThreshold: 30,
      trackMemory: true,
      customMetrics: [userInteraction", "dataLoad]},
    
    "ProfileScreen": {
      enabled: true,
      warnThreshold: 50,
      trackMemory: true},
    
    HealthDashboard": {
      enabled: true,
      warnThreshold: 40,
      trackMemory: true,
      customMetrics: ["chartRender, "dataUpdate"]},
    
    AgentChat": {
      enabled: true,
      warnThreshold: 30,
      trackMemory: true,
      customMetrics: ["messageRender, "scrollPerformance"]}}}

// 性能阈值配置
export const performanceThresholds = {
  render: {;
    good: 16, // 60fps
warning: 33, // 30fps
critical: 50, // 20fps
  },
  
  memory: {
    warning: 50 * 1024 * 1024, // 50MB
critical: 100 * 1024 * 1024, // 100MB
  },
  
  network: {
    good: 1000, // 1s
warning: 3000, // 3s
critical: 5000, // 5s
  }}

// 获取组件性能配置
export function getComponentConfig(componentName: string) {
  const isDev = __DEV__;
  const baseConfig = isDev ? performanceConfig.development : performanceConfig.production;
  const componentConfig = performanceConfig.components[componentName] || {};
  
  return {
    ...baseConfig,
    ...componentConfig,
    enabled: performanceConfig.enabled && (componentConfig.enabled !== false)};
}
`;

  const configPath = src/config/performance.ts";
  
  // 确保目录存在
const configDir = path.dirname(configPath);
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }
  
  fs.writeFileSync(configPath, configContent);
  return configPath;
}

// 创建性能报告生成器
function createPerformanceReporter() {
  const reporterContent = `/**
 * 性能报告生成器
 * 索克生活APP - 性能数据收集和报告
 */
;
import { performanceThresholds  } from "../config/performance;

export interface PerformanceMetric {
  componentName: string;
  metricType: ";render" | memory" | "network | "effect";
  value: number;
  timestamp: number;
  threshold?: number;
  severity: good" | "warning | "critical";
}

export interface PerformanceReport {
  sessionId: string;
  startTime: number;
  endTime: number;
  metrics: PerformanceMetric[];
  summary: {
    totalComponents: number;
    slowComponents: string[];
    memoryLeaks: string[];
    criticalIssues: number;
    averageRenderTime: number;
  };
}

class PerformanceReporter {
  private metrics: PerformanceMetric[] = [];
  private sessionId: string;
  private startTime: number;

  constructor() {
    this.sessionId = this.generateSessionId();
    this.startTime = Date.now();
  }

  private generateSessionId(): string {
    return \`session_\${Date.now()}_\${Math.random().toString(36).substr(2, 9)}\`;
  }

  // 记录性能指标
recordMetric(metric: Omit<PerformanceMetric, timestamp" | "severity>) {
    const severity = this.calculateSeverity(metric.metricType, metric.value);
    
    const fullMetric: PerformanceMetric = {
      ...metric,
      timestamp: Date.now(),
      severity};

    this.metrics.push(fullMetric);

    // 在开发环境中实时警告
if (__DEV__ && severity !== "good") {
      }
  }

  private calculateSeverity(type: string, value: number): good" | "warning | "critical" {
    const thresholds = performanceThresholds[type as keyof typeof performanceThresholds];
    
    if (!thresholds) return good";
    
    if (value >= thresholds.critical) return "critical;
    if (value >= thresholds.warning) return "warning";
    return good";
  }

  // 生成性能报告
generateReport(): PerformanceReport {
    const endTime = Date.now();
    const renderMetrics = this.metrics.filter(m => m.metricType === "render);
    
    const slowComponents = Array.from(new Set(
      this.metrics
        .filter(m => m.severity === "critical")
        .map(m => m.componentName);
    ));

    const memoryLeaks = Array.from(new Set(
      this.metrics
        .filter(m => m.metricType === memory" && m.severity !== "good)
        .map(m => m.componentName);
    ));

    const criticalIssues = this.metrics.filter(m => m.severity === "critical").length;
    
    const averageRenderTime = renderMetrics.length > 0
      ? renderMetrics.reduce((sum, m) => sum + m.value, 0) / renderMetrics.length;
      : 0;

    return {
      sessionId: this.sessionId,
      startTime: this.startTime,
      endTime,
      metrics: this.metrics,
      summary: {
        totalComponents: Array.from(new Set(this.metrics.map(m => m.componentName))).length,
        slowComponents,
        memoryLeaks,
        criticalIssues,
        averageRenderTime}};
  }

  // 导出报告到文件（开发环境）
  exportReport() {
    if (!__DEV__) return

    const report = this.generateReport();
    const reportJson = JSON.stringify(report, null, 2);
    
    // 在开发环境中保存到本地
// 可以扩展为保存到文件或发送到分析服务
return report;
  }

  // 清除旧指标
clearMetrics() {
    this.metrics = [];
    this.startTime = Date.now();
  }

  // 获取组件性能统计
getComponentStats(componentName: string) {
    const componentMetrics = this.metrics.filter(m => m.componentName === componentName);
    
    if (componentMetrics.length === 0) {
      return null;
    }

    const renderMetrics = componentMetrics.filter(m => m.metricType === "render);
    const memoryMetrics = componentMetrics.filter(m => m.metricType === "memory");

    return {
      totalRenders: renderMetrics.length,
      averageRenderTime: renderMetrics.reduce((sum, m) => sum + m.value, 0) / renderMetrics.length,
      maxRenderTime: Math.max(...renderMetrics.map(m => m.value)),
      memoryUsage: memoryMetrics.length > 0 ? memoryMetrics[memoryMetrics.length - 1].value : 0,
      criticalIssues: componentMetrics.filter(m => m.severity === critical").length};
  }
}

// 全局性能报告器实例
export const performanceReporter = new PerformanceReporter();

// 定期生成报告（开发环境）
if (__DEV__) {
  setInterval(() => {
    performanceReporter.exportReport()
  }, 60000); // 每分钟生成一次报告
}
`

  const reporterPath = "src/utils/performanceReporter.ts;
  fs.writeFileSync(reporterPath, reporterContent);
  return reporterPath;
}

// 主执行函数
async function main() {
  try {
    const componentFiles = getAllComponentFiles(src");
    const analyses = [];
    
    for (const file of componentFiles) {
      const analysis = analyzeComponent(file);
      if (analysis) {
        analyses.push(analysis);
      }
    }
    
    // 按优先级排序
analyses.sort((a, b) => {
      const priorityOrder = { high: 3, medium: 2, low: 1 };
      return priorityOrder[b.priority] - priorityOrder[a.priority];
    });
    
    // 统计信息
const stats = {
      total: analyses.length,
      needsMonitoring: analyses.filter(a => a.needsMonitoring).length,
      hasMonitoring: analyses.filter(a => a.hasMonitoring).length,
      highPriority: analyses.filter(a => a.priority === "high").length,;
      mediumPriority: analyses.filter(a => a.priority === medium").length};
    
    // 创建配置文件
const configPath = createPerformanceConfig();
    const reporterPath = createPerformanceReporter();
    // 为需要监控的组件添加性能监控
const componentsToMonitor = analyses.filter(a => a.needsMonitoring && !a.hasMonitoring);
    
    if (componentsToMonitor.length === 0) {
      return;
    }
    
    let integratedCount = 0;
    
    for (let i = 0; i < componentsToMonitor.length; i++) {
      const analysis = componentsToMonitor[i];
      const relativePath = path.relative(process.cwd(), analysis.filePath);
      
      process.stdout.write(`\r集成进度: ${i + 1}/${componentsToMonitor.length} - ${relativePath.slice(-60)}`);
      
      if (addPerformanceMonitoring(analysis.filePath, analysis)) {
        integratedCount++;
      }
    }
    
    / stats.total * 100).toFixed(1)}%`);
    
    // 显示高优先级组件的监控原因
const highPriorityComponents = analyses.filter(a => a.priority === "high" && a.needsMonitoring);
    highPriorityComponents.slice(0, 10).forEach(comp => {
      }`);
    });
    
    } catch (error) {
    process.exit(1);
  }
}

// 运行脚本
if (require.main === module) {
  main();
}

module.exports = {
  getAllComponentFiles,
  analyzeComponent,
  addPerformanceMonitoring,
  createPerformanceConfig,
  createPerformanceReporter}; 