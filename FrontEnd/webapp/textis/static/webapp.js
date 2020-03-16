function getPhrases(word) {

    //alert(objectId);

    $.ajax({
        dataType: "json",
        type: "post",
        async: true,
        cache: false,
        url: "/textis/phrases",
        data: {
            Word: word,
            csrfmiddlewaretoken: window.CSRF_TOKEN,
        },
        success: function(data) {
            result = JSON.parse(data);
            $("#jobAdsPhrases").html(result.phrases);
            $("#selectedWord").html(result.word + ", Occ/Ad " + (result.wordOcc).toPrecision(2));
            $("#frequentWords").html(result.frequentWords);
            $("#mediumWords").html(result.mediumWords);
            $("#rareWords").html(result.rareWords);
            $("#compoundsWordsIn").html(result.compoundsWordsIn);
            $("#compoundsWordsParts").html(result.compoundsWordsParts);
        },
        error: function(xhr, textStatus, errorThrown) {
            //alert("Please report this error: "+errorThrown+xhr.status+ ":" +xhr.responseText);
        }
    });
};