import API_ACCEPT from 'consts:API_ACCEPT';
import API_PROFILE from 'consts:API_PROFILE';

import { getContext } from 'svelte';
import { writable } from 'svelte/store';

const headers = new Headers({
  'Accept': API_ACCEPT,
  'Accept-Profile': API_PROFILE,
});
const controller = new AbortController();
const { signal } = controller;

const is_loading = writable(false);
const content = writable(undefined);

window.addEventListener(
  'popstate',
  (evt) => _nav(evt.state.api_url, window.location.pathname)
);

function _nav(api_url, ui_url, history_action) {
  const done = (status, body) => {
    is_loading.set(false);

    if (history_action !== undefined)
      history[`${history_action}State`](
        { api_url },
        '',
        ui_url
      );

    content.set({ status, body });
  };

  controller.abort();
  is_loading.set(true);

  const req = new Request(api_url, {
    method: 'GET',
    headers: headers,
  });

  fetch(req)
    .then(resp => {
      if (resp.status === 200) {
        resp.json().then(body => {
          done(resp.status, body);
        });
      }
      else {
        done(resp.status);
      }
    })
    .catch(e => {
      if(e.name === 'AbortError')
        return;

      console.log(e);
    });
}

export function useNavigate() {
  const api_root = getContext('api_root').toString();
  const ui_root = getContext('ui_root').toString();

  return {
    nav: function(path, history_action='push') {
      const api_url = new URL(path, api_root).toString();
      const ui_url = _uiify(api_url, api_root, ui_root).toString();
      _nav(api_url, ui_url, history_action);
    },
    is_loading,
    content,

  };
}

export function normalize(path) {
  const url = new URL(path, document.location.origin);
  url.pathname = url.pathname.replace(/(^\/+|\/+$)/g, '');
  return url;
}

function _uiify(url, api_root, ui_root) {
  url = url.toString();

  if (!url.startsWith(api_root)) {
    throw 'Invalid URL';
  }

  return new URL(url.substring(api_root.length - 1), ui_root);

}

export function uiify(url, api_root, ui_root) {
  return _uiify(
    url,
    getContext('api_root').toString(),
    getContext('ui_root').toString(),
  );
}
