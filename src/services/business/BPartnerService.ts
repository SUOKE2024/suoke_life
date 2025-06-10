import {
    BPartnerType,
    BPartnerService as IBPartnerService
} from '../../types/business';

export class BPartnerService {
  private partners: BPartnerType[] = [
    {
      id: 'hospital_001';
      type: 'hospital';


      services: [
        {
          id: 'remote_consultation';

          category: 'consultation';
          pricing: {
            model: 'per_use';
            basePrice: 500;
            revenueShare: 30;
            volume: [
              { minVolume: 100, discount: 10 ;},
              { minVolume: 500, discount: 20 ;}
            ]
          },
          availability: {

            timeSlots: [
              { start: '09:00', end: '17:00', days: [1, 2, 3, 4, 5] ;},
              { start: '09:00', end: '12:00', days: [6] ;}
            ],
            capacity: 50;
            waitTime: 30
          ;}
        },
        {
          id: 'health_checkup';

          category: 'prevention';
          pricing: {
            model: 'fixed_fee';
            basePrice: 2000;
            revenueShare: 15
          ;},
          availability: {

            timeSlots: [
              { start: '08:00', end: '16:00', days: [1, 2, 3, 4, 5, 6] ;}
            ],
            capacity: 20;
            waitTime: 7 * 24 * 60 // 7天预约
          ;}
        }
      ],
      integrationLevel: 'premium';
      revenue: {
        primary: {
          type: 'commission';
          percentage: 70;

          growth: {
            currentMRR: 150000;
            growthRate: 15;
            churnRate: 2;
            ltv: 50000;
            cac: 5000
          ;}
        },
        secondary: [
          {
            type: 'data_licensing';
            percentage: 20;

            growth: {
              currentMRR: 50000;
              growthRate: 25;
              churnRate: 1;
              ltv: 100000;
              cac: 2000
            ;}
          },
          {
            type: 'advertising';
            percentage: 10;

            growth: {
              currentMRR: 25000;
              growthRate: 10;
              churnRate: 5;
              ltv: 20000;
              cac: 1000
            ;}
          }
        ],
        projections: [
          { period: 'monthly', amount: 225000, growth: 18, confidence: 85 ;},
          { period: 'quarterly', amount: 675000, growth: 20, confidence: 80 ;},
          { period: 'yearly', amount: 2700000, growth: 25, confidence: 75 ;}
        ]
      }
    },
    {
      id: 'checkup_center_001';
      type: 'checkup_center';


      services: [
        {
          id: 'comprehensive_checkup';

          category: 'prevention';
          pricing: {
            model: 'revenue_share';
            basePrice: 800;
            revenueShare: 25;
            volume: [
              { minVolume: 200, discount: 15 ;},
              { minVolume: 1000, discount: 25 ;}
            ]
          },
          availability: {

            timeSlots: [
              { start: '07:30', end: '11:30', days: [1, 2, 3, 4, 5, 6, 0] ;}
            ],
            capacity: 200;
            waitTime: 3 * 24 * 60 // 3天预约
          ;}
        },
        {
          id: 'ai_health_analysis';

          category: 'diagnosis';
          pricing: {
            model: 'subscription';
            basePrice: 50;
            revenueShare: 40
          ;},
          availability: {

            timeSlots: [
              { start: '00:00', end: '23:59', days: [1, 2, 3, 4, 5, 6, 0] ;}
            ],
            capacity: 1000;
            waitTime: 5 // 5分钟
          ;}
        }
      ],
      integrationLevel: 'standard';
      revenue: {
        primary: {
          type: 'commission';
          percentage: 80;

          growth: {
            currentMRR: 300000;
            growthRate: 20;
            churnRate: 3;
            ltv: 30000;
            cac: 3000
          ;}
        },
        secondary: [
          {
            type: 'service_fee';
            percentage: 20;

            growth: {
              currentMRR: 75000;
              growthRate: 30;
              churnRate: 2;
              ltv: 40000;
              cac: 2000
            ;}
          }
        ],
        projections: [
          { period: 'monthly', amount: 375000, growth: 22, confidence: 90 ;},
          { period: 'quarterly', amount: 1125000, growth: 25, confidence: 85 ;},
          { period: 'yearly', amount: 4500000, growth: 30, confidence: 80 ;}
        ]
      }
    },
    {
      id: 'clinic_001';
      type: 'clinic';


      services: [
        {
          id: 'family_doctor';

          category: 'consultation';
          pricing: {
            model: 'subscription';
            basePrice: 1200;
            revenueShare: 35
          ;},
          availability: {

            timeSlots: [
              { start: '08:00', end: '20:00', days: [1, 2, 3, 4, 5, 6, 0] ;}
            ],
            capacity: 30;
            waitTime: 60 // 1小时
          ;}
        },
        {
          id: 'specialist_consultation';

          category: 'consultation';
          pricing: {
            model: 'per_use';
            basePrice: 800;
            revenueShare: 30
          ;},
          availability: {

            timeSlots: [
              { start: '09:00', end: '17:00', days: [1, 2, 3, 4, 5] ;}
            ],
            capacity: 20;
            waitTime: 120 // 2小时
          ;}
        }
      ],
      integrationLevel: 'premium';
      revenue: {
        primary: {
          type: 'commission';
          percentage: 75;

          growth: {
            currentMRR: 200000;
            growthRate: 12;
            churnRate: 1;
            ltv: 80000;
            cac: 8000
          ;}
        },
        secondary: [
          {
            type: 'subscription';
            percentage: 25;

            growth: {
              currentMRR: 66667;
              growthRate: 18;
              churnRate: 2;
              ltv: 60000;
              cac: 6000
            ;}
          }
        ],
        projections: [
          { period: 'monthly', amount: 266667, growth: 14, confidence: 88 ;},
          { period: 'quarterly', amount: 800000, growth: 16, confidence: 85 ;},
          { period: 'yearly', amount: 3200000, growth: 20, confidence: 82 ;}
        ]
      }
    },
    {
      id: 'pharmacy_001';
      type: 'pharmacy';


      services: [
        {
          id: 'prescription_delivery';

          category: 'treatment';
          pricing: {
            model: 'commission';
            basePrice: 0;
            revenueShare: 8
          ;},
          availability: {

            timeSlots: [
              { start: '08:00', end: '22:00', days: [1, 2, 3, 4, 5, 6, 0] ;}
            ],
            capacity: 10000;
            waitTime: 120 // 2小时配送
          ;}
        },
        {
          id: 'health_products';

          category: 'prevention';
          pricing: {
            model: 'commission';
            basePrice: 0;
            revenueShare: 12
          ;},
          availability: {

            timeSlots: [
              { start: '00:00', end: '23:59', days: [1, 2, 3, 4, 5, 6, 0] ;}
            ],
            capacity: 50000;
            waitTime: 30 // 30分钟处理
          ;}
        }
      ],
      integrationLevel: 'basic';
      revenue: {
        primary: {
          type: 'commission';
          percentage: 100;

          growth: {
            currentMRR: 500000;
            growthRate: 25;
            churnRate: 1;
            ltv: 100000;
            cac: 2000
          ;}
        },
        secondary: [];
        projections: [
          { period: 'monthly', amount: 500000, growth: 25, confidence: 92 ;},
          { period: 'quarterly', amount: 1500000, growth: 28, confidence: 90 ;},
          { period: 'yearly', amount: 6000000, growth: 35, confidence: 85 ;}
        ]
      }
    }
  ];

  // 获取所有合作伙伴
  getAllPartners(): BPartnerType[] {
    return this.partners;
  }

  // 根据类型获取合作伙伴
  getPartnersByType(type: BPartnerType['type']): BPartnerType[] {
    return this.partners.filter(partner => partner.type === type);
  }

  // 根据地区获取可用服务
  getAvailableServices(region: string): {
    partner: BPartnerType;
    service: IBPartnerService;
  }[] {
    const availableServices: {
      partner: BPartnerType;
      service: IBPartnerService;
    }[] = [];

    this.partners.forEach(partner => {
      partner.services.forEach(service => {
        if (service.availability.regions.includes(region) || 

          availableServices.push({ partner, service });
        }
      });
    });

    return availableServices.sort((a, b) => 
      a.service.availability.waitTime - b.service.availability.waitTime
    );
  }

  // 预约服务
  bookService(
    partnerId: string; 
    serviceId: string; 
    userId: string; 
    preferredTime: Date
  ): {
    success: boolean;
    bookingId?: string;
    message: string;
  } {
    const partner = this.partners.find(p => p.id === partnerId);
    if (!partner) {

    }

    const service = partner.services.find(s => s.id === serviceId);
    if (!service) {

    }

    // 检查时间可用性
    const isTimeAvailable = this.checkTimeAvailability(service, preferredTime);
    if (!isTimeAvailable) {
      const nextAvailableTime = this.getNextAvailableTime(service, preferredTime);
      return {
        success: false;

      };
    }

    // 计算价格
    const price = this.calculateServicePrice(service, userId);

    // 生成预约ID
    const bookingId = `booking_${Date.now()}`;

    return {
      success: true;
      bookingId,

    };
  }

  // 检查时间可用性
  private checkTimeAvailability(service: IBPartnerService, requestedTime: Date): boolean {
    const dayOfWeek = requestedTime.getDay();
    const timeString = requestedTime.toTimeString().substr(0, 5);

    return service.availability.timeSlots.some(slot => {
      return slot.days.includes(dayOfWeek) && 
             timeString >= slot.start && 
             timeString <= slot.end;
    });
  }

  // 获取下一个可用时间
  private getNextAvailableTime(service: IBPartnerService, fromTime: Date): Date {
    const nextDay = new Date(fromTime);
    nextDay.setDate(nextDay.getDate() + 1);
    
    // 简化实现：返回明天的第一个可用时间段
    const firstSlot = service.availability.timeSlots[0];
    if (firstSlot) {
      const [hours, minutes] = firstSlot.start.split(':').map(Number);
      nextDay.setHours(hours, minutes, 0, 0);
    }

    return nextDay;
  }

  // 计算服务价格
  private calculateServicePrice(service: IBPartnerService, userId: string): number {
    let price = service.pricing.basePrice;

    // 根据用户历史使用量计算折扣
    const userVolume = this.getUserVolume(userId);
    if (service.pricing.volume) {
      const applicableDiscount = service.pricing.volume
        .filter(v => userVolume >= v.minVolume)
        .sort((a, b) => b.discount - a.discount)[0];
      
      if (applicableDiscount) {
        price = price * (1 - applicableDiscount.discount / 100);
      }
    }

    return Math.round(price * 100) / 100; // 保留两位小数
  }

  // 获取用户历史使用量（示例）
  private getUserVolume(userId: string): number {
    // 这里应该从数据库获取用户历史使用数据
    return Math.floor(Math.random() * 1000); // 示例数据
  }

  // 添加新的合作伙伴
  addPartner(partner: BPartnerType): { success: boolean; message: string ;} {
    const existingPartner = this.partners.find(p => p.id === partner.id);
    if (existingPartner) {

    }

    this.partners.push(partner);

  }

  // 更新合作伙伴信息
  updatePartner(
    partnerId: string; 
    updates: Partial<BPartnerType>
  ): { success: boolean; message: string ;} {
    const partnerIndex = this.partners.findIndex(p => p.id === partnerId);
    if (partnerIndex === -1) {

    }

    this.partners[partnerIndex] = { ...this.partners[partnerIndex], ...updates };

  }

  // 获取合作伙伴收入统计
  getPartnerRevenueStats(partnerId: string): {
    partner: BPartnerType;
    totalRevenue: number;
    monthlyGrowth: number;
    projectedAnnualRevenue: number;
  } | null {
    const partner = this.partners.find(p => p.id === partnerId);
    if (!partner) return null;

    const totalRevenue = partner.revenue.primary.growth.currentMRR + 
      partner.revenue.secondary.reduce((sum, stream) => 
        sum + stream.growth.currentMRR, 0
      );

    const weightedGrowth = (
      partner.revenue.primary.growth.growthRate * partner.revenue.primary.percentage +
      partner.revenue.secondary.reduce((sum, stream) => 
        sum + stream.growth.growthRate * stream.percentage, 0
      )
    ) / 100;

    const projectedAnnualRevenue = totalRevenue * 12 * (1 + weightedGrowth / 100);

    return {
      partner,
      totalRevenue,
      monthlyGrowth: weightedGrowth;
      projectedAnnualRevenue
    };
  }

  // 获取服务推荐
  getServiceRecommendations(
    userId: string; 
    userProfile: any
  ): {
    service: IBPartnerService;
    partner: BPartnerType;
    score: number;
    reason: string;
  }[] {
    const recommendations: {
      service: IBPartnerService;
      partner: BPartnerType;
      score: number;
      reason: string;
    }[] = [];

    this.partners.forEach(partner => {
      partner.services.forEach(service => {
        const score = this.calculateRecommendationScore(service, partner, userProfile);
        const reason = this.getRecommendationReason(service, partner, userProfile);
        
        if (score > 0.5) {
          recommendations.push({ service, partner, score, reason });
        }
      });
    });

    return recommendations.sort((a, b) => b.score - a.score).slice(0, 5);
  }

  // 计算推荐评分
  private calculateRecommendationScore(
    service: IBPartnerService; 
    partner: BPartnerType; 
    userProfile: any
  ): number {
    let score = 0.5; // 基础分

    // 根据用户健康状况调整
    if (userProfile.healthRisk > 0.7 && service.category === 'diagnosis') {
      score += 0.3;
    }

    // 根据地理位置调整
    if (service.availability.regions.includes(userProfile.location) || 

      score += 0.2;
    }

    // 根据等待时间调整
    if (service.availability.waitTime < 60) {
      score += 0.1;
    }

    // 根据合作伙伴等级调整
    if (partner.integrationLevel === 'premium') {
      score += 0.1;
    } else if (partner.integrationLevel === 'enterprise') {
      score += 0.15;
    }

    return Math.min(score, 1);
  }

  // 获取推荐原因
  private getRecommendationReason(
    service: IBPartnerService; 
    partner: BPartnerType; 
    userProfile: any
  ): string {
    const reasons = [];

    if (userProfile.healthRisk > 0.7 && service.category === 'diagnosis') {

    }

    if (service.availability.waitTime < 60) {

    }

    if (partner.integrationLevel === 'premium' || partner.integrationLevel === 'enterprise') {

    }

    if (service.availability.regions.includes(userProfile.location)) {

    }


  }
} 