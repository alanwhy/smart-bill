<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div class="fixed inset-0 z-50 bg-black/50" @click.self="emit('cancel')" />
    </Transition>
    <div class="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">
      <Transition name="modal" appear>
        <div class="bg-surface rounded-2xl shadow-xl w-full max-w-sm pointer-events-auto">
          <div class="p-6">
            <h3 class="text-lg font-semibold text-text mb-2">{{ title }}</h3>
            <p class="text-sm text-text-secondary">{{ message }}</p>
          </div>
          <div class="border-t border-border px-6 py-4 flex gap-2 justify-end">
            <button
              @click="emit('cancel')"
              class="btn btn-secondary btn-sm"
            >
              {{ cancelLabel }}
            </button>
            <button
              @click="emit('confirm')"
              :class="['btn btn-sm', danger ? 'bg-error hover:bg-error/80 text-white' : 'btn-primary']"
            >
              {{ confirmLabel }}
            </button>
          </div>
        </div>
      </Transition>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  title: string
  message: string
  confirmLabel?: string
  cancelLabel?: string
  danger?: boolean
}>(), {
  confirmLabel: '确认',
  cancelLabel: '取消',
  danger: false,
})

const emit = defineEmits<{
  confirm: []
  cancel: []
}>()
</script>
