function fresh(){
    window.setTimeout(delayFresh,1000);
    function delayFresh(){
        window.parent.location.reload()
    }
}