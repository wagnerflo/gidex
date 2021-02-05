<script>
  export let ui_root;
  export let api_root;
  export let static_root;

  import CSS_NAME from 'consts:CSS_NAME';

  import { setContext } from 'svelte';
  import { MaterialApp,
           AppBar,
           ProgressLinear,
         } from 'svelte-materialify/src';
  import { useNavigate, normalize } from './nav.js';

  import blob from './browser/blob.svelte';
  import tree from './browser/tree.svelte';

  const object_renderers = {
    blob, tree
  };

  const status_renderers = {

  };

  const norm_ui_root = normalize(ui_root);
  const norm_api_root = normalize(api_root);
  const norm_static_root = normalize(static_root);

  setContext('ui_root', norm_ui_root);
  setContext('api_root', norm_api_root);
  setContext('static_root', norm_static_root);

  const { nav, is_loading, content } = useNavigate();
  nav(document.location.pathname, 'replace');
</script>

<style lang="scss" src="./ui.scss"></style>

<svelte:head>
  <link rel="stylesheet" href="{ norm_static_root }/{ CSS_NAME }" />
</svelte:head>

<MaterialApp>
  <AppBar>
    <span slot="title">gidex</span>
  </AppBar>
  {#if $is_loading}
    <ProgressLinear indeterminate={ true } />
  {:else}
    <div style="height: 4px;" />
  {/if}

  <div class="mt-8 mb-8 ml-10 mr-10">
    {#if $content !== undefined}
      {#if $content.status === 200}
        <svelte:component
          this={ object_renderers[$content.body.object.object_type] }
          { ...$content.body } />
      {:else}
        <svelte:component this={ status_renderers[$content.status] }/>
      {/if}
    {/if}
  </div>
</MaterialApp>
