/**
 * 五诊算法系统使用示例
 * 
 * 展示如何使用索克生活五诊算法系统进行中医诊断分析
 * 
 * @author 索克生活技术团队
 * @version 1.0.0
 */

import { FiveDiagnosisEngine, DiagnosisInput, ImageData } from '../FiveDiagnosisEngine';

/**
 * 五诊算法系统使用示例类
 */
export class FiveDiagnosisExample {
  private engine: FiveDiagnosisEngine;

  constructor() {
    // 创建五诊引擎（使用默认配置）
    this.engine = new FiveDiagnosisEngine();
  }

  /**
   * 创建示例图像数据
   */
  private createSampleImageData(): ImageData {
    // 创建一个简单的示例图像数据
    const width = 100;
    const height = 100;
    const data = new ArrayBuffer(width * height * 4); // RGBA
    
    return {
      data,
      format: 'rgba',
      width,
      height,
    };
  }

  /**
   * 完整的五诊分析示例
   */
  public async runCompleteDiagnosisExample(): Promise<void> {
    console.log('=== 索克生活五诊算法系统示例 ===\n');

    // 准备诊断输入数据
    const diagnosisInput: DiagnosisInput = {
      userId: 'user_12345',
      sessionId: 'session_67890',
      timestamp: Date.now(),
      
      // 望诊数据
      lookingData: {
        tongueImage: this.createSampleImageData(),
        faceImage: this.createSampleImageData(),
        bodyImage: this.createSampleImageData(),
        metadata: {
          lighting: 'natural',
          temperature: 25,
          humidity: 60,
          captureTime: new Date().toISOString(),
        },
      },

      // 算诊数据
      calculationData: {
        birthDate: '1990-05-15',
        birthTime: '08:30',
        birthPlace: '北京市',
        currentDate: '2024-12-19',
        currentTime: '14:30',
        currentLocation: '上海市',
      },

      // 用户基本信息
      userProfile: {
        age: 34,
        gender: 'male',
        height: 175,
        weight: 70,
        occupation: '软件工程师',
        medicalHistory: ['高血压家族史'],
        allergies: ['花粉过敏'],
        medications: [],
      },
    };

    try {
      console.log('🔍 开始五诊分析...\n');

      // 执行五诊分析
      const result = await this.engine.analyze(diagnosisInput);

      // 显示分析结果
      this.displayResults(result);

    } catch (error) {
      console.error('❌ 五诊分析失败:', error);
    }
  }

  /**
   * 单独的望诊分析示例
   */
  public async runLookingDiagnosisExample(): Promise<void> {
    console.log('=== 望诊分析示例 ===\n');

    const lookingInput: DiagnosisInput = {
      userId: 'user_12345',
      sessionId: 'session_looking',
      timestamp: Date.now(),
      lookingData: {
        tongueImage: this.createSampleImageData(),
        faceImage: this.createSampleImageData(),
        bodyImage: this.createSampleImageData(),
        metadata: {
          lighting: 'natural',
          temperature: 25,
          humidity: 60,
          captureTime: new Date().toISOString(),
        },
      },
    };

    try {
      const result = await this.engine.analyze(lookingInput);
      console.log('👁️ 望诊分析完成');
      console.log('置信度:', result.confidence);
      console.log('整体评估:', result.overallAssessment);
    } catch (error) {
      console.error('❌ 望诊分析失败:', error);
    }
  }

  /**
   * 单独的算诊分析示例
   */
  public async runCalculationDiagnosisExample(): Promise<void> {
    console.log('=== 算诊分析示例 ===\n');

    const calculationInput: DiagnosisInput = {
      userId: 'user_12345',
      sessionId: 'session_calculation',
      timestamp: Date.now(),
      calculationData: {
        birthDate: '1990-05-15',
        birthTime: '08:30',
        birthPlace: '北京市',
        currentDate: '2024-12-19',
        currentTime: '14:30',
        currentLocation: '上海市',
      },
      userProfile: {
        age: 34,
        gender: 'male',
        height: 175,
        weight: 70,
        occupation: '软件工程师',
        medicalHistory: [],
        allergies: [],
        medications: [],
      },
    };

    try {
      const result = await this.engine.analyze(calculationInput);
      console.log('🧮 算诊分析完成');
      console.log('置信度:', result.confidence);
      console.log('整体评估:', result.overallAssessment);
      if (result.diagnosisResults.calculation) {
        console.log('算诊结果:', result.diagnosisResults.calculation.analysis);
      }
    } catch (error) {
      console.error('❌ 算诊分析失败:', error);
    }
  }

  /**
   * 显示分析结果
   */
  private displayResults(result: any): void {
    console.log('📊 === 五诊分析结果 ===\n');

    // 基本信息
    console.log('🔸 基本信息:');
    console.log(`  置信度: ${(result.confidence * 100).toFixed(1)}%`);
    console.log(`  分析时间: ${new Date(result.timestamp).toLocaleString()}`);
    console.log(`  会话ID: ${result.sessionId}`);
    console.log('');

    // 整体评估
    if (result.overallAssessment) {
      console.log('🔸 整体评估:');
      console.log(`  ${result.overallAssessment}`);
      console.log('');
    }

    // 诊断结果
    if (result.diagnosisResults) {
      console.log('🔸 各诊法结果:');
      
      if (result.diagnosisResults.looking) {
        console.log(`  望诊: ${result.diagnosisResults.looking.analysis}`);
      }
      
      if (result.diagnosisResults.calculation) {
        console.log(`  算诊: ${result.diagnosisResults.calculation.analysis}`);
      }
      
      console.log('');
    }

    // 融合分析结果
    if (result.fusionResult) {
      console.log('🔸 融合分析:');
      console.log(`  置信度: ${(result.fusionResult.confidence * 100).toFixed(1)}%`);
      console.log(`  评估: ${result.fusionResult.overallAssessment}`);
      
      if (result.fusionResult.primarySyndromes && result.fusionResult.primarySyndromes.length > 0) {
        console.log('  主要证候:');
        result.fusionResult.primarySyndromes.forEach((syndrome: any, index: number) => {
          console.log(`    ${index + 1}. ${syndrome.name} (置信度: ${(syndrome.confidence * 100).toFixed(1)}%)`);
        });
      }
      
      console.log('');
    }

    // 体质分析
    if (result.fusionResult?.constitutionAnalysis) {
      const constitution = result.fusionResult.constitutionAnalysis;
      console.log('🔸 体质分析:');
      console.log(`  主要体质: ${constitution.primaryType}`);
      if (constitution.secondaryTypes && constitution.secondaryTypes.length > 0) {
        console.log(`  次要体质: ${constitution.secondaryTypes.join(', ')}`);
      }
      console.log(`  置信度: ${(constitution.confidence * 100).toFixed(1)}%`);
      console.log('');
    }

    // 健康建议
    if (result.fusionResult?.recommendations && result.fusionResult.recommendations.length > 0) {
      console.log('🔸 健康建议:');
      result.fusionResult.recommendations.forEach((recommendation: any, index: number) => {
        console.log(`  ${index + 1}. [${recommendation.category}] ${recommendation.title}`);
        console.log(`     ${recommendation.description}`);
      });
      console.log('');
    }

    // 注意事项
    if (result.qualityReport?.warnings && result.qualityReport.warnings.length > 0) {
      console.log('⚠️ 注意事项:');
      result.qualityReport.warnings.forEach((warning: string, index: number) => {
        console.log(`  ${index + 1}. ${warning}`);
      });
      console.log('');
    }

    // 质量评估
    if (result.qualityReport) {
      console.log('🔸 质量评估:');
      console.log(`  数据质量: ${(result.qualityReport.score * 100).toFixed(1)}%`);
      console.log(`  可靠性: ${result.qualityReport.valid ? '可靠' : '需要改进'}`);
      console.log('');
    }

    console.log('✅ 五诊分析完成！\n');
  }

  /**
   * 清理资源
   */
  public async cleanup(): Promise<void> {
    await this.engine.cleanup();
    console.log('🧹 资源清理完成');
  }
}

/**
 * 运行示例
 */
export async function runFiveDiagnosisExamples(): Promise<void> {
  const example = new FiveDiagnosisExample();

  try {
    // 运行完整的五诊分析示例
    await example.runCompleteDiagnosisExample();

    console.log('\n' + '='.repeat(50) + '\n');

    // 运行单独的望诊示例
    await example.runLookingDiagnosisExample();

    console.log('\n' + '='.repeat(50) + '\n');

    // 运行单独的算诊示例
    await example.runCalculationDiagnosisExample();

  } catch (error) {
    console.error('示例运行失败:', error);
  } finally {
    // 清理资源
    await example.cleanup();
  }
} 