// AgentRoute Arena — shared JS: theme toggle, nav, leaderboard sort + metric bars.
(function () {
  // Theme (in-memory; preview iframe blocks localStorage)
  var root = document.documentElement;
  function setTheme(t) { root.setAttribute('data-theme', t); }
  var toggle = document.querySelector('[data-theme-toggle]');
  if (toggle) {
    toggle.addEventListener('click', function () {
      var cur = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      setTheme(cur);
    });
  }

  // Highlight active nav link
  var path = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav a').forEach(function (a) {
    var href = a.getAttribute('href');
    if (href === path) a.classList.add('active');
  });

  // Leaderboard: render + sort
  var lbEl = document.querySelector('[data-leaderboard]');
  if (lbEl && window.ARA_ROUTERS) {
    var rows = window.ARA_ROUTERS.slice();
    var sortKey = 'score';
    var sortDir = -1;
    var cols = [
      { key: 'rank', label: '#', cls: 'rank' },
      { key: 'name', label: 'Router' },
      { key: 'type', label: 'Type', cls: 'badge-cell' },
      { key: 'score', label: 'AgentRoute', cls: 'score', bar: true },
      { key: 'goal', label: 'Goal' },
      { key: 'accuracy', label: 'Route Acc.' },
      { key: 'recovery', label: 'Recovery' },
      { key: 'clarify', label: 'Clarify' },
      { key: 'safety', label: 'Safety' },
      { key: 'cost', label: 'Cost-eff.' },
      { key: 'turns', label: 'Turn-eff.' },
    ];

    function render() {
      rows.sort(function (a, b) {
        var va = a[sortKey], vb = b[sortKey];
        if (typeof va === 'string') return sortDir * va.localeCompare(vb);
        return sortDir * (va - vb);
      });
      var max = Math.max.apply(null, rows.map(function (r) { return r.score; }));
      var thead = cols.map(function (c) {
        var arrow = (c.key === sortKey) ? (sortDir < 0 ? ' ↓' : ' ↑') : '';
        return '<th data-key="' + c.key + '">' + c.label + arrow + '</th>';
      }).join('');
      var body = rows.map(function (r, i) {
        var rankCls = i < 3 ? 'rank top' : 'rank';
        var cells = cols.map(function (c) {
          var v = r[c.key];
          if (c.bar) {
            var pct = Math.round((v / 100) * 100);
            return '<td class="score">' + v.toFixed(1) + '<div class="bar"><i style="width:' + pct + '%"></i></div></td>';
          }
          if (c.key === 'type') {
            var t = v === 'baseline' ? 'baseline' : (v === 'illustrative' ? 'illustrative' : 'submission');
            return '<td><span class="badge ' + (v === 'baseline' ? 'baseline' : '') + '">' + t + '</span></td>';
          }
          if (typeof v === 'number') return '<td>' + v.toFixed(2) + '</td>';
          if (c.key === 'rank') return '<td class="' + rankCls + '">' + (i + 1) + '</td>';
          return '<td>' + v + '</td>';
        }).join('');
        return '<tr>' + cells + '</tr>';
      }).join('');
      lbEl.innerHTML = '<table class="lb"><thead><tr>' + thead + '</tr></thead><tbody>' + body + '</tbody></table>';
      lbEl.querySelectorAll('th').forEach(function (th) {
        th.addEventListener('click', function () {
          var k = th.getAttribute('data-key');
          if (sortKey === k) sortDir = -sortDir;
          else { sortKey = k; sortDir = -1; }
          render();
        });
      });
    }
    render();
  }

  // Metric bars (metrics page)
  document.querySelectorAll('[data-metric]').forEach(function (el) {
    var v = parseFloat(el.getAttribute('data-val'));
    var pct = Math.max(0, Math.min(1, v)) * 100;
    el.querySelector('.track i').style.width = pct + '%';
    el.querySelector('.val').textContent = v.toFixed(2);
  });
})();
