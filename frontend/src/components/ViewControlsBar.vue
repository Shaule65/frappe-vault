<template>
  <div class="flex items-center justify-between gap-2 px-5 py-4">
    <div class="flex flex-1 items-center gap-2.5 overflow-x-auto h-9">
      <slot name="left" />
    </div>
    <div class="flex items-center gap-2">
      <slot name="right" />
    </div>
  </div>
</template>

<script setup>
// Presentational wrapper component for view controls bar.
</script>
