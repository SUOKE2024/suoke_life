import { Request, Response, NextFunction } from 'express';
import * as dialectService from './dialect.service';
import logger from '../../core/utils/logger';
import { ApiError } from '../../core/utils/errors';
import multer from 'multer';
import os from 'os';
import path from 'path';
import { v4 as uuidv4 } from 'uuid';

// 配置临时文件存储
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, os.tmpdir());
  },
  filename: (req, file, cb) => {
    const extension = path.extname(file.originalname);
    cb(null, `dialect-${uuidv4()}${extension}`);
  },
});

const upload = multer({ 
  storage,
  limits: {
    fileSize: 10 * 1024 * 1024, // 限制10MB
  },
  fileFilter: (req, file, cb) => {
    // 只接受音频文件
    if (file.mimetype.startsWith('audio/')) {
      cb(null, true);
    } else {
      cb(new Error('仅支持音频文件'));
    }
  }
});

/**
 * 获取所有方言
 */
export const getAllDialects = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { active } = req.query;
    const activeOnly = active !== 'false';
    
    const dialects = await dialectService.getAllDialects(activeOnly);
    
    res.status(200).json(dialects);
  } catch (error) {
    logger.error('获取方言列表失败:', error);
    next(error);
  }
};

/**
 * 按地区分组获取方言
 */
export const getDialectsByRegion = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { active } = req.query;
    const activeOnly = active !== 'false';
    
    const dialectsByRegion = await dialectService.getDialectsByRegion(activeOnly);
    
    res.status(200).json(dialectsByRegion);
  } catch (error) {
    logger.error('按地区获取方言列表失败:', error);
    next(error);
  }
};

/**
 * 根据代码获取方言详情
 */
export const getDialectByCode = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { code } = req.params;
    
    const dialect = await dialectService.getDialectByCode(code);
    
    if (!dialect) {
      throw new ApiError(404, `未找到代码为 ${code} 的方言`);
    }
    
    res.status(200).json(dialect);
  } catch (error) {
    logger.error(`获取方言详情失败 [代码: ${req.params.code}]:`, error);
    next(error);
  }
};

/**
 * 创建方言
 */
export const createDialect = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const dialectData = req.body;
    
    const newDialect = await dialectService.createDialect(dialectData);
    
    res.status(201).json(newDialect);
  } catch (error) {
    logger.error('创建方言失败:', error);
    next(error);
  }
};

/**
 * 更新方言
 */
export const updateDialect = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { code } = req.params;
    const dialectData = req.body;
    
    const updatedDialect = await dialectService.updateDialect(code, dialectData);
    
    res.status(200).json(updatedDialect);
  } catch (error) {
    logger.error(`更新方言失败 [代码: ${req.params.code}]:`, error);
    next(error);
  }
};

/**
 * 删除方言
 */
export const deleteDialect = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const { code } = req.params;
    
    const result = await dialectService.deleteDialect(code);
    
    res.status(200).json(result);
  } catch (error) {
    logger.error(`删除方言失败 [代码: ${req.params.code}]:`, error);
    next(error);
  }
};

/**
 * 检测音频中的方言
 */
export const detectDialect = async (req: Request, res: Response, next: NextFunction) => {
  // 使用multer处理上传文件
  upload.single('audio')(req, res, async (err) => {
    if (err) {
      return next(new ApiError(400, err.message));
    }
    
    try {
      const audioFile = req.file;
      if (!audioFile) {
        throw new ApiError(400, '未提供音频文件');
      }
      
      // 从文件中读取音频数据
      const fs = require('fs');
      const audioBuffer = fs.readFileSync(audioFile.path);
      
      const result = await dialectService.detectDialect(audioBuffer, audioFile.mimetype);
      
      // 删除临时文件
      fs.unlinkSync(audioFile.path);
      
      res.status(200).json(result);
    } catch (error) {
      logger.error('检测方言失败:', error);
      next(error);
    }
  });
};

/**
 * 转换方言到标准普通话
 */
export const translateDialectToStandard = async (req: Request, res: Response, next: NextFunction) => {
  // 使用multer处理上传文件
  upload.single('audio')(req, res, async (err) => {
    if (err) {
      return next(new ApiError(400, err.message));
    }
    
    try {
      const audioFile = req.file;
      if (!audioFile) {
        throw new ApiError(400, '未提供音频文件');
      }
      
      const dialectCode = req.body.dialectCode;
      
      // 从文件中读取音频数据
      const fs = require('fs');
      const audioBuffer = fs.readFileSync(audioFile.path);
      
      const result = await dialectService.translateDialectToStandard(
        audioBuffer,
        audioFile.mimetype,
        dialectCode
      );
      
      // 删除临时文件
      fs.unlinkSync(audioFile.path);
      
      // 设置响应头
      res.setHeader('Content-Type', result.mimeType);
      res.setHeader('Content-Disposition', 'attachment; filename="translated.wav"');
      
      // 发送转换后的音频数据
      res.status(200).send(result.audio);
    } catch (error) {
      logger.error('转换方言失败:', error);
      next(error);
    }
  });
};

/**
 * 初始化默认方言数据
 */
export const initializeDefaultDialects = async (req: Request, res: Response, next: NextFunction) => {
  try {
    const result = await dialectService.initializeDefaultDialects();
    
    res.status(200).json(result);
  } catch (error) {
    logger.error('初始化默认方言数据失败:', error);
    next(error);
  }
}; 