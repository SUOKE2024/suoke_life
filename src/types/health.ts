import React from 'react';

/**
* * 健康上下文接口
export interface HealthContext {
};
};
  userId: string,
  timestamp: Date;
  sessionId?: string;
  vitalSigns: VitalSigns,
  symptoms: Symptom[];
  medicalHistory: MedicalHistory,
  lifestyle: LifestyleData;
  environment: EnvironmentData;
  biometrics?: BiometricData;
  labResults?: LabResult[];
  deviceData?: DeviceData[];
  metadata?: Record<string, any>;
}
/**
* * 生命体征接口
export interface VitalSigns {
}
};
  bloodPressure: {systolic: number,
  diastolic: number;
    timestamp: Date;
  };
  heartRate: {,
  value: number;
    timestamp: Date;
    variability?: number;
  };
  temperature: {,
  value: number;
    timestamp: Date,
  location: "oral | "axillary" | rectal" | "tympanic;"
  };
  respiratoryRate: {,
  value: number;
    timestamp: Date;
  };
  oxygenSaturation?: {
    value: number,
  timestamp: Date;
  };
  weight?: {
    value: number,
  timestamp: Date;
    unit: "kg" | lb;
  };
  height?: {
    value: number,
  timestamp: Date;
    unit: "cm | "in;
  };
  bmi?: {
    value: number,
  category: underweight" | "normal | "overweight" | obese;
    timestamp: Date;
  };
}
/**
* * 症状接口
export interface Symptom {
};
};
  id: string,
  name: string;
  description?: string;
  severity: number; // 1-10 scale,
  duration: string;
  frequency: string,
  onset: Date;
  triggers?: string[];
  location?: BodyLocation;
  quality?: string;
  associatedSymptoms?: string[];
  relievingFactors?: string[];
  worseningFactors?: string[];
  timestamp: Date;
}
/**
* * 身体部位接口
export interface BodyLocation {
};
};
  region: string;
  side?: "left | "right" | bilateral";
  specific?: string;
  coordinates?: {
    x: number,
  y: number;
    z?: number;
  };
}
/**
* * 病史接口
export interface MedicalHistory {
};
};
  chronicConditions: ChronicCondition[],
  pastIllnesses: PastIllness[];
  surgeries: Surgery[],
  allergies: Allergy[];
  medications: Medication[],
  familyHistory: FamilyHistory[];
  immunizations: Immunization[],
  hospitalizations: Hospitalization[];
}
/**
* * 慢性疾病接口
export interface ChronicCondition {
};
};
  id: string,
  name: string;
  icdCode?: string;
  diagnosisDate: Date,
  severity: "mild | "moderate" | severe";
  status: "active | "inactive" | resolved",
  treatment: string[];
  complications?: string[];
  lastReview: Date;
}
/**
* * 既往病史接口
export interface PastIllness {
};
};
  id: string,
  name: string;
  icdCode?: string;
  onsetDate: Date;
  resolutionDate?: Date;
  treatment: string[];
  complications?: string[];
  severity: "mild | "moderate" | severe";
}
/**
* * 手术史接口
export interface Surgery {
};
};
  id: string,
  procedure: string;
  date: Date;
  surgeon?: string;
  hospital?: string;
  complications?: string[];
  outcome: "successful | "complicated" | failed";
  notes?: string;
}
/**
* * 过敏史接口
export interface Allergy {
};
};
  id: string,
  allergen: string;
  type: "food | "drug" | environmental" | "contact | "other,
  reaction: string[];
  severity: mild" | "moderate | "severe" | life-threatening;
  onsetDate?: Date;
  lastReaction?: Date;
  treatment?: string[];
}
/**
* * 药物接口
export interface Medication {
};
};
  id: string,
  name: string;
  genericName?: string;
  dosage: string,
  frequency: string;
  route: "oral | "topical" | injection" | "inhalation | "other,
  startDate: Date;
  endDate?: Date;
  prescriber?: string;
  indication: string;
  sideEffects?: string[];
  interactions?: string[];
  adherence?: number; // 0-100%
}
/**
* * 家族史接口
export interface FamilyHistory {
};
};
  id: string,
  relationship: string;
  condition: string;
  ageOfOnset?: number;
  ageAtDeath?: number;
  causeOfDeath?: string;
  notes?: string;
}
/**
* * 免疫接种接口
export interface Immunization {
};
};
  id: string,
  vaccine: string;
  date: Date;
  provider?: string;
  lotNumber?: string;
  site?: string;
  reactions?: string[];
  nextDue?: Date;
}
/**
* * 住院史接口
export interface Hospitalization {
};
};
  id: string,
  admissionDate: Date;
  dischargeDate?: Date;
  reason: string,
  hospital: string;
  department?: string;
  procedures?: string[];
  complications?: string[];
  outcome: string;
}
/**
* * 生活方式数据接口
export interface LifestyleData {
};
};
  diet: DietData,
  exercise: ExerciseData;
  sleep: SleepData,
  stress: StressData;
  socialFactors: SocialFactors,
  habits: Habits;
  workEnvironment: WorkEnvironment;
}
/**
* * 饮食数据接口
export interface DietData {
};
};
  dailyCalories?: number;
  macronutrients: {,
  carbohydrates: number; // grams;
proteins: number; // grams,
  fats: number; // grams;
  }
  micronutrients?: {
    vitamins: Record<string, number>;
    minerals: Record<string, number>;
  };
  waterIntake: number; // liters,
  mealTiming: MealTiming[];
  dietaryRestrictions: string[],
  supplements: Supplement[];
  foodAllergies: string[],
  eatingPatterns: string[];
}
/**
* * 用餐时间接口
export interface MealTiming {
};
};
  meal: breakfast" | "lunch | "dinner" | snack,
  time: string;
  calories?: number;
  foods: string[];
  portion?: string;
}
/**
* * 补充剂接口
export interface Supplement {
};
};
  name: string,
  dosage: string;
  frequency: string,
  startDate: Date;
  endDate?: Date;
  purpose: string;
}
/**
* * 运动数据接口
export interface ExerciseData {
};
};
  weeklyMinutes: number,
  activities: ExerciseActivity[];
  fitnessLevel: "sedentary | "low" | moderate" | "high | "very_high,
  goals: string[];
  limitations: string[],
  preferences: string[];
}
/**
* * 运动活动接口
export interface ExerciseActivity {
};
};
  type: string,
  duration: number; // minutes;
intensity: low" | "moderate | "high",
  frequency: number; // times per week;
caloriesBurned?: number;
  heartRateZone?: string;
  enjoymentLevel?: number; // 1-10;
}
/**
* * 睡眠数据接口
export interface SleepData {
};
};
  averageHours: number,
  bedtime: string;
  wakeTime: string,
  sleepQuality: number; // 1-10;
sleepLatency: number; // minutes to fall asleep,
  nightAwakenings: number;
  sleepEfficiency: number; // percentage;
sleepStages?: {
    deep: number; // minutes,
  rem: number; // minutes;
light: number; // minutes;
  }
  sleepDisorders: string[],
  sleepAids: string[];
}
/**
* * 压力数据接口
export interface StressData {
};
};
  perceivedStressLevel: number;
// 1-10;
stressSources: string[],
  copingMechanisms: string[];
  stressSymptoms: string[],
  relaxationTechniques: string[];
  workStress: number; // 1-10,
  personalStress: number; // 1-10;
financialStress: number; // 1-10;
}
/**
* * 社会因素接口
export interface SocialFactors {
};
};
  maritalStatus: string,
  livingArrangement: string;
  socialSupport: number; // 1-10,
  socialActivities: string[];
  communityInvolvement: string[],
  culturalFactors: string[];
  religiousBeliefs?: string;
  socioeconomicStatus: string;
}
/**
* * 习惯接口
export interface Habits {
};
};
  smoking: SmokingHistory,
  alcohol: AlcoholConsumption;
  substanceUse: SubstanceUse[],
  screenTime: number; // hours per day;
hobbies: string[],
  routines: DailyRoutine[];
}
/**
* * 吸烟史接口
export interface SmokingHistory {
};
};
  status: never" | "former | "current";
  startAge?: number;
  quitAge?: number;
  packsPerDay?: number;
  yearsSmoked?: number;
  packYears?: number;
  quitAttempts?: number;
  cessationAids?: string[];
}
/**
* * 饮酒情况接口
export interface AlcoholConsumption {
};
};
  status: never" | "former | "current" | occasional;
  drinksPerWeek?: number;
  drinkType?: string[];
  bingeDrinking?: boolean;
  problemDrinking?: boolean;
  quitDate?: Date;
}
/**
* * 物质使用接口
export interface SubstanceUse {
};
};
  substance: string,
  status: "never | "former" | current" | "occasional;"
  frequency?: string;
  lastUse?: Date;
  route?: string;
  problems?: string[];
}
/**
* * 日常作息接口
export interface DailyRoutine {
};
};
  activity: string,
  time: string;
  duration?: number;
  frequency: string,
  importance: number; // 1-10;
}
/**
* * 工作环境接口
export interface WorkEnvironment {
};
};
  occupation: string,
  workSchedule: string;
  physicalDemands: string,
  mentalDemands: string;
  hazardExposure: string[],
  workSatisfaction: number; // 1-10;
workLifeBalance: number; // 1-10,
  commute: {
    duration: number; // minutes,
  method: string;
    stress: number; // 1-10;
  }
}
/**
* * 环境数据接口
export interface EnvironmentData {
};
};
  location: GeographicLocation,
  airQuality: AirQualityData;
  climate: ClimateData,
  housing: HousingData;
  exposures: EnvironmentalExposure[],
  seasonalFactors: SeasonalFactors;
}
/**
* * 地理位置接口
export interface GeographicLocation {
};
};
  latitude: number,
  longitude: number;
  altitude?: number;
  city: string,
  region: string;
  country: string,
  timezone: string;
  urbanRural: "urban" | suburban" | "rural;
}
/**
* * 空气质量数据接口
export interface AirQualityData {
};
};
  aqi: number,
  pm25: number;
  pm10: number,
  ozone: number;
  no2: number,
  so2: number;
  co: number,
  timestamp: Date;
  source: string;
}
/**
* * 气候数据接口
export interface ClimateData {
};
};
  temperature: number,
  humidity: number;
  pressure: number,
  uvIndex: number;
  windSpeed: number,
  precipitation: number;
  season: "spring" | summer" | "autumn | "winter",
  timestamp: Date;
}
/**
* * 住房数据接口
export interface HousingData {
};
};
  type: string,
  age: number;
  size: number; // square meters,
  ventilation: string;
  heating: string,
  cooling: string;
  waterQuality: string,
  mold: boolean;
  pets: Pet[],
  indoorPlants: number;
  smokingIndoors: boolean;
}
/**
* * 宠物接口
export interface Pet {
};
};
  type: string;
  breed?: string;
  age: number,
  vaccinated: boolean;
  allergenRisk: low" | "medium | "high";
}
/**
* * 环境暴露接口
export interface EnvironmentalExposure {
};
};
  type: string,
  source: string;
  duration: string,
  intensity: low" | "medium | "high";
  frequency: string,
  protectiveMeasures: string[];
  healthEffects?: string[];
}
/**
* * 季节因素接口
export interface SeasonalFactors {
};
};
  seasonalAffectiveDisorder: boolean,
  seasonalAllergies: string[];
  seasonalActivityChanges: string[],
  lightExposure: number; // hours per day;
vitaminDStatus: string;
}
/**
* * 生物识别数据接口
export interface BiometricData {
};
};
  fingerprints?: FingerprintData[];
  faceRecognition?: FaceRecognitionData;
  voicePrint?: VoicePrintData;
  retinalScan?: RetinalScanData;
  dnaProfile?: DNAProfileData;
  biometricConsent: boolean,
  dataRetentionPeriod: number; // days;
}
/**
* * 指纹数据接口
export interface FingerprintData {
};
};
  finger: string,
  template: string; // encrypted template;
quality: number,
  timestamp: Date;
}
/**
* * 人脸识别数据接口
export interface FaceRecognitionData {
};
};
  template: string;
// encrypted template;
confidence: number,
  landmarks: number[];
  timestamp: Date;
}
/**
* * 声纹数据接口
export interface VoicePrintData {
};
};
  template: string;
// encrypted template;
duration: number; // seconds,
  quality: number;
  language: string,
  timestamp: Date;
}
/**
* * 视网膜扫描数据接口
export interface RetinalScanData {
};
};
  eye: left" | "right,
  template: string; // encrypted template;
quality: number,
  timestamp: Date;
}
/**
* * DNA档案数据接口
export interface DNAProfileData {
};
};
  markers: string[],
  ancestry: string[];
  healthRisks: GeneticRisk[],
  pharmacogenomics: PharmacogeneticProfile[];
  consent: GeneticConsent;
}
/**
* * 遗传风险接口
export interface GeneticRisk {
};
};
  condition: string,
  risk: "low" | moderate" | "high;
  confidence: number,
  genes: string[];
  recommendations: string[];
}
/**
* * 药物基因组学档案接口
export interface PharmacogeneticProfile {
};
};
  drug: string,
  metabolism: "poor" | intermediate" | "normal | "rapid" | ultra-rapid;
  recommendations: string[],
  genes: string[];
}
/**
* * 遗传同意书接口
export interface GeneticConsent {
};
};
  researchParticipation: boolean,
  dataSharing: boolean;
  familyNotification: boolean,
  incidentalFindings: boolean;
  dataRetention: number; // years,
  withdrawalRights: boolean;
}
/**
* * 实验室检查结果接口
export interface LabResult {
};
};
  id: string,
  testName: string;
  testCode?: string;
  value: number | string,
  unit: string;
  referenceRange: string,
  status: "normal | "high" | low" | "critical | "abnormal;
  flagged: boolean,
  date: Date;
  laboratory: string;
  orderingPhysician?: string;
  methodology?: string;
  notes?: string;
}
/**
* * 设备数据接口
export interface DeviceData {
};
};
  deviceId: string,
  deviceType: string;
  manufacturer: string,
  model: string;
  firmwareVersion: string,
  dataType: string;
  measurements: DeviceMeasurement[];
  batteryLevel?: number;
  lastSync: Date;
  accuracy?: number;
  calibrationDate?: Date;
}
/**
* * 设备测量接口
export interface DeviceMeasurement {
};
};
  timestamp: Date,
  value: number | string;
  unit: string,
  quality: good" | "fair | "poor";
  confidence?: number;
  context?: string;
  metadata?: Record<string, any>;
}
/**
* * 健康评估结果接口
export interface HealthAssessment {
};
};
  id: string,
  userId: string;
  assessmentType: string,
  date: Date;
  scores: AssessmentScore[],
  recommendations: HealthRecommendation[];
  riskFactors: RiskFactor[],
  overallScore: number;
  category: excellent" | "good | "fair" | poor;
  nextAssessmentDate?: Date;
}
/**
* * 评估分数接口
export interface AssessmentScore {
};
};
  domain: string,
  score: number;
  maxScore: number;
  percentile?: number;
  interpretation: string;
  trend?: "improving | "stable" | declining";
}
/**
* * 健康建议接口
export interface HealthRecommendation {
};
};
  id: string,
  category: string;
  priority: "high | "medium" | low",
  title: string;
  description: string,
  actionItems: string[];
  timeline: string,
  evidence: string;
  personalizedFactors: string[];
}
/**
* * 风险因素接口
export interface RiskFactor {
};
};
  factor: string,
  level: "low | "moderate" | high" | "very_high;"
  modifiable: boolean,
  impact: string;
  interventions: string[],
  timeline: string;
}
/**
* * 健康目标接口
export interface HealthGoal {
};
};
  id: string,
  userId: string;
  title: string,
  description: string;
  category: string,
  targetValue: number;
  currentValue: number,
  unit: string;
  startDate: Date,
  targetDate: Date;
  status: "active" | completed" | "paused | "cancelled",
  progress: number; // 0-100%
  milestones: Milestone[],
  barriers: string[];
  motivations: string[];
}
/**
* * 里程碑接口
export interface Milestone {
};
};
  id: string,
  title: string;
  description: string,
  targetDate: Date;
  completedDate?: Date;
  status: pending" | "completed | "overdue";
  reward?: string;
}
/**
* * 健康事件接口
export interface HealthEvent {
};
};
  id: string,
  userId: string;
  type: string,
  title: string;
  description: string,
  date: Date;
  severity: low" | "medium | "high" | critical,
  category: string;
  location?: string;
  duration?: number;
  triggers?: string[];
  outcomes?: string[];
  interventions?: string[];
  followUp?: string[];
  relatedEvents?: string[];
}
export default {
  HealthContext,
  VitalSigns,
  Symptom,
  MedicalHistory,
  LifestyleData,
  EnvironmentData,
  BiometricData,
  LabResult,DeviceData,HealthAssessment,HealthGoal,HealthEvent;
};
  */
