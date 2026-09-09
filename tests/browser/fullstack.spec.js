import { test, expect } from '@playwright/test';

test.use({ baseURL: 'http://127.0.0.1:4174' });

async function selectResearchView(page, view) {
  await page
    .locator(`[data-research-workspace-view="${view}"]`)
    .evaluate((button) => button.click());
  await expect(page.locator(`[data-research-workspace-panel="${view}"]`)).toBeVisible();
}

for (const port of [4174, 4175]) {
  test(`real server ${port}: routing, catalog, MSBA and shared file/chat renderer`, async ({ page }) => {
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(`http://127.0.0.1:${port}/`);
    await page.locator('[data-primary-area="science"]').click();
    await expect(page.locator('#workflow-research-results')).toBeVisible();
    await page.locator('#workflow-research-search').fill('RQ-MSBA-E01');
    await expect(page.locator('.research-rq-card')).toHaveCount(1);
    await page.locator('.research-rq-card').click();
    await expect(page.locator('#workflow-research-results')).toContainText('OPERATIONAL');
    await page.locator('#workflow-research-operational').check();
    await expect(page.locator('.research-rq-card')).toHaveCount(1);
    await page.locator('#workflow-research-operational').uncheck();
    await page.locator('[data-primary-area="wesen"]').click();
    await expect(page.locator('#wesen-neural-symbiosis')).toBeVisible();
    await expect(page.locator('#wesen-msba-pathways')).toContainText('Audio');
    await page.locator('[data-primary-area="science"]').click();
    await selectResearchView(page, 'files');
    await page.locator('.fm-source-btn[data-source="docs"]').click();
    await page.locator('.fm-file-label').filter({ hasText: 'preview.md' }).click();
    const viewer = page.locator('#fm-viewer');
    await expect(viewer).toHaveAttribute('data-render-state', 'ready');
    await expect(viewer.locator('.file-renderer-body h2')).toHaveText('Gemeinsamer Renderer');
    await expect(viewer.locator('.file-renderer-body script')).toHaveCount(0);
    expect(await page.evaluate(() => window.unsafeExecuted)).toBeUndefined();
    await viewer.getByRole('button', { name: 'Im Chat anzeigen', exact: true }).click();
    const card = page.locator('#research-chat-log .chat-file-card .file-renderer');
    await expect(card).toHaveAttribute('data-render-state', 'ready');
    await expect(card.locator('.file-renderer-body')).toContainText('Dateiinhalt');
    await expect(card.getByRole('button', { name: 'Bearbeiten', exact: true })).toHaveCount(0);
    await card.getByRole('button', { name: 'Messdaten', exact: true }).click();
    await expect(page.locator('[data-file-key="docs/sample.json"] .file-renderer')).toHaveAttribute('data-file-kind', 'json');
    await page.screenshot({ path: `test-results/fullstack-${port}.png`, fullPage: true });
    expect(errors).toEqual([]);
  });
}

test('real file service: edits persist, stale writers fail, originals stream', async ({ page }) => {
  await page.goto('http://127.0.0.1:4174/');
  const reference = 'notes/browser-edit.md';
  const url = `/api/files/document/${encodeURIComponent(reference)}?source=docs`;
  const created = await page.request.put(url, { data: { action: 'create', content: '# Original\n' } });
  expect(created.ok()).toBeTruthy();
  const data = await created.json();
  const edited = await page.request.put(url, { data: { action: 'write', content: '# Updated\n', expected_sha256: data.file.sha256 } });
  expect(edited.ok()).toBeTruthy();
  const stale = await page.request.put(url, { data: { action: 'write', content: 'stale', expected_sha256: data.file.sha256 } });
  expect(stale.status()).toBe(409);
  const raw = await page.request.get(`/api/files/raw/${encodeURIComponent(reference)}?source=docs`, { headers: { Range: 'bytes=0-8' } });
  expect(raw.status()).toBe(206);
  expect(await raw.text()).toBe('# Updated');
  const protectedWrite = await page.request.put('/api/files/document/registry%2Fquestions.yaml?source=research', { data: { action: 'write', content: '[]', expected_sha256: 'invalid' } });
  expect(protectedWrite.status()).toBe(403);
  const unknown = await page.request.get('/api/files/preview/unknown.b5d?source=docs');
  expect((await unknown.json()).kind).toBe('binary');
});

test('real registered batch: runner, manifest, DATA, report and central rendering', async ({ page }) => {
  await page.goto('http://127.0.0.1:4174/');
  const id = `EXP-BROWSER-${Date.now()}`;
  const response = await page.request.post('/api/experiment/workflow/batch', { data: {
    batch_id: id, protocols: ['temporal_order_spiking_v1'],
    protocol_options: { temporal_order_spiking_v1: { seeds: '101-120', ticks: 32 } },
  }, timeout: 30_000 });
  expect(response.ok()).toBeTruthy();
  const result = await response.json();
  expect(result.failed, JSON.stringify(result)).toBe(0);
  expect(result.completed).toBe(1);
  const path = `experiments/${id}-01/manifest.json`;
  const manifestResponse = await page.request.get(`/api/files/preview/${encodeURIComponent(path)}?source=research`);
  expect(manifestResponse.ok()).toBeTruthy();
  const descriptor = await manifestResponse.json();
  const manifest = JSON.parse(descriptor.content);
  expect(manifest.experiment_status).toBe('completed');
  expect(manifest.epistemic_layers.evid).toContain('not_created');
  expect(descriptor.read_only).toBe(true);
  await page.locator('[data-primary-area="science"]').click();
  await page.evaluate(async (filePath) => {
    const module = await import('/file-renderer.js');
    const host = document.createElement('section'); host.id = 'fullstack-artifact'; document.querySelector('#tab-research').prepend(host);
    await module.renderFile(host, { source: 'research', path: filePath });
  }, path);
  await expect(page.locator('#fullstack-artifact')).toHaveAttribute('data-render-state', 'ready');
  await expect(page.locator('#fullstack-artifact')).toContainText('temporal_order_spiking_v1');
});

test('real inventory changes reach the Wesen pipeline view without authorizing devices', async ({ page }) => {
  await page.goto('http://127.0.0.1:4174/');
  await page.locator('[data-primary-area="wesen"]').click();
  await page.request.post('/__test__/inventory', { data: { available: true } });
  const camera = page.locator('#wesen-symbiosis-pipelines .wesen-symbiosis-item').filter({ hasText: 'Camera' });
  const robot = page.locator('#wesen-symbiosis-pipelines .wesen-symbiosis-item').filter({ hasText: 'Robotics' });
  await expect(camera).toHaveClass(/reachable/);
  await expect(camera).toContainText('endpoint reachable');
  await expect(robot).toContainText('endpoint reachable');
  await expect.poll(async () => {
    const response = await page.request.get('/api/embodiment/connections');
    const data = await response.json();
    return data.connections.find(item => item.connection_id === 'sensor.camera.browser')?.available;
  }).toBe(true);
  await page.request.post('/__test__/inventory', { data: { available: false } });
  await expect.poll(async () => {
    const response = await page.request.get('/api/embodiment/connections');
    const data = await response.json();
    const item = data.connections.find(item => item.connection_id === 'sensor.camera.browser');
    return item && !item.available && !item.authorized && !item.active;
  }).toBe(true);
  await expect(camera).toContainText('endpoint unavailable');
  await expect(robot).toContainText('endpoint unavailable');
  await expect(page.locator('#wesen-neural-symbiosis')).toContainText('READ-ONLY');
});

test('canonical file viewer: split editor live preview and stale-write conflict diff', async ({ page }) => {
  await page.goto('http://127.0.0.1:4174/');
  const reference = `notes/split-editor-${Date.now()}.md`;
  const url = `/api/files/document/${encodeURIComponent(reference)}?source=docs`;
  const created = await page.request.put(url, { data: { action: 'create', content: '# Initial\n\nBody\n' } });
  expect(created.ok()).toBeTruthy();
  const createdData = await created.json();

  await page.evaluate(async (filePath) => {
    const module = await import('/file-renderer.js');
    const host = document.createElement('section');
    host.id = 'split-editor-artifact';
    document.body.append(host);
    await module.renderFile(host, { source: 'docs', path: filePath });
  }, reference);

  const host = page.locator('#split-editor-artifact');
  await expect(host).toHaveAttribute('data-render-state', 'ready');
  await host.getByRole('button', { name: 'Bearbeiten', exact: true }).click();
  await expect(host.locator('.file-renderer-editor-split')).toBeVisible();
  const editor = host.locator('.file-renderer-editor');
  await editor.fill('# Live Preview\n\nUpdated in browser');
  await expect(host.locator('.file-renderer-editor-preview')).toContainText('Live Preview');
  await expect(host.locator('.file-renderer-editor-preview')).toContainText('Updated in browser');

  const remote = await page.request.put(url, {
    data: { action: 'write', content: '# Remote Version\n', expected_sha256: createdData.file.sha256 },
  });
  expect(remote.ok()).toBeTruthy();
  await host.getByRole('button', { name: 'Speichern', exact: true }).click();
  await expect(host.locator('.file-renderer-body')).toContainText('Speicherkonflikt');
  await expect(host.locator('.file-renderer-body')).toContainText('Remote Version');
  await expect(host.locator('.file-renderer-body')).toContainText('Live Preview');
});

test('research review inbox completes an append-only human review', async ({ page }) => {
  await page.goto('http://127.0.0.1:4174/');
  await page.locator('[data-primary-area="science"]').click();
  await selectResearchView(page, 'review');
  await expect(page.locator('#workflow-review-inbox')).toBeVisible();
  const inboxResponse = await page.request.get('/api/research/reviews');
  expect(inboxResponse.ok()).toBeTruthy();
  const inbox = await inboxResponse.json();
  expect(Array.isArray(inbox.items)).toBeTruthy();
  await expect(page.locator('#workflow-review-count')).toContainText('offen');
});
