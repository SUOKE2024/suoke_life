import { Request, Response } from 'express';
import { DiagnosticCoordinationService } from '../services/DiagnosticCoordinationService';
import { XiaoAiService } from '../services/XiaoAiService';
import { logger } from '../index';
import User from '../models/User';
import XiaoAiAgent from '../models/XiaoAiAgent';

// 创建服务实例
const diagnosticCoordinator = new DiagnosticCoordinationService();
const xiaoAiService = new XiaoAiService();

/**
 * 诊断控制器 - 处理四诊服务相关请求
 */
export const diagnosisController = {
  /**
   * 启动诊断流程
   */
  async initiateDiagnosisFlow(req: Request, res: Response): Promise<void> {
    try {
      const { userId, diagnosticServices = [] } = req.body;
      
      if (!userId) {
        res.status(400).json({ error: '用户ID不能为空' });
        return;
      }
      
      // 查找用户
      const user = await User.findOne({ userId });
      
      if (!user) {
        res.status(404).json({ error: '用户不存在' });
        return;
      }
      
      // 获取小艾智能体
      const agent = await XiaoAiAgent.findOne({ name: '小艾' });
      
      if (!agent) {
        res.status(404).json({ error: '小艾智能体不存在' });
        return;
      }
      
      // 确定要启动的诊断服务
      let servicesToInitiate = diagnosticServices;
      
      // 如果没有指定服务，启动所有服务
      if (servicesToInitiate.length === 0) {
        servicesToInitiate = ['looking', 'inquiry', 'smell', 'touch'];
      }
      
      // 切换到诊断协调模式
      agent.state.mode = 'diagnosis-coordination';
      agent.state.activeDiagnosticServices = servicesToInitiate;
      await agent.save();
      
      // 启动诊断流程
      const diagnosticResult = await diagnosticCoordinator.initiateDiagnosticFlow(
        user,
        servicesToInitiate
      );
      
      // 保存欢迎消息到对话历史
      agent.conversationHistory.push({
        timestamp: new Date(),
        userId: 'xiaoai',
        messageType: 'text',
        content: diagnosticResult.response,
        metadata: {
          diagnosticContext: {
            activeDiagnostics: servicesToInitiate,
            diagnosisStage: 'initialization',
          },
        },
      });
      await agent.save();
      
      res.status(200).json({
        success: true,
        message: '诊断流程已启动',
        response: diagnosticResult.response,
        actions: diagnosticResult.actions,
      });
    } catch (error) {
      logger.error('启动诊断流程失败:', error);
      res.status(500).json({ error: '启动诊断流程时发生错误' });
    }
  },
  
  /**
   * 获取所有可用的诊断服务
   */
  async getAvailableDiagnosticServices(req: Request, res: Response): Promise<void> {
    try {
      // 检查诊断服务状态
      const serviceStatus = await diagnosticCoordinator.checkServiceStatus();
      
      res.status(200).json({
        success: true,
        services: serviceStatus,
      });
    } catch (error) {
      logger.error('获取诊断服务状态失败:', error);
      res.status(500).json({ error: '获取诊断服务状态时发生错误' });
    }
  },
  
  /**
   * 获取用户当前的诊断状态
   */
  async getUserDiagnosisStatus(req: Request, res: Response): Promise<void> {
    try {
      const { userId } = req.params;
      
      if (!userId) {
        res.status(400).json({ error: '用户ID不能为空' });
        return;
      }
      
      // 获取小艾智能体
      const agent = await XiaoAiAgent.findOne({ name: '小艾' });
      
      if (!agent) {
        res.status(404).json({ error: '小艾智能体不存在' });
        return;
      }
      
      // 查找最近一条与该用户相关的诊断消息
      const recentDiagnosticMessages = agent.conversationHistory
        .filter(entry => 
          (entry.userId === 'xiaoai' || entry.userId === userId) && 
          entry.metadata?.diagnosticContext
        )
        .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
      
      if (recentDiagnosticMessages.length === 0) {
        res.status(200).json({
          success: true,
          isActive: false,
          message: '用户当前没有活跃的诊断会话',
        });
        return;
      }
      
      // 获取最近的诊断上下文
      const latestDiagnosticContext = recentDiagnosticMessages[0].metadata?.diagnosticContext;
      
      res.status(200).json({
        success: true,
        isActive: agent.state.mode === 'diagnosis-coordination',
        activeDiagnostics: agent.state.activeDiagnosticServices,
        currentStage: latestDiagnosticContext?.diagnosisStage || 'unknown',
        lastInteraction: recentDiagnosticMessages[0].timestamp,
      });
    } catch (error) {
      logger.error('获取用户诊断状态失败:', error);
      res.status(500).json({ error: '获取用户诊断状态时发生错误' });
    }
  },
  
  /**
   * 协调多个诊断服务之间的操作
   */
  async coordinateDiagnosticServices(req: Request, res: Response): Promise<void> {
    try {
      const { userId, action, data } = req.body;
      
      if (!userId || !action) {
        res.status(400).json({ error: '用户ID和操作类型不能为空' });
        return;
      }
      
      // 查找用户
      const user = await User.findOne({ userId });
      
      if (!user) {
        res.status(404).json({ error: '用户不存在' });
        return;
      }
      
      // 获取小艾智能体
      const agent = await XiaoAiAgent.findOne({ name: '小艾' });
      
      if (!agent) {
        res.status(404).json({ error: '小艾智能体不存在' });
        return;
      }
      
      let response;
      
      // 根据操作类型执行不同的协调操作
      switch (action) {
        case 'switchDiagnosticService':
          // 切换诊断服务
          if (data.from && data.to) {
            // 更新活跃的诊断服务
            agent.state.activeDiagnosticServices = agent.state.activeDiagnosticServices
              .filter(service => service !== data.from);
            
            if (!agent.state.activeDiagnosticServices.includes(data.to)) {
              agent.state.activeDiagnosticServices.unshift(data.to);
            }
            
            await agent.save();
            
            // 初始化新的诊断服务
            const initResult = await diagnosticCoordinator.processDiagnosticMessage(
              user,
              '开始诊断',
              [data.to]
            );
            
            response = {
              success: true,
              message: `已从${data.from}切换到${data.to}`,
              response: initResult.response,
              actions: initResult.actions,
            };
          } else {
            response = {
              success: false,
              error: '切换诊断服务需要提供from和to参数',
            };
          }
          break;
          
        case 'completeDiagnostic':
          // 完成当前诊断服务
          if (agent.state.activeDiagnosticServices.length > 0) {
            const completedService = agent.state.activeDiagnosticServices[0];
            agent.state.activeDiagnosticServices = agent.state.activeDiagnosticServices.slice(1);
            
            // 如果没有更多服务，退出诊断模式
            if (agent.state.activeDiagnosticServices.length === 0) {
              agent.state.mode = 'normal';
            }
            
            await agent.save();
            
            response = {
              success: true,
              message: `已完成${completedService}诊断`,
              isLastService: agent.state.activeDiagnosticServices.length === 0,
            };
          } else {
            agent.state.mode = 'normal';
            await agent.save();
            
            response = {
              success: true,
              message: '所有诊断服务已完成',
              isLastService: true,
            };
          }
          break;
          
        default:
          response = {
            success: false,
            error: `不支持的操作类型: ${action}`,
          };
      }
      
      res.status(200).json(response);
    } catch (error) {
      logger.error('协调诊断服务失败:', error);
      res.status(500).json({ error: '协调诊断服务时发生错误' });
    }
  },
  
  /**
   * 完成诊断流程
   */
  async completeDiagnosisFlow(req: Request, res: Response): Promise<void> {
    try {
      const { userId } = req.params;
      const { summary } = req.body;
      
      if (!userId) {
        res.status(400).json({ error: '用户ID不能为空' });
        return;
      }
      
      // 获取小艾智能体
      const agent = await XiaoAiAgent.findOne({ name: '小艾' });
      
      if (!agent) {
        res.status(404).json({ error: '小艾智能体不存在' });
        return;
      }
      
      // 重置智能体状态
      agent.state.mode = 'normal';
      agent.state.activeDiagnosticServices = [];
      await agent.save();
      
      // 添加诊断总结到对话历史
      if (summary) {
        agent.conversationHistory.push({
          timestamp: new Date(),
          userId: 'xiaoai',
          messageType: 'text',
          content: `诊断总结: ${summary}`,
        });
        await agent.save();
      }
      
      res.status(200).json({
        success: true,
        message: '诊断流程已完成',
      });
    } catch (error) {
      logger.error('完成诊断流程失败:', error);
      res.status(500).json({ error: '完成诊断流程时发生错误' });
    }
  },
  
  /**
   * 获取用户的诊断历史
   */
  async getUserDiagnosisHistory(req: Request, res: Response): Promise<void> {
    try {
      const { userId } = req.params;
      
      if (!userId) {
        res.status(400).json({ error: '用户ID不能为空' });
        return;
      }
      
      // 查找用户
      const user = await User.findOne({ userId });
      
      if (!user) {
        res.status(404).json({ error: '用户不存在' });
        return;
      }
      
      // 返回用户的诊断历史
      res.status(200).json({
        success: true,
        diagnosticHistory: {
          lookingDiagnosis: user.diagnosticHistory.lookingDiagnosis,
          inquiryDiagnosis: user.diagnosticHistory.inquiryDiagnosis,
          smellDiagnosis: user.diagnosticHistory.smellDiagnosis,
          touchDiagnosis: user.diagnosticHistory.touchDiagnosis,
        },
      });
    } catch (error) {
      logger.error('获取用户诊断历史失败:', error);
      res.status(500).json({ error: '获取用户诊断历史时发生错误' });
    }
  },
};