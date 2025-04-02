import { Service } from 'typedi';
import * as sharp from 'sharp';
import { Logger } from '../../utils/logger';

@Service()
export class ImageProcessorService {
  private logger = new Logger('ImageProcessorService');

  /**
   * 预处理图像 - 调整大小、标准化和锐化
   * @param imageBuffer 原始图像缓冲区
   * @returns 处理后的图像缓冲区
   */
  async preprocessImage(imageBuffer: Buffer): Promise<Buffer> {
    try {
      this.logger.info('开始图像预处理');
      
      const processed = await sharp(imageBuffer)
        .resize(512, 512, { fit: 'inside' })
        .normalize()
        .sharpen()
        .toBuffer();
      
      this.logger.info('图像预处理完成');
      return processed;
    } catch (error) {
      this.logger.error(`图像预处理失败: ${error.message}`);
      throw new Error(`图像预处理失败: ${error.message}`);
    }
  }
  
  /**
   * 提取感兴趣区域（如舌头、面部等）
   * @param image 原始图像缓冲区
   * @param region 感兴趣区域类型 ('face', 'tongue', 'skin')
   * @returns 提取的区域图像缓冲区
   */
  async extractRegionOfInterest(image: Buffer, region: string): Promise<Buffer> {
    try {
      this.logger.info(`开始提取感兴趣区域: ${region}`);
      
      // 不同区域提取逻辑
      switch (region) {
        case 'face':
          // 面部提取逻辑 - 在实际实现中应使用面部检测算法
          return await this.processFaceRegion(image);
          
        case 'tongue':
          // 舌头提取逻辑 - 在实际实现中应使用舌头检测算法
          return await this.processTongueRegion(image);
          
        case 'skin':
          // 皮肤提取逻辑
          return await this.processSkinRegion(image);
          
        default:
          throw new Error(`不支持的区域类型: ${region}`);
      }
    } catch (error) {
      this.logger.error(`提取感兴趣区域失败: ${error.message}`);
      throw new Error(`提取感兴趣区域失败: ${error.message}`);
    }
  }

  /**
   * 提取图像特征
   * @param image 处理后的图像缓冲区
   * @returns 图像特征对象
   */
  async extractImageFeatures(image: Buffer): Promise<Record<string, any>> {
    try {
      this.logger.info('开始提取图像特征');
      
      // 提取基本特征
      const metadata = await sharp(image).metadata();
      
      // 计算颜色分布
      const stats = await sharp(image).stats();
      
      // 简单的颜色分析
      const dominantChannel = this.getDominantChannel(stats.channels);
      
      // 明暗分析
      const brightness = this.calculateBrightness(stats.channels);
      
      this.logger.info('图像特征提取完成');
      
      return {
        dimensions: {
          width: metadata.width,
          height: metadata.height
        },
        colorStats: stats.channels,
        dominantChannel,
        brightness,
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      this.logger.error(`提取图像特征失败: ${error.message}`);
      throw new Error(`提取图像特征失败: ${error.message}`);
    }
  }

  /**
   * 增强图像质量
   * @param image 原始图像缓冲区
   * @param options 增强选项
   * @returns 增强后的图像缓冲区
   */
  async enhanceImage(image: Buffer, options: { 
    contrast?: number;
    brightness?: number;
    saturation?: number;
  } = {}): Promise<Buffer> {
    try {
      this.logger.info('开始图像增强');
      
      const { contrast = 1.1, brightness = 1.0, saturation = 1.2 } = options;
      
      const enhanced = await sharp(image)
        .modulate({
          brightness,
          saturation
        })
        .linear(contrast, -(128 * contrast) + 128) // 调整对比度
        .toBuffer();
      
      this.logger.info('图像增强完成');
      return enhanced;
    } catch (error) {
      this.logger.error(`图像增强失败: ${error.message}`);
      throw new Error(`图像增强失败: ${error.message}`);
    }
  }

  /**
   * 去除图像噪点
   * @param image 原始图像缓冲区
   * @returns 去噪后的图像缓冲区
   */
  async denoiseImage(image: Buffer): Promise<Buffer> {
    try {
      this.logger.info('开始图像去噪');
      
      // 使用中值滤波进行简单去噪
      const denoised = await sharp(image)
        .median(3)
        .toBuffer();
      
      this.logger.info('图像去噪完成');
      return denoised;
    } catch (error) {
      this.logger.error(`图像去噪失败: ${error.message}`);
      throw new Error(`图像去噪失败: ${error.message}`);
    }
  }
  
  // 内部辅助方法
  
  private async processFaceRegion(image: Buffer): Promise<Buffer> {
    // 模拟面部区域提取
    // 在实际实现中，应使用面部识别库如face-api.js或OpenCV
    return image;
  }
  
  private async processTongueRegion(image: Buffer): Promise<Buffer> {
    // 模拟舌头区域提取
    // 在实际实现中，应使用专门的舌头检测算法
    return image;
  }
  
  private async processSkinRegion(image: Buffer): Promise<Buffer> {
    // 模拟皮肤区域提取
    return image;
  }
  
  private getDominantChannel(channels: any[]): string {
    // 找出主导颜色通道
    const channelNames = ['red', 'green', 'blue'];
    const averages = channels.map(c => c.mean);
    const maxIndex = averages.indexOf(Math.max(...averages));
    return channelNames[maxIndex];
  }
  
  private calculateBrightness(channels: any[]): number {
    // 计算图像亮度 (0-100)
    // 使用加权平均: 0.299R + 0.587G + 0.114B
    if (channels.length >= 3) {
      const brightness = (
        0.299 * channels[0].mean +
        0.587 * channels[1].mean +
        0.114 * channels[2].mean
      ) / 2.55; // 转换为0-100范围
      
      return parseFloat(brightness.toFixed(2));
    }
    return 0;
  }
}