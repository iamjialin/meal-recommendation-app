function del_func(url,event){
    var data = event.value
    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(data), // 将data转化为字符串
        contentType: 'application/json; charset=UTF-8', // 指定contentType
        // dataType: "json",  // 注意：这里是指希望服务端返回的数据类型
        success: function (data) { // 返回数据根据结果进行相应的处理
            alert("successfully deleted!")
            window.location.reload()
        },
        error: function () {
            alert("error")
        }
    });

}



// function search(url){
//     var data = document.getElementById(searchname).innerText
//     $.ajax({
//         type: "POST",
//         url: url,
//         data: JSON.stringify(data), // 将data转化为字符串
//         contentType: 'application/json; charset=UTF-8', // 指定contentType
//         // dataType: "json",  // 注意：这里是指希望服务端返回的数据类型
//         success: function (data) { // 返回数据根据结果进行相应的处理
//             alert("successfully deleted!")
//             window.location.reload()
//         },
//         error: function () {
//             alert("error")
//         }
//     });

// }


