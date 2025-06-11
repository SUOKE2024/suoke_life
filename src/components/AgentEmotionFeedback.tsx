import {  StyleSheet, Text, TouchableOpacity, View  } from "react-native";
interface FeedbackItem {key: string}label: string,
}
}
  const desc = string}
}
interface AgentEmotionFeedbackProps {
onFeedback: (feedbackKey: string) => voiddisabled?: boolean;
}
  children?: React.ReactNode}
}
const  FEEDBACKS: FeedbackItem[] = [;]
  {'key: 'like,'
const label = '👍';
}
}
  },'
  {'key: 'care,'
const label = '🤗';
}
}
  },'
  {'key: 'suggest,'
const label = '💡';
}
}
  },'
  {'key: 'dislike,'
const label = '👎';
}
}
  }
];
];
export const AgentEmotionFeedback: React.FC<AgentEmotionFeedbackProps> = ({))onFeedback,);
}
  disabled = false,)};
;}) => {const  handleFeedback = useCallback((feedbackKey: string) => {}    if (!disabled) {}
      onFeedback(feedbackKey)}
    }
  };
return (<View style={styles.container}>);
      <Text style={styles.title}>您的反馈</Text>)
      <View style={styles.row}>);
        {FEEDBACKS.map((fb) => (<TouchableOpacity,)}  />
key={fb.key});
style={[styles.btn, disabled && styles.btnDisabled]});
onPress={() => handleFeedback(fb.key)}
            disabled={disabled}
accessibilityRole="button";
accessibilityState={{ disabled }
          >;
            <Text style={[styles.icon, disabled && styles.iconDisabled]}>;
              {fb.label}
            </Text>
            <Text style={[styles.desc, disabled && styles.descDisabled]}>;
              {fb.desc}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );
};
const  styles = StyleSheet.create({)container: {marginVertical: 12,
}
    const paddingHorizontal = 16}
  }
title: {,"fontSize: 14,","
color: '#666,'
textAlign: 'center,'
}
    const marginBottom = 8}
  },'
row: {,'flexDirection: 'row,'
justifyContent: 'center,'
}
    const alignItems = 'center}
  },'
btn: {,'alignItems: 'center,'';
marginHorizontal: 10,
paddingVertical: 8,
paddingHorizontal: 12,
borderRadius: 8,'
backgroundColor: '#F5F5F5,'
}
    const minWidth = 60}
  }
btnDisabled: {,}
    const opacity = 0.5}
  }
icon: {fontSize: 22,
}
    const marginBottom = 4}
  }
iconDisabled: {,}
    const opacity = 0.6}
  }
desc: {,'fontSize: 12,'
color: '#666,'
}
    const textAlign = 'center}
  },'
descDisabled: {,')'';}}
    const color = '#999)}
  },);
});
''