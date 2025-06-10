import { AgentApiService } from '../../services/api/agentApiService';
import { AgentFactory } from '../factory/AgentFactory';
import { MessageType } from '../types/agents';

/**
 * 索克生活四智能体系统使用示例
 * 基于README.md第1013-1063行的智能体描述展示具体使用方法
 */
export class AgentUsageExample {
  /**
   * 示例1: 小艾智能体 - 健康咨询与四诊合参
   */
  public static async xiaoaiHealthConsultationExample(): Promise<void> {
    try {
      // 1. 创建小艾智能体
      const agentFactory = AgentFactory.getInstance();
      const xiaoai = await agentFactory.createXiaoaiAgent();

      console.log('小艾智能体创建成功:', xiaoai.getName());

      // 2. 健康咨询对话
      const apiService = AgentApiService.getInstance();
      const chatResponse = await apiService.xiaoaiChat({
        message: '你好小艾，我最近感觉疲劳，能帮我分析一下吗？',
        messageType: MessageType.TEXT,
        userId: 'user123',
        sessionId: 'session456',
      });

      console.log('小艾回复:', chatResponse.response);

      // 3. 四诊合参诊断
      const diagnosisResponse = await apiService.xiaoaiFourDiagnosis({
        userId: 'user123',
        sessionId: 'session456',
        diagnosisType: 'inquiry',
        data: {
          symptoms: ['疲劳', '头晕', '食欲不振'],
          duration: '2周',
        },
      });

      console.log('诊断结果:', diagnosisResponse.diagnosis);
    } catch (error) {
      console.error('小艾示例执行失败:', error);
    }
  }

  /**
   * 示例2: 小克智能体 - 服务管理与农产品定制
   */
  public static async xiaokeServiceManagementExample(): Promise<void> {
    try {
      // 1. 创建小克智能体
      const agentFactory = AgentFactory.getInstance();
      const xiaoke = await agentFactory.createXiaokeAgent();

      console.log('小克智能体创建成功:', xiaoke.getName());

      // 2. 服务订阅管理
      const apiService = AgentApiService.getInstance();
      const subscriptionResponse = await apiService.xiaokeServiceManagement({
        userId: 'user123',
        serviceType: 'health_subscription',
        parameters: {
          plan: 'premium',
          duration: 'monthly',
        },
      });

      console.log('订阅结果:', subscriptionResponse.subscription);

      // 3. 农产品定制
      const productResponse = await apiService.xiaokeProductCustomization({
        userId: 'user123',
        productType: 'organic_vegetables',
        customization: {
          quantity: '5kg',
          deliverySchedule: 'weekly',
          preferences: ['无农药', '本地种植'],
        },
      });

      console.log('定制结果:', productResponse.order);
    } catch (error) {
      console.error('小克示例执行失败:', error);
    }
  }

  /**
   * 示例3: 老克智能体 - 知识传播与游戏互动
   */
  public static async laokeKnowledgeExample(): Promise<void> {
    try {
      // 1. 创建老克智能体
      const agentFactory = AgentFactory.getInstance();
      const laoke = await agentFactory.createLaokeAgent();

      console.log('老克智能体创建成功:', laoke.getName());

      // 2. 知识检索
      const apiService = AgentApiService.getInstance();
      const knowledgeResponse = await apiService.laokeKnowledgeRetrieval({
        userId: 'user123',
        query: '中医养生的基本原则',
        category: 'traditional_medicine',
      });

      console.log('知识内容:', knowledgeResponse.knowledge);
    } catch (error) {
      console.error('老克示例执行失败:', error);
    }
  }

  /**
   * 示例4: 索儿智能体 - 生活健康管理
   */
  public static async soerLifestyleManagementExample(): Promise<void> {
    try {
      // 1. 创建索儿智能体
      const agentFactory = AgentFactory.getInstance();
      const soer = await agentFactory.createSoerAgent();

      console.log('索儿智能体创建成功:', soer.getName());

      // 2. 生活数据分析
      const apiService = AgentApiService.getInstance();
      const analysisResponse = await apiService.soerLifestyleAnalysis({
        userId: 'user123',
        dataType: 'comprehensive',
        timeRange: 'last_week',
      });

      console.log('生活分析:', analysisResponse.analysis);
    } catch (error) {
      console.error('索儿示例执行失败:', error);
    }
  }

  /**
   * 运行所有示例
   */
  public static async runAllExamples(): Promise<void> {
    console.log('开始运行索克生活四智能体系统示例...');

    try {
      await this.xiaoaiHealthConsultationExample();
      await this.xiaokeServiceManagementExample();
      await this.laokeKnowledgeExample();
      await this.soerLifestyleManagementExample();

      console.log('所有示例执行完成！');
    } catch (error) {
      console.error('示例执行过程中出现错误:', error);
    }
  }
}

export default AgentUsageExample;
