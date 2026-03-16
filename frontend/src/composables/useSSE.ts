import { ref, watch, onUnmounted } from 'vue'
import type { Ref } from 'vue'
import type { IProgressInfo } from '@/types/analysis'

// SSE uses native EventSource (not Axios), so we manually camelize keys.
function toCamel(s: string): string {
  return s.replace(/_([a-z])/g, (_, c) => c.toUpperCase())
}
function camelizeKeys(obj: Record<string, unknown>): Record<string, unknown> {
  return Object.fromEntries(Object.entries(obj).map(([k, v]) => [toCamel(k), v]))
}

export function useSSE(taskId: Ref<string | null>) {
  const progress = ref<IProgressInfo | null>(null)
  const sseError = ref<string | null>(null)
  let source: EventSource | null = null

  function closeSource() {
    if (source) {
      source.close()
      source = null
    }
  }

  watch(
    taskId,
    (id) => {
      closeSource()
      sseError.value = null

      if (!id) return

      source = new EventSource(`/api/analysis/${id}/progress`)

      source.onmessage = (e) => {
        try {
          const raw = JSON.parse(e.data) as Record<string, unknown>
          const data = camelizeKeys(raw) as unknown as IProgressInfo
          progress.value = data
          if (data.status === 'success' || data.status === 'error') {
            closeSource()
          }
        } catch {
          sseError.value = '进度数据解析失败'
          closeSource()
        }
      }

      source.onerror = () => {
        sseError.value = 'SSE 连接中断'
        closeSource()
      }
    },
    { immediate: true }
  )

  onUnmounted(() => {
    closeSource()
  })

  return { progress, sseError }
}
