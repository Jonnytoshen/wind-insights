import axios from 'axios'
import type { IAnalysisParams, ILocation, IStartAnalysisResponse, IAnalysisResult, IReportConfig } from '@/types/analysis'

// Recursively convert snake_case keys to camelCase so the frontend can use
// TypeScript-conventional field names without a dedicated mapping layer.
function toCamel(s: string): string {
  return s.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
}

function camelizeKeys(obj: unknown): unknown {
  if (Array.isArray(obj)) return obj.map(camelizeKeys)
  if (obj !== null && typeof obj === 'object') {
    return Object.fromEntries(
      Object.entries(obj as Record<string, unknown>).map(([k, v]) => [toCamel(k), camelizeKeys(v)])
    )
  }
  return obj
}

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Response interceptor: camelize keys + unified error handling
apiClient.interceptors.response.use(
  (response) => {
    if (response.config.responseType !== 'blob') {
      response.data = camelizeKeys(response.data)
    }
    return response
  },
  (error) => {
    const message = error.response?.data?.detail ?? error.message ?? '请求失败，请稍后重试'
    console.error('[API Error]', message, error.response?.status)
    return Promise.reject(new Error(message))
  }
)

export async function startAnalysis(
  location: ILocation,
  params: IAnalysisParams
): Promise<IStartAnalysisResponse> {
  const payload = {
    lat: location.gridLat,
    lon: location.gridLng,
    heights: params.heights,
    start_year: params.startYear,
    end_year: params.endYear,
    wind_surface: params.windSurface,
    filter_outliers: params.filterOutliers,
    project_name: params.projectName,
  }
  const { data } = await apiClient.post<IStartAnalysisResponse>('/analysis/start', payload)
  return data
}

export async function getAnalysisResult(taskId: string): Promise<IAnalysisResult> {
  const { data } = await apiClient.get<IAnalysisResult>(`/analysis/${taskId}/result`)
  return data
}

export async function generateReport(
  taskId: string,
  chartImages: Record<string, string>,
  reportConfig: IReportConfig
): Promise<Blob> {
  const payload = {
    task_id: taskId,
    chart_images: chartImages,
    project_name: reportConfig.projectName,
    project_address: reportConfig.projectAddress,
    report_date: reportConfig.reportDate,
    organization: reportConfig.organization,
    confidentiality: reportConfig.confidentiality,
  }
  const { data } = await apiClient.post<Blob>('/report/generate', payload, {
    responseType: 'blob',
    timeout: 60000,
  })
  return data
}

export async function exportCsv(taskId: string): Promise<Blob> {
  const { data } = await apiClient.get<Blob>(`/analysis/${taskId}/export/csv`, {
    responseType: 'blob',
    timeout: 60000,
  })
  return data
}

export default apiClient
