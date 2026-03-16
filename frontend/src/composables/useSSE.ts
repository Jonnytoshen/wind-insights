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

const MAX_RETRIES = 5
const BASE_DELAY_MS = 1000  // doubles each attempt: 1s, 2s, 4s, 8s, 16s
const MAX_DELAY_MS = 30_000

export function useSSE(taskId: Ref<string | null>) {
  const progress = ref<IProgressInfo | null>(null)
  const sseError = ref<string | null>(null)
  const reconnecting = ref(false)

  let source: EventSource | null = null
  let retryCount = 0
  let retryTimer: ReturnType<typeof setTimeout> | null = null
  let finished = false   // set when task status is success/error

  function clearRetryTimer() {
    if (retryTimer !== null) {
      clearTimeout(retryTimer)
      retryTimer = null
    }
  }

  function closeSource() {
    if (source) {
      source.close()
      source = null
    }
  }

  function connect(id: string) {
    closeSource()
    source = new EventSource(`/api/analysis/${id}/progress`)

    source.onmessage = (e: MessageEvent) => {
      // Any successful message resets the retry counter.
      retryCount = 0
      reconnecting.value = false
      try {
        const raw = JSON.parse(e.data) as Record<string, unknown>
        const data = camelizeKeys(raw) as unknown as IProgressInfo
        progress.value = data
        if (data.status === 'success' || data.status === 'error') {
          finished = true
          closeSource()
        }
      } catch {
        sseError.value = '进度数据解析失败'
        finished = true
        closeSource()
      }
    }

    source.onerror = () => {
      closeSource()

      // If task already finished, a close from the server is expected — ignore.
      if (finished) return

      retryCount++
      if (retryCount > MAX_RETRIES) {
        sseError.value = `SSE 连接失败（已重试 ${MAX_RETRIES} 次）`
        reconnecting.value = false
        return
      }

      const delay = Math.min(BASE_DELAY_MS * 2 ** (retryCount - 1), MAX_DELAY_MS)
      reconnecting.value = true
      retryTimer = setTimeout(() => {
        if (!finished) connect(id)
      }, delay)
    }
  }

  watch(
    taskId,
    (id) => {
      // Reset all state when task changes.
      clearRetryTimer()
      closeSource()
      finished = false
      retryCount = 0
      reconnecting.value = false
      sseError.value = null

      if (!id) return
      connect(id)
    },
    { immediate: true }
  )

  onUnmounted(() => {
    clearRetryTimer()
    closeSource()
  })

  return { progress, sseError, reconnecting }
}
