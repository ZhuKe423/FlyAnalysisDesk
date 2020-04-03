var airplanes = {}
var selectedOneAirPlane = false
var selectedCallSign = ''
var current_time = 0
var show_airplane_label = true
var only_show_selected_airplane = false
var selectedAirPlanes = []
var is_stopped = 0

function start_play(){
    console.log("start_play:" +is_stopped)
    if (is_stopped == 1){
        document.getElementById('startPlay').value = 'Playing'
        is_stopped = 0
    }else{
        document.getElementById('startPlay').value = 'Stopped'
        is_stopped = 1
    }
    $.ajax({
        url: "/app/Cmd/update_stop_state",
        data: {
            stop: is_stopped
        },
        success: function( result ) {
            console.log("update_stop_state: "+ is_stopped)
        }
    })
}


function conver_GPS_toBDformat(x,y)
{
    let point = wgs84togcj02(x,y);
    // point = gcj02tobd09(point[0],point[1]);
    point = [x,y]
    return new BMap.Point(point[0],point[1]);
}

function change_planelabel(){
    let isEnable = document.getElementById('showPlaneLabel').checked
    console.log("change_planelabel:"+isEnable)
    show_airplane_label = isEnable
}

function filter_plane(){
    let isEnable = document.getElementById('filterUnselectedPlane').checked
    console.log("filterUnselectedPlane:"+isEnable)
    only_show_selected_airplane = isEnable
}

function get_airplane_radar()
{
    $.ajax({
        url: "/app/Radar/get",
        data: {
            code: 1
        },
        success: function( result ) {
            // console.log(result['data'])
            for(let i = 0; i < result['data'].length; i++)
            {
                let radar = result['data'][i]
                let callSign = radar['callsign']
                let tmpData = {}

                if (callSign in airplanes) {
                    if (airplanes[callSign]['marker'] != null){
                        map.removeOverlay(airplanes[callSign]['marker']);
                    }
                    airplanes[callSign] = null;
                }
                tmpData['point'] = conver_GPS_toBDformat(parseFloat(radar['longitude']), parseFloat(radar['latitude']))
                tmpData['timestamp'] = radar['utctime']
                current_time = radar['utctime']
                tmpData['callsign'] = callSign
                tmpData['marker'] = null

                let planeIcon = new BMap.Icon("/static/images/airplane.png",new BMap.Size(24, 24),{anchor: new BMap.Size(24, 24)});
                let label = new BMap.Label(radar["callsign"],{offset:new BMap.Size(20,-10)});
                let marker = new BMap.Marker(tmpData['point'],{icon: planeIcon});
                if (show_airplane_label || (selectedAirPlanes.indexOf(callSign) > -1)){
                    marker.setLabel(label);
                }
                if (!only_show_selected_airplane || (selectedAirPlanes.indexOf(callSign) > -1)){
                    map.addOverlay(marker);
                    tmpData['marker'] = marker;
                    label.addEventListener("onclick", function(e){
                        console.log(e.currentTarget.content)
                        document.getElementById('selected_airplane').value = e.currentTarget.content
                        selectedOneAirPlane = true
                        selectedCallSign = e.currentTarget.content
                        // console.log(selectedCallSign)
                    })
                }
                airplanes[callSign] = tmpData
            }
            console.log("update airplane at " + current_time)
            clear_arrived_airplanes()
        }
    });
}

function clear_arrived_airplanes(){
    for(let plane in airplanes) {
        let delta = current_time - airplanes[plane]['timestamp']
        if (Math.abs(delta) > 40)
        {
            // console.log("clear_arrived_airplanes remove: " + plane)
            map.removeOverlay(airplanes[plane]['marker']);
            delete airplanes[plane];
        }
    }
    document.getElementById('cur_datetime').value = timestamp2str(current_time)
    document.getElementById('cur_timestamp').value = current_time
}

function update_airplane_position_radar(map){
    get_airplane_radar()
}

function airplane_update_timer(map){
    // setInterval("update_airplane_position(map)",2000);
    setInterval("update_airplane_position_radar(map)",4000);
}

function show_select_table(){
    var html = ''
    for(let i = 0; i < selectedAirPlanes.length; i++){
        let plane = selectedAirPlanes[i]
        html += "<tr><td>"+plane+"</td><td>"
        html += '<input type="button" onclick="cancel_airplane_selected('+"'"+plane+"'"+')" value="删除"/>'
        html += '<input id="showRadarMarker_'+plane+'" type="checkbox" value="" onchange="show_radar_marker('+"'"+plane+"'"+')" checked/>'
        html += '</td></tr>'
    }
    // console.log(html)
    document.getElementById('AirPlaneTable').getElementsByTagName("tbody")[0].innerHTML = html
}

var selected_plane_flyplan = {}
var selected_plane_radars = {}
var last_a_lat = 0
var radar_marker_names = {}
var radar_markers = {}

function cancel_airplane_selected(plane){
    console.log("cancel_airplane_selected"+plane)
    let index = selectedAirPlanes.indexOf(plane)
    if (index > -1){
        selectedAirPlanes.splice(index)
    }
    show_select_table()
    clear_the_line(plane+'_radar')
    clear_the_line(plane+'_flyplan')
    clear_the_markers(radar_marker_names[plane])
    radar_marker_names[plane] = []
    selected_plane_flyplan[plane] = []
    selected_plane_radars[plane] = []
}

function add_selected_air_plane(){
    var plane = document.getElementById('selected_airplane').value
    console.log("add_selected_air_plane:" + plane)
    if ((plane == '') || (selectedAirPlanes.indexOf(plane) > 0)){
        return
    }
    selectedAirPlanes.push(plane)
    show_select_table()
    show_selected_flyplan(plane)
}

function show_selected_flyplan(plane){
    $.ajax({
        url: "/app/FlyPlan/get_plane_flyplan",
        data: {
            airplane: plane,
            current: current_time,
        },
        success: function( result ) {
            let flyplan = result['data']
            show_selected_plane_radar(plane, flyplan['ATIME']-90*60, flyplan['ATIME'])
            var fp = JSON.parse(flyplan['RTEPTS']);
            let route = []
            for(let i = 0; i < fp.length; i++){
                let item = fp[i]
                var found = false
                for( let j=0; j < fixpoints.length; j++){
                    if(item['PTID'] == fixpoints[j]['poncode']){
                        route.push(fixpoints[j]['point'])
                        found = true
                        break
                    }
                }
                if (found == false){
                    // 3018N10928E
                    if ((item['PTID'][4] == 'N') && (item['PTID'].match(/(\d+)N(\d+)E/) != null)){
                         y = gradetranform(item['PTID'].substr(0,2),item['PTID'].substr(2,2),'00')
                         x = gradetranform(item['PTID'].substr(5,3),item['PTID'].substr(8,2),'00')
                         route.push(conver_GPS_toBDformat(x, y))
                         console.log("find the new point: "+item['PTID'])
                    }else if((item['PTID'][0] == 'N') && (item['PTID'].match(/N(\d+)E(\d+)/) != null)){ // N3022E10930
                         console.log(item['PTID'].substr(1,2)+" "+item['PTID'].substr(3,2))
                         console.log(item['PTID'].substr(6,3)+" "+item['PTID'].substr(9,2))
                         y = gradetranform(item['PTID'].substr(1,2),item['PTID'].substr(3,2),'00')
                         x = gradetranform(item['PTID'].substr(6,3),item['PTID'].substr(9,2),'00')
                         route.push(conver_GPS_toBDformat(x, y))
                         console.log("find the new point: "+item['PTID'])
                    }else{
                        console.log("can't find the fixpoint: "+item['PTID'])
                    }
                }
            }
            selected_plane_flyplan[plane] = route
            draw_select_plane(plane, route, 'flyplan')
        }
    })
}


function create_radar_marker(plane, radar, name, labelStr){
        let Point = conver_GCJ_toBDformat(parseFloat(radar['longitude']),parseFloat(radar['latitude']))
        let tmpData = {}
        tmpData['name'] = name
        tmpData['label'] = labelStr
        tmpData['point'] = Point
        radar_markers[plane].push(tmpData)
}

function show_radar_marker(plane){

    let isEnable = document.getElementById('showRadarMarker_'+plane).checked
    console.log("show_radar_marker:"+isEnable)
    if (isEnable){
        draw_radar_markers(radar_markers[plane])
    }else{
        clear_the_markers(radar_marker_names[plane])
    }
}

function draw_radar_markers(markers){
    console.log("draw_radar_markers:")
    console.log(markers)
    for(let i = 0; i < markers.length; i++){
        let data = markers[i]
        let radarIcon = new BMap.Icon("/static/images/point.png",new BMap.Size(24, 24),{anchor: new BMap.Size(24, 24)});
        let label = new BMap.Label(data['label'],{offset:new BMap.Size(20,-10)});
        let marker = new BMap.Marker(data['point'],{icon: radarIcon});
        marker.setLabel(label);
        marker.name = data['name']
        map.addOverlay(marker);
    }
}

function show_selected_plane_radar(plane, start, end){
    $.ajax({
        url: "/app/Radar/get_plane_radar",
        data: {
            airplane: plane,
            start: start,
            end: end
        },
        success: function( result ) {
            var route = []
            last_a_lat = 0
            console.log(result['data'])
            radar_markers[plane] = []
            radar_marker_names[plane] = []
            for (let i in result['data']){
                let item = result['data'][i]
                let Point = conver_GCJ_toBDformat(parseFloat(item['longitude']),parseFloat(item['latitude']))
                route.push(Point)
                if ((last_a_lat != item['A_altitude']) ){
                    let str = item['C_altitude']+',A'+item['A_altitude']+',S'+parseInt(item['speed'])
                    last_a_lat = item['A_altitude']
                    let name = plane+"_"+item['RDID']
                    create_radar_marker(plane,item,name,str)
                    radar_marker_names[plane].push(name)
                }
            }
            draw_radar_markers(radar_markers[plane])
            selected_plane_radars[plane] = route
            // console.log(route)
            draw_select_plane(plane, route, 'radar')
        }
    })
}

function draw_select_plane(plane, route, type){
    var colors = ['orange','yellow','green','white','gray','skyblue','limegreen']
    var color = colors[selectedAirPlanes.indexOf(plane)]
    var polyline = new BMap.Polyline(route,
        {strokeColor:color, strokeWeight:3, strokeOpacity:0.5}
    );
    polyline.name = plane + '_' + type
    map.addOverlay(polyline);
    console.log("draw "+plane+" line "+type)
}

function clear_the_line(line_name){
    var allOverlay = map.getOverlays();
    allOverlay.map(item => {
        if(item.name === line_name){
            map.removeOverlay(item)
        }
    })
}

function clear_the_markers(markers){
    console.log("clear_the_markers:")
    var allOverlay = map.getOverlays();
    allOverlay.map(item => {
        if(markers.indexOf(item.name) != -1){
            map.removeOverlay(item)
        }
    })
}