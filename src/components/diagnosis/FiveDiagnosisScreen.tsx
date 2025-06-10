import { useNavigation } from "@react-navigation/native";""/;,"/g"/;
import React, { useCallback, useEffect, useState } from "react";";
import {;,}Alert,;
Dimensions,;
ScrollView,;
StyleSheet,;
Text,;
TouchableOpacity,";"";
}
  View'}'';'';
} from "react-native";";
import { colors, spacing } from "../../constants/theme";""/;,"/g"/;
import { fiveDiagnosisService } from "../../services/fiveDiagnosisService";""/;,"/g"/;
import {;,}DiagnosisInput,;
DiagnosisStep,";"";
}
  FiveDiagnosisResult'}'';'';
} from "../../types/diagnosis";""/;,"/g"/;
import Icon from "../common/Icon";""/;,"/g"/;
import CalculationDiagnosisComponent from "./CalculationDiagnosisComponent";""/;,"/g"/;
import { InquiryDiagnosisComponent } from "./components/InquiryDiagnosisComponent";""/;,"/g"/;
import { ListenDiagnosisComponent } from "./components/ListenDiagnosisComponent";""/;,"/g"/;
import { LookDiagnosisComponent } from "./components/LookDiagnosisComponent";""/;,"/g"/;
import { PalpationDiagnosisComponent } from "./components/PalpationDiagnosisComponent";""/;"/g"/;
';,'';
const { width } = Dimensions.get('window');';,'';
interface FiveDiagnosisScreenProps {}}
}
  onComplete?: (result: FiveDiagnosisResult) => void;}
}

const  FiveDiagnosisScreen: React.FC<Suspense fallback={<LoadingSpinner  />}><FiveDiagnosisScreenProps></Suspense> = ({/;));}}/g/;
  onComplete)}
;}) => {const navigation = useNavigation();}}
  const [currentStep, setCurrentStep] = useState<number>(0);}
  const [stepData, setStepData] = useState<Record<number, any>>({});
const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
const [analysisResult, setAnalysisResult] =;
useState<FiveDiagnosisResult | null>(null);
const [isServiceInitialized, setIsServiceInitialized] =;
useState<boolean>(false);
const  diagnosisSteps: DiagnosisStep[] = [;]';'';
    {';,}id: 'look';','';'';
';'';
';,'';
icon: 'eye';','';'';
}
      const component = LookDiagnosisComponent}
    ;},';'';
    {';,}id: 'listen';','';'';
';'';
';,'';
icon: 'ear';','';'';
}
      const component = ListenDiagnosisComponent}
    ;},';'';
    {';,}id: 'inquiry';','';'';
';'';
';,'';
icon: 'message-circle';','';'';
}
      const component = InquiryDiagnosisComponent}
    ;},';'';
    {';,}id: 'palpation';','';'';
';'';
';,'';
icon: 'hand';','';'';
}
      const component = PalpationDiagnosisComponent}
    ;},';'';
    {';,}id: 'calculation';','';'';
';'';
';,'';
icon: 'bar-chart';','';'';
}
      const component = CalculationDiagnosisComponent}
    ;}
];
  ];
const  initializeDiagnosisService = useCallback(async () => {try {}      const await = fiveDiagnosisService.initialize();
}
      setIsServiceInitialized(true);}
    } catch (error) {}}
}
    }
  }, []);
useEffect() => {}}
    initializeDiagnosisService();}
  }, [initializeDiagnosisService]);
const  handleStepPress = useCallback(stepIndex: number) => {if (stepIndex <= currentStep + 1) {}}
        setCurrentStep(stepIndex);}
      }
    }
    [currentStep];
  );
const: handleStepComplete = useCallback(stepIndex: number, data: unknown) => {setStepData(prev) => ({);}        ...prev,);
}
        [stepIndex]: data)}
      ;}));
if (stepIndex === currentStep && stepIndex < diagnosisSteps.length - 1) {}}
        setCurrentStep(stepIndex + 1);}
      }
    }
    [currentStep, diagnosisSteps.length];
  );
const  canPerformAnalysis = useCallback() => {}}
    return Object.keys(stepData).length >= 3; // 至少完成3个步骤}/;/g/;
  }, [stepData]);
const  performAnalysis = useCallback(async () => {if (!canPerformAnalysis() || !isServiceInitialized) {}}
      return;}
    }

    setIsAnalyzing(true);
try {const: input: DiagnosisInput = {lookData: stepData[0],;
listenData: stepData[1],;
inquiryData: stepData[2],;
palpationData: stepData[3],;
calculationData: stepData[4],;
}
        const timestamp = Date.now()}
      ;};
const result = await fiveDiagnosisService.performDiagnosis(input);
setAnalysisResult(result);
showAnalysisResult(result);
if (onComplete) {}}
        onComplete(result);}
      }
    } catch (error) {}}
}
    } finally {}}
      setIsAnalyzing(false);}
    }
  }, [canPerformAnalysis, isServiceInitialized, stepData, onComplete]);
const  showAnalysisResult = useCallback(result: FiveDiagnosisResult) => {Alert.alert([;));]        {);});
}
          onPress: () => showDetailedResult(result)}
        ;}
        {';}';'';
}
          const style = 'default'}'';'';
        ;}
];
      ];
    );
  }, []);
const  showDetailedResult = useCallback(result: FiveDiagnosisResult) => {}}
    // 这里可以导航到详细结果页面}/;/g/;
  ;}, []);
const  resetDiagnosis = useCallback() => {{';}';'';
}
        const style = 'cancel'}'';'';
      ;}
      {';}';,'';
style: 'destructive';','';
onPress: () => {}}
          setCurrentStep(0);}
          setStepData({});
setAnalysisResult(null);
        }
      }
    ]);
  }, []);
const  getCompletedStepsCount = useCallback() => {}}
    return Object.keys(stepData).length;}
  }, [stepData]);
const  getProgressPercentage = useCallback() => {}}
    return (getCompletedStepsCount() / diagnosisSteps.length) * 100;}/;/g/;
  }, [getCompletedStepsCount, diagnosisSteps.length]);
const  renderStepIndicator = useCallback() => {}
    return (<View style={styles.stepIndicator}>);
        {diagnosisSteps.map(step, index) => {}          const isCompleted = stepData[index] !== undefined;
const isCurrent = index === currentStep;
const isAccessible = index <= currentStep + 1;

}
          return (<TouchableOpacity;}  />/;,)key={step.id}/g/;
              style={[;,]styles.stepButton}isCompleted && styles.stepCompleted,;
isCurrent && styles.stepCurrent,);
}
                !isAccessible && styles.stepDisabled)}
];
              ]});
onPress={() => handleStepPress(index)}

              disabled={!isAccessible}
            >;
              <Icon;  />/;,/g/;
name={step.icon}
                size={20}
                color={isCompleted;}                    ? colors.white;
                    : isCurrent;
                      ? colors.primary;
                      : isAccessible;
                        ? colors.textSecondary;
}
                        : colors.border;}
                }
              />/;/g/;
              <Text;  />/;,/g/;
style={[;,]styles.stepTitle}isCompleted && styles.stepTitleCompleted,;
isCurrent && styles.stepTitleCurrent,;
}
                  !isAccessible && styles.stepTitleDisabled}
];
                ]}
              >;
                {step.title}
              </Text>/;/g/;
            </TouchableOpacity>/;/g/;
          );
        })}
      </View>/;/g/;
    );
  }, [diagnosisSteps, stepData, currentStep, handleStepPress]);
const  renderCurrentStep = useCallback() => {const step = diagnosisSteps[currentStep];,}if (!step) return null;
const StepComponent = step.component;
}
}
    return (<View style={styles.stepContent}>;)        <View style={styles.stepHeader}>;
          <Icon name={step.icon} size={32} color={colors.primary}  />/;/g/;
          <View style={styles.stepInfo}>;
            <Text style={styles.stepName}>{step.title}</Text>/;/g/;
            <Text style={styles.stepDescription}>{step.description}</Text>/;/g/;
          </View>/;/g/;
        </View>)/;/g/;
        <View style={styles.stepComponent}>);
          <StepComponent;)  />/;,/g/;
onComplete={(data: any) => handleStepComplete(currentStep, data);}
            onCancel={() => {}}
          />/;/g/;
        </View>/;/g/;
      </View>/;/g/;
    );
  }, [diagnosisSteps, currentStep, handleStepComplete]);
const  renderProgressBar = useCallback() => {}}
    const progress = getProgressPercentage();}
    return (<View style={styles.progressContainer}>;)        <View style={styles.progressBar}>;
          <View style={[styles.progressFill, { width: `${progress;}%` }]}  />``)``/`;`/g`/`;
        </View>)/;/g/;
        <Text style={styles.progressText}>);
          {getCompletedStepsCount()}/{diagnosisSteps.length} 步骤完成/;/g/;
        </Text>/;/g/;
      </View>/;/g/;
    );
  }, [getProgressPercentage, getCompletedStepsCount, diagnosisSteps.length]);
const  renderActionButtons = useCallback() => {}
    return (<View style={styles.actionButtons}>;)        <TouchableOpacity;  />/;,/g/;
style={[styles.actionButton, styles.resetButton]}
          onPress={resetDiagnosis}
';'';
        >';'';
          <Icon name="refresh-cw" size={16} color={colors.textSecondary}  />"/;"/g"/;
          <Text style={styles.resetButtonText}>重置</Text>/;/g/;
        </TouchableOpacity>/;/g/;
        <TouchableOpacity;  />/;,/g/;
style={[;]);,}styles.actionButton,);
styles.analyzeButton,);
            (!canPerformAnalysis() || isAnalyzing) &&;
}
              styles.analyzeButtonDisabled}
];
          ]}
          onPress={performAnalysis}
          disabled={!canPerformAnalysis() || isAnalyzing}

        >";"";
          <Icon;"  />/;,"/g"/;
name="zap";
size={16}
            color={!canPerformAnalysis() || isAnalyzing;}                ? colors.textSecondary;
}
                : colors.white;}
            }
          />/;/g/;
          <Text;  />/;,/g/;
style={[;,]styles.analyzeButtonText,;}              (!canPerformAnalysis() || isAnalyzing) &&;
}
                styles.analyzeButtonTextDisabled}
];
            ]}
          >;

          </Text>/;/g/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;
    );
  }, [resetDiagnosis, canPerformAnalysis, isAnalyzing, performAnalysis]);
return (<ScrollView style={styles.container} showsVerticalScrollIndicator={false}>;)      {// 头部})/;/g/;
      <View style={styles.header}>);
        <TouchableOpacity;)  />/;,/g/;
onPress={() => navigation.goBack()}
          style={styles.backButton}
";"";
        >";"";
          <Icon name="arrow-left" size={24} color={colors.textPrimary}  />"/;"/g"/;
        </TouchableOpacity>/;/g/;
        <Text style={styles.headerTitle}>五诊合参</Text>/;/g/;
        <View style={styles.headerRight}  />/;/g/;
      </View>/;/g/;

      {// 进度条}/;/g/;
      {renderProgressBar()}

      {// 步骤指示器}/;/g/;
      {renderStepIndicator()}

      {// 当前步骤内容}/;/g/;
      {renderCurrentStep()}

      {// 操作按钮}/;/g/;
      {renderActionButtons()}

      {// 结果显示}/;/g/;
      {analysisResult && (<View style={styles.resultContainer}>;)          <Text style={styles.resultTitle}>诊断结果</Text>/;/g/;
          <Text style={styles.resultText}>;
            {analysisResult.overallAssessment});
          </Text>)/;/g/;
        </View>)/;/g/;
      )}
    </ScrollView>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {flex: 1,;
}
    const backgroundColor = colors.background}
  ;},";,"";
header: {,";,}flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'space-between';','';
paddingHorizontal: spacing.lg,;
paddingVertical: spacing.md,;
borderBottomWidth: 1,;
}
    const borderBottomColor = colors.border}
  ;}
backButton: {,;}}
  const padding = spacing.sm}
  ;}
headerTitle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';'';
}
    const color = colors.textPrimary}
  ;}
headerRight: {,;}}
  const width = 40}
  ;}
progressContainer: {paddingHorizontal: spacing.lg,;
}
    const paddingVertical = spacing.md}
  ;}
progressBar: {height: 4,;
backgroundColor: colors.border,;
borderRadius: 2,;
}
    const marginBottom = spacing.sm}
  ;},';,'';
progressFill: {,';,}height: '100%';','';
backgroundColor: colors.primary,;
}
    const borderRadius = 2}
  ;}
progressText: {fontSize: 12,';,'';
color: colors.textSecondary,';'';
}
    const textAlign = 'center'}'';'';
  ;},';,'';
stepIndicator: {,';,}flexDirection: 'row';','';
paddingHorizontal: spacing.lg,;
}
    const paddingVertical = spacing.md}
  ;}
stepButton: {,';,}flex: 1,';,'';
alignItems: 'center';','';
paddingVertical: spacing.sm,;
marginHorizontal: spacing.xs,;
borderRadius: 8,;
}
    const backgroundColor = colors.surface}
  ;}
stepCompleted: {,;}}
  const backgroundColor = colors.primary}
  ;}
stepCurrent: {backgroundColor: colors.surface,;
borderWidth: 2,;
}
    const borderColor = colors.primary}
  ;}
stepDisabled: {,;}}
  const backgroundColor = colors.border}
  ;}
stepTitle: {fontSize: 12,;
color: colors.textSecondary,;
}
    const marginTop = spacing.xs}
  ;}
stepTitleCompleted: {,;}}
  const color = colors.white}
  ;}
stepTitleCurrent: {,';,}color: colors.primary,';'';
}
    const fontWeight = '600'}'';'';
  ;}
stepTitleDisabled: {,;}}
  const color = colors.textTertiary}
  ;}
stepContent: {margin: spacing.lg,;
backgroundColor: colors.surface,;
borderRadius: 12,;
}
    const padding = spacing.lg}
  ;},';,'';
stepHeader: {,';,}flexDirection: 'row';','';
alignItems: 'center';','';'';
}
    const marginBottom = spacing.lg}
  ;}
stepInfo: {marginLeft: spacing.md,;
}
    const flex = 1}
  ;}
stepName: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';'';
}
    const color = colors.textPrimary}
  ;}
stepDescription: {fontSize: 14,;
color: colors.textSecondary,;
}
    const marginTop = spacing.xs}
  ;}
stepComponent: {,;}}
  const minHeight = 200}
  ;},';,'';
actionButtons: {,';,}flexDirection: 'row';','';
paddingHorizontal: spacing.lg,;
paddingVertical: spacing.md,;
}
    const gap = spacing.md}
  ;}
actionButton: {,';,}flex: 1,';,'';
flexDirection: 'row';','';
alignItems: 'center';','';
justifyContent: 'center';','';
paddingVertical: spacing.md,;
borderRadius: 8,;
}
    const gap = spacing.sm}
  ;}
resetButton: {backgroundColor: colors.surface,;
borderWidth: 1,;
}
    const borderColor = colors.border}
  ;}
resetButtonText: {color: colors.textSecondary,';,'';
fontSize: 16,';'';
}
    const fontWeight = '600'}'';'';
  ;}
analyzeButton: {,;}}
  const backgroundColor = colors.primary}
  ;}
analyzeButtonDisabled: {,;}}
  const backgroundColor = colors.border}
  ;}
analyzeButtonText: {color: colors.white,';,'';
fontSize: 16,';'';
}
    const fontWeight = '600'}'';'';
  ;}
analyzeButtonTextDisabled: {,;}}
  const color = colors.textSecondary}
  ;}
resultContainer: {margin: spacing.lg,;
backgroundColor: colors.surface,;
borderRadius: 12,;
padding: spacing.lg,;
borderLeftWidth: 4,;
}
    const borderLeftColor = colors.success}
  ;}
resultTitle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';
color: colors.textPrimary,;
}
    const marginBottom = spacing.md}
  ;}
resultText: {fontSize: 16,;
color: colors.textSecondary,);
}
    const lineHeight = 24)}
  ;});
});
export default React.memo(FiveDiagnosisScreen);';'';
''';