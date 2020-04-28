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


    var frqString = 'Drag the box on the mini-chart, up and down to see more associated words.​\n<br><br>' +
        'n = denotes the Count/Add, eg. “Machine Learning (n=0.2)” denotes that machine learning occurs in 20% of all ads.\n<br><br>' +
        'See also help for chart above“Association and frequency “\n<br><br>';

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

    var frqString = 'Drag the box on the mini-chart, up and down to see more associated words.​\n<br><br>' +
        'n = denotes the association strength.\n<br><br>' +
        'See also help for chart above“Association and frequency “\n';

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

    var Tooltip_AssFrequString = 'You should focus on words that have large association strength and are frequent. Association strength tells you if a word is strongly related to the given search term. Count/Add (= frequency) tells you if it is often used, ie. if it is important.\n' +
        '\n<br><br>' +
        'Association Strength measures how much more often the chosen words and the word in the chart co-occur in a small text window (15 words) of a job ad than expected. It corresponds to the PMI(Pointwise mutual information) value. A value of 0 indicates that they never co-occur together. A value of 1 that they always co-occur together.​ We applied a minimum association strength of 0.5.\n' +
        '\n<br><br>' +
        'Count/Add states how often an word occurs on average in a job ad. Words that occur below 30 times are disregarded.\n' +
        '\n<br><br>' +
        'The overall number of words is limited to the top 100 associated words.\n';

    new jBox('Tooltip', {
        attach: '#Tooltip_AssFrequ',
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
        content: Tooltip_AssFrequString,
    });

    var frqTree= 'The word tree shows associated words based on the PMI measure.\n<br>' +
        'Words are put together in a branch or node, if they occur very commonly together\n<br>' +
        'within a few words of each other in job ads.\n<br>' +
        'The labels of inner nodes are randomly chosen words from lower level nodes.\n';

    new jBox('Tooltip', {
        attach: '#Tooltip_Tree',
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
        content: frqTree,
    });
});

