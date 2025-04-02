export enum DialectType {
  MANDARIN = 'mandarin',        // 普通话
  CANTONESE = 'cantonese',      // 粤语
  SHANGHAINESE = 'shanghainese', // 上海话
  SICHUANESE = 'sichuanese',    // 四川话
  NORTHEASTERN = 'northeastern', // 东北话
  HAKKA = 'hakka',              // 客家话
  MIN = 'min',                  // 闽南语
  XIANG = 'xiang',              // 湘语
  GAN = 'gan',                  // 赣语
  JIN = 'jin',                  // 晋语
  HUI = 'hui',                  // 徽语
  PINGHUA = 'pinghua'           // 平话
}

export interface DialectPreference {
  primary: DialectType;
  secondary?: DialectType;
  autoDetect: boolean;
}

export interface DialectTranslation {
  original: string;
  translated: string;
  targetDialect: DialectType;
  confidence: number;
}

export interface DialectDetection {
  text: string;
  detectedDialect: DialectType;
  confidence: number;
  alternativeDialects?: Array<{dialect: DialectType, confidence: number}>;
}

export interface RegionalDialect {
  region: string;
  primaryDialect: DialectType;
  secondaryDialects: DialectType[];
  description: string;
  popularityRank: number;
}

export interface TTSDialectParams {
  voice: string;
  style?: string;
  rate?: number;
  pitch?: number;
} 