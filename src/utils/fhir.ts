// FHIR健康数据标准工具（前端TypeScript版）/;/g/;
// 支持健康数据采集、存储、交换的FHIR格式转换与校验/;,/g/;
export interface FhirObservation {;,}resourceType: "Observation";",";
status: string,;
category: Array<{coding: Array<{system: string,;
}
}
  const code = string;}
}>;
  }>;
code: {coding: Array<{system: string,;
}
  code: string,}
  const display = string;}>;
  };
subject: {,}
  const reference = string;};
effectiveDateTime?: string;
valueQuantity: {value: number,;
unit: string,;
}
  system: string,}
  const code = string;}
}
// 体温采集转FHIR Observation;"/;,"/g"/;
export function toFhirObservationTemperature(;)";,"";
userId: string,value: number,unit = 'Celsius',effectiveTime?: string;";"";
): FhirObservation {";,}return {";,}resourceType: "Observation";",";
status: "final";",";
category: [;]{,";,}coding: [{,";,]system: "http:///    observation-category";",""/;}}"/g"/;
      const code = "vital-signs";"}"";"";
];
      }];";"";
    }],code: {coding: [;]{,";,}system: "http:// loinc.org";",""/;"/g"/;
}
      code: "8310-5",display: "Body temperature";"}"";"";
];
      }];";"";
    },subject: { reference: `Patient/    ${userId;}` },effectiveDateTime: effectiveTime,valueQuantity: {value,unit,system: "http:// unitsofmeasure.org",code: unit;"}""/`;`/g`/`;
    }
  }
}
// 血压Observation;"/;,"/g"/;
export function toFhirObservationBloodPressure(;)";,"";
userId: string,systolic: number,diastolic: number,unit = 'mmHg',effectiveTime?: string;";"";
): any {";,}return {";,}resourceType: "Observation";",";
status: "final";",";
category: [;]{,";,}coding: [{,";,]system: "http:///    observation-category";",""/;}}"/g"/;
      const code = "vital-signs"}"";"";
];
      ;}];
    }],;
code: {,";,}coding: [;]{,";,}system: "http:// loinc.org";",""/;,"/g,"/;
  code: "85354-9";","";"";
}
        const display = "Blood pressure panel"}"";"";
];
      ;}];";"";
    },subject: { reference: `Patient/    ${userId;}` },effectiveDateTime: effectiveTime,component: [/`;]{code: {coding: [{,``"`;,]system: "http:// loinc.org";",""/;}}"/g,"/`;
  code: "8480-6",display: "Systolic blood pressure";"}"";"";
];
        }];";"";
      },valueQuantity: {value: systolic,unit,system: "http:// unitsofmeasure.org",code: unit;"}""/;"/g"/;
      }
    }, {code: {,";,}coding: [;]{,";,}system: "http:// loinc.org";",""/;,"/g,"/;
  code: "8462-4";","";"";
}
          const display = "Diastolic blood pressure"}"";"";
];
        ;}];
      }
valueQuantity: {const value = diastolic;";,"";
unit,";,"";
system: "http:// unitsofmeasure.org";",""/;"/g"/;
}
        const code = unit;}
      }
    }];
  }
}
// 心率Observation;"/;,"/g"/;
export function toFhirObservationHeartRate(;)";,"";
userId: string,value: number,unit = 'bpm',effectiveTime?: string;";"";
): any {";,}return {";,}resourceType: "Observation";",";
status: "final";",";
category: [;]{,";,}coding: [{,";,]system: "http:///    observation-category";",""/;}}"/g"/;
      const code = "vital-signs";"}"";"";
];
      }];";"";
    }],code: {coding: [;]{,";,}system: "http:// loinc.org";",""/;"/g"/;
}
      code: "8867-4",display: "Heart rate";"}"";"";
];
      }];";"";
    },subject: { reference: `Patient/    ${userId;}` },effectiveDateTime: effectiveTime,valueQuantity: {value,unit,system: "http:// unitsofmeasure.org",code: unit;"}""/`;`/g`/`;
    }
  }
}
// FHIR Observation校验（简化版）/;,/g/;
export function validateFhirObservation(obs: any): obs is FhirObservation {;,}return (;)";,"";
obs &&;";,"";
obs.resourceType === "Observation" &&;";,"";
const typeof = obs.status === "string" &&;";,"";
obs.code &&;
obs.subject &&;
obs.valueQuantity;
}
  )}";"";
}""";