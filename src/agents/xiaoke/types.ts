// 小克智能体类型定义

export interface ServiceContext {
  userId: string;
  sessionId?: string;
  location?: string;
  preferences?: Record<string, any>;
}

export interface UserProfile {
  id: string;
  name: string;
  age: number;
  location: string;
  healthConditions: string[];
  preferences: Record<string, any>;
}

export interface ServiceRecommendation {
  id: string;
  name: string;
  category: string;
  description: string;
  price: number;
  rating: number;
  provider: string;
  availability: boolean;
  matchScore: number;
  benefits: string[];
  requirements: string[];
  estimatedDuration: string;
  location: string;
}

export interface DoctorMatch {
  doctorId: string;
  name: string;
  specialty: string;
  hospital: string;
  rating: number;
  experience: number;
  availability: boolean;
  matchScore: number;
  consultationFee: number;
  languages: string[];
  certifications: string[];
  reviews: any[];
  location: string;
  distance: number;
}

export interface ProductInfo {
  id: string;
  name: string;
  category: string;
  description: string;
  price: number;
  images: string[];
  specifications: Record<string, any>;
  nutritionInfo: Record<string, any>;
  origin: string;
  certifications: string[];
  availability: boolean;
  rating: number;
  reviews: any[];
  supplyChain: any;
}

export interface SupplyChainInfo {
  productId: string;
  stages: Array<{
    id: string;
    name: string;
    description: string;
    location: string;
    timestamp: Date;
    responsible: string;
    certifications: string[];
    quality: Record<string, any>;
    temperature?: number;
    humidity?: number;
  }>;
  blockchainHash: string;
  verificationStatus: string;
  traceabilityScore: number;
  sustainabilityMetrics: Record<string, any>;
}

export interface AppointmentInfo {
  id: string;
  doctorId: string;
  patientId: string;
  timeSlot: Date;
  type: 'consultation' | 'checkup' | 'follow-up';
  status: string;
  notes?: string;
  location: string;
  meetingLink?: string;
  reminders: any[];
  createdAt: Date;
}

export interface XiaokeAgent {
  processMessage(
    message: string,
    context: ServiceContext,
    userId?: string,
    sessionId?: string
  ): Promise<any>;
  recommendServices(
    userProfile: UserProfile,
    healthData?: any,
    preferences?: any
  ): Promise<ServiceRecommendation[]>;
  matchDoctors(
    symptoms: string[],
    specialty?: string,
    location?: string,
    preferences?: any
  ): Promise<DoctorMatch[]>;
  getProductInfo(productId: string): Promise<ProductInfo | null>;
  searchProducts(query: string, filters?: any): Promise<ProductInfo[]>;
  getSupplyChainInfo(productId: string): Promise<SupplyChainInfo | null>;
  createAppointment(
    doctorId: string,
    timeSlot: Date,
    type: 'consultation' | 'checkup' | 'follow-up',
    notes?: string
  ): Promise<AppointmentInfo | null>;
  getUserAppointments(userId: string): Promise<AppointmentInfo[]>;
  subscribeToService(
    serviceId: string,
    plan: 'basic' | 'premium' | 'enterprise',
    duration: number
  ): Promise<any>;
  getStatus(): Promise<any>;
}
