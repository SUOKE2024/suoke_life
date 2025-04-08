import fs from 'fs';
import path from 'path';
import { Logger } from '../../infrastructure/logger';

/**
 * 数据集管理服务 - 负责数据集的加载、处理和管理
 */
export class DatasetService {
  private readonly logger;
  private readonly datasetsDir: string;
  
  constructor(datasetsDir: string) {
    this.logger = new Logger('DatasetService');
    this.datasetsDir = datasetsDir;
  }
  
  /**
   * 获取所有可用数据集列表
   * @returns 数据集信息列表
   */
  async listDatasets(): Promise<DatasetInfo[]> {
    try {
      const categories = await fs.promises.readdir(this.datasetsDir);
      const datasets: DatasetInfo[] = [];
      
      for (const category of categories) {
        const categoryPath = path.join(this.datasetsDir, category);
        const stats = await fs.promises.stat(categoryPath);
        
        if (stats.isDirectory()) {
          const datasetDirs = await fs.promises.readdir(categoryPath);
          
          for (const dataset of datasetDirs) {
            const datasetPath = path.join(categoryPath, dataset);
            const datasetStats = await fs.promises.stat(datasetPath);
            
            if (datasetStats.isDirectory()) {
              const files = await fs.promises.readdir(datasetPath);
              const dataFiles = files.filter(f => !f.startsWith('.') && !f.endsWith('.md'));
              
              // 尝试读取数据集元数据
              let metadata: Record<string, any> = {};
              const metadataPath = path.join(datasetPath, 'metadata.json');
              
              if (files.includes('metadata.json')) {
                try {
                  const metadataContent = await fs.promises.readFile(metadataPath, 'utf8');
                  metadata = JSON.parse(metadataContent);
                } catch (error) {
                  this.logger.warn(`无法解析数据集元数据: ${metadataPath}`);
                }
              }
              
              datasets.push({
                id: `${category}/${dataset}`,
                name: dataset,
                category,
                path: datasetPath,
                fileCount: dataFiles.length,
                files: dataFiles,
                metadata,
                lastModified: datasetStats.mtime.toISOString()
              });
            }
          }
        }
      }
      
      return datasets;
    } catch (error) {
      this.logger.error(`列出数据集失败: ${error.message}`);
      throw new Error(`列出数据集失败: ${error.message}`);
    }
  }
  
  /**
   * 获取特定数据集信息
   * @param datasetId 数据集ID
   * @returns 数据集详细信息
   */
  async getDatasetInfo(datasetId: string): Promise<DatasetDetailInfo> {
    try {
      const [category, dataset] = datasetId.split('/');
      
      if (!category || !dataset) {
        throw new Error(`无效的数据集ID: ${datasetId}`);
      }
      
      const datasetPath = path.join(this.datasetsDir, category, dataset);
      
      // 检查路径是否存在
      try {
        const stats = await fs.promises.stat(datasetPath);
        if (!stats.isDirectory()) {
          throw new Error(`数据集路径不是目录: ${datasetPath}`);
        }
      } catch (error) {
        throw new Error(`数据集不存在: ${datasetId}`);
      }
      
      // 读取数据集文件
      const files = await fs.promises.readdir(datasetPath);
      const dataFiles = files.filter(f => !f.startsWith('.') && !f.endsWith('.md'));
      
      // 尝试读取元数据
      let metadata: Record<string, any> = {};
      const metadataPath = path.join(datasetPath, 'metadata.json');
      
      if (files.includes('metadata.json')) {
        try {
          const metadataContent = await fs.promises.readFile(metadataPath, 'utf8');
          metadata = JSON.parse(metadataContent);
        } catch (error) {
          this.logger.warn(`无法解析数据集元数据: ${metadataPath}`);
        }
      }
      
      // 构建文件信息
      const fileInfoPromises = dataFiles.map(async (file) => {
        const filePath = path.join(datasetPath, file);
        const fileStats = await fs.promises.stat(filePath);
        return {
          name: file,
          size: fileStats.size,
          lastModified: fileStats.mtime.toISOString(),
          extension: path.extname(file)
        };
      });
      
      const fileInfos = await Promise.all(fileInfoPromises);
      
      // 构建详细信息
      const detailInfo: DatasetDetailInfo = {
        id: datasetId,
        name: dataset,
        category,
        path: datasetPath,
        fileCount: dataFiles.length,
        files: fileInfos,
        metadata,
        description: metadata.description || '',
        version: metadata.version || '1.0.0',
        createdAt: metadata.createdAt || '',
        updatedAt: metadata.updatedAt || '',
        source: metadata.source || '',
        license: metadata.license || '',
        authors: metadata.authors || []
      };
      
      return detailInfo;
    } catch (error) {
      this.logger.error(`获取数据集信息失败: ${error.message}`);
      throw new Error(`获取数据集信息失败: ${error.message}`);
    }
  }
  
  /**
   * 加载数据集文件内容
   * @param datasetId 数据集ID
   * @param fileName 文件名
   * @returns 文件内容对象
   */
  async loadDatasetFile(datasetId: string, fileName: string): Promise<DatasetFileContent> {
    try {
      const [category, dataset] = datasetId.split('/');
      
      if (!category || !dataset) {
        throw new Error(`无效的数据集ID: ${datasetId}`);
      }
      
      const filePath = path.join(this.datasetsDir, category, dataset, fileName);
      
      // 检查文件是否存在
      try {
        const stats = await fs.promises.stat(filePath);
        if (!stats.isFile()) {
          throw new Error(`路径不是文件: ${filePath}`);
        }
      } catch (error) {
        throw new Error(`文件不存在: ${fileName} 在数据集 ${datasetId}`);
      }
      
      // 读取文件内容
      const content = await fs.promises.readFile(filePath, 'utf8');
      const stats = await fs.promises.stat(filePath);
      
      // 基于文件扩展名处理不同格式
      const extension = path.extname(fileName).toLowerCase();
      let parsedContent: any = content;
      
      if (extension === '.json') {
        try {
          parsedContent = JSON.parse(content);
        } catch (error) {
          this.logger.warn(`无法解析JSON文件: ${filePath}`);
        }
      } else if (extension === '.csv') {
        // 简单CSV处理
        const lines = content.split('\n').filter(line => line.trim());
        if (lines.length > 0) {
          const headers = lines[0].split(',').map(h => h.trim());
          parsedContent = lines.slice(1).map(line => {
            const values = line.split(',').map(v => v.trim());
            const record: Record<string, string> = {};
            headers.forEach((header, index) => {
              record[header] = values[index] || '';
            });
            return record;
          });
        }
      }
      
      return {
        name: fileName,
        path: filePath,
        content: parsedContent,
        size: stats.size,
        lastModified: stats.mtime.toISOString(),
        extension: extension
      };
    } catch (error) {
      this.logger.error(`加载数据集文件失败: ${error.message}`);
      throw new Error(`加载数据集文件失败: ${error.message}`);
    }
  }
  
  /**
   * 获取数据集摘要统计
   * @returns 数据集统计信息
   */
  async getDatasetStats(): Promise<DatasetStats> {
    try {
      const datasets = await this.listDatasets();
      
      const categoryCounts: Record<string, number> = {};
      let totalFileCount = 0;
      let totalDatasetCount = 0;
      
      datasets.forEach(dataset => {
        categoryCounts[dataset.category] = (categoryCounts[dataset.category] || 0) + 1;
        totalFileCount += dataset.fileCount;
        totalDatasetCount += 1;
      });
      
      return {
        totalDatasetCount,
        totalFileCount,
        categoryCounts,
        lastUpdated: new Date().toISOString()
      };
    } catch (error) {
      this.logger.error(`获取数据集统计失败: ${error.message}`);
      throw new Error(`获取数据集统计失败: ${error.message}`);
    }
  }
}

/**
 * 数据集信息接口
 */
export interface DatasetInfo {
  id: string;
  name: string;
  category: string;
  path: string;
  fileCount: number;
  files: string[];
  metadata: Record<string, any>;
  lastModified: string;
}

/**
 * 数据集详细信息接口
 */
export interface DatasetDetailInfo {
  id: string;
  name: string;
  category: string;
  path: string;
  fileCount: number;
  files: Array<{
    name: string;
    size: number;
    lastModified: string;
    extension: string;
  }>;
  metadata: Record<string, any>;
  description: string;
  version: string;
  createdAt: string;
  updatedAt: string;
  source: string;
  license: string;
  authors: string[];
}

/**
 * 数据集文件内容接口
 */
export interface DatasetFileContent {
  name: string;
  path: string;
  content: any;
  size: number;
  lastModified: string;
  extension: string;
}

/**
 * 数据集统计信息接口
 */
export interface DatasetStats {
  totalDatasetCount: number;
  totalFileCount: number;
  categoryCounts: Record<string, number>;
  lastUpdated: string;
} 