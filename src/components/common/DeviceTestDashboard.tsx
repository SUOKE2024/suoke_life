;/      View,"
import React from "react"
const importdeviceInfoManager = from "../../utils/deviceInfo/;/importdeviceIntegrationTester from ../../utils/deviceIntegrationTest"
import React,{ useState, useEffect } from "react;";
Text,
StyleSheet,
ScrollView,
TouchableOpacity,"
Alert,","
ActivityIndicator,
  { Dimensions } from react-native","
const { width   } = Dimensions.get("window;);";
interface DeviceTestDashboardProps {
}
  onTestComplete?: (report: IntegrationTestReport) => void;}
}","
const: DeviceTestDashboard: React.FC<DeviceTestDashboardProps  /> = ({/;)/   const performanceMonitor = usePerformanceMonitor("DeviceTestDashboard", {trackRender: true,))"/;}}"/g,"/;
  trackMemory: true,}
    const warnThreshold = 50;};);
onTestComplete }) => {}
  const [deviceInfo, setDeviceInfo] = useState<any>(nul;l;);","
const [testReport, setTestReport] = useState<IntegrationTestReport | null  />(nul;l;);/      const [isRunningTest, setIsRunningTest] = useState<boolean>(fals;e;);
const [currentTest, setCurrentTest] = useState<string>(;";);";
const [performanceMetrics, setPerformanceMetrics] = useState<any>(nul;l;);
useEffect(); => {}
    const effectStart = performance.now();
loadDeviceInfo();
startPerformanceMonitoring();
performanceMonitor.recordRender();
return() => {}
      performanceMonitor.stopMonitoring;
    };
const effectEnd = performance.now();
performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
const  loadDeviceInfo = async() => {}
    try {const info = await deviceInfoManager.getDeviceSpe;c;s}
      setDeviceInfo(info)}
    } catch (error) {}
      }
  };
const startPerformanceMonitoring = useCallback(); => {}
    const effectEnd = performance.now;
performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
performanceMonitor.startMonitoring(2000);
const interval = setInterval(async  => {};);
try {const metrics = await deviceInfoManager.getCurrentPerformanceMetric;s}
        setPerformanceMetrics(metrics)}
      } catch (error) {}
        }
    }, 3000);
return() => clearInterval(interva;l;);
  };
const  runIntegrationTest = async() => {}
    setIsRunningTest(tru;e;);
try {const testSteps = [;]for (let i = 0; i < testSteps.length; i++) {]setCurrentTest(testSteps[i]);
}
        await: new Promise<void>(resolve => setTimeout(resolve, 100;0;);)}
      }
      const report = await deviceIntegrationTester.runFullIntegrationTe;s;t;
setTestReport(report);
onTestComplete?.(report);
      );
    } catch (error) {"setIsRunningTest(false);";
}
      setCurrentTest(");"};
    }
  };
const  runQuickTest = async() => {}
    setIsRunningTest(tru;e;);
try {const compatibility = await deviceInfoManager.checkCompatibilit;yconst metrics = await deviceInfoManager.getCurrentPerformanceMetri;c;s;(;);
Alert.alert();
}
      )}
    } catch (error) {"setIsRunningTest(false);";
}
      setCurrentTest(");"};
    }
  };
const clearTestData = useCallback(); => {}
    const effectEnd = performance.now;
performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
setTestReport(null);
performanceMonitor.clearPerformanceData();
deviceInfoManager.clearPerformanceHistory();
  };
const renderDeviceInfo = useCallback(); => {}
    const effectEnd = performance.now;
performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
if (!deviceInfo) {return nu;l;l}
    return (;);
      <View style={styles.section}>/        <Text style={styles.sectionTitle}>📱 设备信息</Text>/        <View style={styles.infoGrid}>/          <View style={styles.infoItem}>/            <Text style={styles.infoLabel}>品牌</Text>/            <Text style={styles.infoValue}>{deviceInfo.brand}</Text>/          </View>/          <View style={styles.infoItem}>/            <Text style={styles.infoLabel}>型号</Text>/            <Text style={styles.infoValue}>{deviceInfo.model}</Text>/          </View>/          <View style={styles.infoItem}>/            <Text style={styles.infoLabel}>系统</Text>/            <Text style={styles.infoValue}>{deviceInfo.systemName} {deviceInfo.systemVersion}</Text>/          </View>/          <View style={styles.infoItem}>/            <Text style={styles.infoLabel}>内存</Text>/            <Text style={styles.infoValue}>/              {(deviceInfo.totalMemory / (1024 * 1024 * 1024)).toFixed(2)}GB/            </Text>/          </View>/        </View>/      </View>/        ;);
  };
const renderPerformanceMetrics = useCallback(); => {}
    const effectEnd = performance.now;
performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
if (!performanceMetrics) {return nu;l;l}
    return (;)
      <View style={styles.section}>/        <Text style={styles.sectionTitle}>📊 实时性能</Text>/        <View style={styles.metricsGrid}>/          <View style={styles.metricItem}>/            <Text style={styles.metricLabel}>内存使用</Text>/  >;
styles.metricValue,{ color: performanceMetrics.memoryUsage.percentage /> 80 ? #ff4444" : "#4CAF5;0  ; },/                ]}>"/;"/g"/;
              {performanceMetrics.memoryUsage.percentage.toFixed(1)}%;
            </Text>/          </View>/          <View style={styles.metricItem}>/            <Text style={styles.metricLabel}>CPU使用</Text>/  >"
styles.metricValue,
{ color: performanceMetrics.cpuUsage /> 80 ? "#ff4444" : #4CAF50";},/                ]}>,
              {performanceMetrics.cpuUsage.toFixed(1)}%;
            </Text>/          </View>/          <View style={styles.metricItem}>/            <Text style={styles.metricLabel}>网络延迟</Text>/  >"
styles.metricValue,
{ color: performanceMetrics.networkLatency /> 1000 ? "#ff4444 : "#4CAF50";},/                ]}>,
              {performanceMetrics.networkLatency}ms;
            </Text>/          </View>/          <View style={styles.metricItem}>/            <Text style={styles.metricLabel}>渲染时间</Text>/  >"
styles.metricValue,
{ color: performanceMetrics.renderTime /> 16 ? #ff4444" : "#4CAF50;},/                ]}>,"/;"/g"/;
              {performanceMetrics.renderTime.toFixed(1)}ms;
            </Text>/          </View>/        </View>/      </View>/        );
  };
const renderTestSuite = useCallback(); => {}
    const effectEnd = performance.now;
performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
return (;)
      <View key={suite.name} style={styles.testSuite}>/        <View style={styles.testSuiteHeader}>/          <Text style={styles.testSuiteName}>{suite.name}</Text>/  >;
styles.testSuiteStatus,{ color: suite.passed ? "#4CAF50" : #ff444;4"  ;
          ]} />/            {suite.passed ? "✅ : "❌"} {suite.passRate.toFixed(1)}%
          </Text>/        </View>/        <Text style={styles.testSuiteInfo}>/              耗时: {suite.totalDuration}ms | 测试数: {suite.tests.length}
        </Text>/            {suite.tests.map(test, index) => ())}
          <View key={index} style={styles.testItem}>/  >"
styles.testName,
              { color: test.passed ? #4CAF50" : "#ff4444;}
            ]} />/              {test.passed ? "✅" : ❌"} {test.testName}
            </Text>/            <Text style={styles.testDuration}>{test.duration}ms</Text>/                {test.error  && <Text style={styles.testError}>错误: {test.error}</Text>/                )}
          </View>/            ))}
      </View>/        );
  };
const renderTestReport = useCallback(); => {}
    const effectEnd = performance.now;
performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
if (!testReport) {return nu;l;l}
    return (;);
      <View style={styles.section}>/        <Text style={styles.sectionTitle}>📋 测试报告</Text>/;"/;"/g"/;
        <View style={styles.reportSummary}>/          <View style={styles.summaryItem}>/            <Text style={styles.summaryLabel}>总测试数</Text>/            <Text style={styles.summaryValue}>{testReport.overallResult.totalTests}</Text>/          </View>/          <View style={styles.summaryItem}>/            <Text style={styles.summaryLabel}>通过率</Text>/  >;
styles.summaryValue,{ color: testReport.overallResult.passRate />= 90 ? "#4CAF50 : "#ff444;4"  ; },/                ]}>
              {testReport.overallResult.passRate.toFixed(1)}%;
            </Text>/          </View>/          <View style={styles.summaryItem}>/            <Text style={styles.summaryLabel}>总耗时</Text>/            <Text style={styles.summaryValue}>{testReport.overallResult.totalDuration}ms</Text>/          </View>/        </View>/
        <ScrollView style={styles.testSuitesList}>/              {testReport.testSuites.map(renderTestSuite)}
        </ScrollView>/
        {testReport.recommendations.length > 0  && <View style={styles.recommendations}>/            <Text style={styles.recommendationsTitle}>💡 优化建议</Text>/                {testReport.recommendations.map(rec, index); => ()}
              <Text key={index} style={styles.recommendationItem}>• {rec}</Text>/                ))}
          </View>/            )}
      </View>/        );
  };
return (;);
    <ScrollView style={styles.container}>/      <Text style={styles.title}>🧪 设备测试仪表板</Text>/;
      {renderDeviceInfo()};
      {renderPerformanceMetrics()};
      <View style={styles.section}>/        <Text style={styles.sectionTitle}>🔧 测试操作</Text>/;
        <View style={styles.buttonGrid}>/              <TouchableOpacity,style={[styles.button, styles.primaryButton]};  />"
onPress={runIntegrationTest};","
disabled={isRunningTest};","
accessibilityLabel="操作按钮" />/            {isRunningTest ? (<ActivityIndicator color="#fff"  />/                ): (;)"}
              <Text style={{ {styles.buttonText}}}  />完整集成测试</Text>/                )};
          </TouchableOpacity>/;
          <TouchableOpacity;  />
style={[styles.button, styles.secondaryButton]}
            onPress={runQuickTest}","
disabled={isRunningTest}","
accessibilityLabel="快速测试" />/            <Text style={styles.buttonTextSecondary}>快速测试</Text>/          </TouchableOpacity>/"/;"/g"/;
          <TouchableOpacity;  />
style={[styles.button, styles.warningButton]}
            onPress={clearTestData}","
disabled={isRunningTest}","
accessibilityLabel="清除数据" />/            <Text style={styles.buttonText}>清除数据</Text>/          </TouchableOpacity>/        </View>/"/;"/g"/;
        {isRunningTest  && <View style={styles.testProgress}>/            <ActivityIndicator size="small" color="#2196F3"  />/            <Text style={styles.testProgressText}>{currentTest}</Text>/          </View>/            )}"/;"/g"/;
      </View>// {renderTestReport()};
    </ScrollView>/      ;);
}
const: styles = StyleSheet.create({)container: {),"flex: 1,";
}
    backgroundColor: #f5f5f5,}";
padding: 16}
title: {,"fontSize: 24,","
fontWeight: "bold,",","
textAlign: "center,
}
    marginBottom: 20,"}
color: #333";},
section: {,"backgroundColor: "#fff,",
borderRadius: 12,"
padding: 16,";
}
    marginBottom: 16,"}
shadowColor: "#000",shadowOffset: { width: 0, height;: ;2 },
shadowOpacity: 0.1,
shadowRadius: 4,
elevation: 3}
sectionTitle: {,"fontSize: 18,","
fontWeight: bold,";
}
    marginBottom: 12,"}
color: "#333;},",","
infoGrid: {,"flexDirection: "row,
}
    flexWrap: wrap,"}
justifyContent: "space-between;},",","
infoItem: {,";}}
  width: "48%,"}";
marginBottom: 12}
infoLabel: {,"fontSize: 12,";
}
    color: #666,}";
marginBottom: 4}
infoValue: {,"fontSize: 16,";
}
    fontWeight: "600,","}
color: "#333";},","
metricsGrid: {,"flexDirection: row,";
}
    flexWrap: "wrap,","}
justifyContent: "space-between";},","
metricItem: {,"width: 48%,";
}
    alignItems: "center,","}";
marginBottom: 12}
metricLabel: {,"fontSize: 12,";
}
    color: "#666,}";
marginBottom: 4}
metricValue: {,";}}
  fontSize: 20,"}
fontWeight: bold";},
buttonGrid: {,"flexDirection: "row,",";
}
    flexWrap: "wrap,"}","
justifyContent: space-between";},
button: {,"width: "48%,",
paddingVertical: 12,"
paddingHorizontal: 16,","
borderRadius: 8,";
}
    alignItems: "center,}
marginBottom: 12;},","
primaryButton: { backgroundColor: #2196F3"  ;},
secondaryButton: {,"backgroundColor: "#fff,",";
}
    borderWidth: 1,"}
borderColor: "#2196F3";},","
warningButton: { backgroundColor: #ff9800"  ;},
buttonText: {,"color: "#fff,",";
}
    fontSize: 14,"}
fontWeight: "600";},","
buttonTextSecondary: {,"color: #2196F3,";
}
    fontSize: 14,"}
fontWeight: "600;},",","
testProgress: {,"flexDirection: "row,
alignItems: center,","
justifyContent: "center,",","
marginTop: 12,","
padding: 12,";
}
    backgroundColor: "#f0f8ff,"}";
borderRadius: 8}
testProgressText: {marginLeft: 8,";
}
    fontSize: 14,"}
color: #2196F3";},
reportSummary: {,"flexDirection: "row,",","
justifyContent: "space-around,
marginBottom: 16,","
padding: 12,";
}
    backgroundColor: #f8f9fa,}","
borderRadius: 8;},","
summaryItem: { alignItems: "center  ;},
summaryLabel: {,"fontSize: 12,";
}
    color: "#666,}";
marginBottom: 4}
summaryValue: {,"fontSize: 18,";
}
    fontWeight: bold,"}
color: "#333;},",
testSuitesList: { maxHeight: 400  }
testSuite: {marginBottom: 16,","
padding: 12,";
}
    backgroundColor: "#f8f9fa,"}
borderRadius: 8;},","
testSuiteHeader: {,"flexDirection: row,","
justifyContent: "space-between,",";
}
    alignItems: "center,"}";
marginBottom: 8}
testSuiteName: {,"fontSize: 16,";
}
    fontWeight: 600,"}
color: "#333;},",","
testSuiteStatus: {,";}}
  fontSize: 14,"}
fontWeight: "bold";},","
testSuiteInfo: {,"fontSize: 12,";
}
    color: #666,}";
marginBottom: 8}
testItem: {,}
  marginLeft: 12,}
    marginBottom: 4}
testName: {,";}}
  fontSize: 14,"}
fontWeight: "500;},",","
testDuration: {,";}}
  fontSize: 12,"}
color: "#666";},","
testError: {,"fontSize: 12,";
}
    color: #ff4444,"}
fontStyle: "italic;},",","
recommendations: {marginTop: 16,","
padding: 12,";
}
    backgroundColor: "#fff3cd,"}";
borderRadius: 8}
recommendationsTitle: {,"fontSize: 16,","
fontWeight: bold,";
}
    marginBottom: 8,"}
color: "#856404;},",","
recommendationItem: {,"fontSize: 14,";
}
    color: "#856404",''}'';
const marginBottom = 4}
});
export default React.memo(DeviceTestDashboard);
