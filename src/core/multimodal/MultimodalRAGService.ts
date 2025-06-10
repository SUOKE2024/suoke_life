import { EventEmitter } from "events";
error, (error) => {}")
      this.emit("encodingError", error);
    });
    this.fusion.on(fusionCompleted", (result) => {}")
      this.emit("fusionCompleted, result);"
    });
    this.encoder.on("multimodalEncoded", (embeddings) => {})
      this.emit(embeddingsGenerated", embeddings);"
    });
  }
  /**
* * 初始化服务
  async initialize(): Promise<void> {
    if (this.isInitialized) return;
    try {
      // 初始化编码器
await this.encoder.initialize();
      // 初始化向量数据库索引
await this.initializeVectorDatabase();
      this.isInitialized = true;
      this.emit("initialized);"
    } catch (error) {
      this.emit("error", error);
      throw new Error(`Failed to initialize MultimodalRAGService: ${error;}`);
    }
  }
  /**
* * 初始化向量数据库
  private async initializeVectorDatabase(): Promise<void> {
    try {
      // 为不同模态创建索引
await this.vectorDB.createIndex(768, cosine"); // 文本"
await this.vectorDB.createIndex(512, "cosine); // 舌象"
await this.vectorDB.createIndex(256, "cosine"); // 脉象
await this.vectorDB.createIndex(768, cosine"); // 融合向量"
    } catch (error) {
      }
  }
  /**
* * 多模态查询
  async query(query: MultimodalQuery): Promise<RAGResponse> {
    if (!this.isInitialized) {
      await this.initialize();
    }
    const cacheKey = this.generateQueryCacheKey(query);
    // 检查缓存
if (this.queryCache.has(cacheKey)) {
      const cachedResult = this.queryCache.get(cacheKey)!;
      this.emit("cacheHit", { query, result: cachedResult ;});
      return cachedResult;
    }
    try {
      // 1. 编码多模态输入
const embeddings = await this.encodeQuery(query);
      // 2. 融合多模态嵌入
const fusionResult = await this.fusion.fuseEmbeddings(;)
        embeddings,
        query.strategy || tcm_diagnosis;
      );
      // 3. 向量检索
const retrievalResults = await this.retrieveRelevantDocuments(;)
        fusionResult,
        query.topK || 5,
        query.threshold || 0.7;
      );
      // 4. 生成回答
const generationResult = await this.generateAnswer(;)
        query,
        retrievalResults,
        fusionResult;
      );
      // 5. 构建响应
const response: RAGResponse = {answer: generationResult.answer;
        confidence: this.calculateResponseConfidence(fusionResult, retrievalResults),
        sources: retrievalResults;
        fusionResult,
        reasoning: generationResult.reasoning;
        metadata: {,
  queryModalities: embeddings.map(e => e.modality);
          fusionStrategy: query.strategy || "tcm_diagnosis,"
          retrievalCount: retrievalResults.length;
          timestamp: Date.now();
        }
      };
      // 缓存结果
this.queryCache.set(cacheKey, response);
      this.emit("queryCompleted", { query, response });
      return response;
    } catch (error) {
      this.emit(queryError", { query, error });"
      throw new Error(`Query processing failed: ${error;}`);
    }
  }
  /**
* * 编码查询中的多模态数据
  private async encodeQuery(query: MultimodalQuery): Promise<Embedding[]> {
    const inputs: Array<{ data: any; modality: ModalityType; metadata?: Record<string; any> }> = [];
    // 添加文本模态
if (query.text) {
      inputs.push({
        data: query.text;
        modality: ModalityType.TEXT;
        metadata: { type: "query_text, ...query.metadata ;}"
      });
    }
    // 添加舌象模态
if (query.tongueImage) {
      inputs.push({
        data: query.tongueImage;
        modality: ModalityType.TONGUE;
        metadata: { type: "tongue_image", ...query.metadata ;}
      });
    }
    // 添加脉象模态
if (query.pulseSignal) {
      inputs.push({
        data: query.pulseSignal;
        modality: ModalityType.PULSE;
        metadata: { type: pulse_signal", ...query.metadata ;}"
      });
    }
    if (inputs.length === 0) {
      throw new Error("No valid input modalities provided);"
    }
    return await this.encoder.encodeMultimodal(inputs);
  }
  /**
* * 检索相关文档
  private async retrieveRelevantDocuments()
    fusionResult: FusionResult;
    topK: number;
    threshold: number;
  ): Promise<RetrievalResult[]> {
    try {
      // 使用融合后的嵌入向量进行检索
const results = await this.vectorDB.search(;)
        fusionResult.fusedEmbedding,
        topK,
        { confidence_threshold: threshold ;};
      );
      // 过滤低置信度结果
const filteredResults = results.filter(result => result.score >= threshold);
      this.emit("retrievalCompleted", {
        fusionResult,
        results: filteredResults;
        originalCount: results.length;
        filteredCount: filteredResults.length;
      });
      return filteredResults;
    } catch (error) {
      throw new Error(`Document retrieval failed: ${error;}`);
    }
  }
  /**
* * 生成回答
  private async generateAnswer()
    query: MultimodalQuery;
    retrievalResults: RetrievalResult[];
    fusionResult: FusionResult;
  ): Promise<{ answer: string; reasoning: string ;}> {
    try {
      // 构建上下文
const context = this.buildContext(query, retrievalResults, fusionResult);
      // 构建提示词
const prompt = this.buildPrompt(query, fusionResult);
      // 生成回答和推理过程
const result = await this.languageModel.generateWithReasoning(prompt, context);
      this.emit(answerGenerated", { query, result, context });"
      return result;
    } catch (error) {
      throw new Error(`Answer generation failed: ${error;}`);
    }
  }
  /**
* * 构建上下文
  private buildContext()
    query: MultimodalQuery;
    retrievalResults: RetrievalResult[];
    fusionResult: FusionResult;
  ): string[] {
    const context: string[] = [];
    // 添加检索到的文档内容
retrievalResults.forEach(result, index) => {}))

    });
    // 添加模态信息
const modalityInfo = Object.entries(fusionResult.modalityWeights);
      .map([modality, weight]) => `${modality}: ${(weight * 100).toFixed(1)}%`);
      .join(" );"

    // 添加融合策略信息

    return context;
  }
  /**
* * 构建提示词
  private buildPrompt(query: MultimodalQuery, fusionResult: FusionResult): string {


    if (query.text) {

    ;}
    if (query.tongueImage) {

    }
    if (query.pulseSignal) {

    }







    return prompt;
  }
  /**
* * 计算响应置信度
  private calculateResponseConfidence()
    fusionResult: FusionResult;
    retrievalResults: RetrievalResult[]
  ): number {
    if (retrievalResults.length === 0) return 0;
    // 基于融合置信度和检索结果质量计算总体置信度
const fusionConfidence = fusionResult.confidence;
    const avgRetrievalScore = retrievalResults.reduce(sum, result) => sum + result.score, 0) /     retrievalResults.length;
    const resultCountFactor = Math.min(retrievalResults.length / 5, 1); // 结果数量因子;
return (fusionConfidence * 0.4 + avgRetrievalScore * 0.4 + resultCountFactor * 0.2);
  }
  /**
* * 添加文档到向量数据库
  async addDocument()
    id: string;
    content: string;
    modality: ModalityType;
    metadata: Record<string, any> = {;}
  ): Promise<void> {
    try {
      // 编码文档内容
const embedding = await this.encoder.encodeModality(content, modality, metadata);
      // 存储到向量数据库
await this.vectorDB.insert(id, embedding.vector, {
        ...metadata,
        modality,
        content,
        timestamp: Date.now();
      });
      this.emit("documentAdded", { id, modality, metadata });
    } catch (error) {
      this.emit(documentAddError", { id, error });"
      throw new Error(`Failed to add document: ${error;}`);
    }
  }
  /**
* * 批量添加文档
  async addDocuments()
    documents: Array<{,
  id: string;
  content: string;
  modality: ModalityType;
      metadata?: Record<string; any>;
    }>
  ): Promise<void> {
    const addPromises = documents.map(doc =>;)
      this.addDocument(doc.id, doc.content, doc.modality, doc.metadata);
    );
    try {
      await Promise.all(addPromises);
      this.emit("documentsAdded, { count: documents.length ;});"
    } catch (error) {
      this.emit("documentsAddError", error);
      throw error;
    }
  }
  /**
* * 添加自定义融合策略
  addFusionStrategy(strategy: FusionStrategy): void {
    this.fusion.addStrategy(strategy);
    this.emit(strategyAdded", strategy);"
  }
  /**
* * 获取支持的融合策略
  getSupportedStrategies(): string[] {
    return this.fusion.getSupportedStrategies();
  }
  /**
* * 生成查询缓存键
  private generateQueryCacheKey(query: MultimodalQuery): string {
    const keyParts = [;
      query.text || ",
      query.tongueImage ? "tongue" : ",
      query.pulseSignal ? "pulse : ",
      query.strategy || default",
      query.topK || 5,
      query.threshold || 0.7;
    ];
    return keyParts.join("|);"
  }
  /**
* * 清理缓存
  clearCache(): void {
    this.queryCache.clear();
    this.embeddingCache.clear();
    this.fusion.clearCache();
    this.emit("cacheCleared");
  }
  /**
* * 获取服务统计信息
  getStats(): Record<string, any> {
    return {isInitialized: this.isInitialized,queryCacheSize: this.queryCache.size,embeddingCacheSize: this.embeddingCache.size,supportedStrategies: this.getSupportedStrategies(),supportedModalities: Object.values(ModalityType);
    };
  }
  /**
* * 清理服务
  async cleanup(): Promise<void> {
    try {
      await this.encoder.cleanup();
      this.clearCache();
      this.isInitialized = false;
      this.emit(cleaned");"
    } catch (error) {
      this.emit('error', error);
      throw error;
    }
  }
}  */