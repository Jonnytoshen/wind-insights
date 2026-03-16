<script setup lang="ts">
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import { useWizardStore } from '@/stores/wizard'
import { useAnalysisStore } from '@/stores/analysis'
import { generateReport } from '@/api'

const wizardStore = useWizardStore()
const analysisStore = useAnalysisStore()
const { reportConfig } = storeToRefs(wizardStore)
const { taskId, result } = storeToRefs(analysisStore)

const generating = ref(false)
const genError = ref('')
const downloadUrl = ref('')

const confidentialityOptions = ['公开', '内部', '秘密', '机密'] as const

// 自动填充项目名称和地址
if (!reportConfig.value.projectName && result.value?.params.projectName) {
  reportConfig.value.projectName = result.value.params.projectName
}
if (!reportConfig.value.projectAddress && result.value?.location) {
  const loc = result.value.location
  reportConfig.value.projectAddress =
    `纬度 ${loc.gridLat.toFixed(3)}°N，经度 ${loc.gridLng.toFixed(3)}°E`
}

async function handleGeneratePdf() {
  if (!taskId.value) {
    genError.value = '未找到分析任务，请重新分析'
    return
  }
  generating.value = true
  genError.value = ''
  downloadUrl.value = ''

  try {
    // 收集图表图片（各 ECharts 实例 getDataURL）
    // 在 Step5Analysis 懒加载场景下图表可能不在 DOM 中，此处收集页面上已渲染的图表
    const chartImages: Record<string, string> = {}
    document.querySelectorAll<HTMLCanvasElement>('canvas[data-chart-id]').forEach((canvas) => {
      const id = canvas.getAttribute('data-chart-id') ?? ''
      if (id) chartImages[id] = canvas.toDataURL('image/png')
    })

    const blob = await generateReport(taskId.value, chartImages, reportConfig.value)
    const url = URL.createObjectURL(blob)
    downloadUrl.value = url

    // 自动触发下载
    const a = document.createElement('a')
    a.href = url
    const date = reportConfig.value.reportDate.replaceAll('-', '')
    a.download = `wind_report_${date}.pdf`
    a.click()
  } catch (err) {
    genError.value = err instanceof Error ? err.message : '生成 PDF 失败，请重试'
  } finally {
    generating.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto px-6 py-8 space-y-8">
    <div>
      <h2 class="text-lg font-semibold text-gray-800">生成 PDF 报告</h2>
      <p class="text-sm text-gray-500 mt-1">填写封面信息后，点击生成按钮下载专业分析报告</p>
    </div>

    <!-- 封面信息表单 -->
    <div class="space-y-4">
      <div class="grid gap-4">
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">项目名称</label>
          <input
            v-model="reportConfig.projectName"
            type="text"
            placeholder="如：华北某风场预可研"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">项目地址</label>
          <input
            v-model="reportConfig.projectAddress"
            type="text"
            placeholder="自动填充坐标，可修改为具体地名"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-1.5">
            <label class="text-sm font-medium text-gray-700">报告日期</label>
            <input
              v-model="reportConfig.reportDate"
              type="date"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div class="space-y-1.5">
            <label class="text-sm font-medium text-gray-700">保密等级</label>
            <select
              v-model="reportConfig.confidentiality"
              class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option v-for="opt in confidentialityOptions" :key="opt" :value="opt">{{ opt }}</option>
            </select>
          </div>
        </div>
        <div class="space-y-1.5">
          <label class="text-sm font-medium text-gray-700">编制单位</label>
          <input
            v-model="reportConfig.organization"
            type="text"
            placeholder="如：XX 能源咨询有限公司"
            class="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>
    </div>

    <!-- 报告目录预览 -->
    <div class="bg-gray-50 rounded-lg p-4 space-y-1 text-sm text-gray-600">
      <p class="font-medium text-gray-800 mb-2">报告目录预览</p>
      <ol class="space-y-0.5 list-decimal list-inside text-xs text-gray-500">
        <li>项目概况</li>
        <li>风资源概况</li>
        <li>风速统计分析</li>
        <li>风向分析</li>
        <li>风功率密度分析</li>
        <li>风切变分析</li>
        <li>湍流强度分析</li>
        <li>极端风速分析</li>
        <li>代表年分析</li>
        <li>综合评价</li>
      </ol>
    </div>

    <!-- 错误提示 -->
    <div v-if="genError" class="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-700">
      {{ genError }}
    </div>

    <!-- 下载成功提示 -->
    <div v-if="downloadUrl" class="bg-green-50 border border-green-200 rounded-lg p-3 text-sm text-green-700">
      ✅ PDF 报告已生成，浏览器正在下载…
      <a :href="downloadUrl" download class="ml-2 underline">重新下载</a>
    </div>

    <!-- 生成按钮 -->
    <button
      class="w-full py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      :disabled="generating || !taskId"
      @click="handleGeneratePdf"
    >
      {{ generating ? '生成中，请稍候…' : '📄 生成 PDF 报告' }}
    </button>
  </div>
</template>
