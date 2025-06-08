export interface DiagnosisStep {
  id: string;
  title: string;
  description: string;
  icon: string;
  component: React.ComponentType<DiagnosisComponentProps>;
}

export interface DiagnosisComponentProps {
  onComplete: (data: any) => void;
  onCancel: () => void;
}

export interface DiagnosisInput {
  lookData?: any;
  listenData?: any;
  inquiryData?: any;
  palpationData?: any;
  calculationData?: any;
  timestamp: number;
}

export interface FiveDiagnosisResult {
  sessionId: string;
  userId: string;
  timestamp: string;
  overallConfidence: number;
  primarySyndrome: {
    name: string;
    confidence: number;
    description: string;
  };
  constitutionType: {
    type: string;
    characteristics: string[];
    recommendations: string[];
  };
  diagnosticResults: {
    look?: DiagnosisResult;
    listen?: DiagnosisResult;
    inquiry?: DiagnosisResult;
    palpation?: DiagnosisResult;
    calculation?: DiagnosisResult;
  };
  fusionAnalysis: {
    evidenceStrength: number;
    syndromePatterns: string[];
    riskFactors: string[];
  };
  healthRecommendations: {
    lifestyle: string[];
    diet: string[];
    exercise: string[];
    treatment: string[];
    prevention: string[];
  };
  qualityMetrics: {
    dataQuality: number;
    resultReliability: number;
    completeness: number;
  };
  overallAssessment: string;
}

export interface DiagnosisResult {
  type: string;
  confidence: number;
  findings: string[];
  recommendations: string[];
  timestamp: string;
}

export interface LookDiagnosisData {
  faceImage?: string;
  tongueImage?: string;
  bodyImage?: string;
  metadata?: any;
}

export interface ListenDiagnosisData {
  voiceRecording?: string;
  breathingPattern?: any;
  coughSound?: string;
  metadata?: any;
}

export interface InquiryDiagnosisData {
  symptoms: string[];
  medicalHistory: string[];
  lifestyle: any;
  currentSymptoms?: string[];
  painLevel?: number;
  duration?: string;
}

export interface PalpationDiagnosisData {
  pulseData: number[];
  touchData?: any;
  temperatureData?: any;
  pressureData?: any;
  metadata?: any;
}

export interface CalculationDiagnosisData {
  personalInfo: {
    birthYear: number;
    birthMonth: number;
    birthDay: number;
    birthHour: number;
    gender: string;
    location: string;
  };
  analysisTypes: {
    ziwuLiuzhu: boolean;
    constitution: boolean;
    bagua: boolean;
    wuyunLiuqi: boolean;
    comprehensive: boolean;
  };
  currentTime: string;
  healthConcerns: string[];
} 