#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

// 修复核心Agent文件语法错误的脚本
function fixCoreAgentFiles() {
  const coreFiles = [
    'src/agents/AgentCoordinator.ts',
    'src/agents/AgentManager.ts'
  ];

  coreFiles.forEach(filePath => {
    if (fs.existsSync(filePath)) {
      try {
        let content = fs.readFileSync(filePath, 'utf8');
        
        // 修复常见的语法错误
        content = content
          // 修复缺失的逗号
          .replace(/collaborationMode: "parallel_supporting";/g, 'collaborationMode: "parallel_supporting"')
          .replace(/context: AgentContext;/g, 'context: AgentContext')
          .replace(/message: string,/g, 'message: string,')
          .replace(/data?: any;/g, 'data?: any')
          
          // 修复函数调用语法
          .replace(/agentPromises\.push\(\)\s*agent\.processMessage/g, 'agentPromises.push(agent.processMessage')
          .replace(/const allAgents = \[;\s*taskAnalysis\.primaryAgent/g, 'const allAgents = [taskAnalysis.primaryAgent')
          .replace(/\.\.\.taskAnalysis\.supportingAgents;/g, '...taskAnalysis.supportingAgents')
          
          // 修复对象语法
          .replace(/reasoning: consensusResult\.reasoning;/g, 'reasoning: consensusResult.reasoning')
          .replace(/timestamp: new Date\(\)\.toISOString\(\);/g, 'timestamp: new Date().toISOString()')
          .replace(/collaborationMode: taskAnalysis\.collaborationMode;/g, 'collaborationMode: taskAnalysis.collaborationMode')
          
          // 修复reduce函数
          .replace(/\.reduce\(sum, d\) => sum \+ d\.confidence, 0\)/g, '.reduce((sum, d) => sum + d.confidence, 0)')
          .replace(/\.reduce\(acc, d\) => \{/g, '.reduce((acc, d) => {')
          .replace(/\.reduce\(\(acc, item\) => acc \+ item, 0\);/g, '.reduce((acc, item) => acc + item, 0)')
          .replace(/\(sum, r\) => sum \+ \(r\.metadata\?\.executionTime \|\| 0\),0;/g, '(sum, r) => sum + (r.metadata?.executionTime || 0), 0')
          
          // 修复map函数
          .replace(/\.map\(r\) => r\.data\)/g, '.map(r => r.data)')
          .replace(/\.map\(agent\) =>;/g, '.map(agent =>')
          .replace(/\.flatMap\(d\) => d\.reasoning\)/g, '.flatMap(d => d.reasoning)')
          .replace(/\.filter\(r\) => r\.success\)/g, '.filter(r => r.success)')
          
          // 修复字符串字面量
          .replace(/this\.log\("info",智能体协调器正在关闭\.\.\.\"\);/g, 'this.log("info", "智能体协调器正在关闭...");')
          .replace(/this\.log\("info",智能体协调器已关闭\"\);/g, 'this.log("info", "智能体协调器已关闭");')
          .replace(/this\.log\("error",智能体管理器初始化失败\", \" error\);/g, 'this.log("error", "智能体管理器初始化失败", error);')
          .replace(/this\.log\("error",任务处理失败\", \" error\);/g, 'this.log("error", "任务处理失败", error);')
          .replace(/this\.log\("error",健康检查失败\", \" error\);/g, 'this.log("error", "健康检查失败", error);')
          
          // 修复函数参数
          .replace(/private async getAgentDecision\(\)\s*agent: any,/g, 'private async getAgentDecision(agent: any,')
          .replace(/private buildConsensus\(decisions: AgentDecisionResult\[\]\): any \{/g, 'private buildConsensus(decisions: AgentDecisionResult[]): any {')
          .replace(/private generateCollaborationSummary\(results: AgentResponse\[\]\): string \{/g, 'private generateCollaborationSummary(results: AgentResponse[]): string {')
          .replace(/private log\(\)\s*level: "info" \| "warn" \| "error",/g, 'private log(level: "info" | "warn" | "error",')
          
          // 修复对象属性
          .replace(/error: error instanceof Error \? error\.message : String\(error\);/g, 'error: error instanceof Error ? error.message : String(error)')
          .replace(/executionTime: response\.metadata\?\.executionTime;/g, 'executionTime: response.metadata?.executionTime')
          .replace(/resourceLimits: \{;/g, 'resourceLimits: {')
          .replace(/\.\.\.config;/g, '...config')
          
          // 修复数组和对象语法
          .replace(/const agentTypes = \[;/g, 'const agentTypes = [')
          .replace(/AgentType\.SOER;/g, 'AgentType.SOER')
          .replace(/uptime: 0;/g, 'uptime: 0')
          
          // 修复函数调用
          .replace(/agent\.processMessage\(;\)/g, 'agent.processMessage(')
          .replace(/`决策请求: \$\{message\}`,context;/g, '`决策请求: ${message}`, context')
          .replace(/return \(;\)/g, 'return (')
          .replace(/setInterval\(\) => \{/g, 'setInterval(() => {')
          
          // 修复for循环
          .replace(/for \(const \[agentType, agent\] of this\.agents\) \{/g, 'for (const [agentType, agent] of this.agents) {')
          .replace(/for \(const \[agentType, status\] of allStatus\) \{/g, 'for (const [agentType, status] of allStatus) {')
          .replace(/for \(const \[agentType, metrics\] of this\.metrics\) \{/g, 'for (const [agentType, metrics] of this.metrics) {')
          
          // 修复其他语法错误
          .replace(/agentTypes\.forEach\(\(\(agentType\) => \{/g, 'agentTypes.forEach((agentType) => {')
          .replace(/lastCheck: new Date\(\);/g, 'lastCheck: new Date()')
          .replace(/averageResponseTime: avgResponseTime,systemUptime,isHealthy: this\.isSystemHealthy\(\),config: this\.config,lastUpdate: new Date\(\);/g, 'averageResponseTime: avgResponseTime, systemUptime, isHealthy: this.isSystemHealthy(), config: this.config, lastUpdate: new Date()')
          
          // 修复Promise类型错误
          .replace(/\): Promise<Map<AgentType, AgentHealthStatus> \| AgentHealthStatus> \{/g, '): Promise<Map<AgentType, AgentHealthStatus> | AgentHealthStatus> {')
          .replace(/\): Map<AgentType, AgentMetrics> \| AgentMetrics \| undefined \{/g, '): Map<AgentType, AgentMetrics> | AgentMetrics | undefined {');
        
        fs.writeFileSync(filePath, content);
        console.log(`✅ 修复了 ${filePath}`);
      } catch (error) {
        console.error(`❌ 修复 ${filePath} 时出错:`, error.message);
      }
    }
  });
}

// 执行修复
console.log('🔧 开始修复核心Agent文件语法错误...');
fixCoreAgentFiles();
console.log('✅ 核心Agent文件修复完成！'); 