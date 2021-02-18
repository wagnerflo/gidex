<script>
  export let now;
  export let date;
  import { format, formatDistance } from 'date-fns'
</script>

<span title={ format(date, 'MMM d, yyyy, HH:mm O') }>
  { formatDistance(date, now,) } ago
</span>
