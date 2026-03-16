<script setup lang="ts">
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useAnalysisStore } from '@/stores/analysis'
import { useWizardStore } from '@/stores/wizard'

const analysisStore = useAnalysisStore()
const wizardStore = useWizardStore()
const { result } = storeToRefs(analysisStore)

const location = computed(() => result.value?.location)
const params = computed(() => result.value?.params)

// 取第一个分析高度的数据作为总览代表值
const firstHeight = computed(() => result.value?.analysisHeights[0] ?? 100)
const firstKey = computed(() => `${firstHeight.value}m`)

const firstStats = computed(() => result.value?.basicStats[firstKey.value])
const firstWeibull = computed(() => result.value?.weibullResults[firstKey.value])
const firstWpd = computed(() => result.value?.wpdResults[firstKey.value])

const cards = computed(() => {
  if (!firstStats.value) return []
  return [
    {
      label: '年均风速',
      value: `${firstStats.value.annualMeanWs.toFixed(2)} m/s`,
      icon: '💨',
      color: 'blue',
    },
    {
      label: '年均风功率密度',
      value: `${(firstWpd.value?.annualWpd ?? 0).toFixed(0)} W/m²`,
      icon: '⚡',
      color: 'yellow',
    },
    {
      label: '主导风向',
      value: firstStats.value.dominantDirection,
      icon: '🧭',
      color: 'green',
    },
    {
      label: 'Weibull k',
      value: firstWeibull.value?.k.toFixed(3) ?? '—',
      icon: '📈',
      color: 'purple',
    },
    {
      label: 'Weibull c',
      value: firstWeibull.value ? `${firstWeibull.value.c.toFixed(2)} m/s` : '—',
      icon: '📉',
      color: 'indigo',
    },
    {
      label: '数据有效率',
      value: `${firstStats.value.dataValidRate.toFixed(1)}%`,
      icon: '✅',
      color: 'teal',
    },
  ]
})

const colorMap: Record<string, string> = {
  blue: 'bg-blue-50 border-blue-200 text-blue-700',
  yellow: 'bg-yellow-50 border-yellow-200 text-yellow-700',
  green: 'bg-green-50 border-green-200 text-green-700',
  purple: 'bg-purple-50 border-purple-200 text-purple-700',
  indigo: 'bg-indigo-50 border-indigo-200 text-indigo-700',
  teal: 'bg-teal-50 border-teal-200 text-teal-700',
}
</script>

<template>
  <div class="max-w-4xl mx-auto px-6 py-8 space-y-8">
    <div class="flex items-start justify-between">
      <div>
        <h2 class="text-lg font-semibold text-gray-800">分析总览</h2>
        <p v-if="location" class="text-sm text-gray-500 mt-1">
          {{ location.gridLat.toFixed(3) }}°N, {{ location.gridLng.toFixed(3) }}°E
          · {{ result?.analysisHeights.join('/') }} m
          · {{ params?.startYear }}—{{ params?.endYear }}
        </p>
      </div>
    </div>

    <!-- 关键指标卡片 -->
    <div v-if="firstStats" class="grid grid-cols-2 md:grid-cols-3 gap-4">
      <div
        v-for="card in cards"
        :key="card.label"
        class="rounded-xl border p-4 space-y-1"
        :class="colorMap[card.color]"
      >
        <div class="flex items-center gap-2">
          <span class="text-xl">{{ card.icon }}</span>
          <span class="text-xs font-medium opacity-70">{{ card.label }}</span>
        </div>
        <p class="text-2xl font-bold">{{ card.value }}</p>
      </div>
    </div>

    <div v-else class="text-center py-12 text-gray-400">
      暂无数据，请先完成数据加载步骤
    </div>

    <!-- 快速操作 -->
    <div v-if="firstStats" class="flex gap-4 pt-2">
      <button
        class="px-6 py-2.5 bg-blue-600 text-white text-sm rounded-lg hover:bg-blue-700 transition-colors"
        @click="wizardStore.nextStep()"
      >
        查看详细分析 →
      </button>
    </div>
  </div>
</template>
