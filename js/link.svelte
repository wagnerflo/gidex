<script>
  let klass = '';

  export let url;
  export { klass as class };

  import { useNavigate, uiify } from './nav.js';
  const { nav } = useNavigate();
</script>

<a class="{ klass }" href={ uiify(url) }
   on:click|preventDefault={ () => nav(url) }>
  <slot/>
</a>
