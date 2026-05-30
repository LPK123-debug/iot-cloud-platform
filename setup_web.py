import os

base = os.path.join("C:\\iot-cloud-platform", "web")
os.makedirs(base, exist_ok=True)

files = {}

files['index.html'] = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IoT Cloud Platform</title>
    <link rel="stylesheet" href="css/style.css">
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
</head>
<body>
    <div class="sidebar">
        <div class="logo">
            <div class="logo-icon">IoT</div>
            <div class="logo-text">Cloud Platform</div>
        </div>
        <nav>
            <a href="#" class="nav-item active" data-page="dashboard"><span class="nav-icon">Dashboard</span></a>
            <a href="#" class="nav-item" data-page="devices"><span class="nav-icon">Devices</span></a>
            <a href="#" class="nav-item" data-page="history"><span class="nav-icon">History</span></a>
        </nav>
        <div class="sidebar-footer"><div class="status-dot"></div><span>System Online</span></div>
    </div>
    <div class="main-content">
        <div id="dashboard" class="page active">
            <div class="page-header"><h1>Dashboard</h1><p>Real-time overview of all devices</p></div>
            <div class="stats-row" id="statsRow"></div>
            <div class="page-header" style="margin-top:32px"><h2>Device Overview</h2></div>
            <div class="device-grid" id="deviceGrid"></div>
        </div>
        <div id="devices" class="page">
            <div class="page-header"><h1>Devices</h1><p>Manage and control your devices</p></div>
            <div class="btn-row"><button class="btn btn-primary" onclick="showAddDevice()">+ Add Device</button></div>
            <div id="addDeviceForm" class="form-box hidden">
                <h3>Register New Device</h3>
                <div class="form-group"><label>Device ID</label><input type="text" id="newDevId" placeholder="e.g. dev002"></div>
                <div class="form-group"><label>Name</label><input type="text" id="newDevName" placeholder="e.g. Bedroom Sensor"></div>
                <div class="form-group"><label>Description</label><input type="text" id="newDevDesc" placeholder="Optional"></div>
                <div class="btn-row"><button class="btn btn-primary" onclick="addDevice()">Submit</button><button class="btn btn-secondary" onclick="hideAddDevice()">Cancel</button></div>
            </div>
            <div class="device-list" id="deviceList"></div>
        </div>
        <div id="history" class="page">
            <div class="page-header"><h1>History</h1><p>View historical sensor data</p></div>
            <div class="form-row">
                <div class="form-group"><label>Device</label><select id="histDevice"></select></div>
                <div class="form-group"><label>Data Type</label><select id="histType"><option value="temperature">Temperature</option><option value="humidity">Humidity</option><option value="light">Light</option></select></div>
                <div class="form-group"><label>Limit</label><select id="histLimit"><option value="20">Last 20</option><option value="50">Last 50</option><option value="100">Last 100</option></select></div>
                <div class="form-group"><button class="btn btn-primary" onclick="loadHistory()" style="margin-top:24px">Query</button></div>
            </div>
            <div class="chart-container"><canvas id="historyChart"></canvas></div>
        </div>
    </div>
    <div id="toast" class="toast hidden"></div>
    <script src="js/api.js"></script>
    <script src="js/app.js"></script>
</body>
</html>'''

files['css/style.css'] = ''':root{--bg:#0a0e17;--bg-card:#111827;--bg-hover:#1e293b;--accent:#22d3ee;--accent-dim:rgba(34,211,238,.15);--success:#34d399;--danger:#f87171;--warning:#fbbf24;--text:#e2e8f0;--text-muted:#64748b;--border:#1e293b;--radius:12px}*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Noto Sans SC',sans-serif;background:var(--bg);color:var(--text);display:flex;min-height:100vh}.sidebar{width:240px;background:var(--bg-card);border-right:1px solid var(--border);padding:24px 16px;display:flex;flex-direction:column;position:fixed;height:100vh;z-index:10}.logo{display:flex;align-items:center;gap:10px;padding:0 8px 24px;border-bottom:1px solid var(--border);margin-bottom:24px}.logo-icon{width:40px;height:40px;background:var(--accent);color:var(--bg);border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}.logo-text{font-size:16px;font-weight:500}.nav-item{display:flex;align-items:center;gap:12px;padding:12px 16px;border-radius:8px;color:var(--text-muted);text-decoration:none;transition:all .2s;margin-bottom:4px;font-size:14px}.nav-item:hover{background:var(--bg-hover);color:var(--text)}.nav-item.active{background:var(--accent-dim);color:var(--accent)}.sidebar-footer{margin-top:auto;display:flex;align-items:center;gap:8px;padding:16px 8px;border-top:1px solid var(--border);font-size:13px;color:var(--text-muted)}.status-dot{width:8px;height:8px;background:var(--success);border-radius:50%;animation:pulse 2s infinite}@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}.main-content{margin-left:240px;flex:1;padding:32px 40px}.page{display:none}.page.active{display:block}.page-header{margin-bottom:24px}.page-header h1{font-size:28px;font-weight:700;margin-bottom:4px}.page-header h2{font-size:20px;font-weight:500;margin-bottom:4px}.page-header p{color:var(--text-muted);font-size:14px}.stats-row{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:16px;margin-bottom:32px}.stat-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:20px;transition:border-color .2s}.stat-card:hover{border-color:var(--accent)}.stat-label{font-size:12px;text-transform:uppercase;letter-spacing:1px;color:var(--text-muted);margin-bottom:8px}.stat-value{font-family:'JetBrains Mono',monospace;font-size:32px;font-weight:600;color:var(--accent)}.stat-value.success{color:var(--success)}.stat-value.danger{color:var(--danger)}.stat-value.warning{color:var(--warning)}.device-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}.device-card{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:20px;cursor:pointer;transition:all .2s;position:relative;overflow:hidden}.device-card:hover{border-color:var(--accent);transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,.3)}.device-card.offline{opacity:.6}.device-card-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:16px}.device-card-name{font-size:16px;font-weight:500}.device-status{padding:4px 10px;border-radius:20px;font-size:11px;font-weight:500;text-transform:uppercase;letter-spacing:.5px}.device-status.online{background:rgba(52,211,153,.15);color:var(--success)}.device-status.offline{background:rgba(248,113,113,.15);color:var(--danger)}.sensor-values{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}.sensor-item{text-align:center}.sensor-label{font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px}.sensor-value{font-family:'JetBrains Mono',monospace;font-size:18px;font-weight:600}.sensor-value.temp{color:#f87171}.sensor-value.humid{color:#60a5fa}.sensor-value.light{color:#fbbf24}.device-list{display:flex;flex-direction:column;gap:8px;margin-top:16px}.device-list-item{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:16px 20px;display:grid;grid-template-columns:60px 1fr 1fr 100px 120px 100px;align-items:center;gap:16px;transition:border-color .2s}.device-list-item:hover{border-color:var(--accent)}.device-list-item.header{background:transparent;border:none;font-size:11px;text-transform:uppercase;letter-spacing:1px;color:var(--text-muted);padding:8px 20px}.btn{padding:8px 16px;border:none;border-radius:8px;font-size:13px;font-weight:500;cursor:pointer;transition:all .2s}.btn-primary{background:var(--accent);color:var(--bg)}.btn-primary:hover{background:#06b6d4}.btn-secondary{background:var(--bg-hover);color:var(--text)}.btn-secondary:hover{background:var(--border)}.btn-danger{background:var(--danger);color:#fff}.btn-danger:hover{background:#ef4444}.btn-small{padding:4px 10px;font-size:12px}.btn-row{display:flex;gap:8px;margin-bottom:16px}.form-box{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;margin-bottom:24px}.form-box h3{margin-bottom:16px;font-size:16px}.form-group{margin-bottom:12px}.form-group label{display:block;font-size:12px;color:var(--text-muted);margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px}.form-group input,.form-group select{width:100%;padding:10px 12px;background:var(--bg);border:1px solid var(--border);border-radius:8px;color:var(--text);font-size:14px;outline:none;transition:border-color .2s}.form-group input:focus,.form-group select:focus{border-color:var(--accent)}.form-row{display:flex;gap:16px;align-items:flex-end;margin-bottom:24px;flex-wrap:wrap}.form-row .form-group{flex:1;min-width:150px;margin-bottom:0}.chart-container{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;height:400px}.control-panel{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:24px;margin-top:16px}.control-panel h3{margin-bottom:16px}.relay-row{display:flex;align-items:center;justify-content:space-between;padding:12px 0;border-bottom:1px solid var(--border)}.relay-row:last-child{border-bottom:none}.relay-info{display:flex;align-items:center;gap:12px}.relay-indicator{width:12px;height:12px;border-radius:50%;background:var(--text-muted)}.relay-indicator.on{background:var(--success);box-shadow:0 0 8px var(--success)}.relay-buttons{display:flex;gap:8px}.toast{position:fixed;bottom:24px;right:24px;padding:12px 24px;border-radius:8px;font-size:14px;z-index:100;transition:all .3s}.toast.success{background:var(--success);color:var(--bg)}.toast.error{background:var(--danger);color:#fff}.toast.hidden{opacity:0;pointer-events:none;transform:translateY(10px)}.hidden{display:none}.detail-modal{position:fixed;inset:0;background:rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center;z-index:50}.detail-content{background:var(--bg-card);border:1px solid var(--border);border-radius:var(--radius);padding:32px;width:600px;max-width:90vw;max-height:80vh;overflow-y:auto}.detail-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:24px}.detail-close{background:none;border:none;color:var(--text-muted);font-size:24px;cursor:pointer}.detail-close:hover{color:var(--text)}@media(max-width:768px){.sidebar{width:60px;padding:16px 8px}.logo-text,.nav-icon,.sidebar-footer span{display:none}.main-content{margin-left:60px;padding:16px}.device-list-item{grid-template-columns:1fr;gap:8px}}'''

files['js/api.js'] = '''const API_BASE = "http://127.0.0.1:5000";
async function apiGet(path){try{const r=await fetch(API_BASE+path);return await r.json()}catch(e){console.error(e);return{code:500,message:e.message}}}
async function apiPost(path,data){try{const r=await fetch(API_BASE+path,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});return await r.json()}catch(e){return{code:500,message:e.message}}}
async function apiDelete(path){try{const r=await fetch(API_BASE+path,{method:"DELETE"});return await r.json()}catch(e){return{code:500,message:e.message}}}'''

files['js/app.js'] = '''let allDevices=[],allLatestData={},historyChart=null;

document.querySelectorAll(".nav-item").forEach(item=>{item.addEventListener("click",function(e){e.preventDefault();const p=this.dataset.page;document.querySelectorAll(".nav-item").forEach(n=>n.classList.remove("active"));this.classList.add("active");document.querySelectorAll(".page").forEach(pg=>pg.classList.remove("active"));document.getElementById(p).classList.add("active");if(p==="history")populateDeviceSelect()})});

function showToast(m,t="success"){const e=document.getElementById("toast");e.textContent=m;e.className="toast "+t;setTimeout(()=>e.classList.add("hidden"),3000)}

async function loadDashboard(){
    const dr=await apiGet("/api/devices");if(dr.code===200)allDevices=dr.data;
    const sr=await apiGet("/api/sensors/all/latest");if(sr.code===200){allLatestData={};sr.data.forEach(d=>allLatestData[d.device_id]=d)}
    renderStats();renderDeviceGrid()
}

function renderStats(){
    const t=allDevices.length,o=allDevices.filter(d=>d.status==="online").length,f=t-o,s=Object.keys(allLatestData).length;
    document.getElementById("statsRow").innerHTML=sc("Total Devices",t,"")+sc("Online",o,"success")+sc("Offline",f,f>0?"danger":"")+sc("Sensors",s,"warning")
}
function sc(l,v,c){return'<div class="stat-card"><div class="stat-label">'+l+'</div><div class="stat-value '+c+'">'+v+'</div></div>'}

function renderDeviceGrid(){
    const g=document.getElementById("deviceGrid");
    if(!allDevices.length){g.innerHTML='<p style="color:var(--text-muted)">No devices registered yet.</p>';return}
    g.innerHTML=allDevices.map(d=>{
        const dt=allLatestData[d.device_id]||{},sc=d.status==="online"?"online":"offline";
        return'<div class="device-card '+sc+'" onclick="showDetail(\''+d.device_id+'\')"><div class="device-card-header"><div class="device-card-name">'+eh(d.name)+'</div><span class="device-status '+sc+'">'+d.status+'</span></div><div class="sensor-values"><div class="sensor-item"><div class="sensor-label">Temp</div><div class="sensor-value temp">'+(dt.temperature!=null?dt.temperature.toFixed(1)+"°C":"--")+'</div></div><div class="sensor-item"><div class="sensor-label">Humid</div><div class="sensor-value humid">'+(dt.humidity!=null?dt.humidity.toFixed(1)+"%":"--")+'</div></div><div class="sensor-item"><div class="sensor-label">Light</div><div class="sensor-value light">'+(dt.light!=null?dt.light.toFixed(0)+" lx":"--")+'</div></div></div></div>'
    }).join("")
}

async function showDetail(id){
    const d=allDevices.find(x=>x.device_id===id);if(!d)return;
    const dt=allLatestData[id]||{};
    const old=document.querySelector(".detail-modal");if(old)old.remove();
    const div=document.createElement("div");
    div.innerHTML='<div class="detail-modal" onclick="if(event.target===this)this.remove()"><div class="detail-content"><div class="detail-header"><h2>'+eh(d.name)+' <span style="color:var(--text-muted);font-size:14px">('+d.device_id+')</span></h2><button class="detail-close" onclick="this.closest(\'.detail-modal\').remove()">&times;</button></div><div class="sensor-values" style="margin-bottom:24px"><div class="sensor-item"><div class="sensor-label">Temperature</div><div class="sensor-value temp" style="font-size:28px">'+(dt.temperature!=null?dt.temperature.toFixed(1)+"°C":"--")+'</div></div><div class="sensor-item"><div class="sensor-label">Humidity</div><div class="sensor-value humid" style="font-size:28px">'+(dt.humidity!=null?dt.humidity.toFixed(1)+"%":"--")+'</div></div><div class="sensor-item"><div class="sensor-label">Light</div><div class="sensor-value light" style="font-size:28px">'+(dt.light!=null?dt.light.toFixed(0)+" lux":"--")+'</div></div></div><div class="control-panel"><h3>Relay Control</h3><div class="relay-row"><div class="relay-info"><div class="relay-indicator '+(d.relay1_state==="on"?"on":"")+'"></div><span>Relay 1 &mdash; <strong>'+(d.relay1_state||"off")+'</strong></span></div><div class="relay-buttons"><button class="btn btn-primary btn-small" onclick="ctrl(\''+d.device_id+"','relay1','on')\">ON</button><button class=\"btn btn-secondary btn-small\" onclick=\"ctrl('"+d.device_id+"','relay1','off')\">OFF</button></div></div><div class=\"relay-row\"><div class=\"relay-info\"><div class=\"relay-indicator "+(d.relay2_state==="on"?"on":"")+'"></div><span>Relay 2 &mdash; <strong>'+(d.relay2_state||"off")+'</strong></span></div><div class="relay-buttons"><button class="btn btn-primary btn-small" onclick="ctrl(\''+d.device_id+"','relay2','on')\">ON</button><button class=\"btn btn-secondary btn-small\" onclick=\"ctrl('"+d.device_id+"','relay2','off')\">OFF</button></div></div></div></div></div>';
    document.body.appendChild(div.firstElementChild)
}

async function ctrl(did,rid,act){
    const r=await apiPost("/api/control/"+did+"/relay/"+rid,{action:act});
    if(r.code===200){showToast(did+" "+rid+" -> "+act);await loadDashboard();showDetail(did)}
    else showToast(r.message||"Failed","error")
}

function renderDeviceList(){
    const l=document.getElementById("deviceList");
    let h='<div class="device-list-item header"><span>ID</span><span>Name</span><span>Description</span><span>Status</span><span>Last Seen</span><span>Actions</span></div>';
    allDevices.forEach(d=>{const sc=d.status==="online"?"online":"offline";h+='<div class="device-list-item"><span style="font-family:JetBrains Mono,monospace;font-size:13px">'+d.device_id+'</span><span>'+eh(d.name)+'</span><span style="color:var(--text-muted)">'+eh(d.description||"-")+'</span><span><span class="device-status '+sc+'">'+d.status+'</span></span><span style="color:var(--text-muted);font-size:12px">'+(d.last_seen||"-")+'</span><span><button class="btn btn-danger btn-small" onclick="delDev(\''+d.device_id+'\')">Delete</button></span></div>'});
    l.innerHTML=h
}

function showAddDevice(){document.getElementById("addDeviceForm").classList.remove("hidden")}
function hideAddDevice(){document.getElementById("addDeviceForm").classList.add("hidden")}

async function addDevice(){
    const id=document.getElementById("newDevId").value.trim(),nm=document.getElementById("newDevName").value.trim(),ds=document.getElementById("newDevDesc").value.trim();
    if(!id||!nm){showToast("ID and Name required","error");return}
    const r=await apiPost("/api/devices",{device_id:id,name:nm,description:ds});
    if(r.code===201){showToast("Registered: "+id);hideAddDevice();document.getElementById("newDevId").value="";document.getElementById("newDevName").value="";document.getElementById("newDevDesc").value="";await loadDashboard();renderDeviceList()}
    else showToast(r.message||"Failed","error")
}

async function delDev(id){
    if(!confirm("Delete "+id+"?"))return;
    const r=await apiDelete("/api/devices/"+id);
    if(r.code===200){showToast("Deleted: "+id);await loadDashboard();renderDeviceList()}
    else showToast(r.message||"Failed","error")
}

function populateDeviceSelect(){document.getElementById("histDevice").innerHTML=allDevices.map(d=>'<option value="'+d.device_id+'">'+d.name+' ('+d.device_id+')</option>').join("")}

async function loadHistory(){
    const did=document.getElementById("histDevice").value,dt=document.getElementById("histType").value,lm=document.getElementById("histLimit").value;
    if(!did){showToast("Select device","error");return}
    const r=await apiGet("/api/sensors/"+did+"/history?limit="+lm);
    if(r.code!==200){showToast("Query failed","error");return}
    const labels=r.data.map(d=>d.timestamp.split(" ")[1]||d.timestamp),values=r.data.map(d=>d[dt]);
    const colors={temperature:"#f87171",humidity:"#60a5fa",light:"#fbbf24"},units={temperature:"°C",humidity:"%",light:" lux"};
    if(historyChart)historyChart.destroy();
    historyChart=new Chart(document.getElementById("historyChart").getContext("2d"),{type:"line",data:{labels:labels.reverse(),datasets:[{label:dt.charAt(0).toUpperCase()+dt.slice(1)+" ("+units[dt]+")",data:values.reverse(),borderColor:colors[dt],backgroundColor:colors[dt]+"22",fill:true,tension:.3,pointRadius:3,pointBackgroundColor:colors[dt]}]},options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{labels:{color:"#94a3b8"}}},scales:{x:{ticks:{color:"#64748b",maxTicksLimit:15},grid:{color:"#1e293b"}},y:{ticks:{color:"#64748b"},grid:{color:"#1e293b"}}}}})
}

function eh(s){return s?s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"):""}

async function init(){await loadDashboard();renderDeviceList();setInterval(async()=>{await loadDashboard();renderDeviceList()},10000)}
init();'''

for fp,ct in files.items():
    full=os.path.join(base,fp)
    os.makedirs(os.path.dirname(full),exist_ok=True)
    with open(full,'w',encoding='utf-8') as f:f.write(ct.lstrip('\n'))
    print("  created:",fp)

print("\nDone!")