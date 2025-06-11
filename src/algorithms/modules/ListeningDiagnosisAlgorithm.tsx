"
";"";
export interface ListeningData {;}voiceRecording?: AudioData;
breathingRecording?: AudioData;
coughRecording?: AudioData;
environmentalAudio?: AudioData;
}
}
  metadata?: Record<string; any>;}
}
export interface AudioData {data: ArrayBuffer}format: string,;
sampleRate: number,
channels: number,
}
}
  const duration = number;}
}
export interface ListeningResult {;}confidence: number,features: ListeningFeatures,analysis: string;
voiceAnalysis?: VoiceAnalysis;
breathingAnalysis?: BreathingAnalysis;
}
}
  coughAnalysis?: CoughAnalysis;}
}
export interface ListeningFeatures {voice: VoiceFeatures}breathing: BreathingFeatures,;
}
}
  const cough = CoughFeatures;}
}
export interface VoiceFeatures {pitch: number}volume: number,;
tone: string,
clarity: string,
rhythm: string,
}
}
  const emotion = string;}
}
export interface BreathingFeatures {rate: number}depth: string,;
rhythm: string,
sound: string,
}
}
  const effort = string;}
}
export interface CoughFeatures {frequency: number}intensity: string,;
type: string,
wetness: string,
}
}
  const timing = string;}
}
export interface VoiceAnalysis {;}}
}
  toneAnalysis: {pitch: { value: number, significance: string;}
},volume: { value: number, significance: string;},clarity: { value: string, significance: string;};
  };
emotionalState: {energy: string,}}
    mood: string,}
    const stress = string;};
organReflection: {heart: string}lung: string,
kidney: string,
}
    liver: string,}
    const spleen = string;};
const syndromeIndications = string[];
}
export interface BreathingAnalysis {;}}
}
  respiratoryAssessment: {rate: { value: number, significance: string;}
},depth: { value: string, significance: string;},rhythm: { value: string, significance: string;};
  };
qiAssessment: {qiStrength: string,}}
    qiFlow: string,}
    const qiDeficiency = boolean;};
organFunction: {lung: string,}}
    kidney: string,}
    const heart = string;};
const syndromeIndications = string[];
}
export interface CoughAnalysis {;}}
}
  coughCharacteristics: {type: { value: string, significance: string;}
},wetness: { value: string, significance: string;},timing: { value: string, significance: string;};
  };
pathogenAnalysis: {windCold: number}windHeat: number,
}
    dryness: number,}
    const phlegmDampness = number;};
organInvolvement: {lung: string,}}
    spleen: string,}
    const kidney = string;};
const syndromeIndications = string[];
;}
export interface UserProfile {";}age: number,";
gender: "male" | "female" | "other,";
height: number,
weight: number,
occupation: string,
}
}
  medicalHistory: string[],allergies: string[],medications: string[];}
}
// 闻诊算法类export class ListeningDiagnosisAlgorithm {/;}private config: ListeningConfig;/g/;
private knowledgeBase: TCMKnowledgeBase;
private voiceAnalyzer!: VoiceAnalyzer;
private breathingAnalyzer!: BreathingAnalyzer;
private coughAnalyzer!: CoughAnalyzer;
constructor(config: ListeningConfig, knowledgeBase: TCMKnowledgeBase) {this.config = config;}this.knowledgeBase = knowledgeBase;
}
}
    this.initializeAnalyzers();}
  }
  // 初始化分析器  private initializeAnalyzers(): void {/;}this.voiceAnalyzer = new VoiceAnalyzer();/g/;
this.config.models.voiceAnalysis,
this.knowledgeBase;
    );
this.breathingAnalyzer = new BreathingAnalyzer();
this.config.models.breathingAnalysis,
this.knowledgeBase;
    );
this.coughAnalyzer = new CoughAnalyzer();
this.config.models.coughAnalysis,
this.knowledgeBase;
}
    );}
  }
  // 执行闻诊分析  public async analyze(data: ListeningData,)
userProfile?: UserProfile;
  ): Promise<ListeningResult /    >  {/;}if (!this.config.enabled) {}}/g/;
}
    }";
try {";}this.emit("algorithm:progress", {")"";}stage: "preprocessing,")"";
}
      const progress = 0.1;)}
      });";
const processedData = await this.preprocessAudio(da;t;a;);";
this.emit("algorithm:progress", {)")"";}stage: "feature_extraction,")"";
}
      const progress = 0.3;)}
      });";
const features = await this.extractFeatures(processedDa;t;a;);";
this.emit("algorithm:progress", {)")"";}}
      stage: "analysis,)"}";
const progress = 0.6;});
const analyses = await this.performAnalyses(;)";
processedData,features,userProf;i;l;e;);";
this.emit("algorithm:progress", {)")"";}}
      stage: "integration,)"}
const progress = 0.8;});";
result: await this.integrateResults(features, analys;e;s;);";
this.emit("algorithm:progress", {)")"";}}
      stage: "completed,)"}";
const progress = 1.0;});
return resu;l;t;
    } catch (error) {"}
this.emit("algorithm:error", { error, stage: "listening_analysis";});";"";
const throw = error;
    }
  }
  ///    >  {}
const processed: ProcessedListeningData = {;};
if (data.voiceRecording) {processed.voiceRecording = await this.preprocessAudioData()";}data.voiceRecording,
        "voice"";
}
      ;);}
    }
    if (data.breathingRecording) {processed.breathingRecording = await this.preprocessAudioData()";}data.breathingRecording,
        "breathing"";
}
      ;);}
    }
    if (data.coughRecording) {processed.coughRecording = await this.preprocessAudioData()";}data.coughRecording,
        "cough"";
}
      ;);}
    }
    return process;e;d;
  }
  // 音频数据预处理  private async preprocessAudioData(audio: AudioData,)
const type = string);: Promise<ProcessedAudioData /    >  {/;}const denoised = await this.denoiseAudio(aud;i;o;);/g/;
const normalized = await this.normalizeAudio(denois;e;d;);
}
    segmented: await this.segmentAudio(normalized, ty;p;e;);}
    return {original: audio,processed: segmented,type,metadata: {originalDuration: audio.duration,processedDuration: segmented.duration,processingTime: Date.now();};};
  }
  ///    >  {/;}const: features: ListeningFeatures = {voice: {pitch: 0,";"/g,"/;
  volume: 0,";
tone: ,";
clarity: ",",";
rhythm: ,";
}
        const emotion = "}
      ;},";
breathing: { rate: 0, depth: ", rhythm: ", sound: ", effort: ";},";
cough: { frequency: 0, intensity: ", type: ", wetness: ", timing: ";}";
    };
if (data.voiceRecording) {features.voice = await this.voiceAnalyzer.extractFeatures();}}
        data.voiceRecording;);}
    }
    if (data.breathingRecording) {features.breathing = await this.breathingAnalyzer.extractFeatures();}}
        data.breathingRecording;);}
    }
    if (data.coughRecording) {features.cough = await this.coughAnalyzer.extractFeatures();}}
        data.coughRecording;);}
    }
    return featur;e;s;
  }
  // 执行各项分析  private async performAnalyses(data: ProcessedListeningData,)
const features = ListeningFeatures;
userProfile?: UserProfile;
  ): Promise<AnalysisResults /    >  {}
const results: AnalysisResults = {;};
if (data.voiceRecording) {results.voiceAnalysis = await this.voiceAnalyzer.analyze();}features.voice,
}
        userProfile;);}
    }
    if (data.breathingRecording) {results.breathingAnalysis = await this.breathingAnalyzer.analyze();}features.breathing,
}
        userProfile;);}
    }
    if (data.coughRecording) {results.coughAnalysis = await this.coughAnalyzer.analyze();}features.cough,
}
        userProfile;);}
    }
    return resul;t;s;
  }
  // 整合分析结果  private async integrateResults(features: ListeningFeatures,)
const analyses = AnalysisResults);: Promise<ListeningResult /    >  {/;}const confidence = this.calculateOverallConfidence(analyses;);/g/;
}
    const analysis = await this.generateComprehensiveAnalysis(analys;e;s;);}
    return {confidence,features,analysis,voiceAnalysis: analyses.voiceAnalysis,breathingAnalysis: analyses.breathingAnalysis,coughAnalysis: analyses.coughAnalysi;s;};
  }
  // 计算整体置信度  private calculateOverallConfidence(analyses: AnalysisResults): number  {/;}const confidences: number[] = [];/g/;
if (analyses.voiceAnalysis) {}}
      confidences.push(0.8);}
    }  if (analyses.breathingAnalysis) {}}
      confidences.push(0.9);}
    }  if (analyses.coughAnalysis) {}}
      confidences.push(0.7);}
    }  if (confidences.length === 0) {}}
      return 0.;5;}
    }
    // 记录渲染性能
performanceMonitor.recordRender();
return (;);
confidences.reduce(sum, con;f;); => sum + conf, 0) / confidences.length/        );
  }
  // 生成综合分析  private async generateComprehensiveAnalysis(analyses: AnalysisResults);: Promise<string>  {/;}const analysisTexts: string[] = [];/g/;
if (analyses.voiceAnalysis) {analysisTexts.push();}}
      );}
    }
    if (analyses.breathingAnalysis) {}}
      analysisTexts.push()}
        `呼吸分析：呼吸频率${analyses.breathingAnalysis.respiratoryAssessment.rate.value}次/分，气机${analyses.breathingAnalysis.qiAssessment.qiFlow}`/          );```/`;`/g`/`;
    }
    if (analyses.coughAnalysis) {analysisTexts.push();}}
      );}
    }
    const  comprehensiveAnalysis =;
const await = this.knowledgeBase.generateCalculationAnalysis({ listeningAnalysis: anal;y;s;e;s ; });
    ;);
  }
  private async denoiseAudio(audio: AudioData): Promise<AudioData  /     >  {/;}return audi;o;  / 占位符* ///
private async normalizeAudio(audio: AudioData): Promise<AudioData /    >  {/;}return audi;o;  / 占位符* ///
private async segmentAudio(audio: AudioData,);
const type = string);: Promise<AudioData /    >  {/;}return audi;o;  / 占位符* ///
}
  // 模拟事件发射  public on(event: string, callback: (data: unknown) => void): void {}
    ;}
  public: emit(event: string, data?: unknown): void  {}
    ;}
  // 清理资源  public async cleanup(): Promise<void> {/;}const await = Promise.all();/g/;
      [;]this.voiceAnalyzer.cleanup?.(),
this.breathingAnalyzer.cleanup?.(),
this.coughAnalyzer.cleanup?.();
];
      ].filter(Boolean;);
}
    );}
  }
}
// 辅助类型定义 * interface ProcessedListeningData {/;}voiceRecording?: ProcessedAudioData;/g/;
breathingRecording?: ProcessedAudioData;
}
}
  coughRecording?: ProcessedAudioData;}
}
interface ProcessedAudioData {original: AudioData}processed: AudioData,
type: string,
}
}
  metadata: Record<string, any>;}
}
interface AnalysisResults {voiceAnalysis?: VoiceAnalysis;}breathingAnalysis?: BreathingAnalysis;
}
}
  coughAnalysis?: CoughAnalysis;}
}
//
constructor(private config: unknown, private knowledgeBase: TCMKnowledgeBase) {;}
  const async = extractFeatures(audio: ProcessedAudioData): Promise<VoiceFeatures /    >  {/;}return {pitch: 150,  volume: 65,  / dB* ///;/;}}/g/;
}
  };
async: analyze(features: VoiceFeatures,userProfile?: UserProfile;);
  );: Promise<VoiceAnalysis /    >  {/;}clarity: {const value = features.clarity;/g/;
}
}
        }
      }
emotionalState: {,}}
}
      ;}
organReflection: {,}}
}
      ;}
    };
  }
  const async = cleanup(): Promise<void> {}
}
class BreathingAnalyzer {}
  constructor(private config: unknown, private knowledgeBase: TCMKnowledgeBase) {;}";
const async = extractFeatures(audio: ProcessedAudioData): Promise<BreathingFeatures /    >  {"}""/;"/g"/;
return {rate: 16, ///     depth: "适中",rhythm: "规律",sound: "平和",effort: "轻松";};"/;"/g"/;
  };
async: analyze(features: BreathingFeatures,userProfile?: UserProfile;);
  );: Promise<BreathingAnalysis /    >  {/;}depth: {const value = features.depth;/g/;
}
}
        }
rhythm: {const value = features.rhythm;
}
}
        }
      }
qiAssessment: {,}}
        const qiDeficiency = false;}
      }
organFunction: {,}}
}
      ;}
    };
  }
  const async = cleanup(): Promise<void> {}
}
class CoughAnalyzer {}
  constructor(private config: unknown, private knowledgeBase: TCMKnowledgeBase) {;}
  const async = extractFeatures(audio: ProcessedAudioData): Promise<CoughFeatures /    >  {/;}}/g/;
}
  ;};
async: analyze(features: CoughFeatures,userProfile?: UserProfile;);
  );: Promise<CoughAnalysis /    >  {/;}}/g/;
}
      }
pathogenAnalysis: {windCold: 0,
windHeat: 0,
dryness: 0,
}
        const phlegmDampness = 0;}
      }
organInvolvement: {,}}
}
      ;}
    };
  }
  const async = cleanup(): Promise<void> {}
}";
export default ListeningDiagnosisAlgorithm;""
