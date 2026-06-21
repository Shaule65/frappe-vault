<template>
  <div class="flex-1 flex flex-col overflow-hidden bg-gray-50/20">
    
    <!-- Page Header (Identical to CRM splitscreen headers) -->
    <header class="flex h-10.5 items-center justify-between border-b bg-white px-5 py-2.5 shrink-0">
      <!-- Breadcrumbs -->
      <div class="flex items-center gap-2 text-lg font-medium min-w-0 flex-1">
        <!-- Mobile Sidebar Trigger -->
        <Button
          class="size-7 sm:hidden flex items-center justify-center p-0 mr-1 focus:outline-none shrink-0"
          variant="ghost"
          @click="mobileSidebarOpened = true"
        >
          <template #icon>
            <FeatherIcon name="menu" class="w-4.5 h-4.5 text-ink-gray-9" />
          </template>
        </Button>

        <Breadcrumbs :items="breadcrumbs" class="min-w-0" />
      </div>
      
      <!-- Right actions -->
      <div class="flex items-center gap-2 shrink-0">
      </div>
    </header>

    <!-- Splitscreen Main Content Body (Exact CRM split match) -->
    <div v-if="secretData" class="flex-1 flex overflow-hidden min-h-0">
      
      <!-- LEFT PANE: Tab navigation & Activity timeline feed -->
      <div class="flex-1 flex flex-col overflow-hidden bg-white border-r border-gray-100">
        <!-- Borderless navigation tabs (matching CRM layout) -->
        <div class="flex items-center gap-7.5 px-6 border-b border-gray-100 bg-white shrink-0 min-h-[45px]">
          <button
            v-for="t in tabs"
            :key="t.name"
            class="py-3.5 text-sm font-medium relative focus:outline-none transition-colors"
            :class="activeTab === t.name ? 'text-ink-gray-9 font-semibold' : 'text-gray-500 hover:text-gray-900'"
            @click="activeTab = t.name"
          >
            <span>{{ t.label }}</span>
            <span
              v-if="activeTab === t.name"
              class="absolute bottom-0 left-0 right-0 h-0.5 bg-gray-950 rounded-full"
            />
          </button>
        </div>

        <!-- Tab Panel content container -->
        <div class="flex-1 overflow-y-auto p-6 min-h-0">
          
          <!-- Activity feed timeline panel -->
          <div v-if="activeTab === 'activity'" class="space-y-6">
            <div class="flex items-center justify-between border-b border-gray-100 pb-3 mb-5">
              <h3 class="text-base font-semibold text-gray-900">Activity Timeline</h3>
            </div>
            
            <div v-if="activity.loading" class="space-y-4">
              <div v-for="i in 3" :key="i" class="h-16 bg-gray-50/50 border border-gray-100 rounded-xl animate-pulse" />
            </div>
            
            <div v-else-if="activityList.length" class="relative border-l border-gray-100 ml-4 pl-6 space-y-6 py-2">
              <div v-for="item in activityList" :key="item.name" class="relative flex items-start gap-4">
                <!-- Dot marker -->
                <span class="absolute -left-[31px] top-2 w-2.5 h-2.5 rounded-full border-2 border-white bg-gray-450 ring-4 ring-white" />
                
                <div class="w-8.5 h-8.5 rounded-full border border-gray-100 bg-gray-50 flex items-center justify-center shrink-0 shadow-sm">
                  <FeatherIcon :name="actionIcons[item.action] || 'activity'" class="w-4 h-4 text-gray-500" />
                </div>
                <div class="min-w-0 flex-1">
                  <p class="text-sm text-gray-800 leading-snug mt-0.5">
                    <span class="font-bold text-gray-950">{{ item.user }}</span>
                    &nbsp;{{ getActivityText(item) }}
                  </p>
                  <p class="text-xs text-gray-400 mt-1 font-medium">{{ formatTime(item.timestamp) }}</p>
                </div>
              </div>
            </div>
            
            <EmptyState v-else icon="activity" title="No activity recorded" />
          </div>

          <!-- Sharing config panel -->
          <div v-else-if="activeTab === 'sharing'" class="space-y-5 max-w-xl">
            <div class="flex items-center justify-between border-b border-gray-100 pb-3 shrink-0">
              <h3 class="text-base font-semibold text-gray-950">Sharing Settings</h3>
              
              <!-- Share Secret Button (Visible if Owner or Admin) -->
              <Button
                v-if="isOwnerOrAdmin"
                variant="solid"
                size="sm"
                class="shadow-sm font-semibold"
                @click="openShareDialog"
              >
                <template #prefix><FeatherIcon name="user-plus" class="w-3.5 h-3.5" /></template>
                <span>Share Secret</span>
              </Button>
            </div>

            <!-- If Not Owner or Admin, show who shared it with them -->
            <div v-if="!isOwnerOrAdmin" class="p-4 bg-gray-50/70 border border-gray-100/50 rounded-xl text-sm leading-relaxed text-ink-gray-7 font-medium shadow-sm flex items-start gap-3">
              <div class="w-9 h-9 rounded-full bg-blue-50 border border-blue-100/50 text-blue-650 flex items-center justify-center shrink-0">
                <FeatherIcon name="share-2" class="w-4.5 h-4.5" />
              </div>
              <div>
                <p class="font-bold text-gray-900 leading-normal">Shared Secret Access</p>
                <p class="mt-1 text-ink-gray-6 font-normal">
                  This secret was shared with you by <strong class="text-ink-gray-8">{{ secretData.owner }}</strong>. You have <strong class="text-ink-gray-8">{{ secretData.permission_level || 'View Only' }}</strong> rights on this secret.
                </p>
              </div>
            </div>

            <div v-else class="space-y-4">
              <!-- Active Shares List -->
              <div class="text-xs font-bold text-gray-500 uppercase tracking-wider pl-0.5">Active Shares</div>

              <div v-if="sharesList.length" class="space-y-3">
                <div
                  v-for="item in sharesList"
                  :key="item.name"
                  class="flex items-center justify-between p-3.5 bg-white border border-gray-100 rounded-xl shadow-sm hover:border-gray-200 transition-colors"
                >
                  <div class="flex items-center gap-3.5 min-w-0">
                    <div class="w-9 h-9 rounded-full bg-gray-50 border border-gray-100 shadow-sm flex items-center justify-center shrink-0">
                      <FeatherIcon
                        :name="item.share_type === 'User' ? 'user' : item.share_type === 'Group' ? 'users' : 'shield'"
                        class="w-4.5 h-4.5 text-gray-500"
                      />
                    </div>
                    <div class="min-w-0">
                      <p class="text-sm font-semibold text-gray-900 truncate leading-snug">
                        {{ item.share_type === 'User' ? item.user : item.share_type === 'Group' ? item.group : item.frappe_role }}
                      </p>
                      <p class="text-xs text-gray-400 mt-1 font-medium flex items-center gap-1.5 leading-none">
                        <span>{{ item.share_type }}</span>
                        <span class="w-1 h-1 rounded-full bg-gray-300" />
                        <span v-if="item.expires_on">Expires {{ formatTime(item.expires_on) }}</span>
                        <span v-else>Never expires</span>
                      </p>
                    </div>
                  </div>

                  <div class="flex items-center gap-3 shrink-0">
                    <Badge
                      :theme="permissionTheme[item.permission_level] || 'gray'"
                      variant="subtle"
                      size="sm"
                    >
                      {{ item.permission_level }}
                    </Badge>

                    <!-- Revoke Access Action -->
                    <button
                      class="p-1.5 rounded hover:bg-red-50 text-ink-gray-4 hover:text-ink-red-3 transition-colors focus:outline-none"
                      title="Revoke Access"
                      @click="handleRevokeShare(item.name, item.share_type === 'User' ? item.user : item.share_type === 'Group' ? item.group : item.frappe_role)"
                    >
                      <FeatherIcon name="trash-2" class="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>

              <!-- Active Shares Empty State -->
              <div v-else class="p-8 bg-gray-50 border border-dashed border-gray-200 rounded-2xl text-center shadow-sm">
                <div class="w-10 h-10 rounded-full bg-gray-100 border border-gray-200/50 flex items-center justify-center mx-auto text-gray-400 mb-3 shrink-0">
                  <FeatherIcon name="users" class="w-5 h-5" />
                </div>
                <p class="text-sm font-semibold text-gray-900 leading-snug">Not Shared Yet</p>
                <p class="text-xs text-gray-500 mt-1 max-w-[280px] mx-auto leading-normal font-medium">
                  This secret is private. Use the Share button to give access to other users, groups, or roles.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- RIGHT PANE: Resizable Side Panel Drawer (off-white bg, bordered) -->
      <div class="w-[380px] shrink-0 flex flex-col overflow-y-auto border-l flex-1 lg:flex-none bg-white">
        
        <!-- Sidebar ID Header (matching CRM Resizer top row) -->
        <div
          class="flex h-[45px] cursor-copy items-center border-b px-5 py-2.5 text-lg font-medium text-ink-gray-9"
          @click="copyField(secretData.name, 'name')"
        >
          {{ secretData.name }}
        </div>

        <!-- Avatar + Title + Quick Actions (matching CRM Lead detail panel) -->
        <div class="flex items-center justify-start gap-5 border-b p-5">
          <!-- Circular type avatar icon -->
          <div :class="`size-12 rounded-full border flex items-center justify-center shrink-0 shadow-sm ${typeMeta[secretData.secret_type || 'Other']?.bg}`">
            <FeatherIcon :name="typeMeta[secretData.secret_type || 'Other']?.icon" class="w-5.5 h-5.5" />
          </div>
          
          <div class="flex flex-col gap-2.5 truncate">
            <Tooltip :text="secretData.title">
              <div class="truncate text-2xl font-medium text-ink-gray-9">
                {{ secretData.title }}
              </div>
            </Tooltip>
            <div class="flex gap-1.5">
              <!-- Quick action buttons row (matching CRM Lead action row) -->
              <Button
                v-if="secretData.username"
                :tooltip="'Copy Username'"
                icon="user"
                @click="copyField(secretData.username, 'username')"
              />
              <Button
                v-if="secretData.secret_type === 'Password' && canCopy"
                :tooltip="'Copy Password'"
                icon="key"
                @click="copyPassword"
              />
              <Button
                v-if="secretData.secret_type === 'API Key' && canCopy"
                :tooltip="'Copy API Secret'"
                icon="code"
                @click="copyAPISecret"
              />
              <Button
                v-if="secretData.url"
                :tooltip="'Open URL'"
                icon="external-link"
                @click="window.open(secretData.url, '_blank')"
              />
              <Button
                v-if="canDelete"
                :tooltip="'Delete'"
                variant="subtle"
                theme="red"
                icon="trash-2"
                @click="showDeleteDialog = true"
              />
            </div>
          </div>
        </div>

        <!-- Edit Mode Toggle (below avatar, matching CRM pattern) -->
        <div v-if="canEdit" class="px-5 py-3 border-b flex items-center justify-end shrink-0">
          <Button
            variant="outline"
            size="sm"
            @click="toggleEditMode"
            :class="isEditing ? 'bg-surface-gray-2 text-ink-gray-9 font-bold border-outline-gray-3' : 'text-ink-gray-7 hover:bg-surface-gray-1'"
          >
            <template #prefix>
              <FeatherIcon :name="isEditing ? 'eye' : 'edit-2'" class="w-3.5 h-3.5" />
            </template>
            <span>{{ isEditing ? 'View' : 'Edit' }}</span>
          </Button>
        </div>

        <div class="flex flex-1 flex-col justify-between overflow-hidden">
          <div class="flex-1 overflow-y-auto p-1 sm:p-3">
          
          <!-- Clipboard clear warning indicator -->
          <div v-if="clipboard.copied.value" class="flex items-center gap-2.5 p-3 mx-2 bg-amber-50/70 text-amber-800 rounded-xl text-xs font-semibold border border-amber-100/40 shadow-sm transition-all duration-300 mb-2">
            <FeatherIcon name="shield" class="w-4 h-4 text-amber-600 animate-pulse shrink-0" />
            <span class="flex-1">Clipboard copied. Auto-clearing in <strong>{{ clipboard.countdown.value }}s</strong>.</span>
          </div>

          <!-- EDIT VIEW FORM (CRM SIDEBAR SPLIT) -->
          <div v-if="isEditing" class="space-y-5">
            <!-- Title -->
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Title <span class="text-red-550">*</span></label>
              <div class="w-[65%]">
                <TextInput v-model="editForm.title" placeholder="Secret Title" class="w-full text-sm" />
              </div>
            </div>

            <!-- Type select -->
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Type</label>
              <div class="w-[65%]">
                <FormControl v-model="editForm.secret_type" type="select" :options="secretTypeOptions" class="w-full text-sm cursor-pointer" />
              </div>
            </div>

            <!-- Folder select -->
            <div class="flex items-center justify-between min-h-[38px]">
              <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Folder</label>
              <div class="w-[65%]">
                <FormControl v-model="editForm.folder" type="select" :options="folderOptions" class="w-full text-sm cursor-pointer" />
              </div>
            </div>

            <div class="w-full border-t border-gray-100 my-4" />

            <!-- Dynamic type inputs -->
            <!-- PASSWORD TYPE -->
            <div v-if="editForm.secret_type === 'Password'" class="space-y-4">
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Username</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.username" placeholder="Username" class="w-full text-sm" />
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Password</label>
                <div class="w-[65%] relative">
                  <TextInput :type="showEditPassword ? 'text' : 'password'" v-model="editForm.password" placeholder="Password" class="w-full text-sm pr-10" />
                  <Button variant="ghost" size="sm" class="absolute right-2 top-1.5 text-gray-400 hover:text-gray-650" @click="showEditPassword = !showEditPassword">
                    <FeatherIcon :name="showEditPassword ? 'eye-off' : 'eye'" class="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">URL</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.url" placeholder="https://example.com" class="w-full text-sm" />
                </div>
              </div>
            </div>

            <!-- API KEY TYPE -->
            <div v-else-if="editForm.secret_type === 'API Key'" class="space-y-4">
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">API Key</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.api_key" placeholder="API Key" class="w-full text-sm" />
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">API Secret</label>
                <div class="w-[65%] relative">
                  <TextInput :type="showEditAPISecret ? 'text' : 'password'" v-model="editForm.api_secret" placeholder="API Secret" class="w-full text-sm pr-10" />
                  <Button variant="ghost" size="sm" class="absolute right-2 top-1.5 text-gray-400 hover:text-gray-650" @click="showEditAPISecret = !showEditAPISecret">
                    <FeatherIcon :name="showEditAPISecret ? 'eye-off' : 'eye'" class="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">URL</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.url" placeholder="https://api.example.com" class="w-full text-sm" />
                </div>
              </div>
            </div>

            <!-- CREDIT CARD TYPE -->
            <div v-else-if="editForm.secret_type === 'Credit Card'" class="space-y-4">
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Card Holder</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.card_holder" placeholder="Holder Name" class="w-full text-sm" />
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Card Number</label>
                <div class="w-[65%] relative">
                  <TextInput :type="showEditCardNumber ? 'text' : 'password'" v-model="editForm.card_number" placeholder="Card Number" class="w-full text-sm pr-10" />
                  <Button variant="ghost" size="sm" class="absolute right-2 top-1.5 text-gray-400 hover:text-gray-655" @click="showEditCardNumber = !showEditCardNumber">
                    <FeatherIcon :name="showEditCardNumber ? 'eye-off' : 'eye'" class="w-4 h-4" />
                  </Button>
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Expiry</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.card_expiry" placeholder="MM/YY" class="w-full text-sm" />
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">CVV</label>
                <div class="w-[65%] relative">
                  <TextInput :type="showEditCardCVV ? 'text' : 'password'" v-model="editForm.card_cvv" placeholder="CVV" class="w-full text-sm pr-10" />
                  <Button variant="ghost" size="sm" class="absolute right-2 top-1.5 text-gray-400 hover:text-gray-655" @click="showEditCardCVV = !showEditCardCVV">
                    <FeatherIcon :name="showEditCardCVV ? 'eye-off' : 'eye'" class="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>

            <!-- DATABASE TYPE -->
            <div v-else-if="editForm.secret_type === 'Database'" class="space-y-4">
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Host</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.db_host" placeholder="localhost" class="w-full text-sm" />
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Port</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.db_port" placeholder="3306" class="w-full text-sm" />
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">DB Name</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.db_name" placeholder="my_database" class="w-full text-sm" />
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Username</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.username" placeholder="Username" class="w-full text-sm" />
                </div>
              </div>
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Password</label>
                <div class="w-[65%] relative">
                  <TextInput :type="showEditDBPassword ? 'text' : 'password'" v-model="editForm.db_password" placeholder="Password" class="w-full text-sm pr-10" />
                  <Button variant="ghost" size="sm" class="absolute right-2 top-1.5 text-gray-400 hover:text-gray-655" @click="showEditDBPassword = !showEditDBPassword">
                    <FeatherIcon :name="showEditDBPassword ? 'eye-off' : 'eye'" class="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>

            <!-- SSH KEY TYPE -->
            <div v-else-if="editForm.secret_type === 'SSH Key'" class="space-y-4">
              <div class="flex items-center justify-between min-h-[38px]">
                <label class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Username</label>
                <div class="w-[65%]">
                  <TextInput v-model="editForm.username" placeholder="e.g. root" class="w-full text-sm" />
                </div>
              </div>
              <div class="space-y-1.5 pt-1.5">
                <label class="block text-sm text-ink-gray-5 mb-1.5">Private Key</label>
                <textarea v-model="editForm.ssh_private_key" rows="6" placeholder="-----BEGIN OPENSSH KEY-----" class="w-full rounded border border-gray-200 bg-white p-3 text-xs font-mono text-gray-800 placeholder-gray-450 focus:outline-none focus:ring-1 focus:ring-gray-900 focus:border-gray-900 shadow-inner" />
              </div>
            </div>

            <!-- CERTIFICATE TYPE -->
            <div v-else-if="editForm.secret_type === 'Certificate'" class="space-y-1.5 pt-1.5">
              <label class="block text-sm text-ink-gray-5 mb-1.5">Certificate Content</label>
              <textarea v-model="editForm.certificate" rows="6" placeholder="-----BEGIN CERTIFICATE-----" class="w-full rounded border border-gray-200 bg-white p-3 text-xs font-mono text-gray-800 placeholder-gray-455 focus:outline-none focus:ring-1 focus:ring-gray-900 focus:border-gray-900 shadow-inner" />
            </div>

            <!-- Stacked Notes Box -->
            <div class="space-y-1.5 pt-1.5">
              <label class="block text-sm text-ink-gray-5 mb-1.5">Notes</label>
              <textarea v-model="editForm.notes" rows="4" placeholder="Enter notes..." class="w-full rounded border border-gray-200 bg-white p-3 text-sm text-gray-850 placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-gray-900 focus:border-gray-900 shadow-inner" />
            </div>

            <!-- Edit Sticky Buttons -->
            <div class="flex items-center justify-end gap-3 pt-3 border-t border-gray-100">
              <Button variant="outline" @click="isEditing = false" class="text-gray-700 hover:bg-gray-100">Cancel</Button>
              <Button variant="solid" @click="handleSave" :loading="updateResource.loading" class="font-semibold shadow-sm px-4">Save Changes</Button>
            </div>
          </div>

          <!-- READ ONLY VIEW COLLAPSIBLES (CRM STYLE DETAILS DRAWER) -->
          <template v-else>
            
            <!-- Collapsible DETAILS Accordion -->
            <div class="section border-b pb-1">
              <div class="section-header flex h-8 items-center justify-between">
                <div
                  class="flex text-ink-gray-9 max-w-fit cursor-pointer items-center gap-2 text-base px-2 font-semibold select-none"
                  @click="detailsOpen = !detailsOpen"
                >
                  <FeatherIcon
                    name="chevron-right"
                    class="h-4 w-4 transition-all duration-300 ease-in-out text-ink-gray-5"
                    :class="{ 'rotate-90': detailsOpen }"
                  />
                  <span>Details</span>
                </div>
              </div>

              <div v-show="detailsOpen" class="space-y-1">
                <!-- Secret Type -->
                <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                  <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Secret Type</div>
                  <div class="w-[65%] flex items-center justify-start min-w-0">
                    <Badge size="md" variant="subtle" :theme="secretData.secret_type === 'Password' ? 'green' : 'gray'">
                      {{ secretData.secret_type }}
                    </Badge>
                  </div>
                </div>

                <!-- Folder -->
                <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                  <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Folder</div>
                  <div class="w-[65%] flex items-center justify-start min-w-0 text-base text-ink-gray-9 truncate">
                    {{ getFolderName(secretData.folder) || '—' }}
                  </div>
                </div>

                <!-- Password Type specific fields -->
                <div v-if="secretData.secret_type === 'Password'" class="space-y-1">
                  <div v-if="secretData.url" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">URL</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <a :href="secretData.url" target="_blank" class="text-sm font-semibold text-indigo-650 hover:text-indigo-800 hover:underline truncate mr-2 inline-flex items-center gap-1">
                        <span>{{ secretData.url }}</span>
                        <FeatherIcon name="external-link" class="w-3.5 h-3.5" />
                      </a>
                    </div>
                  </div>
                  <div v-if="secretData.username" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Username</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-base text-ink-gray-9 font-mono truncate mr-2">{{ secretData.username }}</span>
                    </div>
                  </div>
                  <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Password</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-base text-ink-gray-9 font-mono tracking-wider truncate mr-2">
                        {{ showPassword ? decryptedData?.password : '••••••••••••' }}
                      </span>
                      <div class="flex items-center gap-0.5 shrink-0">
                        <Button variant="ghost" size="sm" @click="togglePassword" class="text-gray-400 hover:text-gray-650" tooltip="Reveal Password">
                          <FeatherIcon :name="showPassword ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                        </Button>
                        <Button v-if="canCopy" variant="ghost" size="sm" @click="copyPassword" class="text-gray-400 hover:text-gray-650" tooltip="Copy Password">
                          <FeatherIcon :name="copiedField === 'password' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'password'}" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- API Key specific fields -->
                <div v-else-if="secretData.secret_type === 'API Key'" class="space-y-1">
                  <div v-if="secretData.url" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Endpoint</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <a :href="secretData.url" target="_blank" class="text-sm font-semibold text-indigo-650 hover:text-indigo-800 hover:underline truncate mr-2 inline-flex items-center gap-1">
                        <span>{{ secretData.url }}</span>
                        <FeatherIcon name="external-link" class="w-3.5 h-3.5" />
                      </a>
                    </div>
                  </div>
                  <div v-if="secretData.api_key" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">API Key</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-base text-ink-gray-9 font-mono truncate mr-2">{{ secretData.api_key }}</span>
                    </div>
                  </div>
                  <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">API Secret</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-base text-ink-gray-9 font-mono tracking-wider truncate mr-2">
                        {{ showAPISecret ? decryptedData?.api_secret : '••••••••••••' }}
                      </span>
                      <div class="flex items-center gap-0.5 shrink-0">
                        <Button variant="ghost" size="sm" @click="toggleAPISecret" class="text-gray-400 hover:text-gray-650" tooltip="Reveal API Secret">
                          <FeatherIcon :name="showAPISecret ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                        </Button>
                        <Button v-if="canCopy" variant="ghost" size="sm" @click="copyAPISecret" class="text-gray-400 hover:text-gray-650" tooltip="Copy API Secret">
                          <FeatherIcon :name="copiedField === 'api_secret' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'api_secret'}" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Credit Card specific fields -->
                <div v-else-if="secretData.secret_type === 'Credit Card'" class="space-y-1">
                  <div v-if="secretData.card_holder" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Card Holder</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-base text-ink-gray-9 truncate mr-2">{{ secretData.card_holder }}</span>
                    </div>
                  </div>
                  <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Card Number</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-base text-ink-gray-9 font-mono tracking-wider truncate mr-2">
                        {{ showCardNumber ? decryptedData?.card_number : '•••• •••• •••• ••••' }}
                      </span>
                      <div class="flex items-center gap-0.5 shrink-0">
                        <Button variant="ghost" size="sm" @click="toggleCardNumber" class="text-gray-400 hover:text-gray-650" tooltip="Reveal Card Number">
                          <FeatherIcon :name="showCardNumber ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                        </Button>
                        <Button v-if="canCopy" variant="ghost" size="sm" @click="copyCardNumber" class="text-gray-400 hover:text-gray-650" tooltip="Copy Card Number">
                          <FeatherIcon :name="copiedField === 'card_number' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'card_number'}" />
                        </Button>
                      </div>
                    </div>
                  </div>
                  <div v-if="secretData.card_expiry" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Expiry</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-base text-ink-gray-9 font-mono truncate mr-2">{{ secretData.card_expiry }}</span>
                    </div>
                  </div>
                  <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">CVV</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-base text-ink-gray-9 font-mono tracking-wider truncate mr-2">
                        {{ showCardCVV ? decryptedData?.card_cvv : '•••' }}
                      </span>
                      <div class="flex items-center gap-0.5 shrink-0">
                        <Button variant="ghost" size="sm" @click="toggleCardCVV" class="text-gray-400 hover:text-gray-650" tooltip="Reveal CVV">
                          <FeatherIcon :name="showCardCVV ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                        </Button>
                        <Button v-if="canCopy" variant="ghost" size="sm" @click="copyCardCVV" class="text-gray-400 hover:text-gray-650" tooltip="Copy CVV">
                          <FeatherIcon :name="copiedField === 'card_cvv' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'card_cvv'}" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Database specific fields -->
                <div v-else-if="secretData.secret_type === 'Database'" class="space-y-1">
                  <div v-if="secretData.db_host" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Host</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-base text-ink-gray-9 font-mono truncate mr-2">{{ secretData.db_host }}{{ secretData.db_port ? ':' + secretData.db_port : '' }}</span>
                    </div>
                  </div>
                  <div v-if="secretData.db_name" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">DB Name</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-base text-ink-gray-9 truncate mr-2">{{ secretData.db_name }}</span>
                    </div>
                  </div>
                  <div v-if="secretData.username" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Username</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-base text-ink-gray-9 font-mono truncate mr-2">{{ secretData.username }}</span>
                    </div>
                  </div>
                  <div class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Password</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-base text-ink-gray-9 font-mono tracking-wider truncate mr-2">
                        {{ showDBPassword ? decryptedData?.db_password : '••••••••••••' }}
                      </span>
                      <div class="flex items-center gap-0.5 shrink-0">
                        <Button variant="ghost" size="sm" @click="toggleDBPassword" class="text-gray-400 hover:text-gray-650" tooltip="Reveal DB Password">
                          <FeatherIcon :name="showDBPassword ? 'eye-off' : 'eye'" class="w-3.5 h-3.5" />
                        </Button>
                        <Button v-if="canCopy" variant="ghost" size="sm" @click="copyDBPassword" class="text-gray-400 hover:text-gray-650" tooltip="Copy DB Password">
                          <FeatherIcon :name="copiedField === 'db_password' ? 'check' : 'copy'" class="w-3.5 h-3.5" :class="{'text-green-600': copiedField === 'db_password'}" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- SSH Key specific fields -->
                <div v-else-if="secretData.secret_type === 'SSH Key'" class="space-y-1">
                  <div v-if="secretData.username" class="flex items-center justify-between py-2 border-b border-gray-100/50 min-h-[36px]">
                    <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5 truncate pr-2">Username</div>
                    <div class="w-[65%] flex items-center justify-between min-w-0">
                      <span class="text-base text-ink-gray-9 font-mono truncate mr-2">{{ secretData.username }}</span>
                    </div>
                  </div>
                  <div v-if="secretData.ssh_private_key" class="py-2.5">
                    <span class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">SSH Private Key</span>
                    <div class="relative bg-gray-50 border border-gray-100 rounded-xl p-3.5 group shadow-inner">
                      <pre class="text-xs font-mono text-gray-800 overflow-x-auto max-h-40 whitespace-pre select-all leading-normal">{{ secretData.ssh_private_key }}</pre>
                      <Button v-if="canCopy" variant="outline" size="sm" @click="copyField(secretData.ssh_private_key, 'ssh_private_key')" class="absolute top-2 right-2 bg-white opacity-0 group-hover:opacity-100 transition-opacity shadow-sm border-gray-200">
                        <template #prefix>
                          <FeatherIcon :name="copiedField === 'ssh_private_key' ? 'check' : 'copy'" class="w-3 h-3" :class="{'text-green-600': copiedField === 'ssh_private_key'}" />
                        </template>
                        <span>Copy</span>
                      </Button>
                    </div>
                  </div>
                </div>

                <!-- Certificate specific fields -->
                <div v-else-if="secretData.secret_type === 'Certificate'" class="space-y-1">
                  <div v-if="secretData.certificate" class="py-2.5">
                    <span class="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">Certificate</span>
                    <div class="relative bg-gray-50 border border-gray-100 rounded-xl p-3.5 group shadow-inner">
                      <pre class="text-xs font-mono text-gray-800 overflow-x-auto max-h-40 whitespace-pre select-all leading-normal">{{ secretData.certificate }}</pre>
                      <Button v-if="canCopy" variant="outline" size="sm" @click="copyField(secretData.certificate, 'certificate')" class="absolute top-2 right-2 bg-white opacity-0 group-hover:opacity-100 transition-opacity shadow-sm border-gray-200">
                        <template #prefix>
                          <FeatherIcon :name="copiedField === 'certificate' ? 'check' : 'copy'" class="w-3 h-3" :class="{'text-green-600': copiedField === 'certificate'}" />
                        </template>
                        <span>Copy</span>
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Collapsible NOTES Accordion -->
            <div v-if="secretData.notes" class="section border-b pb-1">
              <div class="section-header flex h-8 items-center justify-between">
                <div
                  class="flex text-ink-gray-9 max-w-fit cursor-pointer items-center gap-2 text-base px-2 font-semibold select-none"
                  @click="notesOpen = !notesOpen"
                >
                  <FeatherIcon
                    name="chevron-right"
                    class="h-4 w-4 transition-all duration-300 ease-in-out text-ink-gray-5"
                    :class="{ 'rotate-90': notesOpen }"
                  />
                  <span>Notes</span>
                </div>
              </div>
              
              <div v-show="notesOpen" class="p-3.5 bg-gray-50/50 rounded-xl text-sm text-gray-700 border border-gray-100 leading-relaxed shadow-sm whitespace-pre-wrap" v-html="secretData.notes" />
            </div>

            <!-- Collapsible METADATA Accordion -->
            <div class="section border-b pb-1">
              <div class="section-header flex h-8 items-center justify-between">
                <div
                  class="flex text-ink-gray-9 max-w-fit cursor-pointer items-center gap-2 text-base px-2 font-semibold select-none"
                  @click="metaOpen = !metaOpen"
                >
                  <FeatherIcon
                    name="chevron-right"
                    class="h-4 w-4 transition-all duration-300 ease-in-out text-ink-gray-5"
                    :class="{ 'rotate-90': metaOpen }"
                  />
                  <span>Metadata</span>
                </div>
              </div>

              <div v-show="metaOpen" class="space-y-1 px-3">
                <!-- Strength bar -->
                <div v-if="secretData.secret_type === 'Password' && secretData.password_strength" class="flex items-center gap-2 leading-5 min-h-[28px]">
                  <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5">Strength</div>
                  <div class="w-[65%] flex items-center">
                    <Badge size="sm" :theme="secretData.password_strength === 'weak' ? 'red' : 'green'" variant="subtle">
                      {{ secretData.password_strength }}
                    </Badge>
                  </div>
                </div>
                
                <!-- Last accessed -->
                <div class="flex items-center gap-2 leading-5 min-h-[28px]">
                  <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5">Last Accessed</div>
                  <div class="w-[65%] text-base text-ink-gray-9">{{ formatDateOnly(secretData.last_accessed) }}</div>
                </div>
                
                <!-- Access count -->
                <div class="flex items-center gap-2 leading-5 min-h-[28px]">
                  <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5">Access Count</div>
                  <div class="w-[65%] text-base text-ink-gray-9">{{ secretData.access_count || 0 }} times</div>
                </div>

                <!-- Last changed -->
                <div class="flex items-center gap-2 leading-5 min-h-[28px]">
                  <div class="w-[35%] min-w-20 shrink-0 text-sm text-ink-gray-5">Last Changed</div>
                  <div class="w-[65%] text-base text-ink-gray-9">{{ formatDateOnly(secretData.password_last_changed) }}</div>
                </div>
              </div>
            </div>

          </template>
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
          <p class="text-sm text-gray-600 mt-1 leading-normal">
            Are you sure you want to permanently delete <strong>{{ secretData?.title }}</strong>? This action cannot be undone.
          </p>
          <ErrorMessage v-if="deleteError" :message="deleteError" />
        </div>
      </template>
      <template #actions>
        <div class="flex items-center justify-end gap-2 px-4 pb-4">
          <Button variant="outline" @click="showDeleteDialog = false" class="text-gray-700 hover:bg-gray-100">
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
            <label class="block text-sm text-ink-gray-5 mb-1.5">Share Type</label>
            <div class="flex gap-1.5 p-1 bg-surface-gray-2 rounded-lg">
              <button
                v-for="t in ['User', 'Group', 'Role']"
                :key="t"
                type="button"
                class="flex-1 py-1.5 text-xs font-medium rounded-md transition-all duration-200 focus:outline-none"
                :class="newShareType === t ? 'bg-white text-ink-gray-9 shadow-sm' : 'text-ink-gray-6 hover:text-ink-gray-9'"
                @click="() => { newShareType = t; newShareRecipient = '' }"
              >
                {{ t }}
              </button>
            </div>
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
  </div>
</template>

<script setup>
import { ref, computed, watch, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { mobileSidebarOpened } from '../composables/sidebar'
import { nextTick } from 'vue'
import { Button, Badge, FeatherIcon, TextInput, FormControl, Dialog, ErrorMessage, Breadcrumbs, Tooltip, toast } from 'frappe-ui'
import { useSecret, useDecryptSecret, useSecretActivity, useDeleteSecret, useUpdateSecret, useFolders, useVerifyMasterPassword, useShareSecret, useUnshare, useSecretShares, useShareOptions, useVaultStats } from '../composables/vault'
import { useClipboard } from '../composables/clipboard'
import EmptyState from '../components/EmptyState.vue'
import PasswordStrength from '../components/PasswordStrength.vue'

const props = defineProps({
  name: {
    type: String,
    required: true,
  }
})

const router = useRouter()

const activeTab = ref('activity')
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
    { label: 'List', route: '/secrets' },
    { label: secretData.value?.title || 'Loading...' }
  ]
})
const decryptedData = computed(() => decryptResource.data?.decrypted)
const activityList = computed(() => activity.data || [])
const sharesList = computed(() => sharesResource.data || [])
const shareOptions = computed(() => shareOptionsResource.data || { users: [], groups: [], roles: [] })

const recipientOptions = computed(() => {
  const list = newShareType.value === 'User' 
    ? shareOptions.value.users 
    : newShareType.value === 'Group' 
      ? shareOptions.value.groups 
      : shareOptions.value.roles
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

const permissionTheme = {
  'View Only': 'gray',
  'View & Copy': 'blue',
  'Edit': 'orange',
  'Full Control': 'green'
}

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

async function handleRevokeShare(shareName, recipientName) {
  try {
    await unshareResource.submit({ share_name: shareName })
    toast.success(`Revoked access for ${recipientName}`)
    await sharesResource.fetch({ secret_name: props.name })
    activity.reload()
  } catch (err) {
    console.error(err)
    toast.error(err.message || 'Failed to revoke access')
  }
}

const tabs = [
  { name: 'activity', label: 'Activity' },
  { name: 'sharing', label: 'Sharing' },
]

const actionIcons = { Viewed: 'eye', Created: 'plus', Updated: 'edit', Deleted: 'trash', Shared: 'share-2', Unshared: 'user-minus', Copied: 'copy' }

const typeMeta = {
  Password: { icon: 'key', bg: 'bg-emerald-50 text-emerald-600 border-emerald-100', color: 'text-emerald-600' },
  'API Key': { icon: 'code', bg: 'bg-purple-50 text-purple-600 border-purple-100', color: 'text-purple-600' },
  Note: { icon: 'file-text', bg: 'bg-amber-50 text-amber-600 border-amber-100', color: 'text-amber-600' },
  'SSH Key': { icon: 'terminal', bg: 'bg-slate-50 text-slate-600 border-slate-100', color: 'text-slate-600' },
  Certificate: { icon: 'shield', bg: 'bg-indigo-50 text-indigo-600 border-indigo-100', color: 'text-indigo-600' },
  'Credit Card': { icon: 'credit-card', bg: 'bg-blue-50 text-blue-600 border-blue-100', color: 'text-blue-600' },
  Database: { icon: 'database', bg: 'bg-cyan-50 text-cyan-600 border-cyan-100', color: 'text-cyan-600' },
  Other: { icon: 'lock', bg: 'bg-pink-50 text-pink-600 border-pink-100', color: 'text-pink-600' },
}

const secretTypeOptions = [
  { label: 'Password', value: 'Password' },
  { label: 'API Key', value: 'API Key' },
  { label: 'Note', value: 'Note' },
  { label: 'SSH Key', value: 'SSH Key' },
  { label: 'Certificate', value: 'Certificate' },
  { label: 'Credit Card', value: 'Credit Card' },
  { label: 'Database', value: 'Database' },
  { label: 'Other', value: 'Other' },
]

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
</script>
