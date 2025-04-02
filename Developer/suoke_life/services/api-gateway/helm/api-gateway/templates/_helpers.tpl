{{/*
Expand the name of the chart.
*/}}
{{- define "api-gateway.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "api-gateway.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "api-gateway.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "api-gateway.labels" -}}
helm.sh/chart: {{ include "api-gateway.chart" . }}
{{ include "api-gateway.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: suoke-platform
service-type: edge
{{- with .Values.commonLabels }}
{{- toYaml . | nindent 0 }}
{{- end }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "api-gateway.selectorLabels" -}}
app.kubernetes.io/name: {{ include "api-gateway.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: api-gateway
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "api-gateway.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "api-gateway.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Helper function to get environment variable from Value or ValueFrom
*/}}
{{- define "api-gateway.getEnv" -}}
{{- $envName := index . 0 -}}
{{- $envValues := index . 1 -}}
{{- range $envValues }}
{{- if eq .name $envName -}}
{{- if .value -}}
{{- .value | quote -}}
{{- else if .valueFrom -}}
{{- .valueFrom | toYaml -}}
{{- end -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Helper function to check if a env var is required
*/}}
{{- define "api-gateway.mustHas" -}}
{{- $envName := index . 0 -}}
{{- $field := index . 1 -}}
{{- $default := "" -}}
{{- if gt (len .) 2 -}}
{{- $default = index . 2 -}}
{{- end -}}
{{- $envValues := index . 3 -}}
{{- $found := false -}}
{{- range $envValues }}
{{- if eq .name $envName -}}
{{- if eq $field "value" -}}
{{- .value | default $default | quote -}}
{{- $found = true -}}
{{- else if eq $field "valueFrom" -}}
{{- .valueFrom | toYaml -}}
{{- $found = true -}}
{{- end -}}
{{- end -}}
{{- end -}}
{{- if not $found -}}
{{- $default | quote -}}
{{- end -}}
{{- end -}}

{{/*
创建持久卷声明名称
*/}}
{{- define "api-gateway.pvcName" -}}
{{- $pvcName := index . 0 -}}
{{- $context := index . 1 -}}
{{- printf "%s-%s" (include "api-gateway.fullname" $context) $pvcName -}}
{{- end -}}

{{/*
创建配置映射名称
*/}}
{{- define "api-gateway.configMapName" -}}
{{- $configMapName := index . 0 -}}
{{- $context := index . 1 -}}
{{- printf "%s-%s" (include "api-gateway.fullname" $context) $configMapName -}}
{{- end -}}

{{/*
创建密钥名称
*/}}
{{- define "api-gateway.secretName" -}}
{{- $secretName := index . 0 -}}
{{- $context := index . 1 -}}
{{- printf "%s-%s" (include "api-gateway.fullname" $context) $secretName -}}
{{- end -}}

{{/*
Vault注解
*/}}
{{- define "api-gateway.vaultAnnotations" -}}
{{- if .Values.vault.enabled -}}
vault.hashicorp.com/agent-inject: "true"
vault.hashicorp.com/role: {{ .Values.vault.role | default (include "api-gateway.fullname" .) | quote }}
vault.hashicorp.com/agent-inject-status: "update"
{{- range $secret, $options := .Values.vault.secrets }}
vault.hashicorp.com/agent-inject-secret-{{ $secret }}: {{ $options.path | quote }}
vault.hashicorp.com/agent-inject-template-{{ $secret }}: |
  {{ tpl $options.template $ }}
{{- end }}
{{- end -}}
{{- end -}}

{{/*
检查是否启用了特性
*/}}
{{- define "api-gateway.featureEnabled" -}}
{{- $featureName := . -}}
{{- if hasKey $.Values.features $featureName -}}
{{- index $.Values.features $featureName -}}
{{- else -}}
{{- false -}}
{{- end -}}
{{- end -}}

{{/*
Pod注解
*/}}
{{- define "api-gateway.podAnnotations" -}}
{{- if .Values.podAnnotations -}}
{{ toYaml .Values.podAnnotations }}
{{- end }}
{{- if (include "api-gateway.featureEnabled" "prometheus") -}}
prometheus.io/scrape: "true"
prometheus.io/port: {{ .Values.prometheus.port | default "9090" | quote }}
prometheus.io/path: {{ .Values.prometheus.path | default "/metrics" | quote }}
{{- end }}
{{- if (include "api-gateway.featureEnabled" "istio") -}}
sidecar.istio.io/inject: "true"
{{- end }}
{{- if (include "api-gateway.featureEnabled" "linkerd") -}}
linkerd.io/inject: "enabled"
{{- end }}
{{- end -}}

{{/*
附加端口
*/}}
{{- define "api-gateway.additionalPorts" -}}
{{- if (include "api-gateway.featureEnabled" "prometheus") }}
- name: metrics
  containerPort: {{ .Values.prometheus.port | default 9090 }}
  protocol: TCP
{{- end }}
{{- if (include "api-gateway.featureEnabled" "admin") }}
- name: admin
  containerPort: {{ .Values.admin.port | default 8080 }}
  protocol: TCP
{{- end }}
{{- if (include "api-gateway.featureEnabled" "debug") }}
- name: debug
  containerPort: {{ .Values.debug.port | default 9229 }}
  protocol: TCP
{{- end }}
{{- with .Values.additionalPorts }}
{{ toYaml . }}
{{- end }}
{{- end -}}

{{/*
整合所有环境变量
*/}}
{{- define "api-gateway.allEnvVars" -}}
- name: NODE_ENV
  value: {{ .Values.environment | default "production" | quote }}
- name: PORT
  value: {{ .Values.service.port | default 3000 | quote }}
- name: HOST
  value: {{ .Values.service.host | default "0.0.0.0" | quote }}
- name: LOG_LEVEL
  value: {{ .Values.logging.level | default "info" | quote }}
- name: SERVICE_NAME
  value: {{ include "api-gateway.name" . | quote }}
- name: POD_NAME
  valueFrom:
    fieldRef:
      fieldPath: metadata.name
- name: NAMESPACE
  valueFrom:
    fieldRef:
      fieldPath: metadata.namespace
- name: POD_IP
  valueFrom:
    fieldRef:
      fieldPath: status.podIP
{{- if (include "api-gateway.featureEnabled" "prometheus") }}
- name: METRICS_PORT
  value: {{ .Values.prometheus.port | default 9090 | quote }}
- name: METRICS_PATH
  value: {{ .Values.prometheus.path | default "/metrics" | quote }}
{{- end }}
{{- if (include "api-gateway.featureEnabled" "otel") }}
- name: OTEL_ENABLED
  value: "true"
- name: OTEL_SERVICE_NAME
  value: {{ include "api-gateway.name" . | quote }}
- name: OTEL_EXPORTER_OTLP_ENDPOINT
  value: {{ .Values.otel.endpoint | default "http://otel-collector:4317" | quote }}
{{- end }}
{{- with .Values.env }}
{{ toYaml . }}
{{- end }}
{{- end -}}

{{/*
生成以服务为前缀的配置映射和密钥引用
*/}}
{{- define "api-gateway.configVolumeMount" -}}
{{- if (include "api-gateway.featureEnabled" "config") }}
- name: config
  mountPath: /app/config
  readOnly: true
{{- end }}
{{- end -}}

{{/*
生成配置卷
*/}}
{{- define "api-gateway.configVolume" -}}
{{- if (include "api-gateway.featureEnabled" "config") }}
- name: config
  configMap:
    name: {{ include "api-gateway.configMapName" (list "config" .) }}
    optional: false
{{- end }}
{{- end -}}

{{/*
生成日志卷挂载
*/}}
{{- define "api-gateway.logVolumeMount" -}}
{{- if (include "api-gateway.featureEnabled" "persistentLogs") }}
- name: logs
  mountPath: /app/logs
{{- end }}
{{- end -}}

{{/*
生成日志卷
*/}}
{{- define "api-gateway.logVolume" -}}
{{- if (include "api-gateway.featureEnabled" "persistentLogs") }}
- name: logs
  persistentVolumeClaim:
    claimName: {{ include "api-gateway.pvcName" (list "logs" .) }}
{{- end }}
{{- end -}} 