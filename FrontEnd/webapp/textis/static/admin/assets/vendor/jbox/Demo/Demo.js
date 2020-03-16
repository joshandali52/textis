$(document).ready(function () {

    /* Switch on unique zIndex behavior for jBoxes with overlay:true */

    /* Tooltip */
    new jBox('Tooltip', {
        attach: '#Tooltip_Select',
        theme: 'TooltipBorder',
        trigger: 'click',
        width: 400,
        //height: ($(window).height() - 160),
        adjustTracker: true,
        closeOnClick: 'body',
        closeOnEsc: true,
        animation: 'move',
        position: {
            x: 'right',
            y: 'center'
        },
        outside: 'x',
        content: 'Click on a word highligthed in <span class="g-color-primary">red</span>' +
            '<br>' +
            '<br>' +
            'Words or compounds that appear black are not found in any job ad.​<br>' +
            '​<br>' +
            'One analysis process is to investigate relevant words in the syllables one after the other. Relevance is task dependent.​<br>' +
            'Is the course material overall still relevant?​<br>' +
            '1) Select key content terms of the lecture, ie. words in the title or short description. ​<br>' +
            '2) For each word look at its associations, frequencies and contents. This is detailed below​<br>' +
            'Is a particular method or tool still needed?​<br>' +
            '1) Select words related to the method or tool, e.g. its name. ​<br>' +
            '2) For each word look at its associations, frequencies and contents​',
    });


    var frqString = 'Drag the box on the mini-chart, up and down to see more associated words.​<br>' +
            '<br>' +
            'Association Strength measures how much more often the chosen words and the word in the chart co-occur in a small text window of a job ad than expected. A value of 0 indicates tha they never co-occur together. A value of 1 that they always co-occur together.​<br>' +
            '<br>' +
            'It can also be seen as a measure for surprise We use PMI (Pointwise mutual information): For two words w1, w2 we compute n(w1,w2)/(n(w1)*n(w2)) , where n(x,y) states how often x and y co-occurred per “text window” of about 2 sentences and n(x) states how often x occurred in all job ads. The disadvantage of the measure is that it might emphasize very rare words too much.​';

    new jBox('Tooltip', {
        attach: '#Tooltip_Ass',
        theme: 'TooltipBorder',
        trigger: 'click',
        width: 400,
        //height: ($(window).height() - 160),
        adjustTracker: true,
        closeOnClick: 'body',
        closeOnEsc: true,
        animation: 'move',
        position: {
            x: 'right',
            y: 'center'
        },
        outside: 'x',
        content: frqString,
    });
    new jBox('Tooltip', {
        attach: '#Tooltip_Ass2',
        theme: 'TooltipBorder',
        trigger: 'click',
        width: 400,
        //height: ($(window).height() - 160),
        adjustTracker: true,
        closeOnClick: 'body',
        closeOnEsc: true,
        animation: 'move',
        position: {
            x: 'right',
            y: 'center'
        },
        outside: 'x',
        content: frqString,
    });

    var frqString = 'Drag the box on the mini-chart, up and down to see more associated words.​<br>' +
            '<br>' +
            'Drag the box on the mini-chart, up and down to see more associated words.​​<br>' +
            '<br>' +
            'The chart focuses on frequent words. It shows 100 most frequent words out of top 1000 strongest associated words. Association strength is defined under help for "TOP ASSOCIATED WORDS \'PYTHON\' WITH FREQUENCY" .';

    new jBox('Tooltip', {
        attach: '#Tooltip_Frequency',
        theme: 'TooltipBorder',
        trigger: 'click',
        width: 400,
        //height: ($(window).height() - 160),
        adjustTracker: true,
        closeOnClick: 'body',
        closeOnEsc: true,
        animation: 'move',
        position: {
            x: 'right',
            y: 'center'
        },
        outside: 'x',
        content: frqString,
    });
    new jBox('Tooltip', {
        attach: '#Tooltip_Frequency2',
        theme: 'TooltipBorder',
        trigger: 'click',
        width: 400,
        //height: ($(window).height() - 160),
        adjustTracker: true,
        closeOnClick: 'body',
        closeOnEsc: true,
        animation: 'move',
        position: {
            x: 'right',
            y: 'center'
        },
        outside: 'x',
        content: frqString,
    });


    var compString = 'Drag the box on the mini-chart, up and down to see more associated words.​<br>' +
            '<br>' +
            'Compounds: What are adjacent words that co-occur so that they can be said to form a unique meaning? They must occur obeying specific grammatical rules, eg. a “subject” and a “verb”, e.g. “the professor teaches” cannot form a compound, but an object and an attribute such as “big data” can form one.​ ' +
            '<br><br>There is no double counting: “big data” counts only for the compound “big data”, not (in addition) for “big” or “data”.​​';

    new jBox('Tooltip', {
        attach: '#Tooltip_Compounds',
        theme: 'TooltipBorder',
        trigger: 'click',
        width: 400,
        //height: ($(window).height() - 160),
        adjustTracker: true,
        closeOnClick: 'body',
        closeOnEsc: true,
        animation: 'move',
        position: {
            x: 'right',
            y: 'center'
        },
        outside: 'x',
        content: compString,
    });
    new jBox('Tooltip', {
        attach: '#Tooltip_Compounds2',
        theme: 'TooltipBorder',
        trigger: 'click',
        width: 400,
        //height: ($(window).height() - 160),
        adjustTracker: true,
        closeOnClick: 'body',
        closeOnEsc: true,
        animation: 'move',
        position: {
            x: 'right',
            y: 'center'
        },
        outside: 'x',
        content: compString,
    });
});

