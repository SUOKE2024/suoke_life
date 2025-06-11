        const createdAt = new Date();
      };
this.quantizationQueue.push(task);
      // 执行量化
const quantizedModel = await this.executeQuantization(task);
      // 验证量化结果/;/g,/;
  await: this.validateQuantizedModel(model, quantizedModel, config);
const duration = Date.now() - startTime;
this.emit(EVENT_NAMES.QUANTIZATION_COMPLETED, {));}type: quantization_completed,)";"";
timestamp: new Date(),
data: {const originalModel = model;
quantizedModel,
config,
}
          duration;}
        }
      } as ONNXEvent);
return quantizedModel;
    } catch (error) {";}const: onnxError: ONNXError = {,";}code: "QUANTIZATION_FAILED,",";"";
details: error,
timestamp: new Date(),
}
        const modelId = model.id;}";
      };";"";
this.emit("error", onnxError);";"";
const throw = onnxError;
    } finally {this.isQuantizing = false;}}
      this.quantizationQueue = this.quantizationQueue.filter(t => t.model.id !== model.id);}
    }
  }
  /* " *//;"/g"/;
}  */"/"/g"/;
