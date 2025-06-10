// 索克生活 - 生活类型定义/g/;
export interface LifeData {}
  id: string;
  userId: string;
  timestamp: Date;
  category: string;
  data: any;
}

export interface LifeMetrics {}
  steps: number;
  heartRate: number;
  sleep: number;
  stress: number;
}

export interface LifeGoal {}
  id: string;
  title: string;
  target: number;
  current: number;
  unit: string;
}
