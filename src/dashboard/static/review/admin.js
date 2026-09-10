const $ = id => document.getElementById(id);
async function request(path, method = 'GET') {
  const token = $('admin-token').value.trim();
  if (!token) throw new Error('Administrationsschluessel fehlt.');
  const response = await fetch(`/api/review/admin/${path}`, {
    method, credentials:'omit', cache:'no-store', headers:{Authorization:`Bearer ${token}`}, signal:AbortSignal.timeout(20000),
  });
  if (!response.ok) throw new Error(`Anfrage abgelehnt (HTTP ${response.status}).`);
  return response.json();
}
for (const [button,path,method] of [['invite','invitations','POST'],['summary','summary','GET'],['export','export','GET'],['purge','purge','POST']]) {
  $(button).addEventListener('click', async () => {
    $(button).disabled = true;
    try {
      const result = await request(path,method);
      if (button === 'export') {
        const url = URL.createObjectURL(new Blob([JSON.stringify(result,null,2)],{type:'application/json'}));
        const link = document.createElement('a'); link.href = url; link.download = `mhrn-PRIVATE-review-${new Date().toISOString().slice(0,10)}.json`; link.click(); setTimeout(() => URL.revokeObjectURL(url),1500);
        $('admin-status').textContent = 'Private Rohdaten exportiert. Nicht oeffentlich veroeffentlichen.';
      } else {
        $('admin-output').textContent = JSON.stringify(result,null,2);
        $('admin-status').textContent = button === 'invite' ? 'Einmal-Code privat weitergeben; er wird nur jetzt im Klartext ausgegeben.' : 'Anfrage verarbeitet.';
      }
    } catch(e) { $('admin-status').textContent = e.message || 'Anfrage fehlgeschlagen.'; }
    finally { $(button).disabled = false; }
  });
}
$('logout').addEventListener('click', () => { $('admin-token').value = ''; $('admin-output').textContent = ''; $('admin-status').textContent = 'Schluessel und Ansicht geloescht.'; });
