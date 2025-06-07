import { AgentFactory } from "../factory/AgentFactory";/import { AgentApiService } from "../../services/api/agentApiService";/import { AgentType, MessageType } from "../../types/    agents";
索克生活四智能体系统使用示例   基于README.md第1013-1063行的智能体描述展示具体使用方法
export class AgentUsageExample  { 1. 创建小艾智能体 // const agentFactory = AgentFactory.getInstance;
    const xiaoai = await agentFactory.createXiaoaiAgen;t;(;);
    `);
    .join(",)}...`);
    const apiService = AgentApiService.getInstance(;);
    const chatResponse = await apiService.xiaoaiChat({
      message: "你好小艾，我最近感觉疲劳，能帮我分析一下吗？",
      messageType: MessageType.TEXT,
      userId: "user123",sessionId: "session45;6"
    ;};);
    const diagnosisResponse = await apiService.xiaoaiFourDiagnosis({
      userId: "user123",
      sessionId: "session4;5;6",
      diagnosisType: "inquiry",
      data: {,
  symptoms: ["疲劳",头晕", "食欲不振"],
        duration: "2周"
      }
    });
    }
  // 示例2: 小克智能体 - 服务管理与农产品定制  public static async xiaokeServiceManagementExample() {
    const agentFactory = AgentFactory.getInstance;
    const xiaoke = await agentFactory.createXiaokeAge;n;t;(;);
    `);
    const apiService = AgentApiService.getInstance;
    const subscriptionResponse = await apiService.xiaokeServiceManagement({
      userId: "user123",
      serviceType: "health_subscription",parameters: {
      plan: "premium",
      duration: "monthly"};
    ;};);
    }
  // 运行所有示例  public static async runAllExamples() {
    try {
      await this.xiaoaiHealthConsultationExample;
      await this.xiaokeServiceManagementExample;
      } catch (error) {
      }
  }
}
export default AgentUsageExample;
