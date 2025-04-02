import { Request, Response, NextFunction } from 'express';
import { Container } from 'typedi';
import { InquiryService } from '../services/inquiry.service';
import { HttpException } from '../exceptions/http.exception';
import { logger } from '../utils/logger';

/**
 * 问诊控制器
 * 处理与问诊相关的HTTP请求
 * @swagger
 * tags:
 *   name: 问诊
 *   description: 问诊会话管理和交互API
 */
export class InquiryController {
  private inquiryService: InquiryService;

  constructor() {
    this.inquiryService = Container.get(InquiryService);
  }

  /**
   * 创建问诊会话
   * @swagger
   * /api/inquiry/sessions:
   *   post:
   *     summary: 创建新的问诊会话
   *     tags: [问诊]
   *     requestBody:
   *       required: true
   *       content:
   *         application/json:
   *           schema:
   *             type: object
   *             required:
   *               - userId
   *             properties:
   *               userId:
   *                 type: string
   *                 description: 用户ID
   *               patientInfo:
   *                 type: object
   *                 description: 患者信息
   *                 properties:
   *                   name:
   *                     type: string
   *                   age:
   *                     type: number
   *                   gender:
   *                     type: string
   *                     enum: [male, female, other]
   *               preferences:
   *                 type: object
   *                 description: 会话偏好设置
   *     responses:
   *       201:
   *         description: 会话创建成功
   *         content:
   *           application/json:
   *             schema:
   *               type: object
   *               properties:
   *                 success:
   *                   type: boolean
   *                 message:
   *                   type: string
   *                 data:
   *                   type: object
   *       400:
   *         description: 请求参数错误
   *       401:
   *         description: 未授权
   *       500:
   *         description: 服务器错误
   */
  public createSession = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const { userId, patientInfo, preferences } = req.body;
      
      const session = await this.inquiryService.createSession(userId, patientInfo, preferences);
      
      res.status(201).json({
        success: true,
        message: '问诊会话创建成功',
        data: session
      });
    } catch (error) {
      logger.error('创建问诊会话失败', { error });
      next(error);
    }
  }

  /**
   * 更新会话偏好设置
   * @swagger
   * /api/inquiry/sessions/{id}/preferences:
   *   patch:
   *     summary: 更新会话偏好设置
   *     tags: [问诊]
   *     parameters:
   *       - in: path
   *         name: id
   *         schema:
   *           type: string
   *         required: true
   *         description: 会话ID
   *     requestBody:
   *       required: true
   *       content:
   *         application/json:
   *           schema:
   *             type: object
   *             properties:
   *               preferences:
   *                 type: object
   *                 required: true
   *     responses:
   *       200:
   *         description: 会话偏好设置更新成功
   *       400:
   *         description: 请求参数错误
   *       404:
   *         description: 会话不存在
   *       500:
   *         description: 服务器错误
   */
  public updateSessionPreferences = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const { id } = req.params;
      const preferences = req.body;
      
      const updatedSession = await this.inquiryService.updateSessionPreferences(id, preferences);
      
      res.status(200).json({
        success: true,
        message: '会话偏好设置更新成功',
        data: updatedSession
      });
    } catch (error) {
      logger.error('更新会话偏好设置失败', { error });
      next(error);
    }
  }

  /**
   * 处理问诊请求
   * @swagger
   * /api/inquiry/sessions/{sessionId}/inquiries:
   *   post:
   *     summary: 提交问诊请求并获取回复
   *     tags: [问诊]
   *     parameters:
   *       - in: path
   *         name: sessionId
   *         schema:
   *           type: string
   *         required: true
   *         description: 会话ID
   *     requestBody:
   *       required: true
   *       content:
   *         application/json:
   *           schema:
   *             type: object
   *             required:
   *               - content
   *             properties:
   *               content:
   *                 type: string
   *                 description: 问诊内容
   *                 minLength: 2
   *                 maxLength: 2000
   *               metadata:
   *                 type: object
   *                 description: 元数据
   *     responses:
   *       200:
   *         description: 问诊处理成功
   *       400:
   *         description: 请求参数错误
   *       404:
   *         description: 会话不存在
   *       500:
   *         description: 服务器错误
   */
  public processInquiry = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const { sessionId } = req.params;
      const userId = req.user?.id || req.body.userId; // 从认证或请求体获取
      const { content, metadata } = req.body;
      
      const result = await this.inquiryService.processInquiry(userId, sessionId, content, metadata);
      
      res.status(200).json({
        success: true,
        message: '问诊请求处理成功',
        data: result
      });
    } catch (error) {
      logger.error('处理问诊请求失败', { error, sessionId: req.params.sessionId });
      next(error);
    }
  }

  /**
   * 获取症状列表
   */
  public getExtractedSymptoms = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const { sessionId } = req.params;
      
      const symptoms = await this.inquiryService.getExtractedSymptoms(sessionId);
      
      res.status(200).json({
        success: true,
        message: '获取症状列表成功',
        data: { symptoms }
      });
    } catch (error) {
      logger.error('获取症状列表失败', { error });
      next(error);
    }
  }

  /**
   * 结束问诊会话
   */
  public endSession = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const { sessionId } = req.params;
      
      await this.inquiryService.endSession(sessionId);
      
      res.status(200).json({
        success: true,
        message: '问诊会话已结束'
      });
    } catch (error) {
      logger.error('结束问诊会话失败', { error });
      next(error);
    }
  }

  /**
   * 获取用户健康记录
   */
  public getUserHealthRecords = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const { userId } = req.params;
      
      const healthRecords = await this.inquiryService.getUserHealthRecords(userId);
      
      res.status(200).json({
        success: true,
        message: '获取用户健康记录成功',
        data: { healthRecords }
      });
    } catch (error) {
      logger.error('获取用户健康记录失败', { error });
      next(error);
    }
  }

  /**
   * 创建健康记录
   */
  public createHealthRecord = async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const { userId, sessionId, recordData } = req.body;
      
      const healthRecord = await this.inquiryService.createHealthRecord(userId, sessionId, recordData);
      
      res.status(201).json({
        success: true,
        message: '健康记录创建成功',
        data: healthRecord
      });
    } catch (error) {
      logger.error('创建健康记录失败', { error });
      next(error);
    }
  }
}