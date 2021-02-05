<script>
  export let value;

  export function from_mdast(node, handle) {
    return {
      value: node.value,
    };
  }
</script>

{ value }
