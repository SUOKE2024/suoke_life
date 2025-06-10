import: React, {;,}ComponentType,;
Profiler,;
ProfilerOnRenderCallback,;
useEffect,;
useRef,;
}
  useState}
} from "react";";
import PerformanceMonitor from "../../utils/performanceMonitor";""/;,"/g"/;
interface PerformanceProfilerProps {id: string}const children = React.ReactNode;
onRender?: ProfilerOnRenderCallback;
}
}
  enableLogging?: boolean;}
}

// 性能分析器组件/;,/g/;
export const PerformanceProfiler: React.FC<PerformanceProfilerProps> = ({)id}children,);
onRender,);
}
  enableLogging = false)};
;}) => {const handleRender: ProfilerOnRenderCallback = (profileId;,)phase}actualDuration,;
baseDuration,);
startTime,);
commitTime;);
  ) => {// 记录组件渲染性能/;,}PerformanceMonitor.recordComponentRender(profileId, actualDuration);/g/;

}
    if (enableLogging) {}
      console.log(`📊 Component ${profileId} ${phase}:`, {`)`}```;,```;
actualDuration: `${actualDuration.toFixed(2);}ms`,````;,```;
baseDuration: `${baseDuration.toFixed(2);}ms`,````;,```;
startTime: `${startTime.toFixed(2);}ms`,````;,```;
const commitTime = `${commitTime.toFixed(2);}ms`````;```;
      });
    }

    // 调用自定义回调/;,/g/;
if (onRender) {onRender(profileId,;,)phase}actualDuration,;
baseDuration,);
startTime,);
commitTime;);
}
      );}
    }

    // 性能警告/;,/g/;
if (actualDuration > 16) {}}
      console.warn()}
        `⚠️ Slow render detected in ${profileId}: ${actualDuration.toFixed(2)}ms`````;```;
      );
    }
  };
return (<Profiler id={id} onRender={handleRender}>);
      {children});
    </Profiler>)/;/g/;
  );
};

// 高阶组件：为组件添加性能监控/;,/g/;
export function withPerformanceMonitoring<P extends object>(WrappedComponent: ComponentType<P>;);
componentName?: string;);
) {const  displayName =;,}componentName ||;
WrappedComponent.displayName ||";,"";
WrappedComponent.name ||';'';
    'Component';';,'';
const  PerformanceMonitoredComponent: React.FC<P> = (props) => {const mountTimeRef = useRef<number>(0);,}const renderCountRef = useRef<number>(0);
useEffect() => {// 记录组件挂载/;,}mountTimeRef.current = performance.now();,/g/;
PerformanceMonitor.recordComponentMount(displayName);
return () => {// 记录组件卸载/;}}/g/;
        PerformanceMonitor.recordComponentUnmount(displayName);}
      };
    }, []);
useEffect() => {// 记录每次渲染/;,}renderCountRef.current++;,/g/;
const renderTime = performance.now() - mountTimeRef.current;
}
      PerformanceMonitor.recordComponentRender(displayName, renderTime);}
    });
return (<PerformanceProfiler id={displayName} enableLogging={__DEV__}>);
        <WrappedComponent {...props}  />)/;/g/;
      </PerformanceProfiler>)/;/g/;
    );
  };
PerformanceMonitoredComponent.displayName = `withPerformanceMonitoring(${displayName})`;````;,```;
return PerformanceMonitoredComponent;
}

// Hook：组件性能监控/;,/g/;
export function usePerformanceMonitoring() {;,}const mountTimeRef = useRef<number>(0);
const renderCountRef = useRef<number>(0);
const [renderTime, setRenderTime] = useState<number>(0);
useEffect() => {mountTimeRef.current = performance.now();,}PerformanceMonitor.recordComponentMount(componentName);
return () => {}}
}
      PerformanceMonitor.recordComponentUnmount(componentName);}
    };
  }, [componentName]);
useEffect() => {renderCountRef.current++;,}const currentRenderTime = performance.now() - mountTimeRef.current;
setRenderTime(currentRenderTime);
}
    PerformanceMonitor.recordComponentRender(componentName, currentRenderTime);}
  });
return {const renderCount = renderCountRef.current;,}renderTime,;
}
    const mountTime = mountTimeRef.current}
  ;};
}

// 性能监控装饰器/;,/g/;
export function performanceMonitored() {const return = function <P extends object>(target: ComponentType<P>) {;}}
}
    return withPerformanceMonitoring(target; componentName);}
  };
}
';'';
// 网络请求性能监控装饰器'/;,'/g'/;
export function monitorNetworkRequest() {return: function (target: any,);,}propertyName: string,);
const descriptor = PropertyDescriptor;);
  ) {const originalMethod = descriptor.value;,}descriptor.value = async function (...args: any[]) {const startTime = performance.now();,}try {result: await originalMethod.apply(this, args);,}const endTime = performance.now();

        // 记录成功的网络请求/;,/g/;
PerformanceMonitor.recordNetworkRequest(url,;,)method,;
startTime,);
endTime,);
          200;);
        );

}
}
        return result;}
      } catch (error: any) {const endTime = performance.now();}        // 记录失败的网络请求/;,/g/;
const status = error.response?.status || 500;
PerformanceMonitor.recordNetworkRequest(url,;,)method,;
startTime,);
endTime,);
status;);
        );

}
        const throw = error;}
      }
    };
return descriptor;
  };
}

// 性能基准测试组件/;,/g/;
interface PerformanceBenchmarkProps {const name = string;,}iterations?: number;
onComplete?: (results: BenchmarkResult) => void,;
}
}
  const children = React.ReactNode;}
}

interface BenchmarkResult {name: string}iterations: number,;
totalTime: number,;
averageTime: number,;
minTime: number,;
maxTime: number,;
}
}
  const fps = number;}
}

export const PerformanceBenchmark: React.FC<PerformanceBenchmarkProps> = ({)name}iterations = 100,);
onComplete,);
}
  children)};
;}) => {const [isRunning, setIsRunning] = useState(false);,}const [results, setResults] = useState<BenchmarkResult | null>(null);
const timesRef = useRef<number[]>([]);
const  runBenchmark = useCallback(() => {setIsRunning(true);,}timesRef.current = [];
const  runIteration = useCallback((iteration: number) => {if (iteration >= iterations) {}        // 计算结果/;,/g/;
const times = timesRef.current;
totalTime: times.reduce(sum, time) => sum + time, 0);
const averageTime = totalTime / times.length;/;,/g/;
const minTime = Math.min(...times);
const maxTime = Math.max(...times);
const fps = 1000 / averageTime;/;,/g/;
const  benchmarkResult: BenchmarkResult = {name}iterations,;
totalTime,;
averageTime,;
minTime,;
maxTime,;
}
          fps}
        ;};
setResults(benchmarkResult);
setIsRunning(false);
if (onComplete) {}}
          onComplete(benchmarkResult);}
        }

        console.log(`🏁 Benchmark ${name} completed:`, benchmarkResult);````;,```;
return;
      }

      const startTime = performance.now();

      // 使用 requestAnimationFrame 来测量渲染性能/;,/g/;
requestAnimationFrame() => {const endTime = performance.now();,}timesRef.current.push(endTime - startTime);

        // 继续下一次迭代/;/g/;
}
        setTimeout() => runIteration(iteration + 1), 0);}
      });
    };
runIteration(0);
  };
return (<div>);
      <button onClick={runBenchmark} disabled={isRunning}>);
        {isRunning;)}
          ? `Running... (${timesRef.current.length}/${iterations})````/`;`/g`/`;
          : `Run Benchmark: ${name;}`}````;```;
      </button>/;/g/;

      {results && (<div;  />/;,)style={}            marginTop: 10,';,'/g,'/;
  padding: 10,';,'';
border: '1px solid #ccc';','';'';
}
            const borderRadius = 4}
          ;}}
        >);
          <h4>Benchmark Results: {results.name;}</h4>)/;/g/;
          <p>Iterations: {results.iterations;}</p>)/;/g/;
          <p>Total Time: {results.totalTime.toFixed(2);}ms</p>/;/g/;
          <p>Average Time: {results.averageTime.toFixed(2);}ms</p>/;/g/;
          <p>Min Time: {results.minTime.toFixed(2);}ms</p>/;/g/;
          <p>Max Time: {results.maxTime.toFixed(2);}ms</p>/;/g/;
          <p>FPS: {results.fps.toFixed(2);}</p>/;/g/;
        </div>/;/g/;
      )}

      {children}
    </div>/;/g/;
  );
};
export default PerformanceProfiler;';'';
''';