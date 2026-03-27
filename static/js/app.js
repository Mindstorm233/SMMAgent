/**
 * Generator Page Logic (MVP)
 */

const App = {
  currentJobId: null,
  currentCompileId: null,
  currentResult: null,
  pollingTimer: null,
  activeTab: 'json',
  schemeBlobUrl: null,
  schemeLastHash: null,

  async init() {
    await this.loadConfig();
    this.bindEvents();
    this.switchTab('json');
    this.setStatus('ready');
    this.updateProgress(0, 'Idle');
  },

  async loadConfig() {
    const configBar = document.getElementById('configBar');
    try {
      const meta = await API.getModels();
      const chat = meta?.defaults?.chat_model || (meta?.chat_models || [])[0] || '-';
      const emb = meta?.defaults?.embedding_model || (meta?.embedding_models || [])[0] || '-';
      const temp = meta?.defaults?.temperature ?? 0.0;

      configBar.innerHTML = `
        <div class="config-item">
          <span class="config-label">Chat:</span>
          <span class="config-value">${chat}</span>
        </div>
        <div class="config-divider"></div>
        <div class="config-item">
          <span class="config-label">Embedding:</span>
          <span class="config-value">${emb}</span>
        </div>
        <div class="config-divider"></div>
        <div class="config-item">
          <span class="config-label">Temperature:</span>
          <span class="config-value">${temp}</span>
        </div>
        <div class="config-divider"></div>
        <div class="config-item">
          <span class="config-label">Status:</span>
          <span class="status status-ready">
            <span class="status-dot"></span>
            <span>Ready</span>
          </span>
        </div>
      `;
    } catch (e) {
      console.error(e);
      configBar.innerHTML = `
        <div class="config-item">
          <span class="config-label">Status:</span>
          <span class="status status-error">
            <span class="status-dot"></span>
            <span>Backend not reachable</span>
          </span>
        </div>`;
    }
  },

  bindEvents() {
    document.querySelectorAll('.tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        const tabName = e.target.dataset.tab;
        if (tabName) this.switchTab(tabName);
      });
    });

    document.getElementById('btnGenerate')?.addEventListener('click', () => this.handleGenerate());
    document.getElementById('btnStop')?.addEventListener('click', () => this.handleStop());
    document.getElementById('btnClear')?.addEventListener('click', () => this.handleClear());
  },

  switchTab(tabName) {
    this.activeTab = tabName;
    document.querySelectorAll('.tab').forEach(tab => {
      tab.classList.toggle('active', tab.dataset.tab === tabName);
    });
    document.querySelectorAll('.tab-content').forEach(content => {
      content.classList.toggle('active', content.id === `tab-${tabName}`);
    });
  },

  async handleGenerate() {
    const protocol = (document.getElementById('protocolInput')?.value || '').trim();
    if (!protocol) {
      Utils.showToast('Please enter a protocol first', 'warning');
      return;
    }

    this.currentResult = null;
    this.currentCompileId = null;

    this.showProgress();
    this.setButtonsState(true);
    this.setStatus('generating');
    this.updateProgress(5, 'Submitting job...');

    try {
      const job = await API.createCompile(protocol);
      this.currentJobId = job.job_id;

      Utils.showToast(`Job created: ${this.currentJobId}`, 'info');
      await this.pollJobUntilDone(this.currentJobId);

    } catch (e) {
      console.error(e);
      Utils.showToast(`Generate failed: ${e.message}`, 'error');
      this.setStatus('error');
      this.setButtonsState(false);
      this.hideProgress();
    }
  },

  async pollJobUntilDone(jobId) {
    if (this.pollingTimer) clearInterval(this.pollingTimer);

    return new Promise((resolve, reject) => {
      this.pollingTimer = setInterval(async () => {
        try {
          const job = await API.getJob(jobId);
          const pct = job.progress?.percent ?? 0;
          const msg = job.progress?.message || job.progress?.stage || 'Running...';
          this.updateProgress(pct, msg);

          if (job.status === 'succeeded') {
            clearInterval(this.pollingTimer);
            this.pollingTimer = null;

            const compileId = job.result_ref?.id;
            if (!compileId) throw new Error('Missing compile_id in result_ref');

            this.currentCompileId = compileId;
            const result = await API.getResult(compileId);
            this.currentResult = result;

            this.renderResult(result);
            this.switchTab('json');

            Utils.showToast('Generation completed ✅', 'success');
            this.setStatus('ready');
            this.setButtonsState(false);
            this.hideProgress();
            resolve(true);
          }

          if (job.status === 'failed' || job.status === 'cancelled') {
            clearInterval(this.pollingTimer);
            this.pollingTimer = null;

            const errMsg = job.error?.message || 'Job failed';
            Utils.showToast(errMsg, job.status === 'cancelled' ? 'info' : 'error');

            this.setStatus('ready');
            this.setButtonsState(false);
            this.hideProgress();
            resolve(false);
          }
        } catch (e) {
          clearInterval(this.pollingTimer);
          this.pollingTimer = null;
          reject(e);
        }
      }, 800);
    });
  },

  async handleStop() {
    if (!this.currentJobId) {
      Utils.showToast('No running job', 'warning');
      return;
    }
    try {
      await API.cancelJob(this.currentJobId);
      Utils.showToast('Cancelling job...', 'info');
      // Let polling pick up cancelled status later
    } catch (e) {
      Utils.showToast(`Cancel failed: ${e.message}`, 'error');
    }
  },

  handleClear() {
    const protocolInput = document.getElementById('protocolInput');
    if (protocolInput) protocolInput.value = '';

    this.currentJobId = null;
    this.currentCompileId = null;
    this.currentResult = null;

    this.clearResult();
    this.updateProgress(0, 'Idle');
    this.hideProgress();
    this.setButtonsState(false);
    this.setStatus('ready');

    Utils.showToast('Cleared', 'info');
  },

  setButtonsState(running) {
    const gen = document.getElementById('btnGenerate');
    const stop = document.getElementById('btnStop');
    if (gen) gen.disabled = running;
    if (stop) stop.disabled = !running;
  },

  showProgress() {
    const el = document.querySelector('.progress-section');
    if (el) el.classList.add('visible');
  },

  hideProgress() {
    const el = document.querySelector('.progress-section');
    if (el) el.classList.remove('visible');
  },

  updateProgress(percent, message) {
    const fill = document.querySelector('.progress-fill');
    const text = document.querySelector('.progress-status');
    const pct = document.querySelector('.progress-percent');
    if (fill) fill.style.width = `${percent}%`;
    if (text) text.textContent = message || '';
    if (pct) pct.textContent = `${percent}%`;
  },

  setStatus(status) {
    const statusEl = document.querySelector('.status');
    if (!statusEl) return;
    statusEl.className = `status status-${status}`;
    const statusText = statusEl.querySelector('span:last-child');
    const labels = { ready: 'Ready', generating: 'Generating...', error: 'Error' };
    if (statusText) statusText.textContent = labels[status] || 'Ready';
  },

  renderResult(result) {
    const draft = result.draft || {};
    const final = result.final || {};

    this.renderJSONPair(draft, final);
    this.renderCompare(result);
    this.renderEvidence(result.evidence || []);
    this.renderRunbookPair(draft.plan || [], final.plan || []);
    this.renderSchemes(final);

  }
  ,

  renderJSON(finalJson) {
    const container = document.getElementById('tab-json');
    if (!container) return;

    const sections = ['instances', 'connections', 'plan'];

    container.innerHTML = sections.map(section => `
      <div class="collapsible open">
        <div class="collapsible-header">
          <div class="collapsible-title">
            <span>${section === 'instances' ? '🧩' : section === 'connections' ? '🔗' : '📋'}</span>
            <span>${section}</span>
            <span class="badge badge-primary">${(finalJson[section] || []).length} items</span>
          </div>
          <span class="collapsible-icon">▼</span>
        </div>
        <div class="collapsible-content">
          <div class="code-block">
            <div class="code-header">
              <span class="code-title">${section}.json</span>
              <button class="btn btn-ghost btn-sm code-copy-btn" onclick="App.copySection('${section}')">
                📋 Copy
              </button>
            </div>
            <pre class="code-content">${Utils.highlightJSON(finalJson[section] || [])}</pre>
          </div>
        </div>
      </div>
    `).join('');

    container.querySelectorAll('.collapsible-header').forEach(header => {
      header.addEventListener('click', () => header.closest('.collapsible').classList.toggle('open'));
    });
  },

  renderJSONPair(draftJson, finalJson) {
    const container = document.getElementById('tab-json');
    if (!container) return;

    const sections = ['reasoning', 'instances', 'connections', 'plan'];

    const renderSide = (title, icon, data) => `
    <div style="flex:1; min-width: 320px;">
      <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:10px;">
        <div style="font-weight:600; display:flex; gap:8px; align-items:center;">
          <span>${icon}</span><span>${title}</span>
        </div>
        <button class="btn btn-ghost btn-sm" onclick="App.copyWhole('${title.toLowerCase()}')">📋 Copy</button>
      </div>
      ${sections.map(section => this.renderSectionBlock(section, data)).join('')}
    </div>
  `;

    container.innerHTML = `
    <div style="display:flex; gap:14px; flex-wrap:wrap;">
      ${renderSide('Draft', '🧪', draftJson)}
      ${renderSide('Final', '✅', finalJson)}
    </div>
  `;

    // Rebind collapsibles
    container.querySelectorAll('.collapsible-header').forEach(header => {
      header.addEventListener('click', () => header.closest('.collapsible').classList.toggle('open'));
    });

    // cache for copy
    this._draftCache = draftJson;
    this._finalCache = finalJson;
  },

  renderSectionBlock(section, data) {
    const icon = section === 'reasoning' ? '🧠' : section === 'instances' ? '🧩' : section === 'connections' ? '🔗' : '📋';
    const value = data?.[section];

    const count = Array.isArray(value) ? value.length : (value ? 1 : 0);
    const contentObj = (section === 'reasoning')
      ? (value || '')
      : (value || []);

    return `
    <div class="collapsible open">
      <div class="collapsible-header">
        <div class="collapsible-title">
          <span>${icon}</span>
          <span>${section}</span>
          <span class="badge badge-primary">${count} items</span>
        </div>
        <span class="collapsible-icon">▼</span>
      </div>
      <div class="collapsible-content">
        <div class="code-block">
          <pre class="code-content">${Utils.highlightJSON(contentObj)}</pre>
        </div>
      </div>
    </div>
  `;
  },

  async copyWhole(which) {
    const obj = (which === 'draft') ? (this._draftCache || {}) : (this._finalCache || {});
    const text = JSON.stringify(obj, null, 2);
    const ok = await Utils.copyToClipboard(text);
    Utils.showToast(ok ? 'Copied!' : 'Copy failed', ok ? 'success' : 'error');
  },


  async copySection(section) {
    if (!this.currentResult?.final) return;
    const data = JSON.stringify(this.currentResult.final[section] || [], null, 2);
    const ok = await Utils.copyToClipboard(data);
    Utils.showToast(ok ? 'Copied!' : 'Copy failed', ok ? 'success' : 'error');
  },

  renderCompare(result) {
    const container = document.getElementById('tab-compare');
    if (!container) return;

    const stats = result.stats || {};
    const diff = result.diff || {};
    const draft = result.draft || {};
    const final = result.final || {};

    const instDiff = (stats.final_instances ?? 0) - (stats.draft_instances ?? 0);
    const connDiff = (stats.final_connections ?? 0) - (stats.draft_connections ?? 0);

    const listBlock = (title, arr) => `
    <div style="margin-top:10px;">
      <div style="font-weight:600; margin-bottom:6px;">${title} <span class="badge badge-primary">${(arr || []).length}</span></div>
      <div class="code-block"><pre class="code-content">${Utils.highlightJSON(arr || [])}</pre></div>
    </div>
  `;

    container.innerHTML = `
    <div style="display:flex; flex-direction:column; gap:14px;">
      <div class="panel" style="border:1px solid var(--border-color); border-radius: var(--radius-lg);">
        <div class="panel-header">
          <div class="panel-title"><span>📊</span><span>Review Report (Draft vs Final)</span></div>
        </div>
        <div class="panel-body">
          <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px;">
            <div>
              <div style="font-weight:700; margin-bottom:6px;">🧪 Draft Reasoning</div>
              <div class="code-block"><pre class="code-content">${Utils.highlightJSON(draft.reasoning || '')}</pre></div>
            </div>
            <div>
              <div style="font-weight:700; margin-bottom:6px;">✅ Final Reasoning</div>
              <div class="code-block"><pre class="code-content">${Utils.highlightJSON(final.reasoning || '')}</pre></div>
            </div>
          </div>

          <div style="margin-top:14px;">
            <div style="font-weight:700; margin-bottom:6px;">📈 Change Summary</div>
            <div style="display:flex; gap:10px; flex-wrap:wrap;">
              <span class="badge badge-primary">Instances: ${stats.draft_instances ?? 0} → ${stats.final_instances ?? 0} (${instDiff >= 0 ? '+' : ''}${instDiff})</span>
              <span class="badge badge-primary">Connections: ${stats.draft_connections ?? 0} → ${stats.final_connections ?? 0} (${connDiff >= 0 ? '+' : ''}${connDiff})</span>
              <span class="badge badge-primary">RAG Docs: ${stats.doc_count ?? '-'}</span>
              <span class="badge badge-primary">Gen: ${(stats.gen_time ?? 0).toFixed(2)}s</span>
              <span class="badge badge-primary">Ver: ${(stats.ver_time ?? 0).toFixed(2)}s</span>
              <span class="badge badge-primary">Total: ${Utils.formatDuration(stats.duration_ms ?? 0)}</span>
            </div>
          </div>

          <div style="margin-top:14px;">
            <div style="font-weight:700; margin-bottom:6px;">🧾 Added / Removed IDs</div>
            ${listBlock('🧩 Instances Added', diff.instances_added)}
            ${listBlock('🧩 Instances Removed', diff.instances_removed)}
            ${listBlock('🔗 Connections Added', diff.connections_added)}
            ${listBlock('🔗 Connections Removed', diff.connections_removed)}
          </div>
        </div>
      </div>
    </div>
  `;
  },

  async renderSchemes(finalJson) {
    const container = document.getElementById('tab-schemes');
    if (!container) return;

    const jsonStr = JSON.stringify(finalJson || {});
    const hash = String(jsonStr.length) + ':' + (jsonStr.slice(0, 200) || '');

    // If final is unchanged, don't re-request
    if (this.schemeLastHash === hash && this.schemeBlobUrl) {
      container.innerHTML = this._renderSchemesPanel(this.schemeBlobUrl);
      this._bindSchemesDownload(this.schemeBlobUrl);
      return;
    }

    container.innerHTML = `
    <div class="empty-state">
      <div class="spinner spinner-lg"></div>
      <div class="empty-state-title mt-4">Rendering schemes...</div>
      <div class="empty-state-text">Calling draw API to generate PNG</div>
    </div>
  `;

    try {
      const blob = await API.drawSchemes(finalJson);

      // Revoke the old URL to avoid memory leaks
      if (this.schemeBlobUrl) URL.revokeObjectURL(this.schemeBlobUrl);

      const url = URL.createObjectURL(blob);
      this.schemeBlobUrl = url;
      this.schemeLastHash = hash;

      container.innerHTML = this._renderSchemesPanel(url);
      this._bindSchemesDownload(url);
    } catch (e) {
      console.error(e);
      container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">❌</div>
        <div class="empty-state-title">Render failed</div>
        <div class="empty-state-text">${Utils.escapeHtml(e.message || 'Unknown error')}</div>
      </div>
    `;
      Utils.showToast('Schemes render failed', 'error');
    }
  },

  _renderSchemesPanel(imgUrl) {
    return `
    <div style="display:flex; flex-direction:column; gap:12px;">
      <div style="display:flex; align-items:center; justify-content:space-between; gap:10px; flex-wrap:wrap;">
        <div style="font-weight:700; display:flex; gap:8px; align-items:center;">
          <span>🖼️</span><span>Schemes</span>
        </div>
        <div style="display:flex; gap:8px; flex-wrap:wrap;">
          <button id="btnDownloadSchemes" class="btn btn-primary btn-sm">⬇️ Download PNG</button>
          <button id="btnOpenSchemes" class="btn btn-ghost btn-sm">🔍 Open</button>
        </div>
      </div>

      <div class="panel" style="border:1px solid var(--border-color); border-radius: var(--radius-lg);">
        <div class="panel-body" style="padding:12px;">
          <img src="${imgUrl}"
               alt="microfluidic schemes"
               style="width:100%; height:auto; display:block; border-radius:10px; border:1px solid var(--border-color);" />
        </div>
      </div>
    </div>
  `;
  },

  _bindSchemesDownload(imgUrl) {
    const btnDl = document.getElementById('btnDownloadSchemes');
    const btnOpen = document.getElementById('btnOpenSchemes');

    if (btnDl) {
      btnDl.onclick = () => {
        const a = document.createElement('a');
        a.href = imgUrl;
        a.download = `microfluidic_layout_${Date.now()}.png`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        Utils.showToast('Download started ✅', 'success');
      };
    }

    if (btnOpen) {
      btnOpen.onclick = () => window.open(imgUrl, '_blank');
    }
  },


  renderEvidence(evidence) {
    const container = document.getElementById('tab-evidence');
    if (!container) return;

    if (!evidence.length) {
      container.innerHTML = `
        <div class="empty-state">
          <div class="empty-state-icon">📚</div>
          <div class="empty-state-title">No evidence available</div>
          <div class="empty-state-text">Generate a result to see retrieved evidence</div>
        </div>`;
      return;
    }

    container.innerHTML = evidence.map(ev => `
      <div class="evidence-card">
        <div class="evidence-header">
          <div class="evidence-source">
            <span>📄</span>
            <span>${Utils.escapeHtml(ev.source || 'ref')}</span>
          </div>
          <div class="evidence-score">Score: ${((ev.score || 1) * 100).toFixed(0)}%</div>
        </div>
        <div class="evidence-snippet">${Utils.escapeHtml(ev.snippet || '')}</div>
        <div class="evidence-location">📍 ${Utils.escapeHtml(ev.location || '')}</div>
      </div>
    `).join('');
  },

  renderRunbookPair(draftPlan, finalPlan) {
    const container = document.getElementById('tab-runbook');
    if (!container) return;

    const renderTimeline = (title, icon, plan) => {
      if (!plan || !plan.length) {
        return `
        <div style="flex:1; min-width:320px;">
          <div style="font-weight:700; margin-bottom:8px;">${icon} ${title}</div>
          <div class="empty-state">
            <div class="empty-state-icon">📋</div>
            <div class="empty-state-title">No plan</div>
          </div>
        </div>`;
      }
      return `
      <div style="flex:1; min-width:320px;">
        <div style="font-weight:700; margin-bottom:8px;">${icon} ${title}</div>
        <div class="timeline">
          ${plan.map(step => `
            <div class="timeline-item">
              <div class="timeline-dot"></div>
              <div class="timeline-content">
                <div class="timeline-step">Step ${step.step_id ?? '-'}</div>
                <div class="timeline-action">${Utils.escapeHtml(step.action || '')}</div>
                <div class="timeline-duration">⏱️ Duration: ${step.duration_s ?? 0}s</div>
              </div>
            </div>
          `).join('')}
        </div>
      </div>`;
    };

    container.innerHTML = `
    <div style="display:flex; gap:14px; flex-wrap:wrap;">
      ${renderTimeline('Draft Runbook', '🧪', draftPlan)}
      ${renderTimeline('Final Runbook', '✅', finalPlan)}
    </div>
  `;
  },


  clearResult() {
    const empty = (icon, title, text) => `
      <div class="empty-state">
        <div class="empty-state-icon">${icon}</div>
        <div class="empty-state-title">${title}</div>
        <div class="empty-state-text">${text}</div>
      </div>`;

    const json = document.getElementById('tab-json');
    const evidence = document.getElementById('tab-evidence');
    const runbook = document.getElementById('tab-runbook');
    const schemes = document.getElementById('tab-schemes');


    if (json) json.innerHTML = empty('{ }', 'No data yet', 'Enter a protocol and click Generate to start');
    if (evidence) evidence.innerHTML = empty('📚', 'No evidence available', 'Generate a result to see retrieved evidence');
    if (runbook) runbook.innerHTML = empty('📋', 'No operation plan available', 'Generate a result to see the operation timeline');
    if (schemes) schemes.innerHTML = empty('🖼️', 'No schemes yet', 'Generate a result to render the microfluidic layout');

    if (this.schemeBlobUrl) {
      URL.revokeObjectURL(this.schemeBlobUrl);
      this.schemeBlobUrl = null;
      this.schemeLastHash = null;
    }

  }
};

document.addEventListener('DOMContentLoaded', () => App.init());
window.App = App;
