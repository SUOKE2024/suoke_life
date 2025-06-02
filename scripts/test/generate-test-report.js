#!/usr/bin/env node

/**
 * 索克生活测试报告生成器
 * 生成详细的测试报告，包括覆盖率、性能指标和测试结果
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// 颜色定义
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
};

// 打印带颜色的消息
function printMessage(color, message) {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

// 获取当前时间戳
function getCurrentTimestamp() {
  return new Date().toISOString();
}

// 读取 package.json 获取项目信息
function getProjectInfo() {
  const packagePath = path.join(process.cwd(), 'package.json');
  const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));

  return {
    name: packageJson.name,
    version: packageJson.version,
    description: packageJson.description,
  };
}

// 运行命令并获取输出
function runCommand(command, options = {}) {
  try {
    const output = execSync(command, {
      encoding: 'utf8',
      stdio: options.silent ? 'pipe' : 'inherit',
      ...options,
    });
    return { success: true, output };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      output: error.stdout || '',
    };
  }
}

// 解析 Jest 覆盖率报告
function parseCoverageReport() {
  const coveragePath = path.join(process.cwd(), 'coverage/coverage-summary.json');

  if (!fs.existsSync(coveragePath)) {
    return null;
  }

  try {
    const coverage = JSON.parse(fs.readFileSync(coveragePath, 'utf8'));
    return coverage.total;
  } catch (error) {
    printMessage('yellow', `⚠️  无法解析覆盖率报告: ${error.message}`);
    return null;
  }
}

// 解析 Jest 测试结果
function parseTestResults() {
  const resultsPath = path.join(process.cwd(), 'test-results.json');

  if (!fs.existsSync(resultsPath)) {
    return null;
  }

  try {
    const results = JSON.parse(fs.readFileSync(resultsPath, 'utf8'));
    return results;
  } catch (error) {
    printMessage('yellow', `⚠️  无法解析测试结果: ${error.message}`);
    return null;
  }
}

// 生成 HTML 报告
function generateHtmlReport(reportData) {
  const htmlTemplate = `
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>索克生活测试报告</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .content {
            padding: 30px;
        }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }
        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            text-align: center;
            border-left: 4px solid #667eea;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
        }
        .metric-label {
            color: #666;
            margin-top: 5px;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            text-transform: uppercase;
        }
        .status-pass {
            background: #d4edda;
            color: #155724;
        }
        .status-fail {
            background: #f8d7da;
            color: #721c24;
        }
        .status-warning {
            background: #fff3cd;
            color: #856404;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #28a745, #20c997);
            transition: width 0.3s ease;
        }
        .test-details {
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            margin: 20px 0;
        }
        .test-file {
            margin: 10px 0;
            padding: 10px;
            background: white;
            border-radius: 4px;
            border-left: 3px solid #667eea;
        }
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
            border-top: 1px solid #dee2e6;
        }
        @media (max-width: 768px) {
            .metrics {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 索克生活测试报告</h1>
            <p>生成时间: ${reportData.timestamp}</p>
            <p>项目版本: ${reportData.project.version}</p>
        </div>

        <div class="content">
            <div class="section">
                <h2>📊 测试概览</h2>
                <div class="metrics">
                    <div class="metric-card">
                        <div class="metric-value">${reportData.summary.totalTests}</div>
                        <div class="metric-label">总测试数</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" style="color: #28a745">${reportData.summary.passedTests}</div>
                        <div class="metric-label">通过测试</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" style="color: #dc3545">${reportData.summary.failedTests}</div>
                        <div class="metric-label">失败测试</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${reportData.summary.testSuites}</div>
                        <div class="metric-label">测试套件</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>📈 覆盖率报告</h2>
                ${reportData.coverage ? `
                <div class="metrics">
                    <div class="metric-card">
                        <div class="metric-value">${reportData.coverage.statements.pct}%</div>
                        <div class="metric-label">语句覆盖率</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${reportData.coverage.statements.pct}%"></div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${reportData.coverage.branches.pct}%</div>
                        <div class="metric-label">分支覆盖率</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${reportData.coverage.branches.pct}%"></div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${reportData.coverage.functions.pct}%</div>
                        <div class="metric-label">函数覆盖率</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${reportData.coverage.functions.pct}%"></div>
                        </div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${reportData.coverage.lines.pct}%</div>
                        <div class="metric-label">行覆盖率</div>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${reportData.coverage.lines.pct}%"></div>
                        </div>
                    </div>
                </div>
                ` : '<p>覆盖率数据不可用</p>'}
            </div>

            <div class="section">
                <h2>⚡ 性能指标</h2>
                <div class="metrics">
                    <div class="metric-card">
                        <div class="metric-value">${reportData.performance.totalTime}s</div>
                        <div class="metric-label">总执行时间</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${reportData.performance.avgTestTime}ms</div>
                        <div class="metric-label">平均测试时间</div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>🎯 测试状态</h2>
                <div class="test-details">
                    <p><span class="status-badge ${reportData.summary.failedTests === 0 ? 'status-pass' : 'status-fail'}">
                        ${reportData.summary.failedTests === 0 ? '全部通过' : '存在失败'}
                    </span></p>
                    <p>测试成功率: ${((reportData.summary.passedTests / reportData.summary.totalTests) * 100).toFixed(1)}%</p>
                </div>
            </div>

            <div class="section">
                <h2>📝 详细信息</h2>
                <div class="test-details">
                    <h3>项目信息</h3>
                    <p><strong>名称:</strong> ${reportData.project.name}</p>
                    <p><strong>描述:</strong> ${reportData.project.description}</p>
                    <p><strong>版本:</strong> ${reportData.project.version}</p>

                    <h3>测试环境</h3>
                    <p><strong>Node.js:</strong> ${process.version}</p>
                    <p><strong>平台:</strong> ${process.platform}</p>
                    <p><strong>架构:</strong> ${process.arch}</p>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>© 2024 索克生活 - 自动化测试报告</p>
            <p>报告生成于 ${new Date().toLocaleString('zh-CN')}</p>
        </div>
    </div>
</body>
</html>
  `;

  return htmlTemplate;
}

// 主函数
async function generateTestReport() {
  printMessage('cyan', '🧪 开始生成索克生活测试报告...\n');

  const projectInfo = getProjectInfo();
  const timestamp = getCurrentTimestamp();

  // 运行测试并生成覆盖率报告
  printMessage('blue', '📋 运行测试套件...');
  const testResult = runCommand('npm run test:ci', { silent: true });

  if (!testResult.success) {
    printMessage('red', '❌ 测试运行失败');
    console.log(testResult.error);
    process.exit(1);
  }

  // 解析测试结果
  const coverage = parseCoverageReport();
  const testResults = parseTestResults();

  // 构建报告数据
  const reportData = {
    timestamp,
    project: projectInfo,
    summary: {
      totalTests: testResults?.numTotalTests || 0,
      passedTests: testResults?.numPassedTests || 0,
      failedTests: testResults?.numFailedTests || 0,
      testSuites: testResults?.numTotalTestSuites || 0,
    },
    coverage: coverage || null,
    performance: {
      totalTime: testResults ? (testResults.testResults.reduce((acc, suite) => acc + suite.perfStats.runtime, 0) / 1000).toFixed(2) : '0',
      avgTestTime: testResults ? Math.round(testResults.testResults.reduce((acc, suite) => acc + suite.perfStats.runtime, 0) / testResults.numTotalTests) : 0,
    },
  };

  // 生成 JSON 报告
  const jsonReportPath = path.join(process.cwd(), 'test-report.json');
  fs.writeFileSync(jsonReportPath, JSON.stringify(reportData, null, 2));
  printMessage('green', `✅ JSON 报告已生成: ${jsonReportPath}`);

  // 生成 HTML 报告
  const htmlReport = generateHtmlReport(reportData);
  const htmlReportPath = path.join(process.cwd(), 'test-report.html');
  fs.writeFileSync(htmlReportPath, htmlReport);
  printMessage('green', `✅ HTML 报告已生成: ${htmlReportPath}`);

  // 打印摘要
  printMessage('cyan', '\n📊 测试报告摘要:');
  console.log(`   总测试数: ${reportData.summary.totalTests}`);
  console.log(`   通过测试: ${reportData.summary.passedTests}`);
  console.log(`   失败测试: ${reportData.summary.failedTests}`);
  console.log(`   测试套件: ${reportData.summary.testSuites}`);

  if (coverage) {
    console.log(`   语句覆盖率: ${coverage.statements.pct}%`);
    console.log(`   分支覆盖率: ${coverage.branches.pct}%`);
    console.log(`   函数覆盖率: ${coverage.functions.pct}%`);
    console.log(`   行覆盖率: ${coverage.lines.pct}%`);
  }

  console.log(`   总执行时间: ${reportData.performance.totalTime}s`);
  console.log(`   平均测试时间: ${reportData.performance.avgTestTime}ms`);

  // 检查测试是否全部通过
  if (reportData.summary.failedTests > 0) {
    printMessage('red', '\n❌ 存在失败的测试，请检查测试结果');
    process.exit(1);
  } else {
    printMessage('green', '\n🎉 所有测试都通过了！');
  }

  printMessage('cyan', `\n📄 查看详细报告: file://${htmlReportPath}`);
}

// 运行报告生成器
if (require.main === module) {
  generateTestReport().catch((error) => {
    printMessage('red', `❌ 生成测试报告时出错: ${error.message}`);
    process.exit(1);
  });
}

module.exports = { generateTestReport };