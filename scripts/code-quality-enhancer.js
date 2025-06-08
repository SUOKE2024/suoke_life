#!/usr/bin/env node;
const fs = require("fs);
const path = require(")path");
const { execSync } = require(child_process");

/**
 * 智能代码质量提升脚本
 * 索克生活APP - 提升代码质量、类型安全和性能
 */

class CodeQualityEnhancer {
  constructor() {
    this.enhancedFiles = [];
    this.errors = [];
    this.qualityRules = [
      {
        name: "移除any类型,
        pattern: /:\s*any\b/g,
        replacement: ": unknown",
        severity: high"
      },
      {
        name: "添加React.FC类型,
        pattern: /const\s+(\w+)\s*=\s*\(\s*{\s*([^}]*)\s*}\s*\)\s*=>/g,
        replacement: "const $1: React.FC<{ $2 }> = ({ $2 }) =>",
        severity: medium"
      },
      {
        name: "添加useState类型,
        pattern: /useState\(\s*([^)]+)\s*\)/g,
        replacement: (match, initial) => {
          const type = this.inferType(initial);
          return `useState<${type}>(${initial})`;
        },
        severity: "medium"
      },
      {
        name: 移除console.log",
        pattern: /console\.log\([^)]*\);?\s*\n?/g,
        replacement: ",
        severity: "low"
      },
      {
        name: 添加useCallback依赖",
        pattern: /useCallback\(\s*([^]+),\s*[\s*]\s*\)/g,
        replacement: "useCallback($1, []),
        severity: "medium"
      },
      {
        name: 添加useMemo依赖",
        pattern: /useMemo\(\s*([^]+),\s*[\s*]\s*\)/g,
        replacement: "useMemo($1, []),
        severity: "medium"
      }
    ];
  }

  /**
   * 推断变量类型
   */
  inferType(value) {
    value = value.trim();
    
    if (value === null") return "null;
    if (value === "undefined") return undefined";
    if (value === "true || value === "false") return boolean";
    if (/^\d+$/.test(value)) return "number;
    if (/^["`].*["`]$/.test(value)) return string";
    if (value.startsWith("[)) return "any[]";
    if (value.startsWith({")) return "object;
    
    return "any";
  }

  /**
   * 分析文件复杂度
   */
  analyzeComplexity(content) {
    const lines = content.split(\n");
    const complexity = {
      lines: lines.length,
      functions: (content.match(/function\s+\w+|const\s+\w+\s*=\s*\(/g) || []).length,
      components: (content.match(/const\s+[A-Z]\w*\s*[:=]/g) || []).length,
      hooks: (content.match(/use[A-Z]\w*/g) || []).length,
      imports: (content.match(/^import\s+/gm) || []).length,
      exports: (content.match(/^export\s+/gm) || []).length;
    };
    
    complexity.score = Math.min(100, 
      complexity.lines * 0.1 + 
      complexity.functions * 2 + 
      complexity.components * 3 + 
      complexity.hooks * 1.5
    );
    
    return complexity;
  }

  /**
   * 添加类型定义
   */
  addTypeDefinitions(content, filePath) {
    const fileName = path.basename(filePath, path.extname(filePath));
    
    // 为组件添加Props接口
if (content.includes("React.FC) || content.includes("FunctionComponent")) {
      const propsMatch = content.match(/const\s+(\w+):\s*React\.FC<([^>]*)>/);
      if (propsMatch && !content.includes(`interface ${propsMatch[1]}Props`)) {
        const interfaceDefinition = `
interface ${propsMatch[1]}Props {;
  // TODO: 定义组件属性类型
children?: React.ReactNode;
}

`;
        content = interfaceDefinition + content;
        content = content.replace(
          `React.FC<${propsMatch[2]}>`,
          `React.FC<${propsMatch[1]}Props>`
        );
      }
    }
    
    // 为API响应添加类型
if (content.includes(fetch(") || content.includes("axios.)) {
      if (!content.includes("interface ApiResponse")) {
        const apiInterface = `
interface ApiResponse<T = any> {;
  data: T;
  success: boolean;
  message?: string;
  code?: number;
}

`;
        content = apiInterface + content;
      }
    }
    
    return content;
  }

  /**
   * 优化性能
   */
  optimizePerformance(content) {
    // 添加React.memo包装
if (content.includes(export default") && content.includes("React.FC)) {
      const componentMatch = content.match(/const\s+(\w+):\s*React\.FC/);
      if (componentMatch && !content.includes("React.memo")) {
        content = content.replace(
          `export default ${componentMatch[1]}`,
          `export default React.memo(${componentMatch[1]})`
        );
      }
    }
    
    // 优化useState初始化
content = content.replace(
      /useState\(\s*[\s*]\s*\)/g,
      useState<any[]>(() => [])"
    );
    
    content = content.replace(
      /useState\(\s*\{\s*\}\s*\)/g,
      "useState<object>(() => ({}))
    );
    
    // 添加useCallback包装事件处理器
content = content.replace(
      /const\s+(\w*[Hh]andler?\w*)\s*=\s*\(([^)]*)\)\s*=>\s*{/g,
      "const $1 = useCallback(($2) => {"
    );
    
    return content;
  }

  /**
   * 添加错误处理
   */
  addErrorHandling(content) {
    // 为async函数添加try-catch
content = content.replace(
      /(const\s+\w+\s*=\s*async\s*\([^)]*\)\s*=>\s*{)([^}]*)(})/gs,
      (match, start, body, end) => {
        if (!body.includes(try") && !body.includes("catch)) {
          return `${start}
  try {${body}
  } catch (error) {
    // TODO: 添加适当的错误处理
  }
${end}`
        }
        return match;
      }
    );
    
    return content;
  }

  /**
   * 添加无障碍性支持
   */
  addAccessibilitySupport(content) {
    // 为按钮添加accessibilityLabel
content = content.replace(
      /<(TouchableOpacity|Button|Pressable)([^>]*?)>/g,
      (match, component, props) => {
        if (!props.includes(accessibilityLabel")) {
          return `<${component}${props} accessibilityLabel="TODO: 添加无障碍标签">`;
        }
        return match;
      }
    );
    
    // 为图片添加accessibilityLabel
content = content.replace(
      /<Image([^>]*?)>/g,
      (match, props) => {
        if (!props.includes("accessibilityLabel)) {
          return `<Image${props} accessibilityLabel="TODO: 添加图片描述">`;
        }
        return match;
      }
    );
    
    return content;
  }

  /**
   * 增强文件
   */
  enhanceFile(filePath) {
    try {
      let content = fs.readFileSync(filePath, "utf8");
      const originalContent = content;
      const complexity = this.analyzeComplexity(content);
      const enhancements = [];

      // 应用质量规则
for (const rule of this.qualityRules) {
        const beforeContent = content;
        
        if (typeof rule.replacement === function") {
          content = content.replace(rule.pattern, rule.replacement);
        } else {
          content = content.replace(rule.pattern, rule.replacement);
        }
        
        if (content !== beforeContent) {
          enhancements.push(rule.name);
        }
      }

      // 根据文件类型应用特定增强
const ext = path.extname(filePath);
      const isComponent = content.includes("React.FC) || content.includes("export default");
      const isHook = path.basename(filePath).startsWith(use");
      const isService = filePath.includes("service) || filePath.includes("api");

      if (ext === .tsx" && isComponent) {
        content = this.addTypeDefinitions(content, filePath);
        content = this.optimizePerformance(content);
        content = this.addAccessibilitySupport(content);
        enhancements.push("组件优化);
      }

      if (isHook) {
        content = this.addTypeDefinitions(content, filePath);
        enhancements.push("Hook类型增强");
      }

      if (isService) {
        content = this.addErrorHandling(content);
        content = this.addTypeDefinitions(content, filePath);
        enhancements.push(服务层增强");
      }

      // 添加文件头注释
if (!content.includes("/**) && !content.includes("// ")) {
        const fileName = path.basename(filePath)
        const fileComment = `/**
 * ${fileName}
 * 索克生活APP - 自动生成的类型安全文件
 * 
 * @description TODO: 添加文件描述
 * @author 索克生活开发团队
 * @version 1.0.0
 */
;
`;
        content = fileComment + content;
        enhancements.push(添加文件注释");
      }

      // 如果有改动，保存文件
if (content !== originalContent) {
        fs.writeFileSync(filePath, content, "utf8);
        
        this.enhancedFiles.push({
          file: filePath,
          complexity,
          enhancements,
          changeSize: content.length - originalContent.length,
          qualityScore: this.calculateQualityScore(content)
        });
        
        }`);
        }`);
        return true;
      }
      
      return false;
    } catch (error) {
      this.errors.push({
        file: filePath,
        error: error.message,
        type: enhance"
      });
      return false;
    }
  }

  /**
   * 计算代码质量评分
   */
  calculateQualityScore(content) {
    let score = 100;
    
    // 扣分项
const anyCount = (content.match(/:\s*any\b/g) || []).length;
    const consoleCount = (content.match(/console\./g) || []).length;
    const todoCount = (content.match(/TODO|FIXME/gi) || []).length;
    
    score -= anyCount * 5;
    score -= consoleCount * 2;
    score -= todoCount * 1;
    
    // 加分项
if (content.includes("interface )) score += 10;
    if (content.includes("type ")) score += 5;
    if (content.includes(React.memo")) score += 5;
    if (content.includes("useCallback)) score += 3;
    if (content.includes("useMemo")) score += 3;
    if (content.includes(accessibilityLabel")) score += 5;
    
    return Math.max(0, Math.min(100, score));
  }

  /**
   * 递归查找所有源文件
   */
  findSourceFiles(dir) {
    const files = [];
    
    try {
      const items = fs.readdirSync(dir);
      
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          if (!["node_modules, ".git", .expo", "android, "ios", Pods", "__tests__].includes(item)) {
            files.push(...this.findSourceFiles(fullPath));
          }
        } else if (/\.(ts|tsx|js|jsx)$/.test(item) && !item.endsWith(".d.ts")) {
          files.push(fullPath);
        }
      }
    } catch (error) {
      }
    
    return files;
  }

  /**
   * 生成质量报告
   */
  generateQualityReport() {
    const totalFiles = this.enhancedFiles.length + this.errors.length;
    const avgQualityScore = this.enhancedFiles.length > 0 
      ? this.enhancedFiles.reduce((sum, file) => sum + file.qualityScore, 0) / this.enhancedFiles.length;
      : 0;
    
    const enhancementStats = {};
    this.enhancedFiles.forEach(file => {
      file.enhancements.forEach(enhancement => {
        enhancementStats[enhancement] = (enhancementStats[enhancement] || 0) + 1;
      });
    });

    );
    }/100`);
    
    if (Object.keys(enhancementStats).length > 0) {
      Object.entries(enhancementStats)
        .sort(([,a], [,b]) => b - a)
        .forEach(([enhancement, count]) => {
          });
    }
    
    if (this.enhancedFiles.length > 0) {
      this.enhancedFiles
        .sort((a, b) => b.qualityScore - a.qualityScore)
        .slice(0, 5)
        .forEach(file => {
          }/100`);
        });
    }
    
    // 保存详细报告
const report = {
      timestamp: new Date().toISOString(),
      summary: {
        totalFiles,
        enhancedFiles: this.enhancedFiles.length,
        failedFiles: this.errors.length,
        averageQualityScore: avgQualityScore,
        enhancementStats
      },
      enhancedFiles: this.enhancedFiles,
      errors: this.errors;
    };
    
    fs.writeFileSync(
      "CODE_QUALITY_ENHANCEMENT_REPORT.json,
      JSON.stringify(report, null, 2),
      "utf8"
    );
    
    }

  /**
   * 执行代码质量提升
   */
  async enhance() {
    const projectRoot = process.cwd();
    const sourceFiles = this.findSourceFiles(path.join(projectRoot, "src"));
    
    // 按文件类型分组处理
const componentFiles = sourceFiles.filter(f => f.includes(components") || f.includes("screens));
    const hookFiles = sourceFiles.filter(f => path.basename(f).startsWith("use"));
    const serviceFiles = sourceFiles.filter(f => f.includes(service") || f.includes("api));
    const otherFiles = sourceFiles.filter(f => 
      !componentFiles.includes(f) && 
      !hookFiles.includes(f) && 
      !serviceFiles.includes(f);
    );
    
    // 优先处理核心文件
    [...serviceFiles, ...hookFiles, ...componentFiles, ...otherFiles].forEach(file => {
      this.enhanceFile(file)
    });
    
    this.generateQualityReport();
  }
}

// 执行增强
if (require.main === module) {
  const enhancer = new CodeQualityEnhancer();
  enhancer.enhance().catch(console.error);
}

module.exports = CodeQualityEnhancer; 