import { apiClient } from "./apiClient";

/**
 * 机器学习模型训练和优化服务
 * 为五诊算法系统提供模型训练、优化和管理功能
 */

// 训练数据接口
export interface TrainingData {
  id: string;
  userId: string;
  sessionId: string;
  inputData: {
    lookingData?: any;
    listeningData?: any;
    inquiryData?: any;
    palpationData?: any;
    calculationData?: any;
  };
  expectedOutput: {
    syndrome: string;
    constitution: string;
    confidence: number;
    expertValidated: boolean;
  };
  metadata: {
    timestamp: number;
    source: "expert" | "user_feedback" | "clinical_data";
    quality: number;
    tags: string[];
  };
}

// 模型配置接口
export interface ModelConfig {
  modelType: "neural_network" | "random_forest" | "svm" | "ensemble";
  hyperparameters: {
    learningRate?: number;
    epochs?: number;
    batchSize?: number;
    hiddenLayers?: number[];
    regularization?: number;
    [key: string]: any;
  };
  features: {
    looking: string[];
    listening: string[];
    inquiry: string[];
    palpation: string[];
    calculation: string[];
  };
  targetVariables: string[];
}

// 训练任务接口
export interface TrainingTask {
  id: string;
  name: string;
  description: string;
  modelConfig: ModelConfig;
  datasetId: string;
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  progress: number;
  metrics: {
    accuracy?: number;
    precision?: number;
    recall?: number;
    f1Score?: number;
    loss?: number;
    validationAccuracy?: number;
  };
  startTime?: number;
  endTime?: number;
  errorMessage?: string;
}

// 模型评估结果接口
export interface ModelEvaluation {
  modelId: string;
  taskId: string;
  metrics: {
    overall: {
      accuracy: number;
      precision: number;
      recall: number;
      f1Score: number;
      auc: number;
    };
    byDiagnosis: {
      [diagnosis: string]: {
        accuracy: number;
        precision: number;
        recall: number;
        f1Score: number;
        support: number;
      };
    };
    confusionMatrix: number[][];
    featureImportance: {
      [feature: string]: number;
    };
  };
  crossValidation: {
    folds: number;
    meanAccuracy: number;
    stdAccuracy: number;
    scores: number[];
  };
  timestamp: number;
}

// 模型部署状态接口
export interface ModelDeployment {
  modelId: string;
  version: string;
  status: "staging" | "production" | "deprecated";
  deploymentTime: number;
  performance: {
    averageResponseTime: number;
    throughput: number;
    errorRate: number;
    accuracy: number;
  };
  rollbackInfo?: {
    previousVersion: string;
    rollbackTime: number;
    reason: string;
  };
}

/**
 * 机器学习训练服务类
 */
export class MLTrainingService {
  private isInitialized: boolean = false;
  private activeTrainingTasks: Map<string, TrainingTask> = new Map();
  private modelCache: Map<string, any> = new Map();

  constructor() {
    this.initialize();
  }

  /**
   * 初始化ML训练服务
   */
  async initialize(): Promise<void> {
    try {
      console.log("🔧 初始化机器学习训练服务...");

      // 检查后端ML服务状态
      await this.checkMLServiceStatus();

      // 加载现有训练任务
      await this.loadActiveTrainingTasks();

      this.isInitialized = true;
      console.log("✅ 机器学习训练服务初始化完成");
    } catch (error) {
      console.error("❌ 机器学习训练服务初始化失败:", error);
      throw new Error(`ML训练服务初始化失败: ${error}`);
    }
  }

  /**
   * 创建训练数据集
   */
  async createDataset(
    name: string,
    description: string,
    trainingData: TrainingData[]
  ): Promise<string> {
    try {
      console.log("📊 创建训练数据集...", {
        name,
        dataCount: trainingData.length,
      });

      const response = await apiClient.post("/ml/datasets", {
        name,
        description,
        data: trainingData,
        metadata: {
          createdAt: Date.now(),
          dataCount: trainingData.length,
          sources: this.analyzeDataSources(trainingData),
        },
      });

      const datasetId = response.data.datasetId;
      console.log("✅ 训练数据集创建完成", { datasetId });

      return datasetId;
    } catch (error) {
      console.error("❌ 创建训练数据集失败:", error);
      throw new Error(`创建训练数据集失败: ${error}`);
    }
  }

  /**
   * 开始模型训练
   */
  async startTraining(
    name: string,
    description: string,
    modelConfig: ModelConfig,
    datasetId: string
  ): Promise<string> {
    try {
      console.log("🚀 开始模型训练...", {
        name,
        modelType: modelConfig.modelType,
      });

      const response = await apiClient.post("/ml/training/start", {
        name,
        description,
        modelConfig,
        datasetId,
        timestamp: Date.now(),
      });

      const taskId = response.data.taskId;

      // 创建本地训练任务记录
      const trainingTask: TrainingTask = {
        id: taskId,
        name,
        description,
        modelConfig,
        datasetId,
        status: "pending",
        progress: 0,
        metrics: {},
        startTime: Date.now(),
      };

      this.activeTrainingTasks.set(taskId, trainingTask);

      // 开始监控训练进度
      this.monitorTrainingProgress(taskId);

      console.log("✅ 模型训练任务已启动", { taskId });
      return taskId;
    } catch (error) {
      console.error("❌ 启动模型训练失败:", error);
      throw new Error(`启动模型训练失败: ${error}`);
    }
  }

  /**
   * 获取训练任务状态
   */
  async getTrainingStatus(taskId: string): Promise<TrainingTask | null> {
    try {
      const localTask = this.activeTrainingTasks.get(taskId);
      if (!localTask) {
        // 从后端获取任务状态
        const response = await apiClient.get(`/ml/training/status/${taskId}`);
        return response.data;
      }

      return localTask;
    } catch (error) {
      console.error("获取训练状态失败:", error);
      return null;
    }
  }

  /**
   * 停止训练任务
   */
  async stopTraining(taskId: string): Promise<void> {
    try {
      await apiClient.post(`/ml/training/stop/${taskId}`);

      const task = this.activeTrainingTasks.get(taskId);
      if (task) {
        task.status = "cancelled";
        task.endTime = Date.now();
      }

      console.log("✅ 训练任务已停止", { taskId });
    } catch (error) {
      console.error("停止训练任务失败:", error);
      throw error;
    }
  }

  /**
   * 评估模型性能
   */
  async evaluateModel(
    modelId: string,
    testDatasetId: string
  ): Promise<ModelEvaluation> {
    try {
      console.log("📈 开始模型评估...", { modelId, testDatasetId });

      const response = await apiClient.post("/ml/evaluation/start", {
        modelId,
        testDatasetId,
        timestamp: Date.now(),
      });

      const evaluation = response.data;
      console.log("✅ 模型评估完成", {
        accuracy: evaluation.metrics.overall.accuracy,
        f1Score: evaluation.metrics.overall.f1Score,
      });

      return evaluation;
    } catch (error) {
      console.error("❌ 模型评估失败:", error);
      throw new Error(`模型评估失败: ${error}`);
    }
  }

  /**
   * 部署模型到生产环境
   */
  async deployModel(
    modelId: string,
    version: string,
    environment: "staging" | "production"
  ): Promise<ModelDeployment> {
    try {
      console.log("🚀 部署模型...", { modelId, version, environment });

      const response = await apiClient.post("/ml/deployment/deploy", {
        modelId,
        version,
        environment,
        timestamp: Date.now(),
      });

      const deployment = response.data;
      console.log("✅ 模型部署完成", {
        modelId: deployment.modelId,
        status: deployment.status,
      });

      return deployment;
    } catch (error) {
      console.error("❌ 模型部署失败:", error);
      throw new Error(`模型部署失败: ${error}`);
    }
  }

  /**
   * 回滚模型版本
   */
  async rollbackModel(
    modelId: string,
    targetVersion: string,
    reason: string
  ): Promise<void> {
    try {
      console.log("⏪ 回滚模型版本...", { modelId, targetVersion, reason });

      await apiClient.post("/ml/deployment/rollback", {
        modelId,
        targetVersion,
        reason,
        timestamp: Date.now(),
      });

      console.log("✅ 模型版本回滚完成");
    } catch (error) {
      console.error("❌ 模型版本回滚失败:", error);
      throw new Error(`模型版本回滚失败: ${error}`);
    }
  }

  /**
   * 获取模型性能监控数据
   */
  async getModelPerformance(
    modelId: string,
    timeRange: { start: number; end: number }
  ): Promise<{
    metrics: Array<{
      timestamp: number;
      accuracy: number;
      responseTime: number;
      throughput: number;
      errorRate: number;
    }>;
    alerts: Array<{
      type: "accuracy_drop" | "high_latency" | "error_spike";
      message: string;
      timestamp: number;
      severity: "low" | "medium" | "high";
    }>;
  }> {
    try {
      const response = await apiClient.get(
        `/ml/monitoring/performance/${modelId}?start=${timeRange.start}&end=${timeRange.end}`
      );
      return response.data;
    } catch (error) {
      console.error("获取模型性能数据失败:", error);
      throw error;
    }
  }

  /**
   * 优化模型超参数
   */
  async optimizeHyperparameters(
    baseConfig: ModelConfig,
    datasetId: string,
    optimizationConfig: {
      method: "grid_search" | "random_search" | "bayesian";
      maxTrials: number;
      metric: "accuracy" | "f1_score" | "auc";
      parameterRanges: {
        [parameter: string]: {
          type: "continuous" | "discrete" | "categorical";
          range: any[];
        };
      };
    }
  ): Promise<{
    bestConfig: ModelConfig;
    bestScore: number;
    trials: Array<{
      config: ModelConfig;
      score: number;
      duration: number;
    }>;
  }> {
    try {
      console.log("🔧 开始超参数优化...", {
        method: optimizationConfig.method,
        maxTrials: optimizationConfig.maxTrials,
      });

      const response = await apiClient.post(
        "/ml/optimization/hyperparameters",
        {
          baseConfig,
          datasetId,
          optimizationConfig,
          timestamp: Date.now(),
        }
      );

      const result = response.data;
      console.log("✅ 超参数优化完成", {
        bestScore: result.bestScore,
        trialsCount: result.trials.length,
      });

      return result;
    } catch (error) {
      console.error("❌ 超参数优化失败:", error);
      throw new Error(`超参数优化失败: ${error}`);
    }
  }

  /**
   * 获取特征重要性分析
   */
  async getFeatureImportance(modelId: string): Promise<{
    features: Array<{
      name: string;
      importance: number;
      category:
        | "looking"
        | "listening"
        | "inquiry"
        | "palpation"
        | "calculation";
    }>;
    correlationMatrix: number[][];
    featureNames: string[];
  }> {
    try {
      const response = await apiClient.get(
        `/ml/analysis/feature-importance/${modelId}`
      );
      return response.data;
    } catch (error) {
      console.error("获取特征重要性失败:", error);
      throw error;
    }
  }

  /**
   * 添加训练数据反馈
   */
  async addTrainingFeedback(
    sessionId: string,
    actualOutcome: {
      syndrome: string;
      constitution: string;
      confidence: number;
    },
    userFeedback: {
      accuracy: number;
      usefulness: number;
      comments?: string;
    }
  ): Promise<void> {
    try {
      await apiClient.post("/ml/feedback/add", {
        sessionId,
        actualOutcome,
        userFeedback,
        timestamp: Date.now(),
      });

      console.log("✅ 训练反馈已添加", { sessionId });
    } catch (error) {
      console.error("添加训练反馈失败:", error);
      throw error;
    }
  }

  /**
   * 获取服务状态
   */
  getServiceStatus(): {
    isInitialized: boolean;
    activeTrainingTasks: number;
    totalTasks: number;
    averageAccuracy: number;
  } {
    const activeTasks = Array.from(this.activeTrainingTasks.values());
    const completedTasks = activeTasks.filter(
      (task) => task.status === "completed"
    );
    const averageAccuracy =
      completedTasks.length > 0
        ? completedTasks.reduce(
            (sum, task) => sum + (task.metrics.accuracy || 0),
            0
          ) / completedTasks.length
        : 0;

    return {
      isInitialized: this.isInitialized,
      activeTrainingTasks: activeTasks.filter(
        (task) => task.status === "running"
      ).length,
      totalTasks: this.activeTrainingTasks.size,
      averageAccuracy,
    };
  }

  // 私有方法

  private async checkMLServiceStatus(): Promise<void> {
    try {
      const response = await apiClient.get("/ml/health");
      if (!response.data.healthy) {
        throw new Error("ML服务不健康");
      }
    } catch (error) {
      console.warn("ML服务状态检查失败，将使用离线模式:", error);
    }
  }

  private async loadActiveTrainingTasks(): Promise<void> {
    try {
      const response = await apiClient.get("/ml/training/active");
      const tasks = response.data.tasks || [];

      tasks.forEach((task: TrainingTask) => {
        this.activeTrainingTasks.set(task.id, task);
        if (task.status === "running") {
          this.monitorTrainingProgress(task.id);
        }
      });
    } catch (error) {
      console.warn("加载活跃训练任务失败:", error);
    }
  }

  private monitorTrainingProgress(taskId: string): void {
    const checkProgress = async () => {
      try {
        const response = await apiClient.get(`/ml/training/progress/${taskId}`);
        const progress = response.data;

        const task = this.activeTrainingTasks.get(taskId);
        if (task) {
          task.status = progress.status;
          task.progress = progress.progress;
          task.metrics = progress.metrics;

          if (progress.status === "completed" || progress.status === "failed") {
            task.endTime = Date.now();
            if (progress.status === "failed") {
              task.errorMessage = progress.error;
            }
            return; // 停止监控
          }
        }

        // 继续监控
        setTimeout(checkProgress, 5000);
      } catch (error) {
        console.error("监控训练进度失败:", error);
      }
    };

    checkProgress();
  }

  private analyzeDataSources(trainingData: TrainingData[]): {
    [source: string]: number;
  } {
    const sources: { [source: string]: number } = {};

    trainingData.forEach((data) => {
      const source = data.metadata.source;
      sources[source] = (sources[source] || 0) + 1;
    });

    return sources;
  }

  /**
   * 创建训练任务（简化接口）
   */
  async createTrainingTask(
    modelName: string,
    modelConfig: any,
    trainingData: any[]
  ): Promise<{
    id: string;
    modelName: string;
    status: string;
    datasetSize: number;
  }> {
    try {
      console.log("🚀 创建训练任务...", {
        modelName,
        dataSize: trainingData.length,
      });

      // 创建数据集
      const datasetId = await this.createDataset(
        `${modelName}_dataset`,
        `训练数据集 for ${modelName}`,
        trainingData.map((data) => ({
          id: data.id,
          userId: "system",
          sessionId: "training",
          inputData: data.input,
          expectedOutput: data.expectedOutput,
          metadata: data.metadata,
        }))
      );

      // 构建模型配置
      const config: ModelConfig = {
        modelType: modelConfig.type || "neural_network",
        hyperparameters: modelConfig.hyperparameters || {
          learningRate: 0.001,
          epochs: 50,
          batchSize: 32,
        },
        features: {
          looking: ["tongueColor", "coating", "texture"],
          listening: ["voicePattern", "breathingRate"],
          inquiry: ["symptoms", "lifestyle"],
          palpation: ["pulseRate", "strength"],
          calculation: ["birthDate", "currentTime", "location"],
        },
        targetVariables: ["syndrome", "constitution", "confidence"],
      };

      // 开始训练
      const taskId = await this.startTraining(
        modelName,
        `训练模型: ${modelName}`,
        config,
        datasetId
      );

      console.log("✅ 训练任务创建完成", { taskId, modelName });

      return {
        id: taskId,
        modelName,
        status: "pending",
        datasetSize: trainingData.length,
      };
    } catch (error) {
      console.error("❌ 创建训练任务失败:", error);
      throw new Error(`创建训练任务失败: ${error}`);
    }
  }
}

// 导出单例实例
export const mlTrainingService = new MLTrainingService();
