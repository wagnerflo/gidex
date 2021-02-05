<script>
  export let object;
  export let repository;

  import { Breadcrumbs } from 'svelte-materialify/src';
  import { FileDirectory16, File16 } from 'svelte-octicons';

  import Link from '../link.svelte';
  import RepositoryHeader from './header.svelte';
  import PathFrame from './pathframe.svelte';

  $: parent = (
    object.path.length
      ? object.path[object.path.length - 1]
      : undefined
  );
</script>

<RepositoryHeader repository={ repository } />

<PathFrame object={ object }>
  {#if parent}
  <div class="pa-2">
    <Link url={ parent.url } class="filename">..</Link>
  </div>
  {/if}
  {#each object.children as child}
    <div class="d-flex flex-row pa-2">
      <div class="color-icon">
        {#if child.object_type == 'tree'}
          <FileDirectory16 />
        {:else if child.object_type == 'blob'}
          <File16 />
        {/if}
      </div>
      <div class="ml-2">
        <Link url={ child.url } class="filename">{ child.name }</Link>
      </div>
    </div>
  {/each}
</PathFrame>
