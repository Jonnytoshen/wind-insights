import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { IHistoryItem } from '@/types/analysis'

const STORAGE_KEY = 'wind_insights_history'
const MAX_HISTORY = 20

export const useHistoryStore = defineStore('history', () => {
  const records = ref<IHistoryItem[]>(_loadFromStorage())

  function _loadFromStorage(): IHistoryItem[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      return raw ? JSON.parse(raw) : []
    } catch {
      return []
    }
  }

  function _saveToStorage() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(records.value))
    } catch {
      // localStorage 不可用时静默失败
    }
  }

  function addRecord(item: IHistoryItem) {
    // 去重：同坐标 + 同参数的记录更新而非追加
    const existingIdx = records.value.findIndex(
      (r) => r.lat === item.lat && r.lng === item.lng
    )
    if (existingIdx !== -1) {
      records.value.splice(existingIdx, 1)
    }
    records.value.unshift(item)
    if (records.value.length > MAX_HISTORY) {
      records.value = records.value.slice(0, MAX_HISTORY)
    }
    _saveToStorage()
  }

  function removeRecord(id: string) {
    records.value = records.value.filter((r) => r.id !== id)
    _saveToStorage()
  }

  function clearAll() {
    records.value = []
    localStorage.removeItem(STORAGE_KEY)
  }

  return { records, addRecord, removeRecord, clearAll }
})
