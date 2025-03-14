/*--------------------------------------------------------------
# GLOBALS
--------------------------------------------------------------*/
const isLabTop = window.matchMedia('(max-width: 1443px)');
const isTablet = window.matchMedia('(max-width: 1023px)');
const isMobile = window.matchMedia('(max-width: 767px)');
const isNarrow = window.matchMedia('(max-width: 374px)');
const abs = (array) => {return array.map(Math.abs);}

let SRC = null;
let EVE = document.createEvent('MouseEvent');

var mapTyp = 'all';
var mapFrm = null;
var barTyp = 'industry';
var comOpt = 'D-1';
var viewMd = 'treemap';

EVE.initMouseEvent('click', true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);

/*--------------------------------------------------------------
# SOURCE DATA
--------------------------------------------------------------*/

/*--------------------------------------------------------------
# Functions
--------------------------------------------------------------*/
function setFrame(){
  mapFrm = SRC.TICKERS;
  Object.values(SRC[mapTyp]).forEach(val => {
    mapFrm = Object.assign({}, mapFrm, val);
  })
}

function setTypeSelector() {
  if (viewMd == 'treemap') {
    $('.map-type')
    .empty()
    .append('<option value="all">대형주</option>')
    .append('<option value="woS">대형주(삼성전자 제외)</option>')
    $('.map-type option[value="' + mapTyp + '"]').prop('selected', true);
  } else {
    $('.map-type')
    .empty()
    .append('<option value="sector">섹터 Sector</option>')
    .append('<option value="industry">업종 Industry</option>')
    $('.map-type option[value="' + barTyp + '"]').prop('selected', true);
  }
}

function setOptionSelector() {
  Object.entries(SRC.meta).forEach(([key, val]) => {
    $('.map-option').append('<option value="' + key + '">' + val.label + '</option>');
  })
  $('.map-option option[value="' + comOpt + '"]').prop('selected', true);
}

function setSearchSelector(){
  $('.map-searchbar')
    .select2({placeholder: "종목명/섹터/업종"})
    .empty()
	  .append('<option></option>');
  
  $('.map-searchbar').append('<optgroup label="[종목 / Stocks]">');
  Object.entries(SRC.TICKERS)
  .sort((a, b) => b[1].size - a[1].size)
  .forEach(item => {
    if ((mapTyp === "woS") && (item[0] === '005930')) {
      return;
    }
    $('.map-searchbar').append('<option value="' + item[0] + '">' + item[1].name + '</option>');
  })

  $('.map-searchbar').append('<optgroup label="[섹터 / Sectors]">');
  Object.entries(SRC[mapTyp].sector).forEach(([key, val]) => {
    $('.map-searchbar').append('<option value="' + key + '">' + val.name + '</option>');
  })
  $('.map-searchbar').append('<optgroup label="[업종 / Industries]">');
  Object.entries(SRC[mapTyp].industry).forEach(([key, val]) => {
    $('.map-searchbar').append('<option value="' + key + '">' + val.name + '</option>');
  })
}

function setScale(){
  var tag = SRC.METADATA[comOpt];
  $('.map-legend span').each(function(n){
    if(tag.bound[n] == null){
      $(this).html('&nbsp; - &nbsp;');
    } else {
      $(this).html(String(tag.bound[n]) + tag.unit);
    }
    $(this).css('background-color', tag.scale[n]);
  })
}

function setTreemapLayout() {
  return {
    margin:{l:0, r:0, t:0, b:25},
    annotations: [{
      x: 1,
      y: 1,
      xref: 'paper',
      yref: 'paper',
      text: '날짜 삽입?',
      showarrow: false,
      xanchor: 'right',
      yanchor: 'top',
      font: {
          size: 12,
          color: 'white'
      }
      
    }]
  }
}

function setBarLayout() {
  return {
    margin:{l:10, r:0, t:10, b:22}, 
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
  }
}

function setTreemapOption() {
  return {
    displayModeBar:false,
    responsive:true,
    showTips:false
  }
}

function setBarOption() {
  return {
    scrollZoom: false,
    displayModeBar:false, 
    responsive:true, 
    showTips:false, 
  }
}

function clickTreemap(item){
  var elements = $('g.slicetext');
	for (var n = 0; n < elements.length; n++){
		if ($(elements[n]).text().includes(item)){
      !$(elements[n]).get(0).dispatchEvent(EVE);
			return;
		}
	}
}

function rewindOn(){
  if( !$('.map-rewind').attr('class').includes('show') ) {
    $('.map-rewind').toggleClass('show');
  }
}

function rewindOff(){
  if( $('.map-rewind').attr('class').includes('show') ) {
    $('.map-rewind').toggleClass('show');
  }
}

function setTreemap() {
  //var tag = SRC.METADATA[comOpt];
  var layout = setTreemapLayout();
  var option = setTreemapOption();
  var font = 'NanumGothic, Nanum Gothic, Open Sans, sans-serif';

  var customdata = [];
  var labels = [];
  var parents = [];
  var values = [];
  var meta = [];
  var text = [];
  var colors = [];
  
  SRC[$('.map-type').val()].forEach(ticker => {
	  var item = SRC.base[ticker];
	  labels.push(item.name);
	  parents.push(item.ceiling);
	  values.push(item.size);
	  // customdata.push(item.meta);
	  meta.push(item.meta);
	  text.push(item.name + '<br>' + item[$('.map-option')]);
	  colors.push(SRC.colors[ticker][$('.map-option')]);
  })


  Plotly.newPlot(
    'plotly', 
    [{
      type:'treemap',
      branchvalues:'total',
      labels:labels,
      parents:parents,
      values:values,
      // customdata: customdata,
      meta:meta,
      text:text,
      textposition:'middle center',
      textfont:{
        family:font,
        color:'#ffffff'
      },
      texttemplate: '%{label}<br>%{text}',
      hovertemplate: '%{meta}<br>' + SRC.meta[$('.map-option')] + ': %{text}<extra></extra>',
      hoverlabel: {
        font: {
          family: font,
          color: '#ffffff'
        }
      },
      opacity: 0.9,
      marker: {
        colors: colors,
        visible: true
      },
    }],
    layout,
    option
  );
}

function setBarChart() {
  var tag = SRC.METADATA[comOpt];
  var layout = setBarLayout();
  var option = setBarOption();
  var data = Object.values(SRC.WS[barTyp]);
  var x = [];
  var y = [];
  var text = [];
  var meta = [];
  var color = [];
  if (barTyp == 'industry') {
    SRC.METADATA.DUPLICATEDGROUP.forEach(item => {
      data.push(SRC.WS.sector[item]);
    })
  }

  data.forEach(item => {
    item.n = parseFloat(item[comOpt][0].replace(tag.unit, ''));
    item.x = Math.abs(item.n);
  });
  data.sort((a, b) => b.n - a.n);

  var maxX = Math.max(...data.map(item => item.x));
  data.forEach(item => {
    x.push(item.x + 0.45 * maxX);
    y.push(item.name);
    text.push(item[comOpt][0]);
    meta.push(item.meta);
    color.push(item[comOpt][1]);
  })  

  if (isNarrow.matches) {
    var xrange = 1.35 * maxX;
  } else if (isMobile.matches) {
    var xrange = 1.3 * maxX;
  } else if (isTablet.matches) {
    var xrange = 1.2 * maxX;
  } else {
    var xrange = 1.1 * maxX;
  }

  layout.xaxis.range = [0, 1.45 * xrange];
  layout.annotations = y.map(item => {
    return {
      x: 0,
      y: item,
      xref: 'x',
      yref: 'y',
      text: item,
      showarrow: false,
      font: {
        color: 'white',
        size: 13,
      },
      xanchor: 'left',
      yanchor: 'middle',
    };
  });

  Plotly.newPlot(
    'market-map', 
    [{
      type:'bar',
      x: x.reverse(),
      y: y.reverse(),
      orientation: 'h',
      marker: {
        color: color.reverse()
      },
      text: text.reverse(),
      textposition: 'outside',
      meta: meta.reverse(),
      hovertemplate: '%{meta}' + tag.label + ': %{text}<extra></extra>',
      opacity: 0.9
    }], 
    layout, 
    option
  );
}


/*--------------------------------------------------------------
# FETCH & BINDINGS
--------------------------------------------------------------*/
$(document).ready(async function(){
  try {
    const response = await fetch('/src/json/treemap.json');
    if (!response.ok) {
        throw new Error('Network response was not ok');
    }
    
    SRC = await response.json();
	console.log(SRC);
    setTypeSelector();
    // setOptionSelector();
    //setFrame();
    setTreemap();
    //setScale();
    //setSearchSelector();
  } catch (error) {
      console.error('Fetch error:', error);
  }

  $('.map-type').on('change', function() {   
    if (viewMd == 'treemap') {
      mapTyp = $(this).val();
      setFrame(); 
      setTreemap();
      setSearchSelector();
    } else {
      barTyp = $(this).val();
      setBarChart();
    }    
  })

  $('.map-option').on('change', function() {
    comOpt = $(this).val();
    if (viewMd == 'treemap') {
      setTreemap();
    } else {
      setBarChart();
    }    
    setScale();
  })

  $('.map-reset').click(function(){
    setTreemap();
    rewindOff(); 
    setSearchSelector();   
  })

  $('.map-switch i').click(function(){
    if ( $(this).attr('class').includes('fa-map-o') ) {
      viewMd = 'treemap';
      setTreemap();
      $(this).removeClass('fa-map-o').addClass('fa-signal');
      $('.map-searchbar').prop('disabled', false);
    } else {
      viewMd = 'bar';
      setBarChart();
      rewindOff();
      $(this).removeClass('fa-signal').addClass('fa-map-o');
      $('.map-searchbar').prop('disabled', true);      
      
    }
    setTypeSelector();
  })

  $('.map-searchbar').on('select2:select', function (e) {
    var ticker = e.params.data.id;
    if (ticker.startsWith('W')) {
      var elem = SRC[mapTyp].industry[ticker];
      clickTreemap(elem.name);
      return
    } else if (ticker.startsWith('G')) {
      var elem = SRC[mapTyp].sector[ticker];
      clickTreemap(elem.name);
      return
    } else {
      var elem = SRC.TICKERS[ticker];
      clickTreemap(elem.ceiling);
      setTimeout(function(){
        clickTreemap(elem.name);
      }, 1000);      
    }
  });
  
  $('.map-rewind').click(function(){
    if (viewMd == 'bar') {
      return;
    }
    !$('.slice').get(0).dispatchEvent(EVE);
    rewindOff();
  })
  
  $('#market-map').on('plotly_click', function(e, d){
    if (viewMd == 'bar') {
      return;
    }    
    if ($('g.slice').length == 1) {
      rewindOff();
    } else if (
      (!d.points[0].customdata.startsWith('W')) && 
      (!d.points[0].customdata.startsWith('G')) && 
      (!d.points[0].customdata.startsWith('T'))
    ) {
      rewindOn();
    } else {
      return;
    }
  })
})