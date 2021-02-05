<script>
  export let object;

  import { Breadcrumbs } from 'svelte-materialify/src';
  import { Repo16 } from 'svelte-octicons';
  import Link from '../link.svelte';
</script>

<div class="d-flex flex-column rounded-t-lg browser-frame mt-8">
  <div class="frame-header rounded-t-lg">
    <Breadcrumbs items={ object.path.concat([object]) } let:item>
      <Link url={ item.url } class="filename">
        {#if item.name}
          { item.name }
        {:else}
          <Repo16 class="text-inline" />
        {/if}
      </Link>
    </Breadcrumbs>
  </div>
  <slot />
</div>
