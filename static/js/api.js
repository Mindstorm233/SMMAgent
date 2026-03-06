/**
 * API Client - FastAPI backend
 */

const API = {
    baseUrl: '',

    async request(path, options = {}) {
        const url = `${this.baseUrl}${path}`;
        const res = await fetch(url, {
            headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
            ...options,
        });

        if (!res.ok) {
            let msg = `${res.status} ${res.statusText}`;
            try {
                const data = await res.json();
                msg = data?.detail || data?.error?.message || msg;
            } catch (_) { }
            throw new Error(msg);
        }

        // Some endpoints may return no body
        const text = await res.text();
        return text ? JSON.parse(text) : null;
    },

    async health() {
        return this.request('/api/v1/health');
    },

    async getModels() {
        return this.request('/api/v1/meta/models');
    },

    async createCompile(protocol_text) {
        const meta = await this.getModels();
        const defaults = meta?.defaults || {};

        return this.request('/api/v1/compile', {
            method: 'POST',
            body: JSON.stringify({
                protocol_text,
                models: {
                    chat_model: defaults.chat_model,
                    embed_model: defaults.embedding_model,
                    temperature: defaults.temperature
                },
                paths: {},     // 先用后端默认
                options: { return_draft: true, trace: true }
            })
        });
    },


    async getJob(jobId) {
        return this.request(`/api/v1/jobs/${jobId}`);
    },

    async cancelJob(jobId) {
        return this.request(`/api/v1/jobs/${jobId}/cancel`, { method: 'POST', body: '{}' });
    },

    async getResult(compileId) {
        return this.request(`/api/v1/compile/${compileId}/result`);
    },

    async listHistory() {
        return this.request('/api/v1/history');
    },

    async getHistoryDetail(compileId) {
        return this.request(`/api/v1/history/${compileId}`);
    },

    async drawSchemes(finalJson) {
        const url = `${this.baseUrl}/api/v1/draw`;
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ chip_data: finalJson })
        });

        if (!res.ok) {
            let msg = `${res.status} ${res.statusText}`;
            try {
                const data = await res.json();
                msg = data?.detail || data?.error?.message || msg;
            } catch (_) { }
            throw new Error(msg);
        }

        return await res.blob(); // image/png
    }

};

window.API = API;
