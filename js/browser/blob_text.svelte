<script>
  export let content;

  export function matches(str) {
    return /^text\//.test(str);
  }
</script>

<pre class="ma-3">
  { content }
</pre>

