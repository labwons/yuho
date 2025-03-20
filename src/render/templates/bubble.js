/*--------------------------------------------------------------
# GLOBALS
--------------------------------------------------------------*/
const isLabTop = window.matchMedia('(max-width: 1443px)');
const isTablet = window.matchMedia('(max-width: 1023px)');
const isMobile = window.matchMedia('(max-width: 767px)');
const isNarrow = window.matchMedia('(max-width: 374px)');
const fontFamily = 'NanumGothic, Nanum Gothic, Open Sans, sans-serif';

var TOOLBOX = false; // 0: NO TOOLBOX, 1: USE TOOLBOX
var VIEW_MODE = false; // 0: TREEMAP, 1: BAR
var SAMSUNG = true; // 0: WITHOUT SAMSUNG, 1: WITH SAMSUNG
var BARMODE = false; // 0: INDUSTRY, 1: SECTOR
var bubbleLayout = {
	dragmode: TOOLBOX ? "zoom" : false,
    margin:{
        l:20,
        r:0,
        t:0,
        b:35
    },
	xaxis:{
		showline:true,
		zerolinecolor:"lightgrey",
		gridcolor:"lightgrey",
    },
    yaxis:{
		ticklabelposition: 'inside',
		showline:true,
		zerolinecolor:"lightgrey",
		gridcolor:"lightgrey",
    },
};
var bubbleOption = {
    showTips:false,
    responsive:true,
    displayModeBar:true,
    displaylogo:false,
    modeBarButtonsToRemove: [
      // 'toImage','select2d','lasso2d','zoomOut2d','zoomIn2d','resetScale2d'
      'toImage','select2d','lasso2d','resetScale2d'
    ]    
};


/*--------------------------------------------------------------
# SOURCE DATA
--------------------------------------------------------------*/
const srcIndicatorOpt = {{ srcIndicatorOpt }};
const srcTickers = {{ srcTickers }};
const srcSectors = {{ srcSectors }};


/*--------------------------------------------------------------
# Functions
--------------------------------------------------------------*/
function setOption(cssSelector, jsonObj, initKey){
    /*
    [USAGE]
    - setOption('.bubble-x', srcIndicatorOpt, 'D-1');
    - setOption('.bubble-y', srcIndicatorOpt, 'Y-1);
    */
    $(cssSelector).empty();
    Object.entries(jsonObj).forEach(([key, obj]) => {
        var label = (typeof obj === "object" && obj !== null) ? obj.label : obj;
		if (key == initKey) {
			$(cssSelector).append(`<option value="${key}" selected>${label}</option>`)
		} else {
			$(cssSelector).append(`<option value="${key}">${label}</option>`)
		}
    });
}

function setAxisLabel(cssSelector, axis){
	var selected = $(cssSelector).find('option:selected');
	selected.text(axis + ': ' + selected.text());
}

function setSearchBar(cssSelector, jsonObj, sector){
    $(cssSelector)
    .select2({placeholder: "\uc885\ubaa9\uba85\u0020\uac80\uc0c9"}) // 종목명 검색
    .empty()
    .append('<option></option>');

    Object.entries(jsonObj)
    .sort((a, b) => b[1].size - a[1].size)
    .forEach(([ticker, obj]) => {
		if ((sector != 'ALL') && (sector != obj.sectorCode)){
			return
		}
        $(cssSelector).append('<option value="' + ticker + '">' + obj.name + '</option>');
      })
}

function toggleToolbox() {
	TOOLBOX = !TOOLBOX;

	if(TOOLBOX) {
		$('.toolbox-on').css({'display': 'none'});
		$('.js-plotly-plot .plotly .modebar').css({
			'display':'flex',
			'background-color':'rgba(200, 200, 200, 0.4)'
		});
		$('.js-plotly-plot .plotly .modebar').prepend('<i class="toolbox-off fa fa-remove"></i>');
		$('.js-plotly-plot .plotly .modebar-group').css({
			'padding':'0'
		});
		$('.js-plotly-plot .plotly .modebar-btn').css({
			'padding':'0 5px'
		});
		Plotly.relayout('plotly', {
			'dragmode': "zoom",
		})
		$('.toolbox-off').click(function() {
			$(this).remove();
			toggleToolbox();
		})
		
	} else {
		$('.toolbox-on').css({'display': 'inline-block'});
		var plot = document.getElementById('plotly');
		$('.js-plotly-plot .plotly .modebar').css({'display':'none'});
		Plotly.relayout('plotly', {
			'dragmode': false,      
			'xaxis.range': plot.layout.xaxis.range,
			'yaxis.range': plot.layout.yaxis.range,
		});
	}
}

function setBubble(x, y, sector) {
	var xObj = srcIndicatorOpt[x];
	var yObj = srcIndicatorOpt[y];
	var data = {
		type:'scatter',
		x:[],
		y:[],
		mode:'markers',
		meta:[],
		hovertemplate: '%{meta}<br>' + xObj.label + ': %{x}' + xObj.unit + '<br>' + yObj.label + ': %{y}' + yObj.unit + '<extra></extra>',
		hoverlabel: {
			font: {
				family: fontFamily,
				color: '#fffff'
			}
		},
		marker: {
			size:[],
			color:[],
			line: {
				width:1.0,
			},
			opacity: 0.7,        
        },
	};
	
	Object.entries(srcTickers).forEach(([ticker, obj]) => {
		if (
			(sector != 'ALL') &&
			(sector != obj.sectorCode)
		) {
			return;
		}
		
		data.x.push(obj[x]);
		data.y.push(obj[y]);
		data.meta.push(obj.meta);
		data.marker.size.push(obj.size);
		data.marker.color.push(srcSectors[obj.sectorCode].color);		
	});
	
	
	bubbleLayout.xaxis.title = xObj.label + (xObj.unit ? '[' + xObj.unit + ']' : '');
	bubbleLayout.yaxis.title = yObj.label + (yObj.unit ? '[' + yObj.unit + ']' : '');
	bubbleLayout.shapes = [{
		type:'line',
		xref:'paper',
		x0:0, x1:1,
		y0:yObj.mean,
		y1:yObj.mean,
		line:{
			color:'grey',
			width: 1,
			dash:'dot'
		}
	},{
		type:'line',
		yref:'paper',
		x0:xObj.mean, 
		x1:xObj.mean,
		y0:0,
		y1:1,
		line:{
			color:'grey',
			width: 1,
			dash:'dot'
		}
	}];
  
    Plotly.newPlot('plotly', [data], bubbleLayout, bubbleOption)
	.then(function() {
		if (!TOOLBOX) {
			$('.js-plotly-plot .plotly .modebar').css({'display':'none'});
		}
	});
}


$(document).ready(function(){


    setOption('.bubble-x', srcIndicatorOpt, 'D-1');
    setOption('.bubble-y', srcIndicatorOpt, 'Y-1');
	setOption('.bubble-sectors', srcSectors, "ALL");
    setSearchBar('.bubble-searchbar', srcTickers, $('.bubble-sectors').val());
	setBubble($('.bubble-x').val(), $('.bubble-y').val(), $('.bubble-sectors').val());
	setAxisLabel('.bubble-x', 'X');
	setAxisLabel('.bubble-y', 'Y');
	
	$('.toolbox-on').click(function() {
		toggleToolbox();
	})
		
	$('.bubble-sectors').on('change', function() {
		setSearchBar('.bubble-searchbar', srcTickers, $(this).val());
		setBubble($('.bubble-x').val(), $('.bubble-y').val(), $(this).val());
	})
	
	$('.bubble-x').on('change', function() {
		setAxisLabel('.bubble-x', 'X');
		setBubble($(this).val(), $('.bubble-y').val(), $('.bubble-sectors').val());
	})
	
	$('.bubble-y').on('change', function() {
		setAxisLabel('.bubble-y', 'Y');
		setBubble($('.bubble-x').val(), $(this).val(), $('.bubble-sectors').val());
	})
	
	$('.bubble-searchbar').on('select2:select', function (e) {
		var obj = srcTickers[e.params.data.id];
		Plotly.relayout('plotly', {
			'xaxis.range': [0.9 * obj[$('.bubble-x').val()], 1.1 * obj[$('.bubble-x').val()]],
			'yaxis.range': [0.9 * obj[$('.bubble-y').val()], 1.1 * obj[$('.bubble-y').val()]]
		})  
	});
})

