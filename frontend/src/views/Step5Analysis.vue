<script setup lang="ts">
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useAnalysisStore } from '@/stores/analysis'
import WindSpeedLineChart from '@/components/charts/WindSpeedLineChart.vue'
import WindRoseChart from '@/components/charts/WindRoseChart.vue'
import WeibullChart from '@/components/charts/WeibullChart.vue'
import WpdChart from '@/components/charts/WpdChart.vue'
import ShearProfileChart from '@/components/charts/ShearProfileChart.vue'
import TurbulenceChart from '@/components/charts/TurbulenceChart.vue'
import ExtremeWindChart from '@/components/charts/ExtremeWindChart.vue'
import RepYearChart from '@/components/charts/RepYearChart.vue'
import MultiHeightCompare from '@/components/charts/MultiHeightCompare.vue'

const analysisStore = useAnalysisStore()
const { result } = storeToRefs(analysisStore)

const activeModule = ref('basic')
const activeHeight = ref<string>('')

const heights = computed(() => result.value?.analysisHeights ?? [])
const hasMultiHeight = computed(() => heights.value.length >= 2)

// 初始化 activeHeight
if (heights.value.length > 0) {
  activeHeight.value = `${heights.value[0]}m`
}

const modules = computed(() => {
  const list = [
    { key: 'basic', label: '基础统计' },
    { key: 'windrose', label: '风速风向玫瑰图' },
    { key: 'weibull', label: 'Weibull 分布' },
    { key: 'wpd', label: '风功率密度' },
    { key: 'shear', label: '风切变分析' },
    { key: 'turbulence', label: '湍流强度' },
    { key: 'extreme', label: '极端风速' },
    { key: 'repyear', label: '代表年分析' },
  ]
  if (hasMultiHeight.value) {
    list.push({ key: 'compare', label: '多高度对比' })
  }
  return list
})

const heightKey = computed(() =>
  activeHeight.value || `${heights.value[0] ?? 100}m`
)
</script>

<template>
  <div class="flex" style="height: calc(100vh - 180px)">
    <!-- 左侧导航 -->
    <nav class="w-44 bg-gray-50 border-r border-gray-200 flex flex-col py-4 shrink-0 overflow-y-auto">
      <button
        v-for="mod in modules"
        :key="mod.key"
        class="text-left px-4 py-2.5 text-sm transition-colors"
        :class="activeModule === mod.key
          ? 'bg-blue-50 text-blue-700 font-medium border-r-2 border-blue-600'
          : 'text-gray-600 hover:bg-gray-100'"
        @click="activeModule = mod.key"
      >
        {{ mod.label }}
      </button>
    </nav>

    <!-- 右侧内容 -->
    <div class="flex-1 overflow-auto p-6">
      <!-- 高度切换 -->
      <div 
        v-if="activeModule !== 'shear' && activeModule !== 'compare' && heights.length > 1" 
        class="flex gap-2 mb-4"
      >
        <button
          v-for="h in heights"
          :key="h"
          class="px-3 py-1 rounded-full text-xs border transition-colors"
          :class="activeHeight === `${h}m`
            ? 'bg-blue-600 text-white border-blue-600'
            : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'"
          @click="activeHeight = `${h}m`"
        >
          {{ h }} m
        </button>
      </div>

      <div v-if="!result" class="text-center py-20 text-gray-400">
        暂无数据，请先完成数据加载步骤
      </div>
      <template v-else>
        <!-- 懒渲染：仅当切换到该模块时才挂载 -->
        <WindSpeedLineChart
          v-if="activeModule === 'basic'"
          :data="result.basicStats[heightKey]"
          :height="parseInt(heightKey)"
        />
        <WindRoseChart
          v-else-if="activeModule === 'windrose'"
          :data="result.windRoseData[heightKey]"
          :height="parseInt(heightKey)"
        />
        <WeibullChart
          v-else-if="activeModule === 'weibull'"
          :data="result.weibullResults[heightKey]"
          :height="parseInt(heightKey)"
        />
        <WpdChart
          v-else-if="activeModule === 'wpd'"
          :data="result.wpdResults[heightKey]"
          :height="parseInt(heightKey)"
        />
        <ShearProfileChart
          v-else-if="activeModule === 'shear' && result.shearResult"
          :data="result.shearResult"
        />
        <TurbulenceChart
          v-else-if="activeModule === 'turbulence'"
          :data="result.turbulenceData[heightKey]"
          :height="parseInt(heightKey)"
        />
        <ExtremeWindChart
          v-else-if="activeModule === 'extreme'"
          :data="result.extremeWindResults[heightKey]"
          :height="parseInt(heightKey)"
        />
        <RepYearChart
          v-else-if="activeModule === 'repyear'"
          :data="result.representativeYearResults[heightKey]"
          :height="parseInt(heightKey)"
        />
        <MultiHeightCompare
          v-else-if="activeModule === 'compare'"
          :result="result"
        />
      </template>
    </div>
  </div>
</template>
