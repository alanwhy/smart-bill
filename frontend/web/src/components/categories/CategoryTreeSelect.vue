<template>
  <!-- 触发器 -->
  <div ref="triggerRef" class="relative inline-block">
    <button
      type="button"
      @click="toggleOpen"
      class="flex items-center gap-1.5 h-8 px-3 text-sm rounded-lg border border-border bg-surface text-text hover:border-primary/50 transition-colors duration-150 min-w-[120px] max-w-[200px]"
      :class="isOpen ? 'border-primary/70 ring-1 ring-primary/30' : ''"
    >
      <span class="flex-1 text-left truncate">{{ triggerLabel }}</span>
      <svg
        class="w-3.5 h-3.5 text-text-muted flex-shrink-0 transition-transform duration-150"
        :class="isOpen ? 'rotate-180' : ''"
        fill="none" stroke="currentColor" viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>
  </div>

  <!-- 下拉面板（Teleport to body，fixed 定位） -->
  <Teleport to="body">
    <Transition name="dropdown">
      <div
        v-if="isOpen"
        ref="dropdownRef"
        :style="dropdownStyle"
        class="fixed z-[9999] min-w-[220px] max-w-[280px] max-h-[360px] overflow-y-auto bg-surface border border-border rounded-xl shadow-lg py-1"
      >
        <!-- 全部选项 -->
        <button
          type="button"
          @click="clearAll"
          class="w-full flex items-center gap-2 px-3 py-2 text-sm hover:bg-border/50 transition-colors duration-100"
          :class="modelValue.length === 0 ? 'text-primary font-medium' : 'text-text-muted'"
        >
          <span class="w-4 h-4 flex-shrink-0 flex items-center justify-center">
            <svg v-if="modelValue.length === 0" class="w-3.5 h-3.5" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
            </svg>
          </span>
          全部分类
        </button>
        <div class="border-t border-border/60 my-1" />

        <!-- 树形节点 -->
        <TreeNode
          v-for="node in treeData"
          :key="node.id"
          :node="node"
          :selected-ids="modelValue"
          :expanded-ids="expandedIds"
          @toggle-expand="toggleExpand"
          @toggle-select="toggleSelectNode"
        />
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount, defineComponent, h } from 'vue'
import { useCategoriesStore } from '@/stores/categories'
import type { CategoryTree } from '@/types/bill'

const props = defineProps<{
  modelValue: number[]
  placeholder?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: number[]]
}>()

const categoriesStore = useCategoriesStore()
const triggerRef = ref<HTMLElement | null>(null)
const dropdownRef = ref<HTMLElement | null>(null)
const isOpen = ref(false)
const expandedIds = ref<Set<number>>(new Set())
const dropdownStyle = ref<Record<string, string>>({})

// ─── 树数据 ───────────────────────────────────────────────
const treeData = computed(() => categoriesStore.buildTree())

// ─── 获取节点所有后代 id（含自身）────────────────────────
function getDescendantIds(node: CategoryTree): number[] {
  const ids: number[] = [node.id]
  if (node.children?.length) {
    node.children.forEach((child) => ids.push(...getDescendantIds(child)))
  }
  return ids
}

// 在树中按 id 查找节点
function findNode(nodes: CategoryTree[], id: number): CategoryTree | null {
  for (const n of nodes) {
    if (n.id === id) return n
    if (n.children?.length) {
      const found = findNode(n.children, id)
      if (found) return found
    }
  }
  return null
}

// ─── 触发器文字 ───────────────────────────────────────────
const triggerLabel = computed(() => {
  if (!props.modelValue.length) return props.placeholder || '全部分类'
  if (props.modelValue.length === 1) {
    const cat = categoriesStore.byId.get(props.modelValue[0])
    return cat?.name || '1 项'
  }
  return `已选 ${props.modelValue.length} 项`
})

// ─── 展开/折叠 ────────────────────────────────────────────
function toggleExpand(id: number) {
  if (expandedIds.value.has(id)) {
    expandedIds.value.delete(id)
  } else {
    expandedIds.value.add(id)
  }
}

// ─── 勾选/取消勾选节点 ───────────────────────────────────
function toggleSelectNode(node: CategoryTree) {
  const descendants = getDescendantIds(node)
  const allSelected = descendants.every((id) => props.modelValue.includes(id))
  const newVal = allSelected
    ? props.modelValue.filter((id) => !descendants.includes(id))
    : [...new Set([...props.modelValue, ...descendants])]
  emit('update:modelValue', newVal)
}

function clearAll() {
  emit('update:modelValue', [])
  close()
}

// ─── 下拉定位 ────────────────────────────────────────────
function updateDropdownPosition() {
  if (!triggerRef.value) return
  const rect = triggerRef.value.getBoundingClientRect()
  const spaceBelow = window.innerHeight - rect.bottom
  const panelH = 360
  if (spaceBelow >= panelH || spaceBelow >= 180) {
    dropdownStyle.value = {
      top: `${rect.bottom + 6}px`,
      left: `${rect.left}px`,
    }
  } else {
    dropdownStyle.value = {
      bottom: `${window.innerHeight - rect.top + 6}px`,
      left: `${rect.left}px`,
    }
  }
}

function toggleOpen() {
  if (isOpen.value) {
    close()
  } else {
    updateDropdownPosition()
    isOpen.value = true
  }
}

function close() {
  isOpen.value = false
}

// ─── 点击外部关闭 ────────────────────────────────────────
function onDocumentMousedown(e: MouseEvent) {
  const target = e.target as Node
  if (
    triggerRef.value?.contains(target) ||
    dropdownRef.value?.contains(target)
  ) return
  close()
}

onMounted(() => {
  document.addEventListener('mousedown', onDocumentMousedown)
  categoriesStore.getOrFetch()
})

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', onDocumentMousedown)
})

// ─── 内联树节点组件 ───────────────────────────────────────
// 使用 defineComponent 定义，避免循环 import
const TreeNode = defineComponent({
  name: 'TreeNode',
  props: {
    node: { type: Object as () => CategoryTree, required: true },
    selectedIds: { type: Array as () => number[], required: true },
    expandedIds: { type: Object as () => Set<number>, required: true },
    depth: { type: Number, default: 0 },
  },
  emits: ['toggle-expand', 'toggle-select'],
  setup(nodeProps, { emit: nodeEmit }) {
    function getCheckState(node: CategoryTree): 'none' | 'some' | 'all' {
      const desc = getDescendantIds(node)
      const selected = desc.filter((id) => nodeProps.selectedIds.includes(id))
      if (selected.length === 0) return 'none'
      if (selected.length === desc.length) return 'all'
      return 'some'
    }

    return () => {
      const node = nodeProps.node
      const hasChildren = node.children && node.children.length > 0
      const isExpanded = nodeProps.expandedIds.has(node.id)
      const checkState = getCheckState(node)
      const paddingLeft = 12 + nodeProps.depth * 16

      const checkboxEl = h('span', {
        class: [
          'w-4 h-4 flex-shrink-0 rounded border flex items-center justify-center transition-colors duration-100',
          checkState === 'all' ? 'bg-primary border-primary' : 'border-border bg-background',
          checkState === 'some' ? 'border-primary/70' : '',
        ],
        style: 'min-width:16px',
      }, [
        checkState === 'all' ? h('svg', { class: 'w-3 h-3 text-background', fill: 'currentColor', viewBox: '0 0 20 20' }, [
          h('path', { 'fill-rule': 'evenodd', d: 'M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z', 'clip-rule': 'evenodd' })
        ]) : checkState === 'some' ? h('span', { class: 'w-2 h-0.5 bg-primary rounded-full' }) : null,
      ])

      const iconEl = h('span', {
        class: 'w-5 h-5 flex-shrink-0 rounded flex items-center justify-center text-xs',
        style: `background-color: ${node.color}22; color: ${node.color}`,
      }, node.icon || '•')

      const expandBtn = hasChildren ? h('button', {
        type: 'button',
        class: 'w-4 h-4 flex-shrink-0 flex items-center justify-center text-text-muted hover:text-text transition-colors',
        onClick: (e: Event) => { e.stopPropagation(); nodeEmit('toggle-expand', node.id) },
      }, [
        h('svg', { class: ['w-3 h-3 transition-transform duration-150', isExpanded ? 'rotate-90' : ''], fill: 'none', stroke: 'currentColor', viewBox: '0 0 24 24' }, [
          h('path', { 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'stroke-width': '2', d: 'M9 5l7 7-7 7' })
        ])
      ]) : h('span', { class: 'w-4 h-4 flex-shrink-0' })

      const rowEl = h('button', {
        type: 'button',
        class: 'w-full flex items-center gap-1.5 px-3 py-1.5 text-sm hover:bg-border/50 transition-colors duration-100 text-left',
        style: { paddingLeft: `${paddingLeft}px` },
        onClick: () => nodeEmit('toggle-select', node),
      }, [expandBtn, checkboxEl, iconEl, h('span', { class: 'truncate text-text' }, node.name)])

      const children = isExpanded && hasChildren
        ? node.children.map((child) => h(TreeNode, {
            node: child,
            selectedIds: nodeProps.selectedIds,
            expandedIds: nodeProps.expandedIds,
            depth: nodeProps.depth + 1,
            onToggleExpand: (id: number) => nodeEmit('toggle-expand', id),
            onToggleSelect: (n: CategoryTree) => nodeEmit('toggle-select', n),
          }))
        : []

      return h('div', {}, [rowEl, ...children])
    }
  },
})
</script>

<style scoped>
.dropdown-enter-active {
  transition: opacity 0.12s ease, transform 0.12s ease;
}
.dropdown-leave-active {
  transition: opacity 0.08s ease, transform 0.08s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
