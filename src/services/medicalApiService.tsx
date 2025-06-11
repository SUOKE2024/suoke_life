react;
interface ApiResponse<T = any  /> {/data: T;/    , success: boolean;
}
  message?: string}
  code?: number}
// 第三方医疗API集成服务   索克生活APP - 医疗数据API集成管理"/;"/g"/;
| "epic"  *  | "cerner"  *  | "allscripts"  *  | "athenahealth"  *  | "veracross"  *  | "meditech"  *  | "nextgen"  *  | "eclinicalworks"  *  | "practice_fusio;
n";  * / Practice Fusion医疗系统* ///     
// 医疗数据类型 * export interface MedicalRecord {;
/id: string,,/g,/;
  patientId: string,","
providerId: string,","
const recordType = | "diagnosis"| "prescription"| "lab_result;
    | "vital_signs;
    | "allergy;
    | "immunization,"";
data: unknown,
timestamp: string,
source: MedicalApiProvider,
const verified = boolean;
metadata?: {clinician?: stringfacility?: string;
department?: string;
}
    confidence?: number}
};
}
// 患者信息 * export interface PatientInfo {";
/id: string,","/g,"/;
  name: string,","
dateOfBirth: string,gender: "male" | "female" | "other",contactInfo: {phone?: string;"email?: string;"";
}
    address?: string}
};
insuranceInfo?:  {provider: string,}
    const policyNumber = string}
    groupNumber?: string};
emergencyContact?:  {name: string,}
    relationship: string,}
    const phone = string;};
}
// 医疗预约信息 * export interface MedicalAppointment {;
/id: string,,/g,/;
  patientId: string,"
providerId: string,","
clinicianId: string,","
const appointmentType = | "consultation"| "follow_up"| "procedure;
    | "lab_test;
    | "imaging
scheduledTime: string,","
const duration = number //;"/;"/g"/;
    | "completed;
    | "cancelled;
    | "no_show,"";
location: {facility: string,address: string
}
    room?: string}
};
notes?: string;
telehealth?: boolean}
// 处方信息 * export interface Prescription {;
/id: string,,/g,/;
  patientId: string,clinicianId: string,medication: {name: stringgenericName?: string;,
  dosage: string,
frequency: string,
duration: string,
}
  const instructions = string}
}","
prescribedDate: string,","
status: "active" | "completed" | "cancelled" | "expired,";
const refillsRemaining = number;
pharmacy?:  {name: string,}
    address: string,}
    const phone = string;};
}
// 实验室结果 * export interface LabResult {;
/id: string,,/g,/;
  patientId: string,"
testName: string,testCode: string,result: {value: string | numberunit?: string;","
referenceRange?: string;";
}
    const status = "normal" | "abnormal" | "critical" | "pending};
};
orderedDate: string,
resultDate: string,
clinicianId: string,
const labFacility = string;
notes?: string}
// API配置 * interface ApiConfig {
/baseUrl: string,,/g,/;
  apiKey: string,
version: string,
timeout: number,
retryAttempts: number,
rateLimit: {requests: number,
}
  const window = number }
}
}
//
private configs: Map<MedicalApiProvider, ApiConfig  /> = new Map()/  private rateLimiters: Map<MedicalApiProvider, any  /> = new Map();/
constructor() {this.initializeConfigs()}
    this.setupRateLimiters()}
  }
  // 初始化API配置  private initializeConfigs(): void {/;}","/g"/;
this.configs.set("fhir", {",)baseUrl: process.env.FHIR_API_BASE_URL || "https:///     apiKey: process.env.FHIR_API_KEY || ,""/version: "R4,"","/g,"/;
  timeout: 30000,);
}
      retryAttempts: 3,)}
      rateLimit: { requests: 100, window: 60000;})
    });","
this.configs.set("epic", {)"baseUrl: process.env.EPIC_API_BASE_URL ||"https:///     apiKey: process.env.EPIC_API_KEY || ,""/,"/g,"/;
  version: "R4,";
timeout: 30000,);
}
      retryAttempts: 3,)}
      rateLimit: { requests: 50, window: 60000;})
    });","
this.configs.set("cerner", {)"baseUrl: process.env.CERNER_API_BASE_URL || "https:///     apiKey: process.env.CERNER_API_KEY || ,""/,"/g,"/;
  version: "R4,";
timeout: 30000,);
}
      retryAttempts: 3,)}
      rateLimit: { requests: 60, window: 60000;});
    });
    }
  // 设置速率限制器  private setupRateLimiters(): void {}
this.configs.forEach(config, provider); => {}
      this.rateLimiters.set(provider, {))requests: [],);
}
        limit: config.rateLimit.requests;),}
        const window = config.rateLimit.window;});
    });
  }
  // 检查速率限制  private checkRateLimit(provider: MedicalApiProvider): boolean  {/const limiter = this.rateLimiters.get(provide;r;),/g/;
if (!limiter) return t;r;u;e;
const now = Date.now;
limiter.requests = limiter.requests.filter(time: number); => now - time < limiter.window;);
if (limiter.requests.length >= limiter.limit) {}
      return fal;s;e}
    }
    limiter.requests.push(now);
return tr;u;e;
  }
  // 通用API请求方法  private async makeApiRequest(provider: MedicalApiProvider,)"/,"/g,"/;
  endpoint: string,","
method: "GET" | "POST" | "PUT" | "DELETE" = "GET,"";
data?: unknown;
headers?: Record<string; string>;
  ): Promise<any>  {}
    if (!this.checkRateLimit(provider)) {}
      const throw = new Error(`Rate limit exceeded for provider: ${provider;`;);````;```;
    }
    const config = this.configs.get(provide;r;);
if (!config) {}
      const throw = new Error(`Configuration not found for provider: ${provider;`;);````;```;
    }","
const url = `${config.baseUrl}${endpoint;};`;``"`,```;
requestHeaders: { Authorization: `Bearer ${config.apiKey  ;}`,"Content-Type": "application/fhir+json",/      Accept: "application/fhir+json",/          ...header;s;};"/`,`/g`/`;
try {const controller = new AbortControllertimeoutId: setTimeout(); => controller.abort(), config.timeout);","
const: response = await fetch(url, {// 性能监控)"/const: performanceMonitor = usePerformanceMonitor(medicalApiService", {")"trackRender: true,,"/g,"/;
  trackMemory: false,
}
    warnThreshold: 100, ///}
  ;};);
method,
headers: requestHeaders,
body: data ? JSON.stringify(data);: undefined,
const signal = controller.signal;});
clearTimeout(timeoutId);
if (!response.ok)  {}
        const throw = new Error(;)}
          `API request failed: ${response.status;} ${response.statusText};`````;```;
        ;);
      }
      return await response.js;o;n;(;);
    } catch (error) {}
      const throw = error}
    }
  }
  // 获取患者信息  async getPatientInfo(provider: MedicalApiProvider,)
const patientId = string);: Promise<PatientInfo /    >  {/try {const response = await this.makeApiRequest(;);}}/g/;
        provider,}
        `/Patient/    ${patientId;};`);```/`,`/g`/`;
return this.transformPatientData(response, provide;r;);
    } catch (error) {}
      const throw = error}
    }
  }
  // 获取医疗记录  async getMedicalRecords(provider: MedicalApiProvider,)
const patientId = string;
recordType?: string;
dateRange?: { start: string; end: string;}): Promise<MedicalRecord[] /    >  {/;}}/g/;
    try {}","
let endpoint = `/Patient/${patientId} ;``"/`,`/g`/`;
switch (recordType) {case "diagnosis": endpoint += "Conditionbreak;","
case "prescription": ","
endpoint += "MedicationRequest,"
break;","
case "lab_result": ","
endpoint += "Observation?category=laboratory,"
break;","
case "vital_signs": ","
endpoint += "Observation?category=vital-signs;"";
}
          break;"}
default: endpoint += "everything";}","
if (dateRange) {";}}
        const separator = endpoint.includes("?";); ? "&" : "?}";
endpoint += `${separator}date=ge${dateRange.start}&date=le${dateRange.end}`;````;```;
      }
      response: await this.makeApiRequest(provider, endpo;i;n;t;);
return this.transformMedicalRecords(response, provide;r;);
    } catch (error) {}
      const throw = error}
    }
  }
  // 获取预约信息  async getAppointments(provider: MedicalApiProvider,)
const patientId = string;
status?: string;
  ): Promise<MedicalAppointment[] /    >  {/;}}/g/;
    try {}
      let endpoint = `/Appointment?patient=${patientId;};`/          if (status) {endpoint += `&status=${status}`;```/`;`/g`/`;
      }
      response: await this.makeApiRequest(provider, endpo;i;n;t;);
return this.transformAppointments(response, provide;r;);
    } catch (error) {}
      const throw = err;o;r}
    }
  }
  // 创建预约  async createAppointment(provider: MedicalApiProvider,)"/,"/g,"/;
  appointment: Omit<MedicalAppointment, "id"  />/  ): Promise<MedicalAppointment /    >  {/;}","/g"/;
try {const fhirAppointment = this.transformToFhirAppointment(appointmen;t;)const response = await this.makeApiRequest(;)","
provider,/Appointment",/            "POST","
fhirAppointm;e;n;t;);
}
      return this.transformAppointments([response], provider)[0]}
    } catch (error) {throw error}
    }
  }
  // 获取处方信息  async getPrescriptions(provider: MedicalApiProvider,)
const patientId = string;
status?: string;
  ): Promise<Prescription[] /    >  {/;}}/g/;
    try {}
      let endpoint = `/MedicationRequest?patient=${patientId;};`/          if (status) {endpoint += `&status=${status}`;```/`;`/g`/`;
      }
      response: await this.makeApiRequest(provider, endpo;i;n;t;);
return this.transformPrescriptions(response, provide;r;);
    } catch (error) {}
      const throw = error}
    }
  }
  // 获取实验室结果  async getLabResults(provider: MedicalApiProvider,)
const patientId = string;
testType?: string;
  ): Promise<LabResult[] /    >  {/;}}/g/;
    try {}
      let endpoint = `/Observation?patient=${patientId}&category=laborator;y;`/          if (testType) {endpoint += `&code=${testType}`;```/`;`/g`/`;
      }
      response: await this.makeApiRequest(provider, endpo;i;n;t;);
return this.transformLabResults(response, provide;r;);
    } catch (error) {}
      const throw = error}
    }
  }
  // 同步多个提供商的数据  async syncMultipleProviders(providers: MedicalApiProvider[],)/,/g,/;
  patientId: string);: Promise< { success: MedicalApiProvider[],}
    failed: { provider: MedicalApiProvider, error: string;}[],
data: {records: MedicalRecord[]}appointments: MedicalAppointment[],
prescriptions: Prescription[],
}
      const labResults = LabResult[]}
      };
  }> {}
    const: results = {success:  [] as MedicalApiProvider[],}
      failed: [] as { provider: MedicalApiProvid;e;r, error: string;}[],
data: {records: [] as MedicalRecord[],
appointments: [] as MedicalAppointment[],
prescriptions: [] as Prescription[],
}
        const labResults = [] as LabResult[]}
      }
    };
const await = Promise.allSettled();
providers.map(async (provide;r;); => {});
try {const [records, appointments, prescriptions, labResults] = await Promise.all([;);)]this.getMedicalRecords(provider, patientId)}this.getAppointments(provider, patientId),
this.getPrescriptions(provider, patientId)];
this.getLabResults(provider, patientI;d;);];);
results.data.records.push(...records);
results.data.appointments.push(...appointments);
results.data.prescriptions.push(...prescriptions);
results.data.labResults.push(...labResults);
}
          results.success.push(provider)}
        } catch (error) {results.failed.push({)";}}
            provider,)"}
const error = error instanceof Error ? error.message : "Unknown error";});";
        }
      });
    );
return resul;t;s;
  }
  // 数据转换方法  private transformPatientData(data: unknown,)"
const provider = MedicalApiProvider);: PatientInfo  {";}}
    这里实现FHIR标准的转换逻辑 * / return {/;"}""/,"/g,"/;
  id: data.id,name: data.name?.[0]?.text ;|;|`${data.name?.[0]?.given?.join(" ")} ${data.name?.[0]?.family}`,````,```;
dateOfBirth: data.birthDate,"
gender: data.gender,","
contactInfo: {,"phone: data.telecom?.find(t: unknown) => t.system === "phone")?.value;",
email: data.telecom?.find(t: unknown) => t.system === "email")?.value;",
}
        const address = data.address?.[0]?.text}
      }
    };
  }
  private transformMedicalRecords(data: unknown,);
const provider = MedicalApiProvider;);: MedicalRecord[]  {if (!data.entry) return ;[;]return data.entry.map(entry: unknow;n;) => ({),"id: entry.resource.id,","
patientId: entry.resource.subject?.reference?.split("/")[1] || ",/          providerId: provider,""/,"/g,"/;
  recordType: this.determineRecordType(entry.resource.resourceType),
data: entry.resource,
const timestamp = entry.resource.recordedDate ||;entry.resource.effectiveDateTime ||;
new: Date().toISOString(),
source: provider,
verified: true,
metadata: {,}
  clinician: entry.resource.recorder?.display,}
        const facility = entry.resource.encounter?.display}
    }));
  }
  private transformAppointments(data: unknown,);
const provider = MedicalApiProvider;);: MedicalAppointment[]  {if (!data.entry) return ;[;]return data.entry.map(entry: unknow;n;); => ({ ),"id: entry.resource.id,","
patientId: entry.resource.participant;?.find(p: unknown) => p.actor?.reference?.includes("Patient"))
          ?.actor?.reference?.split("/")[1] || ",/          providerId: provider,""/,"/g,"/;
  clinicianId: entry.resource.participant;?.find(p: unknown) => p.actor?.reference?.includes("Practitioner"))
          ?.actor?.reference?.split("/")[1] || ",/          appointmentType: this.mapAppointmentType(")"
entry.resource.serviceType?.[0]?.text);
scheduledTime: entry.resource.start,
duration: entry.resource.minutesDuration || 30,
status: entry.resource.status,"
location: {,"facility: entry.resource.participant?.find(p: unknown) =>;","
p.actor?.reference?.includes("Location");
 })?.actor?.display || ","}","
address: ";},",","
notes: entry.resource.comment,","
const telehealth = entry.resource.serviceType?.[0]?.text;?.toLowerCase();
        .includes("telehealth");";
    }));
  }
  private transformPrescriptions(data: unknown,);
const provider = MedicalApiProvider;);: Prescription[]  {if (!data.entry) return ;[;]return data.entry.map(entry: unknow;n;) => ({),"id: entry.resource.id,","
patientId: entry.resource.subject?.reference?.split("/")[1] || ",/      clinicianId: entry.resource.requester?.reference?.split("/")[1] || ",/          medication: {,"/const name = entry.resource.medicationCodeableConcept?.text ||entry.resource.medicationReference?.display ||;/g"/;
          ",
dosage: entry.resource.dosageInstruction?.[0]?.text || ",
const frequency = entry.resource.dosageInstruction?.[0]?.timing?.repeat?.frequency?.toString() ||;";
const duration = entry.resource.dosageInstruction?.[0]?.timing?.repeat?.duration?.toString() ||,
}
        const instructions = entry.resource.dosageInstruction?.[0]?.patientInstruction || "};
      }
prescribedDate: entry.resource.authoredOn,
status: entry.resource.status,
const refillsRemaining = entry.resource.dispenseRequest?.numberOfRepeatsAllowed || 0;
    }));
  }
  private transformLabResults(data: unknown,);
const provider = MedicalApiProvider;);: LabResult[]  {if (!data.entry) return ;[;]return data.entry.map(entry: unknow;n;) => ({),"id: entry.resource.id,","
patientId: entry.resource.subject?.reference?.split("/")[1] || ",/      testName: entry.resource.code?.text || ,""/,"/g,"/;
  testCode: entry.resource.code?.coding?.[0]?.code || ,
result: {,"const value = entry.resource.valueQuantity?.value ||entry.resource.valueString ||;
unit: entry.resource.valueQuantity?.unit,","
referenceRange: entry.resource.referenceRange?.[0]?.text,","
status: entry.resource.interpretation?.[0]?.coding?.[0]?.code === "N"? "normal;
}
            : "abnormal"};
      }
orderedDate: entry.resource.issued,","
resultDate: entry.resource.effectiveDateTime,","
clinicianId: entry.resource.performer?.[0]?.reference?.split("/")[1] || ",/      labFacility: entry.resource.performer?.[0]?.display || "
    ;}))
  }","
private transformToFhirAppointment(appointment: Omit<MedicalAppointment, "id"  />/      ): unknown  {/;}","/g"/;
return {";}}
      resourceType: "Appointment,"}";
status: appointment.status,serviceType;: ;[;];{ text: appointment.appointmentType}
];
      ],
start: appointment.scheduledTime,
end: new Date(,);
const new = Date(appointment.scheduledTime).getTime(); +;
appointment.duration * 60000;
      ).toISOString(),
minutesDuration: appointment.duration,"
participant: [;]{ actor: {,}","
reference: `Patient/${appointment.patientId  ;}`,/              },``"/`,`/g,`/`;
  required: "required,
status: "accepted";},
        { actor: {,}","
reference: `Practitioner/${appointment.clinicianId  ;}`,/              },``"/`,`/g,`/`;
  required: "required,
const status = "accepted";}";
];
      ],"
const comment = appointment.notes;};
  }","
private determineRecordType(resourceType: string;): MedicalRecord["recordType"]  {"switch (resourceType) {"case "Condition": ","
return "diagnosi;s,"
case "MedicationRequest": ","
return "prescriptio;n,"
case "Observation": ","
return "lab_resul;t,"
case "AllergyIntolerance": ","
return "allerg;y,"
case "Immunization": ","
return "immunizatio;n;"";
}
      const default = return "diagnosi;s};
    }
  }","
private mapAppointmentType(serviceType: string;);: MedicalAppointment["appointmentType"]  {"if (!serviceType) return "consultat;i;o;n,"
const type = serviceType.toLowerCase;","
if (type.includes("follow")) return "follow_u;p;
if (type.includes("procedure")) return "procedur;e;
if (type.includes("lab")) return "lab_tes;t;
if (type.includes("imaging") || type.includes("scan")) return "imagin;g;
}
    return "consultatio;n;};
  }
}
//   ;
export default medicalApiService;""
