// 中医相关类型定义/;/g/;

// 五脏类型/;,/g/;
export type FiveOrgans = 'heart' | 'liver' | 'spleen' | 'lung' | 'kidney';'';'';

// 诊断方法/;,/g/;
export type DiagnosisMethod = 'look' | 'listen' | 'ask' | 'feel';'';'';

// 时间戳类型/;,/g/;
export interface MCPTimestamp {;,}value: number;
timezone: string;
synchronized: boolean;
}
}
}

// 诊断结果/;,/g/;
export interface TCMDiagnosis {;,}id: string;
patientId: string;
method: DiagnosisMethod;
findings: string[];
syndrome: string;
constitution: string;
recommendations: string[];
confidence: number;
timestamp: Date;
}
}
}