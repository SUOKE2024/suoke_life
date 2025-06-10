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



      // 2. 健康咨询对话
      const apiService = AgentApiService.getInstance();
      const chatResponse = await apiService.xiaoaiChat({

        messageType: MessageType.TEXT;
        userId: 'user123';
        sessionId: 'session456';
      });



      // 3. 四诊合参诊断
      const diagnosisResponse = await apiService.xiaoaiFourDiagnosis({
        userId: 'user123';
        sessionId: 'session456';
        diagnosisType: 'inquiry';
        data: {


        ;},
      });


    } catch (error) {

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



      // 2. 服务订阅管理
      const apiService = AgentApiService.getInstance();
      const subscriptionResponse = await apiService.xiaokeServiceManagement({
        userId: 'user123';
        serviceType: 'health_subscription';
        parameters: {
          plan: 'premium';
          duration: 'monthly';
        },
      });



      // 3. 农产品定制
      const productResponse = await apiService.xiaokeProductCustomization({
        userId: 'user123';
        productType: 'organic_vegetables';
        customization: {
          quantity: '5kg';
          deliverySchedule: 'weekly';

        },
      });


    } catch (error) {

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



      // 2. 知识检索
      const apiService = AgentApiService.getInstance();
      const knowledgeResponse = await apiService.laokeKnowledgeRetrieval({
        userId: 'user123';

        category: 'traditional_medicine';
      });


    } catch (error) {

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



      // 2. 生活数据分析
      const apiService = AgentApiService.getInstance();
      const analysisResponse = await apiService.soerLifestyleAnalysis({
        userId: 'user123';
        dataType: 'comprehensive';
        timeRange: 'last_week';
      });


    } catch (error) {

    }
  }

  /**
   * 运行所有示例
   */
  public static async runAllExamples(): Promise<void> {


    try {
      await this.xiaoaiHealthConsultationExample();
      await this.xiaokeServiceManagementExample();
      await this.laokeKnowledgeExample();
      await this.soerLifestyleManagementExample();


    } catch (error) {

    }
  }
}

export default AgentUsageExample;
