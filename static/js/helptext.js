$(function() {
    var helpersNeeded = $(".help-block").parents(".form-group").children("label");
    $("<span class='glyphicon glyphicon-question-sign' aria-hidden='true'></span>")
        .insertAfter(helpersNeeded);
    $(".glyphicon-question-sign").hover(function() {
        var helpText = $(this).parents(".form-group").find(".help-block");
        var xPos = -$(this).parents(".col-xs-12").offset().left + $(this).offset().left + 15;
        var yPos = -$(this).parents(".col-xs-12").offset().top + $(this).offset().top + 15;
        helpText.css({ top: yPos, left: xPos}).show();
    }, function() {
        $(this).parents(".form-group").find(".help-block").hide();
    });
    // add click version of effect too, for mobile users
    $(".glyphicon-question-sign").click(function() {
        var helpText = $(this).parents(".form-group").find(".help-block");
        var xPos = -$(this).parents(".col-xs-12").offset().left + $(this).offset().left + 15;
        var yPos = -$(this).parents(".col-xs-12").offset().top + $(this).offset().top + 15;
        helpText.css({ top: yPos, left: xPos}).toggle();
    });
});
