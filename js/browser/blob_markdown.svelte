<script>
  export let object;
  export let content;

  import { ProgressCircular } from 'svelte-materialify/src';
  import { transformer } from '../markdown.js';

  export function matches(str) {
    return /^text\/(x-)?markdown$/.test(str);
  }

  async function transform(str) {
    return (await transformer.process(str)).result;
  }
</script>

{#await transform(content)}
  <div class="ma-3 align-self-center">
    <ProgressCircular indeterminate={ true } size={ 24 } width={ 2 } />
  </div>
{:then result}
  <div class="mt-3 ml-3 mr-3">
    <svelte:component this={ result } />
  </div>
{/await}
