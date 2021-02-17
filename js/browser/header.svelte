<script>
  export let repository;

  import Link from '../link.svelte';

  import { Menu, Button, Tabs, Tab, TabContent, List, ListItem } from 'svelte-materialify/src';
  import { Repo24,
           GitBranch16,
           Tag16,
           FileDirectory16,
           TriangleDown16,
         } from 'svelte-octicons';

  const ref_icon_map = {
    branch: GitBranch16,
    tag: Tag16,
    workdir: FileDirectory16,
  }

  $: ref_icon = ref_icon_map[repository.ref.type];
</script>

<div class="d-flex flex-row">
  <Repo24 class="align-self-center"/>
  <h4 class="flex-grow-1 ml-2">{ repository.name }</h4>
  <Menu right={ true } closeOnClick={ false }>
    <div slot="activator">
      <Button>
        <svelte:component this={ ref_icon } class="mr-2" />
        {#if repository.ref.type != 'workdir'}
          { repository.ref.name }
        {:else}
          workdir
        {/if}
        <TriangleDown16 />
      </Button>
    </div>
    <Tabs grow>
      <div slot="tabs">
        <Tab>Branches</Tab>
        <Tab>Tags</Tab>
      </div>
      <div>
        <TabContent>
          <List nav dense>
            {#each repository.heads as head}
              <ListItem>
                <span slot="prepend">
                  
                </span>
                <Link url={ head.url }>{ head.name }</Link>
              </ListItem>
            {/each}
          </List>
        </TabContent>
        <TabContent>
          def
        </TabContent>
      </div>
    </Tabs>
  </Menu>
</div>
