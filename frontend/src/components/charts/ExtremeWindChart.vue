<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { IExtremeWindResult } from '@/types/analysis'
import { extremeWindOption } from './extremeWindOption'

const props = defineProps<{
  data: IExtremeWindResult
  height: number
}>()

const chartEl = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObs: ResizeObserver | null = null

onMounted(() => {
  if (!chartEl.value) return
  chart = echarts.init(chartEl.value)
  chart.setOption(extremeWindOption(props.data))

  resizeObs = new ResizeObserver(() => chart?.resize())
  resizeObs.observe(chartEl.value)
})

onUnmounted(() => {
  resizeObs?.disconnect()
  chart?.dispose()
})

watch(() => [props.data, props.height], () => {
  chart?.setOption(extremeWindOption(props.data), true)
})

defineExpose({
  getDataURL: () => chart?.getDataURL({ type: 'png', pixelRatio: 2 }),
})
</script>

<template>
  <div class="space-y-4">
    <div class="flex items-center gap-8 text-sm bg-red-50 rounded-lg p-3">
      <div>
        <span class="text-slate-500 mr-2">V₅₀</span>
        <span class="text-2xl font-bold text-red-700">{{ data.v50.toFixed(1) }}</span>
        <span class="text-slate-500 ml-1">m/s</span>
      </div>
      <div>
        <span class="text-slate-500 mr-2">V₁₀₀</span>
        <span class="text-2xl font-bold text-purple-700">{{ data.v100.toFixed(1) }}</span>
        <span class="text-slate-500 ml-1">m/s</span>
      </div>
      <span class="text-slate-400 text-xs">Gumbel I 型拟合 ({{ data.sampleYears }} 年数据)</span>
    </div>
    <div ref="chartEl" class="w-full h-72" />
  </div>
</template>
