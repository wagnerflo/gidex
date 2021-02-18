<script>
  export let content;

  export function matches(str) {
    return /^application\/(json|javascript)|text\//.test(str);
  }
</script>

<pre class="ma-3">
  { content }
</pre>

