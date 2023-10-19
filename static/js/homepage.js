const state = document.getElementById('signin')
const recommended = document.getElementById('recommended')
const recommended_container = document.getElementById('recommended_container')
const hr_line = document.getElementById('hr_line')
const br_line = document.getElementById('br_line')
console.log(state);
if (state.innerText == 'sign in'){
    recommended.remove();
    recommended_container.remove();
    hr_line.remove();
    br_line.remove();
}
var search_content = document.getElementById("search_holder")
function btn_search(event){
    if(search_content.value == null){
        search_content.value = event.innerText+'; '
        event.style.backgroundColor = "red"
    }else{
        search_content.value = search_content.value+ event.innerText+'; '
        event.style.backgroundColor = "red"
        
    }
    
}

function clear_func(){
    console.log('zheli')
    var suc = document.getElementsByClassName("btn-success")
    var war = document.getElementsByClassName("btn-warning")
    var lig = document.getElementsByClassName("btn-light")
    for (let i =0;i<suc.length;i++){
        
        if (suc[i].style.backgroundColor == "red"){
            console.log("df f a")
            suc[i].style.backgroundColor = "green"
        }
    }
    for (let i =0;i<war.length;i++){
        if (war[i].style.backgroundColor == "red"){
            war[i].style.backgroundColor = "yellow"
        }
    }
    for (let i =0;i<lig.length;i++){
        if (lig[i].style.backgroundColor == "red"){
            lig[i].style.backgroundColor = "rgb(234,234,239)"
        }
    }
    
    
}
