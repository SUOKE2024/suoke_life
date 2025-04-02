/**
 * 知识分类初始化脚本
 * 用于将预定义的分类结构导入数据库
 */

import mongoose from 'mongoose';
import fs from 'fs';
import path from 'path';
import CategoryModel from '../models/category.model';
import logger from '../utils/logger';
import { connectToDatabase } from '../utils/database';

interface CategoryData {
  name: string;
  description?: string;
  icon?: string;
  color?: string;
  children?: CategoryData[];
}

/**
 * 递归创建分类
 * @param categories 分类数据
 * @param parentId 父分类ID
 * @param parentPath 父分类路径
 * @param level 当前级别
 */
async function createCategories(
  categories: CategoryData[],
  parentId?: mongoose.Types.ObjectId,
  parentPath: mongoose.Types.ObjectId[] = [],
  level = 0
): Promise<void> {
  for (const category of categories) {
    try {
      // 检查分类是否已存在
      let existingCategory = await CategoryModel.findOne({ name: category.name });
      
      let categoryId: mongoose.Types.ObjectId;
      
      if (existingCategory) {
        // 更新现有分类
        existingCategory.description = category.description;
        existingCategory.icon = category.icon;
        existingCategory.color = category.color;
        
        if (parentId) {
          existingCategory.parentId = parentId;
          existingCategory.path = [...parentPath, parentId];
          existingCategory.level = level;
        }
        
        await existingCategory.save();
        categoryId = existingCategory._id;
        logger.info(`更新分类: ${category.name}`);
      } else {
        // 创建新分类
        const newCategory = new CategoryModel({
          name: category.name,
          description: category.description,
          icon: category.icon,
          color: category.color,
          parentId: parentId,
          path: parentId ? [...parentPath, parentId] : [],
          level: level,
        });
        
        await newCategory.save();
        categoryId = newCategory._id;
        logger.info(`创建分类: ${category.name}`);
      }
      
      // 递归处理子分类
      if (category.children && category.children.length > 0) {
        const newParentPath = parentId ? [...parentPath, parentId] : [];
        await createCategories(category.children, categoryId, newParentPath, level + 1);
      }
    } catch (error) {
      logger.error(`处理分类 "${category.name}" 时出错:`, { error });
    }
  }
}

/**
 * 导入所有知识分类
 */
async function importAllCategories(): Promise<void> {
  try {
    // 连接数据库
    await connectToDatabase();
    
    // 读取并导入传统文化分类
    const traditionalCulturePath = path.resolve(__dirname, '../data/categories/traditional-culture-categories.json');
    const traditionalCultureCategories = JSON.parse(fs.readFileSync(traditionalCulturePath, 'utf8'));
    await createCategories(traditionalCultureCategories);
    
    // 读取并导入现代医学分类
    const modernMedicinePath = path.resolve(__dirname, '../data/categories/modern-medicine-categories.json');
    const modernMedicineCategories = JSON.parse(fs.readFileSync(modernMedicinePath, 'utf8'));
    await createCategories(modernMedicineCategories);
    
    logger.info('所有知识分类导入完成');
    
    // 关闭数据库连接
    await mongoose.connection.close();
    logger.info('数据库连接已关闭');
    
    process.exit(0);
  } catch (error) {
    logger.error('导入知识分类时出错:', { error });
    process.exit(1);
  }
}

// 执行导入
importAllCategories();