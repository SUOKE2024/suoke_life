/**
 * 知识标签初始化脚本
 * 用于将预定义的标签导入数据库
 */

import mongoose from 'mongoose';
import fs from 'fs';
import path from 'path';
import TagModel from '../models/tag.model';
import logger from '../utils/logger';
import { connectToDatabase } from '../utils/database';

interface TagData {
  name: string;
  description?: string;
  color?: string;
}

/**
 * 导入标签
 * @param tags 标签数据
 */
async function importTags(tags: TagData[]): Promise<void> {
  for (const tag of tags) {
    try {
      // 检查标签是否已存在
      let existingTag = await TagModel.findOne({ name: tag.name });
      
      if (existingTag) {
        // 更新现有标签
        existingTag.description = tag.description;
        existingTag.color = tag.color;
        
        await existingTag.save();
        logger.info(`更新标签: ${tag.name}`);
      } else {
        // 创建新标签
        const newTag = new TagModel({
          name: tag.name,
          description: tag.description,
          color: tag.color,
        });
        
        await newTag.save();
        logger.info(`创建标签: ${tag.name}`);
      }
    } catch (error) {
      logger.error(`处理标签 "${tag.name}" 时出错:`, { error });
    }
  }
}

/**
 * 导入所有知识标签
 */
async function importAllTags(): Promise<void> {
  try {
    // 连接数据库
    await connectToDatabase();
    
    // 读取并导入传统文化标签
    const traditionalCulturePath = path.resolve(__dirname, '../data/tags/traditional-culture-tags.json');
    const traditionalCultureTags = JSON.parse(fs.readFileSync(traditionalCulturePath, 'utf8'));
    await importTags(traditionalCultureTags);
    
    // 读取并导入现代医学标签
    const modernMedicinePath = path.resolve(__dirname, '../data/tags/modern-medicine-tags.json');
    const modernMedicineTags = JSON.parse(fs.readFileSync(modernMedicinePath, 'utf8'));
    await importTags(modernMedicineTags);
    
    logger.info('所有知识标签导入完成');
    
    // 关闭数据库连接
    await mongoose.connection.close();
    logger.info('数据库连接已关闭');
    
    process.exit(0);
  } catch (error) {
    logger.error('导入知识标签时出错:', { error });
    process.exit(1);
  }
}

// 执行导入
importAllTags();