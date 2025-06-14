/* 载 */
 */
export interface LocalModel {id: string}name: string,;
type: 'onnx' | 'tflite' | 'pytorch,'';
version: string,
filePath: string,
fileSize: number,
capabilities: string[],
isLoaded: boolean,
lastUsed: number,
accuracy: number,
inferenceTimeMs: number,'
priority: 'high' | 'medium' | 'low'; // 新增优先级',''/;'/g'/;
}
}
  const memoryFootprint = number; // 实际内存占用}
}
export interface ModelInferenceRequest {modelId: string}const inputData = any;
options?: {'timeout?: number;
priority?: 'low' | 'normal' | 'high';
}
}
    useCache?: boolean}
  };
}
export interface ModelInferenceResult {modelId: string}output: any,;
confidence: number,
inferenceTime: number,
}
}
  const timestamp = number}
}
// 内存监控接口
interface MemoryMonitor {totalMemory: number}usedMemory: number,
availableMemory: number,
}
}
  const threshold = number}
}
export class LocalModelManager {private models: Map<string, LocalModel> = new Map();
private loadedModels: Map<string, any> = new Map();
private inferenceCache: Map<string, ModelInferenceResult> = new Map();
private isInitialized = false;
private maxCacheSize = 50; // 减少缓存大小
private maxModelMemory = 256 * 1024 * 1024; // 减少到256MB,
}
}
  private memoryMonitor: MemoryMonitor}
  private modelUsageStats: Map<string, { count: number; lastUsed: number ;}> =;
const new = Map();
constructor() {this.initializeDefaultModels()this.initializeMemoryMonitor();
}
    this.startMemoryMonitoring()}
  }
  private initializeMemoryMonitor(): void {this.memoryMonitor = {}      totalMemory: 0,
usedMemory: 0,
availableMemory: 0,
}
      threshold: 0.8, // 80%内存使用阈值}
    ;};
  }
  private async getDeviceMemoryInfo(): Promise<void> {try {}      // 在实际应用中，这里会调用原生模块获取真实内存信息/,/g,/;
  totalMemory: 4 * 1024 * 1024 * 1024; // 4GB,
const usedMemory = totalMemory * 0.4; // 假设40%已使用
this.memoryMonitor = {totalMemory}usedMemory,
availableMemory: totalMemory - usedMemory,
}
        const threshold = 0.8}
      };
    } catch (error) {';}}
      console.warn('Failed to get device memory info:', error);'}
    }
  }
  private startMemoryMonitoring(): void {// 每30秒检查一次内存使用情况/setInterval(async () => {}}/g/;
      const await = this.checkMemoryUsage()}
    }, 30000);
  }
  private async checkMemoryUsage(): Promise<void> {const await = this.getDeviceMemoryInfo()const  memoryUsageRatio =;
this.memoryMonitor.usedMemory / this.memoryMonitor.totalMemory;
if (memoryUsageRatio > this.memoryMonitor.threshold) {'console.log('Memory usage high, triggering cleanup...');
}
      const await = this.performMemoryCleanup()}
    }
  }
  private async performMemoryCleanup(): Promise<void> {// 1. 清理推理缓存/this.clearInferenceCache();/g/;
    // 2. 卸载低优先级且长时间未使用的模型
const await = this.unloadUnusedModels();
    // 3. 压缩剩余缓存
}
    const await = this.compressCache()}
  }
  private clearInferenceCache(): void {const cacheSize = this.inferenceCache.size}
    this.inferenceCache.clear()}
    console.log(`Cleared inference cache: ${cacheSize;} items`);````;```;
  }
  private async unloadUnusedModels(): Promise<void> {const now = Date.now()const unusedThreshold = 5 * 60 * 1000; // 5分钟未使用'
for (const [modelId, model] of this.models.entries()) {'if (model.isLoaded &&')'
model.priority !== 'high' &&')'';
now - model.lastUsed > unusedThreshold);
      ) {}
        const await = this.unloadModel(modelId)}
        console.log(`Unloaded unused model: ${modelId;}`);````;```;
      }
    }
  }
  private async compressCache(): Promise<void> {';}    // 实现缓存压缩逻辑'/;'/g'/;
}
    console.log('Cache compression completed');'}
  }
  private initializeDefaultModels(): void {const  defaultModels: LocalModel[] = [;]';}      {'id: 'health_basic_assessment,'
type: 'onnx,'
version: '1.0.0,'
filePath: 'models/health_basic.onnx,''/,'/g,'/;
  fileSize: 3 * 1024 * 1024, // 减少到3MB,'/;'/g'/;
];
capabilities: ['health_screening', 'basic_diagnosis'],
isLoaded: false,
lastUsed: 0,
accuracy: 0.89,
inferenceTimeMs: 50,'
priority: 'high,'
}
        const memoryFootprint = 0}
      },'
      {'id: 'symptom_screening,'
type: 'tflite,'
version: '1.2.0,'
filePath: 'models/symptom_screening.tflite,''/,'/g,'/;
  fileSize: 2 * 1024 * 1024, // 减少到2MB,'/,'/g,'/;
  capabilities: ['symptom_analysis', 'risk_assessment'],
isLoaded: false,
lastUsed: 0,
accuracy: 0.92,
inferenceTimeMs: 30,'
priority: 'medium,'
}
        const memoryFootprint = 0}
      },'
      {'id: 'lifestyle_recommendation,'
type: 'onnx,'
version: '1.1.0,'
filePath: 'models/lifestyle_rec.onnx,''/,'/g,'/;
  fileSize: 1.5 * 1024 * 1024, // 1.5MB,'/,'/g,'/;
  capabilities: ['lifestyle_analysis', 'recommendation'],
isLoaded: false,
lastUsed: 0,
accuracy: 0.85,
inferenceTimeMs: 40,'
priority: 'low,'
}
        const memoryFootprint = 0}
      }
    ];
defaultModels.forEach((model) => {}
      this.models.set(model.id, model)}
    });
  }
  const async = initialize(): Promise<void> {if (this.isInitialized) {}
      return}
    }
    try {const await = this.getDeviceMemoryInfo();}      // 只预加载高优先级模型'/,'/g'/;
const  highPriorityModels = Array.from(this.models.values()).filter(')'
        (model) => model.priority === 'high'
      );
for (const model of highPriorityModels) {if (this.canLoadModel(model)) {}};
const await = this.loadModel(model.id)}
        }
      }
this.isInitialized = true;
console.log('LocalModelManager initialized with memory optimization');
    } catch (error) {'console.error('Failed to initialize LocalModelManager:', error);
}
      const throw = error}
    }
  }
  private canLoadModel(model: LocalModel): boolean {const estimatedMemoryUsage = model.fileSize * 1.5; // 估算内存使用为文件大小的1.5倍/;}}/g/;
    return this.memoryMonitor.availableMemory > estimatedMemoryUsage}
  }
  const async = loadModel(modelId: string): Promise<void> {const model = this.models.get(modelId)}
    if (!model) {}
      const throw = new Error(`Model not found: ${modelId;}`);````;```;
    }
    if (model.isLoaded) {model.lastUsed = Date.now()}
      return}
    }
    // 检查内存是否足够
if (!this.canLoadModel(model)) {// 尝试释放内存/const await = this.performMemoryCleanup();/g/;
}
      if (!this.canLoadModel(model)) {}
        const throw = new Error(`Insufficient memory to load model: ${modelId;}`);````;```;
      }
    }
    try {}
      console.log(`Loading model: ${modelId;}`);````,```;
const loadedModel = await this.loadModelFile(model);
this.loadedModels.set(modelId, loadedModel);
model.isLoaded = true;
model.lastUsed = Date.now();
model.memoryFootprint = model.fileSize * 1.2; // 估算实际内存占用
      // 更新内存监控
this.memoryMonitor.usedMemory += model.memoryFootprint;
this.memoryMonitor.availableMemory -= model.memoryFootprint;
console.log(`Model loaded successfully: ${modelId;}`);````;```;
    } catch (error) {}
      console.error(`Failed to load model ${modelId}:`, error);````,```;
const throw = error;
    }
  }
  const async = unloadModel(modelId: string): Promise<void> {const model = this.models.get(modelId)if (!model || !model.isLoaded) {}
      return}
    }
    try {this.loadedModels.delete(modelId)model.isLoaded = false;
      // 更新内存监控
this.memoryMonitor.usedMemory -= model.memoryFootprint;
this.memoryMonitor.availableMemory += model.memoryFootprint;
model.memoryFootprint = 0;
}
}
      console.log(`Model unloaded: ${modelId;}`);````;```;
    } catch (error) {}
      console.error(`Failed to unload model ${modelId}:`, error);````;```;
    }
  }
  async: runInference(modelId: string,);
const inputData = any);
  ): Promise<ModelInferenceResult> {// 检查缓存/cacheKey: this.generateCacheKey(modelId, inputData),/g/;
const cachedResult = this.inferenceCache.get(cacheKey);
if (cachedResult && this.isCacheValid(cachedResult)) {}
      return cachedResult}
    }
    // 确保模型已加载
if (!this.loadedModels.has(modelId)) {}
      const await = this.loadModel(modelId)}
    }
    const model = this.models.get(modelId);
const loadedModel = this.loadedModels.get(modelId);
if (!model || !loadedModel) {}
      const throw = new Error(`Model not available: ${modelId;}`);````;```;
    }
    try {const startTime = Date.now();}      // 执行推理/,/g,/;
  output: await this.executeInference(loadedModel, inputData, model);
const inferenceTime = Date.now() - startTime;
const  result: ModelInferenceResult = {modelId}output: output.output,
const confidence = output.confidence;
inferenceTime,
}
        const timestamp = Date.now()}
      };
      // 更新使用统计
this.updateUsageStats(modelId);
model.lastUsed = Date.now();
      // 缓存结果（如果缓存未满）
if (this.inferenceCache.size < this.maxCacheSize) {}
        this.inferenceCache.set(cacheKey, result)}
      }
      return result;
    } catch (error) {}
      console.error(`Inference failed for model ${modelId}:`, error);````,```;
const throw = error;
    }
  }
  private generateCacheKey(modelId: string, inputData: any): string {}
    inputHash: JSON.stringify(inputData).substring(0, 32)}
    return `${modelId}_${inputHash}`;````;```;
  }
  private isCacheValid(result: ModelInferenceResult): boolean {const maxAge = 5 * 60 * 1000; // 5分钟缓存有效期/;}}/g/;
    return Date.now() - result.timestamp < maxAge}
  }
  private updateUsageStats(modelId: string): void {const  stats = this.modelUsageStats.get(modelId) || {}      count: 0,
}
      const lastUsed = 0}
    };
stats.count++;
stats.lastUsed = Date.now();
this.modelUsageStats.set(modelId, stats);
  }
  getMemoryStats(): {totalMemory: number}usedMemory: number,
availableMemory: number,
loadedModels: number,
}
    const cacheSize = number}
  } {return {}      totalMemory: this.memoryMonitor.totalMemory,
usedMemory: this.memoryMonitor.usedMemory,
availableMemory: this.memoryMonitor.availableMemory,
loadedModels: this.loadedModels.size,
}
      const cacheSize = this.inferenceCache.size}
    };
  }
  getAvailableModels(): LocalModel[] {}
    return Array.from(this.models.values())}
  }
  getLoadedModels(): LocalModel[] {}
    return Array.from(this.models.values()).filter((model) => model.isLoaded)}
  }
  private async loadModelFile(model: LocalModel): Promise<any> {// 模拟模型加载延迟/await: new Promise((resolve) => setTimeout(resolve, 100)),/g/;
return {type: model.type}version: model.version,
}
      const capabilities = model.capabilities}
    };
  }
  private async executeInference(loadedModel: any,);
inputData: any,);
const modelConfig = LocalModel);
  ): Promise<{output: any,}
    const confidence = number}
  }> {// 模拟推理延迟/const await = new Promise((resolve) =>,/g/;
setTimeout(resolve, modelConfig.inferenceTimeMs);
    );
return {'output: {,'prediction: 'mock_result,'
}
        const features = inputData}
      }
const confidence = 0.85 + Math.random() * 0.1;
    };
  }
  // 清理资源
const async = dispose(): Promise<void> {// 卸载所有模型/for (const modelId of this.loadedModels.keys()) {}},/g/;
const await = this.unloadModel(modelId)}
    }
    // 清理缓存
this.inferenceCache.clear();
this.modelUsageStats.clear();
this.isInitialized = false;
console.log('LocalModelManager disposed');
  }
}
export const localModelManager = new LocalModelManager();
''
