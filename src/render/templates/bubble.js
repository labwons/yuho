/*--------------------------------------------------------------
# GLOBALS
--------------------------------------------------------------*/
const isLabTop = window.matchMedia('(max-width: 1443px)');
const isTablet = window.matchMedia('(max-width: 1023px)');
const isMobile = window.matchMedia('(max-width: 767px)');
const isNarrow = window.matchMedia('(max-width: 374px)');
const fontFamily = 'NanumGothic, Nanum Gothic, Open Sans, sans-serif';
const mapLayout = {
    margin:{
        l:0,
        r:0,
        t:0,
        b:25
    }
};
const barLayout = {
    margin:{
        l:10,
        r:0,
        t:10,
        b:22
    },
    xaxis:{
        autorange: false,
        showticklabels: false,
        showline: false,
        range:[0, 0],
    },
    yaxis:{
        showline: false,
        zeroline: false,
        showticklabels: false
    },
    dragmode: false
};

const mapOption = {
    displayModeBar:false,
    responsive:true,
    showTips:false
};

const barOption = {
    scrollZoom: false,
    displayModeBar:false,
    responsive:true,
    showTips:false,
};

let EVE = document.createEvent('MouseEvent');
EVE.initMouseEvent('click', true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);

var VIEW_MODE = false; // 0: TREEMAP, 1: BAR
var SAMSUNG = true; // 0: WITHOUT SAMSUNG, 1: WITH SAMSUNG
var BARMODE = false; // 0: INDUSTRY, 1: SECTOR


/*--------------------------------------------------------------
# SOURCE DATA
--------------------------------------------------------------*/
const srcMapOpt = {
    all: "\ub300\ud615\uc8fc", // 대형주
    woS: "\ub300\ud615\uc8fc\u0028\uc0bc\uc131\uc804\uc790\u0020\uc81c\uc678\u0029" // 대형주(삼성전자 제외)
};
const srcBarOpt = {
    sector: "\uc139\ud130\u0020\u0053\u0065\u0063\u0074\u006f\u0072", // 섹터 Sector
    industry: "\uc5c5\uc885\u0020\u0049\u006e\u0064\u0075\u0073\u0074\u0072\u0079" // 업종 Industry
};
const srcIndicatorOpt = {{ srcIndicatorOpt }};
const srcTicker = {{ srcTicker }};
const srcColors = {{ srcColors }};


/*--------------------------------------------------------------
# Functions
--------------------------------------------------------------*/
function setOption(cssSelector, jsonObj, initIndex){
    /*
    [USAGE]
    - setOption('.map-type', (VIEW_MODE ? srcBarOpt : srcMapOpt), 0);
    - setOption('.map-option', srcIndicatorOpt, 0);
    */
    $(cssSelector).empty();
    Object.entries(jsonObj).forEach(([key, obj]) => {
        var label = (typeof obj === "object" && obj !== null) ? obj.label : obj;
        $(cssSelector).append(`<option value="${key}">${label}</option>`)
    });
    $(`${cssSelector} option[value="${Object.keys(jsonObj)[initIndex]}"]`).prop('selected', true);
}

function setSearchBar(cssSelector, jsonObj){
    $(cssSelector)
    .select2({placeholder: "\uc885\ubaa9\uba85\u0020\uac80\uc0c9"}) // 종목명 검색
    .empty()
    .append('<option></option>');

    Object.entries(jsonObj)
    .sort((a, b) => b[1].size - a[1].size)
    .forEach(([ticker, obj]) => {
        if (
            ticker.startsWith('N') ||
            ticker.startsWith('W') ||
            ( (!SAMSUNG) && (ticker == '005930') )
        ){
            return
        }
        $(cssSelector).append('<option value="' + ticker + '">' + obj.name + '</option>');
      })
}

function setScaleBar(cssSelector, jsonObj) {
    /*
    [USAGE]
    - setScaleBar('.map-legend', srcIndicatorOpt[$('.map-option')]);
    */
    $(cssSelector).each(function(n){
        if(jsonObj.valueScale[n] == null){
            $(this).html('&nbsp; - &nbsp;');
        } else {
            $(this).html(String(jsonObj.valueScale[n]) + jsonObj.unit);
        }
        $(this).css('background-color', jsonObj.colorScale[n]);
    })
}

function setBar(key) {
    var data = {
        type:'bar',
        x:[],
        y:[],
        orientation:'h',
        marker: {
            color:[]
        },
        text:[],
        textposition: 'outside',
        meta:[],
        hovertemplate: '%{meta}' + srcIndicatorOpt[key].label + ': %{text}<extra></extra>',
        opacity:0.9
    };
    var tickers = [];
    Object.entries(srcTicker).forEach(([ticker, obj]) => {
        if (
            ( BARMODE && (ticker.startsWith('W') && ticker.includes('G')) ) ||
            ( (!BARMODE) && (ticker.startsWith('W') && (!ticker.includes('G'))) )
        ){
            if (ticker !== 'WS0000'){
                obj.ticker = ticker;
                tickers.push(obj);
            }
        }
    });
    tickers.sort((a, b) => a[key] - b[key]).forEach(item => {
        data.x.push(Math.abs(item[key]));
        data.y.push(item.name);
        data.marker.color.push(srcColors[item.ticker][key]);
        data.text.push(item[key] + srcIndicatorOpt[key].unit);
        data.meta.push(item.meta);
    });
    data.x = data.x.map(item => item + 0.3333 * Math.max(...data.x));
    barLayout.annotations = data.y.map(item => {
        return {
            x:0,
            y:item,
            xref:'x',
            yref:'y',
            text: item,
            showarrow:false,
            font: {
                family:fontFamily,
                color:'#ffffff',
                size:13,
            },
            xanchor:'left',
            yanchor:'middle'
        }
    })
    barLayout.xaxis.range = [0, 1.2 * Math.max(...data.x)];

//    if (isNarrow.matches) {
//        var xrange = 1.75 * maxX;
//    } else if (isMobile.matches) {
//        var xrange = 1.5 * maxX;
//    } else if (isTablet.matches) {
//        var xrange = 1.25 * maxX;
//    } else {
//        var xrange = 1.1 * maxX;
//    }

    Plotly.newPlot('plotly', [data], barLayout, barOption);

}

function setMap(key) {
    var data = {
        type:'treemap',
        branchvalues:'total',
        labels: [],
        parents: [],
        values: [],
        text: [],
        meta: [],
        textposition:'middle center',
        textfont:{
            family:fontFamily,
            color:'#ffffff'
        },
        texttemplate: '%{label}<br>%{text}',
        marker: {
            colors: [],
            visible: true,
        },
        hovertemplate: '%{meta}<br>' + srcIndicatorOpt[key].label + ': %{text}<extra></extra>',
        hoverlabel: {
            font: {
                family: fontFamily,
                color: '#ffffff'
            }
        },
        opacity: 0.9,
        pathbar:{
            visible: true,
        }
    };

    Object.entries(srcTicker).forEach(([ticker, obj]) => {
        if (!SAMSUNG) {
            if ( (ticker == '005930') || ticker.startsWith('W') ) {
                return
            }
        } else {
            if (ticker.startsWith('N')) {
                return
            }
        }
        data.labels.push(obj.name);
        data.parents.push(obj.ceiling);
        data.values.push(obj.size);
        if (obj[key] == null) {
            data.text.push(srcIndicatorOpt[key].na);
        } else {
            data.text.push(obj[key] + srcIndicatorOpt[key].unit);
        }
        data.meta.push(obj.meta);
        data.marker.colors.push(srcColors[ticker][key]);

    });
    Plotly.newPlot('plotly', [data], mapLayout, mapOption);
}

function eventClickTreemap(item){
    var elements = $('g.slicetext');
    for (var n = 0; n < elements.length; n++){
        if ($(elements[n]).text().includes(item)){
            !$(elements[n]).get(0).dispatchEvent(EVE);
            return;
        }
    }
}


$(document).ready(function(){

    setOption('.map-type', srcMapOpt, 0);
    setOption('.map-option', srcIndicatorOpt, 0);
    setSearchBar('.map-searchbar', srcTicker);
    setScaleBar('.map-legend', srcIndicatorOpt[$('.map-option').val()]);
    setMap($('.map-option').val());

    $('.map-type').on('change', function(){
        if (VIEW_MODE){
            BARMODE = !BARMODE;
            setBar($('.map-option').val());
        } else {
            SAMSUNG = !SAMSUNG;
            setSearchBar('.map-searchbar', srcTicker);
            setMap($('.map-option').val());
        }
    });

    $('.map-option').on('change', function(){
        setScaleBar('.map-legend', srcIndicatorOpt[$(this).val()]);
        if (VIEW_MODE){
            setBar($(this).val());
        } else {
            setMap($(this).val());
        }
    });

    $('.map-switch i').click(function(){
        VIEW_MODE = !VIEW_MODE;
        if (VIEW_MODE) {
            var _index = BARMODE ? 0 : 1;
            setOption('.map-type', srcBarOpt, _index);
            setBar($('.map-option').val());
            $(this).removeClass('fa-signal').addClass('fa-map-o');
            $('.map-searchbar').prop('disabled', true);
        } else {
            var _index = SAMSUNG ? 0 : 1;
            setOption('.map-type', srcMapOpt, _index);
            setMap($('.map-option').val());
            $(this).removeClass('fa-map-o').addClass('fa-signal');
            $('.map-searchbar').prop('disabled', false);
        }
    });

    $('.map-reset').click(function(){
        VIEW_MODE = false;
        SAMSUNG = true;
        setOption('.map-type', srcMapOpt, 0);
        setOption('.map-option', srcIndicatorOpt, 0);
        setSearchBar('.map-searchbar', srcTicker);
        setScaleBar('.map-legend', srcIndicatorOpt[$('.map-option').val()]);
        setMap($('.map-option').val());
    })

    $('.map-searchbar').on('select2:select', function(e) {
        const ticker = srcTicker[e.params.data.id];
        eventClickTreemap(ticker.ceiling);
        setTimeout(function(){
            eventClickTreemap(ticker.name);
        }, 1000);
    });

    $('#plotly').on('plotly_doubleclick', function() {
        console.log("@@");
        setMap($('.map-option').val());
    })

    $('#plotly').on('plotly_click', function(e, d){
        if (!VIEW_MODE) {
//            if ($('g.slice').length == 1) {
//            rewindOff();
//            } else if (
//            (!d.points[0].customdata.startsWith('W')) &&
//            (!d.points[0].customdata.startsWith('G')) &&
//            (!d.points[0].customdata.startsWith('T'))
//            ) {
//            rewindOn();
//            } else {
//            return;
//            }

        }
    })

})


//function rewindOn(){
//  if( !$('.map-rewind').attr('class').includes('show') ) {
//    $('.map-rewind').toggleClass('show');
//  }
//}
//
//function rewindOff(){
//  if( $('.map-rewind').attr('class').includes('show') ) {
//    $('.map-rewind').toggleClass('show');
//  }
//}
//
///*--------------------------------------------------------------
//# FETCH & BINDINGS
//--------------------------------------------------------------*/
//$(document).ready(async function(){
//
//
//
//  $('.map-reset').click(function(){
//    setTreemap();
//    rewindOff();
//    setSearchSelector();
//  })
//
//  $('.map-switch i').click(function(){
//    if ( $(this).attr('class').includes('fa-map-o') ) {
//      viewMd = 'treemap';
//      setTreemap();
//      $(this).removeClass('fa-map-o').addClass('fa-signal');
//      $('.map-searchbar').prop('disabled', false);
//    } else {
//      viewMd = 'bar';
//      setBarChart();
//      rewindOff();
//      $(this).removeClass('fa-signal').addClass('fa-map-o');
//      $('.map-searchbar').prop('disabled', true);
//
//    }
//    setTypeSelector();
//  })
//
//  $('.map-searchbar').on('select2:select', function (e) {
//    var ticker = e.params.data.id;
//    if (ticker.startsWith('W')) {
//      var elem = SRC[mapTyp].industry[ticker];
//      clickTreemap(elem.name);
//      return
//    } else if (ticker.startsWith('G')) {
//      var elem = SRC[mapTyp].sector[ticker];
//      clickTreemap(elem.name);
//      return
//    } else {
//      var elem = SRC.TICKERS[ticker];
//      clickTreemap(elem.ceiling);
//      setTimeout(function(){
//        clickTreemap(elem.name);
//      }, 1000);
//    }
//  });
//
//  $('.map-rewind').click(function(){
//    if (viewMd == 'bar') {
//      return;
//    }
//    !$('.slice').get(0).dispatchEvent(EVE);
//    rewindOff();
//  })
//
//  $('#market-map').on('plotly_click', function(e, d){
//    if (viewMd == 'bar') {
//      return;
//    }
//    if ($('g.slice').length == 1) {
//      rewindOff();
//    } else if (
//      (!d.points[0].customdata.startsWith('W')) &&
//      (!d.points[0].customdata.startsWith('G')) &&
//      (!d.points[0].customdata.startsWith('T'))
//    ) {
//      rewindOn();
//    } else {
//      return;
//    }
//  })
//})