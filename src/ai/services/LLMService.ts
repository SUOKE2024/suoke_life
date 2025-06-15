/**
 * LLM服务
 * 集成最新的大语言模型
 */

import { AICache, AIModel, AIPerformance, AIRetry, AITask, AITimeout } from '../decorators/AIDecorators';
import type {
    AIRequest,
    AIResponse,
    AIStreamResponse,
    HealthAnalysisRequest,
    HealthAnalysisResponse,
    IAIService
} from '../types/AITypes';
import { AITaskType, LLMModelType } from '../types/AITypes';

@AIModel(LLMModelType.GPT4O)
export default class LLMService implements IAIService {
  private apiKeys: Map<LLMModelType, string> = new Map();
  private baseUrls: Map<LLMModelType, string> = new Map();
  private initialized = false;

  constructor() {
    this.setupDefaultConfigs();
  }

  private setupDefaultConfigs(): void {
    // OpenAI模型配置
    this.baseUrls.set(LLMModelType.GPT4, 'https://api.openai.com/v1');
    this.baseUrls.set(LLMModelType.GPT4_TURBO, 'https://api.openai.com/v1');
    this.baseUrls.set(LLMModelType.GPT4O, 'https://api.openai.com/v1');

    // Anthropic模型配置
    this.baseUrls.set(LLMModelType.CLAUDE_3_OPUS, 'https://api.anthropic.com');
    this.baseUrls.set(LLMModelType.CLAUDE_3_SONNET, 'https://api.anthropic.com');
    this.baseUrls.set(LLMModelType.CLAUDE_3_HAIKU, 'https://api.anthropic.com');

    // Google模型配置
    this.baseUrls.set(LLMModelType.GEMINI_PRO, 'https://generativelanguage.googleapis.com');
    this.baseUrls.set(LLMModelType.GEMINI_ULTRA, 'https://generativelanguage.googleapis.com');

    // 本地模型配置
    this.baseUrls.set(LLMModelType.LLAMA_3_70B, 'http://localhost:11434');
    this.baseUrls.set(LLMModelType.LLAMA_3_8B, 'http://localhost:11434');
  }

  async initialize(): Promise<void> {
    if (this.initialized) return;

    // 从环境变量或配置中加载API密钥
    this.loadApiKeys();
    
    // 验证模型可用性
    await this.validateModels();
    
    this.initialized = true;
  }

  private loadApiKeys(): void {
    // 这里应该从安全的配置源加载API密钥
    const openaiKey = process.env.OPENAI_API_KEY;
    const anthropicKey = process.env.ANTHROPIC_API_KEY;
    const googleKey = process.env.GOOGLE_API_KEY;

    if (openaiKey) {
      this.apiKeys.set(LLMModelType.GPT4, openaiKey);
      this.apiKeys.set(LLMModelType.GPT4_TURBO, openaiKey);
      this.apiKeys.set(LLMModelType.GPT4O, openaiKey);
    }

    if (anthropicKey) {
      this.apiKeys.set(LLMModelType.CLAUDE_3_OPUS, anthropicKey);
      this.apiKeys.set(LLMModelType.CLAUDE_3_SONNET, anthropicKey);
      this.apiKeys.set(LLMModelType.CLAUDE_3_HAIKU, anthropicKey);
    }

    if (googleKey) {
      this.apiKeys.set(LLMModelType.GEMINI_PRO, googleKey);
      this.apiKeys.set(LLMModelType.GEMINI_ULTRA, googleKey);
    }
  }

  private async validateModels(): Promise<void> {
    // 验证关键模型的可用性
    const criticalModels = [LLMModelType.GPT4O, LLMModelType.CLAUDE_3_SONNET];
    
    for (const model of criticalModels) {
      try {
        await this.testModel(model);
      } catch (error) {
        console.warn(`Model ${model} validation failed:`, error);
      }
    }
  }

  private async testModel(modelType: LLMModelType): Promise<void> {
    const testRequest: AIRequest = {
      taskType: AITaskType.TEXT_GENERATION,
      input: 'Hello',
      modelConfig: { modelType, maxTokens: 10 }
    };

    await this.process(testRequest);
  }

  @AIPerformance()
  @AITimeout(30000)
  @AIRetry(3)
  async process(request: AIRequest): Promise<AIResponse> {
    if (!this.initialized) {
      await this.initialize();
    }

    const startTime = Date.now();
    const modelType = request.modelConfig?.modelType || LLMModelType.GPT4O;

    try {
      let response: any;

      switch (modelType) {
        case LLMModelType.GPT4:
        case LLMModelType.GPT4_TURBO:
        case LLMModelType.GPT4O:
          response = await this.processOpenAI(request, modelType);
          break;
        
        case LLMModelType.CLAUDE_3_OPUS:
        case LLMModelType.CLAUDE_3_SONNET:
        case LLMModelType.CLAUDE_3_HAIKU:
          response = await this.processAnthropic(request, modelType);
          break;
        
        case LLMModelType.GEMINI_PRO:
        case LLMModelType.GEMINI_ULTRA:
          response = await this.processGoogle(request, modelType);
          break;
        
        case LLMModelType.LLAMA_3_70B:
        case LLMModelType.LLAMA_3_8B:
          response = await this.processOllama(request, modelType);
          break;
        
        default:
          throw new Error(`Unsupported model type: ${modelType}`);
      }

      return {
        success: true,
        data: response.content,
        metadata: {
          modelUsed: modelType,
          tokensUsed: response.tokensUsed,
          processingTime: Date.now() - startTime,
          confidence: response.confidence
        }
      };

    } catch (error) {
      return {
        success: false,
        error: (error as Error).message,
        metadata: {
          modelUsed: modelType,
          processingTime: Date.now() - startTime
        }
      };
    }
  }

  @AITask(AITaskType.TEXT_GENERATION)
  private async processOpenAI(request: AIRequest, modelType: LLMModelType): Promise<any> {
    const apiKey = this.apiKeys.get(modelType);
    if (!apiKey) {
      throw new Error(`No API key configured for ${modelType}`);
    }

    const response = await fetch(`${this.baseUrls.get(modelType)}/chat/completions`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: modelType,
        messages: [{ role: 'user', content: request.input }],
        max_tokens: request.modelConfig?.maxTokens || 1000,
        temperature: request.modelConfig?.temperature || 0.7
      })
    });

    if (!response.ok) {
      throw new Error(`OpenAI API error: ${response.statusText}`);
    }

    const data = await response.json();
    return {
      content: data.choices[0].message.content,
      tokensUsed: data.usage.total_tokens,
      confidence: 0.9
    };
  }

  @AITask(AITaskType.TEXT_GENERATION)
  private async processAnthropic(request: AIRequest, modelType: LLMModelType): Promise<any> {
    const apiKey = this.apiKeys.get(modelType);
    if (!apiKey) {
      throw new Error(`No API key configured for ${modelType}`);
    }

    const response = await fetch(`${this.baseUrls.get(modelType)}/v1/messages`, {
      method: 'POST',
      headers: {
        'x-api-key': apiKey,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: modelType,
        max_tokens: request.modelConfig?.maxTokens || 1000,
        messages: [{ role: 'user', content: request.input }]
      })
    });

    if (!response.ok) {
      throw new Error(`Anthropic API error: ${response.statusText}`);
    }

    const data = await response.json();
    return {
      content: data.content[0].text,
      tokensUsed: data.usage.input_tokens + data.usage.output_tokens,
      confidence: 0.95
    };
  }

  @AITask(AITaskType.TEXT_GENERATION)
  private async processGoogle(request: AIRequest, modelType: LLMModelType): Promise<any> {
    const apiKey = this.apiKeys.get(modelType);
    if (!apiKey) {
      throw new Error(`No API key configured for ${modelType}`);
    }

    const response = await fetch(
      `${this.baseUrls.get(modelType)}/v1beta/models/${modelType}:generateContent?key=${apiKey}`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          contents: [{ parts: [{ text: request.input }] }],
          generationConfig: {
            maxOutputTokens: request.modelConfig?.maxTokens || 1000,
            temperature: request.modelConfig?.temperature || 0.7
          }
        })
      }
    );

    if (!response.ok) {
      throw new Error(`Google API error: ${response.statusText}`);
    }

    const data = await response.json();
    return {
      content: data.candidates[0].content.parts[0].text,
      tokensUsed: data.usageMetadata?.totalTokenCount || 0,
      confidence: 0.9
    };
  }

  @AITask(AITaskType.TEXT_GENERATION)
  private async processOllama(request: AIRequest, modelType: LLMModelType): Promise<any> {
    const response = await fetch(`${this.baseUrls.get(modelType)}/api/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: modelType,
        prompt: request.input,
        stream: false,
        options: {
          num_predict: request.modelConfig?.maxTokens || 1000,
          temperature: request.modelConfig?.temperature || 0.7
        }
      })
    });

    if (!response.ok) {
      throw new Error(`Ollama API error: ${response.statusText}`);
    }

    const data = await response.json();
    return {
      content: data.response,
      tokensUsed: data.eval_count || 0,
      confidence: 0.85
    };
  }

  async *processStream(request: AIRequest): AsyncGenerator<AIStreamResponse> {
    // 流式处理实现
    const modelType = request.modelConfig?.modelType || LLMModelType.GPT4O;
    
    // 这里实现流式响应逻辑
    yield {
      chunk: "流式响应开始...",
      isComplete: false
    };

    yield {
      chunk: "处理完成",
      isComplete: true
    };
  }

  @AITask(AITaskType.HEALTH_ANALYSIS)
  @AICache(true)
  async analyzeHealth(request: HealthAnalysisRequest): Promise<HealthAnalysisResponse> {
    const prompt = this.buildHealthAnalysisPrompt(request);
    
    const aiRequest: AIRequest = {
      taskType: AITaskType.HEALTH_ANALYSIS,
      input: prompt,
      modelConfig: {
        modelType: LLMModelType.GPT4O,
        maxTokens: 2000,
        temperature: 0.3
      }
    };

    const response = await this.process(aiRequest);
    
    if (!response.success) {
      throw new Error(response.error);
    }

    return this.parseHealthAnalysisResponse(response.data);
  }

  private buildHealthAnalysisPrompt(request: HealthAnalysisRequest): string {
    const { patientData, analysisType } = request;
    
    return `
作为专业的健康分析AI，请分析以下患者信息：

患者信息：
- 年龄：${patientData.age}
- 性别：${patientData.gender}
- 症状：${patientData.symptoms.join(', ')}
- 生命体征：${JSON.stringify(patientData.vitalSigns || {})}
- 病史：${patientData.medicalHistory?.join(', ') || '无'}

分析类型：${analysisType}

请提供：
1. 可能的诊断
2. 置信度评估
3. 治疗建议
4. 风险因素
5. 后续行动建议
${analysisType === 'tcm' || analysisType === 'integrated' ? '6. 中医辨证分析（证候、体质、治法）' : ''}

请以JSON格式返回结果。
    `;
  }

  private parseHealthAnalysisResponse(responseData: string): HealthAnalysisResponse {
    try {
      const parsed = JSON.parse(responseData);
      return {
        success: true,
        data: {
          diagnosis: parsed.diagnosis || '',
          confidence: parsed.confidence || 0.5,
          recommendations: parsed.recommendations || [],
          riskFactors: parsed.riskFactors || [],
          followUpActions: parsed.followUpActions || [],
          tcmAnalysis: parsed.tcmAnalysis
        }
      };
    } catch (error) {
      // 如果JSON解析失败，尝试从文本中提取信息
      return {
        success: true,
        data: {
          diagnosis: responseData.substring(0, 200),
          confidence: 0.7,
          recommendations: ['请咨询专业医生'],
          riskFactors: [],
          followUpActions: ['定期复查']
        }
      };
    }
  }

  async dispose(): Promise<void> {
    this.apiKeys.clear();
    this.baseUrls.clear();
    this.initialized = false;
  }
} 