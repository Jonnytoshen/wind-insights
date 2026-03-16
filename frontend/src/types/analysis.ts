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

export interface IAnalysisParams {
  heights: number[]                // 单位：m，范围 10-300
  startYear: number
  endYear: number
  windSurface: string              // NASA POWER surface alias
  filterOutliers: boolean
  projectName: string
}

export interface IProgressInfo {
  status: 'pending' | 'running' | 'success' | 'error'
  progress: number                 // 0.0 - 1.0
  message: string
}

export interface IWeibullResult {
  k: number
  c: number
  rSquared: number
  speedBins: number[]
  observedFreq: number[]
  fittedPdf: number[]
}

export interface IWindRoseData {
  directions: string[]             // 16 方位
  speedBins: string[]              // 风速段标签
  data: number[][]                 // [方位][风速段] 频率矩阵
  dominantDirection: string
  dominantFrequency: number
}

export interface IExtremeWindResult {
  v50: number
  ciLower: number
  ciUpper: number
  iecClass: string
  annualMaxSeries: number[]
  returnPeriods: number[]
  returnWindSpeeds: number[]
}

export interface IRepresentativeYearResult {
  representativeYear: number
  meanDeviation: number
  pearsonR: number
  yearsRanking: Array<{
    year: number
    annualMeanWs: number
    deviation: number
    pearsonR: number
    score: number
  }>
}

export interface IBasicStats {
  annualMeanWs: number
  yearlyMeans: Array<{ year: number; meanWs: number }>
  monthlyMeans: number[]           // 12 个月
  hourlyMeans: number[]            // 24 小时
  speedBins: number[]
  speedFreq: number[]
  durationCurveWs: number[]
  durationCurveHours: number[]
  dataValidRate: number
  outlierRate: number
}

export interface ITurbulenceData {
  binCenters: number[]
  tiValues: number[]
  countPerBin: number[]
  iecRefA: number[]
  iecRefB: number[]
  iecRefC: number[]
}

export interface IShearResult {
  alpha: number
  alphaFit: number
  heights: number[]
  meanWsByHeight: number[]
}

export interface IWpdResult {
  annualWpd: number
  monthlyWpd: number[]
  iecWindClass: string
}

export interface IAnalysisResult {
  taskId: string
  location: ILocation
  params: IAnalysisParams
  summary: {
    annualMeanWs: number
    annualWpd: number
    dominantDirection: string
    weibullK: number
    weibullC: number
    dataValidRate: number
  }
  basicStats: Record<string, IBasicStats>        // key: `${height}m`
  windRose: Record<string, IWindRoseData>
  weibull: Record<string, IWeibullResult>
  wpd: Record<string, IWpdResult>
  shear: IShearResult
  turbulence: Record<string, ITurbulenceData>
  extremeWind: Record<string, IExtremeWindResult>
  representativeYear: Record<string, IRepresentativeYearResult>
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
  confidentiality: '内部' | '秘密' | '机密' | '公开'
}

export interface IStartAnalysisResponse {
  taskId: string
  estimatedSeconds: number
}
