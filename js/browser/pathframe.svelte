<script>
  export let object;

  import { Breadcrumbs } from 'svelte-materialify/src';
  import { Repo16 } from 'svelte-octicons';
  import Link from '../link.svelte';
</script>

<div class="d-flex flex-column rounded-t-lg browser-frame mt-8">
  <div class="frame-header rounded-t-lg d-flex flex-row">
    <div class="flex-grow-1">
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
    <slot name="header" />
  </div>
  {#if object.commit}
    <div class="frame-header pb-3 pl-3 pr-3">
      <span class="font-weight-bold">
        { object.commit.author }
      </span>
      { object.commit.message }
    </div>
  {/if}
  <slot name="body" />
</div>
