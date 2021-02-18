<script>
  export let object;
  export let repository;

  import { ProgressCircular } from 'svelte-materialify/src';
  import RepositoryHeader from './header.svelte';
  import PathFrame from './pathframe.svelte';

  import blob_text from './blob_text.svelte';
  import blob_markdown from './blob_markdown.svelte';

  const renderers = [
    blob_markdown,
    blob_text,
  ];

  async function content(url) {
    const res = await fetch(url);
    if (res.ok) {
      return await res.text();
    }
    else {
      throw new Error("download error");
    }
  }

  $: console.log(object.mime_type)
</script>

<RepositoryHeader repository={ repository } />

<PathFrame object={ object }>
  <slot slot="body">
    {#await content(object.raw)}
      <div class="ma-3 align-self-center">
        <ProgressCircular indeterminate={ true } size={ 24 } width={ 2 } />
      </div>
    {:then data}
      <svelte:component
        this={ renderers.find(r => r.prototype.matches(object.mime_type)) }
        object={ object }
        content={ data } />
    {/await}
  </slot>
</PathFrame>
