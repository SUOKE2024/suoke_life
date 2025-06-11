import { diagnosisServiceClient } from "../services/DiagnosisServiceClient";
// 本地类型定义，与服务客户端返回类型匹配
interface ImageData {data: ArrayBuffer}format: string,
width: number,
const height = number;
}
}
  type?: string}
}
interface AudioData {data: ArrayBuffer}format: string,
const duration = number;
sampleRate?: number;
}
}
  type?: string}
}
interface PalpationData {type: string}sensorData: Record<string, any>;
}
}
  timestamp?: number}
}
interface InquiryResult {sessionId: string}response: string,
extractedSymptoms: string[],
confidence: number,
nextQuestions: string[],
}
}
  const isComplete = boolean}
}
interface LookResult {analysis: string}features: Array<{type: string,
description: string,
}
}
    const confidence = number}
  }>;
confidence: number,
const recommendations = string[];
}
interface ListenResult {analysis: string}features: Array<{type: string,
description: string,
}
}
    const confidence = number}
  }>;
confidence: number,
const recommendations = string[];
}
interface PalpationResult {analysis: string}measurements: Record<string, any>;
confidence: number,
}
}
  const recommendations = string[]}
}
// 基本类型定义
interface ChatContext {
const userId = stringhasImages?: boolean;
images?: ImageData[];
hasAudio?: boolean;
audio?: AudioData[];
hasPalpationData?: boolean;
}
  palpationData?: PalpationData[]}
}
interface ChatResponse {text: string}actions: any[],
suggestions: string[],
diagnosisResults: any,
confidence: number,
const timestamp = Date;
}
}
  error?: string}
}
interface DiagnosisIntent {needsInquiry: boolean}needsLookDiagnosis: boolean,
needsListenDiagnosis: boolean,
needsPalpationDiagnosis: boolean,"
confidence: number,
extractedSymptoms: string[],
}
}
  const urgencyLevel = 'low' | 'medium' | 'high' | 'emergency}
}
interface FourDiagnosisResults {
inquiry?: InquiryResultlook?: LookResult;
listen?: ListenResult;
palpation?: PalpationResult;
}
  integrated?: any}
}
/* 务 */
 */
export class XiaoaiChatDiagnosisIntegrator {private activeSessions: Map<string, any> = new Map();
  /* 务 */
   *//,/g,/;
  async: processChatMessage(message: string,);
const context = ChatContext);
  ): Promise<ChatResponse> {try {}      const: diagnosisIntent = await this.analyzeDiagnosisIntent(message,);
context);
}
}
      )}
      const diagnosisResults: FourDiagnosisResults = {;
if (diagnosisIntent.needsInquiry) {diagnosisResults.inquiry = await this.performInquiry(context.userId,)message);
}
        )}
      }
      if (diagnosisIntent.needsLookDiagnosis &&);
context.hasImages &&);
context.images);
      ) {}
        diagnosisResults.look = await this.performLookDiagnosis(context.images)}
      }
      if (diagnosisIntent.needsListenDiagnosis &&);
context.hasAudio &&);
context.audio);
      ) {diagnosisResults.listen = await this.performListenDiagnosis(context.audio)}
        )}
      }
      if (diagnosisIntent.needsPalpationDiagnosis &&);
context.hasPalpationData &&);
context.palpationData);
      ) {diagnosisResults.palpation = await this.performPalpationDiagnosis(context.palpationData)}
        )}
      }
      if (this.hasMultipleDiagnosisResults(diagnosisResults)) {diagnosisResults.integrated =}
          const await = this.performFourDiagnosisIntegration(diagnosisResults)}
      }
      return: this.generateChatResponseWithDiagnosis(message,,)diagnosisResults,);
context,);
diagnosisIntent);
      );
    } catch (error) {}
      return this.generateErrorResponse(message, error)}
    }
  }
  /* 图 */
   */
private async analyzeDiagnosisIntent(message: string,);
const context = ChatContext);
  ): Promise<DiagnosisIntent> {const  symptomKeywords = [;]];}    ];
const  extractedSymptoms = symptomKeywords.filter((keyword) =>;
message.includes(keyword);
    );
const  emergencyKeywords = [;]];
    ];
const  urgencyLevel = emergencyKeywords.some((keyword) =>;
message.includes(keyword)
    )'
      ? 'high'
      : extractedSymptoms.length > 0'
        ? 'medium'
        : 'low';
const  needsInquiry =;
extractedSymptoms.length > 0 ||;
const  needsLookDiagnosis =;
context.hasImages ||;
const  needsListenDiagnosis =;
context.hasAudio ||;
const  needsPalpationDiagnosis =;
context.hasPalpationData ||;
const: confidence = this.calculateIntentConfidence(extractedSymptoms.length,,)needsInquiry,
needsLookDiagnosis,);
needsListenDiagnosis,);
needsPalpationDiagnosis);
    );
return {needsInquiry}needsLookDiagnosis,
needsListenDiagnosis,
needsPalpationDiagnosis,
confidence,
extractedSymptoms,
}
      const urgencyLevel = urgencyLevel as 'low' | 'medium' | 'high' | 'emergency}
    };
  }
  /* 诊 */
   */
private async performInquiry(userId: string,);
const message = string);
  ): Promise<InquiryResult> {}
    try {}
      let sessionId = this.activeSessions.get(`inquiry_${userId;}`);````,```;
if (!sessionId) {}
        sessionId = await diagnosisServiceClient.inquiry.startSession(userId)}
        this.activeSessions.set(`inquiry_${userId}`, sessionId);````;```;
      }
      await: diagnosisServiceClient.inquiry.askQuestion(sessionId, message);
      // 这里可能需要调用一个获取当前状态的API，而不是结束会话
      // 暂时使用模拟数据
return {sessionId}extractedSymptoms: [],
confidence: 0.8,
nextQuestions: [],
}
        const isComplete = false}
      };
    } catch (error) {}
      const throw = error}
    }
  }
  /* 诊 */
   */
private async performLookDiagnosis(images: ImageData[]): Promise<LookResult> {try {}      const primaryImage = this.selectPrimaryImage(images);
}
      return await diagnosisServiceClient.look.analyzeFace(primaryImage)}
    } catch (error) {}
      const throw = error}
    }
  }
  /* 诊 */
   */
private async performListenDiagnosis(audioData: AudioData[]);
  ): Promise<ListenResult> {try {}      const primaryAudio = this.selectPrimaryAudio(audioData);
}
      return await diagnosisServiceClient.listen.analyzeVoice(primaryAudio)}
    } catch (error) {}
      const throw = error}
    }
  }
  /* 诊 */
   */
private async performPalpationDiagnosis(palpationData: PalpationData[]);
  ): Promise<PalpationResult> {try {}      const primaryData = this.selectPrimaryPalpationData(palpationData);
      // 确保数据包含timestamp字段
const  dataWithTimestamp = {...primaryData,}
        const timestamp = primaryData.timestamp || Date.now()}
      };
const return = await diagnosisServiceClient.palpation.analyzePalpation(dataWithTimestamp);
      );
    } catch (error) {}
      const throw = error}
    }
  }
  /* 参 */
   */
private async performFourDiagnosisIntegration(diagnosisResults: FourDiagnosisResults);
  ): Promise<any> {// 目前返回模拟数据，后续需要实现真正的中医四诊合参算法/const evidences: string[] = [],/g/;
if (diagnosisResults.inquiry) {evidences.push()';})'
diagnosisResults.inquiry.extractedSymptoms.map((s) => s).join('、')
}
      )}
    }
    if (diagnosisResults.look) {}
}
    }
    if (diagnosisResults.listen) {}
}
    }
    if (diagnosisResults.palpation) {}
}
    }
    return {const tcmDiagnosis = {}
}
      }
const healthRecommendations = [;]'
        {'category: 'lifestyle,'
const priority = 'medium';
}
}
        }
];
      ],
riskFactors: [],'
const followUpActions = [;]{'}
const priority = 'medium';
}
}
        }
];
      ],
const confidence = 0.85;
    };
  }
  /* 复 */
   */
private generateChatResponseWithDiagnosis(originalMessage: string,,)diagnosisResults: FourDiagnosisResults,);
context: ChatContext,);
const intent = DiagnosisIntent)'
  ): ChatResponse {'let responseText =
const actions: any[] = [];
const suggestions: string[] = [];
if (intent.urgencyLevel === 'high' || intent.urgencyLevel === 'emergency') {';}}'';
}
    } else if (intent.extractedSymptoms.length > 0) {}
}
    } else {}
}
    }
    if (diagnosisResults.integrated) {}
      responseText += `\n\n${diagnosisResults.integrated.overallAssessment}`;````,```;
if (diagnosisResults.integrated.healthRecommendations.length > 0) {diagnosisResults.integrated.healthRecommendations.forEach()}
          (rec, index) => {}
            responseText += `\n${index + 1}. ${rec.title}：${rec.description}`;````;```;
          }
        );
      }
    } else {if (diagnosisResults.inquiry) {}
}
      }
      if (diagnosisResults.look) {}
}
      }
      if (diagnosisResults.listen) {}
}
      }
      if (diagnosisResults.palpation) {}
}
      }
    }
    if (intent.needsInquiry && !diagnosisResults.inquiry) {'actions.push({ ',)type: 'inquiry,')''; });'';
}
        const autoStart = true;)}
      });
    }
    return {const text = responseTextactions,
suggestions,
diagnosisResults,
confidence: intent.confidence,
}
      const timestamp = new Date()}
    };
  }
  /* 复 */
   */
private generateErrorResponse(originalMessage: string,);
const error = any);
  ): ChatResponse {return {}      actions: [],
}
}
      diagnosisResults: {}
confidence: 0,
timestamp: new Date(),
const error = error.message;
    };
  }
  /* 果 */
   */
private hasMultipleDiagnosisResults(results: FourDiagnosisResults): boolean {const resultCount = Object.keys(results).length}
    return resultCount >= 2}
  }
  /* 度 */
   */
private calculateIntentConfidence(symptomCount: number,,)needsInquiry: boolean,
needsLook: boolean,);
needsListen: boolean,);
const needsPalpation = boolean);
  ): number {let confidence = 0.5; // 基础置信度/;}    // 症状数量影响
confidence += Math.min(symptomCount * 0.1, 0.3);
    // 诊断需求影响
const  diagnosisNeeds = []needsInquiry,
needsLook,
needsListen,
needsPalpation];
    ];
const activeNeeds = diagnosisNeeds.filter(Boolean).length;
confidence += activeNeeds * 0.05;
}
    return Math.min(confidence, 1.0)}
  }
  /* 片 */
   */
private selectPrimaryImage(images: ImageData[]): ImageData {// 简单选择第一张图片，后续可以实现更智能的选择逻辑/;}}/g/;
    return images[0]}
  }
  /* 频 */
   */
private selectPrimaryAudio(audioData: AudioData[]): AudioData {// 简单选择第一个音频，后续可以实现更智能的选择逻辑/;}}/g/;
    return audioData[0]}
  }
  /* 据 */
   */
private selectPrimaryPalpationData(palpationData: PalpationData[]);
  ): PalpationData {// 简单选择第一个数据，后续可以实现更智能的选择逻辑/;}}/g/;
    return palpationData[0]}
  }
}
''