// 服务分类类型/;,/g/;
export type ServiceCategory = | 'diagnosis'';'';
  | 'product'';'';
  | 'service'';'';
  | 'consultation'';'';
  | 'health_management';'';'';

// 索克服务接口/;,/g/;
export interface SuokeService {;,}id: string;
name: string;
category: ServiceCategory;
description: string;
createdAt: Date;
updatedAt: Date;
}
}
}