function textPositioning(chart) {
    var container = jQuery(chart.container),
        seriesArea = container.find('.highcharts-series-group').get(0).getBBox(),
        span = container.parent().parent().find('.pie-chart-text-wrapper');

    span.css('top', seriesArea.y + (seriesArea.height / 2) - (span.height() / 2));

    if (container.parent().hasClass('has-legends')) {
        span.css('left', seriesArea.x + (seriesArea.width / 2));
    }
}

function buildChart(selector, options) {
    var chartObj,
        timer,
        defaultOptions = {
            chart: {
                plotBackgroundColor: null,
                plotBorderWidth: null,
                plotShadow: false,
                backgroundColor: 'none'
            },
            title: {
                text: '#{missing title}',
                align: 'left',
                style: {
                    fontSize: '18px',
                    fontFamily: 'Arial, sans-serif'
                }
            },
            tooltip: {
                pointFormat: '<b>{point.percentage:.1f}%</b>'
            },
            plotOptions: {
                pie: {
                    allowPointSelect: false,
                    cursor: 'pointer',
                    dataLabels: {
                        enabled: true,
                        // format: '<b>{point.percentage:.1f} %</b>: <br> {point.name}',
                        style: {
                            color: '#787d82',
                            fontSize: '12px',
                            fontFamily: 'Arial, sans-serif'
                        },
                        formatter: function () {
                            return '<div class="legend-text"><b style="font-size: 17px; font-weight: bold;">' + this.y + '%</b> <br> ' + this.key + '</div>';
                        },
                    },
                    borderWidth: 0
                }
            },
            series: [{
                animation: false,
                type: 'pie',
                name: null,
                size: '80%',
                innerSize: '56%',
                data: []
			}]
        },
        extOptions = $.extend(defaultOptions, options);

    Highcharts.getOptions().plotOptions.pie.colors = (function () {
        var colors = ["#0b71b9", "#3ab54a", "rgb(121, 121, 121)", "#000", "#3c446a", "#c1bbb6", "#aca59e", "#978e85", "#edbe71"];
        return colors;
    }());

    $(selector).highcharts(extOptions,
        function (chart) { // on complete
            chartObj = chart;
            textPositioning(chart);
        });
}

jQuery(function () {


    buildChart('#chart-2-wrapper', {
        title: {
            align: 'left',
            style: {
                fontSize: '18px',
                fontFamily: 'Arial, sans-serif'
            }
        },
        series: [{
            animation: false,
            type: 'pie',
            name: null,
            size: '100%',
            innerSize: '46%',
            data: [
				['Sokohali', 35.0],
				['International Shipping Partners', 25.0],
				['Local Distribution Partners', 20.0],
				['Resellers', 20.00]
			]
		}],
        tooltip: true,
        plotOptions: {
            pie: {
                allowPointSelect: false,
                cursor: 'auto',
                dataLabels: {
                    enabled: true,
                    // format: '<b>{point.percentage:.1f} %</b>: <br> {point.name}',
                    style: {
                        color: '#000',
                        fontSize: '1.2em',
                        fontFamily: 'Open Sans',
                    },
                    formatter: function () {
                        return '<div class="legend-text">' + this.key + '</div>';
                    },
                },
                borderWidth: 0
            }
        },
    });


});