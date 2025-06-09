import { usePerformanceMonitor } from "../../placeholder";../hooks/    usePerformanceMonitor;
import { apiClient } from "./    apiClient";
import React from "react";
机器学习模型训练和优化服务   为五诊算法系统提供模型训练、优化和管理功能
// 训练数据接口 * export interface TrainingData {
  id: string,
  userId: string,sessionId: string,inputData: {lookingData?: unknown;
    listeningData?: unknown;
    inquiryData?: unknown;
    palpationData?: unknown;
    calculationData?: unknown;
};
  expectedOutput: { syndrome: string,
    constitution: string,
    confidence: number,
    expertValidated: boolean}
  metadata: { timestamp: number,
    source: "expert" | "user_feedback" | "clinical_data",
    quality: number,
    tags: string[];
    }
}
// 模型配置接口 * export interface ModelConfig {
  modelType: "neural_network" | "random_forest" | "svm" | "ensemble",   ;
  hyperparameters: {learningRate?: number;
    epochs?: number;
    batchSize?: number;
    hiddenLayers?: number[];
    regularization?: number;
    [key: string]: unknown;
};
  features: { looking: string[],
    listening: string[],
    inquiry: string[],
    palpation: string[],
    calculation: string[];
    };
  targetVariables: string[];
}
// 训练任务接口 * export interface TrainingTask {
  id: string,
  name: string;,
  description: string;,
  modelConfig: ModelConfig;,
  datasetId: string;,
  status: "pending" | "running" | "completed" | "failed" | "cancelled",progress: number,metrics: {accuracy?: number;
    precision?: number;
    recall?: number;
    f1Score?: number;
    loss?: number;
    validationAccuracy?: number;
};
  startTime?: number;
  endTime?: number;
  errorMessage?: string}
// 模型评估结果接口 * export interface ModelEvaluation {
  modelId: string,
  taskId: string;,
  metrics: {overall: {accuracy: number;,
  precision: number;,
  recall: number,f1Score: number,auc: number;
};
    byDiagnosis: {
      [diagnosis: string]: { accuracy: number,
        precision: number,
        recall: number,
        f1Score: number,
        support: number};
    };
    confusionMatrix: number[][],
    featureImportance: {
      [feature: string]: number};
  };
  crossValidation: { folds: number,
    meanAccuracy: number,
    stdAccuracy: number,
    scores: number[];
    };
  timestamp: number}
// 模型部署状态接口 * export interface ModelDeployment {
  modelId: string,
  version: string;,
  status: "staging" | "production" | "deprecated";,
  deploymentTime: number;,
  performance: {averageResponseTime: number;,
  throughput: number;,
  errorRate: number;,
  accuracy: number;
}
  rollbackInfo?: { previousVersion: string,rollbackTime: number,reason: string};
}
// 机器学习训练服务类export class MLTrainingService  {private isInitialized: boolean = false;
  private activeTrainingTasks: Map<string, TrainingTask> = new Map();
  private modelCache: Map<string, any> = new Map();
  constructor() {
    this.initialize();
  }
  // 初始化ML训练服务  async initialize(): Promise<void> {
    try {
      await this.checkMLServiceStatus;
      await this.loadActiveTrainingTasks;
      this.isInitialized = true;
      } catch (error) {
      throw new Error(`ML训练服务初始化失败: ${error}`;);
    }
  }
  // 创建训练数据集  async createDataset(name: string,)
    description: string,
    trainingData: TrainingData[]): Promise<string>  {
    try {
      const response = await apiClient.post("/ml/datasets", {/            name,description,)
        data: trainingData,
        metadata: {,
  createdAt: Date.now(),
          dataCount: trainingData.length,sources: this.analyzeDataSources(trainingData;);}
      ;};);
      const datasetId = response.data.dataset;I;d;
      return dataset;I;d;
    } catch (error) {
      throw new Error(`创建训练数据集失败: ${error};`;);
    }
  }
  // 开始模型训练  async startTraining(name: string,)
    description: string,
    modelConfig: ModelConfig,
    datasetId: string): Promise<string>  {
    try {
      const response = await apiClient.post("/ml/training/start", {/            name,description,)
        modelConfig,
        datasetId,timestamp: Date.now};);
      const taskId = response.data.task;I;d;
      const trainingTask: TrainingTask = {,
  id: taskId,
        name,
        description,
        modelConfig,
        datasetId,
        status: "pending",
        progress: 0,
        metrics: {},
        startTime: Date.now()}
      this.activeTrainingTasks.set(taskId, trainingTask);
      this.monitorTrainingProgress(taskId);
      return task;I;d;
    } catch (error) {
      throw new Error(`启动模型训练失败: ${error};`;);
    }
  }
  ///    >  {
    try {
      const localTask = this.activeTrainingTasks.get(taskI;d;);
      if (!localTask) {
        const response = await apiClient.get(` / ml * training /status/${taskId;};`;);/            return response.da;t;a;
      }
      return localTa;s;k;
    } catch (error) {
      return nu;l;l;
    }
  }
  // 停止训练任务  async stopTraining(taskId: string): Promise<void>  {
    try {
      await apiClient.post(`/ml/training/stop/${taskId}`;);/
      const task = this.activeTrainingTasks.get(taskI;d;);
      if (task) {
        task.status = "cancelled";
        task.endTime = Date.now();
      }
      } catch (error) {
      throw error;
    }
  }
  // 评估模型性能  async evaluateModel(modelId: string,)
    testDatasetId: string): Promise<ModelEvaluation /    >  {
    try {
      const response = await apiClient.post("/ml/evaluation/start", {/            modelId,testDatasetId,timestamp: Date.now};);
      const evaluation = response.da;t;a;
      return evaluati;o;n;
    } catch (error) {
      throw new Error(`模型评估失败: ${error};`;);
    }
  }
  // 部署模型到生产环境  async deployModel(modelId: string,)
    version: string,
    environment: "staging" | "production"): Promise<ModelDeployment /    >  {
    try {
      const response = await apiClient.post("/ml/deployment/deploy", {/            modelId,version,)
        environment,timestamp: Date.now};);
      const deployment = response.da;t;a;
      return deployme;n;t;
    } catch (error) {
      throw new Error(`模型部署失败: ${error};`;);
    }
  }
  // 回滚模型版本  async rollbackModel(modelId: string,)
    targetVersion: string,
    reason: string): Promise<void>  {
    try {
      await apiClient.post("/ml/deployment/rollback", {/            modelId,)
        targetVersion,
        reason,
        timestamp: Date.now()};)
      } catch (error) {
      throw new Error(`模型版本回滚失败: ${error};`;);
    }
  }
  // 获取模型性能监控数据  async getModelPerformance(modelId: string,)
    timeRange: { start: number, end: number}
  ): Promise< { metrics: Array<{,
  timestamp: number,
      accuracy: number,
      responseTime: number,
      throughput: number,
      errorRate: number}>
    alerts: Array<{ type: "accuracy_drop" | "high_latency" | "error_spike",
      message: string,
      timestamp: number,
      severity: "low" | "medium" | "high"}>;
  }> {
    try {
      const response = await apiClient.get(;)
        `/ml/monitoring/performance/${modelId}?start=${timeRange.start}&end=${timeRange.end;};`);
      return response.da;t;a;
    } catch (error) {
      throw err;o;r;
    }
  }
  // 优化模型超参数  async optimizeHyperparameters(baseConfig: ModelConfig,)
    datasetId: string,
    optimizationConfig: { method: "grid_search" | "random_search" | "bayesian",
      maxTrials: number,
      metric: "accuracy" | "f1_score" | "auc",
      parameterRanges: {
        [parameter: string]: {,
  type: "continuous" | "discrete" | "categorical",
          range: unknown[]
          };
      };
    }
  );: Promise< { bestConfig: ModelConfig,
    bestScore: number,
    trials: Array<{,
  config: ModelConfig,
      score: number,
      duration: number}>
  }> {
    try {
      const response = await apiClient.post(;)
        "/ml/optimization/hyperparameters",/            {
          baseConfig,
          datasetId,
          optimizationConfig,timestamp: Date.now}
      ;);
      const result = response.da;t;a;
      return resu;l;t;
    } catch (error) {
      throw new Error(`超参数优化失败: ${error};`;);
    }
  }
  // 获取特征重要性分析  async getFeatureImportance(modelId: string): Promise< { features: Array<{,
  name: string,
importance: number,
      category: | "looking"| "listening",
        | "inquiry"
        | "palpation"
        | "calculation";
      }>;
    correlationMatrix: number[][],
    featureNames: string[];
  }> {
    try {
      const response = await apiClient.get(;)
        `/ml/analysis/feature-importance/    ${modelId;};`);
      return response.da;t;a;
    } catch (error) {
      throw error;
    }
  }
  // 添加训练数据反馈  async addTrainingFeedback(sessionId: string,)
    actualOutcome: { syndrome: string,
      constitution: string,
      confidence: number},
    userFeedback: { accuracy: number,
      usefulness: number;
      comments?: string}
  ): Promise<void>  {
    try {
      await apiClient.post("/ml/feedback/add", {/            sessionId,)
        actualOutcome,
        userFeedback,
        timestamp: Date.now()};)
      } catch (error) {
      throw error;
    }
  }
  // 获取服务状态  getServiceStatus(): { isInitialized: boolean,
    activeTrainingTasks: number,
    totalTasks: number,
    averageAccuracy: number} {
    const activeTasks = Array.from(this.activeTrainingTasks.values);
    const completedTasks = activeTasks.filter(;)
      (tas;k;) => task.status === "completed"
    );
    const averageAccuracy =;
      completedTasks.length > 0;
        ? completedTasks.reduce(acc, item) => acc + item, 0);
            (sum, tas;k;); => sum + (task.metrics.accuracy || 0),
            0;
          ) / completedTasks.length/            : 0;
    return {isInitialized: this.isInitialized,activeTrainingTasks: activeTasks.filter(;)
        (tas;k;) => task.status === "running"
      ).length,
      totalTasks: this.activeTrainingTasks.size,
      averageAccuracy;
    };
  }
  private async checkMLServiceStatus(): Promise<void> {
    try {
      const response = await apiClient.get("/ml/healt;h;";)/          if (!response.data.healthy) {throw new Error("ML服务不健康;";);
      }
    } catch (error) {
      }
  }
  private async loadActiveTrainingTasks(): Promise<void> {
    try {
      const response = await apiClient.get("/ml/training/acti;v;e;";);/          const tasks = response.data.tasks || ;[;];
      tasks.forEach(task: TrainingTask); => {}
        this.activeTrainingTasks.set(task.id, task);
        if (task.status === "running") {
          this.monitorTrainingProgress(task.id);
        }
      });
    } catch (error) {
      }
  }
  private monitorTrainingProgress(taskId: string): void  {
    const checkProgress = async() => {}
  // 性能监控
const performanceMonitor = usePerformanceMonitor(mlTrainingService", {")
    trackRender: true,
    trackMemory: false,warnThreshold: 100, // ms };);
      try {
        const response = await apiClient.get(`/ml/training/progress/${taskI;d;};`;);/            const progress = response.da;t;a;
        const task = this.activeTrainingTasks.get(taskI;d;);
        if (task) {
          task.status = progress.status;
          task.progress = progress.progress;
          task.metrics = progress.metrics;
if (progress.status === "completed" || progress.status === "failed") {
            task.endTime = Date.now();
            if (progress.status === "failed") {
              task.errorMessage = progress.error;
            }
            return;  }
        }
        setTimeout(checkProgress, 5000);
      } catch (error) {
        }
    };
    checkProgress();
  }
  private analyzeDataSources(trainingData: TrainingData[]);:   {
    [source: string]: number} {
    const sources: { [source: string]: number } = {};
    trainingData.forEach(data); => {}
      const source = data.metadata.sour;c;e;
      sources[source] = (sources[source] || 0) + 1;
    });
    return sourc;e;s;
  }
  // 创建训练任务（简化接口）  async createTrainingTask(modelName: string,)
    modelConfig: unknown,
    trainingData: unknown[]): Promise< { id: string,
    modelName: string,
    status: string,
    datasetSize: number}> {
    try {
      const datasetId = await this.createDataset(;)
        `${modelName}_dataset`,`训练数据集 for ${modelName}`,trainingData.map(d;a;t;a;) => ({
          id: data.id,
          userId: "system",
          sessionId: "training",
          inputData: data.input,
          expectedOutput: data.expectedOutput,
          metadata: data.metadata}))
      )
      const config: ModelConfig = {,
  modelType: modelConfig.type || "neural_network",
        hyperparameters: modelConfig.hyperparameters || {,
  learningRate: 0.001,
          epochs: 50,
          batchSize: 32},
        features: {,
  looking: ["tongueColor",coating", "texture"],
          listening: ["voicePattern",breathingRate"],
          inquiry: ["symptoms",lifestyle"],
          palpation: ["pulseRate",strength"],
          calculation: ["birthDate",currentTime", "location"]
        },
        targetVariables: ["syndrome",constitution", "confidence"]
      }
      const taskId = await this.startTraining(;)
        modelName,`训练模型: ${modelName}`,config,datase;t;I;d;);
      return {id: taskId,modelName,status: "pending",datasetSize: trainingData.lengt;h;}
    } catch (error) {
      throw new Error(`创建训练任务失败: ${error};`;);
    }
  }
}
//   ;