import { useWizardStore } from '@/stores/wizard'
import { useAnalysisStore } from '@/stores/analysis'
import { startAnalysis, getAnalysisResult } from '@/api'

export function useAnalysis() {
  const wizardStore = useWizardStore()
  const analysisStore = useAnalysisStore()

  async function triggerAnalysis() {
    const { location, params } = wizardStore
    if (!location) {
      analysisStore.setError('请先选择分析点位')
      return
    }

    analysisStore.setLoading(true)
    analysisStore.clearResult()

    try {
      const response = await startAnalysis(location, params)
      analysisStore.setTaskId(response.taskId)
    } catch (err) {
      const message = err instanceof Error ? err.message : '启动分析失败'
      analysisStore.setError(message)
    }
  }

  async function fetchResult() {
    const { taskId } = analysisStore
    if (!taskId) return

    try {
      const result = await getAnalysisResult(taskId)
      analysisStore.setResult(result)
    } catch (err) {
      const message = err instanceof Error ? err.message : '获取结果失败'
      analysisStore.setError(message)
    }
  }

  return { triggerAnalysis, fetchResult }
}
