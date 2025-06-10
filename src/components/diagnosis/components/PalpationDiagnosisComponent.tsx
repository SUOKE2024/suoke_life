import React, { useCallback, useEffect, useState } from "react";";
import {;,}ActivityIndicator,;
Alert,;
Animated,;
ScrollView,;
StyleSheet,;
Text,;
TouchableOpacity,";"";
}
  View'}'';'';
} from "react-native";";
import { colors, spacing } from "../../../constants/theme";""/;,"/g"/;
import {;,}DiagnosisComponentProps,";"";
}
  PalpationDiagnosisData'}'';'';
} from "../../../types/diagnosis";""/;,"/g"/;
export const PalpationDiagnosisComponent: React.FC<DiagnosisComponentProps> = ({));,}onComplete,);
}
  onCancel)};
;}) => {const [isRecording, setIsRecording] = useState(false);';,}const [recordingType, setRecordingType] = useState<';'';
    'pulse' | 'pressure' | null;';'';
  >(null);
const [pulseData, setPulseData] = useState<number[]>([]);
const [pressureData, setPressureData] = useState<any>(null);
const [isAnalyzing, setIsAnalyzing] = useState(false);
const [analysisResult, setAnalysisResult] = useState<any>(null);
const [pulseAnimation] = useState(new Animated.Value(1));
';,'';
useEffect() => {';,}if (isRecording && recordingType === 'pulse') {';}      // 启动脉搏动画/;,'/g'/;
const  pulseAnimationLoop = Animated.loop(Animated.sequence([;,)Animated.timing(pulseAnimation, {)            toValue: 1.2,);,]duration: 600,);}}
            const useNativeDriver = true)}
          ;}),;
Animated.timing(pulseAnimation, {)toValue: 1,);,}duration: 600,);
}
            const useNativeDriver = true)}
          ;});
];
        ]);
      );
pulseAnimationLoop.start();
return () => pulseAnimationLoop.stop();
    }
  }, [isRecording, recordingType, pulseAnimation]);
const  startPulseRecording = useCallback() => {';,}setIsRecording(true);';,'';
setRecordingType('pulse');';'';

    // 模拟脉搏数据采集/;,/g/;
const  interval = setInterval() => {const newPulseValue = 60 + Math.random() * 40; // 模拟脉率60-100;/;}}/g/;
      setPulseData(prev) => [...prev, newPulseValue]);}
    }, 100);

    // 30秒后停止录制/;,/g/;
setTimeout() => {clearInterval(interval);,}setIsRecording(false);
setRecordingType(null);
}
}
    }, 30000);
  }, []);
const  startPressureTest = useCallback() => {';,}setIsRecording(true);';,'';
setRecordingType('pressure');';'';

    // 模拟按压测试/;,/g/;
setTimeout() => {const  mockPressureData = {';}}'';
        leftWrist: {,'}'';
cun: { strength: 'moderate', rhythm: 'regular', depth: 'normal' ;},';,'';
guan: { strength: 'weak', rhythm: 'regular', depth: 'deep' ;},';,'';
chi: { strength: 'strong', rhythm: 'regular', depth: 'shallow' ;}';'';
        },';,'';
rightWrist: {,'}'';
cun: { strength: 'moderate', rhythm: 'regular', depth: 'normal' ;},';,'';
guan: { strength: 'moderate', rhythm: 'regular', depth: 'normal' ;},';,'';
chi: { strength: 'weak', rhythm: 'irregular', depth: 'deep' ;}';'';
        }
      };
setPressureData(mockPressureData);
setIsRecording(false);
setRecordingType(null);

    }, 10000);
  }, []);
const  analyzePalpation = useCallback(async () => {if (pulseData.length === 0 && !pressureData) {}}
      return;}
    }

    setIsAnalyzing(true);
try {// 模拟切诊分析过程/;,}await: new Promise(resolve => setTimeout(resolve, 2000));,/g/;
const  avgPulseRate =;
pulseData.length > 0;
          ? Math.round(pulseData.reduce(a, b) => a + b, 0) / pulseData.length)/;/g/;
          : null;
const  mockResult = {const pulseAnalysis = pulseData.length > 0;}            ? {rate: avgPulseRate}const interpretation = avgPulseRate > 90;

                    : avgPulseRate < 60;

}
                const confidence = 0.89}
              ;}
            : null,;
const pressureAnalysis = pressureData;
          ? {leftWrist: {,;}}
}
              ;}
rightWrist: {,;}}
}
              ;}
const confidence = 0.85;
            ;}
          : null,;
syndromePattern: {,;}}
}
        ;}

      };
setAnalysisResult(mockResult);
    } catch (error) {}}
}
    } finally {}}
      setIsAnalyzing(false);}
    }
  }, [pulseData, pressureData]);
const  handleComplete = useCallback() => {const  data: PalpationDiagnosisData = {}      pulseData,;
touchData: pressureData,;
const metadata = {analysisResult,;}}
        const timestamp = new Date().toISOString()}
      ;}
    };
onComplete(data);
  }, [pulseData, pressureData, analysisResult, onComplete]);
const  renderPulseSection = () => (<View style={styles.testSection}>;)      <Text style={styles.sectionTitle}>脉诊检测</Text>/;/g/;
      <Text style={styles.sectionDescription}>;

      </Text>/;/g/;

      <View style={styles.pulseContainer}>;
        <Animated.View;  />/;,/g/;
style={}[;]}
            styles.pulseIndicator,}';'';
];
            { transform: [{ scale: pulseAnimation ;}] },';,'';
isRecording && recordingType === 'pulse' && styles.pulseRecording';'';
          ]}
        >;
          <Text style={styles.pulseText}>;

          </Text>/;/g/;
        </Animated.View>/;/g/;

        {pulseData.length > 0 && (})          <View style={styles.pulseDataContainer}>;
            <Text style={styles.pulseDataText}>;

            </Text>/;/g/;
            <Text style={styles.pulseDataText}>);
);
              {Math.round()';}}'';
                pulseData.reduce(a, b) => a + b, 0) / pulseData.length;'}''/;'/g'/;
              )}{' '}';'';
              次/分/;/g/;
            </Text>/;/g/;
          </View>/;/g/;
        )}
      </View>/;/g/;

      <TouchableOpacity;  />/;,/g/;
style={[;,]styles.testButton,';,}isRecording &&';,'';
recordingType === 'pulse' &&';'';
}
            styles.testButtonRecording}
];
        ]}
        onPress={startPulseRecording}
        disabled={isRecording}
      >';'';
        <Text style={styles.testButtonText}>';'';
          {isRecording && recordingType === 'pulse'';}            : pulseData.length > 0;'';

        </Text>/;/g/;
      </TouchableOpacity>/;/g/;
    </View>/;/g/;
  );
}
}
  const  renderPressureSection = () => (<View style={styles.testSection}>;)      <Text style={styles.sectionTitle}>按诊检测</Text>/;/g/;
      <Text style={styles.sectionDescription}>;

      </Text>/;/g/;

      <View style={styles.pressureContainer}>;
        <View style={styles.wristDiagram}>;
          <Text style={styles.wristTitle}>左手</Text>/;/g/;
          <View style={styles.pulsePoints}>;
            <View style={styles.pulsePoint}>;
              <Text style={styles.pulsePointText}>寸</Text>/;/g/;
            </View>/;/g/;
            <View style={styles.pulsePoint}>;
              <Text style={styles.pulsePointText}>关</Text>/;/g/;
            </View>/;/g/;
            <View style={styles.pulsePoint}>;
              <Text style={styles.pulsePointText}>尺</Text>/;/g/;
            </View>/;/g/;
          </View>/;/g/;
        </View>/;/g/;

        <View style={styles.wristDiagram}>;
          <Text style={styles.wristTitle}>右手</Text>/;/g/;
          <View style={styles.pulsePoints}>;
            <View style={styles.pulsePoint}>;
              <Text style={styles.pulsePointText}>寸</Text>/;/g/;
            </View>/;/g/;
            <View style={styles.pulsePoint}>;
              <Text style={styles.pulsePointText}>关</Text>/;/g/;
            </View>/;/g/;
            <View style={styles.pulsePoint}>;
              <Text style={styles.pulsePointText}>尺</Text>/;/g/;
            </View>/;/g/;
          </View>/;/g/;
        </View>/;/g/;
      </View>/;/g/;

      <TouchableOpacity;  />/;,/g/;
style={[;,]styles.testButton,';,}isRecording &&';,'';
recordingType === 'pressure' &&';'';
}
            styles.testButtonRecording}
];
        ]}
        onPress={startPressureTest}
        disabled={isRecording}
      >';'';
        <Text style={styles.testButtonText}>';'';
          {isRecording && recordingType === 'pressure'';}            : pressureData;'';

        </Text>)/;/g/;
      </TouchableOpacity>)/;/g/;
    </View>)/;/g/;
  );
const  renderAnalysisResult = () => {if (!analysisResult) return null;}}
}
    return (<View style={styles.resultContainer}>;)        <Text style={styles.resultTitle}>分析结果</Text>/;/g/;

        {analysisResult.pulseAnalysis && (})          <View style={styles.analysisSection}>;
            <Text style={styles.analysisTitle}>脉象分析</Text>/;/g/;
            <Text style={styles.analysisText}>;
              脉率：{analysisResult.pulseAnalysis.rate} 次/分/;/g/;
            </Text>/;/g/;
            <Text style={styles.analysisText}>;

            </Text>/;/g/;
            <Text style={styles.analysisText}>;

            </Text>/;/g/;
            <Text style={styles.analysisText}>;

            </Text>/;/g/;
            <Text style={styles.analysisText}>;

            </Text>)/;/g/;
            <Text style={styles.confidenceText}>);
);
              {(analysisResult.pulseAnalysis.confidence * 100).toFixed(1)}%;
            </Text>/;/g/;
          </View>/;/g/;
        )}

        {analysisResult.pressureAnalysis && (<View style={styles.analysisSection}>;)            <Text style={styles.analysisTitle}>按诊分析</Text>/;/g/;
            <View style={styles.wristAnalysis}>;
              <Text style={styles.wristAnalysisTitle}>左手：</Text>/;/g/;
              <Text style={styles.analysisText}>;
                {analysisResult.pressureAnalysis.leftWrist.overall}
              </Text>/;/g/;
              <Text style={styles.analysisText}>;

              </Text>/;/g/;
              <Text style={styles.analysisText}>;

              </Text>/;/g/;
              <Text style={styles.analysisText}>;

              </Text>/;/g/;
            </View>/;/g/;
            <View style={styles.wristAnalysis}>;
              <Text style={styles.wristAnalysisTitle}>右手：</Text>/;/g/;
              <Text style={styles.analysisText}>;
                {analysisResult.pressureAnalysis.rightWrist.overall}
              </Text>/;/g/;
              <Text style={styles.analysisText}>;

              </Text>/;/g/;
              <Text style={styles.analysisText}>;

              </Text>/;/g/;
              <Text style={styles.analysisText}>;

              </Text>/;/g/;
            </View>)/;/g/;
            <Text style={styles.confidenceText}>);
);
              {(analysisResult.pressureAnalysis.confidence * 100).toFixed(1)}%;
            </Text>/;/g/;
          </View>/;/g/;
        )}

        <View style={styles.recommendationSection}>;
          <Text style={styles.analysisTitle}>证候分析</Text>/;/g/;
          <Text style={styles.analysisText}>;

          </Text>/;/g/;
          <Text style={styles.analysisText}>;

          </Text>/;/g/;
          <Text style={styles.analysisText}>;

          </Text>/;/g/;

          <Text style={styles.analysisTitle}>调理建议</Text>/;/g/;
          {analysisResult.syndromePattern.recommendations.map(rec: string, index: number) => (<Text key={index;} style={styles.recommendationText}>);
                • {rec});
              </Text>)/;/g/;
            );
          )}
        </View>/;/g/;
      </View>/;/g/;
    );
  };
return (<ScrollView style={styles.container} showsVerticalScrollIndicator={false}>;)      <Text style={styles.title}>切诊分析</Text>/;/g/;
      <Text style={styles.subtitle}>;
);
      </Text>)/;/g/;
);
      {renderPulseSection()}
      {renderPressureSection()}

      <View style={styles.actionContainer}>;
        <TouchableOpacity;  />/;,/g/;
style={[styles.button, styles.analyzeButton]}
          onPress={analyzePalpation}
          disabled={isAnalyzing || (pulseData.length === 0 && !pressureData)}';'';
        >';'';
          {isAnalyzing ? (<ActivityIndicator size="small" color={colors.white}  />")""/;"/g"/;
          ) : (<Text style={styles.buttonText}>开始分析</Text>)/;/g/;
          )}
        </TouchableOpacity>/;/g/;
      </View>/;/g/;

      {renderAnalysisResult()}

      {analysisResult && (<View style={styles.actionContainer}>;)          <TouchableOpacity;  />/;,/g/;
style={[styles.button, styles.completeButton]}
            onPress={handleComplete}
          >;
            <Text style={styles.buttonText}>完成切诊</Text>)/;/g/;
          </TouchableOpacity>)/;/g/;
        </View>)/;/g/;
      )}
    </ScrollView>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {flex: 1,;
}
    const padding = spacing.md}
  ;}
title: {,";,}fontSize: 20,";,"";
fontWeight: '600';','';
color: colors.textPrimary,;
}
    const marginBottom = spacing.sm}
  ;}
subtitle: {fontSize: 14,;
color: colors.textSecondary,;
marginBottom: spacing.lg,;
}
    const lineHeight = 20}
  ;}
testSection: {marginBottom: spacing.lg,;
backgroundColor: colors.surface,;
borderRadius: 8,;
}
    const padding = spacing.md}
  ;}
sectionTitle: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
color: colors.textPrimary,;
}
    const marginBottom = spacing.xs}
  ;}
sectionDescription: {fontSize: 14,;
color: colors.textSecondary,;
}
    const marginBottom = spacing.md}
  ;},';,'';
pulseContainer: {,';,}alignItems: 'center';','';'';
}
    const marginBottom = spacing.md}
  ;}
pulseIndicator: {width: 80,;
height: 80,;
borderRadius: 40,';,'';
backgroundColor: colors.primary,';,'';
justifyContent: 'center';','';
alignItems: 'center';','';'';
}
    const marginBottom = spacing.md}
  ;}
pulseRecording: {,;}}
  const backgroundColor = colors.error}
  ;}
pulseText: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';'';
}
    const color = colors.white}
  ;},';,'';
pulseDataContainer: {,';}}'';
  const alignItems = 'center'}'';'';
  ;}
pulseDataText: {fontSize: 12,;
color: colors.textSecondary,;
}
    const marginBottom = spacing.xs}
  ;},';,'';
pressureContainer: {,';,}flexDirection: 'row';','';
justifyContent: 'space-around';','';'';
}
    const marginBottom = spacing.md}
  ;},';,'';
wristDiagram: {,';}}'';
  const alignItems = 'center'}'';'';
  ;}
wristTitle: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';
color: colors.textPrimary,;
}
    const marginBottom = spacing.sm}
  ;},';,'';
pulsePoints: {,';,}flexDirection: 'row';','';'';
}
    const gap = spacing.sm}
  ;}
pulsePoint: {width: 30,;
height: 30,;
borderRadius: 15,';,'';
backgroundColor: colors.border,';,'';
justifyContent: 'center';','';'';
}
    const alignItems = 'center'}'';'';
  ;}
pulsePointText: {fontSize: 12,';,'';
color: colors.textSecondary,';'';
}
    const fontWeight = '600'}'';'';
  ;}
testButton: {backgroundColor: colors.primary,;
paddingVertical: spacing.md,;
paddingHorizontal: spacing.lg,';,'';
borderRadius: 8,';'';
}
    const alignItems = 'center'}'';'';
  ;}
testButtonRecording: {,;}}
  const backgroundColor = colors.error}
  ;}
testButtonText: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';'';
}
    const color = colors.white}
  ;}
actionContainer: {,;}}
  const marginVertical = spacing.md}
  ;}
button: {paddingVertical: spacing.md,;
paddingHorizontal: spacing.lg,';,'';
borderRadius: 8,';'';
}
    const alignItems = 'center'}'';'';
  ;}
analyzeButton: {,;}}
  const backgroundColor = colors.primary}
  ;}
completeButton: {,;}}
  const backgroundColor = colors.success}
  ;}
buttonText: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';'';
}
    const color = colors.white}
  ;}
resultContainer: {backgroundColor: colors.surface,;
borderRadius: 8,;
padding: spacing.md,;
}
    const marginTop = spacing.md}
  ;}
resultTitle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';
color: colors.textPrimary,;
}
    const marginBottom = spacing.md}
  ;}
analysisSection: {marginBottom: spacing.md,;
paddingBottom: spacing.md,;
borderBottomWidth: 1,;
}
    const borderBottomColor = colors.border}
  ;}
analysisTitle: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
color: colors.textPrimary,;
}
    const marginBottom = spacing.sm}
  ;}
analysisText: {fontSize: 14,;
color: colors.textSecondary,;
}
    const marginBottom = spacing.xs}
  ;}
confidenceText: {fontSize: 12,';,'';
color: colors.primary,';'';
}
    const fontWeight = '500'}'';'';
  ;}
wristAnalysis: {,;}}
  const marginBottom = spacing.sm}
  ;}
wristAnalysisTitle: {,';,}fontSize: 14,';,'';
fontWeight: '600';','';
color: colors.textPrimary,;
}
    const marginBottom = spacing.xs}
  ;}
recommendationSection: {,;}}
  const marginTop = spacing.sm}
  ;}
recommendationText: {fontSize: 14,;
color: colors.textSecondary,;
marginBottom: spacing.xs,);
}
    const lineHeight = 20)}
  ;});
});';'';
''';