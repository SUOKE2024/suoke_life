';,'';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView } from "react-native";";
import { Constitution } from "../../services/medKnowledgeService";""/;,"/g"/;
interface ConstitutionCardProps {const constitution = Constitution;,}onPress?: () => void;
}
}
  showDetails?: boolean;}
}
export const ConstitutionCard: React.FC<ConstitutionCardProps> = ({)constitution,);,}onPress,);
}
  showDetails = false;)}
}) => {}}
}";"";
    };';,'';
return colors[type] || '#757575';';'';
  };
return (<TouchableOpacity;)  />/;,/g/;
style={[styles.card, { borderLeftColor: getConstitutionColor(constitution.type) ;}}]}
      onPress={onPress}
      activeOpacity={0.7}
    >;
      <View style={styles.header}>;
        <Text style={styles.name}>{constitution.name}</Text>/;/g/;
        <View style={[styles.typeBadge, { backgroundColor: getConstitutionColor(constitution.type) ;}}]}>;
          <Text style={styles.typeText}>{constitution.type}</Text>/;/g/;
        </View>/;/g/;
      </View>/;/g/;
      <Text style={styles.description} numberOfLines={showDetails ? undefined : 2}>;
        {constitution.description}
      </Text>/;/g/;
      {showDetails  && <View style={styles.detailsContainer}>;
          {// 特征}/;/g/;
          <View style={styles.section}>;
            <Text style={styles.sectionTitle}>主要特征</Text>/;/g/;
            <View style={styles.tagContainer}>;
              {constitution.characteristics.slice(0, 3).map(characteristic, index) => ())}
                <View key={index} style={styles.tag}>;
                  <Text style={styles.tagText}>{characteristic}</Text>/;/g/;
                </View>/;/g/;
              ))}
            </View>/;/g/;
          </View>/;/g/;
          {// 症状}/;/g/;
          {constitution.symptoms.length > 0  && <View style={styles.section}>;
              <Text style={styles.sectionTitle}>常见症状</Text>/;/g/;
              <View style={styles.tagContainer}>;
                {constitution.symptoms.slice(0, 4).map(symptom, index) => ())}
                  <View key={index} style={[styles.tag, styles.symptomTag]}>;
                    <Text style={styles.tagText}>{symptom}</Text>/;/g/;
                  </View>/;/g/;
                ))}
              </View>/;/g/;
            </View>/;/g/;
          )}
          {// 生活建议}/;/g/;
          <View style={styles.section}>;
            <Text style={styles.sectionTitle}>生活建议</Text>/;/g/;
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>;
              <View style={styles.lifestyleContainer}>;
                {constitution.lifestyle.diet.length > 0  && <View style={styles.lifestyleItem}>;
                    <Text style={styles.lifestyleLabel}>饮食</Text>'/;'/g'/;
                    <Text style={styles.lifestyleText}>';'';
                      {constitution.lifestyle.diet.slice(0, 2).join('、')}';'';
                    </Text>/;/g/;
                  </View>/;/g/;
                )}
                {constitution.lifestyle.exercise.length > 0  && <View style={styles.lifestyleItem}>;
                    <Text style={styles.lifestyleLabel}>运动</Text>'/;'/g'/;
                    <Text style={styles.lifestyleText}>';'';
                      {constitution.lifestyle.exercise.slice(0, 2).join('、')}';'';
                    </Text>/;/g/;
                  </View>/;/g/;
                )};
              </View>;/;/g/;
            </ScrollView>;/;/g/;
          </View>;/;/g/;
        </View>;/;/g/;
      )};
      <View style={styles.footer}>;
        <Text style={styles.timestamp}>;

        </Text>;/;/g/;
        {!showDetails && (;)}
          <Text style={styles.viewMore}>点击查看详情</Text>;/;/g/;
        )};
      </View>;/;/g/;
    </TouchableOpacity>;/;/g/;
  );
};
const  styles = StyleSheet.create({)';,}card: {,';,}backgroundColor: '#FFFFFF';','';
borderRadius: 12,;
padding: 16,;
marginVertical: 8,;
marginHorizontal: 16,';,'';
borderLeftWidth: 4,';,'';
shadowColor: '#000';','';
shadowOffset: {width: 0,;
}
      const height = 2;}
    }
shadowOpacity: 0.1,;
shadowRadius: 3.84,;
const elevation = 5;
  },';,'';
header: {,';,}flexDirection: 'row';','';
justifyContent: 'space-between';','';
alignItems: 'center';','';'';
}
    const marginBottom = 12;}
  }
name: {,';,}fontSize: 18,';,'';
fontWeight: 'bold';','';
color: '#333333';','';'';
}
    const flex = 1;}
  }
typeBadge: {paddingHorizontal: 12,;
paddingVertical: 4,;
}
    const borderRadius = 16;}
  },';,'';
typeText: {,';,}color: '#FFFFFF';','';
fontSize: 12,';'';
}
    const fontWeight = '600'}'';'';
  ;}
description: {,';,}fontSize: 14,';,'';
color: '#666666';','';
lineHeight: 20,;
}
    const marginBottom = 12;}
  }
detailsContainer: {,;}}
  const marginTop = 8;}
  }
section: {,;}}
  const marginBottom = 16;}
  }
sectionTitle: {,';,}fontSize: 16,';,'';
fontWeight: '600';','';
color: '#333333';','';'';
}
    const marginBottom = 8;}
  },';,'';
tagContainer: {,';,}flexDirection: 'row';','';
flexWrap: 'wrap';','';'';
}
    const gap = 8;}
  },';,'';
tag: {,';,}backgroundColor: '#F5F5F5';','';
paddingHorizontal: 12,;
paddingVertical: 6,;
borderRadius: 16,;
marginRight: 8,;
}
    const marginBottom = 4;}
  },';,'';
symptomTag: {,';}}'';
  const backgroundColor = '#FFF3E0'}'';'';
  ;}
tagText: {,';,}fontSize: 12,';'';
}
    const color = '#666666'}'';'';
  ;},';,'';
lifestyleContainer: {,';,}flexDirection: 'row';','';'';
}
    const gap = 16;}
  },';,'';
lifestyleItem: {,';,}backgroundColor: '#F8F9FA';','';
padding: 12,;
borderRadius: 8,;
}
    const minWidth = 120;}
  }
lifestyleLabel: {,';,}fontSize: 12,';,'';
fontWeight: '600';','';
color: '#333333';','';'';
}
    const marginBottom = 4;}
  }
lifestyleText: {,';,}fontSize: 12,';,'';
color: '#666666';','';'';
}
    const lineHeight = 16;}
  },';,'';
footer: {,';,}flexDirection: 'row';','';'';
}
    justifyContent: 'space-between',alignItems: 'center',marginTop: 12,paddingTop: 12,borderTopWidth: 1,borderTopColor: '#F0F0F0';'}'';'';
  },timestamp: {fontSize: 12,color: '#999999';')}'';'';
  },viewMore: {fontSize: 12,color: '#007AFF',fontWeight: '500';')}'';'';
  };)';'';
});