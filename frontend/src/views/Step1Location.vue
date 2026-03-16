<script setup lang="ts">
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useWizardStore } from '@/stores/wizard'
import { useHistoryStore } from '@/stores/history'
import MapboxMap from '@/components/map/MapboxMap.vue'
import type { ILocation } from '@/types/analysis'
import { snapToMerra2Grid, formatCoordinate } from '@/utils/geoUtils'

const wizardStore = useWizardStore()
const historyStore = useHistoryStore()
const { location } = storeToRefs(wizardStore)

const manualLat = ref('')
const manualLng = ref('')
const manualError = ref('')

const formattedLat = computed(() =>
  location.value ? formatCoordinate(location.value.lat, 'lat') : '—'
)
const formattedLng = computed(() =>
  location.value ? formatCoordinate(location.value.lng, 'lng') : '—'
)
const formattedGridLat = computed(() =>
  location.value ? formatCoordinate(location.value.gridLat, 'lat') : '—'
)
const formattedGridLng = computed(() =>
  location.value ? formatCoordinate(location.value.gridLng, 'lng') : '—'
)

function onLocationSelected(loc: ILocation) {
  wizardStore.setLocation(loc)
  manualLat.value = loc.lat.toFixed(4)
  manualLng.value = loc.lng.toFixed(4)
  manualError.value = ''
}

function applyManualCoords() {
  const lat = parseFloat(manualLat.value)
  const lng = parseFloat(manualLng.value)
  if (isNaN(lat) || lat < -90 || lat > 90) {
    manualError.value = '纬度范围：-90 至 90'
    return
  }
  if (isNaN(lng) || lng < -180 || lng > 180) {
    manualError.value = '经度范围：-180 至 180'
    return
  }
  const grid = snapToMerra2Grid(lng, lat)
  wizardStore.setLocation({ lat, lng, gridLat: grid.lat, gridLng: grid.lng })
  manualError.value = ''
}

function useHistoryLocation(item: { lat: number; lng: number; gridLat: number; gridLng: number; projectName: string }) {
  wizardStore.setLocation({
    lat: item.lat,
    lng: item.lng,
    gridLat: item.gridLat,
    gridLng: item.gridLng,
    displayName: item.projectName,
  })
}
</script>

<template>
  <div class="flex h-full" style="height: calc(100vh - 180px)">
    <!-- 地图区域 -->
    <div class="flex-1 relative">
      <MapboxMap :selected-location="location" @location-selected="onLocationSelected" />
    </div>

    <!-- 右侧信息面板 -->
    <aside class="w-80 bg-white border-l border-gray-200 flex flex-col p-4 gap-4 overflow-y-auto">
      <h2 class="text-base font-semibold text-gray-800">选择分析点位</h2>

      <!-- 坐标直接输入 -->
      <div class="space-y-2">
        <p class="text-xs text-gray-500">直接输入坐标</p>
        <div class="flex gap-2">
          <input
            v-model="manualLat"
            type="number"
            step="0.0001"
            placeholder="纬度"
            class="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <input
            v-model="manualLng"
            type="number"
            step="0.0001"
            placeholder="经度"
            class="flex-1 px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        <p v-if="manualError" class="text-xs text-red-500">{{ manualError }}</p>
        <button
          class="w-full py-2 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
          @click="applyManualCoords"
        >
          定位到坐标
        </button>
      </div>

      <!-- 已选点位信息 -->
      <div v-if="location" class="bg-blue-50 rounded-lg p-3 space-y-1.5 text-sm">
        <p class="font-medium text-blue-800">已选点位</p>
        <div class="grid grid-cols-2 gap-x-2 text-xs text-gray-600">
          <span class="text-gray-500">点击坐标</span>
          <span>{{ formattedLat }}, {{ formattedLng }}</span>
          <span class="text-gray-500">MERRA-2 网格</span>
          <span class="text-blue-700 font-medium">{{ formattedGridLat }}, {{ formattedGridLng }}</span>
        </div>
        <p class="text-xs text-gray-400 mt-1">分析将使用 MERRA-2 网格中心坐标</p>
      </div>
      <div v-else class="bg-gray-50 rounded-lg p-3 text-sm text-gray-400 text-center">
        点击地图选择点位
      </div>

      <!-- 历史记录 -->
      <div v-if="historyStore.records.length > 0" class="space-y-2">
        <p class="text-xs text-gray-500">最近点位</p>
        <ul class="space-y-1">
          <li
            v-for="item in historyStore.records.slice(0, 5)"
            :key="item.id"
            class="text-xs px-3 py-2 bg-gray-50 hover:bg-gray-100 rounded-lg cursor-pointer transition-colors"
            @click="useHistoryLocation(item)"
          >
            <p class="font-medium text-gray-700 truncate">{{ item.projectName || '未命名点位' }}</p>
            <p class="text-gray-400">{{ item.gridLat.toFixed(3) }}°, {{ item.gridLng.toFixed(3) }}°</p>
          </li>
        </ul>
      </div>
    </aside>
  </div>
</template>
