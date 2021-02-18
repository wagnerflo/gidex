<script>
  export let object;
  export let repository;

  import { parseJSON } from 'date-fns'
  import { Breadcrumbs, Button, Table } from 'svelte-materialify/src';
  import { FileDirectory16,
           File16,
           Eye16,
           EyeClosed16,
           Zap16,
         } from 'svelte-octicons';

  import Link from '../link.svelte';
  import RepositoryHeader from './header.svelte';
  import PathFrame from './pathframe.svelte';
  import Timeago from './timeago.svelte';

  let show_ignored = false;

  $: parent = (
    object.path.length
      ? object.path[object.path.length - 1]
      : undefined
  );
  $: now = new Date();
</script>

<RepositoryHeader repository={ repository } />

<PathFrame object={ object }>
  <slot slot="header">
    {#if repository.ref.type == 'workdir'}
      <Button class="align-self-center mr-3"
              on:click={ () => show_ignored = !show_ignored }>
        {#if show_ignored}
          <EyeClosed16 class="mr-2" /> Hide ignored
        {:else}
          <Eye16 class="mr-2" /> Show ignored
        {/if}
      </Button>
    {/if}
  </slot>

  <slot slot="body">
    <Table class="stripped">
      {#if parent}
        <tr>
          <td class="shrink pr-3 pl-3 pt-2 pb-2" colspan="4">
            <Link url={ parent.url } class="filename">..</Link>
          </td>
        </tr>
      {/if}
      {#each object.children as child}
        {#if show_ignored || !child.ignored}
          <tr>
            <td class="shrink pl-3 pt-2 pb-2">
              {#if child.object_type == 'tree'}
                <FileDirectory16 class="color-icon table-icon" />
              {:else if child.object_type == 'blob'}
                <File16 class="color-icon table-icon" />
              {/if}
            </td>
            <td class="pt-2 pb-2 pl-2">
              <Link url={ child.url } class="filename">{ child.name }</Link>
              {#if child.modified}
                <Zap16 class="color-icon table-icon" />
              {/if}
            </td>
            <td class="pt-2 pb-2 pl-2">
              {#if child.commit}
                { child.commit.message }
              {/if}
            </td>
            <td class="shrink pt-2 pb-2 pl-2 pr-3 text-right">
              {#if child.commit}
                <Timeago now={ now } date={ parseJSON(child.commit.when) } />
              {/if}
            </td>
          </tr>
        {/if}
      {/each}
    </Table>
  </slot>
</PathFrame>
