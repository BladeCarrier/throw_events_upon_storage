/* global $, Dashing, rivets */

Dashing.widgets.HTMLWidget = function(dashboard) {
    var self = this;
    self.__init__ = Dashing.utils.widgetInit(dashboard, 'htmlwidget');
    self.row = 2;
    self.col = 2;
    self.inited=false;
    self.color = '#fffffa';
    self.scope = {};
    self.getWidget = function () {
        return this.__widget__;
    };
    self.getData = function () {
       
    };
    self.interval = 0;
};

rivets.binders['dashing-htmlwidget'] = function binder(el, data) {
    if (!data) return;
        
    var activeDiv = el.childNodes.item(1);
    var passiveDiv = el.childNodes.item(3);
    if (activeDiv.style.display =="none"){
        activeDiv = el.childNodes.item(3);
        passiveDiv = el.childNodes.item(1);
    }
    
    $(passiveDiv).html(data);

    switchdivs = function(){
        passiveDiv.style.display="inline";
        activeDiv.style.display="none";
        activeDiv.childNodes.lengths=0;
        $(activeDiv).html("None");
    };
    setTimeout(switchdivs, 200);
    
    
};
