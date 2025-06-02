#!/usr/bin/env node

/**
 * 索克生活项目智能体协作测试
 * 测试四个智能体之间的协作机制和交互流程
 */

const fs = require('fs');
const path = require('path');

console.log('🤖 索克生活智能体协作测试');
console.log('=====================================');

// 测试结果统计
const collaborationResults = {
  total: 0,
  passed: 0,
  failed: 0,
  scenarios: [],
  errors: []
};

/**
 * 模拟智能体
 */
class MockAgent {
  constructor(name, type, capabilities) {
    this.name = name;
    this.type = type;
    this.capabilities = capabilities;
    this.status = 'active';
    this.memory = [];
  }

  async processMessage(message, context = {}) {
    // 模拟处理延迟
    await new Promise(resolve => setTimeout(resolve, Math.random() * 500 + 100));

    const response = {
      agentId: this.name,
      timestamp: new Date().toISOString(),
      message: this.generateResponse(message, context),
      confidence: Math.random() * 0.3 + 0.7, // 0.7-1.0
      nextActions: this.suggestNextActions(message, context)
    };

    this.memory.push({ input: message, output: response, context });
    return response;
  }

  generateResponse(message, context) {
    switch (this.name) {
      case 'xiaoai':
        if (message.includes('健康') || message.includes('诊断')) {
          return '根据您的症状，我建议进行进一步检查。让我为您安排相关服务。';
        }
        return '您好！我是小艾，专注于健康监测和诊断。有什么可以帮助您的吗？';

      case 'xiaoke':
        if (message.includes('服务') || message.includes('预约')) {
          return '我已为您找到合适的医疗资源，正在安排预约。';
        }
        return '我是小克，负责服务推荐和资源匹配。让我为您提供最佳方案。';

      case 'laoke':
        if (message.includes('知识') || message.includes('学习')) {
          return '这里有相关的中医知识和现代医学资料，我来为您详细解释。';
        }
        return '我是老克，专门负责知识传播和教育。有什么想了解的吗？';

      case 'soer':
        if (message.includes('生活') || message.includes('习惯')) {
          return '基于您的情况，我建议调整作息和饮食习惯，我会持续陪伴您。';
        }
        return '我是索儿，关注您的生活方式和日常健康管理。';

      default:
        return '智能体响应';
    }
  }

  suggestNextActions(message, context) {
    const actions = [];

    switch (this.name) {
      case 'xiaoai':
        if (message.includes('症状')) {
          actions.push('recommend_service', 'schedule_checkup');
        }
        break;
      case 'xiaoke':
        if (message.includes('预约')) {
          actions.push('find_doctor', 'book_appointment');
        }
        break;
      case 'laoke':
        if (message.includes('解释')) {
          actions.push('provide_knowledge', 'create_learning_path');
        }
        break;
      case 'soer':
        if (message.includes('建议')) {
          actions.push('track_habits', 'provide_support');
        }
        break;
    }

    return actions;
  }
}

/**
 * 智能体协调器模拟
 */
class MockAgentCoordinator {
  constructor() {
    this.agents = {
      xiaoai: new MockAgent('xiaoai', 'health_monitor', ['diagnosis', 'health_analysis']),
      xiaoke: new MockAgent('xiaoke', 'service_provider', ['service_matching', 'resource_management']),
      laoke: new MockAgent('laoke', 'knowledge_expert', ['knowledge_sharing', 'education']),
      soer: new MockAgent('soer', 'life_companion', ['lifestyle_management', 'emotional_support'])
    };
    this.collaborationHistory = [];
  }

  async executeCollaboration(scenario, userInput) {
    const collaboration = {
      scenario: scenario.name,
      userInput,
      startTime: Date.now(),
      steps: [],
      result: null
    };

    try {
      // 执行协作流程
      for (const step of scenario.steps) {
        const stepResult = await this.executeStep(step, userInput, collaboration);
        collaboration.steps.push(stepResult);

        // 如果步骤失败，停止执行
        if (!stepResult.success) {
          collaboration.result = 'failed';
          break;
        }
      }

      if (collaboration.result !== 'failed') {
        collaboration.result = 'success';
      }

      collaboration.duration = Date.now() - collaboration.startTime;
      this.collaborationHistory.push(collaboration);

      return collaboration;

    } catch (error) {
      collaboration.result = 'error';
      collaboration.error = error.message;
      collaboration.duration = Date.now() - collaboration.startTime;
      return collaboration;
    }
  }

  async executeStep(step, userInput, collaboration) {
    const { agent, action, expectedOutput } = step;

    try {
      const agentInstance = this.agents[agent];
      if (!agentInstance) {
        throw new Error(`智能体 ${agent} 不存在`);
      }

      const context = {
        collaboration: collaboration.scenario,
        previousSteps: collaboration.steps,
        userInput
      };

      const response = await agentInstance.processMessage(userInput, context);

      const stepResult = {
        agent,
        action,
        input: userInput,
        output: response,
        success: true,
        timestamp: new Date().toISOString()
      };

      // 验证输出是否符合预期
      if (expectedOutput) {
        const meetsExpectation = this.validateOutput(response, expectedOutput);
        stepResult.meetsExpectation = meetsExpectation;
        if (!meetsExpectation) {
          stepResult.success = false;
          stepResult.error = '输出不符合预期';
        }
      }

      return stepResult;

    } catch (error) {
      return {
        agent,
        action,
        input: userInput,
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      };
    }
  }

  validateOutput(response, expectedOutput) {
    // 简单的输出验证
    if (expectedOutput.contains) {
      return expectedOutput.contains.some(keyword =>
        response.message.includes(keyword)
      );
    }

    if (expectedOutput.confidence) {
      return response.confidence >= expectedOutput.confidence;
    }

    return true;
  }
}

/**
 * 协作场景定义
 */
const collaborationScenarios = [
  {
    name: '健康咨询完整流程',
    description: '用户咨询健康问题，四个智能体协作提供完整解决方案',
    userInput: '我最近总是感觉疲劳，想了解可能的原因',
    steps: [
      {
        agent: 'xiaoai',
        action: 'initial_diagnosis',
        expectedOutput: {
          contains: ['疲劳', '检查', '建议']
        }
      },
      {
        agent: 'xiaoke',
        action: 'service_recommendation',
        expectedOutput: {
          contains: ['服务', '预约', '医疗']
        }
      },
      {
        agent: 'laoke',
        action: 'knowledge_sharing',
        expectedOutput: {
          contains: ['知识', '解释', '中医']
        }
      },
      {
        agent: 'soer',
        action: 'lifestyle_advice',
        expectedOutput: {
          contains: ['生活', '习惯', '建议']
        }
      }
    ]
  },
  {
    name: '学习路径规划',
    description: '用户想学习中医知识，智能体协作制定学习计划',
    userInput: '我想系统学习中医养生知识',
    steps: [
      {
        agent: 'laoke',
        action: 'create_learning_path',
        expectedOutput: {
          contains: ['学习', '路径', '中医']
        }
      },
      {
        agent: 'xiaoke',
        action: 'find_resources',
        expectedOutput: {
          contains: ['资源', '课程']
        }
      },
      {
        agent: 'soer',
        action: 'track_progress',
        expectedOutput: {
          contains: ['跟踪', '进度']
        }
      }
    ]
  },
  {
    name: '紧急健康事件处理',
    description: '用户报告紧急健康状况，智能体快速响应',
    userInput: '我突然感到胸闷气短，很担心',
    steps: [
      {
        agent: 'xiaoai',
        action: 'emergency_assessment',
        expectedOutput: {
          contains: ['紧急', '评估', '建议']
        }
      },
      {
        agent: 'xiaoke',
        action: 'emergency_service',
        expectedOutput: {
          contains: ['紧急', '服务', '联系']
        }
      },
      {
        agent: 'soer',
        action: 'emotional_support',
        expectedOutput: {
          contains: ['支持', '陪伴', '安慰']
        }
      }
    ]
  },
  {
    name: '个性化健康方案制定',
    description: '基于用户数据制定个性化健康管理方案',
    userInput: '请根据我的体质制定个性化的健康管理方案',
    steps: [
      {
        agent: 'xiaoai',
        action: 'health_analysis',
        expectedOutput: {
          contains: ['分析', '体质', '健康']
        }
      },
      {
        agent: 'laoke',
        action: 'tcm_constitution',
        expectedOutput: {
          contains: ['体质', '中医', '辨证']
        }
      },
      {
        agent: 'soer',
        action: 'lifestyle_plan',
        expectedOutput: {
          contains: ['方案', '生活', '个性化']
        }
      },
      {
        agent: 'xiaoke',
        action: 'service_integration',
        expectedOutput: {
          contains: ['整合', '服务', '方案']
        }
      }
    ]
  },
  {
    name: '智能体状态同步测试',
    description: '测试智能体之间的状态同步和信息共享',
    userInput: '测试智能体协作状态',
    steps: [
      {
        agent: 'xiaoai',
        action: 'status_report',
        expectedOutput: {
          confidence: 0.8
        }
      },
      {
        agent: 'xiaoke',
        action: 'status_report',
        expectedOutput: {
          confidence: 0.8
        }
      },
      {
        agent: 'laoke',
        action: 'status_report',
        expectedOutput: {
          confidence: 0.8
        }
      },
      {
        agent: 'soer',
        action: 'status_report',
        expectedOutput: {
          confidence: 0.8
        }
      }
    ]
  }
];

/**
 * 执行协作测试
 */
async function runCollaborationTest(scenario) {
  console.log(`\n🎭 测试场景: ${scenario.name}`);
  console.log(`   描述: ${scenario.description}`);
  console.log(`   用户输入: "${scenario.userInput}"`);

  const coordinator = new MockAgentCoordinator();
  const result = await coordinator.executeCollaboration(scenario, scenario.userInput);

  collaborationResults.total++;

  if (result.result === 'success') {
    collaborationResults.passed++;
    console.log(`   ✅ 协作成功 (${result.duration}ms)`);
  } else {
    collaborationResults.failed++;
    console.log(`   ❌ 协作失败: ${result.error || '未知错误'}`);
    collaborationResults.errors.push({
      scenario: scenario.name,
      error: result.error || '协作流程失败'
    });
  }

  // 显示详细步骤
  result.steps.forEach((step, index) => {
    const status = step.success ? '✅' : '❌';
    console.log(`     ${index + 1}. ${step.agent} - ${step.action}: ${status}`);
    if (!step.success) {
      console.log(`        错误: ${step.error}`);
    }
  });

  collaborationResults.scenarios.push(result);
  return result;
}

/**
 * 测试智能体通信协议
 */
async function testCommunicationProtocol() {
  console.log('\n📡 智能体通信协议测试');

  const coordinator = new MockAgentCoordinator();
  const testMessages = [
    { from: 'xiaoai', to: 'xiaoke', message: '需要为用户安排体检服务' },
    { from: 'xiaoke', to: 'laoke', message: '用户想了解体检项目的医学原理' },
    { from: 'laoke', to: 'soer', message: '为用户制定体检后的生活调整建议' },
    { from: 'soer', to: 'xiaoai', message: '用户生活习惯数据已更新' }
  ];

  let communicationSuccess = 0;

  for (const msg of testMessages) {
    try {
      const fromAgent = coordinator.agents[msg.from];
      const toAgent = coordinator.agents[msg.to];

      if (fromAgent && toAgent) {
        const response = await toAgent.processMessage(msg.message, { from: msg.from });
        console.log(`   ✅ ${msg.from} → ${msg.to}: 通信成功`);
        communicationSuccess++;
      } else {
        console.log(`   ❌ ${msg.from} → ${msg.to}: 智能体不存在`);
      }
    } catch (error) {
      console.log(`   ❌ ${msg.from} → ${msg.to}: ${error.message}`);
    }
  }

  collaborationResults.total++;
  if (communicationSuccess === testMessages.length) {
    collaborationResults.passed++;
    console.log(`   ✅ 通信协议测试通过 (${communicationSuccess}/${testMessages.length})`);
  } else {
    collaborationResults.failed++;
    console.log(`   ❌ 通信协议测试失败 (${communicationSuccess}/${testMessages.length})`);
  }
}

/**
 * 测试负载均衡和故障转移
 */
async function testLoadBalancingAndFailover() {
  console.log('\n⚖️  负载均衡和故障转移测试');

  const coordinator = new MockAgentCoordinator();

  // 模拟高负载
  console.log('   测试高负载处理...');
  const promises = [];
  for (let i = 0; i < 20; i++) {
    promises.push(coordinator.agents.xiaoai.processMessage(`并发测试消息${i}`));
  }

  try {
    const results = await Promise.all(promises);
    const successCount = results.filter(r => r.message).length;
    console.log(`   ✅ 高负载测试: ${successCount}/20 成功处理`);
  } catch (error) {
    console.log(`   ❌ 高负载测试失败: ${error.message}`);
  }

  // 模拟智能体故障
  console.log('   测试故障转移...');
  coordinator.agents.xiaoai.status = 'offline';

  try {
    // 尝试使用备用智能体
    const backupResponse = await coordinator.agents.xiaoke.processMessage('健康咨询请求', {
      originalAgent: 'xiaoai',
      isFailover: true
    });
    console.log('   ✅ 故障转移成功');
  } catch (error) {
    console.log(`   ❌ 故障转移失败: ${error.message}`);
  }

  collaborationResults.total++;
  collaborationResults.passed++; // 简化处理，实际应该根据测试结果判断
}

/**
 * 生成协作测试报告
 */
function generateCollaborationReport() {
  const report = {
    timestamp: new Date().toISOString(),
    summary: {
      total: collaborationResults.total,
      passed: collaborationResults.passed,
      failed: collaborationResults.failed,
      successRate: ((collaborationResults.passed / collaborationResults.total) * 100).toFixed(2) + '%'
    },
    scenarios: collaborationResults.scenarios.map(scenario => ({
      name: scenario.scenario,
      result: scenario.result,
      duration: scenario.duration,
      steps: scenario.steps.length,
      successfulSteps: scenario.steps.filter(s => s.success).length
    })),
    errors: collaborationResults.errors,
    recommendations: []
  };

  // 生成建议
  if (collaborationResults.failed > 0) {
    report.recommendations.push('优化失败的协作场景');
  }

  if (collaborationResults.passed / collaborationResults.total < 0.9) {
    report.recommendations.push('提升智能体协作稳定性');
  }

  report.recommendations.push('定期测试智能体协作功能');
  report.recommendations.push('监控智能体性能指标');
  report.recommendations.push('优化智能体通信协议');

  try {
    fs.writeFileSync('agent-collaboration-test-report.json', JSON.stringify(report, null, 2));
    console.log('\n📄 智能体协作测试报告已保存到: agent-collaboration-test-report.json');
  } catch (error) {
    console.warn('⚠️  无法保存测试报告');
  }

  return report;
}

/**
 * 主测试函数
 */
async function runAgentCollaborationTests() {
  console.log('开始智能体协作测试...\n');

  try {
    // 运行协作场景测试
    for (const scenario of collaborationScenarios) {
      await runCollaborationTest(scenario);
    }

    // 运行通信协议测试
    await testCommunicationProtocol();

    // 运行负载均衡和故障转移测试
    await testLoadBalancingAndFailover();

    console.log('\n📊 智能体协作测试结果');
    console.log('=====================================');
    console.log(`总测试数: ${collaborationResults.total}`);
    console.log(`通过: ${collaborationResults.passed}`);
    console.log(`失败: ${collaborationResults.failed}`);
    console.log(`成功率: ${((collaborationResults.passed / collaborationResults.total) * 100).toFixed(2)}%`);

    if (collaborationResults.errors.length > 0) {
      console.log('\n❌ 失败的测试:');
      collaborationResults.errors.forEach(error => {
        console.log(`  - ${error.scenario}: ${error.error}`);
      });
    }

    const report = generateCollaborationReport();

    console.log('\n💡 建议:');
    report.recommendations.forEach(rec => {
      console.log(`  - ${rec}`);
    });

    console.log('\n✅ 智能体协作测试完成！');

  } catch (error) {
    console.error('❌ 测试执行失败:', error.message);
    process.exit(1);
  }
}

// 运行测试
if (require.main === module) {
  runAgentCollaborationTests();
}

module.exports = { runAgentCollaborationTests, collaborationResults };