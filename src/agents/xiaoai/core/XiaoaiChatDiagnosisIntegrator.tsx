import { diagnosisServiceClient } from ../services/    DiagnosisServiceClient;
import React from "react";
/
  ChatContext,
  ChatResponse,
  DiagnosisIntent,
  FourDiagnosisResults,
  IntegratedDiagnosis,
  DiagnosisAction,
  ImageData,
  AudioData,
  PalpationData,
  InquiryResult,
  LookResult,
  ListenResult,
  { PalpationResult } from "../types;//
* 负责在聊天过程中智能识别并调用相应的四诊服务
export class XiaoaiChatDiagnosisIntegrator   {private activeSessions: Map<string, any> = new Map();
  // 处理聊天消息，智能调用四诊服务  async processChatMessage(message: string,)
    context: ChatContext);: Promise<ChatResponse /    >  {
    try {
      const diagnosisIntent = await this.analyzeDiagnosisIntent(message, conte;x;t;);
      const diagnosisResults: FourDiagnosisResults = {}
      if (diagnosisIntent.needsInquiry) {
        diagnosisResults.inquiry = await this.performInquiry(context.userId, messag;e;);
      }
      if (diagnosisIntent.needsLookDiagnosis && context.hasImages && context.images) {
        diagnosisResults.look = await this.performLookDiagnosis(context.image;s;);
      }
      if (diagnosisIntent.needsListenDiagnosis && context.hasAudio && context.audio) {
        diagnosisResults.listen = await this.performListenDiagnosis(context.audi;o;);
      }
      if (diagnosisIntent.needsPalpationDiagnosis && context.hasPalpationData && context.palpationData) {
        diagnosisResults.palpation = await this.performPalpationDiagnosis(context.palpationDat;a;);
      }
      if (this.hasMultipleDiagnosisResults(diagnosisResults)) {
        diagnosisResults.integrated = await this.performFourDiagnosisIntegration(diagnosisResult;s;);
      }
      return this.generateChatResponseWithDiagnosis(message, diagnosisResults, context, diagnosisIntent;);
    } catch (error) {
      return this.generateErrorResponse(message, erro;r;);
    }
  }
  // 分析用户消息的四诊意图  private async analyzeDiagnosisIntent(message: string,)
    context: ChatContext): Promise<DiagnosisIntent /    >  {
    const symptomKeywords = [;
      咳嗽", "胸闷, "头痛", " 发热", "乏力, "失眠", " 腹痛", "恶心, "呕吐", "腹泻", "便秘, "心悸", " 气短", "眩晕, "耳鸣", " 视力模糊", "关节痛,"肌肉痛", " 皮疹", "瘙痒, "出汗", " 怕冷", "怕热, "口干", " 口苦", "食欲不振, "消化不良", " 月经不调", "痛经,";];
    const extractedSymptoms = symptomKeywords.filter(keyword => {};)
      message.includes(keywor;d;);
    )
    const emergencyKeywords = ["急性", " 剧烈", "严重, "突然", " 无法忍受", "呼吸困难];
    const urgencyLevel = emergencyKeywords.some(keyword => message.includes(keywor;d;););
      ? "high" : extractedSymptoms.length > 0 ? medium" : "low;
    const needsInquiry = extractedSymptoms.length > 0 ||;
                        message.includes("症状;";) ||
                        message.includes(不舒服") ||"
                        message.includes("身体) ||"
                        message.includes("健康");
    const needsLookDiagnosis = context.hasImages ||;
                              message.includes(看看;";) ||"
                              message.includes("舌头) ||"
                              message.includes("面色") ||
                              message.includes(照片");"
    const needsListenDiagnosis = context.hasAudio ||;
                                message.includes("听听;) ||"
                                message.includes("声音") ||
                                message.includes(咳嗽声") ||"
                                message.includes("录音);"
    const needsPalpationDiagnosis = context.hasPalpationData ||;
                                  message.includes("脉搏;";) ||
                                  message.includes(按压") ||"
                                  message.includes("触诊);"
    const confidence = this.calculateIntentConfidence(;)
      extractedSymptoms.length,needsInquiry,needsLookDiagnosis,needsListenDiagnosis,needsPalpationDiagnosi;s;);
    return {needsInquiry,needsLookDiagnosis,needsListenDiagnosis,needsPalpationDiagnosis,confidence,extractedSymptoms,urgencyLevel: urgencyLevel as "low" | medium" | "high | "emergency"};
  }
  ///    >  {
    try {
      let sessionId = this.activeSessions.get(`inquiry_${userId}`);
      if (!sessionId) {
        const sessionResponse = await diagnosisServiceClient.inquiry.startSession(user;I;d;);
        sessionId = sessionResponse.session_id;
        this.activeSessions.set(`inquiry_${userId}`, sessionId);
      }
      await diagnosisServiceClient.inquiry.interact(sessionId, message;);
      / 这里可能需要调用一个获取当前状态的API，而不是结束会话*  暂时使用模拟数据* ///;
        sessionId,detectedSymptoms: [;],
        tcmPatterns: [],
        healthProfile: {} as any,
        recommendations: [],
        confidence: 0.8;
      }
    } catch (error) {
      throw error;
    }
  }
  ///    >  {
    try {
      const primaryImage = this.selectPrimaryImage(images;);
      return await diagnosisServiceClient.look.analyzeImage(primaryIm;a;g;e;);
    } catch (error) {
      throw error;
    }
  }
  ///    >  {
    try {
      const primaryAudio = this.selectPrimaryAudio(audioData;);
      return await diagnosisServiceClient.listen.analyzeAudio(primaryAu;d;i;o;);
    } catch (error) {
      throw error;
    }
  }
  ///    >  {
    try {
      const primaryData = this.selectPrimaryPalpationData(palpationData;);
      return await diagnosisServiceClient.palpation.analyzePalpation(primaryD;a;t;a;);
    } catch (error) {
      throw error;
    }
  }
  ///    >  {
    / 目前返回模拟数据，后续需要实现真正的中医四诊合参算法* ///
    const evidences: string[] = [];
    if (diagnosisResults.inquiry) {
      evidences.push("问诊： + diagnosisResults.inquiry.detectedSymptoms.map(s => s.name).join("、"))"
    }
    if (diagnosisResults.look) {
      evidences.push(望诊：" + diagnosisResults.look.overallAssessment)"
    }
    if (diagnosisResults.listen) {
      evidences.push("闻诊： + diagnosisResults.listen.overallAssessment)"
    }
    if (diagnosisResults.palpation) {
      evidences.push("切诊：" + diagnosisResults.palpation.overallAssessment);
    }
    return { overallAssessment: `综合四诊分析：${evidences.join(；")  }`,";
      tcmDiagnosis: {
      syndrome: "待进一步分析,",
      pathogenesis: "基于四诊合参的病机分析", "treatment: 个性化治疗方案",;
        prognosis: "良好},";
      healthRecommendations;: ;[{
      category: "lifestyle",
      title: 生活方式调整",
          description: "基于四诊结果的生活建议,",
          priority: "medium",
          timeframe: 1-2周""
        }
      ],
      riskFactors: [],
      followUpActions: [{,
  action: "定期复查,",
          timeframe: "1周后",
          priority: medium",
          description: "观察症状变化"
        }
      ],
      confidence: 0.85;
    };
  }
  // 生成包含诊断结果的聊天回复  private generateChatResponseWithDiagnosis(originalMessage: string,)
    diagnosisResults: FourDiagnosisResults,
    context: ChatContext,
    intent: DiagnosisIntent);: ChatResponse  {
    let responseText = ;
    const actions: DiagnosisAction[] = [];
    const suggestions: string[] = [];
    if (intent.urgencyLevel === high" || intent.urgencyLevel === "emergency) {
      responseText = "我注意到你描述的症状比较严重，让我立即为你进行详细分析。"
    } else if (intent.extractedSymptoms.length > 0) {
      responseText = `我了解到你有${intent.extractedSymptoms.join(、")}等症状，让我帮你分析一下。`"
    } else {
      responseText = "我来帮你了解一下你的健康状况。"
    }
    if (diagnosisResults.integrated) {
      responseText += `\n\n${diagnosisResults.integrated.overallAssessment}`
      if (diagnosisResults.integrated.healthRecommendations.length > 0) {
        responseText += "\n\n我的建议："
        diagnosisResults.integrated.healthRecommendations.forEach(((rec, index) => {}))
          responseText += `\n${index + 1}. ${rec.title}：${rec.description}`;
        });
      }
    } else {
      if (diagnosisResults.inquiry) {
        responseText += \n\n基于我们的对话，我了解了你的症状情况。""
      }
      if (diagnosisResults.look) {
        responseText += "\n\n从你提供的图片来看： + diagnosisResults.look.overallAssessment"
      }
      if (diagnosisResults.listen) {
        responseText += "\n\n从你的声音分析：" + diagnosisResults.listen.overallAssessment;
      }
      if (diagnosisResults.palpation) {
        responseText += \n\n触诊数据显示：" + diagnosisResults.palpation.overallAssessment"
      }
    }
    if (intent.needsInquiry && !diagnosisResults.inquiry) {
      actions.push({
      type: "inquiry,",
      prompt: "我想了解一下你的具体症状，可以详细说说吗？",
        autoStart: true,
        priority: 1;
      });
    }
    if (intent.needsLookDiagnosis && !diagnosisResults.look) {
      actions.push({
        type: look",
        prompt: "如果方便的话，可以拍张舌头的照片让我看看吗？,",
        optional: true,
        priority: 2;
      });
    }
    if (intent.needsListenDiagnosis && !diagnosisResults.listen) {
      actions.push({
      type: "listen",
      prompt: 可以录一段咳嗽声或者说话声让我听听吗？",
        optional: true,
        priority: 3;
      });
    }
    suggestions.push("继续描述症状) "
    suggestions.push("上传相关图片");
    suggestions.push(录制音频")"
    suggestions.push("查看详细报告)"
    return {text: responseText,actions,suggestions,diagnosisResults,timestamp: Date.now(;);};
  }
  // 生成错误回复  private generateErrorResponse(message: string, error: unknown): ChatResponse  {
    return {
      text: "抱歉，我在分析你的情况时遇到了一些技术问题。请稍后再试，或者换个方式描述你的症状。", "
      suggestions: [重新描述症状", "稍后再试, "联系技术支持"],timestamp: Date.now();};
  }
  // 辅助方法  private calculateIntentConfidence(symptomCount: number,)
    needsInquiry: boolean,
    needsLook: boolean,
    needsListen: boolean,
    needsPalpation: boolean);: number  {
    let confidence = 0;.;5;  /
    confidence += symptomCount * 0.1  confidence += (needsInquiry ? 0.2 : 0)
    confidence += (needsLook ? 0.1 : 0);
    confidence += (needsListen ? 0.1 : 0);
    confidence += (needsPalpation ? 0.1 : 0);
    return Math.min(confidence, 1.;0;);
  }
  private hasMultipleDiagnosisResults(results: FourDiagnosisResults);: boolean  {
    const count = [results.inquiry, results.look, results.listen, results.palpation];
      .filter(result => result !== undefined).leng;t;h;
    return count ;> ;1;
  }
  private selectPrimaryImage(images: ImageData[]): ImageData  {
    const tongueImage = images.find(img => img.type === tongue";); "
    if (tongueImage) {return tongueIma;g;e}
    const faceImage = images.find(img => img.type === "face;);"
    if (faceImage) {return faceIma;g;e;}
    return images[0];
  }
  private selectPrimaryAudio(audioData: AudioData[]): AudioData  {
    const coughAudio = audioData.find(audio => audio.type === "cough";);
    if (coughAudio) {return coughAud;i;o}
    const voiceAudio = audioData.find(audio => audio.type === voice;";);"
    if (voiceAudio) {return voiceAud;i;o;}
    return audioData[0];
  }
  private selectPrimaryPalpationData(palpationData: PalpationData[]): PalpationData  {
    const pulseData = palpationData.find(data => data.type === "pulse); "
    if (pulseData) {return pulseDa;t;a;}
    return palpationData[0];
  }
  //
    if (sessionType) {
      this.activeSessions.delete(`${sessionType}_${userId}`);
    } else {
      const keysToDelete = Array.from(this.activeSessions.keys(;))
        .filter(key => key.endsWith(`_${userId}`););
      keysToDelete.forEach(key => this.activeSessions.delete(key););
    }
  }
  // 获取活跃会话状态  getActiveSessionsStatus(userId: string):   { [key: string]: unknown } {
    const userSessions: { [key: string]: unknown } = {};
    this.activeSessions.forEach(((sessionId, key) => {}))
      if (key.endsWith(`_${userId}`)) {
        const sessionType = key.replace(`_${userId}`, "';);"'
        userSessions[sessionType] = sessionId;
      }
    });
    return userSessio;n;s;
  }
}