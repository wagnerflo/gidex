<script>
  export let depth;
  export let children;

  export function from_mdast(node, handle) {
    return {
        depth: node.depth,
        children: node.children.map(handle),
    };
  }
</script>

{#if depth == 1}
<h1 class="heading mb-5">
  {#each children as child}
    <svelte:component this={ child } />
  {/each}
</h1>
{:else}
<h6>
  {#each children as child}
    <svelte:component this={ child } />
  {/each}
</h6>
{/if}
