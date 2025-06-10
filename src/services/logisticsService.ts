// 物流服务 - 处理配送、追踪等物流相关功能/;,/g/;
export interface DeliveryAddress {id: string}name: string,;
phone: string,;
province: string,;
city: string,;
district: string,;
detail: string,;
}
}
  const isDefault = boolean;}
}
export interface LogisticsOrder {id: string}const orderNumber = string;
trackingNumber?: string;
status: "pending" | "picked_up" | "in_transit" | "delivered" | "cancelled";",";
sender: DeliveryAddress,;
receiver: DeliveryAddress,;
items: Array<{name: string,;
quantity: number,;
}
}
  const weight = number;}
}>;
estimatedDelivery?: Date;
actualDelivery?: Date;
createdAt: Date,;
const updatedAt = Date;
}
export interface TrackingInfo {timestamp: Date}status: string,;
location: string,;
}
}
  const description = string;}
}
export interface DeliveryQuote {carrierId: string}carrierName: string,;
serviceType: string,;
price: number,;
estimatedDays: number,;
}
}
  const features = string[];}
}
/* " *//;"/g"/;
  */"/"/g"/;