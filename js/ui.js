import ui from './ui.svelte';

const app = new ui({
  target: document.body,
  props: {
    ...document.currentScript.dataset,
  },
});
