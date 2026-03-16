<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useWizardStore } from '@/stores/wizard'
import { useAnalysisStore } from '@/stores/analysis'
import { useAnalysis } from '@/composables/useAnalysis'
import { useSSE } from '@/composables/useSSE'

const wizardStore = useWizardStore()
const analysisStore = useAnalysisStore()
const { triggerAnalysis, fetchResult } = useAnalysis()

const { taskId, error } = storeToRefs(analysisStore)
const { progress, sseError, reconnecting } = useSSE(taskId)

const logMessages = ref<string[]>([])
const retrying = ref(false)

onMounted(async () => {
  // 如果已经有 taskId（刷新后恢复），直接订阅进度；否则启动新任务
  if (!taskId.value) {
    await startTask()
  }
})

async function startTask() {
  logMessages.value = []
  await triggerAnalysis()
}

// 监听进度变化，追加日志
import { watch } from 'vue'
watch(progress, (p) => {
  if (p?.message) {
    logMessages.value.push(p.message)
  }
  // 分析成功后自动跳转步骤 4
  if (p?.status === 'success') {
    fetchResult().then(() => {
      setTimeout(() => wizardStore.nextStep(), 600)
    })
  }
})

async function retry() {
  retrying.value = true
  analysisStore.clearResult()
  logMessages.value = []
  await startTask()
  retrying.value = false
}

function progressPercent() {
  return Math.round(progress.value?.progress ?? 0)
}
</script>

<template>
  <div class="max-w-xl mx-auto px-6 py-12 space-y-8">
    <div class="text-center space-y-2">
      <h2 class="text-lg font-semibold text-gray-800">正在获取分析数据</h2>
      <p class="text-sm text-gray-500">系统正在从 NASA POWER API 拉取 MERRA-2 历史数据，请稍候…</p>
    </div>

    <!-- 进度条 -->
    <div class="space-y-2">
      <div class="flex justify-between text-sm text-gray-600">
        <span>{{ progress?.message ?? '准备中…' }}</span>
        <span>{{ progressPercent() }}%</span>
      </div>
      <div class="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
        <div
          class="h-3 rounded-full transition-all duration-500"
          :class="progress?.status === 'error' ? 'bg-red-500' : 'bg-blue-600'"
          :style="{ width: `${progressPercent()}%` }"
        />
      </div>
    </div>

    <!-- 重连提示 -->
    <div
      v-if="reconnecting"
      class="flex items-center gap-2 bg-yellow-50 border border-yellow-200 rounded-lg px-4 py-2 text-sm text-yellow-700"
    >
      <svg class="animate-spin h-4 w-4 text-yellow-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
      </svg>
      SSE 连接中断，正在重连…
    </div>

    <!-- 错误提示 -->
    <div
      v-if="progress?.status === 'error' || error || sseError"
      class="bg-red-50 border border-red-200 rounded-lg p-4 space-y-3"
    >
      <p class="text-sm text-red-700 font-medium">分析失败</p>
      <p class="text-xs text-red-600">{{ error ?? sseError ?? progress?.message }}</p>
      <button
        class="px-4 py-2 bg-red-600 text-white text-sm rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
        :disabled="retrying"
        @click="retry"
      >
        {{ retrying ? '重试中…' : '重试' }}
      </button>
    </div>

    <!-- 成功提示 -->
    <div
      v-if="progress?.status === 'success'"
      class="bg-green-50 border border-green-200 rounded-lg p-4 text-sm text-green-700 text-center"
    >
      ✅ 数据获取完成，正在跳转…
    </div>

    <!-- 实时日志 -->
    <div class="bg-gray-900 rounded-lg p-4 h-48 overflow-y-auto font-mono text-xs text-green-400 space-y-0.5">
      <p v-if="logMessages.length === 0" class="text-gray-500">等待任务启动…</p>
      <p v-for="(msg, i) in logMessages" :key="i">
        <span class="text-gray-500">[{{ String(i + 1).padStart(2, '0') }}]</span>
        {{ msg }}
      </p>
    </div>

    <p class="text-xs text-center text-gray-400">
      任务 ID：{{ taskId ?? '—' }}
    </p>
  </div>
</template>
