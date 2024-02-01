

Magnifier = function(){

    function getCursorPos(e) {
    
        var a, x = 0, y = 0;
        e = e || window.event;
        /* Get the x and y positions of the image: */
        // a = this.targetImg.getBoundingClientRect();
        a = glassModule.targetImg.getBoundingClientRect();
        /* Calculate the cursor's x and y coordinates, relative to the image: */
        x = e.pageX - a.left;
        y = e.pageY - a.top;
        /* Consider any page scrolling: */
        x = x - window.pageXOffset;
        y = y - window.pageYOffset;
        return {x : x, y : y};
    }

    function moveMagnifier(e) {
        var pos, x, y;
        /* Prevent any other actions that may occur when moving over the image */
        e.preventDefault();
        /* Get the cursor's x and y positions: */
        pos = getCursorPos(e);
        x = pos.x;
        y = pos.y;
        /* Prevent the magnifier glass from being positioned outside the image: */
        if (x > glassModule.targetImg.width - (glassModule.w / glassModule.zoom)) {x = glassModule.targetImg.width - (glassModule.w / glassModule.zoom);}
        if (x < glassModule.w / glassModule.zoom) {x = glassModule.w / glassModule.zoom;}
        if (y > glassModule.targetImg.height - (glassModule.h / glassModule.zoom)) {y = glassModule.targetImg.height - (glassModule.h / glassModule.zoom);}
        if (y < glassModule.h / glassModule.zoom) {y = glassModule.h / glassModule.zoom;}
        /* Set the position of the magnifier glass: */
        glassModule.glass.style.left = (x - glassModule.w) + "px";
        glassModule.glass.style.top = (y - glassModule.h) + "px";
        /* Display what the magnifier glass "sees": */
        glassModule.glass.style.backgroundPosition = "-" + ((x * glassModule.zoom) - glassModule.w + glassModule.bw) + "px -" + ((y * glassModule.zoom) - glassModule.h + glassModule.bw) + "px";
    }

    glassModule = {
        glass: null,
        img: null,
        targetImg:null,
        zoom: 3,
        w: 0,
        h: 0,
        bw: 3,
        isShow: true,
        init: function (targetImgId, zoom) {
    
            this.zoom = zoom;
            this.targetImgId = targetImgId;
            this.targetImg = document.getElementById(targetImgId);
    
            /* create style */
            // var style = document.createElement('style');
            // style.type = 'text/css';
            var style = 'z-index:100; position: absolute; border: 3px solid #000; cursor: none; width: 400px;height: 400px; background-repeat: no-repeat; background-size: ' + (this.targetImg.width * this.zoom) + 'px ' + (this.targetImg.height * this.zoom) + 'px;';
            // document.getElementsByTagName('head')[0].appendChild(style);
    
            /* create glass */
            this.glass = document.createElement("DIV");
            this.glass.setAttribute("id", "img-magnifier-glass");
            this.glass.setAttribute("class", "img-magnifier-glass");
            this.glass.setAttribute("style", style);
    
            this.targetImg.parentElement.insertBefore(this.glass, this.targetImg);
            this.w = this.glass.offsetWidth * 0.5;
            this.h = this.glass.offsetHeight * 0.5;
          
            /* Execute a function when someone moves the magnifier glass over the image: */
            this.glass.addEventListener("mousemove", moveMagnifier);
            this.targetImg.addEventListener("mousemove", moveMagnifier);
          
            /*and also for touch screens:*/
            this.glass.addEventListener("touchmove", moveMagnifier);
            this.targetImg.addEventListener("touchmove", moveMagnifier);
        },
        show: function(){
            if(this.isShow)return;
            this.glass.style.display = "block";
            this.isShow = true;
        },
        hide: function(){
            if(this.isShow){
                this.glass.style.display = "none";
                this.isShow = false;
                this.resetImg();
            }
        },
        switch: function(){
            if(this.isShow){
                this.hide();
            }else{
                this.show();
            }
        },
        resetImg: function(){
            this.glass.style.backgroundImage = "url('" + this.targetImg.src + "')";
        }
    }
    return glassModule;        
}


