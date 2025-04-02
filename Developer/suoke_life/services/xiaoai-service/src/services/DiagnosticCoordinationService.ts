import axios from 'axios';
import { logger } from '../index';
import { IUser } from '../models/User';

// 诊断服务接口
interface DiagnosticService {
  name: string;
  endpoint: string;
  description: string;
  isActive: boolean;
}

// 诊断结果接口
interface DiagnosticResult {
  response: string;
  currentStage?: string;
  actions?: any[];
  diagnosticData?: any;
}

export class DiagnosticCoordinationService {
  private diagnosticServices: Record<string, DiagnosticService>;
  
  constructor() {
    // 初始化四诊服务配置
    this.diagnosticServices = {
      looking: {
        name: '望诊服务',
        endpoint: process.env.LOOKING_DIAGNOSIS_SERVICE_URL || 'http://looking-diagnosis-service:3001',
        description: '通过面相、舌象等视觉信息进行诊断',
        isActive: true,
      },
      inquiry: {
        name: '问诊服务',
        endpoint: process.env.INQUIRY_DIAGNOSIS_SERVICE_URL || 'http://inquiry-diagnosis-service:3002',
        description: '通过询问病史、症状等信息进行诊断',
        isActive: true,
      },
      smell: {
        name: '闻诊服务',
        endpoint: process.env.SMELL_DIAGNOSIS_SERVICE_URL || 'http://smell-diagnosis-service:3003',
        description: '通过气味、声音等信息进行诊断',
        isActive: true,
      },
      touch: {
        name: '切诊服务',
        endpoint: process.env.TOUCH_DIAGNOSIS_SERVICE_URL || 'http://touch-diagnosis-service:3004',
        description: '通过脉象、触诊等信息进行诊断',
        isActive: true,
      },
    };
    
    logger.info('四诊协调服务已初始化');
  }
  
  /**
   * 检查诊断服务状态
   */
  public async checkServiceStatus(): Promise<Record<string, boolean>> {
    const serviceStatus: Record<string, boolean> = {};
    
    for (const [serviceId, service] of Object.entries(this.diagnosticServices)) {
      try {
        const response = await axios.get(`${service.endpoint}/health`, { timeout: 3000 });
        serviceStatus[serviceId] = response.status === 200;
        
        // 更新服务状态
        this.diagnosticServices[serviceId].isActive = serviceStatus[serviceId];
      } catch (error) {
        logger.warn(`${service.name}服务检查失败:`, error);
        serviceStatus[serviceId] = false;
        this.diagnosticServices[serviceId].isActive = false;
      }
    }
    
    return serviceStatus;
  }
  
  /**
   * 启动诊断流程
   */
  public async initiateDiagnosticFlow(
    user: IUser,
    requestedDiagnostics: string[]
  ): Promise<DiagnosticResult> {
    try {
      // 检查服务状态
      const serviceStatus = await this.checkServiceStatus();
      
      // 过滤出可用的诊断服务
      const availableDiagnostics = requestedDiagnostics.filter(
        (serviceId) => serviceStatus[serviceId]
      );
      
      if (availableDiagnostics.length === 0) {
        return {
          response: '抱歉，目前没有可用的诊断服务。请稍后再试。',
        };
      }
      
      // 为用户提供诊断服务说明
      const diagnosticDescriptions = availableDiagnostics
        .map((serviceId) => {
          const service = this.diagnosticServices[serviceId];
          return `- ${service.name}：${service.description}`;
        })
        .join('\n');
      
      // 生成诊断初始化响应
      const welcomeResponse = this.generateDiagnosticWelcomeMessage(
        user,
        availableDiagnostics
      );
      
      // 确定第一个诊断服务
      const firstDiagnostic = this.determineFirstDiagnosticService(
        availableDiagnostics,
        user
      );
      
      // 准备初始化第一个诊断服务
      const initActions = await this.prepareInitialDiagnosticActions(
        firstDiagnostic,
        user
      );
      
      return {
        response: welcomeResponse,
        currentStage: 'initialization',
        actions: initActions,
      };
    } catch (error) {
      logger.error('启动诊断流程失败:', error);
      return {
        response: '抱歉，启动诊断流程时出现错误。请稍后再试。',
      };
    }
  }
  
  /**
   * 处理诊断相关消息
   */
  public async processDiagnosticMessage(
    user: IUser,
    message: string,
    activeDiagnostics: string[]
  ): Promise<DiagnosticResult> {
    try {
      // 检查有无活跃的诊断服务
      if (!activeDiagnostics || activeDiagnostics.length === 0) {
        return {
          response: '抱歉，当前没有活跃的诊断服务。请先启动诊断流程。',
        };
      }
      
      // 确定当前活跃的诊断服务
      const currentDiagnostic = activeDiagnostics[0];
      const service = this.diagnosticServices[currentDiagnostic];
      
      if (!service || !service.isActive) {
        return {
          response: `抱歉，${service?.name || '请求的服务'}当前不可用。正在切换到其他诊断服务...`,
          actions: [
            {
              type: 'switchDiagnosticService',
              data: {
                from: currentDiagnostic,
                to: this.determineNextDiagnosticService(activeDiagnostics),
              },
            },
          ],
        };
      }
      
      // 将消息转发到当前诊断服务
      try {
        const response = await axios.post(
          `${service.endpoint}/api/diagnosis`,
          {
            userId: user.userId,
            message,
            userContext: {
              accessibilityNeeds: user.accessibilityNeeds,
              diagnosticHistory: user.diagnosticHistory,
            },
          },
          { timeout: 5000 }
        );
        
        // 处理诊断服务响应
        const diagnosticResponse = response.data;
        
        // 检查是否需要切换到下一个诊断服务
        if (diagnosticResponse.isComplete) {
          // 保存诊断结果
          await this.saveDiagnosticResult(user, currentDiagnostic, diagnosticResponse.diagnosticData);
          
          // 确定下一个诊断服务
          const nextDiagnostic = this.determineNextDiagnosticService(activeDiagnostics);
          
          if (nextDiagnostic) {
            // 准备切换到下一个诊断服务
            return {
              response: `${diagnosticResponse.message}\n\n接下来，我将为您启动${this.diagnosticServices[nextDiagnostic].name}。`,
              currentStage: 'switching',
              actions: [
                {
                  type: 'switchDiagnosticService',
                  data: {
                    from: currentDiagnostic,
                    to: nextDiagnostic,
                  },
                },
              ],
            };
          } else {
            // 所有诊断服务已完成
            return {
              response: `${diagnosticResponse.message}\n\n所有诊断服务已完成。感谢您的配合！`,
              currentStage: 'completed',
              actions: [
                {
                  type: 'completeDiagnostic',
                  data: {
                    summary: '四诊服务已全部完成',
                  },
                },
              ],
            };
          }
        }
        
        // 继续当前诊断服务
        return {
          response: diagnosticResponse.message,
          currentStage: diagnosticResponse.currentStage,
          actions: diagnosticResponse.actions,
        };
      } catch (error) {
        logger.error(`与${service.name}通信失败:`, error);
        
        // 尝试切换到下一个服务
        const nextDiagnostic = this.determineNextDiagnosticService(activeDiagnostics);
        
        if (nextDiagnostic) {
          return {
            response: `抱歉，${service.name}暂时无法使用。正在切换到${this.diagnosticServices[nextDiagnostic].name}...`,
            actions: [
              {
                type: 'switchDiagnosticService',
                data: {
                  from: currentDiagnostic,
                  to: nextDiagnostic,
                },
              },
            ],
          };
        } else {
          return {
            response: '抱歉，当前所有诊断服务都不可用。请稍后再试。',
          };
        }
      }
    } catch (error) {
      logger.error('处理诊断消息失败:', error);
      return {
        response: '抱歉，处理您的诊断请求时出现错误。请稍后再试。',
      };
    }
  }
  
  /**
   * 生成诊断欢迎消息
   */
  private generateDiagnosticWelcomeMessage(
    user: IUser,
    availableDiagnostics: string[]
  ): string {
    // 对于有视觉障碍的用户，提供更详细的语音描述
    if (user.accessibilityNeeds.visuallyImpaired) {
      return `您好，我是小艾，我将协助您完成中医四诊。我将引导您完成${availableDiagnostics.length}项诊断服务，包括${availableDiagnostics.map(id => this.diagnosticServices[id].name).join('、')}。整个过程将通过语音引导您完成，请您按照语音提示操作。我们将一步一步来，首先开始${this.diagnosticServices[availableDiagnostics[0]].name}。`;
    }
    
    // 标准欢迎消息
    return `您好，我是小艾，将协助您完成中医四诊。

我们将进行以下诊断服务：
${availableDiagnostics.map(id => `- ${this.diagnosticServices[id].name}`).join('\n')}

首先，我们将开始${this.diagnosticServices[availableDiagnostics[0]].name}。请按照指引完成每一步。`;
  }
  
  /**
   * 确定第一个诊断服务
   */
  private determineFirstDiagnosticService(
    availableDiagnostics: string[],
    user: IUser
  ): string {
    // 对于视障用户，优先使用问诊
    if (user.accessibilityNeeds.visuallyImpaired && availableDiagnostics.includes('inquiry')) {
      return 'inquiry';
    }
    
    // 默认按标准顺序：望(looking)、闻(smell)、问(inquiry)、切(touch)
    const standardOrder = ['looking', 'smell', 'inquiry', 'touch'];
    
    // 按标准顺序找到第一个可用的诊断服务
    for (const serviceId of standardOrder) {
      if (availableDiagnostics.includes(serviceId)) {
        return serviceId;
      }
    }
    
    // 如果没有按标准顺序找到，返回第一个可用的
    return availableDiagnostics[0];
  }
  
  /**
   * 确定下一个诊断服务
   */
  private determineNextDiagnosticService(activeDiagnostics: string[]): string | null {
    if (activeDiagnostics.length <= 1) {
      return null;
    }
    
    return activeDiagnostics[1];
  }
  
  /**
   * 准备初始化诊断操作
   */
  private async prepareInitialDiagnosticActions(
    diagnosticId: string,
    user: IUser
  ): Promise<any[]> {
    const service = this.diagnosticServices[diagnosticId];
    
    try {
      // 调用诊断服务初始化接口
      const response = await axios.post(
        `${service.endpoint}/api/init`,
        {
          userId: user.userId,
          userContext: {
            accessibilityNeeds: user.accessibilityNeeds,
            diagnosticHistory: user.diagnosticHistory,
          },
        },
        { timeout: 5000 }
      );
      
      return response.data.actions || [];
    } catch (error) {
      logger.error(`初始化${service.name}失败:`, error);
      return [
        {
          type: 'notification',
          data: {
            message: `无法初始化${service.name}，请稍后再试。`,
            level: 'error',
          },
        },
      ];
    }
  }
  
  /**
   * 保存诊断结果
   */
  private async saveDiagnosticResult(
    user: IUser,
    diagnosticId: string,
    diagnosticData: any
  ): Promise<void> {
    try {
      // 根据诊断类型保存结果
      switch (diagnosticId) {
        case 'looking':
          user.diagnosticHistory.lookingDiagnosis.push(JSON.stringify(diagnosticData));
          break;
        case 'inquiry':
          user.diagnosticHistory.inquiryDiagnosis.push(JSON.stringify(diagnosticData));
          break;
        case 'smell':
          user.diagnosticHistory.smellDiagnosis.push(JSON.stringify(diagnosticData));
          break;
        case 'touch':
          user.diagnosticHistory.touchDiagnosis.push(JSON.stringify(diagnosticData));
          break;
      }
      
      await user.save();
      logger.info(`已保存用户${user.userId}的${this.diagnosticServices[diagnosticId].name}结果`);
    } catch (error) {
      logger.error(`保存诊断结果失败:`, error);
      throw error;
    }
  }
}