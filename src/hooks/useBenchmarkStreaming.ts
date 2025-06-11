import {  useEffect, useState, useCallback, useRef  } from "react"
import { benchmarkStreamingService } from "../services"
import type { StreamEvent, StreamConfig } from "../services"
interface BenchmarkStreamingState {isConnected: boolean}connectionState: string,
events: StreamEvent[],
}
}
  const error = string | null}
}
interface UseBenchmarkStreamingOptions {
autoConnect?: booleanmaxEvents?: number;
}
  eventTypes?: string[];}";
}
export useBenchmarkStreaming: (options: UseBenchmarkStreamingOptions = {;}) => {const {autoConnect = true,maxEvents = 100,eventTypes = ["benchmark_progress",benchmark_complete', "benchmark_error",system_status'];'}
  } = options;
const [state, setState] = useState<BenchmarkStreamingState>({isConnected: false,connectionState: 'CLOSED',events: [],error: null;)'}
  });
const eventListenerRef = useRef<(event: StreamEvent) => void) | null>(null);
const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  // 事件处理器
const handleStreamEvent = useCallback(;);
    (event: StreamEvent) => {setState(prevState => ({...prevState,events: [event, ...prevState.events].slice(0, maxEvents),error: null;))}
      }));
    }
    [maxEvents];
  );
  // 连接WebSocket;/,/g,/;
  connect: useCallback(async () => {try {setState(prevState => ({  ...prevState, error: null ; })););
const await = benchmarkStreamingService.connect();
      // 订阅事件
benchmarkStreamingService.subscribeToEvents(eventTypes);
      // 添加事件监听器'/,'/g'/;
if (eventListenerRef.current) {';}}
        benchmarkStreamingService.removeEventListener('*', eventListenerRef.current);'}
      }
eventListenerRef.current = handleStreamEvent;
benchmarkStreamingService.addEventListener('*', eventListenerRef.current);
      // 启动心跳检测
benchmarkStreamingService.startHeartbeat();
setState(prevState => ({)...prevState,'isConnected: true,')'
connectionState: 'OPEN,)'
}
        const error = null;)}
      }));
    } catch (error) {setState(prevState => ({ )        ...prevState,'isConnected: false,')'
const connectionState = 'CLOSED)'
 })}
      }));
    }
  }, [eventTypes, handleStreamEvent]);
  // 断开连接'/,'/g,'/;
  disconnect: useCallback() => {if (eventListenerRef.current) {benchmarkStreamingService.removeEventListener('*', eventListenerRef.current);';}}'';
      eventListenerRef.current = null}
    }
    benchmarkStreamingService.disconnect();
if (reconnectTimeoutRef.current) {clearTimeout(reconnectTimeoutRef.current)}
      reconnectTimeoutRef.current = null}
    }
    setState(prevState => ({)...prevState,)'isConnected: false,)
}
      const connectionState = 'CLOSED')'}
    ;}));
  }, []);
  // 启动流式基准测试
const startStreamingBenchmark = useCallback(;);
    (config: StreamConfig) => {if (state.isConnected) {benchmarkStreamingService.startStreamingBenchmark(config)}
      } else {}
}
      }
    }
    [state.isConnected];
  );
  // 停止流式基准测试
const stopStreamingBenchmark = useCallback(;);
    (benchmarkId: string) => {if (state.isConnected) {benchmarkStreamingService.stopStreamingBenchmark(benchmarkId)}
      }
    }
    [state.isConnected];
  );
  // 清除事件历史/,/g,/;
  clearEvents: useCallback() => {setState(prevState => ({...prevState,events: [];))}
    }));
  }, []);
  // 获取特定类型的事件
const getEventsByType = useCallback(;);
    (eventType: string) => {return state.events.filter(event => event.type === eventType)}
    }
    [state.events];
  );
  // 获取最新事件
const getLatestEvent = useCallback(;);
    (eventType?: string) => {if (eventType) {return state.events.find(event => event.type === eventType) || null}
      }
      return state.events[0] || null;
    }
    [state.events];
  );
  // 监控连接状态'
useEffect() => {const checkConnectionState = () => {const currentState = benchmarkStreamingService.getConnectionState()setState(prevState => ({)        ...prevState,)'connectionState: currentState,)
}
        isConnected: currentState === 'OPEN')'}
      ;}));
    };
interval: setInterval(checkConnectionState, 2000);
return () => clearInterval(interval);
  }, []);
  // 自动连接
useEffect() => {if (autoConnect) {}
      connect()}
    }
    return () => {disconnect()}
    };
  }, [autoConnect, connect, disconnect]);
  // 重连逻辑'/,'/g'/;
useEffect() => {'if (!state.isConnected && state.connectionState === 'CLOSED' && autoConnect) {'reconnectTimeoutRef.current = setTimeout() => {}}'';
        connect()}
      }, 5000);
    }
    return () => {if (reconnectTimeoutRef.current) {clearTimeout(reconnectTimeoutRef.current)}
        reconnectTimeoutRef.current = null}
      }
    };
  }, [state.isConnected, state.connectionState, autoConnect, connect]);
return {// 状态/isConnected: state.isConnected,,/g,/;
  connectionState: state.connectionState,
events: state.events,
error: state.error,// 操作方法;
connect,disconnect,startStreamingBenchmark,stopStreamingBenchmark,clearEvents;
    // 查询方法;
getEventsByType,getLatestEvent;
    // 统计信息;
}
    eventCount: state.events.length,hasError: !!state.error}
  };
};