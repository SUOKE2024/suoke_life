import React from 'react';
import { usePerformanceMonitor } from '../hooks/usePerformanceMonitor';
interface ApiResponse<T = any /> { data: T;/, success: boolean;
  message?: string,
  code?: number}
// 第三方医疗API集成服务   索克生活APP - 医疗数据API集成管理
// 医疗API提供商类型 * export type MedicalApiProvider = | "fhir"  *// FHIR标准医疗数据* *   | "epic"  * */// Epic医疗系统* *   | "cerner"  * */// Cerner医疗系统* *   | "allscripts"  * */// Allscripts医疗系统* *   | "athenahealth"  * */// athenahealth医疗系统* *   | "veracross"  * */// Veracross医疗系统* *   | "meditech"  * */// MEDITECH医疗系统* *   | "nextgen"  * */// NextGen医疗系统* *   | "eclinicalworks"  * */// eClinicalWorks医疗系统* *   | "practice_fusio;n";  * */// Practice Fusion医疗系统* * ; * *//;
// 医疗数据类型 * export interface MedicalRecord { id: string, */;
  patientId: string,
  providerId: string,
  recordType:   | "diagnosis"| "prescription"| "lab_result",
    | "vital_signs"
    | "allergy"
    | "immunization";
  data: unknown,
  timestamp: string,
  source: MedicalApiProvider,
  verified: boolean;
  metadata?:  {
    clinician?: string;
    facility?: string;
    department?: string;
    confidence?: number};
}
// 患者信息 * export interface PatientInfo { id: string, */
  name: string,
  dateOfBirth: string,
  gender: "male" | "female" | "other",
  contactInfo: {phone?: string;
    email?: string;
    address?: string};
  insuranceInfo?:  { provider: string,
    policyNumber: string;
    groupNumber?: string};
  emergencyContact?:  { name: string,
    relationship: string,
    phone: string};
}
// 医疗预约信息 * export interface MedicalAppointment { id: string, */
  patientId: string,
  providerId: string,
  clinicianId: string,
  appointmentType:   | "consultation"| "follow_up"| "procedure",
    | "lab_test"
    | "imaging";
  scheduledTime: string,
  duration: number // 分钟 *, status:   | "scheduled"| "confirmed"| "in_progress" */
    | "completed"
    | "cancelled"
    | "no_show";
  location: {facility: string,
    address: string;
    room?: string};
  notes?: string;
  telehealth?: boolean}
// 处方信息 * export interface Prescription { id: string, */;
  patientId: string,
  clinicianId: string,
  medication: {name: string;
    genericName?: string;
    dosage: string,
    frequency: string,
    duration: string,
    instructions: string}
  prescribedDate: string,
  status: "active" | "completed" | "cancelled" | "expired",
  refillsRemaining: number;
  pharmacy?:  { name: string,
    address: string,
    phone: string};
}
// 实验室结果 * export interface LabResult { id: string, */;
  patientId: string,
  testName: string,
  testCode: string,
  result: {value: string | number;
    unit?: string;
    referenceRange?: string,
    status: "normal" | "abnormal" | "critical" | "pending"};
  orderedDate: string,
  resultDate: string,
  clinicianId: string,
  labFacility: string;
  notes?: string}
// API配置 * interface ApiConfig { baseUrl: string, */
  apiKey: string,
  version: string,
  timeout: number,
  retryAttempts: number,
  rateLimit: {requests: number,
    window: number; // 毫秒 *     }; */
}
// 医疗API服务类 * class MedicalApiService { */
  private configs: Map<MedicalApiProvider, ApiConfig /> = new Map();/  private rateLimiters: Map<MedicalApiProvider, any /> = new Map();/
  constructor() {
    this.initializeConfigs();
    this.setupRateLimiters();
  }
  // /    初始化API配置  private initializeConfigs(): void {
    // FHIR标准配置 *     this.configs.set("fhir", { */
      baseUrl: process.env.FHIR_API_BASE_URL || "https:// api.fhir.org * R4", *// apiKey: process.env.FHIR_API_KEY || "",
      version: "R4",
      timeout: 30000,
      retryAttempts: 3,
      rateLimit: { requests: 100, window: 60000}
    })
    // Epic配置 *     this.configs.set("epic", { */
      baseUrl: process.env.EPIC_API_BASE_URL ||"https:// fhir.epic.com * interconnect-fhir-oauth", *// apiKey: process.env.EPIC_API_KEY || "",
      version: "R4",
      timeout: 30000,
      retryAttempts: 3,
      rateLimit: { requests: 50, window: 60000}
    })
    // Cerner配置 *     this.configs.set("cerner", { */
      baseUrl: process.env.CERNER_API_BASE_URL || "https:// fhir-open.cerner.com * r4", *// apiKey: process.env.CERNER_API_KEY || "",
      version: "R4",
      timeout: 30000,
      retryAttempts: 3,
      rateLimit: { requests: 60, window: 60000}
    });
    // 其他提供商的配置... *   } */
  // /    设置速率限制器  private setupRateLimiters();: void {
    this.configs.forEach((config, provider); => {
      this.rateLimiters.set(provider, {
        requests:  [],
        limit: config.rateLimit.requests,
        window: config.rateLimit.window,
      });
    });
  }
  // /    检查速率限制  private checkRateLimit(provider: MedicalApiProvider);: boolean  {
    const limiter = this.rateLimiters.get(provide;r;);
    if (!limiter) return t;r;u;e;
    const now = Date.now;(;);
    limiter.requests = limiter.requests.filter(
      (time: number); => now - time < limiter.window;);
    if (limiter.requests.length >= limiter.limit) {
      return fal;s;e;
    }
    limiter.requests.push(now);
    return tr;u;e
  }
  // /    通用API请求方法  private async makeApiRequest(provider: MedicalApiProvider,
    endpoint: string,
    method: "GET" | "POST" | "PUT" | "DELETE" = "GET",
    data?: unknown,
    headers?: Record<string, string>
  );: Promise<any>  {
    if (!this.checkRateLimit(provider)) {
      throw new Error(`Rate limit exceeded for provider: ${provider};`;);
    }
    const config = this.configs.get(provide;r;)
    if (!config) {
      throw new Error(`Configuration not found for provider: ${provider};`;)
    }
    const url = `${config.baseUrl}${endpoint;};`
    const requestHeaders = { Authorization: `Bearer ${config.apiKey  }`,;
      "Content-Type": "application/fhir+json",/      Accept: "application/fhir+json",/      ...header;s
    ;};
    try {
      const controller = new AbortController;(;);
      const timeoutId = setTimeout((); => controller.abort(), config.timeout)
      const response = await fetch(url, {;
  // 性能监控
  const performanceMonitor = usePerformanceMonitor('medicalApiService', {;
    trackRender: true,
    trackMemory: false,
    warnThreshold: 100, // ms ;/
  ;};);
        method,
        headers: requestHeaders,
        body: data ? JSON.stringify(data);: undefined,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      if (!response.ok)  {
        throw new Error(
          `API request failed: ${response.status} ${response.statusText};`
        ;);
      }
      return await response.js;o;n;(;)
    } catch (error) {
      console.error(`Medical API request failed for ${provider}:`, error);
      throw err;o;r;
    }
  }
  // /    获取患者信息  async getPatientInfo(provider: MedicalApiProvider,
    patientId: string;);: Promise<PatientInfo />  {
    try {
      const response = await this.makeApiRequest(;
        provider,
        `/Patient/${patientId;};`;/      ;);
      return this.transformPatientData(response, provide;r;)
    } catch (error) {
      console.error(`Failed to get patient info from ${provider}:`, error);
      throw err;o;r;
    }
  }
  // /    获取医疗记录  async getMedicalRecords(provider: MedicalApiProvider,
    patientId: string,
    recordType?: string,
    dateRange?:  { start: string, end: string}): Promise<MedicalRecord[] />  {
    try {
      let endpoint = `/Patient/${patientId};/;`/
      switch (recordType) {
        case "diagnosis":
          endpoint += "Condition";
          break
        case "prescription":
          endpoint += "MedicationRequest";
          break
        case "lab_result":
          endpoint += "Observation?category=laboratory";
          break
        case "vital_signs":
          endpoint += "Observation?category=vital-signs";
          break
        default: endpoint += "everything"}
      if (dateRange) {
        const separator = endpoint.includes("?";); ? "&" : "?"
        endpoint += `${separator}date=ge${dateRange.start}&date=le${dateRange.end}`;
      }
      const response = await this.makeApiRequest(provider, endpo;i;n;t;);
      return this.transformMedicalRecords(response, provide;r;)
    } catch (error) {
      console.error(`Failed to get medical records from ${provider}:`, error);
      throw err;o;r;
    }
  }
  // /    获取预约信息  async getAppointments(provider: MedicalApiProvider,
    patientId: string,
    status?: string;
  ): Promise<MedicalAppointment[] />  {
    try {
      let endpoint = `/Appointment?patient=${patientId;};`/      if (status) {
        endpoint += `&status=${status}`;
      }
      const response = await this.makeApiRequest(provider, endpo;i;n;t;);
      return this.transformAppointments(response, provide;r;)
    } catch (error) {
      console.error(`Failed to get appointments from ${provider}:`, error);
      throw err;o;r
    }
  }
  // /    创建预约  async createAppointment(provider: MedicalApiProvider,
    appointment: Omit<MedicalAppointment, "id" />/  );: Promise<MedicalAppointment />  {
    try {
      const fhirAppointment = this.transformToFhirAppointment(appointmen;t;)
      const response = await this.makeApiRequest(;
        provider,
        "/Appointment",/        "POST",
        fhirAppointm;e;n;t
      ;);
      return this.transformAppointments([response], provider)[0]
    } catch (error) {
      console.error(`Failed to create appointment with ${provider}:`, error);
      throw err;o;r;
    }
  }
  // /    获取处方信息  async getPrescriptions(provider: MedicalApiProvider,
    patientId: string,
    status?: string;
  ): Promise<Prescription[] />  {
    try {
      let endpoint = `/MedicationRequest?patient=${patientId;};`/      if (status) {
        endpoint += `&status=${status}`;
      }
      const response = await this.makeApiRequest(provider, endpo;i;n;t;);
      return this.transformPrescriptions(response, provide;r;)
    } catch (error) {
      console.error(`Failed to get prescriptions from ${provider}:`, error);
      throw err;o;r;
    }
  }
  // /    获取实验室结果  async getLabResults(provider: MedicalApiProvider,
    patientId: string,
    testType?: string;
  ): Promise<LabResult[] />  {
    try {
      let endpoint = `/Observation?patient=${patientId}&category=laborator;y;`/      if (testType) {
        endpoint += `&code=${testType}`;
      }
      const response = await this.makeApiRequest(provider, endpo;i;n;t;);
      return this.transformLabResults(response, provide;r;)
    } catch (error) {
      console.error(`Failed to get lab results from ${provider}:`, error);
      throw err;o;r;
    }
  }
  // /    同步多个提供商的数据  async syncMultipleProviders(providers: MedicalApiProvider[],
    patientId: string;);: Promise< {, success: MedicalApiProvider[],
    failed: { provider: MedicalApiProvider, error: string}[],
    data: { records: MedicalRecord[],
      appointments: MedicalAppointment[],
      prescriptions: Prescription[],
      labResults: LabResult[];
      };
  }> {
    const results = {;
      success:  [] as MedicalApiProvider[],
      failed:  [] as {, provider: MedicalApiProvid;e;r, error: string}[],
      data: {
        records:  [] as MedicalRecord[],
        appointments:  [] as MedicalAppointment[],
        prescriptions:  [] as Prescription[],
        labResults:  [] as LabResult[]
      }
    };
    await Promise.allSettled(
      providers.map(async (provide;r;); => {
        try {
          const [records, appointments, prescriptions, labResults] = await Promise.all([;
              this.getMedicalRecords(provider, patientId),
              this.getAppointments(provider, patientId),
              this.getPrescriptions(provider, patientId),
              this.getLabResults(provider, patientI;d;);];);
          results.data.records.push(...records);
          results.data.appointments.push(...appointments);
          results.data.prescriptions.push(...prescriptions);
          results.data.labResults.push(...labResults);
          results.success.push(provider)
        } catch (error) {
          results.failed.push({
            provider,
            error: error instanceof Error ? error.message : "Unknown error",
          });
        }
      })
    );
    return resul;t;s;
  }
  // /    数据转换方法  private transformPatientData(data: unknown,
    provider: MedicalApiProvider;);: PatientInfo  {
    // 根据不同提供商的数据格式进行转换* *  这里实现FHIR标准的转换逻辑 * *// return {/;
      id: data.id,
      name: data.name?.[0]?.text ;|;|`${data.name?.[0]?.given?.join(" ")} ${data.name?.[0]?.family}`,
      dateOfBirth: data.birthDate,
      gender: data.gender,
      contactInfo: {
        phone: data.telecom?.find((t: unknown) => t.system === "phone")?.value,
        email: data.telecom?.find((t: unknown) => t.system === "email")?.value,
        address: data.address?.[0]?.text
      }
    };
  }
  private transformMedicalRecords(data: unknown,
    provider: MedicalApiProvider;);: MedicalRecord[]  {
    if (!data.entry) return ;[;];
    return data.entry.map((entry: unknow;n;) => ({,
      id: entry.resource.id,
      patientId: entry.resource.subject?.reference?.split("/")[1] || "",/      providerId: provider,
      recordType: this.determineRecordType(entry.resource.resourceType),
      data: entry.resource,
      timestamp: entry.resource.recordedDate ||;entry.resource.effectiveDateTime ||
        new Date().toISOString(),
      source: provider,
      verified: true,
      metadata: {
        clinician: entry.resource.recorder?.display,
        facility: entry.resource.encounter?.display,
      }
    }));
  }
  private transformAppointments(data: unknown,
    provider: MedicalApiProvider;);: MedicalAppointment[]  {
    if (!data.entry) return ;[;];
    return data.entry.map((entry: unknow;n;); => ({,
      id: entry.resource.id,
      patientId: entry.resource.participant;?.find((p: unknown) => p.actor?.reference?.includes("Patient"))
          ?.actor?.reference?.split("/")[1] || "",/      providerId: provider,
      clinicianId: entry.resource.participant;?.find((p: unknown) => p.actor?.reference?.includes("Practitioner"))
          ?.actor?.reference?.split("/")[1] || "",/      appointmentType: this.mapAppointmentType(
        entry.resource.serviceType?.[0]?.text),
      scheduledTime: entry.resource.start,
      duration: entry.resource.minutesDuration || 30,
      status: entry.resource.status,
      location: {
        facility: entry.resource.participant?.find((p: unknown) =>;
            p.actor?.reference?.includes("Location")
          )?.actor?.display || "",
        address: "",
      },
      notes: entry.resource.comment,
      telehealth: entry.resource.serviceType?.[0]?.text;?.toLowerCase()
        .includes("telehealth");
    }));
  }
  private transformPrescriptions(data: unknown,
    provider: MedicalApiProvider;);: Prescription[]  {
    if (!data.entry) return ;[;];
    return data.entry.map((entry: unknow;n;) => ({,
      id: entry.resource.id,
      patientId: entry.resource.subject?.reference?.split("/")[1] || "",/      clinicianId: entry.resource.requester?.reference?.split("/")[1] || "",/      medication: {
        name: entry.resource.medicationCodeableConcept?.text ||entry.resource.medicationReference?.display ||,
          "",
        dosage: entry.resource.dosageInstruction?.[0]?.text || "",
        frequency: entry.resource.dosageInstruction?.[0]?.timing?.repeat?.frequency?.toString() ||
          "",
        duration: entry.resource.dosageInstruction?.[0]?.timing?.repeat?.duration?.toString() ||
          "",
        instructions: entry.resource.dosageInstruction?.[0]?.patientInstruction || ""
      },
      prescribedDate: entry.resource.authoredOn,
      status: entry.resource.status,
      refillsRemaining: entry.resource.dispenseRequest?.numberOfRepeatsAllowed || 0;
    }));
  }
  private transformLabResults(data: unknown,
    provider: MedicalApiProvider;);: LabResult[]  {
    if (!data.entry) return ;[;];
    return data.entry.map((entry: unknow;n;) => ({,
      id: entry.resource.id,
      patientId: entry.resource.subject?.reference?.split("/")[1] || "",/      testName: entry.resource.code?.text || "",
      testCode: entry.resource.code?.coding?.[0]?.code || "",
      result: {
        value: entry.resource.valueQuantity?.value ||entry.resource.valueString ||,
          "",
        unit: entry.resource.valueQuantity?.unit,
        referenceRange: entry.resource.referenceRange?.[0]?.text,
        status: entry.resource.interpretation?.[0]?.coding?.[0]?.code === "N"? "normal"
            : "abnormal"
      },
      orderedDate: entry.resource.issued,
      resultDate: entry.resource.effectiveDateTime,
      clinicianId: entry.resource.performer?.[0]?.reference?.split("/")[1] || "",/      labFacility: entry.resource.performer?.[0]?.display || ""
    }))
  }
  private transformToFhirAppointment(appointment: Omit<MedicalAppointment, "id" />/  ): unknown  {
    return {
      resourceType: "Appointment",
      status: appointment.status,
      serviceType;: ;[;{, text: appointment.appointmentType}
      ],
      start: appointment.scheduledTime,
      end: new Date(,
        new Date(appointment.scheduledTime).getTime(); +
          appointment.duration * 60000
      ).toISOString(),
      minutesDuration: appointment.duration,
      participant: [{, actor: {
            reference: `Patient/${appointment.patientId  }`,/          },
          required: "required",
          status: "accepted",
        },
        { actor: {
            reference: `Practitioner/${appointment.clinicianId  }`,/          },
          required: "required",
          status: "accepted",
        }
      ],
      comment: appointment.notes,
    };
  }
  private determineRecordType(resourceType: string;): MedicalRecord["recordType"]  {
    switch (resourceType) {
      case "Condition":
        return "diagnosi;s";
      case "MedicationRequest":
        return "prescriptio;n";
      case "Observation":
        return "lab_resul;t";
      case "AllergyIntolerance":
        return "allerg;y";
      case "Immunization":
        return "immunizatio;n";
      default: return "diagnosi;s";
    }
  }
  private mapAppointmentType(serviceType: string;);: MedicalAppointment["appointmentType"]  {
    if (!serviceType) return "consultat;i;o;n";
    const type = serviceType.toLowerCase;(;);
    if (type.includes("follow")) return "follow_u;p;"
    if (type.includes("procedure")) return "procedur;e;"
    if (type.includes("lab")) return "lab_tes;t;"
    if (type.includes("imaging") || type.includes("scan")) return "imagin;g;"
    return "consultatio;n;";
  }
}
// 导出服务实例 * export const medicalApiService = new MedicalApiService;(;); */;
export default medicalApiService;