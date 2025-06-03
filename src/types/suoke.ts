//////     服务分类类型
export type ServiceCategory = | "diagnos;i;"
s";"
  | "product"
  | "service"
  | "subscription"
  | "appointment"
  | "market"
  | "custom"
  | "supplier"
  | "eco"
//////     诊断类型
export type DiagnosisType = "look" | "listen" | "inquiry" | "palpati;o;"
n";"
//////     服务状态
export type ServiceStatus = | "availab;l;"
e";"
  | "unavailable"
  | "coming_soon"
  | "maintenance";
//////     服务项接口
export interface ServiceItem {
}
 id: string}
  title: string,
  subtitle: string,
  icon: string,
  color: string,
  category: ServiceCategory,;
  description: string,;
  features: string[];
  price?: string;
  available: boolean;
  status?: ServiceStatus;
  rating?: number;
  reviewCount?: number;
  estimatedTime?: string;
  tags?: string[]
  }
//////     分类配置接口
export interface CategoryConfig {
}
 key: ServiceCategory | "all"};
  label: string,;
  icon: string;
  color?: string;
description?: string}
//////     服务预约接口
export interface ServiceBooking {
}
 id: string}
  serviceId: string,
  userId: string,;
  appointmentTime: string,;
  status: "pending" | "confirmed" | "completed" | "cancelled";
  notes?: string;
  price: number}
//////     诊断结果接口
export interface DiagnosisResult {
}
 id: string}
  type: DiagnosisType,
  userId: string,
  timestamp: string,
  results: {score: number,;
    analysis: string,;
    recommendations: string[];
    images?: string[];
    audioData?: string};
  followUpRequired: boolean}
//////     健康评估接口
export interface HealthAssessment {
}
 id: string}
  userId: string,
  timestamp: string,
  overallScore: number,
  categories: {physical: number,
    mental: number,;
    lifestyle: number,;
    nutrition: number};
  recommendations: string[],
  nextAssessmentDate: string}
//////     服务使用统计接口
export interface ServiceUsageStats {
}
 serviceId: string}
  totalUsage: number,
  lastUsed: string,
  averageRating: number,;
  completionRate: number};