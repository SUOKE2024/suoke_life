
        const createdAt = new Date();
      };
this.optimizationQueue.push(task);
      // 执行优化/;,/g/;
const optimizedModel = await this.executeOptimization(task);
      // 验证优化结果/;,/g,/;
  result: await this.validateOptimizationResult(model, optimizedModel, options);
const duration = Date.now() - startTime;
      // 记录优化历史/;,/g/;
this.recordOptimizationHistory(model.id, result);
this.emit(EVENT_NAMES.OPTIMIZATION_COMPLETED, {));,}type: optimization_completed";",)";,"";
timestamp: new Date(),;
data: {const originalModel = model;
optimizedModel,;
options,;
result,;
}
          duration;}
        }
      } as ONNXEvent);
return optimizedModel;
    } catch (error) {";,}const: onnxError: ONNXError = {,";,}code: "OPTIMIZATION_FAILED,",";,"";
details: error,;
timestamp: new Date(),;
}
        const modelId = model.id;}";"";
      };";,"";
this.emit("error", onnxError);";,"";
const throw = onnxError;
    } finally {this.isOptimizing = false;}}
      this.optimizationQueue = this.optimizationQueue.filter(t => t.model.id !== model.id);}
    }
  }
  /* " *//;"/g"/;
}  */"/"/g"/;