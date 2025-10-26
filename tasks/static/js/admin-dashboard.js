// admin-dashboard.js
document.addEventListener('DOMContentLoaded', () => {
  function readJSON(id, fallback) {
    const el = document.getElementById(id);
    if (!el) return fallback;
    try { return JSON.parse(el.textContent || el.innerText); }
    catch(e){ return fallback; }
  }

  const pending = Number(readJSON('pending-count', 0) || 0);
  const inProgress = Number(readJSON('inprogress-count', 0) || 0);
  const completed = Number(readJSON('completed-count', 0) || 0);

  const monthlyLabels = readJSON('monthly-labels', []);
  const monthlyValues = readJSON('monthly-values', []);

  const topLabels = readJSON('top-users-labels', []);
  const topValues = readJSON('top-users-values', []);

  // mini donut
  const ctxDonut = document.getElementById('miniDonut');
  if (ctxDonut) {
    new Chart(ctxDonut, {
      type: 'doughnut',
      data: {
        labels: ['Pending','In Progress','Completed'],
        datasets: [{
          data: [pending, inProgress, completed],
          backgroundColor: ['#b49ce3','#f4b183','#8fd19e'],
          borderWidth: 0
        }]
      },
      options: { responsive: true, maintainAspectRatio: false, cutout: '70%', plugins:{ legend:{ display:false } } }
    });
  }

  // area monthly
  const ctxArea = document.getElementById('areaChart');
  if (ctxArea) {
    new Chart(ctxArea, {
      type: 'line',
      data: {
        labels: monthlyLabels.length ? monthlyLabels : ['Jan','Feb','Mar','Apr','May'],
        datasets: [{
          label: 'Monthly Tasks',
          data: monthlyValues.length ? monthlyValues : [2,3,4,2,5],
          fill: true,
          borderColor: '#7c4dff',
          backgroundColor: 'rgba(124,77,255,0.08)',
          tension: 0.35,
          pointRadius: 0
        }]
      },
      options: { responsive: true, maintainAspectRatio:false, plugins:{ legend:{ display:false }}, scales:{ x:{ display:false } } }
    });
  }

  // top users bar
  const ctxBar = document.getElementById('barChart');
  if (ctxBar) {
    new Chart(ctxBar, {
      type: 'bar',
      data: {
        labels: topLabels.length ? topLabels : ['A','B','C','D','E'],
        datasets: [{
          label: 'Completed',
          data: topValues.length ? topValues : [1,2,1,3,2],
          backgroundColor: 'rgba(124,77,255,0.85)',
          borderRadius: 6,
          maxBarThickness: 36
        }]
      },
      options: { responsive:true, maintainAspectRatio:false, plugins:{ legend:{ display:false } }, scales:{ y:{ beginAtZero:true } } }
    });
  }
});
