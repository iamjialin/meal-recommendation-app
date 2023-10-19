var star1 = document.getElementById("star1")
var star2 = document.getElementById("star2")
var star3 = document.getElementById("star3")
var star4 = document.getElementById("star4")
var star5 = document.getElementById("star5")

star1.onmouseover = function(){
    star1.src = "/static/dirtyimg/starred.png"
    star2.src = "/static/dirtyimg/unstarred.png"
    star3.src = "/static/dirtyimg/unstarred.png"
    star4.src = "/static/dirtyimg/unstarred.png"
    star5.src = "/static/dirtyimg/unstarred.png"
}

star2.onmouseover = function(){
    star1.src = "/static/dirtyimg/starred.png"
    star2.src = "/static/dirtyimg/starred.png"
    star3.src = "/static/dirtyimg/unstarred.png"
    star4.src = "/static/dirtyimg/unstarred.png"
    star5.src = "/static/dirtyimg/unstarred.png"
}

star3.onmouseover = function(){
    star1.src = "/static/dirtyimg/starred.png"
    star2.src = "/static/dirtyimg/starred.png"
    star3.src = "/static/dirtyimg/starred.png"
    star4.src = "/static/dirtyimg/unstarred.png"
    star5.src = "/static/dirtyimg/unstarred.png"
}

star4.onmouseover = function(){
    star1.src = "/static/dirtyimg/starred.png"
    star2.src = "/static/dirtyimg/starred.png"
    star3.src = "/static/dirtyimg/starred.png"
    star4.src = "/static/dirtyimg/starred.png"
    star5.src = "/static/dirtyimg/unstarred.png"
}

star5.onmouseover = function(){
    star1.src = "/static/dirtyimg/starred.png"
    star2.src = "/static/dirtyimg/starred.png"
    star3.src = "/static/dirtyimg/starred.png"
    star4.src = "/static/dirtyimg/starred.png"
    star5.src = "/static/dirtyimg/starred.png"
}





const like_img = document.getElementById("like_img")
function POSTInWebRefresh(url) {
    console.log("jinlaile")
    var data = document.getElementById("Recipe_name").innerText;  // 将id=form的表单数据序列化
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
            else if (data != "Existed"){
                var like = document.getElementById("like_btn")
                console.log(data)
                like.innerText = data
                like_img.src = "/static/dirtyimg/liked.png"
            }else{
                var like = document.getElementById("like_btn")
                console.log(data)
                like.innerText = parseInt(like.innerText)-1
                like_img.src = "/static/dirtyimg/unliked.png"
            }
            
        },
        error: function () {
            var like = document.getElementById("like_btn")
            like.innerText = 'false'
        }
    });
}


function send_rate(url, event){
    console.log("jinlaile")
    var data = event.id;  // 将id=form的表单数据序列化
    data = data.charAt(4)
    var recipe_name = document.getElementById("Recipe_name").innerText; 
    console.log(data)
    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(data+recipe_name), // 将data转化为字符串
        contentType: 'application/json; charset=UTF-8', // 指定contentType
        // dataType: "json",  // 注意：这里是指希望服务端返回的数据类型
        success: function (data) { // 返回数据根据结果进行相应的处理
            if(data == "Rated"){
                alert("Sorry, you cannot rate again!")
            }else if(data == "Not logged"){
                alert("Please log in first.")
            }else{
                alert("Thank for your rating!")
                var rate = document.getElementById("rate")
                var new_rating = parseFloat(data)
                var star_btn_1 = document.getElementById('star_fix_' + String(Math.round(new_rating)))
                if (Math.round(new_rating) < 5){
                    var star_btn_2 = document.getElementById('star_fix_' + String(Math.round(new_rating)+1))
                    star_btn_2.src = "/static/dirtyimg/unstarred.png" 
                }
                star_btn_1.src = "/static/dirtyimg/starred.png"    // 根据新rating修改star图片
                rate.innerText = new_rating.toFixed(2);
                window.location.reload()
            }
            
        },
        error: function () {
            alert("error")
        }
    });

}



function comment_submit(url){
    console.log("jinlaile")
    var data = document.getElementById("comment").value
    var recipe_name = document.getElementById("Recipe_name").innerText;
    console.log({'recipe_name':recipe_name,'comment':data})
    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify({'recipe_name':recipe_name,'comment':data}), // 将data转化为字符串
        contentType: 'application/json; charset=UTF-8', // 指定contentType
        // dataType: "json",  // 注意：这里是指希望服务端返回的数据类型
        success: function (data) { // 返回数据根据结果进行相应的处理
            if(data == "success"){
                location.reload();
                alert("Comment posted.")
                
            }else if(data == "Not logged"){
                alert("Please log in first.")
            }
            
        },
        error: function () {
            alert("error")
        }
    });

}


function add_week(url){
    var recipe_name = document.getElementById("Recipe_name").innerText;
    $.ajax({
        type: "POST",
        url: url,
        data: JSON.stringify(recipe_name), // 将data转化为字符串
        contentType: 'application/json; charset=UTF-8', // 指定contentType
        // dataType: "json",  // 注意：这里是指希望服务端返回的数据类型
        success: function (data) { // 返回数据根据结果进行相应的处理
            if(data == "100"){
                var add_btn = document.getElementById("add_btn")
                add_btn.innerText = "Added"
                alert("Already add to your weekly recipe!")
            }else if(data =="Not logged"){
                alert("Please Log in first")
            }else if(data == "already exist"){
                alert('already exist')
            }
        },
        error: function () {
            alert("error")
        }
    });

}
