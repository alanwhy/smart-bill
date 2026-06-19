<template>
  <div class="min-h-screen flex flex-col items-center justify-center bg-background text-text px-4 py-12">
    <!-- Brand -->
    <div class="mb-8 text-center login-brand-appear">
      <div class="flex items-center justify-center gap-2.5 mb-2">
        <div class="w-10 h-10 rounded-xl bg-primary/10 flex items-center justify-center">
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
            <path d="M7 8V6.5C7 5.67 7.67 5 8.5 5h5C14.33 5 15 5.67 15 6.5V8" stroke="#F59E0B" stroke-width="1.8" stroke-linecap="round"/>
            <rect x="2" y="8" width="20" height="12" rx="3" fill="#F59E0B"/>
            <rect x="14" y="11" width="6" height="6" rx="3" fill="#92400E"/>
            <circle cx="17" cy="14" r="1.5" fill="#F59E0B"/>
          </svg>
        </div>
        <span class="text-2xl font-bold text-primary tracking-tight">爱理财</span>
      </div>
      <p class="text-sm text-text-muted">智能账单识别与管理</p>
    </div>

    <!-- Login Card -->
    <div class="w-full max-w-sm card p-8 login-card-appear">
      <h2 class="text-xl font-semibold text-text mb-6">登录</h2>

      <form @submit.prevent="handleLogin" class="space-y-5">
        <!-- Username -->
        <div>
          <label for="username" class="block text-sm font-medium text-text-secondary mb-1.5">
            用户名
          </label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            autocomplete="username"
            placeholder="请输入用户名"
            :disabled="isLoading"
            class="input disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        <!-- Password -->
        <div>
          <label for="password" class="block text-sm font-medium text-text-secondary mb-1.5">
            密码
          </label>
          <div class="relative">
            <input
              id="password"
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              autocomplete="current-password"
              placeholder="请输入密码"
              :disabled="isLoading"
              class="input pr-10 disabled:opacity-50 disabled:cursor-not-allowed"
            />
            <button
              type="button"
              @click="showPassword = !showPassword"
              class="absolute inset-y-0 right-0 flex items-center pr-3 cursor-pointer text-text-muted hover:text-text transition-colors duration-200"
              :aria-label="showPassword ? '隐藏密码' : '显示密码'"
              tabindex="-1"
            >
              <svg v-if="showPassword" class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
              </svg>
              <svg v-else class="w-[18px] h-[18px]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
              </svg>
            </button>
          </div>
        </div>

        <!-- Error -->
        <Transition name="fade">
          <p v-if="errorMsg" :key="errorMsg" class="text-sm text-error shake">{{ errorMsg }}</p>
        </Transition>

        <!-- Submit -->
        <button
          type="submit"
          :disabled="isLoading || !form.username || !form.password"
          class="btn btn-primary w-full gap-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-primary"
        >
          <svg v-if="isLoading" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          <span>{{ isLoading ? '登录中...' : '登录' }}</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const form = ref({ username: '', password: '' })
const showPassword = ref(false)
const isLoading = ref(false)
const errorMsg = ref('')

async function handleLogin() {
  // 先清空再设置，让 :key 变化触发 shake 重新播放
  errorMsg.value = ''
  isLoading.value = true
  try {
    await authStore.login(form.value.username, form.value.password)
    if (authStore.mustChangePassword) {
      router.push({ name: 'ForceChangePassword' })
    } else {
      router.push({ name: 'Dashboard' })
    }
  } catch (e) {
    await nextTick()
    errorMsg.value = (e as Error).message || '登录失败，请重试'
  } finally {
    isLoading.value = false
  }
}
</script>
