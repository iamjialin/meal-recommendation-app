var sub_btn = document.getElementById("sub_btn")
console.log(sub_btn.innerText)
if (sub_btn.innerText=='unsubscribe'){
    sub_btn.className="btn btn-danger"
}
function subscribe(url) {
    console.log("sfas")
    var data = document.getElementById("username").innerText;  // get username
    console.log(data)
    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(data), // 将data转化为字符串
        contentType: 'application/json; charset=UTF-8', // 指定contentType
        // dataType: "json",  // 注意：这里是指希望服务端返回的数据类型
        success: function (data) { // 返回数据根据结果进行相应的处理
            if(data == "Not logged"){
                console.log("response")
                alert("Please Log in.")
                
            }
            else if (data == "100"){
                var sub_btn = document.getElementById("sub_btn")
                console.log(data)
                alert('Thanks for subcription')
                sub_btn.innerText = "unsubscribe"
                sub_btn.className = "btn btn-danger"
            }else if (data == 'already subscribe'){
                var sub_btn = document.getElementById("sub_btn")
                sub_btn.innerText = "subscribe"
                sub_btn.className = "btn btn-info"
            }
            
        },
        error: function () {
            alert("error")
        }
    });
}