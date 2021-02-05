<script>
  export let repository;

  import { Menu, Button, List, ListItem } from 'svelte-materialify/src';
  import { Repo24 } from 'svelte-octicons';
</script>

<div class="d-flex flex-row">
  <Repo24 class="align-self-center"/>
  <h4 class="flex-grow-1 ml-2">{ repository.name }</h4>
  <Menu>
    <div slot="activator">
      <Button>Activate</Button>
    </div>
    <List>
      <ListItem>Option 1</ListItem>
      <ListItem>Option 2</ListItem>
      <ListItem>This is Cool</ListItem>
    </List>
  </Menu>
</div>
