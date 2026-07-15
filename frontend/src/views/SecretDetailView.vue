<template>
  <div class="flex-1 flex flex-col overflow-hidden bg-surface-base">
    
    <!-- Page Header -->
    <header class="flex h-10.5 items-center justify-between border-b border-outline-gray-1 bg-surface-base px-5 py-2.5 shrink-0">
      <!-- Breadcrumbs -->
      <div class="flex items-center gap-2 text-lg font-medium min-w-0 flex-1">
        <Button
          class="sm:hidden mr-1 shrink-0"
          variant="ghost"
          icon="lucide-menu"
          @click="mobileSidebarOpened = true"
        />

        <Breadcrumbs :items="breadcrumbs" class="min-w-0" />
      </div>
    </header>

    <!-- Splitscreen Main Content Body (Exact CRM split match) -->
    <div v-if="secretData" class="flex-1 flex overflow-hidden min-h-0">
      
      <!-- LEFT PANE: Tab navigation & Activity timeline feed -->
      <div class="flex-1 flex flex-col overflow-hidden bg-surface-base border-r border-outline-gray-1">
        <Tabs v-model="activeTabIndex" :tabs="tabsList" class="flex flex-1 flex-col overflow-hidden">
          <template #tab-panel="{ tab }">
            <!-- Activity feed timeline panel -->
            <div v-if="activeTabIndex === 0" class="p-6 overflow-y-auto flex-1">
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
                    <div class="w-5 h-5 flex items-center justify-center shrink-0 z-10 text-ink-gray-5 bg-surface-base mt-0.5">
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

            <!-- Sharing config panel -->
            <div v-else-if="activeTabIndex === 1" class="p-6 overflow-y-auto flex-1">
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
                  <div class="w-9 h-9 rounded-full bg-blue-50 border border-blue-100/50 text-blue-650 flex items-center justify-center shrink-0">
                    <FeatherIcon name="share-2" class="w-4.5 h-4.5" />
                  </div>
                  <div>
                    <p class="font-bold text-ink-gray-9 leading-normal">Shared Secret Access</p>
                    <p class="mt-1 text-ink-gray-6 font-normal">
                      This secret was shared with you by <strong class="text-ink-gray-8">{{ secretData.owner }}</strong>. You have <strong class="text-ink-gray-8">{{ secretData.permission_level || 'View Only' }}</strong> rights on this secret.
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
                        <div class="w-9 h-9 rounded-full bg-surface-gray-2 border border-outline-gray-1 shadow-sm flex items-center justify-center shrink-0">
                          <FeatherIcon
                            :name="item.share_type === 'User' ? 'user' : item.share_type === 'Group' ? 'users' : 'shield'"
                            class="w-4.5 h-4.5 text-ink-gray-5"
                          />
                        </div>
                        <div class="min-w-0">
                          <p class="text-sm font-semibold text-ink-gray-9 truncate leading-snug">
                            {{ item.share_type === 'User' ? item.user : item.share_type === 'Group' ? item.group : item.frappe_role }}
                          </p>
                          <p class="text-xs text-ink-gray-4 mt-1 font-medium flex items-center gap-1.5 leading-none">
                            <span>{{ item.share_type }}</span>
                            <span class="w-1 h-1 rounded-full bg-surface-gray-4" />
                            <span v-if="item.expires_on">Expires {{ formatTime(item.expires_on) }}</span>
                            <span v-else>Never expires</span>
                          </p>
                        </div>
                      </div>

                      <div class="flex items-center gap-3 shrink-0">
                        <Badge
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
                          class="!p-1.5 h-auto text-ink-gray-4 hover:!text-ink-red-3 hover:!bg-red-50"
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
                      This secret is private. Use the Share button to give access to other users, groups, or roles.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Tabs>
      </div>

      <!-- RIGHT PANE: Resizable Side Panel Drawer (off-white bg, bordered) -->
      <div class="w-[380px] shrink-0 flex flex-col overflow-y-auto flex-1 lg:flex-none bg-surface-base">
        
        <!-- Sidebar Header Box (exact match to CRM-DEAL right panel header) -->
        <div class="border-b border-outline-gray-1 bg-surface-base">
          <!-- Top ID row exactly matching TabsList height structure -->
          <div class="flex h-[45px] cursor-copy items-center border-b px-5 py-2.5 text-lg-medium text-ink-gray-9 bg-surface-base">
           {{ secretData.name }}
          </div>

          <!-- Avatar, Title & Individual Action Buttons Row -->
          <div class="p-6 flex items-start gap-4">
            <div :class="`size-14 rounded-full flex items-center justify-center shrink-0 shadow-sm border border-outline-gray-1 ${typeMeta[secretData.secret_type || 'Other']?.bg}`">
              <FeatherIcon :name="typeMeta[secretData.secret_type || 'Other']?.icon || 'key'" class="w-6 h-6 text-ink-gray-7" />
            </div>
            
            <div class="min-w-0 flex-1 pt-0.5">
              <Tooltip :text="secretData.title">
                <h2 class="truncate text-3xl-medium text-ink-gray-9 mb-2.5">
                  {{ secretData.title }}
                </h2>
              </Tooltip>
              
              <!-- Action Button (Delete only, slightly smaller) -->
              <div v-if="canDelete" class="flex items-center gap-2">
                <Button
                  variant="subtle"
                  theme="red"
                  size="xs"
                  icon="trash-2"
                  title="Delete Secret"
                  @click="showDeleteDialog = true"
                />
              </div>
            </div>
          </div>
        </div>

        <div class="flex flex-1 flex-col justify-between overflow-hidden">
          
          <!-- MAIN SCROLLABLE ATTRIBUTES AREA -->
          <div class="flex-1 overflow-y-auto">
            
            <!-- Clipboard clear warning indicator -->
            <div v-if="clipboard.copied.value" class="flex items-center gap-2.5 p-3 mx-4 my-2 bg-amber-50/70 text-amber-800 rounded-xl text-xs font-semibold border border-amber-100/40 shadow-sm transition-all duration-300">
              <FeatherIcon name="shield" class="w-4 h-4 text-amber-600 animate-pulse shrink-0" />
              <span class="flex-1">Clipboard copied. Auto-clearing in <strong>{{ clipboard.countdown.value }}s</strong>.</span>
            </div>

            <!-- Collapsible DETAILS Accordion -->
            <div class="border-b border-outline-gray-1 py-4 px-6">
              <div class="flex items-center justify-between select-none cursor-pointer" @click="detailsOpen = !detailsOpen">
                <div class="flex items-center gap-2.5">
                  <FeatherIcon name="chevron-down" class="h-5 w-5 text-ink-gray-5 transition-transform duration-200" :class="{ '-rotate-90': !detailsOpen }" />
                  <h3 class="text-base font-bold text-ink-gray-9">Details</h3>
                </div>

                <!-- Edit icon button matching native CRM button box -->
                <div v-if="canEdit" @click.stop>
                  <Button
                    variant="ghost"
                    size="sm"
                    :icon="isEditing ? 'eye' : 'edit'"
                    :title="isEditing ? 'View Details' : 'Edit Details'"
                    @click="toggleEditMode"
                  />
                </div>
              </div>

            <div v-show="detailsOpen" class="mt-3.5">
              <!-- EDIT VIEW FORM -->
              <div v-if="isEditing" class="space-y-4 pt-1 px-6">
                <!-- Title -->
                <div class="flex items-center justify-between gap-3 text-sm">
                  <label class="w-28 shrink-0 text-ink-gray-5 font-normal">Title <span class="text-red-550">*</span></label>
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
                <div v-if="editForm.secret_type === 'Password'" class="space-y-3">
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <label class="w-28 shrink-0 text-ink-gray-5 font-normal">Username</label>
                    <div class="flex-1 min-w-0">
                      <TextInput v-model="editForm.username" placeholder="Username" class="w-full text-sm" />
                    </div>
                  </div>
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <label class="w-28 shrink-0 text-ink-gray-5 font-normal">Password</label>
                    <div class="flex-1 min-w-0 relative">
                      <TextInput :type="showEditPassword ? 'text' : 'password'" v-model="editForm.password" placeholder="Password" class="w-full text-sm pr-9" />
                      <button type="button" class="absolute right-2.5 top-2 text-ink-gray-4 hover:text-ink-gray-9" @click="showEditPassword = !showEditPassword">
                        <FeatherIcon :name="showEditPassword ? 'eye-off' : 'eye'" class="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <label class="w-28 shrink-0 text-ink-gray-5 font-normal">URL</label>
                    <div class="flex-1 min-w-0">
                      <TextInput v-model="editForm.url" placeholder="https://example.com" class="w-full text-sm" />
                    </div>
                  </div>
                </div>

                <div v-else-if="editForm.secret_type === 'API Key'" class="space-y-3">
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <label class="w-28 shrink-0 text-ink-gray-5 font-normal">API Key</label>
                    <div class="flex-1 min-w-0">
                      <TextInput v-model="editForm.api_key" placeholder="API Key" class="w-full text-sm" />
                    </div>
                  </div>
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <label class="w-28 shrink-0 text-ink-gray-5 font-normal">API Secret</label>
                    <div class="flex-1 min-w-0 relative">
                      <TextInput :type="showEditAPISecret ? 'text' : 'password'" v-model="editForm.api_secret" placeholder="API Secret" class="w-full text-sm pr-9" />
                      <button type="button" class="absolute right-2.5 top-2 text-ink-gray-4 hover:text-ink-gray-9" @click="showEditAPISecret = !showEditAPISecret">
                        <FeatherIcon :name="showEditAPISecret ? 'eye-off' : 'eye'" class="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <label class="w-28 shrink-0 text-ink-gray-5 font-normal">Endpoint URL</label>
                    <div class="flex-1 min-w-0">
                      <TextInput v-model="editForm.url" placeholder="https://api.example.com" class="w-full text-sm" />
                    </div>
                  </div>
                </div>

                <div v-else-if="editForm.secret_type === 'Credit Card'" class="space-y-3">
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <label class="w-28 shrink-0 text-ink-gray-5 font-normal">Card Holder</label>
                    <div class="flex-1 min-w-0">
                      <TextInput v-model="editForm.card_holder" placeholder="Name on Card" class="w-full text-sm" />
                    </div>
                  </div>
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <label class="w-28 shrink-0 text-ink-gray-5 font-normal">Card Number</label>
                    <div class="flex-1 min-w-0 relative">
                      <TextInput :type="showEditCardNumber ? 'text' : 'password'" v-model="editForm.card_number" placeholder="•••• •••• •••• ••••" class="w-full text-sm pr-9 font-mono" />
                      <button type="button" class="absolute right-2.5 top-2 text-ink-gray-4 hover:text-ink-gray-9" @click="showEditCardNumber = !showEditCardNumber">
                        <FeatherIcon :name="showEditCardNumber ? 'eye-off' : 'eye'" class="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <label class="w-28 shrink-0 text-ink-gray-5 font-normal">Expiry</label>
                    <div class="flex-1 min-w-0">
                      <TextInput v-model="editForm.card_expiry" placeholder="MM/YY" class="w-full text-sm font-mono" />
                    </div>
                  </div>
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <label class="w-28 shrink-0 text-ink-gray-5 font-normal">CVV</label>
                    <div class="flex-1 min-w-0 relative">
                      <TextInput :type="showEditCardCVV ? 'text' : 'password'" v-model="editForm.card_cvv" placeholder="123" class="w-full text-sm pr-9 font-mono" />
                      <button type="button" class="absolute right-2.5 top-2 text-ink-gray-4 hover:text-ink-gray-9" @click="showEditCardCVV = !showEditCardCVV">
                        <FeatherIcon :name="showEditCardCVV ? 'eye-off' : 'eye'" class="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>

                <div v-else-if="editForm.secret_type === 'Database'" class="space-y-3">
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <label class="w-28 shrink-0 text-ink-gray-5 font-normal">Host</label>
                    <div class="flex-1 min-w-0">
                      <TextInput v-model="editForm.db_host" placeholder="localhost or IP" class="w-full text-sm font-mono" />
                    </div>
                  </div>
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <label class="w-28 shrink-0 text-ink-gray-5 font-normal">Port</label>
                    <div class="flex-1 min-w-0">
                      <TextInput v-model="editForm.db_port" placeholder="3306" class="w-full text-sm font-mono" />
                    </div>
                  </div>
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <label class="w-28 shrink-0 text-ink-gray-5 font-normal">DB Name</label>
                    <div class="flex-1 min-w-0">
                      <TextInput v-model="editForm.db_name" placeholder="Database Name" class="w-full text-sm" />
                    </div>
                  </div>
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <label class="w-28 shrink-0 text-ink-gray-5 font-normal">Username</label>
                    <div class="flex-1 min-w-0">
                      <TextInput v-model="editForm.username" placeholder="DB Username" class="w-full text-sm font-mono" />
                    </div>
                  </div>
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <label class="w-28 shrink-0 text-ink-gray-5 font-normal">Password</label>
                    <div class="flex-1 min-w-0 relative">
                      <TextInput :type="showEditDBPassword ? 'text' : 'password'" v-model="editForm.db_password" placeholder="DB Password" class="w-full text-sm pr-9" />
                      <button type="button" class="absolute right-2.5 top-2 text-ink-gray-4 hover:text-ink-gray-9" @click="showEditDBPassword = !showEditDBPassword">
                        <FeatherIcon :name="showEditDBPassword ? 'eye-off' : 'eye'" class="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>

                <div v-else-if="editForm.secret_type === 'SSH Key'" class="space-y-3">
                  <div class="flex items-center justify-between gap-3 text-sm">
                    <label class="w-28 shrink-0 text-ink-gray-5 font-normal">Username</label>
                    <div class="flex-1 min-w-0">
                      <TextInput v-model="editForm.username" placeholder="root / ubuntu" class="w-full text-sm font-mono" />
                    </div>
                  </div>
                  <div class="pt-1">
                    <FormControl type="textarea" label="SSH Private Key" v-model="editForm.ssh_private_key" :rows="5" placeholder="-----BEGIN OPENSSH PRIVATE KEY-----..." class="w-full text-xs font-mono" />
                  </div>
                </div>

                <div v-else-if="editForm.secret_type === 'Certificate'" class="space-y-3">
                  <div class="pt-1">
                    <FormControl type="textarea" label="Certificate / PEM" v-model="editForm.certificate" :rows="5" placeholder="-----BEGIN CERTIFICATE-----..." class="w-full text-xs font-mono" />
                  </div>
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

                <!-- Password Type fields -->
                <template v-if="secretData.secret_type === 'Password'">
                  <div v-if="secretData.url" class="flex items-center justify-between py-1 text-sm">
                    <span class="w-28 shrink-0 text-ink-gray-5 font-normal">URL</span>
                    <a :href="secretData.url" target="_blank" class="min-w-0 flex-1 text-right font-medium text-indigo-650 hover:underline truncate inline-flex items-center justify-end gap-1">
                      <span class="truncate">{{ secretData.url }}</span>
                      <FeatherIcon name="external-link" class="w-3.5 h-3.5 shrink-0" />
                    </a>
                  </div>
                  <div v-if="secretData.username" class="flex items-center justify-between py-1 text-sm">
                    <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Username</span>
                    <span class="min-w-0 flex-1 text-right font-mono font-medium text-ink-gray-9 truncate">{{ secretData.username }}</span>
                  </div>
                  <div class="flex items-center justify-between py-1 text-sm">
                    <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Password</span>
                    <div class="min-w-0 flex-1 flex items-center justify-end gap-2">
                      <span class="font-mono tracking-wider font-medium text-ink-gray-9 truncate">
                        {{ showPassword ? decryptedData?.password : '••••••••••••' }}
                      </span>
                      <div class="flex items-center gap-0.5 shrink-0">
                        <button type="button" @click="togglePassword" class="p-1 text-ink-gray-4 hover:text-ink-gray-9 rounded" title="Reveal Password">
                          <FeatherIcon :name="showPassword ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                        </button>
                        <button v-if="canCopy" type="button" @click="copyPassword" class="p-1 text-ink-gray-4 hover:text-ink-gray-9 rounded" title="Copy Password">
                          <FeatherIcon :name="copiedField === 'password' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'password'}" />
                        </button>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- API Key fields -->
                <template v-else-if="secretData.secret_type === 'API Key'">
                  <div v-if="secretData.url" class="flex items-center justify-between py-1 text-sm">
                    <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Endpoint</span>
                    <a :href="secretData.url" target="_blank" class="min-w-0 flex-1 text-right font-medium text-indigo-650 hover:underline truncate inline-flex items-center justify-end gap-1">
                      <span class="truncate">{{ secretData.url }}</span>
                      <FeatherIcon name="external-link" class="w-3.5 h-3.5 shrink-0" />
                    </a>
                  </div>
                  <div v-if="secretData.api_key" class="flex items-center justify-between py-1 text-sm">
                    <span class="w-28 shrink-0 text-ink-gray-5 font-normal">API Key</span>
                    <span class="min-w-0 flex-1 text-right font-mono font-medium text-ink-gray-9 truncate">{{ secretData.api_key }}</span>
                  </div>
                  <div class="flex items-center justify-between py-1 text-sm">
                    <span class="w-28 shrink-0 text-ink-gray-5 font-normal">API Secret</span>
                    <div class="min-w-0 flex-1 flex items-center justify-end gap-2">
                      <span class="font-mono tracking-wider font-medium text-ink-gray-9 truncate">
                        {{ showAPISecret ? decryptedData?.api_secret : '••••••••••••' }}
                      </span>
                      <div class="flex items-center gap-0.5 shrink-0">
                        <button type="button" @click="toggleAPISecret" class="p-1 text-ink-gray-4 hover:text-ink-gray-9 rounded" title="Reveal API Secret">
                          <FeatherIcon :name="showAPISecret ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                        </button>
                        <button v-if="canCopy" type="button" @click="copyAPISecret" class="p-1 text-ink-gray-4 hover:text-ink-gray-9 rounded" title="Copy API Secret">
                          <FeatherIcon :name="copiedField === 'api_secret' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'api_secret'}" />
                        </button>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- Credit Card fields -->
                <template v-else-if="secretData.secret_type === 'Credit Card'">
                  <div v-if="secretData.card_holder" class="flex items-center justify-between py-1 text-sm">
                    <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Card Holder</span>
                    <span class="min-w-0 flex-1 text-right font-medium text-ink-gray-9 truncate">{{ secretData.card_holder }}</span>
                  </div>
                  <div class="flex items-center justify-between py-1 text-sm">
                    <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Card Number</span>
                    <div class="min-w-0 flex-1 flex items-center justify-end gap-2">
                      <span class="font-mono tracking-wider font-medium text-ink-gray-9 truncate">
                        {{ showCardNumber ? decryptedData?.card_number : '•••• •••• •••• ••••' }}
                      </span>
                      <div class="flex items-center gap-0.5 shrink-0">
                        <button type="button" @click="toggleCardNumber" class="p-1 text-ink-gray-4 hover:text-ink-gray-9 rounded" title="Reveal Card Number">
                          <FeatherIcon :name="showCardNumber ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                        </button>
                        <button v-if="canCopy" type="button" @click="copyCardNumber" class="p-1 text-ink-gray-4 hover:text-ink-gray-9 rounded" title="Copy Card Number">
                          <FeatherIcon :name="copiedField === 'card_number' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'card_number'}" />
                        </button>
                      </div>
                    </div>
                  </div>
                  <div v-if="secretData.card_expiry" class="flex items-center justify-between py-1 text-sm">
                    <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Expiry</span>
                    <span class="min-w-0 flex-1 text-right font-mono font-medium text-ink-gray-9 truncate">{{ secretData.card_expiry }}</span>
                  </div>
                  <div class="flex items-center justify-between py-1 text-sm">
                    <span class="w-28 shrink-0 text-ink-gray-5 font-normal">CVV</span>
                    <div class="min-w-0 flex-1 flex items-center justify-end gap-2">
                      <span class="font-mono tracking-wider font-medium text-ink-gray-9 truncate">
                        {{ showCardCVV ? decryptedData?.card_cvv : '•••' }}
                      </span>
                      <div class="flex items-center gap-0.5 shrink-0">
                        <button type="button" @click="toggleCardCVV" class="p-1 text-ink-gray-4 hover:text-ink-gray-9 rounded" title="Reveal CVV">
                          <FeatherIcon :name="showCardCVV ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                        </button>
                        <button v-if="canCopy" type="button" @click="copyCardCVV" class="p-1 text-ink-gray-4 hover:text-ink-gray-9 rounded" title="Copy CVV">
                          <FeatherIcon :name="copiedField === 'card_cvv' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'card_cvv'}" />
                        </button>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- Database fields -->
                <template v-else-if="secretData.secret_type === 'Database'">
                  <div v-if="secretData.db_host" class="flex items-center justify-between py-1 text-sm">
                    <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Host</span>
                    <span class="min-w-0 flex-1 text-right font-mono font-medium text-ink-gray-9 truncate">{{ secretData.db_host }}{{ secretData.db_port ? ':' + secretData.db_port : '' }}</span>
                  </div>
                  <div v-if="secretData.db_name" class="flex items-center justify-between py-1 text-sm">
                    <span class="w-28 shrink-0 text-ink-gray-5 font-normal">DB Name</span>
                    <span class="min-w-0 flex-1 text-right font-medium text-ink-gray-9 truncate">{{ secretData.db_name }}</span>
                  </div>
                  <div v-if="secretData.username" class="flex items-center justify-between py-1 text-sm">
                    <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Username</span>
                    <span class="min-w-0 flex-1 text-right font-mono font-medium text-ink-gray-9 truncate">{{ secretData.username }}</span>
                  </div>
                  <div class="flex items-center justify-between py-1 text-sm">
                    <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Password</span>
                    <div class="min-w-0 flex-1 flex items-center justify-end gap-2">
                      <span class="font-mono tracking-wider font-medium text-ink-gray-9 truncate">
                        {{ showDBPassword ? decryptedData?.db_password : '••••••••••••' }}
                      </span>
                      <div class="flex items-center gap-0.5 shrink-0">
                        <button type="button" @click="toggleDBPassword" class="p-1 text-ink-gray-4 hover:text-ink-gray-9 rounded" title="Reveal DB Password">
                          <FeatherIcon :name="showDBPassword ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                        </button>
                        <button v-if="canCopy" type="button" @click="copyDBPassword" class="p-1 text-ink-gray-4 hover:text-ink-gray-9 rounded" title="Copy DB Password">
                          <FeatherIcon :name="copiedField === 'db_password' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'db_password'}" />
                        </button>
                      </div>
                    </div>
                  </div>
                </template>

                <!-- SSH Key fields -->
                <template v-else-if="secretData.secret_type === 'SSH Key'">
                  <div v-if="secretData.username" class="flex items-center justify-between py-1 text-sm">
                    <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Username</span>
                    <span class="min-w-0 flex-1 text-right font-mono font-medium text-ink-gray-9 truncate">{{ secretData.username }}</span>
                  </div>
                  <div v-if="secretData.ssh_private_key" class="pt-2">
                    <span class="block text-xs font-semibold text-ink-gray-5 uppercase tracking-wider mb-1.5">SSH Private Key</span>
                    <div class="relative bg-surface-gray-2 border border-outline-gray-1 rounded-xl p-3 group shadow-inner">
                      <pre class="text-xs font-mono text-ink-gray-8 overflow-x-auto max-h-36 whitespace-pre select-all leading-normal">{{ secretData.ssh_private_key }}</pre>
                      <button v-if="canCopy" type="button" @click="copyField(secretData.ssh_private_key, 'ssh_private_key')" class="absolute top-2 right-2 px-2 py-1 bg-surface-base border border-outline-gray-1 rounded-md text-xs font-medium text-ink-gray-7 opacity-0 group-hover:opacity-100 transition-opacity shadow-2xs flex items-center gap-1">
                        <FeatherIcon :name="copiedField === 'ssh_private_key' ? 'check' : 'copy'" class="w-3 h-3" :class="{'text-green-600': copiedField === 'ssh_private_key'}" />
                        <span>Copy</span>
                      </button>
                    </div>
                  </div>
                </template>

                <!-- Certificate fields -->
                <template v-else-if="secretData.secret_type === 'Certificate'">
                  <div v-if="secretData.certificate" class="pt-2">
                    <span class="block text-xs font-semibold text-ink-gray-5 uppercase tracking-wider mb-1.5">Certificate</span>
                    <div class="relative bg-surface-gray-2 border border-outline-gray-1 rounded-xl p-3 group shadow-inner">
                      <pre class="text-xs font-mono text-ink-gray-8 overflow-x-auto max-h-36 whitespace-pre select-all leading-normal">{{ secretData.certificate }}</pre>
                      <button v-if="canCopy" type="button" @click="copyField(secretData.certificate, 'certificate')" class="absolute top-2 right-2 px-2 py-1 bg-surface-base border border-outline-gray-1 rounded-md text-xs font-medium text-ink-gray-7 opacity-0 group-hover:opacity-100 transition-opacity shadow-2xs flex items-center gap-1">
                        <FeatherIcon :name="copiedField === 'certificate' ? 'check' : 'copy'" class="w-3 h-3" :class="{'text-green-600': copiedField === 'certificate'}" />
                        <span>Copy</span>
                      </button>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </div>

          <!-- Collapsible NOTES Accordion -->
          <div v-if="secretData.notes" class="border-b border-outline-gray-1 py-4 px-6">
            <div class="flex items-center justify-between select-none cursor-pointer" @click="notesOpen = !notesOpen">
              <div class="flex items-center gap-2.5">
                <FeatherIcon name="chevron-down" class="h-5 w-5 text-ink-gray-5 transition-transform duration-200" :class="{ '-rotate-90': !notesOpen }" />
                <h3 class="text-base font-bold text-ink-gray-9">Notes</h3>
              </div>
            </div>
            
            <div v-show="notesOpen" class="mt-2.5 py-1 text-sm text-ink-gray-8 leading-relaxed whitespace-pre-wrap font-normal" v-html="secretData.notes" />
          </div>

          <!-- Collapsible METADATA Accordion -->
          <div class="border-b border-outline-gray-1 py-4 px-6">
            <div class="flex items-center justify-between select-none cursor-pointer" @click="metaOpen = !metaOpen">
              <div class="flex items-center gap-2.5">
                <FeatherIcon name="chevron-down" class="h-5 w-5 text-ink-gray-5 transition-transform duration-200" :class="{ '-rotate-90': !metaOpen }" />
                <h3 class="text-base font-bold text-ink-gray-9">Metadata</h3>
              </div>
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
          </div>
          </div>
        </div>
      </div>
      
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
                { label: 'Group', value: 'Group', class: 'flex-1 !justify-center', onClick: () => { newShareRecipient = '' } },
                { label: 'Role', value: 'Role', class: 'flex-1 !justify-center', onClick: () => { newShareRecipient = '' } }
              ]"
              class="w-full !flex"
            />
          </div>

          <!-- Recipient Selection -->
          <FormControl
            :label="`Select ${newShareType}`"
            type="select"
            v-model="newShareRecipient"
            :options="recipientOptions"
          />

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
          :disabled="!newShareRecipient"
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
            <span class="font-bold text-ink-gray-9">{{ shareToRevoke?.share_type === 'User' ? shareToRevoke?.user : shareToRevoke?.share_type === 'Group' ? shareToRevoke?.group : shareToRevoke?.frappe_role }}</span>?
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
  </div>
</template>

<script setup>
import { ref, computed, reactive, watch } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Badge, FeatherIcon, TextInput, FormControl, Dialog, ErrorMessage, Breadcrumbs, Tooltip, toast, TabButtons, Tabs } from 'frappe-ui'
import { mobileSidebarOpened, useSecret, useDecryptSecret, useSecretActivity, useDeleteSecret, useUpdateSecret, useShareSecret, useUnshare, useSecretShares, useShareOptions, useVaultStats, useFolders } from '../composables/vault'
import { useClipboard } from '../composables/clipboard'
import EmptyState from '../components/EmptyState.vue'
import StrengthBadge from '../components/StrengthBadge.vue'
import { actionIcons, secretTypeOptions, permissionTheme, typeMeta, formatRelativeTime } from '../composables/constants'

const props = defineProps({
  name: {
    type: String,
    required: true,
  }
})

const router = useRouter()

const activeTabIndex = ref(0)
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
const showPassword = ref(false)
const showAPISecret = ref(false)
const showCardNumber = ref(false)
const showCardCVV = ref(false)
const showDBPassword = ref(false)

// Sensitive fields type toggle flags (Edit view)
const showEditPassword = ref(false)
const showEditAPISecret = ref(false)
const showEditCardNumber = ref(false)
const showEditCardCVV = ref(false)
const showEditDBPassword = ref(false)

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
const shareOptions = computed(() => shareOptionsResource.data || { users: [], groups: [], roles: [] })

const recipientOptions = computed(() => {
  const owner = secretData.value?.owner
  let list = newShareType.value === 'User' 
    ? shareOptions.value.users 
    : newShareType.value === 'Group' 
      ? shareOptions.value.groups 
      : shareOptions.value.roles
      
  if (newShareType.value === 'User' && owner) {
    list = list.filter(item => item.value !== owner)
  }
  
  return [{ label: 'Choose recipient...', value: '' }, ...list]
})

// Sharing Form State
const newShareType = ref('User') // 'User', 'Group', 'Role'
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
  if (roles.includes('Vault Admin') || roles.includes('System Manager')) return true
  return secretData.value?.owner === currentSessionUser.value
})

const userPermission = computed(() => secretData.value?.user_permission || 'View Only')

const canEdit = computed(() => {
  if (stats.data?.is_admin) return true
  if (currentSessionUser.value === 'Administrator') return true
  const roles = window.frappe?.user_roles || window.frappe?.boot?.user?.roles || []
  if (roles.includes('Vault Admin') || roles.includes('System Manager')) return true
  if (secretData.value?.owner === currentSessionUser.value) return true
  return ['Edit', 'Full Control'].includes(userPermission.value)
})

const canDelete = computed(() => {
  if (stats.data?.is_admin) return true
  if (currentSessionUser.value === 'Administrator') return true
  const roles = window.frappe?.user_roles || window.frappe?.boot?.user?.roles || []
  if (roles.includes('Vault Admin') || roles.includes('System Manager')) return true
  if (secretData.value?.owner === currentSessionUser.value) return true
  return userPermission.value === 'Full Control'
})

const canCopy = computed(() => {
  if (stats.data?.is_admin) return true
  if (currentSessionUser.value === 'Administrator') return true
  const roles = window.frappe?.user_roles || window.frappe?.boot?.user?.roles || []
  if (roles.includes('Vault Admin') || roles.includes('System Manager')) return true
  if (secretData.value?.owner === currentSessionUser.value) return true
  return ['View & Copy', 'Edit', 'Full Control'].includes(userPermission.value)
})



function openShareDialog() {
  newShareType.value = 'User'
  newShareRecipient.value = ''
  newSharePermission.value = 'View Only'
  newShareExpiresOn.value = ''
  showShareDialog.value = true
  shareOptionsResource.fetch()
}

async function handleShareSecret() {
  if (!newShareRecipient.value) {
    toast.error('Please select a recipient')
    return
  }

  isSharing.value = true
  try {
    await shareResource.submit({
      shared_name: props.name,
      shared_doctype: 'Vault Secret',
      share_type: newShareType.value,
      user: newShareType.value === 'User' ? newShareRecipient.value : undefined,
      group: newShareType.value === 'Group' ? newShareRecipient.value : undefined,
      frappe_role: newShareType.value === 'Role' ? newShareRecipient.value : undefined,
      permission_level: newSharePermission.value,
      expires_on: newShareExpiresOn.value || undefined,
    })

    toast.success(`Secret shared successfully with ${newShareRecipient.value}`)

    // Reset fields and close
    newShareRecipient.value = ''
    newShareExpiresOn.value = ''
    showShareDialog.value = false
    await sharesResource.fetch({ secret_name: props.name })
    activity.reload()
  } catch (err) {
    console.error(err)
    toast.error(err.messages?.[0] || err.message || 'Failed to share secret')
  } finally {
    isSharing.value = false
  }
}

function confirmRevokeShare(item) {
  shareToRevoke.value = item
  showRevokeConfirm.value = true
}

async function handleRevokeShare() {
  if (!shareToRevoke.value) return
  const recipientName = shareToRevoke.value.share_type === 'User' ? shareToRevoke.value.user : shareToRevoke.value.share_type === 'Group' ? shareToRevoke.value.group : shareToRevoke.value.frappe_role
  try {
    await unshareResource.submit({ share_name: shareToRevoke.value.name })
    toast.success(`Revoked access for ${recipientName}`)
    showRevokeConfirm.value = false
    shareToRevoke.value = null
    await sharesResource.fetch({ secret_name: props.name })
    activity.reload()
  } catch (err) {
    console.error(err)
    toast.error(err.message || 'Failed to revoke access')
  }
}



const folderOptions = computed(() => {
  const options = [{ label: 'No Folder', value: '' }]
  if (folders.data) {
    folders.data.forEach(f => {
      options.push({ label: f.folder_name, value: f.name })
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
  certificate: '',
})

watch(() => props.name, (n) => {
  if (n) {
    secret.submit({ name: n })
    activity.submit({ secret_name: n })
    showPassword.value = false
    showAPISecret.value = false
    showCardNumber.value = false
    showCardCVV.value = false
    showDBPassword.value = false
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
async function togglePassword() {
  if (showPassword.value) {
    showPassword.value = false
    return
  }
  await ensureDecrypted(() => {
    showPassword.value = true
  })
}

async function copyPassword() {
  await ensureDecrypted(() => {
    if (decryptedData.value?.password) {
      copyField(decryptedData.value.password, 'password')
    } else {
      toast.error('Password field is empty')
    }
  })
}

async function toggleAPISecret() {
  if (showAPISecret.value) {
    showAPISecret.value = false
    return
  }
  await ensureDecrypted(() => {
    showAPISecret.value = true
  })
}

async function copyAPISecret() {
  await ensureDecrypted(() => {
    if (decryptedData.value?.api_secret) {
      copyField(decryptedData.value.api_secret, 'api_secret')
    } else {
      toast.error('API Secret field is empty')
    }
  })
}

async function toggleCardNumber() {
  if (showCardNumber.value) {
    showCardNumber.value = false
    return
  }
  await ensureDecrypted(() => {
    showCardNumber.value = true
  })
}

async function copyCardNumber() {
  await ensureDecrypted(() => {
    if (decryptedData.value?.card_number) {
      copyField(decryptedData.value.card_number, 'card_number')
    } else {
      toast.error('Card number field is empty')
    }
  })
}

async function toggleCardCVV() {
  if (showCardCVV.value) {
    showCardCVV.value = false
    return
  }
  await ensureDecrypted(() => {
    showCardCVV.value = true
  })
}

async function copyCardCVV() {
  await ensureDecrypted(() => {
    if (decryptedData.value?.card_cvv) {
      copyField(decryptedData.value.card_cvv, 'card_cvv')
    } else {
      toast.error('CVV field is empty')
    }
  })
}

async function toggleDBPassword() {
  if (showDBPassword.value) {
    showDBPassword.value = false
    return
  }
  await ensureDecrypted(() => {
    showDBPassword.value = true
  })
}

async function copyDBPassword() {
  await ensureDecrypted(() => {
    if (decryptedData.value?.db_password) {
      copyField(decryptedData.value.db_password, 'db_password')
    } else {
      toast.error('Database Password field is empty')
    }
  })
}

async function toggleEditMode() {
  if (isEditing.value) {
    isEditing.value = false
    return
  }

  await ensureDecrypted(() => {
    showEditPassword.value = false
    showEditAPISecret.value = false
    showEditCardNumber.value = false
    showEditCardCVV.value = false
    showEditDBPassword.value = false

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
    editForm.certificate = sd.certificate || ''

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
    } else if (editForm.secret_type === 'Certificate') {
      payload.certificate = editForm.certificate
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
    console.error('Save failed:', e)
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
    console.error('Delete failed:', err)
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
