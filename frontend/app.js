const API_BASE = 'http://127.0.0.1:5000';

function q(id){return document.getElementById(id);}

async function getJSON(url){
  const res = await fetch(url);
  if(!res.ok) throw new Error(await res.text());
  return res.json();
}

function params(){
  const start = q('start').value;
  const end = q('end').value;
  const s = new URLSearchParams();
  if(start) s.set('start', start);
  if(end) s.set('end', end);
  return s.toString();
}

async function refresh(){
  try {
    const p = params();
    const metrics = await getJSON(`${API_BASE}/api/summary/metrics?${p}`);
    q('kpi-trips').textContent = metrics.trips ?? '-';
    q('kpi-speed').textContent = metrics.avg_speed_kmh ?? '-';
    q('kpi-fpkm').textContent = metrics.avg_fare_per_km ?? '-';
    q('kpi-tfare').textContent = metrics.total_fare ?? '-';

    const top = await getJSON(`${API_BASE}/api/summary/top-pickups?k=10&${p}`);

    const trips = await getJSON(`${API_BASE}/api/trips?limit=50&${p}`);
    renderTrips(trips);
  } catch (e){
    console.error(e);
    alert('Failed to load data — is the API running and DB loaded?');
  }
}

function renderTrips(rows){
  const tb = document.querySelector('#trips tbody');
  tb.innerHTML = '';
  rows.forEach(r => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${r.pickup_datetime ?? ''}</td>
      <td>${r.dropoff_datetime ?? ''}</td>
      <td>${r.pickup_zone ?? ''}</td>
      <td>${r.dropoff_zone ?? ''}</td>
      <td>${r.trip_distance ?? ''}</td>
      <td>${r.duration_sec ?? ''}</td>
      <td>${r.fare_amount ?? ''}</td>
      <td>${r.tip_amount ?? ''}</td>
      <td>${r.speed_kmh ?? ''}</td>
    `;
    tb.appendChild(tr);
  });
}

document.getElementById('refresh').addEventListener('click', refresh);
refresh();
