/**
 * 四诊协调服务接口定义
 */

export interface ICoordinatorRequest {
  sessionId: string;
  userId: string;
  diagnosisId: string;
  diagnosisType: 'inquiry';
  diagnosisData: Record<string, any>;
  timestamp: Date;
  metadata?: Record<string, any>;
}

export interface ICoordinatorResponse {
  success: boolean;
  coordinationId: string;
  integratedResults?: Record<string, any>;
  message?: string;
  status?: string;
  timestamp?: Date;
}

export interface ICoordinatorWebhookPayload {
  coordinationId: string;
  sessionId: string;
  userId: string;
  diagnosisIds: string[];
  integratedResults: {
    tcmPatterns: Array<{
      name: string;
      confidence: number;
      description?: string;
    }>;
    constitutionAnalysis: {
      primaryType: string;
      secondaryTypes: string[];
      description?: string;
      score?: Record<string, number>;
    };
    recommendations: Array<{
      category: string;
      content: string;
      importance: 'high' | 'medium' | 'low';
    }>;
    summary: string;
  };
  timestamp: Date;
} 