/**
 * 视障用户专属内容格式服务
 * 为视力障碍用户提供适配的内容格式，增强可访问性
 */
import { logger } from '../utils/logger';
import { AccessibilityLevel, ElementDescription } from '../types/accessibility';

/**
 * 内容类型
 */
export enum ContentType {
  ARTICLE = 'article',
  RECIPE = 'recipe',
  PRODUCT = 'product',
  NEWS = 'news',
  TUTORIAL = 'tutorial',
  VIDEO = 'video',
  AUDIO = 'audio',
  INTERACTIVE = 'interactive',
  IMAGE = 'image',
  CHART = 'chart'
}

/**
 * 图像描述级别
 */
export enum ImageDescriptionLevel {
  BASIC = 'basic',           // 基础描述
  DETAILED = 'detailed',     // 详细描述
  CONTEXTUAL = 'contextual', // 带上下文的描述
  TECHNICAL = 'technical'    // 技术性描述
}

/**
 * 图像特征
 */
interface ImageFeature {
  type: 'color' | 'object' | 'text' | 'layout' | 'symbol';
  description: string;
  importance: 'high' | 'medium' | 'low';
  location?: string;
}

/**
 * 图表数据点
 */
interface ChartDataPoint {
  label: string;
  value: number | string;
  category?: string;
  trend?: 'up' | 'down' | 'stable';
}

/**
 * 视觉内容描述
 */
export interface VisualContentDescription {
  type: 'image' | 'chart' | 'diagram' | 'illustration';
  alt: string;
  detailedDescription: string;
  features?: ImageFeature[];
  dataPoints?: ChartDataPoint[];
  keyInsight?: string;
  contextualRelevance?: string;
}

/**
 * 视障用户专属内容服务
 */
export class VisionImpairedContentService {
  /**
   * 生成针对视障用户的文章摘要
   * @param title 文章标题
   * @param content 文章内容
   * @param maxLength 最大长度
   * @returns 适合屏幕阅读的文章摘要
   */
  public generateAccessibleSummary(title: string, content: string, maxLength: number = 200): string {
    try {
      // 去除HTML标签
      const plainText = content.replace(/<[^>]*>/g, '');
      
      // 提取关键句子
      const sentences = plainText.match(/[^.!?]+[.!?]+/g) || [];
      const importantSentences = sentences.filter(s => 
        s.includes('重要') || 
        s.includes('关键') || 
        s.includes('总结') || 
        s.includes('结论')
      );
      
      // 如果没有找到关键句，使用前几句
      const selectedSentences = importantSentences.length > 0 
        ? importantSentences.slice(0, 3)
        : sentences.slice(0, 3);
      
      // 组合摘要
      let summary = `${title}。`;
      summary += selectedSentences.join(' ');
      
      // 限制长度
      if (summary.length > maxLength) {
        summary = summary.substring(0, maxLength - 3) + '...';
      }
      
      return summary;
    } catch (error) {
      logger.error('生成无障碍摘要失败', { error, title });
      // 出错时返回简单摘要
      return `${title}。该文章无法生成摘要，请访问完整内容。`;
    }
  }
  
  /**
   * 为视觉内容生成详细描述
   * @param image 图像信息
   * @param descriptionLevel 描述级别
   * @returns 详细的图像描述
   */
  public generateImageDescription(
    image: {
      url: string;
      alt?: string;
      context?: string;
      tags?: string[];
      recognizedObjects?: string[];
      recognizedText?: string;
      colors?: string[];
    },
    descriptionLevel: ImageDescriptionLevel = ImageDescriptionLevel.DETAILED
  ): VisualContentDescription {
    try {
      let description: VisualContentDescription = {
        type: 'image',
        alt: image.alt || '图像',
        detailedDescription: ''
      };
      
      // 基本描述总是包含
      let baseDescription = image.alt || '无描述文本的图像';
      
      // 根据描述级别增加细节
      switch (descriptionLevel) {
        case ImageDescriptionLevel.BASIC:
          description.detailedDescription = baseDescription;
          break;
          
        case ImageDescriptionLevel.DETAILED:
          // 添加识别到的对象
          if (image.recognizedObjects && image.recognizedObjects.length > 0) {
            baseDescription += `。图中包含: ${image.recognizedObjects.join('、')}`;
          }
          
          // 添加识别到的文本
          if (image.recognizedText) {
            baseDescription += `。图中文字: ${image.recognizedText}`;
          }
          
          description.detailedDescription = baseDescription;
          
          // 提取特征
          description.features = this.extractImageFeatures(image);
          break;
          
        case ImageDescriptionLevel.CONTEXTUAL:
          // 详细描述加上下文
          const detailedDesc = this.generateImageDescription(
            image, 
            ImageDescriptionLevel.DETAILED
          );
          
          let contextualDesc = detailedDesc.detailedDescription;
          
          // 添加上下文信息
          if (image.context) {
            contextualDesc += `。上下文: ${image.context}`;
          }
          
          description = {
            ...detailedDesc,
            detailedDescription: contextualDesc,
            contextualRelevance: image.context
          };
          break;
          
        case ImageDescriptionLevel.TECHNICAL:
          // 技术性描述包含所有可用信息
          const contextDesc = this.generateImageDescription(
            image, 
            ImageDescriptionLevel.CONTEXTUAL
          );
          
          let technicalDesc = contextDesc.detailedDescription;
          
          // 添加颜色信息
          if (image.colors && image.colors.length > 0) {
            technicalDesc += `。主要颜色: ${image.colors.join('、')}`;
          }
          
          description = {
            ...contextDesc,
            detailedDescription: technicalDesc
          };
          break;
      }
      
      return description;
    } catch (error) {
      logger.error('生成图像描述失败', { error, imageUrl: image.url });
      // 出错时返回基本描述
      return {
        type: 'image',
        alt: image.alt || '图像',
        detailedDescription: image.alt || '无法生成详细描述的图像'
      };
    }
  }
  
  /**
   * 提取图像特征
   * @param image 图像信息
   * @returns 图像特征数组
   */
  private extractImageFeatures(image: any): ImageFeature[] {
    const features: ImageFeature[] = [];
    
    // 添加识别到的对象作为特征
    if (image.recognizedObjects) {
      image.recognizedObjects.forEach((obj: string, index: number) => {
        features.push({
          type: 'object',
          description: obj,
          importance: index < 3 ? 'high' : 'medium'
        });
      });
    }
    
    // 添加识别到的文本作为特征
    if (image.recognizedText) {
      features.push({
        type: 'text',
        description: image.recognizedText,
        importance: 'high'
      });
    }
    
    // 添加颜色作为特征
    if (image.colors && image.colors.length > 0) {
      features.push({
        type: 'color',
        description: `主要颜色: ${image.colors.join('、')}`,
        importance: 'medium'
      });
    }
    
    return features;
  }
  
  /**
   * 生成图表的无障碍描述
   * @param chart 图表数据
   * @returns 图表描述
   */
  public generateChartDescription(
    chart: {
      type: 'bar' | 'line' | 'pie' | 'scatter' | 'area';
      title: string;
      data: ChartDataPoint[];
      xAxisLabel?: string;
      yAxisLabel?: string;
      insight?: string;
    }
  ): VisualContentDescription {
    try {
      let description: VisualContentDescription = {
        type: 'chart',
        alt: `${chart.title} ${chart.type}图表`,
        detailedDescription: '',
        dataPoints: chart.data,
        keyInsight: chart.insight
      };
      
      // 根据图表类型生成不同的描述
      switch (chart.type) {
        case 'bar':
          description.detailedDescription = this.generateBarChartDescription(chart);
          break;
        case 'line':
          description.detailedDescription = this.generateLineChartDescription(chart);
          break;
        case 'pie':
          description.detailedDescription = this.generatePieChartDescription(chart);
          break;
        default:
          description.detailedDescription = this.generateGenericChartDescription(chart);
      }
      
      // 如果有洞察，添加到描述末尾
      if (chart.insight) {
        description.detailedDescription += ` 关键发现: ${chart.insight}`;
      }
      
      return description;
    } catch (error) {
      logger.error('生成图表描述失败', { error, chartTitle: chart.title });
      // 出错时返回基本描述
      return {
        type: 'chart',
        alt: `${chart.title || '未命名'} 图表`,
        detailedDescription: `这是一个${chart.type || ''}图表，无法生成详细描述。`
      };
    }
  }
  
  /**
   * 生成条形图描述
   * @param chart 图表数据
   * @returns 条形图描述
   */
  private generateBarChartDescription(chart: any): string {
    let desc = `这是一个题为"${chart.title}"的条形图`;
    
    if (chart.xAxisLabel && chart.yAxisLabel) {
      desc += `，横轴表示${chart.xAxisLabel}，纵轴表示${chart.yAxisLabel}`;
    }
    
    desc += '。';
    
    // 添加数据点信息
    if (chart.data && chart.data.length > 0) {
      // 找出最大值和最小值
      const values = chart.data.map((d: ChartDataPoint) => 
        typeof d.value === 'number' ? d.value : 0
      );
      
      const maxValue = Math.max(...values);
      const minValue = Math.min(...values);
      
      const maxItem = chart.data.find((d: ChartDataPoint) => 
        d.value === maxValue
      );
      
      const minItem = chart.data.find((d: ChartDataPoint) => 
        d.value === minValue
      );
      
      desc += `图表包含${chart.data.length}个数据项。`;
      
      // 报告最高值和最低值
      if (maxItem) {
        desc += `${maxItem.label}的值最高，为${maxItem.value}。`;
      }
      
      if (minItem && minItem !== maxItem) {
        desc += `${minItem.label}的值最低，为${minItem.value}。`;
      }
      
      // 如果数据点不多，列出所有数据
      if (chart.data.length <= 5) {
        desc += '所有数据点为：';
        chart.data.forEach((point: ChartDataPoint, index: number) => {
          desc += `${point.label}: ${point.value}`;
          if (index < chart.data.length - 1) {
            desc += '；';
          } else {
            desc += '。';
          }
        });
      }
    }
    
    return desc;
  }
  
  /**
   * 生成折线图描述
   * @param chart 图表数据
   * @returns 折线图描述
   */
  private generateLineChartDescription(chart: any): string {
    let desc = `这是一个题为"${chart.title}"的折线图`;
    
    if (chart.xAxisLabel && chart.yAxisLabel) {
      desc += `，横轴表示${chart.xAxisLabel}，纵轴表示${chart.yAxisLabel}`;
    }
    
    desc += '。';
    
    // 添加趋势信息
    if (chart.data && chart.data.length > 0) {
      desc += `图表展示了${chart.data.length}个数据点的趋势。`;
      
      // 计算整体趋势
      const values = chart.data.map((d: ChartDataPoint) => 
        typeof d.value === 'number' ? d.value : 0
      );
      
      if (values.length > 1) {
        const firstValue = values[0];
        const lastValue = values[values.length - 1];
        
        if (lastValue > firstValue) {
          desc += `总体趋势是上升的，从${firstValue}上升到${lastValue}。`;
        } else if (lastValue < firstValue) {
          desc += `总体趋势是下降的，从${firstValue}下降到${lastValue}。`;
        } else {
          desc += `总体趋势是稳定的，开始和结束都是${firstValue}。`;
        }
      }
      
      // 添加关键点
      const maxValue = Math.max(...values);
      const minValue = Math.min(...values);
      
      const maxIndex = values.indexOf(maxValue);
      const minIndex = values.indexOf(minValue);
      
      if (maxIndex !== -1) {
        desc += `最高点出现在${chart.data[maxIndex].label}，值为${maxValue}。`;
      }
      
      if (minIndex !== -1 && minIndex !== maxIndex) {
        desc += `最低点出现在${chart.data[minIndex].label}，值为${minValue}。`;
      }
    }
    
    return desc;
  }
  
  /**
   * 生成饼图描述
   * @param chart 图表数据
   * @returns 饼图描述
   */
  private generatePieChartDescription(chart: any): string {
    let desc = `这是一个题为"${chart.title}"的饼图。`;
    
    // 添加数据点信息
    if (chart.data && chart.data.length > 0) {
      // 计算总和
      const total = chart.data.reduce((sum: number, item: ChartDataPoint) => 
        sum + (typeof item.value === 'number' ? item.value : 0), 
        0
      );
      
      // 按照值的大小排序
      const sortedData = [...chart.data].sort((a, b) => {
        const aVal = typeof a.value === 'number' ? a.value : 0;
        const bVal = typeof b.value === 'number' ? b.value : 0;
        return bVal - aVal;
      });
      
      desc += `饼图包含${chart.data.length}个部分，总计${total}。`;
      
      // 描述最大的几个部分
      const topItems = sortedData.slice(0, 3);
      desc += '主要部分为：';
      
      topItems.forEach((item: ChartDataPoint, index: number) => {
        const percentage = ((typeof item.value === 'number' ? item.value : 0) / total * 100).toFixed(1);
        
        desc += `${item.label}占${percentage}%`;
        if (index < topItems.length - 1) {
          desc += '，';
        } else {
          desc += '。';
        }
      });
      
      // 如果有很多小部分，汇总它们
      if (sortedData.length > 3) {
        const otherItems = sortedData.slice(3);
        const otherTotal = otherItems.reduce((sum: number, item: ChartDataPoint) => 
          sum + (typeof item.value === 'number' ? item.value : 0), 
          0
        );
        
        const otherPercentage = (otherTotal / total * 100).toFixed(1);
        
        if (otherTotal > 0) {
          desc += `其他${otherItems.length}个部分共占${otherPercentage}%。`;
        }
      }
    }
    
    return desc;
  }
  
  /**
   * 生成通用图表描述
   * @param chart 图表数据
   * @returns 图表描述
   */
  private generateGenericChartDescription(chart: any): string {
    let desc = `这是一个题为"${chart.title}"的${chart.type}图表。`;
    
    if (chart.data && chart.data.length > 0) {
      desc += `图表包含${chart.data.length}个数据点。`;
      
      // 列出重要的数据点
      const importantPoints = chart.data.slice(0, 5);
      
      if (importantPoints.length > 0) {
        desc += '主要数据包括：';
        
        importantPoints.forEach((point: ChartDataPoint, index: number) => {
          desc += `${point.label}: ${point.value}`;
          if (index < importantPoints.length - 1) {
            desc += '；';
          } else {
            desc += '。';
          }
        });
      }
    }
    
    return desc;
  }
  
  /**
   * 为内容生成屏幕阅读器优化的结构
   * 转换内容为更易于屏幕阅读器理解的格式
   * @param content 原始HTML内容
   * @returns 优化后的HTML内容
   */
  public generateScreenReaderFriendlyContent(content: string): string {
    try {
      let optimizedContent = content;
      
      // 1. 增强标题的可访问性
      optimizedContent = optimizedContent.replace(
        /<h([1-6])>(.*?)<\/h\1>/gi,
        '<h$1 role="heading" aria-level="$1">$2</h$1>'
      );
      
      // 2. 增强图像的可访问性
      optimizedContent = optimizedContent.replace(
        /<img([^>]*)>/gi,
        (match, attributes) => {
          // 检查是否已经有alt属性
          if (!/alt\s*=\s*["'][^"']*["']/i.test(attributes)) {
            attributes += ' alt="图像"';
          }
          return `<img${attributes} role="img">`;
        }
      );
      
      // 3. 增强链接的可访问性
      optimizedContent = optimizedContent.replace(
        /<a([^>]*)>(.*?)<\/a>/gi,
        (match, attributes, content) => {
          if (!content.trim()) {
            content = '链接';
          }
          return `<a${attributes} role="link">${content}</a>`;
        }
      );
      
      // 4. 增强表格的可访问性
      optimizedContent = optimizedContent.replace(
        /<table([^>]*)>/gi,
        '<table$1 role="table">'
      );
      
      optimizedContent = optimizedContent.replace(
        /<th([^>]*)>/gi,
        '<th$1 scope="col">'
      );
      
      // 5. 增强列表的可访问性
      optimizedContent = optimizedContent.replace(
        /<ul([^>]*)>/gi,
        '<ul$1 role="list">'
      );
      
      optimizedContent = optimizedContent.replace(
        /<ol([^>]*)>/gi,
        '<ol$1 role="list">'
      );
      
      // 6. 替换纯图标按钮
      optimizedContent = optimizedContent.replace(
        /<button([^>]*)aria-label\s*=\s*["']([^"']*)["']([^>]*)>\s*<i[^>]*><\/i>\s*<\/button>/gi,
        '<button$1aria-label="$2"$3><i aria-hidden="true"></i> <span class="sr-only">$2</span></button>'
      );
      
      return optimizedContent;
    } catch (error) {
      logger.error('生成屏幕阅读器友好内容失败', { error });
      return content; // 出错时返回原内容
    }
  }
  
  /**
   * 为视障用户生成内容结构导航
   * @param content HTML内容
   * @returns 内容结构描述数组
   */
  public generateContentStructureNavigation(content: string): ElementDescription[] {
    try {
      const elementDescriptions: ElementDescription[] = [];
      
      // 提取标题
      const headings = content.match(/<h([1-6])[^>]*>(.*?)<\/h\1>/gi) || [];
      
      headings.forEach(heading => {
        const levelMatch = heading.match(/<h([1-6])/i);
        const level = levelMatch ? parseInt(levelMatch[1]) : 1;
        
        // 提取标题内容并去除HTML标签
        const textMatch = heading.match(/<h[1-6][^>]*>(.*?)<\/h[1-6]>/i);
        const text = textMatch ? textMatch[1].replace(/<[^>]*>/g, '') : '';
        
        elementDescriptions.push({
          type: 'header',
          label: text,
          importance: level <= 2 ? 'high' : 'medium'
        });
      });
      
      // 提取链接
      const links = content.match(/<a[^>]*>(.*?)<\/a>/gi) || [];
      
      links.forEach(link => {
        // 提取链接文本
        const textMatch = link.match(/<a[^>]*>(.*?)<\/a>/i);
        let text = textMatch ? textMatch[1].replace(/<[^>]*>/g, '') : '';
        
        // 如果链接文本为空或只包含图像，尝试获取aria-label或title
        if (!text.trim() || text.includes('img')) {
          const ariaLabelMatch = link.match(/aria-label\s*=\s*["']([^"']*)["']/i);
          const titleMatch = link.match(/title\s*=\s*["']([^"']*)["']/i);
          
          if (ariaLabelMatch) {
            text = ariaLabelMatch[1];
          } else if (titleMatch) {
            text = titleMatch[1];
          } else {
            text = '未命名链接';
          }
        }
        
        elementDescriptions.push({
          type: 'link',
          label: text,
          importance: 'medium'
        });
      });
      
      // 提取图像
      const images = content.match(/<img[^>]*>/gi) || [];
      
      images.forEach(image => {
        // 提取图像alt或title
        const altMatch = image.match(/alt\s*=\s*["']([^"']*)["']/i);
        const titleMatch = image.match(/title\s*=\s*["']([^"']*)["']/i);
        
        let description = '';
        if (altMatch) {
          description = altMatch[1];
        } else if (titleMatch) {
          description = titleMatch[1];
        } else {
          description = '未描述图像';
        }
        
        elementDescriptions.push({
          type: 'image',
          label: description,
          importance: 'medium'
        });
      });
      
      // 提取表单
      const forms = content.match(/<form[^>]*>/gi) || [];
      
      forms.forEach((form, index) => {
        elementDescriptions.push({
          type: 'form',
          label: `表单 ${index + 1}`,
          importance: 'high'
        });
      });
      
      return elementDescriptions;
    } catch (error) {
      logger.error('生成内容结构导航失败', { error });
      return []; // 出错时返回空数组
    }
  }
  
  /**
   * 生成内容的触觉探索版本（盲文或触觉图形的描述）
   * @param content 内容对象
   * @returns 触觉版本描述
   */
  public generateTactileVersionDescription(content: any): string {
    try {
      let tactileDescription = `触觉版本:${content.title || '内容'}。`;
      
      // 根据内容类型生成不同的触觉描述
      switch (content.type) {
        case ContentType.CHART:
          tactileDescription += '图表可通过触觉图形表示，包含';
          if (content.dataPoints && content.dataPoints.length > 0) {
            tactileDescription += `${content.dataPoints.length}个数据点，`;
            
            // 描述数据范围
            const values = content.dataPoints
              .map((p: any) => typeof p.value === 'number' ? p.value : 0);
            
            if (values.length > 0) {
              const min = Math.min(...values);
              const max = Math.max(...values);
              tactileDescription += `数值范围从${min}到${max}。`;
            }
          }
          break;
          
        case ContentType.IMAGE:
          tactileDescription += '图像可通过触觉图形表示，';
          if (content.alt) {
            tactileDescription += `描述为: ${content.alt}。`;
          }
          if (content.features && content.features.length > 0) {
            tactileDescription += '主要特征包括: ';
            const mainFeatures = content.features
              .filter((f: any) => f.importance === 'high')
              .map((f: any) => f.description);
            
            tactileDescription += mainFeatures.join('、') + '。';
          }
          break;
          
        case ContentType.ARTICLE:
          tactileDescription += '文章结构包含: ';
          if (content.structure) {
            const sections = content.structure.map((s: any) => s.title || '未命名章节');
            tactileDescription += sections.join('、') + '。';
          } else {
            tactileDescription += '正文内容。';
          }
          break;
          
        default:
          tactileDescription += '内容可以通过文本盲文阅读。';
      }
      
      // 添加交互提示
      tactileDescription += '可通过触摸探索细节，或使用盲文阅读器浏览完整内容。';
      
      return tactileDescription;
    } catch (error) {
      logger.error('生成触觉版本描述失败', { error, contentType: content.type });
      return `触觉版本:${content.title || '内容'}。可通过盲文阅读器浏览。`;
    }
  }
}

export default new VisionImpairedContentService();