/**
 * 将经纬度对齐到最近的 MERRA-2 网格点
 * 纬度分辨率：0.5°，经度分辨率：0.625°
 */
export function snapToMerra2Grid(lng: number, lat: number): { lat: number; lng: number } {
  const latGrid = Math.round(lat / 0.5) * 0.5
  const lngGrid = Math.round(lng / 0.625) * 0.625
  return { lat: latGrid, lng: lngGrid }
}

/**
 * 计算 MERRA-2 网格单元的四角边界（GeoJSON Polygon 坐标）
 */
export function calcMerra2GridBounds(
  gridLat: number,
  gridLng: number
): [number, number][] {
  const halfLat = 0.25
  const halfLng = 0.3125
  return [
    [gridLng - halfLng, gridLat - halfLat],
    [gridLng + halfLng, gridLat - halfLat],
    [gridLng + halfLng, gridLat + halfLat],
    [gridLng - halfLng, gridLat + halfLat],
    [gridLng - halfLng, gridLat - halfLat],
  ]
}

/**
 * 格式化坐标显示（保留 4 位小数）
 */
export function formatCoordinate(value: number, type: 'lat' | 'lng'): string {
  const abs = Math.abs(value).toFixed(4)
  if (type === 'lat') {
    return value >= 0 ? `${abs}°N` : `${abs}°S`
  }
  return value >= 0 ? `${abs}°E` : `${abs}°W`
}

/**
 * 估算分析时长（秒）
 */
export function estimateAnalysisDuration(
  heights: number[],
  startYear: number,
  endYear: number
): number {
  const years = endYear - startYear + 1
  const requests = heights.length * years
  // 每个请求约 3 秒，部分并发，约 1/3 时间
  return Math.ceil((requests * 3) / 3)
}
