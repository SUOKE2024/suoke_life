/**
 * 舌头特征模型
 * 描述舌诊过程中观察的舌体特征
 */
export interface TongueFeatures {
  /**
   * 舌质颜色 (淡白, 淡红, 红, 绛, 紫暗)
   */
  tongueColor: string;
  
  /**
   * 舌体形态 (正常, 胖大, 瘦薄, 点刺, 裂纹)
   */
  tongueShape: string;
  
  /**
   * 舌苔状态 (无苔, 薄白, 厚白, 薄黄, 黄腻, 黑苔)
   */
  tongueCoating: string;
  
  /**
   * 舌体湿润度 (干燥, 适中, 偏湿)
   */
  moisture: string;
  
  /**
   * 是否有裂纹
   */
  cracks: boolean;
  
  /**
   * 是否有斑点
   */
  spots: boolean;
  
  /**
   * 是否有齿痕
   */
  teethMarks: boolean;
  
  /**
   * 是否有舌偏斜
   */
  deviation: boolean;
}

/**
 * 舌诊分析结果
 * 包含完整的舌诊分析结果和中医辨证
 */
export interface TongueDiagnosisResult {
  /**
   * 诊断ID，唯一标识一次舌诊分析
   */
  diagnosisId: string;
  
  /**
   * 关联的问诊会话ID
   */
  sessionId: string;
  
  /**
   * 诊断时间戳
   */
  timestamp: string;
  
  /**
   * 舌头特征分析结果
   */
  features: TongueFeatures;
  
  /**
   * 中医辨证结果
   * 包含辨证概念和置信度
   */
  tcmImplications: Array<{
    /**
     * 中医辨证概念 (如"脾虚"、"湿热"等)
     */
    concept: string;
    
    /**
     * 置信度 (0-1)
     */
    confidence: number;
  }>;
  
  /**
   * 健康建议
   */
  recommendations: string[];
  
  /**
   * 元数据，包含诊断过程的附加信息
   */
  metadata: {
    /**
     * 拍摄时间
     */
    captureTime?: string;
    
    /**
     * 光照条件
     */
    lightingCondition?: string;
    
    /**
     * 处理步骤
     */
    processingSteps?: string[];
    
    /**
     * 其他元数据
     */
    [key: string]: any;
  };
}

/**
 * 舌诊分析请求
 */
export interface TongueDiagnosisRequest {
  /**
   * Base64编码的舌头图像
   */
  imageBase64: string;
  
  /**
   * 会话ID
   */
  sessionId: string;
  
  /**
   * 元数据
   */
  metadata?: {
    /**
     * 拍摄时间
     */
    captureTime?: string;
    
    /**
     * 光照条件
     */
    lightingCondition?: string;
    
    /**
     * 其他元数据
     */
    [key: string]: any;
  };
}