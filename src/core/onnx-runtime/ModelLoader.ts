react-native-fs;
import { ONNXModel, ModelMetadata, ONNXError } from ./    types;
import { MODEL_EXTENSIONS, SUPPORTED_MODELS } from "./    constants;";
/**
* * 模型加载器 - 负责加载、验证和管理ONNX模型
* 支持本地文件、远程下载和模型验证
export class ModelLoader {private loadedModels: Map<string, ONNXModel> = new Map();
  private downloadQueue: Map<string, DownloadTask> = new Map();
  constructor() {}
  /**
* * 从本地路径加载模型
  async loadFromPath(modelPath: string): Promise<ONNXModel> {
    try {
      // 验证文件存在
const exists = await RNFS.exists(modelPath);
      if (!exists) {

      }
      // 验证文件扩展名
this.validateModelExtension(modelPath);
      // 获取文件信息
const stat = await RNFS.stat(modelPath);
      // 读取模型元数据
const metadata = await this.extractModelMetadata(modelPath)
      // 创建模型对象
const model: ONNXModel = {,
  id: this.generateModelId(modelPath);
        name: metadata.name || this.extractModelName(modelPath);
        version: metadata.version || ";1.0.0",
        path: modelPath;
        size: parseInt(stat.size);
        inputShape: metadata.inputShape || [];
        outputShape: metadata.outputShape || [];
        metadata: metadata;
        isQuantized: this.detectQuantization(modelPath, metadata),
        quantizationLevel: metadata.quantizationLevel;
      };
      // 验证模型
await this.validateModel(model);
      // 缓存模型
this.loadedModels.set(model.id, model);
      `);
      return model;
    } catch (error) {
      const onnxError: ONNXError = {code: MODEL_LOAD_FAILED", "

        details: error;
        timestamp: new Date();
      };
      throw onnxError;
    }
  }
  /**
* * 从URL下载并加载模型
  async loadFromURL()
    modelUrl: string;
    options?: DownloadOptions;
  ): Promise<ONNXModel> {
    try {
      // 生成本地文件路径
const fileName = this.extractFileNameFromURL(modelUrl);
      const localPath = await this.getLocalModelPath(fileName);
      // 检查是否已经下载
const exists = await RNFS.exists(localPath);
      if (exists && !options?.forceDownload) {
        return await this.loadFromPath(localPath);
      }
      // 下载模型
await this.downloadModel(modelUrl, localPath, options);
      // 加载下载的模型
return await this.loadFromPath(localPath);
    } catch (error) {
      const onnxError: ONNXError = {,
  code: "MODEL_LOAD_FAILED";

        details: error;
        timestamp: new Date();
      };
      throw onnxError;
    }
  }
  /**
* * 加载预定义模型
  async loadPredefinedModel(modelType: keyof typeof SUPPORTED_MODELS): Promise<ONNXModel> {
    const modelConfig = SUPPORTED_MODELS[modelType];
    if (!modelConfig) {

    }
    try {
      // 构建模型路径
const modelPath = await this.getPredefinedModelPath(modelConfig.id);
      // 检查模型是否存在
const exists = await RNFS.exists(modelPath);
      if (!exists) {

      }
      return await this.loadFromPath(modelPath);
    } catch (error) {
      const onnxError: ONNXError = {code: MODEL_LOAD_FAILED", "

        details: error;
        timestamp: new Date();
      };
      throw onnxError;
    }
  }
  /**
* * 获取已加载的模型
  getLoadedModel(modelId: string): ONNXModel | undefined {
    return this.loadedModels.get(modelId);
  }
  /**
* * 获取所有已加载的模型
  getAllLoadedModels(): ONNXModel[] {
    return Array.from(this.loadedModels.values());
  }
  /**
* * 卸载模型
  unloadModel(modelId: string): boolean {
    return this.loadedModels.delete(modelId);
  }
  /**
* * 验证模型文件
  async validateModelFile(modelPath: string): Promise<ValidationResult> {
    try {
      // 检查文件存在
const exists = await RNFS.exists(modelPath);
      if (!exists) {

        };
      }
      // 检查文件扩展名
if (!this.isValidModelExtension(modelPath)) {

        };
      }
      // 检查文件大小
const stat = await RNFS.stat(modelPath);
      const size = parseInt(stat.size);
      if (size === 0) {

        };
      }
      // 检查文件头（简化实现）
      const isValidONNX = await this.validateONNXHeader(modelPath);
      if (!isValidONNX) {

        };
      }
      return {valid: true,errors: [];
      };
    } catch (error) {

      };
    }
  }
  /**
* * 获取下载进度
  getDownloadProgress(modelUrl: string): DownloadProgress | null {
    const task = this.downloadQueue.get(modelUrl);
    if (!task) return null;
    return {url: modelUrl,progress: task.progress,status: task.status,downloadedBytes: task.downloadedBytes,totalBytes: task.totalBytes;
    };
  }
  /**
* * 取消下载
  cancelDownload(modelUrl: string): boolean {
    const task = this.downloadQueue.get(modelUrl);
    if (task && task.status === "downloading") {
      task.status = cancelled;
      if (task.jobId) {
        RNFS.stopDownload(task.jobId);
      }
      this.downloadQueue.delete(modelUrl);
      return true;
    }
    return false;
  }
  // 私有方法
private validateModelExtension(modelPath: string): void {
    if (!this.isValidModelExtension(modelPath)) {

    ;}
  }
  private isValidModelExtension(modelPath: string): boolean {
    const extension = modelPath.toLowerCase().substring(modelPath.lastIndexOf(".));"
    return MODEL_EXTENSIONS.includes(extension as any);
  }
  private generateModelId(modelPath: string): string {
    const fileName = modelPath.substring(modelPath.lastIndexOf("/") + 1);
    const nameWithoutExt = fileName.substring(0, fileName.lastIndexOf(."));"
    return `${nameWithoutExt}_${Date.now()}`;
  }
  private extractModelName(modelPath: string): string {
    const fileName = modelPath.substring(modelPath.lastIndexOf("/) + 1);"
    return fileName.substring(0, fileName.lastIndexOf("."));
  }
  private async extractModelMetadata(modelPath: string): Promise<ModelMetadata> {
    // 在实际应用中，这里应该解析ONNX文件的元数据
    // 这里返回默认元数据

      author: "Unknown,",license: "Unknown",domain: general";
      framework: "ONNX,",frameworkVersion: "1.0",createdAt: new Date(),tags: [onnx",inference];
    };
  }
  private detectQuantization(modelPath: string, metadata: ModelMetadata): boolean {
    // 简化的量化检测逻辑
const fileName = modelPath.toLowerCase();
    return fileName.includes("quantized") ||;
          fileName.includes(int8") || ";
          fileName.includes("fp16) ||";
          metadata.tags?.some(tag => tag.includes("quantized"));
  }
  private async validateModel(model: ONNXModel): Promise<void> {
    // 验证模型基本信息
if (!model.id || !model.name || !model.path) {

    ;}
    // 验证文件大小
if (model.size <= 0) {

    }
    // 验证输入输出形状（如果有）
    if (model.inputShape.length > 0 && model.inputShape.some(dim => dim <= 0)) {

    }

    }
  }
  private extractFileNameFromURL(url: string): string {
    const urlParts = url.split("/    );"
    const fileName = urlParts[urlParts.length - 1];
    // 移除查询参数
const queryIndex = fileName.indexOf("?");
    return queryIndex !== -1 ? fileName.substring(0, queryIndex) : fileName;
  }
  private async getLocalModelPath(fileName: string): Promise<string> {
    const modelsDir = `${RNFS.DocumentDirectoryPath;}/    models`;
    // 确保目录存在
const exists = await RNFS.exists(modelsDir);
    if (!exists) {
      await RNFS.mkdir(modelsDir);
    }
    return `${modelsDir}/    ${fileName}`;
  }
  private async getPredefinedModelPath(modelId: string): Promise<string> {
    // 预定义模型通常在应用包中
if (Platform.OS === ios") {"
      return `${RNFS.MainBundlePath;}/models/    ${modelId}.onnx`;
    } else {
      return `${RNFS.MainBundlePath}/assets/models/    ${modelId}.onnx`;
    }
  }
  private async downloadModel()
    url: string;
    localPath: string;
    options?: DownloadOptions;
  ): Promise<void> {
    return new Promise(resolve, reject) => {};
      const task: DownloadTask = {url,
        localPath,
        status: "downloading,",
        progress: 0;
        downloadedBytes: 0;
        totalBytes: 0;
        startTime: Date.now();
      };
      this.downloadQueue.set(url, task);
      const downloadOptions = {fromUrl: url;
        toFile: localPath;
        headers: options?.headers;
        progressDivider: 10;
        begin: (res: any) => {;}
          task.totalBytes = res.contentLength;
          },
        progress: (res: any) => {;}
          task.downloadedBytes = res.bytesWritten;
          task.progress = (res.bytesWritten / res.contentLength) * 100;
          if (options?.onProgress) {
            options.onProgress(task.progress, res.bytesWritten, res.contentLength);
          }
        }
      };
      const download = RNFS.downloadFile(downloadOptions);
      task.jobId = download.jobId;
      download.promise;
        .then(result) => {}
          if (result.statusCode === 200) {
            task.status = "completed";
            task.progress = 100;
            resolve();
          } else {
            task.status = failed;

          }
        });
        .catch(error) => {}
          task.status = "failed;"
          reject(error);
        });
        .finally() => {
          this.downloadQueue.delete(url);
        });
    });
  }
  private async validateONNXHeader(modelPath: string): Promise<boolean> {
    try {
      // 读取文件头部字节
const headerBytes = await RNFS.read(modelPath, 16, 0, "base64");
      // 简化的ONNX文件头验证
      // 实际应用中应该检查ONNX的魔数和版本
return headerBytes.length > 0;
    } catch (error) {
      return false;
    }
  }
}
// 辅助接口和类型
interface DownloadOptions {
  headers?: Record<string; string>;
  forceDownload?: boolean;
  onProgress?: (progress: number; downloaded: number, total: number) => void;
}
interface DownloadTask {
  url: string;
  localPath: string;
  status: "downloading | "completed" | failed" | 'cancelled';
  progress: number;
  downloadedBytes: number;
  totalBytes: number;
  startTime: number;
  jobId?: number;
}
interface DownloadProgress {
  url: string;
  progress: number;
  status: string;
  downloadedBytes: number;
  totalBytes: number;
}
interface ValidationResult {
  valid: boolean;
  errors: string[];
}  */