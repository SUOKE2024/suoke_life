/**
 * 版本管理控制器
 * 处理知识条目的版本控制功能
 */
import { Request, Response } from 'express';
import mongoose from 'mongoose';
import { BadRequestError } from '../errors/bad-request-error';
import { NotFoundError } from '../errors/not-found-error';
import logger from '../utils/logger';
import versionService from '../services/version.service';
import { successResponse, errorResponse } from '../utils/response';

export class VersionController {
  /**
   * 获取知识条目的版本历史
   * @swagger
   * /api/versions/{knowledgeType}/{id}:
   *   get:
   *     summary: 获取知识条目的版本历史
   *     description: 返回特定知识条目的所有历史版本信息
   *     tags: [版本管理]
   *     parameters:
   *       - in: path
   *         name: knowledgeType
   *         schema:
   *           type: string
   *         required: true
   *         description: 知识类型，如"tcm"、"nutrition"等
   *       - in: path
   *         name: id
   *         schema:
   *           type: string
   *         required: true
   *         description: 知识条目ID
   *     responses:
   *       200:
   *         description: 成功获取版本历史
   *         content:
   *           application/json:
   *             schema:
   *               allOf:
   *                 - $ref: '#/components/schemas/ApiResponse'
   *                 - type: object
   *                   properties:
   *                     data:
   *                       type: array
   *                       items:
   *                         type: object
   *                         properties:
   *                           version:
   *                             type: integer
   *                             example: 1
   *                           createdAt:
   *                             type: string
   *                             format: date-time
   *                           createdBy:
   *                             type: string
   *                             example: "60d5f7b7e4b0e6c7a14e1b5c"
   *                           changeDescription:
   *                             type: string
   *                             example: "初始版本"
   *       400:
   *         description: 无效的请求参数
   *         content:
   *           application/json:
   *             schema:
   *               $ref: '#/components/schemas/ErrorResponse'
   *       404:
   *         description: 知识条目不存在
   *         content:
   *           application/json:
   *             schema:
   *               $ref: '#/components/schemas/ErrorResponse'
   *       500:
   *         description: 服务器错误
   *         content:
   *           application/json:
   *             schema:
   *               $ref: '#/components/schemas/ErrorResponse'
   */
  async getVersionHistory(req: Request, res: Response) {
    try {
      const { knowledgeType, id } = req.params;
      
      if (!mongoose.Types.ObjectId.isValid(id)) {
        throw new BadRequestError('无效的知识条目ID');
      }
      
      const versions = await versionService.getVersionHistory(knowledgeType, id);
      
      return successResponse(res, versions, '获取版本历史成功');
    } catch (error) {
      logger.error('获取版本历史失败', { 
        error: (error as Error).message, 
        knowledgeType: req.params.knowledgeType,
        id: req.params.id
      });
      
      if (error instanceof BadRequestError) {
        return errorResponse(res, error.message, 'BadRequestError', 400);
      }
      
      if (error instanceof NotFoundError) {
        return errorResponse(res, error.message, 'NotFoundError', 404);
      }
      
      return errorResponse(res, '服务器错误', 'InternalServerError', 500);
    }
  }

  /**
   * 获取特定版本的知识条目
   * @swagger
   * /api/versions/{knowledgeType}/{id}/{version}:
   *   get:
   *     summary: 获取特定版本的知识条目
   *     description: 获取知识条目的指定版本内容
   *     tags: [版本管理]
   *     parameters:
   *       - in: path
   *         name: knowledgeType
   *         schema:
   *           type: string
   *         required: true
   *         description: 知识类型，如"tcm"、"nutrition"等
   *       - in: path
   *         name: id
   *         schema:
   *           type: string
   *         required: true
   *         description: 知识条目ID
   *       - in: path
   *         name: version
   *         schema:
   *           type: integer
   *         required: true
   *         description: 要获取的版本号
   *     responses:
   *       200:
   *         description: 成功获取版本数据
   *         content:
   *           application/json:
   *             schema:
   *               allOf:
   *                 - $ref: '#/components/schemas/ApiResponse'
   *                 - type: object
   *                   properties:
   *                     data:
   *                       type: object
   *                       description: 版本内容，根据知识类型有不同的结构
   *       400:
   *         description: 无效的请求参数
   *         content:
   *           application/json:
   *             schema:
   *               $ref: '#/components/schemas/ErrorResponse'
   *       404:
   *         description: 未找到指定版本
   *         content:
   *           application/json:
   *             schema:
   *               $ref: '#/components/schemas/ErrorResponse'
   *       500:
   *         description: 服务器错误
   *         content:
   *           application/json:
   *             schema:
   *               $ref: '#/components/schemas/ErrorResponse'
   */
  async getSpecificVersion(req: Request, res: Response) {
    try {
      const { knowledgeType, id, version } = req.params;
      
      if (!mongoose.Types.ObjectId.isValid(id)) {
        throw new BadRequestError('无效的知识条目ID');
      }
      
      const versionNumber = parseInt(version);
      if (isNaN(versionNumber) || versionNumber <= 0) {
        throw new BadRequestError('无效的版本号');
      }
      
      const versionData = await versionService.getSpecificVersion(knowledgeType, id, versionNumber);
      
      if (!versionData) {
        throw new NotFoundError('未找到指定版本的知识条目');
      }
      
      return successResponse(res, versionData, '获取版本数据成功');
    } catch (error) {
      logger.error('获取特定版本失败', { 
        error: (error as Error).message, 
        knowledgeType: req.params.knowledgeType,
        id: req.params.id,
        version: req.params.version
      });
      
      if (error instanceof BadRequestError) {
        return errorResponse(res, error.message, 'BadRequestError', 400);
      }
      
      if (error instanceof NotFoundError) {
        return errorResponse(res, error.message, 'NotFoundError', 404);
      }
      
      return errorResponse(res, '服务器错误', 'InternalServerError', 500);
    }
  }

  /**
   * 回滚到特定版本
   * @swagger
   * /api/versions/{knowledgeType}/{id}/rollback/{version}:
   *   post:
   *     summary: 回滚到特定版本
   *     description: 将知识条目回滚到指定的历史版本
   *     tags: [版本管理]
   *     parameters:
   *       - in: path
   *         name: knowledgeType
   *         schema:
   *           type: string
   *         required: true
   *         description: 知识类型，如"tcm"、"nutrition"等
   *       - in: path
   *         name: id
   *         schema:
   *           type: string
   *         required: true
   *         description: 知识条目ID
   *       - in: path
   *         name: version
   *         schema:
   *           type: integer
   *         required: true
   *         description: 要回滚到的版本号
   *     security:
   *       - bearerAuth: []
   *     responses:
   *       200:
   *         description: 成功回滚到指定版本
   *         content:
   *           application/json:
   *             schema:
   *               allOf:
   *                 - $ref: '#/components/schemas/ApiResponse'
   *                 - type: object
   *                   properties:
   *                     data:
   *                       type: object
   *                       properties:
   *                         id:
   *                           type: string
   *                           example: "60d5f7b7e4b0e6c7a14e1b5c"
   *                         version:
   *                           type: integer
   *                           example: 3
   *                         previousVersion:
   *                           type: integer
   *                           example: 2
   *       400:
   *         description: 无效的请求参数
   *         content:
   *           application/json:
   *             schema:
   *               $ref: '#/components/schemas/ErrorResponse'
   *       401:
   *         description: 未授权
   *         content:
   *           application/json:
   *             schema:
   *               $ref: '#/components/schemas/ErrorResponse'
   *       404:
   *         description: 未找到指定版本
   *         content:
   *           application/json:
   *             schema:
   *               $ref: '#/components/schemas/ErrorResponse'
   *       500:
   *         description: 服务器错误
   *         content:
   *           application/json:
   *             schema:
   *               $ref: '#/components/schemas/ErrorResponse'
   */
  async rollbackToVersion(req: Request, res: Response) {
    try {
      const { knowledgeType, id, version } = req.params;
      
      if (!mongoose.Types.ObjectId.isValid(id)) {
        throw new BadRequestError('无效的知识条目ID');
      }
      
      const versionNumber = parseInt(version);
      if (isNaN(versionNumber) || versionNumber <= 0) {
        throw new BadRequestError('无效的版本号');
      }
      
      // 设置用户ID（如果有）
      const userId = req.currentUser ? req.currentUser.id : undefined;
      
      const result = await versionService.rollbackToVersion(knowledgeType, id, versionNumber, userId);
      
      return successResponse(res, result, `已成功回滚到版本 ${versionNumber}`);
    } catch (error) {
      logger.error('回滚版本失败', { 
        error: (error as Error).message, 
        knowledgeType: req.params.knowledgeType,
        id: req.params.id,
        version: req.params.version
      });
      
      if (error instanceof BadRequestError) {
        return errorResponse(res, error.message, 'BadRequestError', 400);
      }
      
      if (error instanceof NotFoundError) {
        return errorResponse(res, error.message, 'NotFoundError', 404);
      }
      
      return errorResponse(res, '服务器错误', 'InternalServerError', 500);
    }
  }

  /**
   * 比较两个版本的差异
   * @swagger
   * /api/versions/{knowledgeType}/{id}/compare:
   *   get:
   *     summary: 比较两个版本的差异
   *     description: 比较同一知识条目的两个不同版本，并返回差异
   *     tags: [版本管理]
   *     parameters:
   *       - in: path
   *         name: knowledgeType
   *         schema:
   *           type: string
   *         required: true
   *         description: 知识类型，如"tcm"、"nutrition"等
   *       - in: path
   *         name: id
   *         schema:
   *           type: string
   *         required: true
   *         description: 知识条目ID
   *       - in: query
   *         name: fromVersion
   *         schema:
   *           type: integer
   *         required: true
   *         description: 起始版本号
   *       - in: query
   *         name: toVersion
   *         schema:
   *           type: integer
   *         required: true
   *         description: 目标版本号
   *     responses:
   *       200:
   *         description: 成功获取版本差异
   *         content:
   *           application/json:
   *             schema:
   *               allOf:
   *                 - $ref: '#/components/schemas/ApiResponse'
   *                 - type: object
   *                   properties:
   *                     data:
   *                       type: object
   *                       properties:
   *                         additions:
   *                           type: array
   *                           items:
   *                             type: object
   *                         deletions:
   *                           type: array
   *                           items:
   *                             type: object
   *                         modifications:
   *                           type: array
   *                           items:
   *                             type: object
   *       400:
   *         description: 无效的请求参数
   *         content:
   *           application/json:
   *             schema:
   *               $ref: '#/components/schemas/ErrorResponse'
   *       404:
   *         description: 未找到指定版本
   *         content:
   *           application/json:
   *             schema:
   *               $ref: '#/components/schemas/ErrorResponse'
   *       500:
   *         description: 服务器错误
   *         content:
   *           application/json:
   *             schema:
   *               $ref: '#/components/schemas/ErrorResponse'
   */
  async compareVersions(req: Request, res: Response) {
    try {
      const { knowledgeType, id } = req.params;
      const { fromVersion, toVersion } = req.query;
      
      if (!mongoose.Types.ObjectId.isValid(id)) {
        throw new BadRequestError('无效的知识条目ID');
      }
      
      const fromVersionNumber = parseInt(fromVersion as string);
      const toVersionNumber = parseInt(toVersion as string);
      
      if (isNaN(fromVersionNumber) || isNaN(toVersionNumber) || 
          fromVersionNumber <= 0 || toVersionNumber <= 0) {
        throw new BadRequestError('无效的版本号');
      }
      
      const diff = await versionService.compareVersions(
        knowledgeType, 
        id, 
        fromVersionNumber, 
        toVersionNumber
      );
      
      return successResponse(res, diff, '获取版本差异成功');
    } catch (error) {
      logger.error('比较版本差异失败', { 
        error: (error as Error).message, 
        knowledgeType: req.params.knowledgeType,
        id: req.params.id,
        fromVersion: req.query.fromVersion,
        toVersion: req.query.toVersion
      });
      
      if (error instanceof BadRequestError) {
        return errorResponse(res, error.message, 'BadRequestError', 400);
      }
      
      if (error instanceof NotFoundError) {
        return errorResponse(res, error.message, 'NotFoundError', 404);
      }
      
      return errorResponse(res, '服务器错误', 'InternalServerError', 500);
    }
  }
}

export default new VersionController();