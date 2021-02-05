<script>
  export let children;

  export function from_mdast(node, handle) {
    return {
      children: node.children.map(handle)
    };
  }
</script>

<div class="markdown">
  {#each children as child}
    <svelte:component this={ child } />
  {/each}
</div>
