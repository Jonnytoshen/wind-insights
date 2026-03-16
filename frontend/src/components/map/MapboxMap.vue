<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import mapboxgl from 'mapbox-gl'
import type { ILocation } from '@/types/analysis'
import { snapToMerra2Grid, calcMerra2GridBounds } from '@/utils/geoUtils'
import 'mapbox-gl/dist/mapbox-gl.css'

const props = defineProps<{
  selectedLocation: ILocation | null
}>()

const emit = defineEmits<{
  (e: 'location-selected', location: ILocation): void
}>()

const mapContainer = ref<HTMLDivElement | null>(null)
let map: mapboxgl.Map | null = null
let marker: mapboxgl.Marker | null = null

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_TOKEN as string

onMounted(() => {
  if (!mapContainer.value) return

  mapboxgl.accessToken = MAPBOX_TOKEN

  map = new mapboxgl.Map({
    container: mapContainer.value,
    style: 'mapbox://styles/mapbox/satellite-streets-v12',
    center: [104.0, 35.0],
    zoom: 4,
  })

  map.addControl(new mapboxgl.NavigationControl(), 'top-right')
  map.addControl(new mapboxgl.ScaleControl({ maxWidth: 100 }), 'bottom-left')

  map.on('load', () => {
    setupGridLayer()
  })

  map.on('click', (e) => {
    const { lng, lat } = e.lngLat
    const grid = snapToMerra2Grid(lng, lat)
    const location: ILocation = {
      lat,
      lng,
      gridLat: grid.lat,
      gridLng: grid.lng,
    }
    emit('location-selected', location)
    placeMarker(lng, lat)
    updateGridHighlight(grid.lat, grid.lng)
  })
})

onUnmounted(() => {
  map?.remove()
  map = null
})

// 监听外部 location 变化（如从历史记录或手动输入设置）
watch(
  () => props.selectedLocation,
  (loc) => {
    if (!loc || !map) return
    placeMarker(loc.lng, loc.lat)
    updateGridHighlight(loc.gridLat, loc.gridLng)
    map.flyTo({ center: [loc.lng, loc.lat], zoom: 8, duration: 1000 })
  }
)

function placeMarker(lng: number, lat: number) {
  if (!map) return
  marker?.remove()
  marker = new mapboxgl.Marker({ color: '#2563eb' })
    .setLngLat([lng, lat])
    .addTo(map)
}

function setupGridLayer() {
  if (!map) return
  map.addSource('merra2-grid', {
    type: 'geojson',
    data: { type: 'FeatureCollection', features: [] },
  })
  map.addLayer({
    id: 'merra2-grid-fill',
    type: 'fill',
    source: 'merra2-grid',
    paint: {
      'fill-color': '#2563eb',
      'fill-opacity': 0.08,
    },
  })
  map.addLayer({
    id: 'merra2-grid-outline',
    type: 'line',
    source: 'merra2-grid',
    paint: {
      'line-color': '#2563eb',
      'line-width': 1.5,
      'line-opacity': 0.5,
    },
  })
}

function updateGridHighlight(gridLat: number, gridLng: number) {
  if (!map || !map.getSource('merra2-grid')) return
  const coords = calcMerra2GridBounds(gridLat, gridLng)
  ;(map.getSource('merra2-grid') as mapboxgl.GeoJSONSource).setData({
    type: 'FeatureCollection',
    features: [
      {
        type: 'Feature',
        geometry: { type: 'Polygon', coordinates: [coords] },
        properties: {},
      },
    ],
  })
}
</script>

<template>
  <div ref="mapContainer" class="w-full h-full" />
</template>
