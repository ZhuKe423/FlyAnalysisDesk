
function change_date(){
    var time = document.getElementById('set_datetime').value
    var reg = /^[1-9]\d{3}-(0[1-9]|1[0-2])-(0[1-9]|[1-2][0-9]|3[0-1])\s+(20|21|22|23|[0-1]\d):[0-5]\d:[0-5]\d$/;
    var regExp = new RegExp(reg);
    if(!regExp.test(time)){
    　　alert("时间格式不正确,正确格式为: 2014-01-01 12:00:00 ");
    　　return;
    }

    $.ajax({
        url: "/app/Cmd/change_datetime",
        data: {
            datetime: time
        },
        success: function( result ) {
            document.getElementById('cur_datetime').value = ''
            document.getElementById('cur_timestamp').value = ''
        }
    })
}

function update_speed(){
    var speedSelect = document.getElementById('selectSpeed')
    var index = speedSelect.selectedIndex
    var playspeed = parseInt(speedSelect.options[index].value)

    $.ajax({
        url: "/app/Cmd/update_play_speed",
        data: {
            playSpeed: playspeed
        },
        success: function( result ) {
        }
    })
}