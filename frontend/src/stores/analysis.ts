import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { IAnalysisResult } from '@/types/analysis'

export const useAnalysisStore = defineStore('analysis', () => {
  const taskId = ref<string | null>(null)
  const result = ref<IAnalysisResult | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  function setTaskId(id: string) {
    taskId.value = id
    error.value = null
  }

  function setResult(r: IAnalysisResult) {
    result.value = r
    isLoading.value = false
    error.value = null
  }

  function setLoading(loading: boolean) {
    isLoading.value = loading
  }

  function setError(msg: string) {
    error.value = msg
    isLoading.value = false
  }

  function clearResult() {
    taskId.value = null
    result.value = null
    isLoading.value = false
    error.value = null
  }

  return {
    taskId,
    result,
    isLoading,
    error,
    setTaskId,
    setResult,
    setLoading,
    setError,
    clearResult,
  }
})
