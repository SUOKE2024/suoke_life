#!/usr/bin/env ts-node

/**
 * 索克生活测试修复脚本
 * 系统性修复测试失败问题
 */

import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

interface TestFixResult {
  success: boolean;
  message: string;
  details?: string[];
  fixedFiles?: string[];
}

class TestFailureFixer {
  private projectRoot: string;
  private fixedFiles: Set<string> = new Set();

  constructor(projectRoot: string = process.cwd()) {
    this.projectRoot = projectRoot;
  }

  /**
   * 修复所有测试失败问题
   */
  async fixAllTestFailures(): Promise<TestFixResult> {
    console.log('🔧 开始修复测试失败问题...\n');

    const fixes = [
      () => this.fixUtilsIndexExports(),
      () => this.fixReactNativeImports(),
      () => this.fixTypeImports(),
      () => this.fixMissingMocks(),
      () => this.updateJestConfig(),
    ];

    const results: TestFixResult[] = [];

    for (const fix of fixes) {
      try {
        const result = await fix();
        results.push(result);
        
        if (result.success) {
          console.log(`✅ ${result.message}`);
          if (result.fixedFiles) {
            result.fixedFiles.forEach(file => this.fixedFiles.add(file));
          }
        } else {
          console.log(`❌ ${result.message}`);
        }
      } catch (error) {
        console.log(`❌ 修复过程中出错: ${error instanceof Error ? error.message : String(error)}`);
      }
    }

    const successCount = results.filter(r => r.success).length;
    const totalFixes = results.length;

    return {
      success: successCount === totalFixes,
      message: `完成 ${successCount}/${totalFixes} 项修复`,
      details: results.map(r => r.message),
      fixedFiles: Array.from(this.fixedFiles)
    };
  }

  /**
   * 修复 utils/index.ts 的导出问题
   */
  private async fixUtilsIndexExports(): Promise<TestFixResult> {
    const filePath = path.join(this.projectRoot, 'src/utils/index.ts');
    
    if (!fs.existsSync(filePath)) {
      return { success: false, message: 'utils/index.ts 文件不存在' };
    }

    try {
      let content = fs.readFileSync(filePath, 'utf8');
      let fixedCount = 0;

      // 修复常见的导出问题
      const fixes = [
        // 修复 default 导出问题，改为命名导出
        {
          pattern: /export \{ default as (\w+) \} from '\.\/([^']+)';/g,
          replacement: (match: string, name: string, modulePath: string) => {
            const moduleFile = path.join(this.projectRoot, 'src/utils', modulePath + '.ts');
            if (fs.existsSync(moduleFile)) {
              const moduleContent = fs.readFileSync(moduleFile, 'utf8');
              // 检查是否有默认导出
              if (moduleContent.includes('export default')) {
                return match; // 保持原样
              } else {
                // 改为命名导出
                return `export * as ${name} from './${modulePath}';`;
              }
            }
            return `// export * as ${name} from './${modulePath}'; // TODO: 检查模块导出`;
          }
        }
      ];

      for (const fix of fixes) {
        const newContent = content.replace(fix.pattern, fix.replacement as any);
        if (newContent !== content) {
          content = newContent;
          fixedCount++;
        }
      }

      if (fixedCount > 0) {
        fs.writeFileSync(filePath, content);
        return {
          success: true,
          message: `修复了 utils/index.ts 中的 ${fixedCount} 个导出问题`,
          fixedFiles: [filePath]
        };
      }

      return { success: true, message: 'utils/index.ts 无需修复' };
    } catch (error) {
      return {
        success: false,
        message: `修复 utils/index.ts 失败: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  }

  /**
   * 修复 React Native 导入问题
   */
  private async fixReactNativeImports(): Promise<TestFixResult> {
    const testFiles = this.findTestFiles();
    let fixedCount = 0;

    for (const testFile of testFiles) {
      try {
        let content = fs.readFileSync(testFile, 'utf8');
        let modified = false;

        // 添加 React Native 模块的 mock
        if (content.includes('react-native-permissions') && !content.includes('jest.mock')) {
          const mockCode = `
// Mock react-native-permissions
jest.mock('react-native-permissions', () => ({
  PERMISSIONS: {
    ANDROID: {
      CAMERA: 'android.permission.CAMERA',
      RECORD_AUDIO: 'android.permission.RECORD_AUDIO',
    },
    IOS: {
      CAMERA: 'ios.permission.CAMERA',
      MICROPHONE: 'ios.permission.MICROPHONE',
    },
  },
  RESULTS: {
    GRANTED: 'granted',
    DENIED: 'denied',
    BLOCKED: 'blocked',
  },
  request: jest.fn(() => Promise.resolve('granted')),
  check: jest.fn(() => Promise.resolve('granted')),
}));

`;
          content = mockCode + content;
          modified = true;
        }

        // 添加其他 React Native 模块的 mock
        if (content.includes('react-native') && !content.includes('jest.mock(\'react-native\'')) {
          const rnMockCode = `
// Mock react-native
jest.mock('react-native', () => ({
  Platform: { OS: 'ios' },
  Alert: { alert: jest.fn() },
  AppState: { currentState: 'active' },
  Dimensions: { get: jest.fn(() => ({ width: 375, height: 812 })) },
}));

`;
          content = rnMockCode + content;
          modified = true;
        }

        if (modified) {
          fs.writeFileSync(testFile, content);
          fixedCount++;
          this.fixedFiles.add(testFile);
        }
      } catch (error) {
        console.log(`修复 ${testFile} 时出错: ${error}`);
      }
    }

    return {
      success: true,
      message: `修复了 ${fixedCount} 个测试文件的 React Native 导入问题`,
      fixedFiles: Array.from(this.fixedFiles)
    };
  }

  /**
   * 修复类型导入问题
   */
  private async fixTypeImports(): Promise<TestFixResult> {
    const sourceFiles = this.findSourceFiles();
    let fixedCount = 0;

    for (const sourceFile of sourceFiles) {
      try {
        let content = fs.readFileSync(sourceFile, 'utf8');
        let modified = false;

        // 修复相对路径导入
        const importRegex = /} from ['"]\.\.\/types\/([^'"]+)['"];/g;
        content = content.replace(importRegex, (match, typePath) => {
          const fullTypePath = path.resolve(path.dirname(sourceFile), `../types/${typePath}`);
          if (!fs.existsSync(fullTypePath + '.ts') && !fs.existsSync(fullTypePath + '.tsx')) {
            // 尝试其他可能的路径
            const alternativePaths = [
              `../types/index`,
              `../../types/${typePath}`,
              `../../../types/${typePath}`
            ];
            
            for (const altPath of alternativePaths) {
              const altFullPath = path.resolve(path.dirname(sourceFile), altPath);
              if (fs.existsSync(altFullPath + '.ts') || fs.existsSync(altFullPath + '.tsx')) {
                modified = true;
                return match.replace(`../types/${typePath}`, altPath);
              }
            }
          }
          return match;
        });

        if (modified) {
          fs.writeFileSync(sourceFile, content);
          fixedCount++;
          this.fixedFiles.add(sourceFile);
        }
      } catch (error) {
        console.log(`修复 ${sourceFile} 时出错: ${error}`);
      }
    }

    return {
      success: true,
      message: `修复了 ${fixedCount} 个文件的类型导入问题`,
      fixedFiles: Array.from(this.fixedFiles)
    };
  }

  /**
   * 添加缺失的 mock
   */
  private async fixMissingMocks(): Promise<TestFixResult> {
    const mockDir = path.join(this.projectRoot, 'src/__mocks__');
    
    if (!fs.existsSync(mockDir)) {
      fs.mkdirSync(mockDir, { recursive: true });
    }

    const mocks = [
      {
        file: 'react-native-permissions.ts',
        content: `
export const PERMISSIONS = {
  ANDROID: {
    CAMERA: 'android.permission.CAMERA',
    RECORD_AUDIO: 'android.permission.RECORD_AUDIO',
  },
  IOS: {
    CAMERA: 'ios.permission.CAMERA',
    MICROPHONE: 'ios.permission.MICROPHONE',
  },
};

export const RESULTS = {
  GRANTED: 'granted',
  DENIED: 'denied',
  BLOCKED: 'blocked',
};

export const request = jest.fn(() => Promise.resolve('granted'));
export const check = jest.fn(() => Promise.resolve('granted'));
`
      },
      {
        file: 'react-native.ts',
        content: `
export const Platform = { OS: 'ios' };
export const Alert = { alert: jest.fn() };
export const AppState = { currentState: 'active' };
export const Dimensions = { get: jest.fn(() => ({ width: 375, height: 812 })) };
`
      }
    ];

    let createdCount = 0;
    for (const mock of mocks) {
      const mockPath = path.join(mockDir, mock.file);
      if (!fs.existsSync(mockPath)) {
        fs.writeFileSync(mockPath, mock.content);
        createdCount++;
        this.fixedFiles.add(mockPath);
      }
    }

    return {
      success: true,
      message: `创建了 ${createdCount} 个 mock 文件`,
      fixedFiles: Array.from(this.fixedFiles)
    };
  }

  /**
   * 更新 Jest 配置
   */
  private async updateJestConfig(): Promise<TestFixResult> {
    const jestConfigPath = path.join(this.projectRoot, 'jest.config.js');
    
    if (!fs.existsSync(jestConfigPath)) {
      return { success: false, message: 'Jest 配置文件不存在' };
    }

    try {
      let content = fs.readFileSync(jestConfigPath, 'utf8');
      
      // 添加必要的配置
      if (!content.includes('transformIgnorePatterns')) {
        const transformIgnoreConfig = `
  transformIgnorePatterns: [
    'node_modules/(?!(react-native|@react-native|react-native-permissions)/)'
  ],`;
        
        content = content.replace(
          /module\.exports = \{/,
          `module.exports = {${transformIgnoreConfig}`
        );
      }

      if (!content.includes('setupFilesAfterEnv')) {
        const setupConfig = `
  setupFilesAfterEnv: ['<rootDir>/src/__tests__/setup.ts'],`;
        
        content = content.replace(
          /module\.exports = \{/,
          `module.exports = {${setupConfig}`
        );
      }

      fs.writeFileSync(jestConfigPath, content);
      this.fixedFiles.add(jestConfigPath);

      return {
        success: true,
        message: '更新了 Jest 配置',
        fixedFiles: [jestConfigPath]
      };
    } catch (error) {
      return {
        success: false,
        message: `更新 Jest 配置失败: ${error instanceof Error ? error.message : String(error)}`
      };
    }
  }

  /**
   * 查找测试文件
   */
  private findTestFiles(): string[] {
    const testFiles: string[] = [];
    const testDirs = [
      path.join(this.projectRoot, 'src/__tests__'),
      path.join(this.projectRoot, 'src/agents'),
    ];

    const scanDir = (dir: string) => {
      if (!fs.existsSync(dir)) return;
      
      const items = fs.readdirSync(dir);
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          scanDir(fullPath);
        } else if (item.endsWith('.test.ts') || item.endsWith('.test.tsx')) {
          testFiles.push(fullPath);
        }
      }
    };

    testDirs.forEach(scanDir);
    return testFiles;
  }

  /**
   * 查找源文件
   */
  private findSourceFiles(): string[] {
    const sourceFiles: string[] = [];
    const srcDir = path.join(this.projectRoot, 'src');

    const scanDir = (dir: string) => {
      if (!fs.existsSync(dir)) return;
      
      const items = fs.readdirSync(dir);
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory() && !item.startsWith('.') && item !== '__tests__') {
          scanDir(fullPath);
        } else if ((item.endsWith('.ts') || item.endsWith('.tsx')) && !item.endsWith('.test.ts') && !item.endsWith('.test.tsx')) {
          sourceFiles.push(fullPath);
        }
      }
    };

    scanDir(srcDir);
    return sourceFiles;
  }
}

// 主函数
async function main(): Promise<void> {
  try {
    const fixer = new TestFailureFixer();
    const result = await fixer.fixAllTestFailures();
    
    console.log('\n📊 修复结果:');
    console.log(`状态: ${result.success ? '✅ 成功' : '❌ 部分失败'}`);
    console.log(`消息: ${result.message}`);
    
    if (result.fixedFiles && result.fixedFiles.length > 0) {
      console.log(`\n修复的文件 (${result.fixedFiles.length}个):`);
      result.fixedFiles.forEach(file => {
        console.log(`  - ${path.relative(process.cwd(), file)}`);
      });
    }

    if (result.details) {
      console.log('\n详细信息:');
      result.details.forEach(detail => console.log(`  - ${detail}`));
    }

    process.exit(result.success ? 0 : 1);
  } catch (error) {
    console.error('❌ 修复过程中发生错误:', error);
    process.exit(1);
  }
}

// 如果直接运行此脚本
if (require.main === module) {
  main();
}

export { TestFailureFixer }; 