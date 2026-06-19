<template>
  <!-- 当前节点行 -->
  <div
    :class="[
      'flex items-center gap-3 px-4 py-3 hover:bg-surface/60 transition-colors cursor-pointer',
      !isLast ? 'border-b border-border/50' : '',
    ]"
    :style="{ paddingLeft: `${16 + depth * 20}px` }"
  >
    <!-- 展开/折叠按钮（有子节点时显示） -->
    <button
      v-if="hasChildren"
      @click.stop="emit('toggle', cat.id)"
      class="flex-shrink-0 w-4 h-4 flex items-center justify-center text-text-muted hover:text-text transition-colors"
    >
      <svg :class="['w-3.5 h-3.5 transition-transform duration-200', expanded ? 'rotate-90' : '']" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
      </svg>
    </button>
    <div v-else class="flex-shrink-0 w-4" />

    <!-- 图标 -->
    <div
      class="flex-shrink-0 w-8 h-8 rounded-md flex items-center justify-center text-base"
      :style="{ backgroundColor: cat.color + '22' }"
    >
      {{ cat.icon || '📦' }}
    </div>

    <!-- 名称信息 -->
    <div class="flex-1 min-w-0">
      <div class="flex items-center gap-2 flex-wrap">
        <span class="text-sm font-medium text-text truncate">{{ cat.name }}</span>
        <span class="text-[10px] px-1.5 py-0.5 rounded text-text-muted bg-surface border border-border">#{{ cat.sort_order }}</span>
        <span v-if="hasChildren" class="text-[10px] px-1.5 py-0.5 rounded bg-primary/10 text-primary border border-primary/20">
          {{ childCount }} 个子分类
        </span>
      </div>
      <div class="flex items-center gap-2 mt-0.5">
        <span class="inline-block w-2.5 h-2.5 rounded-full border border-border/50" :style="{ backgroundColor: cat.color }" />
        <span class="text-xs text-text-muted">{{ cat.color }}</span>
      </div>
    </div>

    <!-- 操作按钮 -->
    <div class="flex gap-1 flex-shrink-0">
      <button @click.stop="emit('create-child', cat.id)" class="p-1.5 hover:bg-primary/10 rounded-lg transition-colors" title="添加子分类">
        <svg class="w-3.5 h-3.5 text-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
        </svg>
      </button>
      <button @click.stop="emit('edit', cat)" class="p-1.5 hover:bg-surface rounded-lg transition-colors" title="编辑">
        <svg class="w-3.5 h-3.5 text-text-secondary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
        </svg>
      </button>
      <button @click.stop="emit('delete', cat)" class="p-1.5 hover:bg-error/10 rounded-lg transition-colors" title="删除">
        <svg class="w-3.5 h-3.5 text-error" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
        </svg>
      </button>
    </div>
  </div>

  <!-- 子节点递归（展开时） -->
  <template v-if="expanded && hasChildren">
    <CategoryNodeRow
      v-for="(child, idx) in children"
      :key="child.id"
      :cat="child"
      :children="getChildren(child.id)"
      :depth="depth + 1"
      :is-last="idx === children.length - 1"
      :expanded="expandedSet.has(child.id)"
      :get-children="getChildren"
      :expanded-set="expandedSet"
      @toggle="emit('toggle', $event)"
      @create-child="emit('create-child', $event)"
      @edit="emit('edit', $event)"
      @delete="emit('delete', $event)"
    />
  </template>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Category } from '@/types/bill'

interface Props {
  cat: Category
  children: Category[]
  depth: number
  isLast: boolean
  expanded: boolean
  getChildren: (id: number) => Category[]
  expandedSet: Set<number>
}

const props = defineProps<Props>()
const emit = defineEmits<{
  toggle: [id: number]
  'create-child': [parentId: number]
  edit: [cat: Category]
  delete: [cat: Category]
}>()

const hasChildren = computed(() => props.children.length > 0)
const childCount = computed(() => props.children.length)
</script>
