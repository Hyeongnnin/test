<template>
  <div class="p-4">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-xl font-semibold">나의 생성 문서</h2>
      <button @click="showCreate = !showCreate" class="px-3 py-1 bg-brand-600 text-white rounded">새 문서 생성</button>
    </div>

    <div v-if="showCreate" class="mb-4">
      <CreateDocumentForm @created="onCreated" @cancel="showCreate=false" />
    </div>

    <div v-if="loading" class="text-sm text-gray-500">로딩 중...</div>

    <div v-else>
      <ul class="space-y-3">
        <li v-for="d in docs" :key="d.id" class="p-3 border rounded flex justify-between items-center">
          <div>
            <div class="font-medium">{{ getTemplateName(d) }}</div>
            <div class="text-xs text-gray-500">상태: {{ d.status }} · 생성: {{ d.created_at }}</div>
          </div>
          <div class="flex gap-2">
            <button v-if="d.file_url" @click.prevent="openPreview(d.file_url)" class="px-3 py-1 bg-gray-100 rounded">파일 열기</button>
            <button @click="onEdit(d)" class="px-3 py-1 bg-gray-100 rounded">수정</button>
            <button @click="onDelete(d)" class="px-3 py-1 bg-red-100 rounded">삭제</button>
          </div>
        </li>
      </ul>
      <div v-if="docs.length === 0" class="text-sm text-gray-500 mt-3">생성한 문서가 없습니다.</div>
    </div>
  </div>
  <!-- Edit Modal -->
  <div v-if="showEdit" class="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
    <div class="bg-white p-4 rounded w-11/12 md:w-1/2">
      <h3 class="text-lg font-semibold mb-3">문서 수정</h3>
      <div class="mb-3">
        <label class="block text-sm font-medium mb-1">새 파일 (PDF)</label>
        <input type="file" @change="onEditFileChange" accept=".pdf,application/pdf" />
        <div v-if="editFileName" class="text-sm text-gray-600 mt-1">선택된 파일: {{ editFileName }}</div>
      </div>
      <div class="flex justify-end gap-2">
        <button @click="showEdit=false" class="px-3 py-1 bg-gray-100 rounded">취소</button>
        <button @click="saveEdit" class="px-3 py-1 bg-brand-600 text-white rounded">저장</button>
      </div>
    </div>
  </div>

  <!-- Preview Modal -->
  <div v-if="showPreview" class="fixed inset-0 bg-black bg-opacity-60 flex items-center justify-center z-50">
    <div class="bg-white w-11/12 h-5/6 rounded overflow-hidden">
      <div class="flex justify-between items-center p-2 border-b">
        <div class="font-medium">미리보기</div>
        <button @click="showPreview=false" class="px-2 py-1 bg-gray-100 rounded">닫기</button>
      </div>
      <iframe :src="previewUrl" class="w-full h-full" />
    </div>
  </div>

  <!-- Toast -->
  <div v-if="toast.message" :class="['fixed bottom-6 right-6 p-3 rounded shadow-lg text-white', toast.type === 'success' ? 'bg-green-600' : (toast.type === 'error' ? 'bg-red-600' : 'bg-gray-800')]">
    {{ toast.message }}
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchGenerated, fetchTemplates, GeneratedDocument, deleteGenerated, updateGenerated } from '../api'
import CreateDocumentForm from './CreateDocumentForm.vue'

const docs = ref<GeneratedDocument[]>([])
const templates = ref<any[]>([])
const loading = ref(true)
const showCreate = ref(false)
const showEdit = ref(false)
const editingDoc = ref<GeneratedDocument | null>(null)
const editFileRef = ref<File | null>(null)
const editFileName = ref('')
const toast = ref({ message: '', type: '' })
const showPreview = ref(false)
const previewUrl = ref('')

onMounted(async () => {
  await reload()
})

async function reload() {
  loading.value = true
  try {
    docs.value = await fetchGenerated()
    templates.value = await fetchTemplates()
  } catch (e) {
    console.error('문서 로드 실패', e)
    alert('문서를 불러오지 못했습니다. 로그인 상태를 확인하세요.')
  } finally {
    loading.value = false
  }
}

function getTemplateName(d: GeneratedDocument) {
  if (!d.template) return '템플릿 없음'
  if (typeof d.template === 'number') {
    const t = templates.value.find((x: any) => x.id === d.template)
    return t ? t.name : `템플릿 #${d.template}`
  }
  return (d.template as any).name || '템플릿'
}

function resolveFileUrl(url: string | undefined | null) {
  if (!url) return '#'
  if (url.startsWith('http')) return url
  // ensure absolute
  const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'
  const host = base.replace(/\/api\/?$/, '')
  return host + url
}



async function onDelete(d: GeneratedDocument) {
  if (!confirm('정말로 삭제하시겠습니까?')) return
  try {
    await deleteGenerated(d.id)
    showToast('삭제되었습니다.', 'success')
    await reload()
  } catch (e) {
    console.error('삭제 실패', e)
    showToast('삭제에 실패했습니다.', 'error')
  }
}

function onCreated(created: GeneratedDocument) {
  showCreate.value = false
  showToast('문서가 생성되었습니다.', 'success')
  reload()
}

function onEdit(d: GeneratedDocument) {
  editingDoc.value = d
  editFileRef.value = null
  editFileName.value = ''
  showEdit.value = true
}

function onEditFileChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files || input.files.length === 0) {
    editFileRef.value = null
    editFileName.value = ''
    return
  }
  const file = input.files[0]
  // only pdf
  if (!file.name.toLowerCase().endsWith('.pdf') && file.type !== 'application/pdf') {
    alert('PDF 파일만 업로드 가능합니다.')
    input.value = ''
    return
  }
  editFileRef.value = file
  editFileName.value = file.name
}

async function saveEdit() {
  if (!editingDoc.value) return
  const fd = new FormData()
  if (editFileRef.value) fd.append('file', editFileRef.value)
  try {
    await updateGenerated(editingDoc.value.id, fd)
    showEdit.value = false
    showToast('문서가 수정되었습니다.', 'success')
    await reload()
  } catch (e) {
    console.error('수정 실패', e)
    showToast('수정에 실패했습니다.', 'error')
  }
}

function showToast(message: string, type = 'info') {
  toast.value.message = message
  toast.value.type = type
  setTimeout(() => {
    toast.value.message = ''
    toast.value.type = ''
  }, 3000)
}

function openPreview(url: string | undefined | null) {
  if (!url) return
  previewUrl.value = resolveFileUrl(url)
  showPreview.value = true
}
</script>

<style scoped>
</style>
