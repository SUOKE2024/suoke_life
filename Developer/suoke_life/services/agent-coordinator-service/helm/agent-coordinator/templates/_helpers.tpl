{{/*
实用助手函数
*/}}

{{/* 应用名称 */}}
{{- define "agent-coordinator.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/* 应用全名 */}}
{{- define "agent-coordinator.fullname" -}}
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

{{/* 通用标签 */}}
{{- define "agent-coordinator.labels" -}}
helm.sh/chart: {{ include "agent-coordinator.chart" . }}
{{ include "agent-coordinator.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
tier: ai
part-of: suoke-life
{{- end }}

{{/* 选择器标签 */}}
{{- define "agent-coordinator.selectorLabels" -}}
app.kubernetes.io/name: {{ include "agent-coordinator.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app: agent-coordinator
{{- end }}

{{/* Chart名称及版本 */}}
{{- define "agent-coordinator.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}