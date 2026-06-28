<template>
  <div class="flex-1 flex flex-col overflow-hidden bg-surface-base">
    
    <!-- Page Header -->
    <header class="flex h-10.5 items-center justify-between border-b border-outline-gray-2 bg-surface-base px-5 py-2.5 shrink-0">
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
      <div class="flex-1 flex flex-col overflow-hidden bg-surface-base border-r border-outline-gray-2">
        <!-- Borderless navigation tabs (matching CRM layout) -->
        <div class="flex items-center gap-7.5 px-6 border-b border-outline-gray-2 bg-surface-base shrink-0 min-h-[45px]">
          <button
            v-for="t in tabs"
            :key="t.name"
            class="py-3.5 text-sm font-medium relative focus:outline-none transition-colors"
            :class="activeTab === t.name ? 'text-ink-gray-9 font-semibold' : 'text-ink-gray-5 hover:text-ink-gray-9'"
            @click="activeTab = t.name"
          >
            <span>{{ t.label }}</span>
            <span
              v-if="activeTab === t.name"
              class="absolute bottom-0 left-0 right-0 h-0.5 bg-ink-gray-9 rounded-full"
            />
          </button>
        </div>

        <!-- Tab Panel content container -->
        <div class="flex-1 flex flex-col overflow-y-auto p-6 min-h-0">
          
          <!-- Activity feed timeline panel -->
          <div v-if="activeTab === 'activity'" class="flex-1 flex flex-col max-w-3xl">
            <div class="flex items-center justify-between border-b border-outline-gray-2 pb-4 mb-6">
              <h3 class="text-lg font-bold text-ink-gray-9">Activity</h3>
            </div>
            
            <div v-if="activity.loading" class="space-y-4">
              <div v-for="i in 3" :key="i" class="h-16 bg-surface-gray-2 border border-outline-gray-2 rounded-xl animate-pulse" />
            </div>
            
            <div v-else-if="activityList.length" class="relative space-y-6 before:absolute before:top-3 before:bottom-3 before:left-[15px] before:w-px before:bg-outline-gray-2 pl-1 py-1">
              <div v-for="item in activityList" :key="item.name" class="relative flex items-start gap-4">
                <!-- Single clean icon circle centered on the line -->
                <div class="w-8 h-8 rounded-full border border-outline-gray-2 bg-surface-base flex items-center justify-center shrink-0 shadow-2xs z-10 text-ink-gray-7">
                  <FeatherIcon :name="actionIcons[item.action] || 'activity'" class="w-3.5 h-3.5" />
                </div>
                <div class="min-w-0 flex-1 pt-1 flex items-baseline justify-between gap-4">
                  <p class="text-sm text-ink-gray-8 leading-snug">
                    <span class="font-bold text-ink-gray-9">{{ item.user }}</span>
                    <span class="text-ink-gray-6 ml-1.5">{{ getActivityText(item) }}</span>
                  </p>
                  <span class="text-xs text-ink-gray-4 font-normal shrink-0">{{ formatTime(item.timestamp) }}</span>
                </div>
              </div>
            </div>
            
            <EmptyState v-else icon="activity" title="No activity recorded" />
          </div>

          <!-- Sharing config panel -->
          <div v-else-if="activeTab === 'sharing'" class="space-y-5 max-w-xl">
            <div class="flex items-center justify-between border-b border-outline-gray-2 pb-3 shrink-0">
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
            <div v-if="!isOwnerOrAdmin" class="p-4 bg-surface-gray-2 border border-outline-gray-2 rounded-xl text-sm leading-relaxed text-ink-gray-7 font-medium shadow-sm flex items-start gap-3">
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
                  class="flex items-center justify-between p-3.5 bg-surface-elevation-1 border border-outline-gray-2 rounded-xl shadow-sm hover:border-outline-gray-3 transition-colors"
                >
                  <div class="flex items-center gap-3.5 min-w-0">
                    <div class="w-9 h-9 rounded-full bg-surface-gray-2 border border-outline-gray-2 shadow-sm flex items-center justify-center shrink-0">
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
                      :theme="permissionTheme[item.permission_level] || 'gray'"
                      variant="subtle"
                      size="sm"
                    >
                      {{ item.permission_level }}
                    </Badge>

                    <!-- Revoke Access Action -->
                    <Button
                      variant="ghost"
                      icon="lucide-trash-2"
                      class="!p-1.5 h-auto text-ink-gray-4 hover:!text-ink-red-3 hover:!bg-red-50"
                      title="Revoke Access"
                      @click="handleRevokeShare(item.name, item.share_type === 'User' ? item.user : item.share_type === 'Group' ? item.group : item.frappe_role)"
                    />
                  </div>
                </div>
              </div>

              <!-- Active Shares Empty State -->
              <div v-else class="p-8 bg-surface-gray-2 border border-dashed border-outline-gray-2 rounded-2xl text-center shadow-sm">
                <div class="w-10 h-10 rounded-full bg-surface-gray-3 border border-outline-gray-2 flex items-center justify-center mx-auto text-ink-gray-4 mb-3 shrink-0">
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
      </div>

      <!-- RIGHT PANE: Resizable Side Panel Drawer (off-white bg, bordered) -->
      <div class="w-[380px] shrink-0 flex flex-col overflow-y-auto border-l border-outline-gray-2 flex-1 lg:flex-none bg-surface-base">
        
        <!-- Sidebar ID Header (matching CRM top ID text) -->
        <div class="px-6 pt-5 pb-1 flex items-center justify-between">
          <span
            class="text-sm font-mono font-medium text-ink-gray-5 hover:text-ink-gray-7 cursor-pointer select-none transition-colors"
            @click="copyField(secretData.name, 'name')"
            title="Click to copy ID"
          >
            {{ secretData.name }}
          </span>
        </div>

        <!-- Avatar + Title + Quick Actions (matching CRM Lead detail panel) -->
        <div class="px-6 pt-3 pb-6 flex items-start gap-4 border-b border-outline-gray-2">
          <!-- Circular type avatar icon -->
          <div :class="`size-12 rounded-full border flex items-center justify-center shrink-0 shadow-2xs ${typeMeta[secretData.secret_type || 'Other']?.bg}`">
            <FeatherIcon :name="typeMeta[secretData.secret_type || 'Other']?.icon" class="w-6 h-6" />
          </div>
          
          <div class="flex flex-col gap-2 min-w-0 flex-1 pt-0.5">
            <Tooltip :text="secretData.title">
              <h2 class="truncate text-xl font-bold text-ink-gray-9 leading-tight">
                {{ secretData.title }}
              </h2>
            </Tooltip>
            
            <!-- Action buttons row (matching CRM rounded square / circular buttons) -->
            <div class="flex items-center gap-1.5 pt-1">
              <button
                v-if="secretData.username"
                title="Copy Username"
                class="w-7.5 h-7.5 rounded-lg border border-outline-gray-2 bg-surface-base hover:bg-surface-gray-2 flex items-center justify-center text-ink-gray-7 transition-colors shadow-2xs"
                @click="copyField(secretData.username, 'username')"
              >
                <FeatherIcon name="user" class="w-3.5 h-3.5" />
              </button>
              <button
                v-if="secretData.secret_type === 'Password' && canCopy"
                title="Copy Password"
                class="w-7.5 h-7.5 rounded-lg border border-outline-gray-2 bg-surface-base hover:bg-surface-gray-2 flex items-center justify-center text-ink-gray-7 transition-colors shadow-2xs"
                @click="copyPassword"
              >
                <FeatherIcon name="key" class="w-3.5 h-3.5" />
              </button>
              <button
                v-if="secretData.secret_type === 'API Key' && canCopy"
                title="Copy API Secret"
                class="w-7.5 h-7.5 rounded-lg border border-outline-gray-2 bg-surface-base hover:bg-surface-gray-2 flex items-center justify-center text-ink-gray-7 transition-colors shadow-2xs"
                @click="copyAPISecret"
              >
                <FeatherIcon name="code" class="w-3.5 h-3.5" />
              </button>
              <button
                v-if="secretData.url"
                title="Open URL"
                class="w-7.5 h-7.5 rounded-lg border border-outline-gray-2 bg-surface-base hover:bg-surface-gray-2 flex items-center justify-center text-ink-gray-7 transition-colors shadow-2xs"
                @click="window.open(secretData.url, '_blank')"
              >
                <FeatherIcon name="external-link" class="w-3.5 h-3.5" />
              </button>
              <button
                v-if="canDelete"
                title="Delete Secret"
                class="w-7.5 h-7.5 rounded-lg border border-red-100 bg-red-50 hover:bg-red-100/80 flex items-center justify-center text-red-600 transition-colors shadow-2xs ml-auto"
                @click="showDeleteDialog = true"
              >
                <FeatherIcon name="trash-2" class="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </div>

        <div class="flex flex-1 flex-col justify-between overflow-hidden">
          <div class="flex-1 overflow-y-auto">
          
          <!-- Clipboard clear warning indicator -->
          <div v-if="clipboard.copied.value" class="flex items-center gap-2.5 p-3 mx-4 my-2 bg-amber-50/70 text-amber-800 rounded-xl text-xs font-semibold border border-amber-100/40 shadow-sm transition-all duration-300">
            <FeatherIcon name="shield" class="w-4 h-4 text-amber-600 animate-pulse shrink-0" />
            <span class="flex-1">Clipboard copied. Auto-clearing in <strong>{{ clipboard.countdown.value }}s</strong>.</span>
          </div>

          <!-- Collapsible DETAILS Accordion (matching CRM styling) -->
          <div class="border-b border-outline-gray-2 py-3.5 px-6">
            <div class="flex items-center justify-between select-none">
              <div
                class="flex items-center gap-2 cursor-pointer font-bold text-ink-gray-9 text-sm"
                @click="detailsOpen = !detailsOpen"
              >
                <FeatherIcon
                  name="chevron-right"
                  class="h-4 w-4 transition-transform duration-200 text-ink-gray-5"
                  :class="{ 'rotate-90': detailsOpen }"
                />
                <span>Details</span>
              </div>

              <!-- Edit toggle button aligned right inside accordion header matching CRM -->
              <button
                v-if="canEdit"
                @click="toggleEditMode"
                class="flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded-md transition-colors"
                :class="isEditing ? 'bg-ink-gray-9 text-surface-white' : 'text-ink-gray-6 hover:bg-surface-gray-2 hover:text-ink-gray-9 border border-outline-gray-2'"
              >
                <FeatherIcon :name="isEditing ? 'eye' : 'edit-2'" class="w-3 h-3" />
                <span>{{ isEditing ? 'View' : 'Edit' }}</span>
              </button>
            </div>

            <div v-show="detailsOpen" class="mt-3.5">
              <!-- EDIT VIEW FORM -->
              <div v-if="isEditing" class="space-y-4 pt-1">
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

                <div class="w-full border-t border-outline-gray-2 my-2" />

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
                <div class="flex items-center justify-end gap-2 pt-4 border-t border-outline-gray-2">
                  <Button variant="outline" size="sm" @click="isEditing = false">Cancel</Button>
                  <Button variant="solid" size="sm" @click="handleSave" :loading="updateResource.loading" class="font-semibold shadow-2xs">Save Changes</Button>
                </div>
              </div>

              <!-- READ ONLY VIEW -->
              <div v-else class="space-y-2.5 py-1">
                <!-- Secret Type -->
                <div class="flex items-center justify-between py-1 text-sm">
                  <span class="w-28 shrink-0 text-ink-gray-5 font-normal">Secret Type</span>
                  <div class="min-w-0 flex-1 flex justify-end truncate">
                    <Badge size="sm" variant="subtle" :theme="secretData.secret_type === 'Password' ? 'green' : 'gray'">
                      {{ secretData.secret_type }}
                    </Badge>
                  </div>
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
                    <div class="relative bg-surface-gray-2 border border-outline-gray-2 rounded-xl p-3 group shadow-inner">
                      <pre class="text-xs font-mono text-ink-gray-8 overflow-x-auto max-h-36 whitespace-pre select-all leading-normal">{{ secretData.ssh_private_key }}</pre>
                      <button v-if="canCopy" type="button" @click="copyField(secretData.ssh_private_key, 'ssh_private_key')" class="absolute top-2 right-2 px-2 py-1 bg-surface-base border border-outline-gray-2 rounded-md text-xs font-medium text-ink-gray-7 opacity-0 group-hover:opacity-100 transition-opacity shadow-2xs flex items-center gap-1">
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
                    <div class="relative bg-surface-gray-2 border border-outline-gray-2 rounded-xl p-3 group shadow-inner">
                      <pre class="text-xs font-mono text-ink-gray-8 overflow-x-auto max-h-36 whitespace-pre select-all leading-normal">{{ secretData.certificate }}</pre>
                      <button v-if="canCopy" type="button" @click="copyField(secretData.certificate, 'certificate')" class="absolute top-2 right-2 px-2 py-1 bg-surface-base border border-outline-gray-2 rounded-md text-xs font-medium text-ink-gray-7 opacity-0 group-hover:opacity-100 transition-opacity shadow-2xs flex items-center gap-1">
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
          <div v-if="secretData.notes" class="border-b border-outline-gray-2 py-3.5 px-6">
            <div class="flex items-center justify-between select-none">
              <div
                class="flex items-center gap-2 cursor-pointer font-bold text-ink-gray-9 text-sm"
                @click="notesOpen = !notesOpen"
              >
                <FeatherIcon
                  name="chevron-right"
                  class="h-4 w-4 transition-transform duration-200 text-ink-gray-5"
                  :class="{ 'rotate-90': notesOpen }"
                />
                <span>Notes</span>
              </div>
            </div>
            
            <div v-show="notesOpen" class="mt-3 p-3.5 bg-surface-gray-2 rounded-xl text-sm text-ink-gray-8 border border-outline-gray-2 leading-relaxed whitespace-pre-wrap font-normal" v-html="secretData.notes" />
          </div>

          <!-- Collapsible METADATA Accordion -->
          <div class="border-b border-outline-gray-2 py-3.5 px-6">
            <div class="flex items-center justify-between select-none">
              <div
                class="flex items-center gap-2 cursor-pointer font-bold text-ink-gray-9 text-sm"
                @click="metaOpen = !metaOpen"
              >
                <FeatherIcon
                  name="chevron-right"
                  class="h-4 w-4 transition-transform duration-200 text-ink-gray-5"
                  :class="{ 'rotate-90': metaOpen }"
                />
                <span>Metadata</span>
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
  </div>
</template>

<script setup>
import { ref, computed, watch, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { Button, Badge, FeatherIcon, TextInput, FormControl, Dialog, ErrorMessage, Breadcrumbs, Tooltip, toast, TabButtons } from 'frappe-ui'
import { mobileSidebarOpened, useSecret, useDecryptSecret, useSecretActivity, useDeleteSecret, useUpdateSecret, useFolders, useVerifyMasterPassword, useShareSecret, useUnshare, useSecretShares, useShareOptions, useVaultStats } from '../composables/vault'
import { useClipboard } from '../composables/clipboard'
import EmptyState from '../components/EmptyState.vue'
import StrengthBadge from '../components/StrengthBadge.vue'
import { actionIcons, secretTypeOptions, permissionTheme, typeMeta } from '../composables/constants'

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
