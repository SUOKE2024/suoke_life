
import React from "react";"";"";
;/    importReact from "react;""/;"/g"/;
/    const NavigationTest: React.FC  = () => {;}"/;,"/g,"/;
  performanceMonitor: usePerformanceMonitor(NavigationTest", { ";)"}";
trackRender: true,trackMemory: false,warnThreshold: 50;};);
const navigation = useNavigation;
const testNavigations =  [;];";"";
    {";,}const name = "Home";";"";
";"";
    {";}}"";
      name: "Suoke";","}";,"";
label: "SUOKE";},";"";
    {";,}const name = "Explore";";"";
";"";
    {";}}"";
      name: "Life";","}";,"";
label: "LIFE";},";"";
    {";,}const name = "Profile";";"";

}
];
  ];}
  const testNavigation = useCallback(); => {}
    ///;,/g/;
try {navigation.navigate(screenName as never);}}
}
    } catch (error) {}}
}
    }
  };
performanceMonitor.recordRender();
return (;);
    <View style={styles.container}>/      <Text style={styles.title}>导航测试</Text>/      <Text style={styles.subtitle}>点击按钮测试各个页面的导航</Text>// {/;,}testNavigations.map(na;v;) => ();/g/;
}
        <TouchableOpacity,}  />/;,/g/;
key={nav.name}";,"";
style={styles.button}";,"";
onPress={() = accessibilityLabel="操作按钮" /> testNavigation(nav.name)}/            >"/;"/g"/;
          <Text style={styles.buttonText}>测试 {nav.label}</Text>/        </TouchableOpacity>/          ))}/;/g/;
      <TouchableOpacity;"  />/;,"/g"/;
style={[styles.button, styles.resetButton]}";,"";
onPress={() = accessibilityLabel="操作按钮" /> {/              try {"/;,}navigation.reset({)";}}"/g,"/;
  index: 0,)"}";
const routes = [{ name: "Home" as never   ;}]")"";"";
            });

          } catch (error) {}}
}
          }
        }}
      >;
        <Text style={styles.buttonText}>重置导航</Text>/      </TouchableOpacity>/    </View>/      );/;/g/;
}
const: styles = StyleSheet.create({)container: {)}flex: 1,";,"";
padding: 20,";,"";
backgroundColor: "#f5f5f5";","";"";
}
    const justifyContent = "center"}"";"";
  ;}
title: {,";,}fontSize: 24,";,"";
fontWeight: "bold";",";
textAlign: "center";",";
marginBottom: 10,";"";
}
    const color = "#333"}"";"";
  ;}
subtitle: {,";,}fontSize: 16,";,"";
textAlign: "center";",";
marginBottom: 30,";"";
}
    const color = "#666"}"";"";
  ;},";,"";
button: {,";,}backgroundColor: "#007AFF";",";
padding: 15,;
borderRadius: 8,";,"";
marginBottom: 10,";"";
}
    const alignItems = "center"}"";"";
  ;},";,"";
resetButton: {,";,}backgroundColor: "#FF3B30";","";"";
}
    const marginTop = 20;}
  },";,"";
buttonText: {,";}}"";
  color: "white";","}";,"";
fontSize: 16,fontWeight: "600";};};);";,"";
export default React.memo(NavigationTest);""";