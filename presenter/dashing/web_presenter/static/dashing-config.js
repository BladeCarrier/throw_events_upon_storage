/* global $, Dashboard */



//--------------------demo 1-------------------------
var demoDashboard1 = new Dashboard("demoDashboard1");

demoDashboard1.addWidget('w0', 'HTMLWidget', {
    getData: function () {
        var self = this;
        var $div = $('<div>');
	var val = $div.load("/static/dashboard1/widget0.html");
        var data = {
            value:val,
        };

        $.extend(self.data, data);
        
    },
    interval: 0
});
demoDashboard1.addWidget('w1', 'HTMLWidget', {
    getData: function () {
        var self = this;
        var $div = $('<div>');
	var val = $div.load("/static/dashboard1/widget1.html");
        var data = {
            value:val,
        };

        $.extend(self.data, data);
        
    },
    interval: 0
});
demoDashboard1.addWidget('w2', 'HTMLWidget', {
    getData: function () {
        var self = this;
        var $div = $('<div>');
	var val = $div.load("/static/dashboard1/widget2.html");
        var data = {
            value:val,
        };

        $.extend(self.data, data);
        
    },
    interval: 0
});
demoDashboard1.addWidget('w3', 'HTMLWidget', {
    getData: function () {
        var self = this;
        var $div = $('<div>');
	var val = $div.load("/static/dashboard1/widget3.html");
        var data = {
            value:val,
        };

        $.extend(self.data, data);
        
    },
    interval: 0
});


//---------------------demo2-----------------------------
/*
var demoDashboard2 = new Dashboard("demoDashboard2");
demoDashboard2.addWidget('w2', 'HTMLWidget', {
    getData: function () {
        var self = this;
        var $div = $('<div>');
	var val = $div.load("/static/dashboard1/widget2.html");
        var data = {
            value:val,
        };

        $.extend(self.data, data);
        
    },
    interval: 0
});
*/
/*
demoDashboard1.addWidget('avgmass', 'HTMLWidget', {
    
    getData: function () {
        var self = this;
        Dashing.utils.get("HistWidget", function(data) {
            $.extend(self.data, data);
        });
    },

    interval: 3000
});
demoDashboard1.addWidget('mlfit', 'HTMLWidget', {
    getData: function () {
        var self = this;
        Dashing.utils.get("MLFitHistWidget", function(data) {
            $.extend(self.data, data);
        });
    },
    interval: 3000
});

*/


/*alt implementation of the hist widget
function getCookie(name) {
  var value = "; " + document.cookie;
  var parts = value.split("; " + name + "=");
  if (parts.length == 2) return parts.pop().split(";").shift();
};
demoDashboard1.addWidget('avgmass', 'HTMLWidget', {
    
    getData: function () {
        
        var self = this;
        $.ajax({
         type: "POST",
         url:"/bokeh_to_html/",
         data: {
           csrfmiddlewaretoken:getCookie("csrftoken"),
           //type: "avgmass",
             },
         success: function(data){
                      $.extend(self.data, data);
         },
         error: function(){
             alert("Error");
         },
       });


         
    },
    interval: 5000
});
*/
/*
demoDashboard1.addWidget('lena', 'HTMLWidget', {
    getData: function () {
        var self = this;
        Dashing.utils.get('LenaWidget', function(data) {
            $.extend(self.data, data);
        });
    },
    interval: 5000
});
*/
