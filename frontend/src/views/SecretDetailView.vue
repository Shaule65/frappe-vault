<template>

  <div class="h-full w-full bg-surface-base text-ink-gray-9 flex flex-col">
    <!-- Split header using PageHeaderBase -->
            <PageHeaderBase class="flex h-12 border-b border-outline-gray-1 bg-surface-base shrink-0">
      <!-- Details Main Header (Left/Middle) -->
      <div :class="[showActivitySidebar ? 'hidden lg:flex' : 'flex', 'min-w-0 flex-1 items-center justify-between gap-3 px-3 lg:px-5 bg-surface-base']">
        <div class="flex min-w-0 items-center gap-2">
          <Button variant="ghost" icon="lucide-arrow-left" @click="router.push('/secrets')" />
          <div v-if="secretData" :class="`size-6 rounded-full flex items-center justify-center shrink-0 shadow-sm border border-outline-gray-1 ${typeMeta[secretData.secret_type || 'Other']?.bg}`">
            <FeatherIcon :name="typeMeta[secretData.secret_type || 'Other']?.icon || 'key'" class="w-3.5 h-3.5 text-ink-gray-7" />
          </div>
          <PageHeaderTitle v-if="secretData">{{ secretData.title }}</PageHeaderTitle>
          <div v-if="secretData" class="text-sm text-ink-gray-5 font-mono ml-2 cursor-copy hover:text-ink-gray-8" @click="copyToClipboard(secretData.name)" title="Copy ID">
            {{ secretData.name }}
          </div>
        </div>

        <div class="flex items-center gap-1 shrink-0">
          <Button v-if="canEdit" variant="ghost" :icon="isEditing ? 'lucide-eye' : 'lucide-edit'" :label="isEditing ? 'View' : 'Edit'" @click="toggleEditMode" />
          <Button v-if="canDelete" variant="ghost" icon="lucide-trash-2" theme="red" title="Delete" @click="showDeleteDialog = true" />
          <Button variant="ghost" :icon="showActivitySidebar ? 'lucide-panel-right-close' : 'lucide-panel-right'" title="Toggle Activity" @click="showActivitySidebar = !showActivitySidebar" />
        </div>
      </div>

      <!-- Activity Sidebar Header (Right) -->
      <div v-show="showActivitySidebar" class="flex w-full lg:w-1/2 shrink-0 items-center justify-between lg:border-l border-outline-gray-1 px-3 lg:px-4 bg-surface-base">
        <div class="flex items-center gap-2">
          <Button class="lg:hidden" variant="ghost" icon="lucide-arrow-left" @click="showActivitySidebar = false" />
          <PageHeaderTitle>Sharing & Activity</PageHeaderTitle>
        </div>
      </div>
    </PageHeaderBase>

    <div v-if="secretData" class="flex min-h-0 flex-1">
      <!-- Reading pane (Left side: Details) -->
      <section :class="[showActivitySidebar ? 'hidden lg:flex' : 'flex', 'h-full min-h-0 min-w-0 flex-1 flex-col bg-surface-gray-2/20']">


        <ScrollArea class="min-h-0 flex-1">
          <div class="space-y-6 px-5 py-6">
            
            <article class="space-y-2">
              <div class="flex items-center justify-between cursor-pointer select-none group" @click="detailsOpen = !detailsOpen">
                <h3 class="text-xs font-semibold text-ink-gray-5 uppercase tracking-wider group-hover:text-ink-gray-7 transition-colors">Secret Data</h3>
                <FeatherIcon name="chevron-down" class="w-4 h-4 text-ink-gray-4 transition-transform duration-200" :class="{ '-rotate-90': !detailsOpen }" />
              </div>
              <div v-show="detailsOpen" class="space-y-4 pt-2">
                <!-- EDIT VIEW FORM -->
              <div v-if="isEditing" class="space-y-4 pt-1 px-6">
                <!-- Title -->
                <div class="flex items-center justify-between gap-3 text-sm">
                  <label class="w-28 shrink-0 text-ink-gray-5 font-normal">Title <span class="text-ink-red-3">*</span></label>
                  <div class="flex-1 min-w-0">
                    <TextInput v-model="editForm.title" placeholder="Secret Title" class="w-full text-sm" />
                  </div>
                </div>

                <!-- Type select -->
                <div class="flex items-center justify-between gap-3 text-sm">
                  <label class="w-28 shrink-0 text-ink-gray-5 font-normal">Type</label>
                  <div class="flex-1 min-w-0">
                    <FormControl v-model="editForm.secret_type" type="select" :options="secretTypeOptions" class="w-full text-sm cursor-pointer" />
                  </div>
                </div>

                <!-- Folder select -->
                <div class="flex items-center justify-between gap-3 text-sm">
                  <label class="w-28 shrink-0 text-ink-gray-5 font-normal">Folder</label>
                  <div class="flex-1 min-w-0">
                    <FormControl v-model="editForm.folder" type="select" :options="folderOptions" class="w-full text-sm cursor-pointer" />
                  </div>
                </div>

                <div class="w-full border-t border-outline-gray-1 my-2" />

                <!-- Dynamic type inputs -->
                <div class="space-y-3">
                  <template v-for="field in secretFieldsConfig[editForm.secret_type] || []" :key="field.name">
                    <!-- Textarea -->
                    <div v-if="field.type === 'textarea'" class="pt-1">
                      <FormControl type="textarea" :label="field.label" v-model="editForm[field.name]" :rows="5" :placeholder="field.placeholder" class="w-full text-xs" :class="field.mono ? 'font-mono' : ''" />
                    </div>

                    <!-- File Attachment Edit Input (Multi-File Support) -->
                    <div v-else-if="field.type === 'file'" class="space-y-2 pt-1">
                      <label class="block text-xs font-semibold text-ink-gray-5 uppercase tracking-wider">{{ field.label }}</label>

                      <!-- List of Attached Files in Edit Mode -->
                      <div v-if="editAttachmentList.length > 0" class="space-y-2">
                        <div
                          v-for="(fileUrl, fIdx) in editAttachmentList"
                          :key="fileUrl + fIdx"
                          class="p-2.5 rounded-xl border border-outline-gray-1 bg-surface-gray-2 flex items-center justify-between shadow-2xs"
                        >
                          <div class="flex items-center gap-3 overflow-hidden min-w-0">
                            <img
                              v-if="isImageUrl(fileUrl)"
                              :src="fileUrl"
                              class="w-10 h-10 object-cover rounded-lg shrink-0 border border-outline-gray-1 bg-surface-base cursor-pointer"
                              @click="openImagePreview(fileUrl)"
                            />
                            <div v-else class="w-10 h-10 rounded-lg bg-surface-gray-3 border border-outline-gray-1 flex items-center justify-center shrink-0">
                              <FeatherIcon name="paperclip" class="w-5 h-5 text-ink-gray-7" />
                            </div>
                            <div class="min-w-0">
                              <p class="text-xs font-semibold text-ink-gray-9 truncate">{{ getFileName(fileUrl) }}</p>
                              <p class="text-[11px] text-ink-gray-5 font-mono truncate">{{ fileUrl }}</p>
                            </div>
                          </div>

                          <Button
                            variant="ghost"
                            size="xs"
                            icon="x"
                            class="!p-1 h-auto text-ink-gray-5 hover:text-ink-red-3 hover:bg-surface-gray-3 focus:outline-none"
                            title="Remove file"
                            @click.stop.prevent="removeEditAttachment(fIdx)"
                          />
                        </div>
                      </div>

                      <!-- Upload Drag & Drop Trigger -->
                      <div
                        class="relative border-2 border-dashed border-outline-gray-2 rounded-xl p-4 text-center hover:border-ink-gray-6 transition-colors cursor-pointer bg-surface-gray-1"
                        @click="triggerEditFileInput(field.name)"
                      >
                        <FormControl
                          type="file"
                          :id="'edit_file_input_' + field.name"
                          class="hidden"
                          multiple
                          accept="*/*"
                          @change="handleEditFileUpload($event, field.name)"
                        />
                        <div class="flex flex-col items-center gap-1">
                          <FeatherIcon name="paperclip" class="w-6 h-6 text-ink-gray-5" />
                          <span class="text-xs font-semibold text-ink-gray-8">
                            {{ uploadingEditFiles ? 'Uploading files...' : (editAttachmentList.length > 0 ? '+ Add More Files' : 'Click or drag files here to upload') }}
                          </span>
                          <span class="text-[10px] text-ink-gray-5">Supports Images, PDFs, Zip, Documents (Select multiple files)</span>
                        </div>
                      </div>
                    </div>

                    <!-- Text / Password / URL -->
                    <div v-else class="flex items-center justify-between gap-3 text-sm">
                      <label class="w-28 shrink-0 text-ink-gray-5 font-normal">{{ field.label }}</label>
                      <div class="flex-1 min-w-0 relative">
                        <TextInput :type="field.type === 'password' && !editRevealedFields[field.name] ? 'password' : 'text'" v-model="editForm[field.name]" :placeholder="field.placeholder" class="w-full text-sm" :class="[field.mono ? 'font-mono' : '', field.type === 'password' ? 'pr-9' : '']" />
                        <Button v-if="field.type === 'password'" variant="ghost" :icon="editRevealedFields[field.name] ? 'lucide-eye-off' : 'lucide-eye'" class="absolute right-1 top-1 !p-1.5 h-auto text-ink-gray-4 hover:text-ink-gray-9 focus:outline-none" @click="toggleField(field.name, true)" />
                      </div>
                    </div>
                  </template>
                </div>

                <!-- Notes input -->
                <div class="pt-2">
                  <FormControl type="textarea" label="Notes" v-model="editForm.notes" :rows="3" placeholder="Enter notes..." class="w-full text-sm" />
                </div>

                <!-- Edit Action Buttons -->
                <div class="flex items-center justify-end gap-2 pt-4 border-t border-outline-gray-1">
                  <Button variant="outline" size="sm" @click="isEditing = false">Cancel</Button>
                  <Button variant="solid" size="sm" @click="handleSave" :loading="updateResource.loading" class="font-semibold shadow-2xs">Save Changes</Button>
                </div>
              </div>

              <!-- READ ONLY VIEW -->
              <div v-else class="space-y-2.5 py-1">
                <!-- Secret Type -->
                <div class="flex items-center justify-between py-1 text-sm">
                  <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Secret Type</span>
                  <span class="min-w-0 flex-1 text-right font-medium text-ink-gray-9 truncate">{{ secretData.secret_type }}</span>
                </div>

                <!-- Folder -->
                <div class="flex items-center justify-between py-1 text-sm">
                  <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Folder</span>
                  <span class="min-w-0 flex-1 text-right font-medium text-ink-gray-9 truncate">
                    {{ getFolderName(secretData.folder) || '—' }}
                  </span>
                </div>

                <!-- Dynamic Fields Array -->
                <template v-for="field in secretFieldsConfig[secretData.secret_type] || []" :key="field.name">
                  <!-- File Attachment View Mode -->
                  <div v-if="field.type === 'file'" class="pt-3 space-y-3">
                    <div class="flex items-center justify-between">
                      <span class="block text-xs font-semibold text-ink-gray-5 uppercase tracking-wider">{{ field.label }}</span>
                      <span v-if="parseAttachments(secretData[field.name]).length > 0" class="text-xs font-medium text-ink-gray-5">
                        {{ parseAttachments(secretData[field.name]).length }} {{ parseAttachments(secretData[field.name]).length === 1 ? 'file' : 'files' }}
                      </span>
                    </div>
                    
                    <div v-if="parseAttachments(secretData[field.name]).length > 0" class="space-y-2 max-h-96 overflow-y-auto pr-1">
                      <div
                        v-for="(fileUrl, aIdx) in parseAttachments(secretData[field.name])"
                        :key="fileUrl + aIdx"
                        class="bg-surface-gray-2 border border-outline-gray-1 rounded-xl p-3 flex items-center justify-between gap-3 hover:border-outline-gray-2 transition-colors shadow-2xs"
                      >
                        <div class="flex items-center gap-3 overflow-hidden min-w-0 cursor-pointer" @click="isImageUrl(fileUrl) && !imageLoadErrorMap[fileUrl] ? openImagePreview(fileUrl) : openFileUrl(fileUrl)">
                          <img
                            v-if="isImageUrl(fileUrl) && !imageLoadErrorMap[fileUrl]"
                            :src="fileUrl"
                            class="w-10 h-10 object-cover rounded-lg shrink-0 border border-outline-gray-1 bg-surface-base hover:opacity-90 transition-opacity"
                            @error="imageLoadErrorMap[fileUrl] = true"
                          />
                          <div v-else class="w-10 h-10 rounded-lg bg-surface-gray-3 border border-outline-gray-1 flex items-center justify-center shrink-0">
                            <FeatherIcon name="file-text" class="w-5 h-5 text-ink-gray-7" />
                          </div>
                          <div class="min-w-0">
                            <p class="text-xs font-semibold text-ink-gray-9 truncate hover:text-ink-blue-link transition-colors">{{ getFileName(fileUrl) }}</p>
                            <p class="text-[11px] text-ink-gray-5 font-mono truncate">{{ fileUrl }}</p>
                          </div>
                        </div>

                        <div class="flex items-center gap-1.5 shrink-0">
                          <Button
                            v-if="isImageUrl(fileUrl) && !imageLoadErrorMap[fileUrl]"
                            variant="subtle"
                            size="xs"
                            icon="eye"
                            label="Preview"
                            class="font-medium text-xs shadow-2xs"
                            @click="openImagePreview(fileUrl)"
                          />

                          <a
                            v-if="canCopy"
                            :href="fileUrl"
                            target="_blank"
                            download
                            class="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg text-xs font-medium bg-surface-base border border-outline-gray-2 text-ink-gray-8 hover:bg-surface-gray-1 transition-colors shadow-2xs"
                          >
                            <FeatherIcon name="download" class="w-3.5 h-3.5 text-ink-gray-6" /> Download
                          </a>
                        </div>
                      </div>
                    </div>

                    <div v-else class="text-xs text-ink-gray-4 italic py-1">No files attached.</div>
                  </div>

                  <div v-else-if="secretData[field.name] || field.type === 'password'" :class="field.type === 'textarea' ? 'pt-2' : 'flex items-center justify-between py-1 text-sm'">
                    <span v-if="field.type === 'textarea'" class="block text-xs font-semibold text-ink-gray-5 uppercase tracking-wider mb-1.5">{{ field.label }}</span>
                    <span v-else class="w-28 shrink-0 text-ink-gray-5 font-normal">{{ field.label }}</span>
                    
                    <!-- Textarea Content -->
                    <div v-if="field.type === 'textarea'" class="relative bg-surface-gray-2 border border-outline-gray-1 rounded-xl p-3 group shadow-inner">
                      <pre class="text-xs font-mono text-ink-gray-8 overflow-x-auto max-h-36 whitespace-pre select-all leading-normal">{{ secretData[field.name] }}</pre>
                      <Button v-if="canCopy" variant="ghost" :icon="copiedField === field.name ? 'lucide-check' : 'lucide-copy'" :class="copiedField === field.name ? 'text-ink-green-3 hover:text-ink-green-4' : 'text-ink-gray-7'" class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity bg-surface-base border border-outline-gray-1 shadow-2xs text-xs font-medium h-auto !py-1 !px-2 rounded-md" label="Copy" @click="copyFieldData(field.name)" />
                    </div>

                    <!-- URL Link -->
                    <div v-else-if="field.isLink" class="min-w-0 flex-1 flex items-center justify-end gap-1.5 overflow-hidden">
                      <a :href="secretData[field.name]" target="_blank" class="min-w-0 font-medium text-ink-blue-link hover:underline truncate inline-flex items-center justify-end gap-1">
                        <span class="truncate">{{ secretData[field.name] }}</span>
                        <FeatherIcon name="external-link" class="w-3.5 h-3.5 shrink-0 text-ink-blue-link" />
                      </a>
                      <Button
                        v-if="canCopy"
                        variant="ghost"
                        :icon="copiedField === field.name ? 'lucide-check' : 'lucide-copy'"
                        :class="copiedField === field.name ? 'text-ink-green-3 hover:text-ink-green-4' : 'text-ink-gray-4 hover:text-ink-gray-9'"
                        class="!p-1 h-auto focus:outline-none shrink-0"
                        :title="'Copy ' + field.label"
                        @click="copyFieldData(field.name)"
                      />
                    </div>

                    <!-- Password/Hidden Field -->
                    <div v-else-if="field.type === 'password'" class="min-w-0 flex-1 flex items-center justify-end gap-2">
                      <span class="font-mono tracking-wider font-medium text-ink-gray-9 truncate">
                        {{ revealedFields[field.name] ? decryptedData?.[field.name] : (field.name === 'card_number' ? '•••• •••• •••• ••••' : (field.name === 'card_cvv' ? '•••' : '••••••••••••')) }}
                      </span>
                      <div class="flex items-center gap-0.5 shrink-0">
                        <Button variant="ghost" :icon="revealedFields[field.name] ? 'lucide-eye-off' : 'lucide-eye'" class="!p-1 h-auto text-ink-gray-4 hover:text-ink-gray-9 focus:outline-none" :title="'Reveal ' + field.label" @click="toggleField(field.name)" />
                        <Button v-if="canCopy" variant="ghost" :icon="copiedField === field.name ? 'lucide-check' : 'lucide-copy'" :class="copiedField === field.name ? 'text-ink-green-3 hover:text-ink-green-4' : 'text-ink-gray-4 hover:text-ink-gray-9'" class="!p-1 h-auto focus:outline-none" :title="'Copy ' + field.label" @click="copyFieldData(field.name)" />
                      </div>
                    </div>

                    <!-- Standard Text Field -->
                    <div v-else class="min-w-0 flex-1 flex items-center justify-end gap-1.5 overflow-hidden">
                      <span class="min-w-0 font-medium text-ink-gray-9 truncate" :class="field.mono ? 'font-mono' : ''">
                        {{ field.name === 'db_host' ? secretData.db_host + (secretData.db_port ? ':' + secretData.db_port : '') : secretData[field.name] }}
                      </span>
                      <Button
                        v-if="canCopy"
                        variant="ghost"
                        :icon="copiedField === field.name ? 'lucide-check' : 'lucide-copy'"
                        :class="copiedField === field.name ? 'text-ink-green-3 hover:text-ink-green-4' : 'text-ink-gray-4 hover:text-ink-gray-9'"
                        class="!p-1 h-auto focus:outline-none shrink-0"
                        :title="'Copy ' + field.label"
                        @click="copyFieldData(field.name)"
                      />
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </article>

          <div v-if="secretData.notes" class="h-px w-full bg-outline-gray-2" />

            <article v-if="secretData.notes" class="space-y-2">
              <div class="flex items-center justify-between cursor-pointer select-none group" @click="notesOpen = !notesOpen">
                <h3 class="text-xs font-semibold text-ink-gray-5 uppercase tracking-wider group-hover:text-ink-gray-7 transition-colors">Notes</h3>
                <FeatherIcon name="chevron-down" class="w-4 h-4 text-ink-gray-4 transition-transform duration-200" :class="{ '-rotate-90': !notesOpen }" />
              </div>
              <div v-show="notesOpen" class="mt-2.5 py-1 text-sm text-ink-gray-8 leading-relaxed whitespace-pre-wrap font-normal" v-html="secretData.notes" />
            </article>

            <div class="h-px w-full bg-outline-gray-2" />

            <article class="space-y-2">
              <div class="flex items-center justify-between cursor-pointer select-none group" @click="metaOpen = !metaOpen">
                <h3 class="text-xs font-semibold text-ink-gray-5 uppercase tracking-wider group-hover:text-ink-gray-7 transition-colors">Metadata</h3>
                <FeatherIcon name="chevron-down" class="w-4 h-4 text-ink-gray-4 transition-transform duration-200" :class="{ '-rotate-90': !metaOpen }" />
              </div>
              <div v-show="metaOpen" class="mt-3 space-y-2.5 py-1">
                <div v-if="secretData.secret_type === 'Password' && secretData.password_strength" class="flex items-center justify-between py-1 text-sm">
                  <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Strength</span>
                  <div class="min-w-0 flex-1 flex justify-end">
                    <StrengthBadge :strength="secretData.password_strength" size="sm" />
                  </div>
                </div>
                
                <div class="flex items-center justify-between py-1 text-sm">
                  <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Last Accessed</span>
                  <span class="min-w-0 flex-1 text-right font-medium text-ink-gray-9 truncate">{{ formatDateOnly(secretData.last_accessed) }}</span>
                </div>
                
                <div class="flex items-center justify-between py-1 text-sm">
                  <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Access Count</span>
                  <span class="min-w-0 flex-1 text-right font-medium text-ink-gray-9 truncate">{{ secretData.access_count || 0 }} times</span>
                </div>

                <div class="flex items-center justify-between py-1 text-sm">
                  <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Last Changed</span>
                  <span class="min-w-0 flex-1 text-right font-medium text-ink-gray-9 truncate">{{ formatDateOnly(secretData.password_last_changed) }}</span>
                </div>
              </div>
            </article>

          </div>
        </ScrollArea>
      </section>

      <!-- Message list pane (Right side: Tabs) -->
      <section v-show="showActivitySidebar" class="flex h-full min-h-0 w-full lg:w-1/2 shrink-0 flex-col lg:border-l border-outline-gray-1 bg-surface-base">
        <!-- Category tabs pinned above -->
        <div class="flex shrink-0 items-center border-b border-outline-gray-1 px-4 py-2">
          <TabButtons
            v-model="activeTabLabel"
            :options="[{ label: 'Sharing' }, { label: 'Activity' }]"
          />
        </div>

        <ScrollArea class="min-h-0 flex-1" viewport-class="p-0">
          <div v-if="activeTabLabel === 'Activity'">
            <div class="px-6 py-5">
              <div class="w-full pt-1">
                <div class="flex items-center justify-between mb-6 pb-2.5 border-b border-outline-gray-1">
                  <h2 class="text-base font-bold text-ink-gray-9">Activity</h2>
                  <Button variant="ghost" icon="lucide-refresh-cw" size="sm" @click="activity.reload()" title="Refresh Activity" />
                </div>

                <div v-if="activity.loading" class="space-y-4">
                  <div v-for="i in 3" :key="i" class="h-14 bg-surface-gray-2 border border-outline-gray-1 rounded-xl animate-pulse" />
                </div>
                
                <div v-else-if="activityList.length" class="relative space-y-6 before:absolute before:top-2 before:bottom-2 before:left-2.5 before:w-px before:bg-outline-gray-2 py-1">
                  <div v-for="item in activityList" :key="item.name" class="relative flex items-start gap-3.5">
                    <!-- Clean icon without background/border/shadow -->
                    <div class="w-5 h-5 flex items-center justify-center shrink-0 relative text-ink-gray-5 bg-surface-base mt-0.5">
                      <FeatherIcon :name="actionIcons[item.action] || 'activity'" class="w-4 h-4" />
                    </div>
                    <!-- Content aligned with right-aligned timestamp -->
                    <div class="min-w-0 flex-1 flex flex-col gap-1.5">
                      <div class="flex items-start justify-between w-full gap-4">
                        <div class="text-sm leading-relaxed text-ink-gray-8">
                          <span class="font-bold text-ink-gray-9">{{ item.user }}</span>
                          <span class="text-ink-gray-6 ml-1.5">{{ getActionMainText(item) }}</span>
                        </div>
                        <span class="ml-auto text-xs text-ink-gray-4 shrink-0 whitespace-nowrap text-right pt-0.5">{{ formatRelativeTime(item.timestamp) }}</span>
                      </div>
                      
                      <!-- Activity Details Card / Bubble (matching CRM lead comment box) -->
                      <div v-if="hasActivityDetails(item)" class="mt-1.5 p-3 rounded-lg bg-surface-gray-2 border border-outline-gray-1 text-sm text-ink-gray-8 leading-relaxed w-full font-normal shadow-2xs">
                        {{ getActivityDetailText(item) }}
                      </div>
                    </div>
                  </div>
                </div>
                
                <EmptyState v-else icon="activity" title="No activity recorded" />
              </div>
            </div>
          </div>
          <div v-if="activeTabLabel === 'Sharing'">
            <div class="px-6 py-5">
              <div class="space-y-5 w-full">
                <div class="flex items-center justify-between border-b border-outline-gray-1 pb-3 shrink-0">
                  <h3 class="text-base font-semibold text-ink-gray-9">Sharing Settings</h3>
                  
                  <!-- Share Secret Button (Visible if Owner or Admin) -->
                  <Button
                    v-if="isOwnerOrAdmin"
                    variant="solid"
                    size="sm"
                    class="shadow-sm font-semibold"
                    iconLeft="lucide-user-plus"
                    label="Share Secret"
                    @click="openShareDialog"
                  />
                </div>

                <!-- If Not Owner or Admin, show who shared it with them -->
                <div v-if="!isOwnerOrAdmin" class="p-4 bg-surface-gray-2 border border-outline-gray-1 rounded-xl text-sm leading-relaxed text-ink-gray-7 font-medium shadow-sm flex items-start gap-3">
                  <div class="w-9 h-9 rounded-full bg-surface-gray-3 border border-outline-gray-1 flex items-center justify-center shrink-0 text-ink-gray-7">
                    <FeatherIcon name="share-2" class="w-4.5 h-4.5" />
                  </div>
                  <div>
                    <p class="font-bold text-ink-gray-9 leading-normal">Shared Secret Access</p>
                    <p class="mt-1 text-ink-gray-6 font-normal">
                      This secret was shared with you by <strong class="text-ink-gray-8">{{ secretData.shared_by || secretData.owner }}</strong>. You have <strong class="text-ink-gray-8">{{ secretData.permission_level || 'View Only' }}</strong> rights on this secret.
                    </p>
                  </div>
                </div>

                <div v-else class="space-y-4">
                  <!-- Active Shares List -->
                  <div class="text-xs font-bold text-ink-gray-5 uppercase tracking-wider pl-0.5">Active Shares</div>

                  <div v-if="sharesList.length" class="space-y-3">
                    <div
                      v-for="item in sharesList"
                      :key="item.name"
                      class="flex items-center justify-between p-3.5 bg-surface-elevation-1 border border-outline-gray-1 rounded-xl shadow-sm hover:border-outline-gray-3 transition-colors"
                    >
                      <div class="flex items-center gap-3.5 min-w-0">
                        <div class="w-9 h-9 rounded-full bg-surface-gray-2 border border-outline-gray-1 shadow-2xs flex items-center justify-center shrink-0">
                          <FeatherIcon
                            :name="item.share_type === 'UserGroup' || item.user_count > 1 ? 'users' : (item.share_type === 'Role' ? 'shield' : 'user')"
                            class="w-4.5 h-4.5 text-ink-gray-5"
                          />
                        </div>
                        <div class="min-w-0">
                          <div class="flex items-center gap-1.5 min-w-0">
                            <p class="text-sm font-semibold text-ink-gray-9 truncate leading-snug">
                              {{ item.share_type === 'User' ? item.user : (item.share_type === 'UserGroup' ? item.user : item.frappe_role) }}
                            </p>
                            <Button
                              v-if="item.share_type === 'Role'"
                              variant="ghost"
                              size="sm"
                              class="!h-6 !px-1.5 text-xs text-ink-blue-link hover:underline shrink-0"
                              title="View role members"
                              @click="openRoleUsersModal(item.frappe_role)"
                            >
                              View Members
                            </Button>
                            <Button
                              v-else-if="item.share_type === 'UserGroup' || item.user_count > 1"
                              variant="ghost"
                              size="sm"
                              class="!h-6 !px-1.5 text-xs text-ink-blue-link hover:underline shrink-0"
                              title="View shared users"
                              @click="openUserGroupModal(item)"
                            >
                              View Members
                            </Button>
                          </div>
                          <p class="text-xs text-ink-gray-4 mt-1 font-medium flex items-center gap-1.5 leading-none">
                            <span>{{ item.share_type }}</span>
                            <span class="w-1 h-1 rounded-full bg-surface-gray-4" />
                            <span v-if="item.expires_on">Expires {{ formatTime(item.expires_on) }}</span>
                            <span v-else>Never expires</span>
                          </p>
                        </div>
                      </div>

                      <div class="flex items-center gap-3 shrink-0">
                        <Dropdown
                          v-if="!item.is_revoked && isOwnerOrAdmin"
                          :options="[
                            { label: 'View Only', onClick: () => handleUpdateSharePermission(item.name, 'View Only') },
                            { label: 'View & Copy', onClick: () => handleUpdateSharePermission(item.name, 'View & Copy') },
                            { label: 'Edit', onClick: () => handleUpdateSharePermission(item.name, 'Edit') },
                            { label: 'Full Control', onClick: () => handleUpdateSharePermission(item.name, 'Full Control') }
                          ]"
                        >
                          <Badge
                            :theme="permissionTheme[item.permission_level] || 'gray'"
                            variant="subtle"
                            size="sm"
                            class="cursor-pointer hover:opacity-80 transition-opacity"
                            title="Click to update permission level"
                          >
                            {{ item.permission_level }} ▾
                          </Badge>
                        </Dropdown>
                        <Badge
                          v-else
                          :theme="item.is_revoked ? 'red' : (permissionTheme[item.permission_level] || 'gray')"
                          variant="subtle"
                          size="sm"
                        >
                          {{ item.is_revoked ? 'Revoked' : item.permission_level }}
                        </Badge>

                        <!-- Revoke Access Action -->
                        <Button
                          v-if="!item.is_revoked"
                          variant="ghost"
                          icon="lucide-trash-2"
                          class="!p-1.5 h-auto text-ink-gray-4 hover:!text-ink-red-3 hover:!bg-surface-red-2"
                          title="Revoke Access"
                          @click="confirmRevokeShare(item)"
                        />
                      </div>
                    </div>
                  </div>

                  <!-- Active Shares Empty State -->
                  <div v-else class="p-8 bg-surface-gray-2 border border-dashed border-outline-gray-1 rounded-2xl text-center shadow-sm">
                    <div class="w-10 h-10 rounded-full bg-surface-gray-3 border border-outline-gray-1 flex items-center justify-center mx-auto text-ink-gray-4 mb-3 shrink-0">
                      <FeatherIcon name="users" class="w-5 h-5" />
                    </div>
                    <p class="text-sm font-semibold text-ink-gray-9 leading-snug">Not Shared Yet</p>
                    <p class="text-xs text-ink-gray-5 mt-1 max-w-[280px] mx-auto leading-normal font-medium">
                      This secret is private. Use the Share button to give access to other users or roles.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </ScrollArea>
      </section>
    </div>

    <!-- Empty Loading State -->
    <div v-else class="flex-1 flex items-center justify-center bg-surface-base">
      <div class="h-8 w-8 border-2 border-ink-blue-3 border-t-transparent rounded-full animate-spin" />
    </div>

    <!-- Delete Confirmation Dialog (matching CRM/Frappe UI styles) -->
    <Dialog
      v-model="showDeleteDialog"
      :options="{
        title: 'Delete Secret',
        size: 'sm',
      }"
    >
      <template #body-content>
        <div class="space-y-3">
          <p class="text-sm text-ink-gray-6 mt-1 leading-normal">
            Are you sure you want to permanently delete <strong>{{ secretData?.title }}</strong>? This action cannot be undone.
          </p>
          <ErrorMessage v-if="deleteError" :message="deleteError" />
        </div>
      </template>
      <template #actions>
        <div class="flex items-center justify-end gap-2 px-4 pb-4">
          <Button variant="outline" @click="showDeleteDialog = false" class="text-ink-gray-7 hover:bg-surface-gray-2">
            Cancel
          </Button>
          <Button variant="solid" theme="red" @click="confirmDelete" :loading="deleteResource.loading" class="font-semibold shadow-sm px-4">
            Delete
          </Button>
        </div>
      </template>
    </Dialog>



    <!-- Share Secret Dialog -->
    <Dialog
      v-model="showShareDialog"
      :options="{
        title: 'Share Secret',
        size: 'sm',
      }"
    >
      <template #body-content>
        <div class="space-y-4">
          <!-- Share Type Selection -->
          <div>
            <label class="block text-p-sm-medium text-ink-gray-7 mb-1.5">Share Type</label>
            <TabButtons
              v-model="newShareType"
              :options="[
                { label: 'User', value: 'User', class: 'flex-1 !justify-center', onClick: () => { newShareRecipient = '' } },
                { label: 'Role', value: 'Role', class: 'flex-1 !justify-center', onClick: () => { newShareRecipient = '' } }
              ]"
              class="w-full !flex"
            />
          </div>

          <!-- Recipient Selection: MultiSelect Component vs Single Role Select -->
          <div v-if="newShareType === 'User'" class="space-y-1.5">
            <label class="block text-p-sm-medium text-ink-gray-7">Select Users</label>
            <MultiSelect
              v-model="selectedUserEmails"
              :options="userMembers"
              placeholder="Select users to share with…"
              class="w-full"
            >
              <template #prefix>
                <div v-if="visibleSelected.length" class="flex -space-x-1.5">
                  <Avatar
                    v-for="m in visibleSelected"
                    :key="m.value"
                    :image="m.image"
                    :label="m.label"
                    size="sm"
                  />
                  <span
                    v-if="overflowCount > 0"
                    class="z-10 grid size-5 place-items-center rounded-full bg-surface-gray-3 text-p-xs-medium text-ink-gray-7"
                  >
                    +{{ overflowCount }}
                  </span>
                </div>
                <FeatherIcon v-else name="users" class="w-4 h-4 text-ink-gray-5" />
              </template>

              <template #summary="{ selectedOptions, summary }">
                <template v-if="selectedOptions.length">
                  {{ selectedOptions.map((o) => o.label).join(', ') }}
                </template>
                <template v-else>{{ summary }}</template>
              </template>

              <template #item-prefix="{ item }">
                <Avatar :image="item.image" :label="item.label" size="sm" />
              </template>

              <template #item-label="{ item }">
                <div class="min-w-0 flex items-center justify-between w-full">
                  <div class="truncate font-medium text-ink-gray-9 text-xs">{{ item.label }}</div>
                  <div class="truncate text-[11px] text-ink-gray-5 font-mono ml-2">{{ item.value }}</div>
                </div>
              </template>
            </MultiSelect>
          </div>

          <!-- Role Selection: MultiSelect Component -->
          <div v-else class="space-y-1.5">
            <label class="block text-p-sm-medium text-ink-gray-7">Select Roles</label>
            <MultiSelect
              v-model="selectedRoles"
              :options="roleMembers"
              placeholder="Select roles to share with…"
              class="w-full"
            >
              <template #prefix>
                <div v-if="visibleSelectedRoles.length" class="flex -space-x-1.5">
                  <span
                    v-for="r in visibleSelectedRoles"
                    :key="r.value"
                    class="z-10 inline-flex items-center justify-center px-1.5 py-0.5 rounded bg-surface-blue-2 text-ink-blue-link text-xs font-medium border border-outline-blue-1"
                  >
                    {{ r.label }}
                  </span>
                  <span
                    v-if="overflowRoleCount > 0"
                    class="z-10 grid size-5 place-items-center rounded-full bg-surface-gray-3 text-p-xs-medium text-ink-gray-7"
                  >
                    +{{ overflowRoleCount }}
                  </span>
                </div>
                <FeatherIcon v-else name="shield" class="w-4 h-4 text-ink-gray-5" />
              </template>

              <template #summary="{ selectedOptions, summary }">
                <template v-if="selectedOptions.length">
                  {{ selectedOptions.map((o) => o.label).join(', ') }}
                </template>
                <template v-else>{{ summary }}</template>
              </template>

              <template #item-label="{ item }">
                <div class="min-w-0 flex items-center justify-between w-full">
                  <div class="truncate font-medium text-ink-gray-9 text-xs">{{ item.label }}</div>
                </div>
              </template>
            </MultiSelect>
          </div>

          <!-- Permission Level Selection -->
          <FormControl
            label="Permission Level"
            type="select"
            v-model="newSharePermission"
            :options="[
              { label: 'View Only', value: 'View Only' },
              { label: 'View & Copy', value: 'View & Copy' },
              { label: 'Edit', value: 'Edit' },
              { label: 'Full Control', value: 'Full Control' }
            ]"
          />

          <!-- Optional Expiration Date -->
          <FormControl
            label="Expires On (Optional)"
            type="datetime-local"
            v-model="newShareExpiresOn"
          />
        </div>
      </template>
      <template #actions>
        <Button variant="ghost" label="Cancel" @click="showShareDialog = false" class="text-ink-gray-7 focus:outline-none" />
        <Button
          variant="solid"
          label="Share"
          :loading="isSharing"
          :disabled="newShareType === 'User' ? selectedUserEmails.length === 0 : selectedRoles.length === 0"
          @click="handleShareSecret"
          class="font-semibold shadow-sm focus:outline-none"
        />
      </template>
    </Dialog>

    <!-- Revoke Confirmation Dialog -->
    <Dialog
      v-model="showRevokeConfirm"
      :options="{
        title: 'Revoke Share Access',
        size: 'sm',
      }"
    >
      <template #body-content>
        <div class="pt-2">
          <p class="text-sm text-ink-gray-7">
            Are you sure you want to revoke share access for
            <span class="font-bold text-ink-gray-9">{{ shareToRevoke?.share_type === 'User' ? shareToRevoke?.user : shareToRevoke?.frappe_role }}</span>?
          </p>
        </div>
      </template>
      <template #actions>
        <div class="flex justify-end gap-2 px-4 pb-4">
          <Button variant="ghost" label="Cancel" @click="showRevokeConfirm = false" class="text-ink-gray-7 focus:outline-none" />
          <Button
            variant="solid"
            theme="red"
            label="Revoke Access"
            :loading="unshareResource.loading"
            @click="handleRevokeShare"
            class="px-4 font-semibold shadow-sm focus:outline-none"
          />
        </div>
      </template>
    </Dialog>
    <!-- Image Lightbox Modal / Popover Preview -->
    <Dialog v-model="previewModalOpen" :options="{ size: 'xl', title: 'Image Preview' }">
      <template #body-content>
        <div class="flex flex-col items-center gap-4 py-2">
          <div class="relative w-full max-h-[75vh] flex items-center justify-center bg-surface-gray-7 rounded-2xl overflow-hidden p-2">
            <img :src="previewImageUrl" class="max-w-full max-h-[70vh] object-contain rounded-lg" />
          </div>
          <div class="w-full flex items-center justify-between px-1">
            <span class="text-xs font-mono text-ink-gray-7 truncate max-w-xs">{{ getFileName(previewImageUrl) }}</span>
            <div class="flex items-center gap-2">
              <a :href="previewImageUrl" target="_blank" download class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-surface-base border border-outline-gray-2 text-ink-gray-9 hover:bg-surface-gray-1 transition-colors shadow-2xs">
                <FeatherIcon name="download" class="w-4 h-4 text-ink-gray-7" /> Download
              </a>
              <a :href="previewImageUrl" target="_blank" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold bg-surface-base border border-outline-gray-2 text-ink-gray-9 hover:bg-surface-gray-1 transition-colors shadow-2xs">
                <FeatherIcon name="external-link" class="w-4 h-4 text-ink-gray-7" /> Open Original
              </a>
            </div>
          </div>
        </div>
      </template>
    </Dialog>

    <!-- Role Users Modal -->
    <Dialog v-model="showRoleUsersModal" :options="{ title: selectedRoleName ? `People with ${selectedRoleName} Role` : 'People with Access', size: 'lg' }">
      <template #body-content>
        <div class="flex flex-col gap-4 py-1">
          <TextInput
            v-model="roleMemberSearchQuery"
            type="text"
            placeholder="Search members by name or email…"
            iconLeft="search"
            class="w-full"
          />

          <div class="space-y-4">
            <!-- Active Members Section -->
            <div>
              <h4 class="text-xs font-bold text-ink-gray-5 uppercase tracking-wider mb-2">
                Active Members ({{ activeRoleUsersList.length }})
              </h4>

              <div v-if="roleUsersResource.loading" class="py-6 flex flex-col items-center justify-center space-y-2">
                <FeatherIcon name="loader" class="w-5 h-5 animate-spin text-ink-gray-5" />
                <span class="text-xs text-ink-gray-5">Loading members...</span>
              </div>

              <div v-else-if="activeRoleUsersList.length" class="flex flex-col max-h-56 overflow-y-auto divide-y divide-outline-gray-1 bg-surface-base border border-outline-gray-1 rounded-xl">
                <div
                  v-for="u in activeRoleUsersList"
                  :key="u.user"
                  class="flex items-center justify-between gap-3 p-2.5 hover:bg-surface-gray-1 transition-colors"
                >
                  <div class="flex items-center gap-3 min-w-0 flex-1">
                    <Avatar :label="u.full_name || u.user" size="md" />
                    <div class="min-w-0">
                      <div class="text-sm font-medium text-ink-gray-9 truncate">
                        {{ u.full_name || u.user }}
                      </div>
                      <div class="truncate text-xs text-ink-gray-5">
                        {{ u.user }}
                      </div>
                    </div>
                  </div>

                  <!-- Permission Level Selector -->
                  <FormControl
                    v-if="isOwnerOrAdmin"
                    type="select"
                    :modelValue="getUserPermissionLevel(u)"
                    :options="[
                      { label: 'View Only', value: 'View Only' },
                      { label: 'View & Copy', value: 'View & Copy' },
                      { label: 'Edit', value: 'Edit' },
                      { label: 'Full Control', value: 'Full Control' }
                    ]"
                    class="!w-36 text-xs shrink-0"
                    @update:modelValue="(val) => handleUpdateUserPermission(u, val)"
                    @change="(val) => handleUpdateUserPermission(u, val)"
                  />

                  <!-- Three-Dot Menu -->
                  <Dropdown
                    v-if="isOwnerOrAdmin"
                    :options="[
                      {
                        label: 'Revoke Access',
                        icon: 'lucide-user-minus',
                        theme: 'red',
                        onClick: () => handleRevokeRoleMember(u)
                      }
                    ]"
                  >
                    <template #default="{ open }">
                      <Button variant="ghost" icon="lucide-more-vertical" class="!p-1.5 text-ink-gray-5 hover:text-ink-gray-9 focus:outline-none" />
                    </template>
                  </Dropdown>
                </div>
              </div>
              <p v-else class="text-xs text-ink-gray-5 italic py-4 text-center">No active members.</p>
            </div>

            <!-- Revoked / Removed Members Section -->
            <div v-if="revokedRoleUsersList.length">
              <h4 class="text-xs font-bold text-ink-gray-5 uppercase tracking-wider mb-2">
                Revoked / Removed Members ({{ revokedRoleUsersList.length }})
              </h4>

              <div class="flex flex-col max-h-44 overflow-y-auto divide-y divide-outline-gray-1 bg-surface-gray-2 border border-outline-gray-1 rounded-xl">
                <div
                  v-for="u in revokedRoleUsersList"
                  :key="u.user"
                  class="flex items-center justify-between gap-3 p-2.5 hover:bg-surface-gray-1 transition-colors"
                >
                  <div class="flex items-center gap-3 min-w-0 flex-1">
                    <Avatar :label="u.full_name || u.user" size="md" class="opacity-60" />
                    <div class="min-w-0">
                      <div class="text-sm font-medium text-ink-gray-7 truncate flex items-center gap-2">
                        <span>{{ u.full_name || u.user }}</span>
                        <Badge variant="subtle" theme="red" size="sm">Revoked</Badge>
                      </div>
                      <div class="truncate text-xs text-ink-gray-5">
                        {{ u.user }}
                      </div>
                    </div>
                  </div>

                  <!-- Re-grant Access Button -->
                  <Button
                    v-if="isOwnerOrAdmin"
                    variant="subtle"
                    theme="blue"
                    label="Re-grant Access"
                    icon="lucide-user-plus"
                    size="sm"
                    class="shrink-0 font-medium"
                    @click="handleRegrantRoleMember(u)"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
      <template #actions="{ close }">
        <div class="flex justify-end gap-2">
          <Button variant="ghost" label="Cancel" @click="close" />
          <Button
            v-if="isOwnerOrAdmin"
            variant="solid"
            label="Save Changes"
            :loading="isSavingRoleMembers"
            @click="handleSaveRoleMemberPermissions"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, watch, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import {
  Button,
  Badge,
  FeatherIcon,
  TextInput,
  FormControl,
  Dialog,
  Dropdown,
  ErrorMessage,
  Breadcrumbs,
  Tooltip,
  toast,
  TabButtons,
  Tabs,
  PageHeaderBase,
  PageHeaderTitle,
  ScrollArea,
  Avatar,
  MultiSelect
} from 'frappe-ui'
import { mobileSidebarOpened, useSecret, useDecryptSecret, useSecretActivity, useDeleteSecret, useUpdateSecret, useShareSecret, useUnshare, useSecretShares, useShareOptions, useVaultStats, useFolders, useRoleUsers, useUpdateSharePermission, useSaveRoleMemberPermission } from '../composables/vault'
import { useClipboard } from '../composables/clipboard'
import EmptyState from '../components/EmptyState.vue'
import StrengthBadge from '../components/StrengthBadge.vue'
import { actionIcons, secretTypeOptions, permissionTheme, typeMeta, formatRelativeTime } from '../composables/constants'
import { cleanUrl, parseAttachments, isImageUrl, getFileName } from '../utils/attachments'

const props = defineProps({
  name: {
    type: String,
    required: true,
  }
})

const router = useRouter()

const showActivitySidebar = ref(window.innerWidth >= 1024)

function handleResize() {
  if (window.innerWidth >= 1024) {
    showActivitySidebar.value = true
  } else {
    showActivitySidebar.value = false
  }
}

onMounted(() => {
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
const activeTabIndex = ref(0)
const activeTabLabel = ref('Sharing')
const tabsList = computed(() => [
  { label: 'Activity', icon: 'lucide-sparkles' },
  { label: sharesList.value.length ? `Sharing (${sharesList.value.length})` : 'Sharing', icon: 'lucide-share-2' },
])
const isEditing = ref(false)

// Collapsible blocks
const detailsOpen = ref(true)
const notesOpen = ref(true)
const metaOpen = ref(true)

// Sensitive fields reveal flags (Read-only view)
const revealedFields = ref({})
const editRevealedFields = ref({})

const secretFieldsConfig = {
  'Password': [
    { name: 'url', label: 'URL', type: 'url', isLink: true },
    { name: 'username', label: 'Username', type: 'text', mono: true },
    { name: 'password', label: 'Password', type: 'password', mono: true }
  ],
  'API Key': [
    { name: 'url', label: 'Endpoint URL', type: 'url', isLink: true },
    { name: 'api_key', label: 'API Key', type: 'text', mono: true },
    { name: 'api_secret', label: 'API Secret', type: 'password', mono: true }
  ],
  'Credit Card': [
    { name: 'card_holder', label: 'Card Holder', type: 'text', mono: false },
    { name: 'card_number', label: 'Card Number', type: 'password', mono: true, placeholder: '•••• •••• •••• ••••' },
    { name: 'card_expiry', label: 'Expiry', type: 'text', mono: true, placeholder: 'MM/YY' },
    { name: 'card_cvv', label: 'CVV', type: 'password', mono: true, placeholder: '123' }
  ],
  'Database': [
    { name: 'url', label: 'URL', type: 'url', isLink: true },
    { name: 'db_host', label: 'Host', type: 'text', mono: true, placeholder: 'localhost or IP' },
    { name: 'db_port', label: 'Port', type: 'text', mono: true, placeholder: '3306' },
    { name: 'db_name', label: 'DB Name', type: 'text', mono: false },
    { name: 'username', label: 'Username', type: 'text', mono: true },
    { name: 'db_password', label: 'Password', type: 'password', mono: true }
  ],
  'SSH Key': [
    { name: 'url', label: 'URL / Server IP', type: 'url', isLink: true },
    { name: 'username', label: 'Username', type: 'text', mono: true, placeholder: 'root / ubuntu' },
    { name: 'ssh_private_key', label: 'SSH Private Key', type: 'textarea', mono: true, placeholder: '-----BEGIN OPENSSH PRIVATE KEY-----...' }
  ],
  'Media': [
    { name: 'url', label: 'URL', type: 'url', isLink: true },
    { name: 'attachment', label: 'Attachment', type: 'file' }
  ],
  'Note': [
    { name: 'url', label: 'URL', type: 'url', isLink: true }
  ],
  'Other': [
    { name: 'url', label: 'URL', type: 'url', isLink: true }
  ]
}

const editAttachmentList = ref([])
const uploadingEditFiles = ref(false)
const previewModalOpen = ref(false)
const previewImageUrl = ref('')

function openImagePreview(url) {
  previewImageUrl.value = cleanUrl(url)
  previewModalOpen.value = true
}

function openFileUrl(url) {
  const cleaned = cleanUrl(url)
  if (cleaned) window.open(cleaned, '_blank')
}

function removeEditAttachment(index) {
  editAttachmentList.value.splice(index, 1)
  syncEditAttachmentForm()
}

function syncEditAttachmentForm() {
  if (editAttachmentList.value.length === 0) {
    editForm.attachment = ''
  } else if (editAttachmentList.value.length === 1) {
    editForm.attachment = editAttachmentList.value[0]
  } else {
    editForm.attachment = JSON.stringify(editAttachmentList.value)
  }
}

function triggerEditFileInput(fieldname) {
  const el = document.getElementById('edit_file_input_' + fieldname)
  if (el) el.click()
}

async function handleEditFileUpload(event, fieldname) {
  const files = Array.from(event.target.files || [])
  if (!files.length) return
  uploadingEditFiles.value = true
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
        editAttachmentList.value.push(data.message.file_url)
      }
    }
    syncEditAttachmentForm()
  } catch (err) {
    toast.error(err.message || 'File upload failed')
  } finally {
    uploadingEditFiles.value = false
  }
}

const showShareDialog = ref(false)
const showRevokeConfirm = ref(false)
const shareToRevoke = ref(null)

const secret = useSecret(props.name)
const decryptResource = useDecryptSecret()
const activity = useSecretActivity(props.name)
const deleteResource = useDeleteSecret()
const updateResource = useUpdateSecret()
const folders = useFolders()
const clipboard = useClipboard()

// Sharing resources
const shareResource = useShareSecret()
const unshareResource = useUnshare()
const sharesResource = useSecretShares(props.name)
const shareOptionsResource = useShareOptions()
const stats = useVaultStats()

const secretData = computed(() => secret.data)
const breadcrumbs = computed(() => {
  return [
    { label: 'Secrets', route: '/secrets' },
    { label: secretData.value?.title || 'Loading...' }
  ]
})
const decryptedData = computed(() => decryptResource.data?.decrypted)
const activityList = computed(() => activity.data || [])
const sharesList = computed(() => sharesResource.data || [])
const shareOptions = computed(() => shareOptionsResource.data || { users: [], roles: [] })

const recipientOptions = computed(() => {
  const owner = secretData.value?.owner
  let list = newShareType.value === 'User' 
    ? shareOptions.value.users 
    : shareOptions.value.roles
      
  if (newShareType.value === 'User' && owner) {
    list = list.filter(item => item.value !== owner)
  }
  
  return [{ label: 'Choose recipient...', value: '' }, ...list]
})

// Sharing Form State
const newShareType = ref('User') // 'User', 'Role'
const newShareRecipient = ref('')
const newSharePermission = ref('View Only')
const newShareExpiresOn = ref('')
const isSharing = ref(false)

const currentSessionUser = computed(() => {
  if (window.frappe?.boot?.user) {
    if (typeof window.frappe.boot.user === 'object') {
      return window.frappe.boot.user.name || 'Guest'
    }
    return window.frappe.boot.user
  }
  if (window.frappe?.session?.user) {
    return window.frappe.session.user
  }
  if (window.frappe?.user?.name) {
    return window.frappe.user.name
  }
  return 'Guest'
})
const isOwnerOrAdmin = computed(() => {
  if (stats.data?.is_admin) return true
  if (currentSessionUser.value === 'Administrator') return true
  const roles = window.frappe?.user_roles || window.frappe?.boot?.user?.roles || []
  if (roles.includes('Vault Admin')) return true
  return secretData.value?.owner === currentSessionUser.value || secretData.value?.user_permission === 'Full Control'
})

const userPermission = computed(() => secretData.value?.user_permission || 'View Only')

const canEdit = computed(() => {
  if (stats.data?.is_admin) return true
  if (currentSessionUser.value === 'Administrator') return true
  const roles = window.frappe?.user_roles || window.frappe?.boot?.user?.roles || []
  if (roles.includes('Vault Admin')) return true
  if (secretData.value?.owner === currentSessionUser.value) return true
  return ['Edit', 'Full Control'].includes(userPermission.value)
})

const canDelete = computed(() => {
  if (stats.data?.is_admin) return true
  if (currentSessionUser.value === 'Administrator') return true
  const roles = window.frappe?.user_roles || window.frappe?.boot?.user?.roles || []
  if (roles.includes('Vault Admin')) return true
  if (secretData.value?.owner === currentSessionUser.value) return true
  return userPermission.value === 'Full Control'
})

const canCopy = computed(() => {
  if (stats.data?.is_admin) return true
  if (currentSessionUser.value === 'Administrator') return true
  const roles = window.frappe?.user_roles || window.frappe?.boot?.user?.roles || []
  if (roles.includes('Vault Admin')) return true
  if (secretData.value?.owner === currentSessionUser.value) return true
  return ['View & Copy', 'Edit', 'Full Control'].includes(userPermission.value)
})

const selectedUserEmails = ref([])
const selectedRoles = ref([])

const userMembers = computed(() => {
  const users = shareOptions.value.users || []
  return users.map(u => ({
    label: u.label || u.value,
    value: u.value,
    image: null,
  }))
})

const roleMembers = computed(() => {
  const roles = shareOptions.value.roles || []
  return roles.map(r => ({
    label: r.label || r.value,
    value: r.value,
  }))
})

const MAX_AVATARS = 3
const visibleSelected = computed(() =>
  selectedUserEmails.value
    .map((v) => userMembers.value.find((m) => m.value === v))
    .filter(Boolean)
    .slice(0, MAX_AVATARS)
)
const overflowCount = computed(() =>
  Math.max(0, selectedUserEmails.value.length - MAX_AVATARS)
)

const visibleSelectedRoles = computed(() =>
  selectedRoles.value
    .map((v) => roleMembers.value.find((m) => m.value === v))
    .filter(Boolean)
    .slice(0, MAX_AVATARS)
)
const overflowRoleCount = computed(() =>
  Math.max(0, selectedRoles.value.length - MAX_AVATARS)
)

function openShareDialog() {
  newShareType.value = 'User'
  newShareRecipient.value = ''
  selectedUserEmails.value = []
  selectedRoles.value = []
  newSharePermission.value = 'View Only'
  newShareExpiresOn.value = ''
  showShareDialog.value = true
  shareOptionsResource.fetch()
}

async function handleShareSecret() {
  if (newShareType.value === 'User' && selectedUserEmails.value.length === 0) {
    toast.error('Please select at least one user')
    return
  }
  if (newShareType.value === 'Role' && selectedRoles.value.length === 0) {
    toast.error('Please select at least one role')
    return
  }

  isSharing.value = true
  try {
    if (newShareType.value === 'User') {
      for (const email of selectedUserEmails.value) {
        await shareResource.submit({
          shared_name: props.name,
          shared_doctype: 'Vault Secret',
          share_type: 'User',
          user: email,
          permission_level: newSharePermission.value,
          expires_on: newShareExpiresOn.value || undefined,
        })
      }
      toast.success(`Shared successfully with ${selectedUserEmails.value.length} user(s)`)
    } else {
      for (const role of selectedRoles.value) {
        await shareResource.submit({
          shared_name: props.name,
          shared_doctype: 'Vault Secret',
          share_type: 'Role',
          frappe_role: role,
          permission_level: newSharePermission.value,
          expires_on: newShareExpiresOn.value || undefined,
        })
      }
      toast.success(`Shared successfully with ${selectedRoles.value.length} role(s)`)
    }

    newShareRecipient.value = ''
    selectedUserEmails.value = []
    selectedRoles.value = []
    newShareExpiresOn.value = ''
    showShareDialog.value = false
    await sharesResource.fetch({ secret_name: props.name })
    activity.reload()
  } catch (err) {
    toast.error(err.messages?.[0] || err.message || 'Failed to share secret')
  } finally {
    isSharing.value = false
  }
}

const imageLoadErrorMap = reactive({})
const showRoleUsersModal = ref(false)
const selectedRoleName = ref('')
const roleMemberSearchQuery = ref('')
const revokedUserIds = ref(new Set())
const userPermissionOverrides = ref({})
const isSavingRoleMembers = ref(false)
const roleUsersResource = useRoleUsers()
const saveRoleMemberPermResource = useSaveRoleMemberPermission()
const updateSharePermResource = useUpdateSharePermission()

const roleUsersList = computed(() => roleUsersResource.data || [])
const filteredRoleUsersList = computed(() => {
  if (!roleMemberSearchQuery.value.trim()) return roleUsersList.value
  const q = roleMemberSearchQuery.value.toLowerCase().trim()
  return roleUsersList.value.filter(u =>
    (u.full_name && u.full_name.toLowerCase().includes(q)) ||
    (u.user && u.user.toLowerCase().includes(q))
  )
})

watch(() => roleUsersResource.data, (data) => {
  if (data && Array.isArray(data)) {
    const rev = new Set()
    const perms = {}
    data.forEach(u => {
      if (u.is_revoked) rev.add(u.user)
      if (u.permission_level) perms[u.user] = u.permission_level
    })
    revokedUserIds.value = rev
    userPermissionOverrides.value = perms
  }
})

const activeRoleUsersList = computed(() => {
  return filteredRoleUsersList.value.filter(u => !revokedUserIds.value.has(u.user))
})

const revokedRoleUsersList = computed(() => {
  return filteredRoleUsersList.value.filter(u => revokedUserIds.value.has(u.user))
})

function openRoleUsersModal(roleName) {
  if (!roleName) return
  selectedRoleName.value = roleName
  roleMemberSearchQuery.value = ''
  revokedUserIds.value = new Set()
  userPermissionOverrides.value = {}
  showRoleUsersModal.value = true
  roleUsersResource.submit({
    role_name: roleName,
    shared_name: props.name,
    shared_doctype: 'Vault Secret'
  })
}

function openUserGroupModal(item) {
  selectedRoleName.value = ''
  roleMemberSearchQuery.value = ''
  revokedUserIds.value = new Set()
  userPermissionOverrides.value = {}
  showRoleUsersModal.value = true
  roleUsersResource.submit({
    shared_name: props.name,
    shared_doctype: 'Vault Secret'
  })
}

function getUserPermissionLevel(userObj) {
  if (userPermissionOverrides.value && userPermissionOverrides.value[userObj.user]) {
    return userPermissionOverrides.value[userObj.user]
  }
  return userObj.permission_level || 'View Only'
}

function handleUpdateUserPermission(userObj, val) {
  let permValue = 'View Only'
  if (typeof val === 'string') {
    permValue = val
  } else if (val && typeof val === 'object') {
    if (val.target && val.target.value) {
      permValue = val.target.value
    } else if (val.value) {
      permValue = val.value
    }
  }
  userPermissionOverrides.value = {
    ...userPermissionOverrides.value,
    [userObj.user]: permValue
  }
}

function handleRevokeRoleMember(userObj) {
  const updatedSet = new Set(revokedUserIds.value)
  updatedSet.add(userObj.user)
  revokedUserIds.value = updatedSet
}

function handleRegrantRoleMember(userObj) {
  const updatedSet = new Set(revokedUserIds.value)
  updatedSet.delete(userObj.user)
  revokedUserIds.value = updatedSet
}

async function handleSaveRoleMemberPermissions() {
  isSavingRoleMembers.value = true
  try {
    const users = roleUsersList.value || []
    for (const u of users) {
      const isRev = revokedUserIds.value.has(u.user)
      const permLevel = userPermissionOverrides.value[u.user] || u.permission_level || 'View Only'
      await saveRoleMemberPermResource.submit({
        shared_name: props.name,
        shared_doctype: 'Vault Secret',
        user: u.user,
        permission_level: permLevel,
        is_revoked: isRev,
      })
    }
    toast.success('Role member permissions saved successfully')
    showRoleUsersModal.value = false
    await sharesResource.fetch({ secret_name: props.name })
  } catch (err) {
    toast.error(err.messages?.[0] || err.message || 'Failed to save role member permissions')
  } finally {
    isSavingRoleMembers.value = false
  }
}

async function handleUpdateSharePermission(shareName, permissionLevel) {
  try {
    await updateSharePermResource.submit({
      share_name: shareName,
      permission_level: permissionLevel,
    })
    toast.success(`Permission updated to ${permissionLevel}`)
    await sharesResource.fetch({ secret_name: props.name })
  } catch (err) {
    toast.error(err.messages?.[0] || err.message || 'Failed to update permission')
  }
}

function confirmRevokeShare(item) {
  shareToRevoke.value = item
  showRevokeConfirm.value = true
}

async function handleRevokeShare() {
  if (!shareToRevoke.value) return
  const recipientName = shareToRevoke.value.share_type === 'User' ? shareToRevoke.value.user : shareToRevoke.value.frappe_role
  try {
    await unshareResource.submit({ share_name: shareToRevoke.value.name })
    toast.success(`Revoked access for ${recipientName}`)
    showRevokeConfirm.value = false
    shareToRevoke.value = null
    await sharesResource.fetch({ secret_name: props.name })
    activity.reload()
  } catch (err) {
    toast.error(err.message || 'Failed to revoke access')
  }
}



const folderOptions = computed(() => {
  const options = [{ label: 'No Folder', value: '' }]
  if (folders.data) {
    folders.data.forEach(f => {
      if (f.can_write || f.name === secretData.value?.folder) {
        options.push({ label: f.folder_name, value: f.name })
      }
    })
  }
  return options
})

const copiedField = ref(null)

const editForm = reactive({
  title: '',
  secret_type: 'Password',
  folder: '',
  url: '',
  username: '',
  email: '',
  notes: '',
  password: '',
  api_key: '',
  api_secret: '',
  card_holder: '',
  card_number: '',
  card_expiry: '',
  card_cvv: '',
  db_host: '',
  db_port: '',
  db_name: '',
  db_password: '',
  ssh_private_key: '',
  attachment: '',
})

watch(() => props.name, (n) => {
  if (n) {
    secret.submit({ name: n })
    activity.submit({ secret_name: n })
    revealedFields.value = {}
    editRevealedFields.value = {}
    isEditing.value = false
  }
})

folders.submit()

function getFolderName(folderId) {
  if (!folderId) return ''
  const found = folders.data?.find(f => f.name === folderId)
  return found ? found.folder_name : folderId
}

function copyField(value, fieldName) {
  if (!value) return
  clipboard.copy(value)
  copiedField.value = fieldName
  setTimeout(() => {
    if (copiedField.value === fieldName) {
      copiedField.value = null
    }
  }, 3000)
}

async function ensureDecrypted(actionCallback) {
  try {
    if (!decryptedData.value) {
      await decryptResource.submit({ name: props.name })
    }
    if (actionCallback) {
      await actionCallback()
    }
  } catch (err) {
    const errMsg = err.messages?.[0] || err.message || 'Failed to decrypt secret'
    toast.error(errMsg)
  }
}

// --- Sensitive Field Handlers ---
async function toggleField(fieldName, isEdit = false) {
  if (isEdit) {
    editRevealedFields.value[fieldName] = !editRevealedFields.value[fieldName]
    return
  }
  
  if (revealedFields.value[fieldName]) {
    revealedFields.value[fieldName] = false
    return
  }
  
  await ensureDecrypted(() => {
    revealedFields.value[fieldName] = true
  })
}

async function copyFieldData(fieldName) {
  let val = decryptedData.value?.[fieldName] || secretData.value?.[fieldName]
  if (!val && fieldName === 'db_host' && secretData.value?.db_host) {
    val = secretData.value.db_host + (secretData.value.db_port ? ':' + secretData.value.db_port : '')
  }
  if (val) {
    copyField(val, fieldName)
  } else {
    await ensureDecrypted(() => {
      if (decryptedData.value?.[fieldName]) {
        copyField(decryptedData.value[fieldName], fieldName)
      } else {
        toast.error('Field is empty')
      }
    })
  }
}

async function toggleEditMode() {
  if (isEditing.value) {
    isEditing.value = false
    return
  }

  await ensureDecrypted(() => {
    editRevealedFields.value = {}

    const sd = secretData.value || {}
    const dd = decryptedData.value || {}

    editForm.title = sd.title || ''
    editForm.secret_type = sd.secret_type || 'Password'
    editForm.folder = sd.folder || ''
    editForm.url = sd.url || ''
    editForm.username = sd.username || ''
    editForm.email = sd.email || ''
    editForm.notes = sd.notes || ''

    editForm.password = dd.password || ''
    editForm.api_key = sd.api_key || ''
    editForm.api_secret = dd.api_secret || ''
    editForm.card_holder = sd.card_holder || ''
    editForm.card_number = dd.card_number || ''
    editForm.card_expiry = sd.card_expiry || ''
    editForm.card_cvv = dd.card_cvv || ''
    editForm.db_host = sd.db_host || ''
    editForm.db_port = sd.db_port || ''
    editForm.db_name = sd.db_name || ''
    editForm.db_password = dd.db_password || ''
    editForm.ssh_private_key = sd.ssh_private_key || ''
    editAttachmentList.value = parseAttachments(sd.attachment)
    syncEditAttachmentForm()

    isEditing.value = true
  })
}

async function handleSave() {
  if (!editForm.title || !editForm.title.trim()) {
    toast.error('Please enter a secret title')
    return
  }

  try {
    const payload = {
      title: editForm.title,
      secret_type: editForm.secret_type,
      folder: editForm.folder,
      notes: editForm.notes,
      url: editForm.url,
    }

    if (editForm.secret_type === 'Password') {
      payload.username = editForm.username
      payload.password = editForm.password
      payload.url = editForm.url
    } else if (editForm.secret_type === 'API Key') {
      payload.api_key = editForm.api_key
      payload.api_secret = editForm.api_secret
      payload.url = editForm.url
    } else if (editForm.secret_type === 'Credit Card') {
      payload.card_holder = editForm.card_holder
      payload.card_number = editForm.card_number
      payload.card_expiry = editForm.card_expiry
      payload.card_cvv = editForm.card_cvv
    } else if (editForm.secret_type === 'Database') {
      payload.db_host = editForm.db_host
      payload.db_port = editForm.db_port
      payload.db_name = editForm.db_name
      payload.username = editForm.username
      payload.db_password = editForm.db_password
    } else if (editForm.secret_type === 'SSH Key') {
      payload.username = editForm.username
      payload.ssh_private_key = editForm.ssh_private_key
    } else if (editForm.secret_type === 'Media') {
      syncEditAttachmentForm()
      payload.attachment = editForm.attachment
    }

    await updateResource.submit({
      name: props.name,
      ...payload,
    })

    isEditing.value = false
    await secret.submit({ name: props.name })
    await activity.submit({ secret_name: props.name })
    decryptResource.submit({ name: props.name })
  } catch (e) {
    toast.error(e.messages?.[0] || e.message || 'Failed to save changes')
  }
}

const showDeleteDialog = ref(false)
const deleteError = ref('')

async function confirmDelete() {
  deleteError.value = ''
  try {
    await deleteResource.submit({ name: props.name })
    showDeleteDialog.value = false
    toast.success('Secret deleted successfully')
    router.push('/secrets')
  } catch (err) {
    deleteError.value = err.messages?.[0] || err.message || 'Failed to delete secret'
    toast.error(deleteError.value)
  }
}

function formatTime(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  return d.toLocaleString('en-US', {
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function formatDateOnly(dt) {
  if (!dt) return 'Never'
  return new Date(dt).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function parseDetails(details) {
  if (!details) return {}
  if (typeof details === 'object') return details
  try {
    return JSON.parse(details)
  } catch (e) {
    return {}
  }
}

function getActivityText(item) {
  const details = parseDetails(item.details)
  switch (item.action) {
    case 'Created':
      return 'created this secret'
    case 'Updated':
      return 'updated this secret'
    case 'Deleted':
      return 'deleted this secret'
    case 'Viewed':
      return 'viewed this secret'
    case 'Copied': {
      const field = details.field || 'password'
      return `copied the ${field} field`
    }
    case 'Shared': {
      const recipient = details.recipient || 'Unknown'
      const permission = details.permission || 'View Only'
      const expiresOn = details.expires_on ? ` (expires ${formatTime(details.expires_on)})` : ''
      return `shared this secret with ${recipient} (${permission})${expiresOn}`
    }
    case 'Unshared': {
      const recipient = details.recipient || 'Unknown'
      return `revoked access for ${recipient}`
    }
    default:
      return `${item.action.toLowerCase()} this secret`
  }
}

function getActionMainText(item) {
  switch (item.action) {
    case 'Created': return 'created this secret'
    case 'Updated': return 'updated this secret'
    case 'Deleted': return 'deleted this secret'
    case 'Viewed': return 'viewed this secret'
    case 'Copied': return 'copied secret credentials'
    case 'Shared': return 'shared access to this secret'
    case 'Unshared': return 'revoked secret access'
    default: return `${item.action.toLowerCase()} this secret`
  }
}

function hasActivityDetails(item) {
  return ['Copied', 'Shared', 'Unshared'].includes(item.action)
}

function getDetailIcon(item) {
  switch (item.action) {
    case 'Copied': return 'copy'
    case 'Shared': return 'share-2'
    case 'Unshared': return 'shield-off'
    default: return 'info'
  }
}

function getActivityDetailText(item) {
  const details = parseDetails(item.details)
  switch (item.action) {
    case 'Copied': {
      const field = details.field || 'password'
      return `Field: ${field}`
    }
    case 'Shared': {
      const recipient = details.recipient || 'Unknown'
      const permission = details.permission || 'View Only'
      const expiresOn = details.expires_on ? ` • Expires ${formatTime(details.expires_on)}` : ''
      return `${recipient} (${permission})${expiresOn}`
    }
    case 'Unshared': {
      const recipient = details.recipient || 'Unknown'
      return `Recipient: ${recipient}`
    }
    default: return ''
  }
}
</script>
