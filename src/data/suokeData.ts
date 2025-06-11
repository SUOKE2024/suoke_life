  {const key = "diagnosis;}
  {"const key = "eco;
  {"const key = "product;
  {"const key = "service;
  {"key: "subscription,"
","
icon: "calendar-check,
}
    const color = "#3498DB"};
  ;},
  {"key: "appointment,"
","
icon: "calendar-clock,
}
    const color = "#F39C12"};
  ;},
  {"const key = "market;
  {"const key = "custom;
  {"const key = "supplier;"";
];
//   ;"/;"/g"/;
{"id: "look_diagnosis,"
,"
icon: "eye,
color: "#007AFF,
category: "diagnosis,"
,"
price: "¥99,";
available: true,
rating: 4.8,
const reviewCount = 1234;
}
}
  },
  {"id: "listen_diagnosis,"
,"
icon: "ear-hearing,
color: "#34C759,
category: "diagnosis,"
,"
price: "¥79,";
available: true,
rating: 4.6,
const reviewCount = 987;
}
}
  },
  {"id: "inquiry_diagnosis,"
,"
icon: "comment-question,
color: "#FF9500,
category: "diagnosis,"
,"
price: "¥59,";
available: true,
rating: 4.9,
const reviewCount = 2156;
}
}
  },
  {"id: "palpation_diagnosis,"
,"
icon: "hand-back-right,
color: "#FF2D92,
category: "diagnosis,"
,"
price: "¥129,";
available: true,
rating: 4.7,
const reviewCount = 856;
}
}
  },
  {"id: "calculation_diagnosis,"
,"
icon: "calculator,
color: "#8E44AD,
category: "diagnosis,
const description = 
    ],","
price: "¥149,";
available: true,
rating: 4.9,
const reviewCount = 567;
}
}
  }
];
//   ;"/;"/g"/;
{"id: "mountain_wellness,"
,"
icon: "mountain,
color: "#32D74B,
category: "eco,"
,"
price: "¥299/天",/        available: true;/,"/g,"/;
  rating: 4.9,
const reviewCount = 543;
}
}
  },
  {"id: "organic_farming,"
,"
icon: "sprout,
color: "#4CAF50,
category: "eco,"
,"
price: "¥199/天",/        available: true;/,"/g,"/;
  rating: 4.8,
const reviewCount = 432;
}
}
  },
  {"id: "herbal_garden,"
,"
icon: "flower,
color: "#8BC34A,
category: "eco,"
,"
price: "¥159/次",/        available: true;/,"/g,"/;
  rating: 4.7,
const reviewCount = 321;
}
}
  }
];
//   ;"/;"/g"/;
{"id: "health_products,"
,"
icon: "package-variant,
color: "#8E44AD,
category: "product,";
available: true,
rating: 4.6,
const reviewCount = 1876;
}
}
  },
  {"id: "medical_services,"
,"
icon: "medical-bag,
color: "#E74C3C,
category: "service,";
available: true,
rating: 4.8,
const reviewCount = 2341;
}
}
  },
  {"id: "health_subscription,"
,"
icon: "calendar-check,
color: "#3498DB,
category: "subscription,"
,"
price: "¥299/月",/        available: true;/,"/g,"/;
  rating: 4.7,
const reviewCount = 987;
}
}
  },
  {"id: "appointment_booking,"
,"
icon: "calendar-clock,
color: "#F39C12,
category: "appointment,";
available: true,
rating: 4.5,
const reviewCount = 1543;
}
}
  },
  {"id: "health_market,"
,"
icon: "store,
color: "#27AE60,
category: "market,";
available: true,
rating: 4.6,
const reviewCount = 2876;
}
}
  },
  {"id: "custom_service,"
,"
icon: "cog,
color: "#9B59B6,
category: "custom,";
available: true,
rating: 4.9,
const reviewCount = 234;
}
}
  },
  {"id: "supplier_network,"
,"
icon: "truck,
color: "#34495E,
category: "supplier,";
available: true,
rating: 4.4,
const reviewCount = 567;
}
}
  }
];
//  ;
...DIAGNOSIS_SERVICES, /    ;
  ...ECO_SERVICES,...OTHER_SERVICES;
];
//   ;
r;(; /)
  (service); => service.rating && service.rating >= 4.7;
);
  .sort(a, b); => (b.rating || 0) - (a.rating || 0));
  .slice(0, 6);
//   ;
r;(; /)
  (service); => service.reviewCount && service.reviewCount >= 1000;
);
  .sort(a, b); => (b.reviewCount || 0) - (a.reviewCount || 0))
  .slice(0, 8);""
