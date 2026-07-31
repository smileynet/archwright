// ELK Direct SVG — interactive state machine diagram
// Integrated from spike: .scratch/spike-elk-direct/
(function() {
  if (typeof ELK === 'undefined') return;
  var dataEl = document.getElementById('elk-graph-data');
  if (!dataEl) return;

  var graphData;
  try { graphData = JSON.parse(dataEl.textContent); }
  catch (e) { return; }

  var elk = new ELK();
  var _layoutId = 0;
  var _viewBox = null;
  var _measureSvg = null;

  // Empty graph guard
  if (!graphData.states || graphData.states.length === 0) {
    document.getElementById('elk-diagram').innerHTML = '<p style="color:var(--neutral);text-align:center;padding:40px">No states to display for this actor.</p>';
    return;
  }

  function measureText(text, fontSize) {
    if (!_measureSvg) {
      _measureSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      _measureSvg.style.position = 'absolute';
      _measureSvg.style.visibility = 'hidden';
      _measureSvg.style.width = '0';
      _measureSvg.style.height = '0';
      document.body.appendChild(_measureSvg);
    }
    var t = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    t.setAttribute('font-family', 'system-ui, sans-serif');
    t.setAttribute('font-size', fontSize || '13');
    t.textContent = text;
    _measureSvg.appendChild(t);
    var w = t.getComputedTextLength();
    _measureSvg.removeChild(t);
    return Math.ceil(w);
  }

  var spacingMap = { compact: 25, normal: 45, spacious: 80 };
  var clearanceMap = { tight: 8, normal: 20, wide: 45 };

  function getCtlValue(id, fallback) {
    var el = document.getElementById(id);
    return el ? el.value : fallback;
  }

  function buildElkGraph() {
    var dir = getCtlValue('ctl-direction', 'DOWN');
    var routing = getCtlValue('ctl-routing', 'SPLINES');
    var spacing = spacingMap[getCtlValue('ctl-spacing', 'normal')];
    var clearance = clearanceMap[getCtlValue('ctl-clearance', 'normal')];
    var showLabels = getCtlValue('ctl-labels', 'show') === 'show';

    var graph = {
      id: "root",
      layoutOptions: {
        'elk.algorithm': 'layered',
        'elk.direction': dir,
        'elk.edgeRouting': routing,
        'elk.spacing.nodeNode': String(spacing),
        'elk.layered.spacing.nodeNodeBetweenLayers': String(Math.round(spacing * 1.2)),
        'elk.spacing.edgeEdge': String(Math.round(clearance * 0.6)),
        'elk.layered.spacing.edgeEdgeBetweenLayers': String(Math.round(clearance * 0.6)),
        'elk.spacing.edgeNode': String(clearance),
        'elk.layered.spacing.edgeNodeBetweenLayers': String(clearance),
        'elk.layered.crossingMinimization.strategy': 'LAYER_SWEEP',
        'elk.layered.nodePlacement.strategy': 'NETWORK_SIMPLEX',
        'elk.layered.cycleBreaking.strategy': 'DEPTH_FIRST',
        'elk.layered.thoroughness': '10',
        'elk.spacing.edgeLabel': '8',
        'elk.spacing.labelLabel': '5',
        'elk.edgeLabels.placement': 'CENTER',
        'elk.nodeSize.constraints': '[NODE_LABELS, MINIMUM_SIZE]',
        'elk.nodeLabels.placement': '[H_CENTER, V_CENTER, INSIDE]',
        'elk.padding': '[top=30,left=30,bottom=30,right=30]'
      },
      children: graphData.states.map(function(s) {
        var labelW = measureText(s.label, '13');
        return { id: s.id, width: Math.max(90, labelW + 28), height: 44,
                 labels: [{ text: s.label, width: labelW, height: 14 }] };
      }),
      edges: graphData.transitions.map(function(t) {
        var e = { id: t.id, sources: [t.from], targets: [t.to] };
        if (showLabels) {
          var lw = measureText(t.label, '11');
          e.labels = [{ text: t.label, width: lw, height: 14 }];
        }
        return e;
      })
    };
    return graph;
  }

  function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

  function renderSVG(layoutResult) {
    var padding = 30;
    var w = (layoutResult.width || 800) + padding * 2;
    var h = (layoutResult.height || 600) + padding * 2;
    var actorLabel = graphData.actorLabel || 'State Machine';
    var stateCount = graphData.states.length;
    var transCount = graphData.transitions.length;

    var svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ' + w + ' ' + h + '" role="img" aria-labelledby="elk-title elk-desc">';
    svg += '<title id="elk-title">State machine diagram: ' + esc(actorLabel) + '</title>';
    svg += '<desc id="elk-desc">' + stateCount + ' states, ' + transCount + ' transitions. Click states or edges for details.</desc>';
    svg += '<defs>';
    svg += '<marker id="arr" viewBox="0 0 8 6" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L8 3 L0 6Z" fill="var(--neutral)"/></marker>';
    svg += '<marker id="arr-hl" viewBox="0 0 8 6" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto" markerUnits="userSpaceOnUse"><path d="M0 0 L8 3 L0 6Z" fill="var(--info)"/></marker>';
    svg += '</defs>';

    var routing = getCtlValue('ctl-routing', 'SPLINES');

    // Edges
    (layoutResult.edges || []).forEach(function(edge) {
      var sections = edge.sections || [];
      if (sections.length === 0) return;
      var src = (edge.sources || [])[0];
      var tgt = (edge.targets || [])[0];
      svg += '<g class="edge-group" data-edge-id="' + esc(edge.id) + '" data-source="' + esc(src) + '" data-target="' + esc(tgt) + '" tabindex="0" role="button" aria-label="Transition: ' + esc(edge.id) + '">';

      var fullD = '';
      sections.forEach(function(section) {
        var points = [];
        if (section.startPoint) points.push(section.startPoint);
        if (section.bendPoints) points = points.concat(section.bendPoints);
        if (section.endPoint) points.push(section.endPoint);
        if (points.length < 2) return;

        if (routing === 'SPLINES' && points.length >= 4) {
          fullD += 'M ' + (points[0].x + padding) + ' ' + (points[0].y + padding);
          var i = 1;
          while (i + 2 < points.length) {
            fullD += ' C ' + (points[i].x + padding) + ' ' + (points[i].y + padding) + ','
                           + (points[i+1].x + padding) + ' ' + (points[i+1].y + padding) + ','
                           + (points[i+2].x + padding) + ' ' + (points[i+2].y + padding);
            i += 3;
          }
          for (; i < points.length; i++) {
            fullD += ' L ' + (points[i].x + padding) + ' ' + (points[i].y + padding);
          }
        } else {
          fullD += 'M ' + (points[0].x + padding) + ' ' + (points[0].y + padding);
          for (var i = 1; i < points.length; i++) {
            fullD += ' L ' + (points[i].x + padding) + ' ' + (points[i].y + padding);
          }
        }
      });

      svg += '<path class="edge-hit" d="' + fullD + '"/>';
      svg += '<path class="edge-line" d="' + fullD + '" marker-end="url(#arr)"/>';
      svg += '</g>';

      // Edge labels
      if (edge.labels && edge.labels.length > 0) {
        edge.labels.forEach(function(lbl) {
          if (lbl.x !== undefined && lbl.y !== undefined) {
            var lx = lbl.x + padding, ly = lbl.y + padding;
            var lw = lbl.width || 60, lh = lbl.height || 14;
            svg += '<g class="edge-label" data-edge-id="' + esc(edge.id) + '">';
            svg += '<rect x="' + (lx - 3) + '" y="' + (ly - 2) + '" width="' + (lw + 6) + '" height="' + (lh + 6) + '"/>';
            svg += '<text x="' + (lx + lw/2) + '" y="' + (ly + lh) + '" text-anchor="middle">' + esc(lbl.text) + '</text>';
            svg += '</g>';
          }
        });
      }
    });

    // Nodes
    (layoutResult.children || []).forEach(function(node) {
      var nx = node.x + padding, ny = node.y + padding, nw = node.width, nh = node.height;
      var label = (node.labels && node.labels[0]) ? node.labels[0].text : node.id;
      // Link to behavior-detail section
      var detailAnchor = graphData.detailAnchors ? graphData.detailAnchors[node.id] : null;
      svg += '<g class="state-node" data-node-id="' + esc(node.id) + '"' + (detailAnchor ? ' data-detail="' + esc(detailAnchor) + '"' : '') + ' tabindex="0" role="button" aria-label="State: ' + esc(label) + '">';
      svg += '<rect x="' + nx + '" y="' + ny + '" width="' + nw + '" height="' + nh + '"/>';
      svg += '<text x="' + (nx + nw/2) + '" y="' + (ny + nh/2 + 5) + '" text-anchor="middle">' + esc(label) + '</text>';
      svg += '</g>';
    });

    svg += '</svg>';
    return svg;
  }

  function doLayout() {
    var myId = ++_layoutId;
    var graph = buildElkGraph();
    elk.layout(graph).then(function(result) {
      if (myId !== _layoutId) return;
      document.getElementById('elk-diagram').innerHTML = renderSVG(result);
      _viewBox = null;
      fitToView();
      attachEvents();
    }).catch(function(err) {
      if (myId !== _layoutId) return;
      document.getElementById('elk-diagram').innerHTML = '<p style="color:var(--danger);padding:24px">ELK layout error: ' + esc(err.message) + '</p>';
    });
  }

  function fitToView() {
    var svg = document.querySelector('#elk-diagram svg');
    if (!svg) return;
    var vb = svg.getAttribute('viewBox').split(' ').map(Number);
    _viewBox = { x: vb[0], y: vb[1], w: vb[2], h: vb[3] };
    svg.setAttribute('viewBox', _viewBox.x + ' ' + _viewBox.y + ' ' + _viewBox.w + ' ' + _viewBox.h);
  }

  function zoom(factor) {
    var svg = document.querySelector('#elk-diagram svg');
    if (!svg || !_viewBox) return;
    var cx = _viewBox.x + _viewBox.w / 2, cy = _viewBox.y + _viewBox.h / 2;
    _viewBox.w /= factor;
    _viewBox.h /= factor;
    _viewBox.x = cx - _viewBox.w / 2;
    _viewBox.y = cy - _viewBox.h / 2;
    svg.setAttribute('viewBox', _viewBox.x + ' ' + _viewBox.y + ' ' + _viewBox.w + ' ' + _viewBox.h);
  }

  // Wheel zoom
  var diagramEl = document.getElementById('elk-diagram');
  diagramEl.addEventListener('wheel', function(e) {
    e.preventDefault();
    zoom(e.deltaY < 0 ? 1.15 : 0.87);
  }, { passive: false });

  // Drag pan
  (function() {
    var dragging = false, startX, startY, startVB;
    diagramEl.addEventListener('mousedown', function(e) {
      if (e.target.closest('.state-node, .edge-group')) return;
      dragging = true; startX = e.clientX; startY = e.clientY;
      startVB = _viewBox ? { x: _viewBox.x, y: _viewBox.y, w: _viewBox.w, h: _viewBox.h } : null;
      diagramEl.style.cursor = 'grabbing';
    });
    document.addEventListener('mousemove', function(e) {
      if (!dragging || !startVB) return;
      var svg = document.querySelector('#elk-diagram svg');
      if (!svg) return;
      var rect = diagramEl.getBoundingClientRect();
      var sx = startVB.w / rect.width, sy = startVB.h / rect.height;
      _viewBox.x = startVB.x - (e.clientX - startX) * sx;
      _viewBox.y = startVB.y - (e.clientY - startY) * sy;
      svg.setAttribute('viewBox', _viewBox.x + ' ' + _viewBox.y + ' ' + _viewBox.w + ' ' + _viewBox.h);
    });
    document.addEventListener('mouseup', function() { dragging = false; diagramEl.style.cursor = ''; });
  })();

  function attachEvents() {
    document.querySelectorAll('#elk-diagram .state-node').forEach(function(el) {
      el.addEventListener('click', function() { selectNode(this.dataset.nodeId); });
      el.addEventListener('dblclick', function() {
        var anchor = this.dataset.detail;
        if (anchor) {
          var target = document.getElementById(anchor);
          if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      });
      el.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); selectNode(this.dataset.nodeId); }
      });
    });
    document.querySelectorAll('#elk-diagram .edge-group').forEach(function(el) {
      el.addEventListener('click', function(e) { e.stopPropagation(); selectEdge(this.dataset.edgeId); });
      el.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); selectEdge(this.dataset.edgeId); }
      });
    });
    var svg = document.querySelector('#elk-diagram svg');
    if (svg) svg.addEventListener('click', function(e) {
      if (e.target === svg || e.target.tagName === 'svg') clearHighlights();
    });
  }

  function selectNode(nodeId) {
    clearHighlights();
    var node = document.querySelector('#elk-diagram .state-node[data-node-id="' + nodeId + '"]');
    if (node) node.classList.add('highlighted');
    document.querySelectorAll('#elk-diagram .edge-group').forEach(function(ep) {
      if (ep.dataset.source === nodeId || ep.dataset.target === nodeId) {
        ep.classList.add('highlighted');
        var ln = ep.querySelector('.edge-line');
        if (ln) ln.setAttribute('marker-end', 'url(#arr-hl)');
      } else { ep.classList.add('dimmed'); }
    });
    document.querySelectorAll('#elk-diagram .state-node').forEach(function(n) {
      if (n.dataset.nodeId !== nodeId && !isNeighbor(nodeId, n.dataset.nodeId)) n.classList.add('dimmed');
    });
    document.querySelectorAll('#elk-diagram .edge-label').forEach(function(lbl) {
      var ep = document.querySelector('#elk-diagram .edge-group[data-edge-id="' + lbl.dataset.edgeId + '"]');
      if (ep && ep.classList.contains('dimmed')) lbl.classList.add('dimmed');
    });
    showNodeInfo(nodeId);
  }

  function selectEdge(edgeId) {
    clearHighlights();
    var el = document.querySelector('#elk-diagram .edge-group[data-edge-id="' + edgeId + '"]');
    if (!el) return;
    el.classList.add('highlighted');
    var ln = el.querySelector('.edge-line');
    if (ln) ln.setAttribute('marker-end', 'url(#arr-hl)');
    var src = el.dataset.source, tgt = el.dataset.target;
    document.querySelectorAll('#elk-diagram .state-node').forEach(function(n) {
      if (n.dataset.nodeId === src || n.dataset.nodeId === tgt) n.classList.add('highlighted');
      else n.classList.add('dimmed');
    });
    document.querySelectorAll('#elk-diagram .edge-group').forEach(function(ep) { if (ep !== el) ep.classList.add('dimmed'); });
    document.querySelectorAll('#elk-diagram .edge-label').forEach(function(lbl) { if (lbl.dataset.edgeId !== edgeId) lbl.classList.add('dimmed'); });
    showEdgeInfo(edgeId, src, tgt);
  }

  function isNeighbor(nodeId, otherId) {
    var edges = document.querySelectorAll('#elk-diagram .edge-group');
    for (var i = 0; i < edges.length; i++) {
      if ((edges[i].dataset.source === nodeId && edges[i].dataset.target === otherId) ||
          (edges[i].dataset.target === nodeId && edges[i].dataset.source === otherId)) return true;
    }
    return false;
  }

  function clearHighlights() {
    document.querySelectorAll('#elk-diagram .highlighted, #elk-diagram .dimmed').forEach(function(el) { el.classList.remove('highlighted', 'dimmed'); });
    document.querySelectorAll('#elk-diagram .edge-line[marker-end="url(#arr-hl)"]').forEach(function(p) { p.setAttribute('marker-end', 'url(#arr)'); });
    var panel = document.getElementById('elk-info-panel');
    if (panel) { panel.className = 'empty'; panel.textContent = 'Click a state or transition for details. Double-click a state to jump to its detail section.'; }
  }

  function showNodeInfo(nodeId) {
    var state = graphData.states.find(function(s) { return s.id === nodeId; });
    var panel = document.getElementById('elk-info-panel');
    if (!panel) return;
    panel.className = '';
    panel.textContent = '';
    var h = document.createElement('h3');
    h.textContent = state ? state.label : nodeId;
    panel.appendChild(h);
    if (state && state.description) {
      var d = document.createElement('p');
      d.textContent = state.description;
      panel.appendChild(d);
    }
  }

  function showEdgeInfo(edgeId, src, tgt) {
    var t = graphData.transitions.find(function(x) { return x.id === edgeId; });
    var panel = document.getElementById('elk-info-panel');
    if (!panel) return;
    panel.className = '';
    panel.textContent = '';
    var h = document.createElement('h3');
    h.textContent = 'Transition: ' + (t ? t.label : edgeId);
    panel.appendChild(h);
    var d = document.createElement('p');
    d.textContent = src + ' \u2192 ' + tgt;
    panel.appendChild(d);
  }

  // Controls
  ['ctl-direction', 'ctl-routing', 'ctl-spacing', 'ctl-clearance', 'ctl-labels'].forEach(function(id) {
    var el = document.getElementById(id);
    if (el) el.addEventListener('change', doLayout);
  });
  var btnZoomIn = document.getElementById('btn-zoom-in');
  var btnZoomOut = document.getElementById('btn-zoom-out');
  var btnFit = document.getElementById('btn-fit');
  var btnExport = document.getElementById('btn-export');
  if (btnZoomIn) btnZoomIn.addEventListener('click', function() { zoom(1.3); });
  if (btnZoomOut) btnZoomOut.addEventListener('click', function() { zoom(0.77); });
  if (btnFit) btnFit.addEventListener('click', fitToView);
  if (btnExport) btnExport.addEventListener('click', function() {
    var svg = document.querySelector('#elk-diagram svg');
    if (!svg) return;
    // Resolve CSS variables to computed values before serialization (they don't
    // resolve when rendered via Image→Canvas for PNG export)
    var root = getComputedStyle(document.documentElement);
    var neutralColor = root.getPropertyValue('--neutral').trim() || '#6e7781';
    var infoColor = root.getPropertyValue('--info').trim() || '#0969da';
    var cardColor = root.getPropertyValue('--card').trim() || '#f6f8fa';
    var clone = svg.cloneNode(true);
    // Replace CSS var references in markers with computed values
    clone.querySelectorAll('marker#arr path').forEach(function(p) { p.setAttribute('fill', neutralColor); });
    clone.querySelectorAll('marker#arr-hl path').forEach(function(p) { p.setAttribute('fill', infoColor); });
    // Replace CSS var references in edge/node styles
    clone.querySelectorAll('.edge-group path.edge-line').forEach(function(p) {
      if (!p.closest('.highlighted')) p.style.stroke = neutralColor;
    });
    clone.querySelectorAll('.state-node rect').forEach(function(r) {
      r.style.stroke = infoColor;
      r.style.fill = cardColor;
    });
    clone.querySelectorAll('.state-node text').forEach(function(t) {
      t.style.fill = root.getPropertyValue('--fg').trim() || '#1f2328';
    });
    clone.querySelectorAll('.edge-label text').forEach(function(t) {
      t.style.fill = root.getPropertyValue('--fg').trim() || '#1f2328';
    });
    clone.querySelectorAll('.edge-label rect').forEach(function(r) {
      r.style.fill = cardColor;
    });
    var data = new XMLSerializer().serializeToString(clone);
    var canvas = document.createElement('canvas');
    var box = svg.viewBox.baseVal;
    canvas.width = box.width * 2; canvas.height = box.height * 2;
    var ctx = canvas.getContext('2d');
    var img = new Image();
    img.onload = function() {
      ctx.fillStyle = cardColor;
      ctx.fillRect(0, 0, canvas.width, canvas.height);
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
      var a = document.createElement('a');
      a.href = canvas.toDataURL('image/png');
      a.download = 'state-diagram.png';
      a.click();
    };
    img.onerror = function() {
      console.error('PNG export failed — SVG could not be rendered as image');
    };
    img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(data);
  });

  // Keyboard shortcuts
  document.addEventListener('keydown', function(e) {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.tagName === 'SELECT') return;
    if (e.key === 'Escape') clearHighlights();
    if (e.key === 'f' && !e.ctrlKey && !e.metaKey) fitToView();
    if (e.key === '+' || e.key === '=') zoom(1.2);
    if (e.key === '-') zoom(0.83);
  });

  // Initial render
  doLayout();
})();
