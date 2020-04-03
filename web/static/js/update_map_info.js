var starpoint = []
var fixpoints = []
var starinfo = []
var routePointArr = []
var routPolyline = []


function intial_enviroment(map){
		get_starinfo();
		get_starpoints();
		get_fixpoints(map);
}

function get_starinfo(){
    //console.log("click get fix points button!");
    $.ajax({
        url: "/app/Map/get_star_info",
        data: {
            code: 1
        },
        success: function( result ) {
            for(let i = 0; i < result['data'].length; i ++)
            {
                starinfo.push(result['data'][i])
            }
            console.log(starinfo)
        }
    });
}

function get_starpoints(map)
{
    //console.log("click get fix points button!");
    $.ajax({
        url: "/app/Map/get_star_point",
        data: {
            code: 1
        },
        success: function( result ) {
            console.log("get_starpoints:")
            console.log(result['data'])
            for(let i = 0; i < result['data'].length; i ++)
            {
                starpoint.push(result['data'][i])
            }
        }
    });
}

function is_star_point(poncode)
{
    for(let i = 0; i < starpoint.length; i++){
        if( poncode == starpoint[i])
        return true;
    }
    return false;
}

function conver_GCJ_toBDformat(x,y)
{
    let point = gcj02tobd09(x,y);
    return new BMap.Point(point[0],point[1]);
}

function get_fixpoints(map){
    $.ajax({
        url: "/app/Map/get_fix_point",
        data: {
            code: 1
        },
        success: function( result ) {
            console.log(result['data'])
            for(let i = 0; i < result['data'].length ; i ++)
			{
			    let item = result['data'][i]
			    let ggPoint = conver_GCJ_toBDformat(item['longV'],item['latV'])
			    var key_fixpoint = ['UU617','UU616','UU615','UU614','UU613','UU612']
			    tmpData = {
				 				"point": ggPoint,
				 				"label": item['poncode'],
				 				"star": is_star_point(item['poncode']),
				 				"poncode": item['poncode']
				 			};
				/*
                if (tmpData['star'] == false){
                    console.log("show key fix points!!")
                    tmpData['star'] = (key_fixpoint.indexOf(item['poncode']) > -1)?true:false
                }
                */
                fixpoints.push(tmpData)
			}
			update_fixpoints_onmap(map, fixpoints);
        }
    })
}

function update_fixpoints_onmap(map, gpoints)
{
    setTimeout(function(){
        for (var index = 0; index < gpoints.length; index++){
            if(gpoints[index]['star'] == true){
                myIcon = new BMap.Icon("/static/images/starpoint2.png",new BMap.Size(24, 24),{anchor: new BMap.Size(12, 24)});
            }else{
                myIcon = new BMap.Icon("/static/images/fixpoint3.png",new BMap.Size(24, 24),{anchor: new BMap.Size(12, 24)});
                let label = new BMap.Label(gpoints[index]['label'],{offset:new BMap.Size(20,-10)});
            }
            let marker = new BMap.Marker(gpoints[index]['point'],{icon: myIcon});
            if(gpoints[index]['star'] == true){
                let label = new BMap.Label(gpoints[index]['label'],{offset:new BMap.Size(20,-10)});
                marker.setLabel(label); //添加百度label
                map.addOverlay(marker);
            }

        }
        update_starroute(map);
        // get_radar();
    }, 2000);
}

function update_starroute(map)
{
    console.log("update_starroute:")
    console.log(starinfo)
    for(let index = 0; index < starinfo.length; index++){
        let route = []
        points = JSON.parse(starinfo[index]['POINTS'])
        for (let i = 0; i < points.length; i++){
            for(let j = 0; j < fixpoints.length; j++){
                if(points[i] == fixpoints[j]['poncode']){
                    route.push(fixpoints[j]['point'])
                }
            }
        }
        routePointArr.push(route)
    }

    console.log(routePointArr)
    for(let i = 0; i < routePointArr.length; i++){
        var polyline = new BMap.Polyline(
            routePointArr[i],
            {strokeColor:"blue", strokeWeight:1, strokeOpacity:0.5}
        );

        routPolyline.push(polyline);
        map.addOverlay(polyline);
    }
    console.log(routPolyline)
}

function change_starroute(){
    let isEnable = document.getElementById('showStarRoute').checked
    if(isEnable){
        console.log('change_starroute: ' + isEnable)
        for(let i = 0; i < routePointArr.length; i++){
            var polyline = new BMap.Polyline(
                routePointArr[i],
                {strokeColor:"blue", strokeWeight:2, strokeOpacity:0.5}
            );
            map.addOverlay(polyline);
        }
    }else{
        console.log('change_starroute: ' + isEnable)
        map.clearOverlays();
        airplane_marker = {}
        show_fixpoints();
    }
}

function show_fixpoints()
{
    var gpoints = fixpoints;
    for (var index = 0; index < gpoints.length; index++){
        if(gpoints[index]['star'] == true){
            myIcon = new BMap.Icon("/static/images/starpoint2.png",new BMap.Size(24, 24),{anchor: new BMap.Size(12, 24)});
        }else{
            myIcon = new BMap.Icon("/static/images/fixpoint3.png",new BMap.Size(24, 24),{anchor: new BMap.Size(12, 24)});
            let label = new BMap.Label(gpoints[index]['label'],{offset:new BMap.Size(20,-10)});
        }
        let marker = new BMap.Marker(gpoints[index]['point'],{icon: myIcon});
        if(gpoints[index]['star'] == true){
            let label = new BMap.Label(gpoints[index]['label'],{offset:new BMap.Size(20,-10)});
            marker.setLabel(label); //添加百度label
        }
        map.addOverlay(marker);
    }
}