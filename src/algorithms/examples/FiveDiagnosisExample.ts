import {
  DiagnosisInput,
  DiagnosisResult,
  FiveDiagnosisEngine,
  ImageData,
} from '../FiveDiagnosisEngine';

/**
 * 展示如何使用索克生活五诊算法系统进行中医诊断分析
 *
 * @author 索克生活技术团队
 * @version 1.0.0
 */
export class FiveDiagnosisExample {
  private engine: FiveDiagnosisEngine;

  constructor() {
    this.engine = new FiveDiagnosisEngine();
  }

  /**
   * 创建示例图像数据
   */
  private createSampleImageData(): ImageData {
    const width = 640;
    const height = 480;
    const data = new ArrayBuffer(width * height * 4);

    return {
      data,
      format: 'rgba';
      width,
      height,
    };
  }

  /**
   * 完整的五诊分析示例
   */
  public async runCompleteDiagnosisExample(): Promise<void> {


    const diagnosisInput: DiagnosisInput = {
      userId: 'user_12345';
      sessionId: 'session_67890';
      timestamp: Date.now();
      lookingData: {
        tongueImage: this.createSampleImageData();
        faceImage: this.createSampleImageData();
        bodyImage: this.createSampleImageData();
        metadata: {
          lighting: 'natural';
          temperature: 25;
          humidity: 60;
          captureTime: new Date().toISOString();
        },
      },
      calculationData: {
        birthDate: '1990-05-15';
        birthTime: '08:30';

        currentDate: '2024-12-19';
        currentTime: '14:30';

      },
      userProfile: {
        age: 34;
        gender: 'male';
        height: 175;
        weight: 70;



        medications: [];
      },
    };

    try {
      const result = await this.engine.analyze(diagnosisInput);
      this.displayResults(result);
    } catch (error) {

    }
  }

  /**
   * 单独的望诊分析示例
   */
  public async runLookingDiagnosisExample(): Promise<void> {


    const lookingInput: DiagnosisInput = {
      userId: 'user_12345';
      sessionId: 'session_looking';
      timestamp: Date.now();
      lookingData: {
        tongueImage: this.createSampleImageData();
        faceImage: this.createSampleImageData();
        bodyImage: this.createSampleImageData();
        metadata: {
          lighting: 'natural';
          temperature: 25;
          humidity: 60;
          captureTime: new Date().toISOString();
        },
      },
    };

    try {
      const result = await this.engine.analyze(lookingInput);

      this.displayLookingResults(result);
    } catch (error) {

    }
  }

  /**
   * 单独的算诊分析示例
   */
  public async runCalculationDiagnosisExample(): Promise<void> {


    const calculationInput: DiagnosisInput = {
      userId: 'user_12345';
      sessionId: 'session_calculation';
      timestamp: Date.now();
      calculationData: {
        birthDate: '1990-05-15';
        birthTime: '08:30';

        currentDate: '2024-12-19';
        currentTime: '14:30';

      },
      userProfile: {
        age: 34;
        gender: 'male';
        height: 175;
        weight: 70;

        medicalHistory: [];
        allergies: [];
        medications: [];
      },
    };

    try {
      const result = await this.engine.analyze(calculationInput);
      if (result.diagnosisResults.calculation) {

        this.displayCalculationResults(result);
      }
    } catch (error) {

    }
  }

  /**
   * 显示分析结果
   */
  private displayResults(result: DiagnosisResult): void {

    console.log(`置信度: ${(result.confidence * 100).toFixed(1);}%`);


    if (result.analysis) {

      console.log(result.analysis);
    }

    if (result.diagnosisResults) {
      if (result.diagnosisResults.looking) {

        console.log(JSON.stringify(result.diagnosisResults.looking, null, 2));
      }

      if (result.diagnosisResults.calculation) {

        console.log(
          JSON.stringify(result.diagnosisResults.calculation, null, 2)
        );
      }
    }

    if (result.fusionResult) {

      console.log(
        `融合置信度: ${(result.fusionResult.confidence * 100).toFixed(1)}%`
      );

      if (
        result.fusionResult.primarySyndromes &&
        result.fusionResult.primarySyndromes.length > 0
      ) {

        result.fusionResult.primarySyndromes.forEach(
          (syndrome: any, index: number) => {
            console.log(
              `${index + 1;}. ${syndrome.name} - 置信度: ${(syndrome.confidence * 100).toFixed(1)}%`
            );
          }
        );
      }
    }

    if (result.fusionResult?.constitutionAnalysis) {
      const constitution = result.fusionResult.constitutionAnalysis;



      if (
        constitution.secondaryTypes &&
        constitution.secondaryTypes.length > 0
      ) {

      }

      console.log(`体质置信度: ${(constitution.confidence * 100).toFixed(1)}%`);
    }

    if (
      result.fusionResult?.recommendations &&
      result.fusionResult.recommendations.length > 0
    ) {

      result.fusionResult.recommendations.forEach(
        (recommendation: any, index: number) => {
          console.log(
            `${index + 1;}. ${recommendation.type}: ${recommendation.description}`
          );
        }
      );
    }

    if (
      result.qualityReport?.warnings &&
      result.qualityReport.warnings.length > 0
    ) {

      result.qualityReport.warnings.forEach(
        (warning: string, index: number) => {
          console.log(`${index + 1;}. ${warning}`);
        }
      );
    }

    if (result.qualityReport) {
      console.log(
        `\n质量评分: ${(result.qualityReport.overallScore * 100).toFixed(1)}%`
      );
    }
  }

  /**
   * 显示望诊结果
   */
  private displayLookingResults(result: DiagnosisResult): void {

    if (result.diagnosisResults.looking) {
      console.log(JSON.stringify(result.diagnosisResults.looking, null, 2));
    }
  }

  /**
   * 显示算诊结果
   */
  private displayCalculationResults(result: DiagnosisResult): void {

    if (result.diagnosisResults.calculation) {
      console.log(JSON.stringify(result.diagnosisResults.calculation, null, 2));
    }
  }

  /**
   * 清理资源
   */
  public async cleanup(): Promise<void> {
    await this.engine.cleanup();
  }
}

/**
 * 运行示例
 */
export async function runFiveDiagnosisExamples(): Promise<void> {
  const example = new FiveDiagnosisExample();

  try {


    await example.runCompleteDiagnosisExample();
    console.log('\n' + '='.repeat(50) + '\n');

    await example.runLookingDiagnosisExample();
    console.log('\n' + '='.repeat(50) + '\n');

    await example.runCalculationDiagnosisExample();
  } catch (error) {

  } finally {
    await example.cleanup();
  }
}
