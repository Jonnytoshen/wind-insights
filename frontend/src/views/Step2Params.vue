<script setup lang="ts">
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useWizardStore } from '@/stores/wizard'
import { estimateAnalysisDuration } from '@/utils/geoUtils'

const wizardStore = useWizardStore()
const { params } = storeToRefs(wizardStore)

const CURRENT_YEAR = new Date().getFullYear()

// 预设快捷高度
const PRESET_HEIGHTS = [10, 50, 80, 100, 120, 140]

// NASA POWER 支持的地表覆盖类型
const SURFACE_OPTIONS = [
  { value: 'vegtype_11', label: '裸土（Bare Soil）' },
  { value: 'vegtype_12', label: '农田（Cropland）' },
  { value: 'vegtype_6',  label: '稀树草原（Savanna）' },
  { value: 'vegtype_7',  label: '开阔灌丛（Open Shrubland）' },
  { value: 'vegtype_8',  label: '草地（Grassland）' },
  { value: 'openwater',  label: '开阔水面（Open Water）' },
  { value: 'airportgrass', label: '机场草地（Airport Grass）' },
  { value: 'airportice',   label: '机场冰面（Airport Ice）' },
]

const customHeightInput = ref('')
const customHeightError = ref('')

const estimatedSeconds = computed(() =>
  estimateAnalysisDuration(
    params.value.heights,
    params.value.startYear,
    params.value.endYear
  )
)

const estimatedLabel = computed(() => {
  const s = estimatedSeconds.value
  return s < 60 ? `约 ${s} 秒` : `约 ${Math.ceil(s / 60)} 分钟`
})

const yearRange = computed(() => {
  const start = 1981
  const end = CURRENT_YEAR - 1
  const result = []
  for (let y = end; y >= start; y--) result.push(y)
  return result
})

function toggleHeight(h: number) {
  const heights = [...params.value.heights]
  const idx = heights.indexOf(h)
  if (idx === -1) {
    if (heights.length >= 5) return
    heights.push(h)
    heights.sort((a, b) => a - b)
  } else {
    heights.splice(idx, 1)
  }
  wizardStore.setParams({ heights })
}

function addCustomHeight() {
  const h = parseInt(customHeightInput.value)
  if (isNaN(h) || h < 10 || h > 300) {
    customHeightError.value = '高度范围：10 ～ 300 m'
    return
  }
  if (params.value.heights.includes(h)) {
    customHeightError.value = '该高度已添加'
    return
  }
  if (params.value.heights.length >= 5) {
    customHeightError.value = '最多添加 5 个高度'
    return
  }
  const heights = [...params.value.heights, h].sort((a, b) => a - b)
  wizardStore.setParams({ heights })
  customHeightInput.value = ''
  customHeightError.value = ''
}
</script>

<template>
  <div class="max-w-2xl mx-auto px-6 py-8 space-y-8">
    <h2 class="text-lg font-semibold text-gray-800">配置分析参数</h2>

    <!-- 分析高度 -->
    <section class="space-y-3">
      <label class="block text-sm font-medium text-gray-700">
        分析高度（最多 5 个，范围 10 ～ 300 m）
      </label>
      <div class="flex flex-wrap gap-2">
        <button
          v-for="h in PRESET_HEIGHTS"
          :key="h"
          class="px-3 py-1.5 rounded-full text-sm border transition-colors"
          :class="params.heights.includes(h)
            ? 'bg-blue-600 text-white border-blue-600'
            : 'bg-white text-gray-600 border-gray-300 hover:border-blue-400'"
          @click="toggleHeight(h)"
        >
          {{ h }} m
        </button>
      </div>
      <!-- 自定义高度输入 -->
      <div class="flex gap-2 items-start">
        <div class="flex-1">
          <input
            v-model="customHeightInput"
            type="number"
            min="10"
            max="300"
            placeholder="自定义高度（m）"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            @keydown.enter="addCustomHeight"
          />
          <p v-if="customHeightError" class="mt-1 text-xs text-red-500">{{ customHeightError }}</p>
        </div>
        <button
          class="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          @click="addCustomHeight"
        >
          添加
        </button>
      </div>
      <!-- 已选高度标签 -->
      <div v-if="params.heights.length > 0" class="flex flex-wrap gap-2">
        <span
          v-for="h in params.heights"
          :key="h"
          class="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
        >
          {{ h }} m
          <button class="ml-1 text-blue-500 hover:text-blue-700" @click="toggleHeight(h)">×</button>
        </span>
      </div>
    </section>

    <!-- 时间范围 -->
    <section class="space-y-3">
      <label class="block text-sm font-medium text-gray-700">时间范围</label>
      <div class="flex items-center gap-4">
        <div class="flex flex-col gap-1">
          <span class="text-xs text-gray-500">起始年</span>
          <select
            :value="params.startYear"
            class="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            @change="wizardStore.setParams({ startYear: parseInt(($event.target as HTMLSelectElement).value) })"
          >
            <option v-for="y in yearRange" :key="y" :value="y">{{ y }}</option>
          </select>
        </div>
        <span class="text-gray-400 mt-4">—</span>
        <div class="flex flex-col gap-1">
          <span class="text-xs text-gray-500">结束年</span>
          <select
            :value="params.endYear"
            class="px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            @change="wizardStore.setParams({ endYear: parseInt(($event.target as HTMLSelectElement).value) })"
          >
            <option
              v-for="y in yearRange.filter(y => y >= params.startYear)"
              :key="y"
              :value="y"
            >{{ y }}</option>
          </select>
        </div>
        <div class="mt-4 text-sm text-gray-500">
          共 {{ params.endYear - params.startYear + 1 }} 年
        </div>
      </div>
    </section>

    <!-- 地表覆盖类型 -->
    <section class="space-y-2">
      <label class="block text-sm font-medium text-gray-700">地表覆盖类型</label>
      <p class="text-xs text-gray-400">影响 NASA POWER API 内部风切变指数，请选择与场址实际情况最接近的类型</p>
      <select
        :value="params.windSurface"
        class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        @change="wizardStore.setParams({ windSurface: ($event.target as HTMLSelectElement).value })"
      >
        <option v-for="opt in SURFACE_OPTIONS" :key="opt.value" :value="opt.value">
          {{ opt.label }}
        </option>
      </select>
    </section>

    <!-- 项目名称 -->
    <section class="space-y-2">
      <label class="block text-sm font-medium text-gray-700">项目名称（可选）</label>
      <input
        :value="params.projectName"
        type="text"
        placeholder="如：华北某风场预可研"
        class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
        @input="wizardStore.setParams({ projectName: ($event.target as HTMLInputElement).value })"
      />
    </section>

    <!-- 异常值过滤 -->
    <section class="flex items-center justify-between py-2">
      <div>
        <p class="text-sm font-medium text-gray-700">异常值过滤（3σ 法）</p>
        <p class="text-xs text-gray-400">过滤超出 3 倍标准差的异常风速记录</p>
      </div>
      <button
        class="relative w-12 h-6 rounded-full transition-colors"
        :class="params.filterOutliers ? 'bg-blue-600' : 'bg-gray-300'"
        @click="wizardStore.setParams({ filterOutliers: !params.filterOutliers })"
      >
        <span
          class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow transition-transform"
          :class="params.filterOutliers ? 'translate-x-6' : 'translate-x-0'"
        />
      </button>
    </section>

    <!-- 预估时长 -->
    <div class="bg-yellow-50 border border-yellow-200 rounded-lg px-4 py-3 text-sm text-yellow-800">
      预计分析时长：<strong>{{ estimatedLabel }}</strong>
      （{{ params.heights.length }} 个高度 × {{ params.endYear - params.startYear + 1 }} 年）
    </div>
  </div>
</template>
