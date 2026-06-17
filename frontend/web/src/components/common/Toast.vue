<template>
  <transition name="toast">
    <div
      v-if="visible"
      :class="[
        'fixed bottom-6 left-1/2 -translate-x-1/2 z-[100] flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg text-sm font-medium min-w-[200px] max-w-[320px]',
        typeClasses,
      ]"
    >
      <span class="text-base leading-none">{{ icon }}</span>
      <span class="flex-1">{{ message }}</span>
      <button @click="visible = false" class="opacity-60 hover:opacity-100 transition-opacity leading-none">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </button>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'

const props = withDefaults(defineProps<{
  message: string
  type?: 'error' | 'success' | 'info'
  duration?: number
}>(), {
  type: 'error',
  duration: 3000,
})

const emit = defineEmits<{ close: [] }>()

const visible = ref(true)
let timer: ReturnType<typeof setTimeout>

const typeClasses = computed(() => ({
  error: 'bg-error text-white',
  success: 'bg-green-500 text-white',
  info: 'bg-primary text-white',
}[props.type]))

const icon = computed(() => ({
  error: '✕',
  success: '✓',
  info: 'ℹ',
}[props.type]))

const startTimer = () => {
  clearTimeout(timer)
  timer = setTimeout(() => {
    visible.value = false
    setTimeout(() => emit('close'), 300)
  }, props.duration)
}

watch(visible, (val) => {
  if (val) startTimer()
}, { immediate: true })
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(16px);
}
</style>
