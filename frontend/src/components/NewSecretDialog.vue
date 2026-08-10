<template>
  <Dialog v-model="show" :options="{ title: 'Add Secret', size: 'lg' }">
    <template #body-content>
      <div class="space-y-4">
        <FormControl label="Title" v-model="form.title" :required="true" placeholder="e.g. Gmail, AWS Console, Passport Scan" />

        <FormControl label="Secret Type" type="select" v-model="form.secret_type" :options="SECRET_TYPES" />

        <div class="grid grid-cols-2 gap-4">
          <FormControl label="Folder" type="select" v-model="form.folder" :options="folderOptions" :class="form.secret_type === 'Credit Card' ? 'col-span-2' : ''" />
          <FormControl v-if="form.secret_type !== 'Credit Card'" label="URL" v-model="form.url" placeholder="https://..." />
        </div>

        <!-- Password fields -->
        <template v-if="form.secret_type === 'Password'">
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Username" v-model="form.username" />
            <FormControl label="Email" v-model="form.email" type="email" />
          </div>
          <FormControl label="Password" v-model="form.password" :type="showSecrets ? 'text' : 'password'">
            <template #suffix>
              <Button variant="ghost" class="!p-1 h-auto text-ink-gray-5 hover:text-ink-gray-9" :icon="showSecrets ? 'lucide-eye-off' : 'lucide-eye'" @click="showSecrets = !showSecrets" />
            </template>
          </FormControl>
          <FormControl label="TOTP Secret (2FA Seed)" v-model="form.totp_secret" :type="showSecrets ? 'text' : 'password'" placeholder="Base32 format">
            <template #suffix>
              <Button variant="ghost" class="!p-1 h-auto text-ink-gray-5 hover:text-ink-gray-9" :icon="showSecrets ? 'lucide-eye-off' : 'lucide-eye'" @click="showSecrets = !showSecrets" />
            </template>
          </FormControl>
        </template>

        <!-- API Key fields -->
        <template v-if="form.secret_type === 'API Key'">
          <FormControl label="API Key" v-model="form.api_key" />
          <FormControl label="API Secret" v-model="form.api_secret" :type="showSecrets ? 'text' : 'password'">
            <template #suffix>
              <Button variant="ghost" class="!p-1 h-auto text-ink-gray-5 hover:text-ink-gray-9" :icon="showSecrets ? 'lucide-eye-off' : 'lucide-eye'" @click="showSecrets = !showSecrets" />
            </template>
          </FormControl>
          <FormControl label="TOTP Secret (2FA Seed)" v-model="form.totp_secret" :type="showSecrets ? 'text' : 'password'" placeholder="Base32 format">
            <template #suffix>
              <Button variant="ghost" class="!p-1 h-auto text-ink-gray-5 hover:text-ink-gray-9" :icon="showSecrets ? 'lucide-eye-off' : 'lucide-eye'" @click="showSecrets = !showSecrets" />
            </template>
          </FormControl>
        </template>

        <!-- Media / Multi-File Attachment fields -->
        <template v-if="form.secret_type === 'Media'">
          <div class="space-y-2 pt-1">
            <label class="block text-sm font-medium text-ink-gray-7">Document / Media Attachments</label>

            <!-- List of Uploaded Files -->
            <div v-if="attachmentList.length > 0" class="space-y-2">
              <div
                v-for="(fileUrl, idx) in attachmentList"
                :key="fileUrl + idx"
                class="p-2.5 rounded-xl border border-outline-gray-1 bg-surface-gray-2 flex items-center justify-between shadow-2xs"
              >
                <div class="flex items-center gap-3 overflow-hidden min-w-0">
                  <img
                    v-if="isImageUrl(fileUrl)"
                    :src="fileUrl"
                    class="w-10 h-10 object-cover rounded-lg shrink-0 border border-outline-gray-1 bg-surface-base"
                  />
                  <div v-else class="w-10 h-10 rounded-lg bg-surface-gray-3 border border-outline-gray-1 flex items-center justify-center shrink-0">
                    <FeatherIcon name="paperclip" class="w-5 h-5 text-ink-gray-7" />
                  </div>
                  <div class="min-w-0">
                    <p class="text-xs font-semibold text-ink-gray-9 truncate">{{ getFileName(fileUrl) }}</p>
                    <a :href="fileUrl" target="_blank" class="text-[11px] font-mono text-ink-gray-5 hover:text-blue-600 dark:hover:text-blue-400 hover:underline truncate block">{{ fileUrl }}</a>
                  </div>
                </div>

                <Button
                  variant="ghost"
                  size="xs"
                  icon="x"
                  class="!p-1 h-auto text-ink-gray-5 hover:text-ink-red-3 hover:bg-surface-gray-3 focus:outline-none"
                  title="Remove File"
                  @click.stop.prevent="removeAttachment(idx)"
                />
              </div>
            </div>

            <!-- Multi-File Upload Dropzone Trigger -->
            <div
              class="relative border-2 border-dashed border-outline-gray-2 rounded-xl p-4 text-center hover:border-ink-gray-6 transition-colors cursor-pointer bg-surface-gray-1"
              @click="triggerFileInput('attachment')"
            >
              <FormControl
                type="file"
                id="file_input_attachment"
                class="hidden"
                multiple
                accept="*/*"
                @change="handleFileUpload($event)"
              />
              <div class="flex flex-col items-center gap-1">
                <FeatherIcon name="paperclip" class="w-6 h-6 text-ink-gray-5" />
                <span class="text-xs font-semibold text-ink-gray-8">
                  {{ uploadingFiles ? 'Uploading files...' : (attachmentList.length > 0 ? '+ Add More Files' : 'Click or drag files here to upload') }}
                </span>
                <span class="text-[10px] text-ink-gray-5">Supports Images, PDFs, Zip, Documents (Select multiple files)</span>
              </div>
            </div>
          </div>
        </template>

        <!-- Credit Card fields -->
        <template v-if="form.secret_type === 'Credit Card'">
          <FormControl label="Card Holder" v-model="form.card_holder" />
          <div class="grid grid-cols-3 gap-4">
            <FormControl label="Card Number" v-model="form.card_number" :type="showSecrets ? 'text' : 'password'" class="col-span-2">
              <template #suffix>
                <Button variant="ghost" class="!p-1 h-auto text-ink-gray-5 hover:text-ink-gray-9" :icon="showSecrets ? 'lucide-eye-off' : 'lucide-eye'" @click="showSecrets = !showSecrets" />
              </template>
            </FormControl>
            <FormControl label="CVV" v-model="form.card_cvv" :type="showSecrets ? 'text' : 'password'">
              <template #suffix>
                <Button variant="ghost" class="!p-1 h-auto text-ink-gray-5 hover:text-ink-gray-9" :icon="showSecrets ? 'lucide-eye-off' : 'lucide-eye'" @click="showSecrets = !showSecrets" />
              </template>
            </FormControl>
          </div>
          <FormControl label="Expiry (MM/YY)" v-model="form.card_expiry" placeholder="12/28" />
        </template>

        <!-- Database fields -->
        <template v-if="form.secret_type === 'Database'">
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Host" v-model="form.db_host" />
            <FormControl label="Port" v-model="form.db_port" type="number" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <FormControl label="Database Name" v-model="form.db_name" />
            <FormControl label="Username" v-model="form.username" />
          </div>
          <FormControl label="Password" v-model="form.db_password" :type="showSecrets ? 'text' : 'password'">
            <template #suffix>
              <Button variant="ghost" class="!p-1 h-auto text-ink-gray-5 hover:text-ink-gray-9" :icon="showSecrets ? 'lucide-eye-off' : 'lucide-eye'" @click="showSecrets = !showSecrets" />
            </template>
          </FormControl>
        </template>

        <!-- SSH Key fields -->
        <template v-if="form.secret_type === 'SSH Key'">
          <FormControl label="Username" v-model="form.username" placeholder="root / ubuntu" />
          <FormControl label="SSH Private Key" type="textarea" v-model="form.ssh_private_key" :rows="5" placeholder="-----BEGIN OPENSSH PRIVATE KEY-----..." class="font-mono" />
        </template>

        <FormControl label="Notes" type="textarea" v-model="form.notes" :rows="3" />
      </div>
    </template>

    <template #actions>
      <Button variant="solid" @click="handleCreate" :loading="createResource.loading">Create</Button>
    </template>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Button, Dialog, FormControl, FeatherIcon, toast } from 'frappe-ui'
import { useCreateSecret, useFolders } from '../composables/vault'
import { SECRET_TYPES } from '../composables/constants'
import { cleanUrl, parseAttachments, isImageUrl, getFileName } from '../utils/attachments'

const props = defineProps({
  modelValue: Boolean,
  initialFolder: String,
})
const emit = defineEmits(['update:modelValue', 'created'])

const show = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const createResource = useCreateSecret()
const foldersResource = useFolders()

const folderOptions = computed(() => {
  const opts = [{ label: 'None', value: '' }]
  for (const f of foldersResource.data || []) {
    if (f.can_write) {
      opts.push({ label: f.folder_name, value: f.name })
    }
  }
  return opts
})

const defaultForm = () => ({
  title: '', secret_type: 'Password', folder: props.initialFolder || '', url: '', username: '', email: '',
  password: '', totp_secret: '', api_key: '', api_secret: '', ssh_private_key: '', attachment: '', notes: '', card_holder: '', card_number: '',
  card_expiry: '', card_cvv: '', db_host: '', db_port: '', db_name: '', db_password: '',
})

const form = ref(defaultForm())
const attachmentList = ref([])
const showSecrets = ref(false)
const uploadingFiles = ref(false)

watch(show, (v) => {
  if (v) {
    form.value = defaultForm()
    attachmentList.value = []
    showSecrets.value = false
  }
})

function removeAttachment(index) {
  attachmentList.value.splice(index, 1)
  syncAttachmentForm()
}

function syncAttachmentForm() {
  if (attachmentList.value.length === 0) {
    form.value.attachment = ''
  } else if (attachmentList.value.length === 1) {
    form.value.attachment = attachmentList.value[0]
  } else {
    form.value.attachment = JSON.stringify(attachmentList.value)
  }
}

async function handleFileUpload(event) {
  const files = Array.from(event.target.files || [])
  if (!files.length) return

  uploadingFiles.value = true
  try {
    for (const file of files) {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('is_private', 1)

      const response = await fetch('/api/method/upload_file', {
        method: 'POST',
        headers: {
          'X-Frappe-CSRF-Token': window.csrf_token || ''
        },
        body: formData
      })
      const data = await response.json()
      if (data.message && data.message.file_url) {
        attachmentList.value.push(data.message.file_url)
      }
    }
    syncAttachmentForm()
  } catch (err) {
    toast.error(err.message || 'File upload failed')
  } finally {
    uploadingFiles.value = false
  }
}

function triggerFileInput(fieldname) {
  const el = document.getElementById('file_input_' + fieldname)
  if (el) el.click()
}

async function handleCreate() {
  const result = await createResource.submit(form.value)
  emit('created', result)
}
</script>
