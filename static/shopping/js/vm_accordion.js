var WWAccordion = {};
dojo.require("dijit._base.sniff");

dojo.declare("WWAccordion", null, {
	constructor: function(args) {
	 this.interval = 1000;
	 this.mode = 'onclick';
	 dojo.mixin(this,args);
	 this.enabled = true;
	 this.init();
	},
	
	init: function(){
	  this.opened = -1;
    this.dts = dojo.query('dt.parent.level'+this.level, this.node);
	  this.dds = dojo.query('dd.parent.level'+this.level, this.node);
    this.dts.forEach(function(el, i){
      el.i = i;
      if(dojo.style(this.dds[i], 'height') > 0){
        this.opened = i;
      }
      dojo.connect(el, this.mode, dojo.hitch(this,'onOpenOrClose'));
      new WWAccordion({node : this.dds[i], level : this.level+1, mode: this.mode, interval : this.interval});
    },this);
  },
  
  onOpenOrClose: function(e){
    var el = e.currentTarget;
    if(this.mode == "onmouseenter" && dojo.hasClass(el, 'close')) return;
    
    var h = dojo.style(this.dds[el.i], 'height');
    if(h == 0){
      if(this.opened >= 0 && this.opened != el.i){     
        if(this.dds[this.opened].wwanim && this.dds[this.opened].wwanim.status() == "playing"){
          this.dds[this.opened].wwanim.stop();
        }
        this.dds[this.opened].wwanim = dojo.animateProperty({node: this.dds[this.opened], properties: {height: 0}, duration: this.interval, onEnd: dojo.hitch(this,'onCloseEnd')}).play();
        dojo.removeClass(this.dts[this.opened],'open');
      }
      dojo.style(this.dds[el.i], 'display', 'block');
      if(this.dds[el.i].wwanim && this.dds[el.i].wwanim.status() == "playing"){
        this.dds[el.i].wwanim.stop();
      }
      
      this.dds[el.i].wwanim = dojo.animateProperty({node: this.dds[el.i], properties: {height: dojo.style(dojo.query('dl.level'+(this.level+1), this.dds[el.i])[0], 'height')}, duration: this.interval, onEnd: dojo.hitch(this,'onOpenEnd')}).play();
      dojo.addClass(this.dts[el.i],'open');
      this.opened = el.i;
    }else{
      if(this.dds[el.i].wwanim && this.dds[el.i].wwanim.status() == "playing"){
        this.dds[el.i].wwanim.stop();
      }
      this.dds[el.i].wwanim = dojo.animateProperty({node: this.dds[el.i], properties: {height: 0}, duration: this.interval, onEnd: dojo.hitch(this,'onCloseEnd')}).play();
      dojo.removeClass(this.dts[el.i],'open');
    }
  },
  
  onOpenEnd: function(el){
    dojo.style(el, 'height', '100%');
  },
  
  onCloseEnd: function(el){
    dojo.style(el, 'display', 'none');
  }
  
});