import { Request, Response, NextFunction } from 'express';
import { Container } from 'typedi';
import { Logger } from '../utils/logger';
import { TongueDiagnosisService } from '../services/tongue-diagnosis/tongue-diagnosis.service';

/**
 * 四诊协调服务Webhook控制器
 * 处理来自四诊协调服务的请求
 */
export class CoordinatorWebhookController {
  private logger = new Logger('CoordinatorWebhookController');
  private tongueDiagnosisService: TongueDiagnosisService;
  
  constructor() {
    this.tongueDiagnosisService = Container.get(TongueDiagnosisService);
  }
  
  /**
   * 验证请求来源是否合法
   * @param req Express请求对象
   * @param res Express响应对象
   * @param next Express下一个中间件
   */
  async validateCoordinatorRequest(req: Request, res: Response, next: NextFunction): Promise<void> {
    // 检查授权头或API密钥
    const apiKey = req.headers['x-api-key'];
    const expectedApiKey = process.env.COORDINATOR_API_KEY;
    
    if (!apiKey || apiKey !== expectedApiKey) {
      this.logger.warn(`未授权的webhook请求: ${req.ip}`);
      res.status(401).json({
        success: false,
        message: '未授权的请求',
        error: 'UNAUTHORIZED'
      });
      return;
    }
    
    next();
  }
  
  /**
   * 处理四诊分析请求
   * @param req Express请求对象
   * @param res Express响应对象
   * @param next Express下一个中间件
   */
  async handleDiagnosisRequest(req: Request, res: Response, next: NextFunction): Promise<void> {
    try {
      this.logger.logWithRequestId(req, '收到四诊协调服务请求');
      
      const { sessionId, userId, requestType } = req.body;
      
      if (!sessionId) {
        this.logger.error('缺少会话ID');
        res.status(400).json({
          success: false,
          message: '缺少会话ID',
          error: 'MISSING_SESSION_ID'
        });
        return;
      }
      
      if (!requestType) {
        this.logger.error('缺少请求类型');
        res.status(400).json({
          success: false,
          message: '缺少请求类型',
          error: 'MISSING_REQUEST_TYPE'
        });
        return;
      }
      
      // 根据请求类型处理
      switch (requestType) {
        case 'GET_TONGUE_DIAGNOSIS':
          // 获取最新的舌诊结果
          const tongueHistory = await this.tongueDiagnosisService.getDiagnosisHistory(
            userId,
            sessionId,
            1, // 只获取最新的一条
            0
          );
          
          if (tongueHistory.total === 0) {
            res.status(404).json({
              success: false,
              message: '未找到舌诊记录',
              error: 'DIAGNOSIS_NOT_FOUND'
            });
          } else {
            res.status(200).json({
              success: true,
              data: tongueHistory.records[0]
            });
          }
          break;
          
        case 'GET_TONGUE_HISTORY':
          // 获取舌诊历史记录
          const limit = req.body.limit || 10;
          const offset = req.body.offset || 0;
          
          const history = await this.tongueDiagnosisService.getDiagnosisHistory(
            userId,
            sessionId,
            limit,
            offset
          );
          
          res.status(200).json({
            success: true,
            data: {
              total: history.total,
              offset,
              limit,
              records: history.records
            }
          });
          break;
          
        default:
          this.logger.warn(`未知的请求类型: ${requestType}`);
          res.status(400).json({
            success: false,
            message: '未知的请求类型',
            error: 'UNKNOWN_REQUEST_TYPE'
          });
      }
    } catch (error) {
      this.logger.error(`处理四诊协调服务请求错误: ${error.message}`);
      next(error);
    }
  }
} 