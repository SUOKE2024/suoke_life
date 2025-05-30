/**
 * 索克生活四智能体系统使用示例
 * 基于README.md第1013-1063行的智能体描述展示具体使用方法
 */

import { AgentFactory } from '../factory/AgentFactory';
import { AgentApiService } from '../../services/api/agentApiService';
import { AgentType, MessageType } from '../../types/agents';

export class AgentUsageExample {
  
  /**
   * 示例1: 小艾智能体 - 四诊协调与健康咨询
   */
  public static async xiaoaiHealthConsultationExample() {
    console.log('=== 小艾智能体使用示例 ===');
    
    // 1. 创建小艾智能体
    const agentFactory = AgentFactory.getInstance();
    const xiaoai = await agentFactory.createXiaoaiAgent();
    console.log(`创建智能体: ${xiaoai.name} (${xiaoai.type})`);
    console.log(`核心功能: ${xiaoai.capabilities.slice(0, 5).join(', ')}...`);
    
    // 2. 语音交互示例
    const apiService = AgentApiService.getInstance();
    const chatResponse = await apiService.xiaoaiChat({
      message: "你好小艾，我最近感觉疲劳，能帮我分析一下吗？",
      messageType: MessageType.TEXT,
      userId: "user123",
      sessionId: "session456"
    });
    
    console.log('语音交互响应:', chatResponse.data?.content);
    
    // 3. 四诊协调示例
    const diagnosisResponse = await apiService.xiaoaiFourDiagnosis({
      userId: "user123",
      sessionId: "session456",
      diagnosisType: "inquiry",
      data: {
        symptoms: ["疲劳", "头晕", "食欲不振"],
        duration: "2周"
      }
    });
    
    console.log('四诊协调结果:', diagnosisResponse.data);
  }
  
  /**
   * 示例2: 小克智能体 - 服务管理与农产品定制
   */
  public static async xiaokeServiceManagementExample() {
    console.log('=== 小克智能体使用示例 ===');
    
    const agentFactory = AgentFactory.getInstance();
    const xiaoke = await agentFactory.createXiaokeAgent();
    console.log(`创建智能体: ${xiaoke.name} (${xiaoke.type})`);
    
    const apiService = AgentApiService.getInstance();
    
    // 1. 服务订阅管理
    const subscriptionResponse = await apiService.xiaokeServiceManagement({
      userId: "user123",
      serviceType: "health_subscription",
      parameters: {
        plan: "premium",
        duration: "monthly"
      }
    });
    
    console.log('服务订阅响应:', subscriptionResponse.data);
  }
  
  /**
   * 运行所有示例
   */
  public static async runAllExamples() {
    try {
      await this.xiaoaiHealthConsultationExample();
      await this.xiaokeServiceManagementExample();
      
      console.log('=== 所有示例运行完成 ===');
    } catch (error) {
      console.error('示例运行出错:', error);
    }
  }
}

export default AgentUsageExample;