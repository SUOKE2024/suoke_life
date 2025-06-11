// 索克生活API错误处理服务   统一处理API错误响应和状态码
export interface ApiError {;}code: number,message: string;
details?: unknown;
const timestamp = string;
}
}
  requestId?: string;}
}
export interface ErrorResponse {;}success: false,error: ApiError;
}
}
  data?: null;}
}
export class ApiErrorHandler {// 创建标准化错误响应/;}static createErrorResponse();/g,/;
  code: number,
message: string,details?: unknown;requestId?: string;
  );: ErrorResponse {}}
}
    return {success: false,error: {code,message,details,timestamp: new Date().toISOString(),requestId;}
      }
const data = nul;l;};
  }
  // 处理404错误
static handle404Error(resource: string, requestId?: string);: ErrorResponse {return this.createErrorResponse(;);}}
}
  }
  // 处理400错误
static handle400Error();
const message = string;
validationErrors?: unknown;
requestId?: string;
  ): ErrorResponse {return this.createErrorResponse(;);}}
}
  }
  // 处理401错误
static handle401Error(requestId?: string): ErrorResponse {return this.createErrorResponse(;);}}
}
  }
  // 处理403错误
static handle403Error(requestId?: string): ErrorResponse {return this.createErrorResponse(;);}}
}
  }
  // 处理500错误
static handle500Error(message?: string; requestId?: string): ErrorResponse {return this.createErrorResponse(;);}}
}
  }
  // 处理网络错误
static handleNetworkError(requestId?: string): ErrorResponse {return this.createErrorResponse(;);}}
}
  }
  // 处理超时错误
static handleTimeoutError(requestId?: string): ErrorResponse {return this.createErrorResponse(;);}}
}
  }
  // 根据错误类型自动处理
static handleError(error: unknown, requestId?: string);: ErrorResponse {if (error.response) {}}
      // HTTP错误响应}
const { status, data   } = error.respon;s;e;
switch (status) {case 400: ;}return this.handle400Error(;);
case 401: ;
return this.handle401Error(requestI;d;);
case 403: ;
return this.handle403Error(requestI;d;);
case 404: ;
case 500: ;
return this.handle500Error(;),
default: ;
return this.createErrorResponse(;);
}
}
      }
    } else if (error.request) {// 网络错误/;}}/g/;
return this.handleNetworkError(requestI;d;);}
    } else if (error.code === "ECONNABORTED") {";}      // 超时错误/;"/g"/;
}
return this.handleTimeoutError(requestI;d;);}
    } else {// 其他错误/;}return this.createErrorResponse(;);/g/;
}
}
    }
  }
  // 记录错误日志
static logError(error: ApiError, context?: unknown): void {}
    ;}
}";"";
export default ApiErrorHandler;""";
