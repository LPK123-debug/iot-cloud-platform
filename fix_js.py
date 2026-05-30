import os

js = r'''let allDevices=[],allLatestData={},historyChart=null;

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
        return'<div class="device-card '+sc+'" onclick="showDetail(\''+d.device_id+'\')">'
            +'<div class="device-card-header">'
            +'<div class="device-card-name">'+eh(d.name)+'</div>'
            +'<span class="device-status '+sc+'">'+d.status+'</span>'
            +'</div>'
            +'<div class="sensor-values">'
            +'<div class="sensor-item"><div class="sensor-label">Temp</div><div class="sensor-value temp">'+(dt.temperature!=null?dt.temperature.toFixed(1)+"\u00B0C":"--")+'</div></div>'
            +'<div class="sensor-item"><div class="sensor-label">Humid</div><div class="sensor-value humid">'+(dt.humidity!=null?dt.humidity.toFixed(1)+"%":"--")+'</div></div>'
            +'<div class="sensor-item"><div class="sensor-label">Light</div><div class="sensor-value light">'+(dt.light!=null?dt.light.toFixed(0)+" lx":"--")+'</div></div>'
            +'</div></div>'
    }).join("")
}

async function showDetail(id){
    const d=allDevices.find(x=>x.device_id===id);if(!d)return;
    const dt=allLatestData[id]||{};
    const old=document.querySelector(".detail-modal");if(old)old.remove();
    const div=document.createElement("div");
    const r1state=d.relay1_state||"off";
    const r2state=d.relay2_state||"off";
    const r1cls=r1state==="on"?"on":"";
    const r2cls=r2state==="on"?"on":"";
    const tempVal=dt.temperature!=null?dt.temperature.toFixed(1)+"\u00B0C":"--";
    const humidVal=dt.humidity!=null?dt.humidity.toFixed(1)+"%":"--";
    const lightVal=dt.light!=null?dt.light.toFixed(0)+" lux":"--";
    div.innerHTML='<div class="detail-modal" onclick="if(event.target===this)this.remove()">'
        +'<div class="detail-content">'
        +'<div class="detail-header">'
        +'<h2>'+eh(d.name)+' <span style="color:var(--text-muted);font-size:14px">('+d.device_id+')</span></h2>'
        +'<button class="detail-close" onclick="this.closest(\'detail-modal\').remove()">&times;</button>'
        +'</div>'
        +'<div class="sensor-values" style="margin-bottom:24px">'
        +'<div class="sensor-item"><div class="sensor-label">Temperature</div><div class="sensor-value temp" style="font-size:28px">'+tempVal+'</div></div>'
        +'<div class="sensor-item"><div class="sensor-label">Humidity</div><div class="sensor-value humid" style="font-size:28px">'+humidVal+'</div></div>'
        +'<div class="sensor-item"><div class="sensor-label">Light</div><div class="sensor-value light" style="font-size:28px">'+lightVal+'</div></div>'
        +'</div>'
        +'<div class="control-panel"><h3>Relay Control</h3>'
        +'<div class="relay-row"><div class="relay-info"><div class="relay-indicator '+r1cls+'"></div><span>Relay 1 &mdash; <strong>'+r1state+'</strong></span></div>'
        +'<div class="relay-buttons"><button class="btn btn-primary btn-small" onclick="ctrl(\''+d.device_id+"','relay1','on')\">ON</button>"
        +'<button class="btn btn-secondary btn-small" onclick="ctrl(\''+d.device_id+"','relay1','off')\">OFF</button></div></div>"
        +'<div class="relay-row"><div class="relay-info"><div class="relay-indicator '+r2cls+'"></div><span>Relay 2 &mdash; <strong>'+r2state+'</strong></span></div>'
        +'<div class="relay-buttons"><button class="btn btn-primary btn-small" onclick="ctrl(\''+d.device_id+"','relay2','on')\">ON</button>"
        +'<button class="btn btn-secondary btn-small" onclick="ctrl(\''+d.device_id+"','relay2','off')\">OFF</button></div></div>"
        +'</div></div></div>';
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
    allDevices.forEach(d=>{
        const sc=d.status==="online"?"online":"offline";
        h+='<div class="device-list-item">'
            +'<span style="font-family:JetBrains Mono,monospace;font-size:13px">'+d.device_id+'</span>'
            +'<span>'+eh(d.name)+'</span>'
            +'<span style="color:var(--text-muted)">'+eh(d.description||"-")+'</span>'
            +'<span><span class="device-status '+sc+'">'+d.status+'</span></span>'
            +'<span style="color:var(--text-muted);font-size:12px">'+(d.last_seen||"-")+'</span>'
            +'<span><button class="btn btn-danger btn-small" onclick="delDev(\''+d.device_id+'\')">Delete</button></span>'
            +'</div>'
    });
    l.innerHTML=h
}

function showAddDevice(){document.getElementById("addDeviceForm").classList.remove("hidden")}
function hideAddDevice(){document.getElementById("addDeviceForm").classList.add("hidden")}

async function addDevice(){
    const id=document.getElementById("newDevId").value.trim(),
          nm=document.getElementById("newDevName").value.trim(),
          ds=document.getElementById("newDevDesc").value.trim();
    if(!id||!nm){showToast("ID and Name required","error");return}
    const r=await apiPost("/api/devices",{device_id:id,name:nm,description:ds});
    if(r.code===201){
        showToast("Registered: "+id);hideAddDevice();
        document.getElementById("newDevId").value="";
        document.getElementById("newDevName").value="";
        document.getElementById("newDevDesc").value="";
        await loadDashboard();renderDeviceList()
    }else showToast(r.message||"Failed","error")
}

async function delDev(id){
    if(!confirm("Delete "+id+"?"))return;
    const r=await apiDelete("/api/devices/"+id);
    if(r.code===200){showToast("Deleted: "+id);await loadDashboard();renderDeviceList()}
    else showToast(r.message||"Failed","error")
}

function populateDeviceSelect(){
    document.getElementById("histDevice").innerHTML=
        allDevices.map(d=>'<option value="'+d.device_id+'">'+eh(d.name)+' ('+d.device_id+')</option>').join("")
}

async function loadHistory(){
    const did=document.getElementById("histDevice").value,
          dt=document.getElementById("histType").value,
          lm=document.getElementById("histLimit").value;
    if(!did){showToast("Select device","error");return}
    const r=await apiGet("/api/sensors/"+did+"/history?limit="+lm);
    if(r.code!==200){showToast("Query failed","error");return}
    const labels=r.data.map(d=>d.timestamp.split(" ")[1]||d.timestamp).reverse();
    const values=r.data.map(d=>d[dt]).reverse();
    const colors={temperature:"#f87171",humidity:"#60a5fa",light:"#fbbf24"};
    const units={temperature:"\u00B0C",humidity:"%",light:" lux"};
    if(historyChart)historyChart.destroy();
    historyChart=new Chart(document.getElementById("historyChart").getContext("2d"),{
        type:"line",
        data:{labels:labels,datasets:[{
            label:dt.charAt(0).toUpperCase()+dt.slice(1)+" ("+units[dt]+")",
            data:values,borderColor:colors[dt],backgroundColor:colors[dt]+"22",
            fill:true,tension:0.3,pointRadius:3,pointBackgroundColor:colors[dt]
        }]},
        options:{responsive:true,maintainAspectRatio:false,
            plugins:{legend:{labels:{color:"#94a3b8"}}},
            scales:{
                x:{ticks:{color:"#64748b",maxTicksLimit:15},grid:{color:"#1e293b"}},
                y:{ticks:{color:"#64748b"},grid:{color:"#1e293b"}}
            }
        }
    })
}

function eh(s){return s?s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"):""}

async function init(){await loadDashboard();renderDeviceList();setInterval(async()=>{await loadDashboard();renderDeviceList()},10000)}
init();
'''

dst = r"C:\iot-cloud-platform\server\static\js\app.js"
os.makedirs(os.path.dirname(dst), exist_ok=True)
with open(dst, "w", encoding="utf-8") as f:
    f.write(js)

web_dst = r"C:\iot-cloud-platform\web\js\app.js"
with open(web_dst, "w", encoding="utf-8") as f:
    f.write(js)

print("app.js fixed")