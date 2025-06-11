import { AgentApiService } from "../../services/api/agentApiService"
import { AgentFactory } from "../factory/AgentFactory"
import { MessageType } from "../types/agents";
/* 法 */
 */
export class AgentUsageExample {/* 参 *//;}   */
const public = static async xiaoaiHealthConsultationExample(): Promise<void> {try {}      // 1. 创建小艾智能体;
const agentFactory = AgentFactory.getInstance();
const xiaoai = await agentFactory.createXiaoaiAgent();
      // 2. 健康咨询对话
const apiService = AgentApiService.getInstance();
const  chatResponse = await apiService.xiaoaiChat({)"messageType: MessageType.TEXT,')'
userId: 'user123,)'
}
}
        const sessionId = 'session456)'}
      });
      // 3. 四诊合参诊断'/,'/g'/;
const  diagnosisResponse = await apiService.xiaoaiFourDiagnosis({ )'userId: 'user123,'
sessionId: 'session456,'
diagnosisType: 'inquiry,'';
const data = {) })}
        ;},);
      });
    } catch (error) {}
}
    }
  }
  /* 制 */
   */
const public = static async xiaokeServiceManagementExample(): Promise<void> {try {}      // 1. 创建小克智能体
const agentFactory = AgentFactory.getInstance();
const xiaoke = await agentFactory.createXiaokeAgent();
      // 2. 服务订阅管理
const apiService = AgentApiService.getInstance();
const  subscriptionResponse = await apiService.xiaokeServiceManagement({',)userId: 'user123,''serviceType: 'health_subscription,'
parameters: {,'plan: 'premium,')
}
          const duration = 'monthly)}
        },);
      });
      // 3. 农产品定制'/,'/g'/;
const  productResponse = await apiService.xiaokeProductCustomization({ )'userId: 'user123,'
productType: 'organic_vegetables,'
customization: {,'quantity: '5kg,'
const deliverySchedule = 'weekly)'
 })}
        },);
      });
    } catch (error) {}
}
    }
  }
  /* 动 */
   */
const public = static async laokeKnowledgeExample(): Promise<void> {try {}      // 1. 创建老克智能体
const agentFactory = AgentFactory.getInstance();
const laoke = await agentFactory.createLaokeAgent();
      // 2. 知识检索
const apiService = AgentApiService.getInstance();
const  knowledgeResponse = await apiService.laokeKnowledgeRetrieval({ ',)userId: 'user123,')'; })
}
        const category = 'traditional_medicine)'}
      });
    } catch (error) {}
}
    }
  }
  /* 理 */
   */
const public = static async soerLifestyleManagementExample(): Promise<void> {try {}      // 1. 创建索儿智能体
const agentFactory = AgentFactory.getInstance();
const soer = await agentFactory.createSoerAgent();
      // 2. 生活数据分析
const apiService = AgentApiService.getInstance();
const  analysisResponse = await apiService.soerLifestyleAnalysis({',)userId: 'user123,')'dataType: 'comprehensive,)'
}
        const timeRange = 'last_week)'}
      });
    } catch (error) {}
}
    }
  }
  /* 例 */
   */
const public = static async runAllExamples(): Promise<void> {try {}      const await = this.xiaoaiHealthConsultationExample();
const await = this.xiaokeServiceManagementExample();
const await = this.laokeKnowledgeExample();
const await = this.soerLifestyleManagementExample();
}
}
    } catch (error) {}
}
    }
  }
}
export default AgentUsageExample;
''