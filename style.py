css = u'''
body {
    margin: 0px 10px;
}

body, td, th, div {
    font-family: Calibri, "Segoe UI", "Trebuchet MS", "Verdana";
}

h2.generation-date,
h1.main-title {
    color: #333333;
}

td.test-subpage,
body {
    background:  #f8f8f8 no-repeat fixed;
    background: -moz-linear-gradient(-90deg,#ffffff,#dddddd) #f8f8f8 no-repeat fixed;
    background: -webkit-gradient(linear, left top, left bottom, from(#ffffff), to(#dddddd)) #f8f8f8 no-repeat fixed;
    filter: progid:DXImageTransform.Microsoft.Gradient( StartColorStr='#ffffff', EndColorStr='#dddddd', GradientType=0);
    background: linear-gradient(-90deg,#ffffff,#dddddd) #f8f8f8 no-repeat fixed;
    
}
.panel {
    color: #ffffcc;
    background: #223322 no-repeat fixed;
    background: -moz-linear-gradient(-90deg,#333333,#223322) #223322 no-repeat fixed;
    background: -webkit-gradient(linear, left top, left bottom, from(#333333), to(#223322)) #223322 no-repeat fixed;
    filter: progid:DXImageTransform.Microsoft.Gradient( StartColorStr='#333333', EndColorStr='#223322', GradientType=0);
    background: linear-gradient(-90deg,#333333,#223322) #223322 no-repeat fixed;
    padding: 1px 20px;
    -moz-border-radius : 15px;
         border-radius : 15px;
}
.panel h1, .panel h2, .panel h3 {
    color: #dddd55;
    text-decoration: underline;
}

table {
    border-spacing: 0px;
}
.conf_specificationList > tr > td,
.conf_specificationList > tr > th,
.conf_specificationList > tbody > tr > td,
.conf_specificationList > tbody > tr > th,
.table-wrap td,
.table-wrap th {
    padding: 5px;
    margin: 0px;
    background-color: #ffffff;
}
.conf_specificationList > tbody > tr > td,
.conf_specificationList > tbody > tr > th,
.conf_specificationList > tr > td,
.conf_specificationList > tr > th,
.table-wrap td,
.table-wrap th {
    padding: 5px;
    margin: 0px;
    border-style: solid;
    border-color: #999;
    border-left-width: 1px;
    border-right-width: 0px;
    border-top-width: 1px;
    border-bottom-width: 0px;
    background-color: #ffffff;
}

.conf_specificationList > tbody > tr > td:last-child,
.conf_specificationList > tbody > tr > th:last-child,
.conf_specificationList > tr > td:last-child,
.conf_specificationList > tr > th:last-child,
.table-wrap td:last-child,
.table-wrap th:last-child {
    border-right-width: 2px;
}
.conf_specificationList > tbody > tr:last-child > td,
.conf_specificationList > tbody > tr:last-child > th,
.conf_specificationList > tr:last-child > td,
.conf_specificationList > tr:last-child > th,
.table-wrap tr:last-child td,
.table-wrap tr:last-child th {
    border-bottom-width: 2px;
}
.table-wrap {
    padding: 0px 10px;
    margin-bottom: 5px;
    margin-top: 5px;
}
.conf_blankBullet {
}
.conf_blankBullet {
    width : 30px;
    padding-left: 10px;
    padding-right: 10px;
}
img[src='/s/1814/1/_/images/icons/docs_16.gif'] {
    display: none;
}
.emoticon {
    display: none;
    
    background : #000000;
}

h1 a {
    text-decoration : none;
}
.conf_specificationList,
.conf_specificationOutputTable {
    width: 100%%;
}
.conf_exeDetails {
    width: 200px;
}
.conf_specificationLinks {
    text-align : right;
}

.test-subpage-linex {
    display: none;
}

.tests-total {
    text-align: center;
}

.header-line th {
    text-align : center;
    color: #ffffff;
    text-shadow: 0px -1px 1px rgba(0,0,0,0.6);
    background-color: #a9b1bd !important;
    background: -moz-linear-gradient( -90deg, #a9b1bd, #596273) !important;
    background: -webkit-gradient(linear, left top, left bottom, from(#a9b1bd), to(#596273)) !important;
    filter: progid:DXImageTransform.Microsoft.Gradient( StartColorStr='#a9b1bd', EndColorStr='#596273', GradientType=0);
    background:      linear-gradient( -90deg, #a9b1bd, #596273) !important;
}

td.no-value {
    background-color: #cccccc !important;
    background: -moz-linear-gradient( -90deg, #eeeeee, #cccccc) !important;
    background: -webkit-gradient(linear, left top, left bottom, from(#eeeeee), to(#cccccc)) !important;
    filter: progid:DXImageTransform.Microsoft.Gradient( StartColorStr='#eeeeee', EndColorStr='#cccccc', GradientType=0);
    background:      linear-gradient( -90deg, #eeeeee, #cccccc) !important;
}

td.result-success,
td.values.test-success {
    background-color: #aaffaa !important;
    background: -moz-linear-gradient( -90deg, #ccffcc, #aaffaa) !important;
    background: -webkit-gradient(linear, left top, left bottom, from(#ccffcc), to(#aaffaa)) !important;
    filter: progid:DXImageTransform.Microsoft.Gradient( StartColorStr='#ccffcc', EndColorStr='#aaffaa', GradientType=0);
    background:      linear-gradient( -90deg, #ccffcc, #aaffaa) !important;
}

td.result-failure,
td.values.test-failures,
td.values.test-errors {
    background-color: #ffaaaa !important;
    background: -moz-linear-gradient( -90deg, #ffcccc, #ffaaaa) !important;
    background: -webkit-gradient(linear, left top, left bottom, from(#ffcccc), to(#ffaaaa)) !important;
    filter: progid:DXImageTransform.Microsoft.Gradient( StartColorStr='#ffcccc', EndColorStr='#ffaaaa', GradientType=0);
    background:      linear-gradient( -90deg, #ffcccc, #ffaaaa) !important;
}

td.result-ignored,
td.values.test-ignored {
    background-color: #ffffaa !important;
    background: -moz-linear-gradient( -90deg, #ffffcc, #ffffaa) !important;
    background: -webkit-gradient(linear, left top, left bottom, from(#ffffcc), to(#ffffaa)) !important;
    filter: progid:DXImageTransform.Microsoft.Gradient( StartColorStr='#ffffcc', EndColorStr='#ffffaa', GradientType=0);
    background:      linear-gradient( -90deg, #ffffcc, #ffffaa) !important;
}

td.test-title,
td.test-link,
td.test-sut {
    background-color: #ffffff !important;
    background: -moz-linear-gradient( -90deg, #ffffff, #eeeeee) !important;
    background: -webkit-gradient(linear, left top, left bottom, from(#ffffff), to(#eeeeee)) !important;
    filter: progid:DXImageTransform.Microsoft.Gradient( StartColorStr='#ffffff', EndColorStr='#eeeeee', GradientType=0);
    background:      linear-gradient( -90deg, #ffffff, #eeeeee) !important;
}


.test-id,
.test-success,
.test-failures,
.test-ignored,
.test-errors {
    text-align : right;
    width: 50px;
}

.test-link {
    text-align : center;
    width : 20px;
}

tr > span {
    display : none;
    width : 0px;
}

.hide-allok .allok,
.show-onlyerrors .noerrors,
#header,
#comments-section,
#labels-section,
.page-metadata,
.tableview,
.conf_executionTitle,
.conf_executionDetails,
#navigation,
#footer,
.logo,
.hidden {
    display: none;
}

.img-link {
    display: inline-block;
    width : 16px;
    height : 16px;
    background : url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABGdBTUEAAK/INwWK6QAAABl0RVh0U29mdHdhcmUAQWRvYmUgSW1hZ2VSZWFkeXHJZTwAAAINSURBVBgZBcG/r55zGAfg6/4+z3va01NHlYgzEfE7MdCIGISFgS4Gk8ViYyM2Mdlsko4GSf8Do0FLRCIkghhYJA3aVBtEz3nP89wf11VJvPDepdd390+8Nso5nESBQoq0pfvXm9fzWf19453LF85vASqJlz748vInb517dIw6EyYBIIG49u+xi9/c9MdvR//99MPPZ7+4cP4IZhhTPbwzT2d+vGoaVRRp1rRliVvHq+cfvM3TD82+7mun0o/ceO7NT+/4/KOXjwZU1ekk0840bAZzMQ2mooqh0A72d5x/6sB9D5zYnff3PoYBoWBgFKPKqDKqjCpjKr//dcu9p489dra88cydps30KswACfNEKanSaxhlntjJ8Mv12Paie+vZ+0+oeSwwQ0Iw1xAR1CiFNJkGO4wu3ZMY1AAzBI0qSgmCNJsJUEOtJSMaCTBDLyQ0CknAGOgyTyFFiLI2awMzdEcSQgSAAKVUmAeNkxvWJWCGtVlDmgYQ0GFtgg4pNtOwbBcwQy/Rife/2yrRRVI0qYCEBly8Z+P4qMEMy7JaVw72N568e+iwhrXoECQkfH91kY7jwwXMsBx1L93ZruqrK6uuiAIdSnTIKKPLPFcvay8ww/Hh+ufeznTXu49v95IMoQG3784gYXdTqvRmqn/Wpa/ADFX58MW3L71SVU9ETgEIQQQIOOzub+fhIvwPRDgeVjWDahIAAAAASUVORK5CYII=');
}

.test-ignored,
.test-sut {
    display : none;
}

.loading {
    display: block;
    width: 100%%;
    text-align: center;
    margin: 0px;
    padding: 0px;
}

.loading div {
    display: inline-block;
    -moz-border-radius-bottomleft : 12px;
    -moz-border-radius-bottomright : 12px;
    border-bottom-left-radius : 12px;
    border-bottom-right-radius : 12px;
    font-size: 20px;
    font-weight: bold;
    text-shadow: 0px -2px 1px rgba(0,0,0,0.4);
    color: #ffffff;
    margin: 0;
    padding: 15px 40px 20px 40px;
    
    background-color: #ff3388 !important;
    background: -moz-linear-gradient( -90deg, #ff3388, #770022) !important;
    background: -webkit-gradient(linear, left top, left bottom, from(#ff3388), to(#770022)) !important;
    filter: progid:DXImageTransform.Microsoft.Gradient( StartColorStr='#ff3388', EndColorStr='#770022', GradientType=0);
    background:      linear-gradient( -90deg, #ff3388, #770022) !important;
}

.show-all .loading,
.hide-allok .loading,
.show-onlyerrors .loading {
    display : none;
}

.multichoices {
    display: none;
}

.show-all .multichoices,
.hide-allok .multichoices,
.show-onlyerrors .multichoices {
    display : block;
}

.multichoices {
    float: right;
    margin: 4px 10px; 
    padding: 0px;
    -moz-border-radius : 12px;
    -o-border-radius : 12px;
    -webkit-border-radius : 12px;
    border-radius : 12px;
    -moz-box-shadow : 0px 0px 8px rgba(0,0,0,0.3);
    -webkit-box-shadow : 0px 0px 8px rgba(0,0,0,0.3);
    box-shadow : 0px 0px 8px rgba(0,0,0,0.3);
}

.multichoices .choice {
    display : inline-block;
    padding: 5px 10px;
    margin-left: -1px;
    border: 1px solid #a8a8a8;
    min-width: 60px;
    text-align: center;
    font-weight: bold;
    color: #666666;
}

.multichoices .choice {
    background:  #f8f8f8 no-repeat;
    background: -moz-linear-gradient(-90deg,#ffffff,#c8c8c8) #f8f8f8 no-repeat;
    background: -webkit-gradient(linear, left top, left bottom, from(#ffffff), to(#c8c8c8)) #f8f8f8 no-repeat;
    filter: progid:DXImageTransform.Microsoft.Gradient( StartColorStr='#ffffff', EndColorStr='#c8c8c8', GradientType=0);
    background: linear-gradient(-90deg,#ffffff,#c8c8c8) #f8f8f8 no-repeat;
    cursor: pointer;
}

.multichoices .choice:first-child {
    -moz-border-radius-topleft : 12px;
    -moz-border-radius-bottomleft : 12px;
    border-top-left-radius : 12px;
    border-bottom-left-radius : 12px;
}
.multichoices .choice:last-child {
    -moz-border-radius-topright : 12px;
    -moz-border-radius-bottomright : 12px;
    border-top-right-radius : 12px;
    border-bottom-right-radius : 12px;
}

.show-all #filter-complete,
.hide-allok #filter-partial,
.show-onlyerrors #filter-error,
.multichoices .choice.selected {
    font-weight: bold;
    background:  #55b6f2 no-repeat;
    background: -moz-linear-gradient(-90deg,#2a92d4,#55b6f2) #55b6f2 no-repeat;
    background: -webkit-gradient(linear, left top, left bottom, from(#2a92d4), to(#55b6f2)) #55b6f2 no-repeat;
    filter: progid:DXImageTransform.Microsoft.Gradient( StartColorStr='#2a92d4', EndColorStr='#55b6f2', GradientType=0);
    background: linear-gradient(-90deg,#2a92d4,#55b6f2) #55b6f2 no-repeat;
    
    color: #ffffff;
    text-shadow: 0px -1px 0px rgba(0,0,0,0.6);
    border-color: #2a92d4;
}

'''

header = u'''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">
<title>%(title)s</title>
<script type='text/javascript' src="http://ajax.googleapis.com/ajax/libs/jquery/1.4/jquery.min.js"></script>
<script type='text/javascript' src="http://ajax.googleapis.com/ajax/libs/jqueryui/1.8/jquery-ui.min.js"></script>
<script type='text/javascript'>
var conf_greenPepper = {
    getSpecification : function() {
        return this;
    },
    registerResults : function() {
        return this;
    },
    run : function() {
        return this;
    }
};
</script>
<style type='text/css'>
'''+css+'''
</style>
</head>
<body>

'''
footer = u'''
</body>
</html>
'''
