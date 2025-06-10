import React, { useState, useCallback } from "react";";
import {;,}View,;
Text,;
TextInput,;
TouchableOpacity,;
ScrollView,;
StyleSheet,;
Alert,";"";
}
  ActivityIndicator;'}'';'';
} from "react-native";"";"";
// 简化的类型定义/;,/g/;
interface TCMAnalysisRequest {symptoms: string[]}userId: string,;
const constitutionType = string;
medicalHistory?: string[];
currentMedications?: string[];
lifestyleFactors?: {diet?: string;,}exercise?: string;
sleep?: string;
stress?: string;
}
}
    environment?: string;}
};
}
interface TCMAnalysisResponse {syndromeAnalysis: {primarySyndrome: string,;
secondarySyndromes: string[],;
}
}
  const confidence = number;}
};
constitutionAssessment: {constitutionType: string,;
}
  const characteristics = string[];}
  };
recommendations: {lifestyle: string[],;
dietary: string[],;
}
  const exercise = string[];}
  };
}
interface HerbRecommendationRequest {syndromeType: string}constitutionType: string,;
userId: string,;
}
}
  const currentSymptoms = string[];}
}
interface HerbRecommendationResponse {formula: {name: string,;
herbs: Array<{name: string,;
dosage: string,;
}
}
  const function = string;}
}>;
  };
instructions: string[],;
const precautions = string[];
}
interface TCMAnalysisComponentProps {const userId = string;,}onAnalysisResult?: (result: TCMAnalysisResponse) => void;
onHerbResult?: (result: HerbRecommendationResponse) => void;
}
}
  onError?: (error: Error) => void;}
}
export const TCMAnalysisComponent: React.FC<TCMAnalysisComponentProps> = ({)userId}onAnalysisResult,);
onHerbResult,);
}
  onError;)}';'';
}) => {';,}const [symptoms, setSymptoms] = useState<string[]>([']);'';
const [constitutionType, setConstitutionType] = useState<string>('balanced');';,'';
const [medicalHistory, setMedicalHistory] = useState(');'';
const [currentMedications, setCurrentMedications] = useState(');'';
const [lifestyle, setLifestyle] = useState({';,)diet: "";","";,}exercise: '';','';
sleep: ';',')'';
stress: ';',)';'';
}
    const environment = ')'}'';'';
  ;});
const [isAnalyzing, setIsAnalyzing] = useState(false);
const [isRecommending, setIsRecommending] = useState(false);
const [analysisResult, setAnalysisResult] = useState<TCMAnalysisResponse | null>(null);
const [herbResult, setHerbResult] = useState<HerbRecommendationResponse | null>(null);
  // 体质类型选项/;,/g/;
const  constitutionTypes = [;]';'';
    {';,}const value = "balanced";";"";
";"";
    {";,}const value = "qi_deficiency";";"";
";"";
    {";,}const value = "yang_deficiency";";"";
";"";
    {";,}const value = "yin_deficiency";";"";
";"";
    {";,}const value = "phlegm_dampness";";"";
";"";
    {";,}const value = "damp_heat";";"";
";"";
    {";,}const value = "blood_stasis";";"";
";"";
    {";,}const value = "qi_stagnation";";"";
";"";
    {";,}const value = "special_constitution";";"";

];
  ];
  // 添加症状"/;,"/g"/;
const  addSymptom = useCallback() => {";}}"";
    setSymptoms(prev => [...prev, '']);'}'';'';
  }, []);
  // 更新症状/;,/g,/;
  const: updateSymptom = useCallback(index: number, value: string) => {}}
    setSymptoms(prev => prev.map(symptom, i) => i === index ? value : symptom));}
  }, []);
  // 删除症状/;,/g/;
const  removeSymptom = useCallback(index: number) => {if (symptoms.length > 1) {}}
      setSymptoms(prev => prev.filter(_, i) => i !== index));}
    }
  }, [symptoms.length]);
  // 执行中医分析/;,/g/;
const  handleAnalysis = useCallback(async () => {const validSymptoms = symptoms.filter(s => s.trim());,}if (validSymptoms.length === 0) {}}
      return;}
    }
    setIsAnalyzing(true);
setAnalysisResult(null);
try {// 模拟分析结果/;,}const: mockResult: TCMAnalysisResponse = {syndromeAnalysis: {,;}}/g/;
          const confidence = 0.85;}
        }
constitutionAssessment: {const constitutionType = constitutionType;
}
}
        }
recommendations: {,;}}
}
        ;}
      };
setAnalysisResult(mockResult);
onAnalysisResult?.(mockResult);
    } catch (error) {onError?.(error as Error);}}
}
    } finally {}}
      setIsAnalyzing(false);}
    }
  }, [symptoms, userId, constitutionType, medicalHistory, currentMedications, lifestyle, onAnalysisResult, onError]);
  // 获取中药推荐/;,/g/;
const  handleHerbRecommendation = useCallback(async () => {if (!analysisResult) {}}
      return;}
    }
    setIsRecommending(true);
setHerbResult(null);
try {// 模拟中药推荐结果/;,}const: mockHerbResult: HerbRecommendationResponse = {formula: {const herbs = [;]{{}            {{}}/g/;
];
          ]}
        ;}

      };
setHerbResult(mockHerbResult);
onHerbResult?.(mockHerbResult);
    } catch (error) {onError?.(error as Error);}}
}
    } finally {}}
      setIsRecommending(false);}
    }
  }, [analysisResult, symptoms, userId, onHerbResult, onError]);
  // 清除结果'/;,'/g'/;
const  handleClear = useCallback() => {';,}setSymptoms([']);'';
setConstitutionType('balanced');';,'';
setMedicalHistory(');'';
setCurrentMedications(');'';
setLifestyle({';,)diet: "";","";,}exercise: '';','';
sleep: ';',')'';
stress: ';',)';'';
}
      const environment = ')'}'';'';
    ;});
setAnalysisResult(null);
setHerbResult(null);
  }, []);
return (<ScrollView style={styles.container}>;)      <Text style={styles.title}>中医智能分析</Text>/;/g/;
      {});
      <View style={styles.section}>);
        <Text style={styles.sectionTitle}>症状描述</Text>)/;/g/;
        {symptoms.map(symptom, index) => ())}
          <View key={index} style={styles.symptomRow}>;
            <TextInput;  />/;,/g/;
style={styles.symptomInput}
              value={symptom}
              onChangeText={(value) => updateSymptom(index, value)}

            />/;/g/;
            {symptoms.length > 1  && <TouchableOpacity;}  />/;,/g/;
style={styles.removeButton}
                onPress={() => removeSymptom(index)}
              >;
                <Text style={styles.removeButtonText}>删除</Text>/;/g/;
              </TouchableOpacity>/;/g/;
            )}
          </View>/;/g/;
        ))}
        <TouchableOpacity style={styles.addButton} onPress={addSymptom}>;
          <Text style={styles.addButtonText}>添加症状</Text>/;/g/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;
      {}
      <View style={styles.section}>;
        <Text style={styles.sectionTitle}>体质类型</Text>/;/g/;
        <View style={styles.constitutionGrid}>;
          {constitutionTypes.map(type) => ();}}
            <TouchableOpacity;}  />/;,/g/;
key={type.value}
              style={[;,]styles.constitutionButton,;}}
                constitutionType === type.value && styles.constitutionButtonActive;}
];
              ]}}
              onPress={() => setConstitutionType(type.value)}
            >;
              <Text;  />/;,/g/;
style={[;,]styles.constitutionButtonText,;}}
                  constitutionType === type.value && styles.constitutionButtonTextActive;}
];
                ]}}
              >;
                {type.label}
              </Text>/;/g/;
            </TouchableOpacity>/;/g/;
          ))}
        </View>/;/g/;
      </View>/;/g/;
      {}
      <View style={styles.buttonContainer}>;
        <TouchableOpacity;  />/;,/g/;
style={[styles.button, styles.primaryButton]}
          onPress={handleAnalysis}
          disabled={isAnalyzing}
        >';'';
          {isAnalyzing ? ()';}}'';
            <ActivityIndicator color="#fff"  />"}""/;"/g"/;
          ) : (<Text style={styles.buttonText}>开始分析</Text>)/;/g/;
          )}
        </TouchableOpacity>/;/g/;
        {analysisResult  && <TouchableOpacity;}  />/;,/g/;
style={[styles.button, styles.secondaryButton]}
            onPress={handleHerbRecommendation}
            disabled={isRecommending}
          >";"";
            {isRecommending ? ()";}}"";
              <ActivityIndicator color="#007AFF"  />"}""/;"/g"/;
            ) : (<Text style={[styles.buttonText, styles.secondaryButtonText]}>中药推荐</Text>)/;/g/;
            )}
          </TouchableOpacity>/;/g/;
        )}
        <TouchableOpacity;  />/;,/g/;
style={[styles.button, styles.clearButton]}
          onPress={handleClear}
        >;
          <Text style={[styles.buttonText, styles.clearButtonText]}>清除</Text>/;/g/;
        </TouchableOpacity>/;/g/;
      </View>/;/g/;
      {}
      {analysisResult  && <View style={styles.resultSection}>;
          <Text style={styles.resultTitle}>分析结果</Text>/;/g/;
          <View style={styles.resultCard}>;
            <Text style={styles.resultLabel}>主要证型：</Text>/;/g/;
            <Text style={styles.resultValue}>{analysisResult.syndromeAnalysis.primarySyndrome}</Text>/;/g/;
                        <Text style={styles.resultLabel}>体质评估：</Text>/;/g/;
            <Text style={styles.resultValue}>{analysisResult.constitutionAssessment.constitutionType}</Text>/;/g/;
                        <Text style={styles.resultLabel}>生活建议：</Text>/;/g/;
            {analysisResult.recommendations.lifestyle.map(item, index) => ())}
              <Text key={index} style={styles.recommendationItem}>• {item}</Text>/;/g/;
            ))}
          </View>/;/g/;
        </View>/;/g/;
      )}
      {}
      {herbResult  && <View style={styles.resultSection}>;
          <Text style={styles.resultTitle}>中药推荐</Text>/;/g/;
          <View style={styles.resultCard}>;
            <Text style={styles.resultLabel}>方剂名称：</Text>/;/g/;
            <Text style={styles.resultValue}>{herbResult.formula.name}</Text>/;/g/;
                        <Text style={styles.resultLabel}>药物组成：</Text>/;/g/;
            {herbResult.formula.herbs.map(herb, index) => ())}
              <Text key={index} style={styles.herbItem}>;
                {herb.name} {herb.dosage} - {herb.function}
              </Text>/;/g/;
            ))}
                        <Text style={styles.resultLabel}>服用方法：</Text>/;/g/;
            {herbResult.instructions.map(instruction, index) => ())}
              <Text key={index} style={styles.instructionItem}>• {instruction}</Text>/;/g/;
            ))}
          </View>/;/g/;
        </View>/;/g/;
      )}
    </ScrollView>/;/g/;
  );
};
const  styles = StyleSheet.create({)container: {,";,}flex: 1,";"";
}
    backgroundColor: '#f5f5f5';',}'';
padding: 16;}
title: {,';,}fontSize: 24,';,'';
fontWeight: 'bold';','';
color: '#333';','';'';
}
    textAlign: 'center';',}'';
marginBottom: 24;},';,'';
section: {,';,}backgroundColor: '#fff';','';
borderRadius: 12,;
}
    padding: 16,}
    marginBottom: 16;}
sectionTitle: {,';,}fontSize: 18,';,'';
fontWeight: '600';','';'';
}
    color: '#333';','}'';
marginBottom: 12;},';,'';
symptomRow: {,';,}flexDirection: 'row';','';'';
}
    alignItems: 'center';',}'';
marginBottom: 8;}
symptomInput: {flex: 1,';,'';
borderWidth: 1,';,'';
borderColor: '#ddd';','';
borderRadius: 8,;
}
    padding: 12,}
    fontSize: 16;}
removeButton: {,';,}marginLeft: 8,';,'';
backgroundColor: '#FF3B30';','';
borderRadius: 6,;
}
    paddingHorizontal: 12,}
    paddingVertical: 8;},';,'';
removeButtonText: {,';}}'';
  color: '#fff';','}'';
fontSize: 14;},';,'';
addButton: {,';,}backgroundColor: '#007AFF';','';
borderRadius: 8,';,'';
padding: 12,';'';
}
    alignItems: 'center';',}'';
marginTop: 8;},';,'';
addButtonText: {,';,}color: '#fff';','';'';
}
    fontSize: 16,'}'';
fontWeight: '600';},';,'';
constitutionGrid: {,';,}flexDirection: 'row';','';'';
}
    flexWrap: 'wrap';',}'';
gap: 8;},';,'';
constitutionButton: {,';,}backgroundColor: '#f0f0f0';','';
borderRadius: 20,;
paddingHorizontal: 16,;
}
    paddingVertical: 8,}
    marginBottom: 8;},';,'';
constitutionButtonActive: {,'}'';
backgroundColor: '#007AFF';},';,'';
constitutionButtonText: {,';}}'';
  fontSize: 14,'}'';
color: '#666';},';,'';
constitutionButtonTextActive: {,'}'';
color: '#fff';},';,'';
buttonContainer: {,;}}
  gap: 12,}
    marginBottom: 24;}
button: {borderRadius: 12,';'';
}
    padding: 16,'}'';
alignItems: 'center';},';,'';
primaryButton: {,'}'';
backgroundColor: '#007AFF';},';,'';
secondaryButton: {,';,}backgroundColor: '#fff';','';'';
}
    borderWidth: 1,'}'';
borderColor: '#007AFF';},';,'';
clearButton: {,';,}backgroundColor: '#fff';','';'';
}
    borderWidth: 1,'}'';
borderColor: '#FF3B30';},';,'';
buttonText: {,';,}fontSize: 16,';'';
}
    fontWeight: '600';','}';,'';
color: '#fff';},';,'';
secondaryButtonText: {,'}'';
color: '#007AFF';},';,'';
clearButtonText: {,'}'';
color: '#FF3B30';},';,'';
resultSection: {,}
  marginBottom: 24;}
resultTitle: {,';,}fontSize: 20,';,'';
fontWeight: 'bold';','';'';
}
    color: '#333';','}'';
marginBottom: 12;},';,'';
resultCard: {,';,}backgroundColor: '#fff';','';'';
}
    borderRadius: 12,}
    padding: 16;}
resultLabel: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
color: '#333';','';'';
}
    marginTop: 12,}
    marginBottom: 4;}
resultValue: {,';,}fontSize: 16,';'';
}
    color: '#666';',}'';
marginBottom: 8;}
recommendationItem: {,';,}fontSize: 14,';'';
}
    color: '#666';',}'';
marginBottom: 4;}
herbItem: {,';,}fontSize: 14,';,'';
color: '#666';','';'';
}
    marginBottom: 4,}
    paddingLeft: 8;}
instructionItem: {,)';,}fontSize: 14,)';'';
}
    color: '#666';')',}'';
const marginBottom = 4;}});';,'';
export default TCMAnalysisComponent;