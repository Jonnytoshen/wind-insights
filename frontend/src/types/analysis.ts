// TypeScript 类型定义 — Wind Insights 前端
// 字段名与后端 snake_case 经 camelCase 转换后对应

export interface ILocation {
  lat: number
  lng: number
  displayName?: string
  /** MERRA-2 网格对齐后的坐标 */
  gridLat: number
  gridLng: number
}

export interface IAnalysisParams {
  heights: number[]                // 单位：m，范围 10-300
  startYear: number
  endYear: number
  windSurface: string              // NASA POWER surface alias
  filterOutliers: boolean
  projectName: string
}

export interface IProgressInfo {
  taskId: string
  status: 'pending' | 'running' | 'success' | 'error'
  progress: number                 // 0–100
  message: string
  currentStep: string
}

// ---- Per-height analysis types ----

export interface IHistogramData {
  bins: number[]
  frequencies: number[]
}

export interface IWeibullResult {
  k: number
  c: number
  histogram: IHistogramData
  fittedPdf: number[]
}

export interface IWindRoseData {
  directions: string[]             // 16 方位
  frequency: number[]              // per-direction frequency (%)
  speedBinFreqs: number[][]        // [speed_bin][direction] frequency (%)
}

export interface IExtremeWindResult {
  v50: number
  v100: number
  sampleYears: number
  annualMaxYears: number[]
  annualMaxValues: number[]
  error?: string
}

export interface IRepresentativeYearResult {
  representativeYear: number
  biasFromLongTerm: number
  longTermMonthlyMean: (number | null)[]
  repYearMonthlyMean: (number | null)[]
}

export interface IBasicStats {
  annualMeanWs: number
  dataValidRate: number
  outlierCount: number
  monthlyMeanTimestamps: string[]
  monthlyMeanValues: number[]
  dominantDirection: string
}

export interface ITurbulenceData {
  annualMeanTi: number
  ti15: number | null
  windSpeedBins: number[]
  tiMeanByBin: number[]
  tiStdByBin: number[]
}

export interface IShearResult {
  alpha: number
  r2: number
  heights: number[]
  meanSpeeds: number[]
  fittedSpeeds: number[]
}

export interface IWpdResult {
  annualWpd: number
  monthlyWpd: number[]
}

// ---- Top-level analysis result ----

export interface IAnalysisResult {
  taskId: string
  analysisHeights: number[]
  location: {
    lat: number
    lng: number
    gridLat: number
    gridLng: number
  }
  params: {
    startYear: number
    endYear: number
    windSurface: string
    projectName: string
  }
  basicStats: Record<string, IBasicStats>
  weibullResults: Record<string, IWeibullResult>
  windRoseData: Record<string, IWindRoseData>
  extremeWindResults: Record<string, IExtremeWindResult>
  representativeYearResults: Record<string, IRepresentativeYearResult>
  turbulenceData: Record<string, ITurbulenceData>
  shearResult: IShearResult | null
  wpdResults: Record<string, IWpdResult>
}

export interface IHistoryItem {
  id: string
  lat: number
  lng: number
  gridLat: number
  gridLng: number
  projectName: string
  createdAt: string
  heights: number[]
  startYear: number
  endYear: number
  summary?: {
    meanWs: number
    wpd: number
  }
}

export interface IReportConfig {
  projectName: string
  projectAddress: string
  reportDate: string
  organization: string
  confidentiality: '内部' | '保密' | '机密' | '公开'
}

export interface IStartAnalysisResponse {
  taskId: string
  message: string
}

