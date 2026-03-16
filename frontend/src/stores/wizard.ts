import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ILocation, IAnalysisParams, IReportConfig } from '@/types/analysis'

const CURRENT_YEAR = new Date().getFullYear()
const SESSION_KEY = 'wind_insights_wizard'

const DEFAULT_PARAMS: IAnalysisParams = {
  heights: [100],
  startYear: CURRENT_YEAR - 10,
  endYear: CURRENT_YEAR - 1,
  windSurface: 'vegtype_8',
  filterOutliers: true,
  projectName: '',
}

const DEFAULT_REPORT_CONFIG: IReportConfig = {
  projectName: '',
  projectAddress: '',
  reportDate: new Date().toISOString().slice(0, 10),
  organization: '',
  confidentiality: '内部',
}

export const useWizardStore = defineStore('wizard', () => {
  const currentStep = ref(0)
  const location = ref<ILocation | null>(null)
  const params = ref<IAnalysisParams>({ ...DEFAULT_PARAMS })
  const reportConfig = ref<IReportConfig>({ ...DEFAULT_REPORT_CONFIG })

  const canGoNext = computed(() => {
    if (currentStep.value === 0) return location.value !== null
    if (currentStep.value === 1) return params.value.heights.length > 0
    return true
  })

  function nextStep() {
    if (currentStep.value < 5) currentStep.value++
  }

  function prevStep() {
    if (currentStep.value > 0) currentStep.value--
  }

  function goToStep(step: number) {
    if (step >= 0 && step <= 5) currentStep.value = step
  }

  function setLocation(loc: ILocation) {
    location.value = loc
  }

  function setParams(p: Partial<IAnalysisParams>) {
    params.value = { ...params.value, ...p }
  }

  function reset() {
    currentStep.value = 0
    location.value = null
    params.value = { ...DEFAULT_PARAMS }
    reportConfig.value = { ...DEFAULT_REPORT_CONFIG }
    sessionStorage.removeItem(SESSION_KEY)
  }

  // 持久化关键状态到 sessionStorage
  function persist() {
    try {
      sessionStorage.setItem(SESSION_KEY, JSON.stringify({
        currentStep: currentStep.value,
        location: location.value,
        params: params.value,
        reportConfig: reportConfig.value,
      }))
    } catch {
      // sessionStorage 不可用时静默失败
    }
  }

  function restore() {
    try {
      const raw = sessionStorage.getItem(SESSION_KEY)
      if (!raw) return
      const saved = JSON.parse(raw)
      currentStep.value = saved.currentStep ?? 0
      location.value = saved.location ?? null
      params.value = { ...DEFAULT_PARAMS, ...saved.params }
      reportConfig.value = { ...DEFAULT_REPORT_CONFIG, ...saved.reportConfig }
    } catch {
      // 解析失败时忽略
    }
  }

  return {
    currentStep,
    location,
    params,
    reportConfig,
    canGoNext,
    nextStep,
    prevStep,
    goToStep,
    setLocation,
    setParams,
    reset,
    persist,
    restore,
  }
})
