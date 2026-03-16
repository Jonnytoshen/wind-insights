<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'
import type { IBasicStats } from '@/types/analysis'
import { windSpeedLineOption } from './windSpeedLineOption'

const props = defineProps<{
  data: IBasicStats
  height: number
}>()

const chartEl = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null
let resizeObs: ResizeObserver | null = null

onMounted(() => {
  if (!chartEl.value) return
  chart = echarts.init(chartEl.value)
  chart.setOption(windSpeedLineOption({
    timestamps: props.data.monthlyMeanTimestamps ?? [],
    values: props.data.monthlyMeanValues ?? [],
  }))

  resizeObs = new ResizeObserver(() => chart?.resize())
  resizeObs.observe(chartEl.value)
})

onUnmounted(() => {
  resizeObs?.disconnect()
  chart?.dispose()
})

watch(
  () => [props.data, props.height],
  () => {
    chart?.setOption(windSpeedLineOption({
      timestamps: props.data.monthlyMeanTimestamps ?? [],
      values: props.data.monthlyMeanValues ?? [],
    }), true)
  }
)
</script>

<template>
  <div ref="chartEl" class="w-full h-80" />
</template>
