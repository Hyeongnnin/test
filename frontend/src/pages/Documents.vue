<template>
  <section>
    <h2 class="text-2xl font-semibold mb-4">근로서류</h2>
    <div class="p-4 bg-white rounded shadow">
      <div class="mb-4">
        <button @click="tab = 'generated'" :class="buttonClass(tab === 'generated')">내 문서</button>
        <button @click="tab = 'templates'" :class="buttonClass(tab === 'templates')" class="ml-2">템플릿</button>
      </div>

      <div>
        <GeneratedDocuments v-if="tab === 'generated'" />
        <DocumentsTemplates v-else />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import GeneratedDocuments from '../components/GeneratedDocuments.vue'
import DocumentsTemplates from '../components/DocumentsTemplates.vue'

const tab = ref<'generated'|'templates'>('generated')

function buttonClass(active: boolean) {
  return [
    'px-3 py-1 rounded',
    active ? 'bg-brand-600 text-white' : 'bg-gray-100 text-gray-700'
  ].join(' ')
}
</script>

<style scoped>
</style>
