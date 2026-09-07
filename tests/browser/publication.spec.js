import { test, expect } from '@playwright/test';

test.use({ baseURL: 'http://127.0.0.1:4174' });

for (const port of [4174, 4175]) {
  test(`publication ${port}: complete research reader, central rendering and immutable originals`, async ({ page }) => {
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.goto(`http://127.0.0.1:${port}/`);
    await page.locator('[data-primary-area="science"]').click();
    await page.locator('.fm-source-btn[data-source="docs"]').click();
    await page.getByRole('button', { name: 'Abhandlung lesen', exact: true }).click();
    const viewer = page.locator('#fm-viewer');
    await expect(viewer).toHaveAttribute('data-render-state', 'ready');
    await expect(viewer).toContainText('Aktuelle Fassung 1.2');
    await viewer.getByRole('button', { name: 'Historische Lesefassung 1.0', exact: true }).click();
    await expect(viewer).toContainText('vollstaendige Lesefassung');
    await expect(page.locator('.fm-source-btn[data-source="research"]')).toHaveClass(/active/);
    await expect(viewer.getByRole('button', { name: 'Bearbeiten', exact: true })).toHaveCount(0);
    const prefix = `http://127.0.0.1:${port}/api/files/preview/`;
    const manifestResponse = await page.request.get(prefix + encodeURIComponent('publications/reader/manifest.json') + '?source=research');
    expect(manifestResponse.ok()).toBeTruthy();
    const manifest = JSON.parse((await manifestResponse.json()).content);
    expect(manifest.section_count).toBe(46);
    for (const section of manifest.sections) {
      const response = await page.request.get(prefix + encodeURIComponent(`publications/reader/${section.path}`) + '?source=research');
      expect(response.ok(), section.path).toBeTruthy();
      const descriptor = await response.json();
      expect(descriptor.truncated, section.path).toBe(false);
      expect(descriptor.read_only, section.path).toBe(true);
      expect(descriptor.editable, section.path).toBe(false);
      expect(descriptor.content, section.path).toContain('Inhaltsuebersicht');
    }
    await viewer.getByRole('button', { name: manifest.sections[0].title, exact: true }).click();
    await expect(viewer.getByRole('button', { name: 'Weiter', exact: true }).first()).toBeVisible();
    await viewer.getByRole('button', { name: 'Weiter', exact: true }).first().click();
    await expect(viewer).toContainText(manifest.sections[1].title);
    const write = await page.request.put(`http://127.0.0.1:${port}/api/files/document/` + encodeURIComponent('publications/reader/README.md') + '?source=research', {
      data: { action: 'write', content: 'unauthorized change', expected_sha256: 'invalid' },
    });
    expect(write.status()).toBe(403);
    const catalog = await page.request.get(prefix + encodeURIComponent('publications/catalog.json') + '?source=research');
    const publication = JSON.parse((await catalog.json()).content).publications[0];
    expect(publication.authority).toBe('interpretation_only');
    expect(publication.automatic_evidence_promotion).toBe(false);
    expect(errors).toEqual([]);
  });
}
