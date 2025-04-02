import { SmellAnalysisResult, SmellDiagnosisRequest, SmellDiagnosisResult, SmellDiagnosisType, SmellType, TcmImplication } from '../interfaces/smell-diagnosis.interface';
import { v4 as uuidv4 } from 'uuid';

/**
 * 气息分析结果模型
 */
export class SmellAnalysisResultModel implements SmellAnalysisResult {
  id: string;
  userId: string;
  timestamp: Date;
  smellType: SmellType;
  intensity: number;
  description: string;
  relatedConditions: string[];
  confidence: number;
  rawData?: any;
  metadata?: Record<string, any>;

  constructor(data: Partial<SmellAnalysisResult>) {
    this.id = data.id || uuidv4();
    this.userId = data.userId || '';
    this.timestamp = data.timestamp || new Date();
    this.smellType = data.smellType || SmellType.NORMAL;
    this.intensity = data.intensity || 0;
    this.description = data.description || '';
    this.relatedConditions = data.relatedConditions || [];
    this.confidence = data.confidence || 0;
    this.rawData = data.rawData;
    this.metadata = data.metadata;
  }

  /**
   * 将模型转换为JSON对象
   */
  toJSON(): Record<string, any> {
    return {
      id: this.id,
      userId: this.userId,
      timestamp: this.timestamp,
      smellType: this.smellType,
      intensity: this.intensity,
      description: this.description,
      relatedConditions: this.relatedConditions,
      confidence: this.confidence,
      ...(this.rawData ? { rawData: this.rawData } : {}),
      ...(this.metadata ? { metadata: this.metadata } : {})
    };
  }

  /**
   * 从JSON对象创建模型
   */
  static fromJSON(json: Record<string, any>): SmellAnalysisResultModel {
    return new SmellAnalysisResultModel({
      id: json.id,
      userId: json.userId,
      timestamp: new Date(json.timestamp),
      smellType: json.smellType,
      intensity: json.intensity,
      description: json.description,
      relatedConditions: json.relatedConditions,
      confidence: json.confidence,
      rawData: json.rawData,
      metadata: json.metadata
    });
  }
}

/**
 * 闻诊结果模型
 */
export class SmellDiagnosisResultModel implements SmellDiagnosisResult {
  id: string;
  userId: string;
  requestId: string;
  timestamp: Date;
  diagnosisType: SmellDiagnosisType;
  analysisResults: SmellAnalysisResult[];
  tcmImplications: TcmImplication[];
  recommendations: string[];
  confidence: number;
  metadata?: Record<string, any>;

  constructor(data: Partial<SmellDiagnosisResult>) {
    this.id = data.id || uuidv4();
    this.userId = data.userId || '';
    this.requestId = data.requestId || '';
    this.timestamp = data.timestamp || new Date();
    this.diagnosisType = data.diagnosisType || SmellDiagnosisType.BREATH;
    this.analysisResults = data.analysisResults || [];
    this.tcmImplications = data.tcmImplications || [];
    this.recommendations = data.recommendations || [];
    this.confidence = data.confidence || 0;
    this.metadata = data.metadata;
  }

  /**
   * 将模型转换为JSON对象
   */
  toJSON(): Record<string, any> {
    return {
      id: this.id,
      userId: this.userId,
      requestId: this.requestId,
      timestamp: this.timestamp,
      diagnosisType: this.diagnosisType,
      analysisResults: this.analysisResults.map(result => 
        result instanceof SmellAnalysisResultModel 
          ? result.toJSON() 
          : result
      ),
      tcmImplications: this.tcmImplications,
      recommendations: this.recommendations,
      confidence: this.confidence,
      ...(this.metadata ? { metadata: this.metadata } : {})
    };
  }

  /**
   * 从JSON对象创建模型
   */
  static fromJSON(json: Record<string, any>): SmellDiagnosisResultModel {
    return new SmellDiagnosisResultModel({
      id: json.id,
      userId: json.userId,
      requestId: json.requestId,
      timestamp: new Date(json.timestamp),
      diagnosisType: json.diagnosisType,
      analysisResults: json.analysisResults.map((result: any) => 
        SmellAnalysisResultModel.fromJSON(result)
      ),
      tcmImplications: json.tcmImplications,
      recommendations: json.recommendations,
      confidence: json.confidence,
      metadata: json.metadata
    });
  }
} 